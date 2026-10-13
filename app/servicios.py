"""Servicios de negocio. Aquí se ejecutan las reglas; las rutas solo traducen HTTP.

S01: registrar_incidencia.
S02: listar_por_asignar, listar_tecnicos_activos, asignar_incidencia.
S03: listar_asignaciones_de, iniciar_atencion, registrar_solucion.
S04: listar_reportes_de, confirmar_solucion, rechazar_solucion, reabrir_incidencia.
S05: listar_incidencias, obtener_detalle, calcular_tablero.
"""
from datetime import datetime

from .db import get_db, transaccion
from .dominio import (
    CATEGORIAS,
    ESTADOS,
    PRIORIDADES,
    IMPACTOS,
    UBICACIONES,
    ErrorEstado,
    ErrorNoEncontrada,
    ErrorPermiso,
    ErrorValidacion,
    PLAZO_REAPERTURA,
    calcular_prioridad,
    dentro_de_plazo_reapertura,
    porcentaje_cierre,
    parsear_riesgo,
    validar_descripcion,
    validar_motivo,
    validar_opcion,
    validar_solucion,
)
from .historial import registrar_evento
from .reloj import fecha_iso

# Solo estos campos se leen del cliente; código, autor, fecha, estado y prioridad
# los genera el servidor (AC-S01-09).
CAMPOS_REGISTRO = {
    "ubicacion": "ubicación",
    "categoria": "categoría",
    "descripcion": "descripción",
    "impacto": "impacto",
    "riesgo_personas": "riesgo para personas",
}


def _vacio(valor):
    return valor is None or (isinstance(valor, str) and valor.strip() == "")


def registrar_incidencia(datos, usuario, reloj):
    """Valida, calcula la prioridad y guarda la incidencia y su evento en una transacción."""
    if usuario is None or usuario["rol"] != "SOLICITANTE":
        raise ErrorPermiso("Solo un solicitante puede registrar incidencias")

    validadores = {
        "ubicacion": lambda v: validar_opcion(v, UBICACIONES, "ubicación"),
        "categoria": lambda v: validar_opcion(v, CATEGORIAS, "categoría"),
        "descripcion": validar_descripcion,
        "impacto": lambda v: validar_opcion(v, IMPACTOS, "impacto"),
        "riesgo_personas": parsear_riesgo,
    }
    errores, valores = [], {}
    for campo, etiqueta in CAMPOS_REGISTRO.items():
        valor = datos.get(campo)
        if _vacio(valor):
            errores.append(f"Falta el campo {etiqueta}")
            continue
        try:
            valores[campo] = validadores[campo](valor)
        except ErrorValidacion as error:
            errores.extend(error.args)
    if errores:
        raise ErrorValidacion(*errores)

    prioridad = calcular_prioridad(valores["riesgo_personas"], valores["impacto"])
    ahora = fecha_iso(reloj.ahora())

    with transaccion() as conn:
        siguiente = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM incidencias").fetchone()[0]
        codigo = f"INC-{siguiente:04d}"
        cursor = conn.execute(
            "INSERT INTO incidencias (codigo, solicitante_id, ubicacion, categoria, descripcion,"
            " impacto, riesgo_personas, prioridad, estado, creada_en)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'REGISTRADA', ?)",
            (codigo, usuario["id"], valores["ubicacion"], valores["categoria"],
             valores["descripcion"], valores["impacto"], int(valores["riesgo_personas"]),
             prioridad, ahora),
        )
        registrar_evento(conn, cursor.lastrowid, usuario["id"], "REGISTRAR", None, "REGISTRADA", ahora)

    return {"id": cursor.lastrowid, "codigo": codigo, "prioridad": prioridad}


# ---------------------------------------------------------------- S02 ----

def listar_por_asignar():
    """Incidencias REGISTRADAS, de la más antigua a la más reciente."""
    return get_db().execute(
        "SELECT codigo, ubicacion, categoria, prioridad, creada_en FROM incidencias"
        " WHERE estado = 'REGISTRADA' ORDER BY id"
    ).fetchall()


