"""S03 — Atender una incidencia y registrar la solución (AC-S03-01 a AC-S03-13).

Esperados escritos a mano; reloj fijo en 2026-10-13T12:00:00+00:00.
"""
import pytest

from app import servicios
from app.db import get_db

REGISTRO = {
    "ubicacion": "BIB-01",
    "categoria": "HIDRAULICA",
    "descripcion": "Gotea el lavamanos del baño del primer piso",
    "impacto": "ALTO",
    "riesgo_personas": "false",
}
SOLUCION = "Se reemplazó el empaque del grifo y se probó sin fugas"


def uid(conn, nombre):
    return conn.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (nombre,)).fetchone()[0]


def usuario(db, nombre):
    return db.execute("SELECT id, rol FROM usuarios WHERE nombre_usuario = ?", (nombre,)).fetchone()


@pytest.fixture
def asignada(app, reloj):
    """INC-0001 de solicitante1, ASIGNADA a tecnico1 mediante los servicios de S01 y S02."""
    with app.app_context():
        db = get_db()
        codigo = servicios.registrar_incidencia(REGISTRO, usuario(db, "solicitante1"), reloj)["codigo"]
        servicios.asignar_incidencia(codigo, uid(db, "tecnico1"), usuario(db, "coordinador1"), reloj)
        return codigo


@pytest.fixture
def en_atencion(app, reloj, asignada):
    with app.app_context():
        servicios.iniciar_atencion(asignada, usuario(get_db(), "tecnico1"), reloj)
    return asignada


def estado(conn):
    return conn.execute("SELECT estado FROM incidencias WHERE codigo = 'INC-0001'").fetchone()[0]


def contar(conn, sql):
    return conn.execute(sql).fetchone()[0]


def iniciar(client, codigo):
    return client.post(f"/incidencias/{codigo}/iniciar")


def solucionar(client, codigo, texto):
    return client.post(f"/incidencias/{codigo}/solucion", data={"solucion": texto})


def test_iniciar_atencion(iniciar_sesion, conn, asignada):  # AC-S03-01
    assert iniciar(iniciar_sesion("tecnico1"), asignada).status_code == 302
    assert estado(conn) == "EN_ATENCION"
    assert conn.execute("SELECT tecnico_id FROM asignaciones").fetchone()[0] == uid(conn, "tecnico1")
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'INICIAR_ATENCION'").fetchone()
    assert evento["usuario_id"] == uid(conn, "tecnico1")
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("ASIGNADA", "EN_ATENCION")
    assert evento["creado_en"] == "2026-10-13T12:00:00+00:00"


def test_tecnico_no_asignado(iniciar_sesion, conn, asignada):  # AC-S03-02
    client = iniciar_sesion("tecnico2")
    assert iniciar(client, asignada).status_code == 403
    assert solucionar(client, asignada, SOLUCION).status_code == 403
    assert estado(conn) == "ASIGNADA"
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 2  # REGISTRAR + ASIGNAR


@pytest.mark.parametrize("nombre", ["solicitante1", "coordinador1"])
def test_otros_roles(iniciar_sesion, conn, asignada, nombre):  # AC-S03-03
    client = iniciar_sesion(nombre)
    assert iniciar(client, asignada).status_code == 403
    assert client.get("/incidencias/mis-asignaciones").status_code == 403
    assert estado(conn) == "ASIGNADA"


def test_sin_sesion(client, conn, asignada):  # AC-S03-03
    respuesta = iniciar(client, asignada)
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"
    assert estado(conn) == "ASIGNADA"


def test_iniciar_dos_veces(iniciar_sesion, conn, asignada):  # AC-S03-04
    client = iniciar_sesion("tecnico1")
    iniciar(client, asignada)
    assert iniciar(client, asignada).status_code == 409
    assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'INICIAR_ATENCION'") == 1


def test_solucion_valida(iniciar_sesion, conn, en_atencion):  # AC-S03-05
    assert solucionar(iniciar_sesion("tecnico1"), en_atencion, SOLUCION).status_code == 302
    assert estado(conn) == "PENDIENTE_VALIDACION"
    sol = conn.execute("SELECT * FROM soluciones").fetchone()
    assert sol["descripcion"] == SOLUCION
    assert sol["tecnico_id"] == uid(conn, "tecnico1")
    assert sol["creada_en"] == "2026-10-13T12:00:00+00:00"
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'REGISTRAR_SOLUCION'").fetchone()
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("EN_ATENCION", "PENDIENTE_VALIDACION")
    assert evento["solucion_id"] == sol["id"]


