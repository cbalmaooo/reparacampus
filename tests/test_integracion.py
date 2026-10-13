"""Pruebas de integración obligatorias contra SQLite real en archivo (INT-01 a INT-03).

Recorren el flujo completo por HTTP, con una sesión independiente por actor, y
verifican estado, registros y eventos en la base. Esperados escritos a mano.
"""
import pytest

from tests.flujo import REGISTRO, SOLUCION_1, SOLUCION_2
from tests.conftest import CONTRASENAS


@pytest.fixture
def actores(app):
    """Un cliente HTTP con sesión propia para cada actor."""
    clientes = {}
    for nombre in ("solicitante1", "coordinador1", "tecnico1"):
        cliente = app.test_client()
        respuesta = cliente.post("/login", data={"usuario": nombre, "contrasena": CONTRASENAS[nombre]})
        assert respuesta.status_code == 302
        clientes[nombre] = cliente
    return clientes


def ok(respuesta):
    assert respuesta.status_code == 302, respuesta.get_data(as_text=True)[:300]


def registrar_y_resolver(actores, conn):
    sol, coord, tec = actores["solicitante1"], actores["coordinador1"], actores["tecnico1"]
    ok(sol.post("/incidencias/", data=REGISTRO))
    tecnico_id = conn.execute("SELECT id FROM usuarios WHERE nombre_usuario = 'tecnico1'").fetchone()[0]
    ok(coord.post("/incidencias/INC-0001/asignar", data={"tecnico_id": str(tecnico_id)}))
    ok(tec.post("/incidencias/INC-0001/iniciar"))
    ok(tec.post("/incidencias/INC-0001/solucion", data={"solucion": SOLUCION_1}))


def acciones(conn):
    return [f[0] for f in conn.execute("SELECT accion FROM eventos ORDER BY id")]


def test_int_01_flujo_de_cierre(actores, conn):
    """INT-01: registrar → asignar → iniciar → proponer → confirmar."""
    registrar_y_resolver(actores, conn)
    ok(actores["solicitante1"].post("/incidencias/INC-0001/confirmar"))
    assert conn.execute("SELECT estado FROM incidencias").fetchone()[0] == "CERRADA"
    assert acciones(conn) == ["REGISTRAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION", "CONFIRMAR"]
    assert conn.execute("SELECT COUNT(*) FROM cierres").fetchone()[0] == 1


def test_int_02_rechazo_y_nueva_solucion(actores, conn):
    """INT-02: … → proponer S1 → rechazar → proponer S2 → confirmar."""
    registrar_y_resolver(actores, conn)
    sol, tec = actores["solicitante1"], actores["tecnico1"]
    ok(sol.post("/incidencias/INC-0001/rechazar", data={"motivo": "El daño sigue presente"}))
    ok(tec.post("/incidencias/INC-0001/solucion", data={"solucion": SOLUCION_2}))
    ok(sol.post("/incidencias/INC-0001/confirmar"))
    assert conn.execute("SELECT estado FROM incidencias").fetchone()[0] == "CERRADA"
    assert [f[0] for f in conn.execute("SELECT descripcion FROM soluciones ORDER BY id")] == [SOLUCION_1, SOLUCION_2]
    tecnicos = {f[0] for f in conn.execute("SELECT tecnico_id FROM soluciones")}
    assert len(tecnicos) == 1  # mismo técnico en ambas soluciones
    assert acciones(conn) == ["REGISTRAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION",
                              "RECHAZAR", "REGISTRAR_SOLUCION", "CONFIRMAR"]
    motivo = conn.execute("SELECT motivo FROM eventos WHERE accion = 'RECHAZAR'").fetchone()[0]
    assert motivo == "El daño sigue presente"


def test_int_03_cierre_reapertura_y_nuevo_cierre(actores, conn, reloj):
    """INT-03: cierre → reapertura → nueva solución → nuevo cierre."""
    registrar_y_resolver(actores, conn)
    sol, tec = actores["solicitante1"], actores["tecnico1"]
    ok(sol.post("/incidencias/INC-0001/confirmar"))
    reloj.avanzar(hours=24)
    ok(sol.post("/incidencias/INC-0001/reabrir", data={"motivo": "La falla volvió a aparecer"}))
    ok(tec.post("/incidencias/INC-0001/solucion", data={"solucion": SOLUCION_2}))
    reloj.avanzar(hours=1)
    ok(sol.post("/incidencias/INC-0001/confirmar"))
    assert conn.execute("SELECT estado FROM incidencias").fetchone()[0] == "CERRADA"
    cierres = [f[0] for f in conn.execute("SELECT cerrada_en FROM cierres ORDER BY id")]
    assert cierres == ["2026-10-13T12:00:00+00:00", "2026-10-14T13:00:00+00:00"]
    assert conn.execute("SELECT COUNT(*) FROM soluciones").fetchone()[0] == 2
    assert acciones(conn) == ["REGISTRAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION",
                              "CONFIRMAR", "REABRIR", "REGISTRAR_SOLUCION", "CONFIRMAR"]