def listar_tecnicos_activos():
    return get_db().execute(
        "SELECT id, nombre_usuario FROM usuarios WHERE rol = 'TECNICO' AND activo = 1"
        " ORDER BY nombre_usuario"
    ).fetchall()


def asignar_incidencia(codigo, tecnico_id, usuario, reloj):
    """Asigna una incidencia REGISTRADA a un técnico activo (S02).

    Las verificaciones se hacen dentro de la transacción para que nadie cambie
    el estado entre la comprobación y la escritura.
    """
    if usuario is None or usuario["rol"] != "COORDINADOR":
        raise ErrorPermiso("Solo el coordinador puede asignar incidencias")
    try:
        tecnico_id = int(tecnico_id)
    except (TypeError, ValueError):
        raise ErrorValidacion("Selecciona un técnico válido") from None

    ahora = fecha_iso(reloj.ahora())
    with transaccion() as conn:
        incidencia = conn.execute(
            "SELECT id, estado FROM incidencias WHERE codigo = ?", (codigo,)
        ).fetchone()
        if incidencia is None:
            raise ErrorNoEncontrada("Incidencia no encontrada")
        if incidencia["estado"] != "REGISTRADA":
            raise ErrorEstado(
                f"Solo se puede asignar una incidencia REGISTRADA; esta está {incidencia['estado']}"
            )
        tecnico = conn.execute(
            "SELECT id, rol, activo FROM usuarios WHERE id = ?", (tecnico_id,)
        ).fetchone()
        if tecnico is None or tecnico["rol"] != "TECNICO":
            raise ErrorValidacion("Selecciona un técnico válido")
        if tecnico["activo"] != 1:
            raise ErrorValidacion("El técnico seleccionado está inactivo")

        conn.execute(
            "INSERT INTO asignaciones (incidencia_id, coordinador_id, tecnico_id, asignada_en)"
            " VALUES (?, ?, ?, ?)",
            (incidencia["id"], usuario["id"], tecnico["id"], ahora),
        )
        conn.execute(
            "UPDATE incidencias SET estado = 'ASIGNADA' WHERE id = ? AND estado = 'REGISTRADA'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "ASIGNAR", "REGISTRADA", "ASIGNADA", ahora)


# ---------------------------------------------------------------- S03 ----

def listar_asignaciones_de(tecnico_id):
    """Incidencias asignadas al técnico, en cualquier estado, con su última solución."""
    return get_db().execute(
        "SELECT i.codigo, i.ubicacion, i.categoria, i.descripcion, i.prioridad, i.estado,"
        " (SELECT s.descripcion FROM soluciones s WHERE s.incidencia_id = i.id"
        "  ORDER BY s.id DESC LIMIT 1) AS ultima_solucion"
        " FROM incidencias i JOIN asignaciones a ON a.incidencia_id = i.id"
        " WHERE a.tecnico_id = ? ORDER BY i.id",
        (tecnico_id,),
    ).fetchall()


def _incidencia_del_tecnico(conn, codigo, usuario):
    """Devuelve la incidencia si existe y está asignada al técnico de la sesión."""
    if usuario is None or usuario["rol"] != "TECNICO":
        raise ErrorPermiso("Solo el técnico asignado puede atender la incidencia")
    fila = conn.execute(
        "SELECT i.id, i.estado, a.tecnico_id FROM incidencias i"
        " LEFT JOIN asignaciones a ON a.incidencia_id = i.id WHERE i.codigo = ?",
        (codigo,),
    ).fetchone()
    if fila is None:
        raise ErrorNoEncontrada("Incidencia no encontrada")
    if fila["tecnico_id"] != usuario["id"]:
        raise ErrorPermiso("Solo el técnico asignado puede atender la incidencia")
    return fila


def iniciar_atencion(codigo, usuario, reloj):
    """ASIGNADA -> EN_ATENCION por el técnico asignado (S03)."""
    ahora = fecha_iso(reloj.ahora())
    with transaccion() as conn:
        incidencia = _incidencia_del_tecnico(conn, codigo, usuario)
        if incidencia["estado"] != "ASIGNADA":
            raise ErrorEstado(
                f"Solo se puede iniciar la atención de una incidencia ASIGNADA; esta está {incidencia['estado']}"
            )
        conn.execute(
            "UPDATE incidencias SET estado = 'EN_ATENCION' WHERE id = ? AND estado = 'ASIGNADA'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "INICIAR_ATENCION",
                         "ASIGNADA", "EN_ATENCION", ahora)


def registrar_solucion(codigo, texto, usuario, reloj):
    """EN_ATENCION -> PENDIENTE_VALIDACION con una solución nueva (S03).

    Cada solución es un registro nuevo: las anteriores nunca se sobrescriben.
    """
    ahora = fecha_iso(reloj.ahora())
    with transaccion() as conn:
        incidencia = _incidencia_del_tecnico(conn, codigo, usuario)
        if incidencia["estado"] != "EN_ATENCION":
            raise ErrorEstado(
                f"Solo se puede registrar una solución con la incidencia EN_ATENCION; esta está {incidencia['estado']}"
            )
        texto_limpio = validar_solucion(texto)
        cursor = conn.execute(
            "INSERT INTO soluciones (incidencia_id, tecnico_id, descripcion, creada_en) VALUES (?, ?, ?, ?)",
            (incidencia["id"], usuario["id"], texto_limpio, ahora),
        )
        conn.execute(
            "UPDATE incidencias SET estado = 'PENDIENTE_VALIDACION' WHERE id = ? AND estado = 'EN_ATENCION'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "REGISTRAR_SOLUCION",
                         "EN_ATENCION", "PENDIENTE_VALIDACION", ahora, solucion_id=cursor.lastrowid)


# ---------------------------------------------------------------- S04 ----

def _ultimo_cierre(conn, incidencia_id):
    """Fecha del cierre más reciente (UTC) o None si nunca se cerró."""
    valor = conn.execute(
        "SELECT MAX(cerrada_en) FROM cierres WHERE incidencia_id = ?", (incidencia_id,)
    ).fetchone()[0]
    return datetime.fromisoformat(valor) if valor else None


def listar_reportes_de(solicitante_id, reloj):
    """Incidencias del solicitante con técnico, última solución y plazo de reapertura."""
    db = get_db()
    filas = db.execute(
        "SELECT i.id, i.codigo, i.ubicacion, i.categoria, i.descripcion, i.prioridad, i.estado,"
        " u.nombre_usuario AS tecnico,"
        " (SELECT s.descripcion FROM soluciones s WHERE s.incidencia_id = i.id"
        "  ORDER BY s.id DESC LIMIT 1) AS ultima_solucion"
        " FROM incidencias i"
        " LEFT JOIN asignaciones a ON a.incidencia_id = i.id"
        " LEFT JOIN usuarios u ON u.id = a.tecnico_id"
        " WHERE i.solicitante_id = ? ORDER BY i.id",
        (solicitante_id,),
    ).fetchall()
    ahora = reloj.ahora()
    reportes = []
    for fila in filas:
        reporte = dict(fila)
        reporte["reabrir_hasta"] = None
        if fila["estado"] == "CERRADA":
            cierre = _ultimo_cierre(db, fila["id"])
            if cierre and dentro_de_plazo_reapertura(cierre, ahora):
                reporte["reabrir_hasta"] = fecha_iso(cierre + PLAZO_REAPERTURA)
        reportes.append(reporte)
    return reportes


def _incidencia_del_dueno(conn, codigo, usuario):
    """Devuelve la incidencia si existe y pertenece al solicitante de la sesión.

    Si pertenece a otro solicitante se responde "no encontrada", sin revelar que existe.
    """
    if usuario is None or usuario["rol"] != "SOLICITANTE":
        raise ErrorPermiso("Solo el solicitante dueño puede validar o reabrir la incidencia")
    fila = conn.execute(
        "SELECT id, estado, solicitante_id FROM incidencias WHERE codigo = ?", (codigo,)
    ).fetchone()
    if fila is None or fila["solicitante_id"] != usuario["id"]:
        raise ErrorNoEncontrada("Incidencia no encontrada")
    return fila


def _exigir_estado(incidencia, esperado, accion):
    if incidencia["estado"] != esperado:
        raise ErrorEstado(
            f"Solo se puede {accion} una incidencia {esperado}; esta está {incidencia['estado']}"
        )


def confirmar_solucion(codigo, usuario, reloj):
    """PENDIENTE_VALIDACION -> CERRADA, con un registro de cierre nuevo (S04)."""
    ahora = fecha_iso(reloj.ahora())
    with transaccion() as conn:
        incidencia = _incidencia_del_dueno(conn, codigo, usuario)
        _exigir_estado(incidencia, "PENDIENTE_VALIDACION", "confirmar la solución de")
        conn.execute(
            "INSERT INTO cierres (incidencia_id, solicitante_id, cerrada_en) VALUES (?, ?, ?)",
            (incidencia["id"], usuario["id"], ahora),
        )
        conn.execute(
            "UPDATE incidencias SET estado = 'CERRADA' WHERE id = ? AND estado = 'PENDIENTE_VALIDACION'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "CONFIRMAR",
                         "PENDIENTE_VALIDACION", "CERRADA", ahora)


def rechazar_solucion(codigo, motivo, usuario, reloj):
    """PENDIENTE_VALIDACION -> EN_ATENCION con el mismo técnico y la solución intacta (S04)."""
    ahora = fecha_iso(reloj.ahora())
    with transaccion() as conn:
        incidencia = _incidencia_del_dueno(conn, codigo, usuario)
        _exigir_estado(incidencia, "PENDIENTE_VALIDACION", "rechazar la solución de")
        motivo_limpio = validar_motivo(motivo)
        conn.execute(
            "UPDATE incidencias SET estado = 'EN_ATENCION' WHERE id = ? AND estado = 'PENDIENTE_VALIDACION'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "RECHAZAR",
                         "PENDIENTE_VALIDACION", "EN_ATENCION", ahora, motivo=motivo_limpio)


def reabrir_incidencia(codigo, motivo, usuario, reloj):
    """CERRADA -> EN_ATENCION si han pasado <= 48 h desde el último cierre (S04).

    La hora efectiva es siempre la del reloj del servidor; nunca la del cliente.
    """
    instante = reloj.ahora()
    with transaccion() as conn:
        incidencia = _incidencia_del_dueno(conn, codigo, usuario)
        _exigir_estado(incidencia, "CERRADA", "reabrir")
        motivo_limpio = validar_motivo(motivo)
        cierre = _ultimo_cierre(conn, incidencia["id"])
        if cierre is None or not dentro_de_plazo_reapertura(cierre, instante):
            raise ErrorEstado("El plazo de 48 horas para reabrir esta incidencia ya venció")
        conn.execute(
            "UPDATE incidencias SET estado = 'EN_ATENCION' WHERE id = ? AND estado = 'CERRADA'",
            (incidencia["id"],),
        )
        registrar_evento(conn, incidencia["id"], usuario["id"], "REABRIR",
                         "CERRADA", "EN_ATENCION", fecha_iso(instante), motivo=motivo_limpio)


# ---------------------------------------------------------------- S05 ----

ETIQUETAS_ACCION = {
    "REGISTRAR": "Registró la incidencia",
    "ASIGNAR": "Asignó la incidencia",
    "INICIAR_ATENCION": "Inició la atención",
    "REGISTRAR_SOLUCION": "Registró una solución",
    "RECHAZAR": "Rechazó la solución",
    "CONFIRMAR": "Confirmó la solución (cierre)",
    "REABRIR": "Reabrió la incidencia",
}

_SELECT_LISTADO = (
    "SELECT i.codigo, i.ubicacion, i.categoria, i.prioridad, i.estado, i.creada_en,"
    " ut.nombre_usuario AS tecnico"
    " FROM incidencias i"
    " LEFT JOIN asignaciones a ON a.incidencia_id = i.id"
    " LEFT JOIN usuarios ut ON ut.id = a.tecnico_id"
)


def _filtro_visibilidad(usuario):
    """Condición SQL según el rol: la visibilidad se aplica en la consulta, no en la plantilla."""
    if usuario["rol"] == "COORDINADOR":
        return "1 = 1", []
    if usuario["rol"] == "SOLICITANTE":
        return "i.solicitante_id = ?", [usuario["id"]]
    if usuario["rol"] == "TECNICO":
        return "a.tecnico_id = ?", [usuario["id"]]
    raise ErrorPermiso("Rol sin acceso a incidencias")


def listar_incidencias(usuario, estado=None, prioridad=None):
    """Incidencias visibles para el usuario, con filtros combinables (S05)."""
    estado = estado or None
    prioridad = prioridad or None
    if (estado is not None and estado not in ESTADOS) or (prioridad is not None and prioridad not in PRIORIDADES):
        raise ErrorValidacion("Filtro no válido")
    condicion, parametros = _filtro_visibilidad(usuario)
    sql = f"{_SELECT_LISTADO} WHERE {condicion}"
    if estado:
        sql += " AND i.estado = ?"
        parametros.append(estado)
    if prioridad:
        sql += " AND i.prioridad = ?"
        parametros.append(prioridad)
    return get_db().execute(sql + " ORDER BY i.id", parametros).fetchall()


def obtener_detalle(codigo, usuario):
    """Incidencia, soluciones, cierres e historial, si el usuario puede verla (S05).

    Si no existe o no está permitida, se responde "no encontrada" sin revelar datos.
    """
    db = get_db()
    condicion, parametros = _filtro_visibilidad(usuario)
    incidencia = db.execute(
        "SELECT i.id, i.codigo, i.ubicacion, i.categoria, i.descripcion, i.impacto,"
        " i.riesgo_personas, i.prioridad, i.estado, i.creada_en,"
        " us.nombre_usuario AS solicitante, ut.nombre_usuario AS tecnico"
        " FROM incidencias i JOIN usuarios us ON us.id = i.solicitante_id"
        " LEFT JOIN asignaciones a ON a.incidencia_id = i.id"
        " LEFT JOIN usuarios ut ON ut.id = a.tecnico_id"
        f" WHERE i.codigo = ? AND {condicion}",
        [codigo, *parametros],
    ).fetchone()
    if incidencia is None:
        raise ErrorNoEncontrada("Incidencia no encontrada")

    historial = db.execute(
        "SELECT e.accion, e.estado_anterior, e.estado_nuevo, e.motivo, e.creado_en,"
        " u.nombre_usuario AS autor, s.descripcion AS solucion,"
        " CASE WHEN e.accion = 'ASIGNAR' THEN"
        "  (SELECT t.nombre_usuario FROM asignaciones a2 JOIN usuarios t ON t.id = a2.tecnico_id"
        "   WHERE a2.incidencia_id = e.incidencia_id) END AS tecnico_asignado"
        " FROM eventos e JOIN usuarios u ON u.id = e.usuario_id"
        " LEFT JOIN soluciones s ON s.id = e.solucion_id"
        " WHERE e.incidencia_id = ? ORDER BY e.id",
        (incidencia["id"],),
    ).fetchall()
    cierres = db.execute(
        "SELECT cerrada_en FROM cierres WHERE incidencia_id = ? ORDER BY id", (incidencia["id"],)
    ).fetchall()
    return {"incidencia": incidencia, "historial": historial, "cierres": cierres}


def calcular_tablero():
    """Cantidades por estado y prioridad, críticas no cerradas y porcentaje de cierre (S05)."""
    db = get_db()
    por_estado = {e: 0 for e in ESTADOS}
    for fila in db.execute("SELECT estado, COUNT(*) FROM incidencias GROUP BY estado"):
        por_estado[fila[0]] = fila[1]
    por_prioridad = {p: 0 for p in PRIORIDADES}
    for fila in db.execute("SELECT prioridad, COUNT(*) FROM incidencias GROUP BY prioridad"):
        por_prioridad[fila[0]] = fila[1]
    criticas = db.execute(
        f"{_SELECT_LISTADO} WHERE i.prioridad = 'CRITICA' AND i.estado <> 'CERRADA' ORDER BY i.id"
    ).fetchall()
    total = sum(por_estado.values())
    return {
        "por_estado": por_estado,
        "por_prioridad": por_prioridad,
        "criticas_abiertas": criticas,
        "total": total,
        "cerradas": por_estado["CERRADA"],
        "porcentaje_cierre": porcentaje_cierre(por_estado["CERRADA"], total),
    }
