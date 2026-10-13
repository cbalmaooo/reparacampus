"""Servicios de negocio. Aquí se ejecutan las reglas; las rutas solo traducen HTTP.

S01: registrar_incidencia.
"""
from .db import transaccion
from .dominio import (
    CATEGORIAS,
    IMPACTOS,
    UBICACIONES,
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
