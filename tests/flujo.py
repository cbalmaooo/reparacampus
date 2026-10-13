"""Ayudas compartidas para preparar incidencias con los servicios reales de S01–S04."""
from app import servicios
from app.db import get_db

REGISTRO = {
    "ubicacion": "LAB-01",
    "categoria": "ELECTRICIDAD",
    "descripcion": "El tomacorriente del puesto 4 hace chispas",
    "impacto": "ALTO",
    "riesgo_personas": "true",
}
SOLUCION_1 = "Se reemplazó el tomacorriente dañado del puesto 4"
SOLUCION_2 = "Se cambió también el cableado del circuito del puesto 4"


def usuario(nombre):
    return get_db().execute(
        "SELECT id, rol FROM usuarios WHERE nombre_usuario = ?", (nombre,)
    ).fetchone()


def hasta_pendiente(reloj, solicitante="solicitante1", tecnico="tecnico1"):
    """Registra, asigna, inicia y propone S1. Devuelve el código. Requiere app_context."""
    codigo = servicios.registrar_incidencia(REGISTRO, usuario(solicitante), reloj)["codigo"]
    servicios.asignar_incidencia(codigo, usuario(tecnico)["id"], usuario("coordinador1"), reloj)
    servicios.iniciar_atencion(codigo, usuario(tecnico), reloj)
    servicios.registrar_solucion(codigo, SOLUCION_1, usuario(tecnico), reloj)
    return codigo
