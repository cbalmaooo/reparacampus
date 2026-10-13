"""Servicios de negocio. Aquí se ejecutan las reglas; las rutas solo traducen HTTP.

S01: registrar_incidencia.
S02: listar_por_asignar, listar_tecnicos_activos, asignar_incidencia.
"""
from .db import get_db, transaccion
from .dominio import (
    CATEGORIAS,
    IMPACTOS,
    UBICACIONES,
    ErrorEstado,
    ErrorNoEncontrada,
    ErrorPermiso,
    ErrorValidacion,
    calcular_prioridad,
    parsear_riesgo,
    validar_descripcion,
    validar_opcion,
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