@pytest.mark.parametrize(
    "longitud, aceptada, mensaje",
    [
        (20, True, None),
        (19, False, "La solución debe tener al menos 20 caracteres"),
        (800, True, None),
        (801, False, "La solución no puede superar 800 caracteres"),
    ],
)
def test_limites_de_solucion(iniciar_sesion, conn, en_atencion, longitud, aceptada, mensaje):  # AC-S03-06, 07
    respuesta = solucionar(iniciar_sesion("tecnico1"), en_atencion, "A" * longitud)
    if aceptada:
        assert respuesta.status_code == 302 and estado(conn) == "PENDIENTE_VALIDACION"
    else:
        assert respuesta.status_code == 400
        assert mensaje in respuesta.get_data(as_text=True)
        assert estado(conn) == "EN_ATENCION"
        assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 0
        assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'REGISTRAR_SOLUCION'") == 0


def test_espacios_externos(iniciar_sesion, conn, en_atencion):  # AC-S03-08
    client = iniciar_sesion("tecnico1")
    assert solucionar(client, en_atencion, "   " + "A" * 19 + "   ").status_code == 400
    assert solucionar(client, en_atencion, "          ").status_code == 400
    assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 0
    assert solucionar(client, en_atencion, "   " + "A" * 20 + "   ").status_code == 302
    assert conn.execute("SELECT descripcion FROM soluciones").fetchone()[0] == "A" * 20


def test_solucion_antes_de_iniciar(iniciar_sesion, conn, asignada):  # AC-S03-09
    assert solucionar(iniciar_sesion("tecnico1"), asignada, SOLUCION).status_code == 409
    assert estado(conn) == "ASIGNADA"
    assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 0


@pytest.mark.parametrize("estado_actual", ["PENDIENTE_VALIDACION", "CERRADA"])
def test_otros_estados_incompatibles(iniciar_sesion, conn, asignada, estado_actual):  # AC-S03-10
    conn.execute("UPDATE incidencias SET estado = ? WHERE codigo = ?", (estado_actual, asignada))
    client = iniciar_sesion("tecnico1")
    assert iniciar(client, asignada).status_code == 409
    assert solucionar(client, asignada, SOLUCION).status_code == 409
    assert estado(conn) == estado_actual
    assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 0


def test_registrada_sin_asignacion(iniciar_sesion, conn, app, reloj):  # AC-S03-10 (REGISTRADA)
    with app.app_context():
        servicios.registrar_incidencia(REGISTRO, usuario(get_db(), "solicitante1"), reloj)
    respuesta = iniciar(iniciar_sesion("tecnico1"), "INC-0001")
    assert respuesta.status_code == 403  # no está asignada a este técnico
    assert estado(conn) == "REGISTRADA"


def test_nueva_solucion_conserva_la_anterior(iniciar_sesion, conn, en_atencion):  # AC-S03-11
    client = iniciar_sesion("tecnico1")
    solucionar(client, en_atencion, SOLUCION)
    # Efecto de un rechazo (S04): vuelve a EN_ATENCION con el mismo técnico.
    # El flujo completo con el servicio de rechazo se prueba en INT-02 al integrar S04.
    conn.execute("UPDATE incidencias SET estado = 'EN_ATENCION' WHERE codigo = ?", (en_atencion,))
    segunda = "Se cambió también la llave de paso del lavamanos"
    assert solucionar(client, en_atencion, segunda).status_code == 302
    textos = [f[0] for f in conn.execute("SELECT descripcion FROM soluciones ORDER BY id")]
    assert textos == [SOLUCION, segunda]
    assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'REGISTRAR_SOLUCION'") == 2


def test_texto_parecido_a_html(iniciar_sesion, conn, en_atencion):  # AC-S03-12
    client = iniciar_sesion("tecnico1")
    texto = "<script>alert('x')</script> cambio de breaker principal"
    solucionar(client, en_atencion, texto)
    assert conn.execute("SELECT descripcion FROM soluciones").fetchone()[0] == texto
    html = client.get("/incidencias/mis-asignaciones").get_data(as_text=True)
    assert "<script>alert('x')</script>" not in html
    assert "&lt;script&gt;" in html


def test_incidencia_inexistente(iniciar_sesion, conn):  # AC-S03-13
    client = iniciar_sesion("tecnico1")
    assert iniciar(client, "INC-9999").status_code == 404
    assert solucionar(client, "INC-9999", SOLUCION).status_code == 404
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 0


def test_cada_tecnico_ve_solo_sus_asignaciones(iniciar_sesion, client, asignada):  # T-S03-07
    assert "INC-0001" in iniciar_sesion("tecnico1").get("/incidencias/mis-asignaciones").get_data(as_text=True)
    client.post("/logout")
    assert "INC-0001" not in iniciar_sesion("tecnico2").get("/incidencias/mis-asignaciones").get_data(as_text=True)


def test_sin_efectos_parciales(app, monkeypatch, reloj, conn, en_atencion):  # S03: falla en la transacción
    def falla(*_args, **_kwargs):
        raise RuntimeError("falla simulada al guardar el evento")

    monkeypatch.setattr(servicios, "registrar_evento", falla)
    with app.app_context():
        with pytest.raises(RuntimeError):
            servicios.registrar_solucion(en_atencion, SOLUCION, usuario(get_db(), "tecnico1"), reloj)
    assert estado(conn) == "EN_ATENCION"
    assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 0
