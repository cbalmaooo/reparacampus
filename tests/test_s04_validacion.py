"""S04 — Validar o reabrir una incidencia (AC-S04-01 a AC-S04-14).

Esperados escritos a mano. El reloj de prueba arranca en 2026-10-13T12:00:00+00:00
y se avanza con reloj.avanzar(...); nunca se espera tiempo real ni se toca el reloj
del sistema.
"""
import pytest

from app import servicios
from app.db import get_db
from tests.flujo import SOLUCION_1, SOLUCION_2, hasta_pendiente, usuario

MOTIVO = "El daño sigue presente"


@pytest.fixture
def pendiente(app, reloj):
    with app.app_context():
        return hasta_pendiente(reloj)


@pytest.fixture
def cerrada(app, reloj, pendiente):
    """INC-0001 CERRADA el 2026-10-13T12:00:00+00:00."""
    with app.app_context():
        servicios.confirmar_solucion(pendiente, usuario("solicitante1"), reloj)
    return pendiente


def estado(conn):
    return conn.execute("SELECT estado FROM incidencias WHERE codigo = 'INC-0001'").fetchone()[0]


def contar(conn, sql):
    return conn.execute(sql).fetchone()[0]


def uid(conn, nombre):
    return conn.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (nombre,)).fetchone()[0]


def accion(client, codigo, nombre, motivo=None):
    datos = {} if motivo is None else {"motivo": motivo}
    return client.post(f"/incidencias/{codigo}/{nombre}", data=datos)


def test_confirmar(iniciar_sesion, conn, pendiente):  # AC-S04-01
    assert accion(iniciar_sesion("solicitante1"), pendiente, "confirmar").status_code == 302
    assert estado(conn) == "CERRADA"
    cierre = conn.execute("SELECT * FROM cierres").fetchone()
    assert cierre["solicitante_id"] == uid(conn, "solicitante1")
    assert cierre["cerrada_en"] == "2026-10-13T12:00:00+00:00"
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'CONFIRMAR'").fetchone()
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("PENDIENTE_VALIDACION", "CERRADA")


def test_rechazar_con_motivo_valido(iniciar_sesion, conn, pendiente):  # AC-S04-02
    assert accion(iniciar_sesion("solicitante1"), pendiente, "rechazar", MOTIVO).status_code == 302
    assert estado(conn) == "EN_ATENCION"
    assert conn.execute("SELECT tecnico_id FROM asignaciones").fetchone()[0] == uid(conn, "tecnico1")
    assert [f[0] for f in conn.execute("SELECT descripcion FROM soluciones")] == [SOLUCION_1]
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'RECHAZAR'").fetchone()
    assert evento["motivo"] == MOTIVO
    assert evento["usuario_id"] == uid(conn, "solicitante1")
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("PENDIENTE_VALIDACION", "EN_ATENCION")


@pytest.mark.parametrize("longitud, aceptado", [(10, True), (9, False), (300, True), (301, False)])
def test_limites_motivo_rechazo(iniciar_sesion, conn, pendiente, longitud, aceptado):  # AC-S04-03
    respuesta = accion(iniciar_sesion("solicitante1"), pendiente, "rechazar", "A" * longitud)
    if aceptado:
        assert respuesta.status_code == 302 and estado(conn) == "EN_ATENCION"
    else:
        assert respuesta.status_code == 400
        assert estado(conn) == "PENDIENTE_VALIDACION"
        assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'RECHAZAR'") == 0


def test_motivo_con_espacios(iniciar_sesion, conn, pendiente):  # AC-S04-04
    client = iniciar_sesion("solicitante1")
    assert accion(client, pendiente, "rechazar", "   " + "A" * 9 + "   ").status_code == 400
    assert accion(client, pendiente, "rechazar", "            ").status_code == 400
    assert estado(conn) == "PENDIENTE_VALIDACION"


