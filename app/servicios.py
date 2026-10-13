"""Servicios de negocio. Aquí se ejecutan las reglas; las rutas solo traducen HTTP.

S01: registrar_incidencia.
S02: listar_por_asignar, listar_tecnicos_activos, asignar_incidencia.
S03: listar_asignaciones_de, iniciar_atencion, registrar_solucion.
S04: listar_reportes_de, confirmar_solucion, rechazar_solucion, reabrir_incidencia.
"""
from datetime import datetime

from .db import get_db, transaccion
from .dominio import (
    CATEGORIAS,
    IMPACTOS,
    UBICACIONES,
    ErrorEstado,
    ErrorNoEncontrada,
    ErrorPermiso,
    ErrorValidacion,
    PLAZO_REAPERTURA,
    calcular_prioridad,
    dentro_de_plazo_reapertura,
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