def test_reabrir_dentro_del_plazo(iniciar_sesion, conn, reloj, cerrada):  # AC-S04-05
    reloj.avanzar(hours=24)
    respuesta = accion(iniciar_sesion("solicitante1"), cerrada, "reabrir", "La fuga volvió a aparecer")
    assert respuesta.status_code == 302
    assert estado(conn) == "EN_ATENCION"
    assert conn.execute("SELECT tecnico_id FROM asignaciones").fetchone()[0] == uid(conn, "tecnico1")
    assert contar(conn, "SELECT COUNT(*) FROM cierres") == 1
    assert contar(conn, "SELECT COUNT(*) FROM soluciones") == 1
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'REABRIR'").fetchone()
    assert evento["motivo"] == "La fuga volvió a aparecer"
    assert evento["creado_en"] == "2026-10-14T12:00:00+00:00"


def test_reabrir_exactamente_a_las_48_horas(iniciar_sesion, conn, reloj, cerrada):  # AC-S04-06
    reloj.avanzar(hours=48)  # cierre 13/10 12:00:00 → ahora 15/10 12:00:00
    assert accion(iniciar_sesion("solicitante1"), cerrada, "reabrir", MOTIVO).status_code == 302
    assert estado(conn) == "EN_ATENCION"


def test_reabrir_un_segundo_despues(iniciar_sesion, conn, reloj, cerrada):  # AC-S04-07
    reloj.avanzar(hours=48, seconds=1)  # ahora 15/10 12:00:01
    client = iniciar_sesion("solicitante1")
    # Una hora enviada por el cliente se ignora: manda el reloj del servidor.
    respuesta = client.post(f"/incidencias/{cerrada}/reabrir",
                            data={"motivo": MOTIVO, "ahora": "2026-10-13T12:00:00+00:00"})
    assert respuesta.status_code == 409
    assert "plazo de 48 horas" in respuesta.get_data(as_text=True)
    assert estado(conn) == "CERRADA"
    assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'REABRIR'") == 0


def test_plazo_desde_el_ultimo_cierre(app, iniciar_sesion, conn, reloj, cerrada):  # AC-S04-08
    with app.app_context():
        reloj.avanzar(hours=1)
        servicios.reabrir_incidencia(cerrada, MOTIVO, usuario("solicitante1"), reloj)
        reloj.avanzar(hours=39)  # T0 + 40 h: nueva solución y segundo cierre
        servicios.registrar_solucion(cerrada, SOLUCION_2, usuario("tecnico1"), reloj)
        servicios.confirmar_solucion(cerrada, usuario("solicitante1"), reloj)
    reloj.avanzar(hours=20)  # T0 + 60 h: 60 h desde el primer cierre, 20 h desde el último
    assert accion(iniciar_sesion("solicitante1"), cerrada, "reabrir", MOTIVO).status_code == 302
    assert estado(conn) == "EN_ATENCION"
    assert contar(conn, "SELECT COUNT(*) FROM cierres") == 2
    assert [f[0] for f in conn.execute("SELECT descripcion FROM soluciones ORDER BY id")] == [SOLUCION_1, SOLUCION_2]


@pytest.mark.parametrize("longitud", [9, 301])
def test_limites_motivo_reapertura(iniciar_sesion, conn, cerrada, longitud):  # AC-S04-09
    assert accion(iniciar_sesion("solicitante1"), cerrada, "reabrir", "A" * longitud).status_code == 400
    assert estado(conn) == "CERRADA"
    assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'REABRIR'") == 0


@pytest.mark.parametrize("operacion", ["confirmar", "rechazar"])
def test_solicitante_no_dueno(iniciar_sesion, conn, pendiente, operacion):  # AC-S04-10
    respuesta = accion(iniciar_sesion("solicitante2"), pendiente, operacion, MOTIVO)
    assert respuesta.status_code == 404
    html = respuesta.get_data(as_text=True)
    assert "Incidencia no encontrada" in html and "INC-0001" not in html
    assert estado(conn) == "PENDIENTE_VALIDACION"
    assert contar(conn, "SELECT COUNT(*) FROM cierres") == 0


def test_solicitante_no_dueno_no_reabre(iniciar_sesion, conn, cerrada):  # AC-S04-10
    assert accion(iniciar_sesion("solicitante2"), cerrada, "reabrir", MOTIVO).status_code == 404
    assert estado(conn) == "CERRADA"


@pytest.mark.parametrize("nombre", ["coordinador1", "tecnico1"])
@pytest.mark.parametrize("operacion", ["confirmar", "rechazar"])
def test_coordinador_o_tecnico(iniciar_sesion, conn, pendiente, nombre, operacion):  # AC-S04-11
    assert accion(iniciar_sesion(nombre), pendiente, operacion, MOTIVO).status_code == 403
    assert estado(conn) == "PENDIENTE_VALIDACION"


def test_coordinador_no_reabre(iniciar_sesion, conn, cerrada):  # AC-S04-11
    assert accion(iniciar_sesion("coordinador1"), cerrada, "reabrir", MOTIVO).status_code == 403
    assert estado(conn) == "CERRADA"


def test_sin_sesion_e_inexistente(client, iniciar_sesion, conn, pendiente):  # AC-S04-12
    respuesta = accion(client, pendiente, "confirmar")
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"
    assert accion(iniciar_sesion("solicitante1"), "INC-9999", "confirmar").status_code == 404
    assert estado(conn) == "PENDIENTE_VALIDACION"


def test_estados_incompatibles(app, iniciar_sesion, conn, reloj, pendiente):  # AC-S04-13
    client = iniciar_sesion("solicitante1")
    # PENDIENTE_VALIDACION: no se puede reabrir
    assert accion(client, pendiente, "reabrir", MOTIVO).status_code == 409
    # EN_ATENCION: no se puede confirmar, rechazar ni reabrir
    accion(client, pendiente, "rechazar", MOTIVO)
    for operacion in ("confirmar", "rechazar", "reabrir"):
        assert accion(client, pendiente, operacion, MOTIVO).status_code == 409
    assert estado(conn) == "EN_ATENCION"
    # CERRADA: no se puede confirmar ni rechazar
    with app.app_context():
        servicios.registrar_solucion(pendiente, SOLUCION_2, usuario("tecnico1"), reloj)
    accion(client, pendiente, "confirmar")
    assert accion(client, pendiente, "confirmar").status_code == 409
    assert accion(client, pendiente, "rechazar", MOTIVO).status_code == 409
    assert contar(conn, "SELECT COUNT(*) FROM cierres") == 1


def test_motivo_parecido_a_html(iniciar_sesion, conn, pendiente):  # AC-S04-14
    client = iniciar_sesion("solicitante1")
    corto = "<b>no</b>"  # 9 caracteres: se rechaza y vuelve al formulario escapado
    html = accion(client, pendiente, "rechazar", corto).get_data(as_text=True)
    assert "<b>no</b>" not in html and "&lt;b&gt;no&lt;/b&gt;" in html
    texto = "<script>x</script> sigue goteando"
    accion(client, pendiente, "rechazar", texto)
    assert conn.execute("SELECT motivo FROM eventos WHERE accion = 'RECHAZAR'").fetchone()[0] == texto


def test_vista_mis_reportes(iniciar_sesion, client, cerrada):  # T-S04 (vista)
    html = iniciar_sesion("solicitante1").get("/incidencias/mis-reportes").get_data(as_text=True)
    assert "INC-0001" in html and "Puedes reabrirla hasta 2026-10-15 12:00 UTC" in html
    client.post("/logout")
    assert "INC-0001" not in iniciar_sesion("solicitante2").get("/incidencias/mis-reportes").get_data(as_text=True)


def test_vista_oculta_reabrir_fuera_de_plazo(iniciar_sesion, reloj, cerrada):
    reloj.avanzar(hours=49)
    html = iniciar_sesion("solicitante1").get("/incidencias/mis-reportes").get_data(as_text=True)
    assert "Reabrir incidencia" not in html


def test_confirmar_sin_efectos_parciales(app, monkeypatch, conn, reloj, pendiente):
    def falla(*_args, **_kwargs):
        raise RuntimeError("falla simulada al guardar el evento")

    monkeypatch.setattr(servicios, "registrar_evento", falla)
    with app.app_context():
        with pytest.raises(RuntimeError):
            servicios.confirmar_solucion(pendiente, usuario("solicitante1"), reloj)
    assert estado(conn) == "PENDIENTE_VALIDACION"
    assert contar(conn, "SELECT COUNT(*) FROM cierres") == 0
