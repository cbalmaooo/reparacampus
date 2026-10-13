"""S05 — Consultas, historial y tablero (AC-S05-03 a AC-S05-18).

AC-S05-01 y 02 (sesión y hash) están en test_auth.py y test_seed.py; la regla de
redondeo de AC-S05-17 también en test_dominio.py. Esperados escritos a mano.
"""
import re

import pytest

from app import servicios
from app.db import get_db
from tests.flujo import REGISTRO, SOLUCION_1, SOLUCION_2, hasta_pendiente, usuario

CRITICA = dict(REGISTRO, riesgo_personas="true", impacto="ALTO")
ALTA = dict(REGISTRO, riesgo_personas="false", impacto="ALTO")
NORMAL = dict(REGISTRO, riesgo_personas="false", impacto="BAJO")


def codigos(html):
    return set(re.findall(r"INC-\d{4}", html))


def registrar(datos, solicitante, reloj):
    return servicios.registrar_incidencia(datos, usuario(solicitante), reloj)["codigo"]


def asignar(codigo, tecnico, reloj):
    servicios.asignar_incidencia(codigo, usuario(tecnico)["id"], usuario("coordinador1"), reloj)


@pytest.fixture
def escenario(app, reloj):
    """INC-0001 sol1 CRITICA asignada a t1 · INC-0002 sol1 NORMAL registrada
    · INC-0003 sol2 CRITICA registrada · INC-0004 sol2 ALTA asignada a t2."""
    with app.app_context():
        registrar(CRITICA, "solicitante1", reloj)
        registrar(NORMAL, "solicitante1", reloj)
        registrar(CRITICA, "solicitante2", reloj)
        registrar(ALTA, "solicitante2", reloj)
        asignar("INC-0001", "tecnico1", reloj)
        asignar("INC-0004", "tecnico2", reloj)


def test_solicitante_ve_solo_las_propias(iniciar_sesion, escenario):  # AC-S05-03
    html = iniciar_sesion("solicitante1").get("/incidencias/").get_data(as_text=True)
    assert codigos(html) == {"INC-0001", "INC-0002"}


def test_solicitante_no_lee_incidencia_ajena(iniciar_sesion, escenario):  # AC-S05-04
    respuesta = iniciar_sesion("solicitante1").get("/incidencias/INC-0003")
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 404
    assert "Incidencia no encontrada" in html and "solicitante2" not in html


def test_tecnico_ve_solo_sus_asignaciones(iniciar_sesion, escenario):  # AC-S05-05
    client = iniciar_sesion("tecnico1")
    assert codigos(client.get("/incidencias/").get_data(as_text=True)) == {"INC-0001"}
    assert client.get("/incidencias/INC-0004").status_code == 404
    assert client.get("/incidencias/INC-0001").status_code == 200


def test_coordinador_ve_todas(iniciar_sesion, escenario):  # AC-S05-06
    html = iniciar_sesion("coordinador1").get("/incidencias/").get_data(as_text=True)
    assert codigos(html) == {"INC-0001", "INC-0002", "INC-0003", "INC-0004"}


@pytest.mark.parametrize(
    "consulta, esperados",
    [
        ("estado=REGISTRADA", {"INC-0002", "INC-0003"}),
        ("prioridad=CRITICA", {"INC-0001", "INC-0003"}),
        ("estado=REGISTRADA&prioridad=CRITICA", {"INC-0003"}),
        ("estado=&prioridad=", {"INC-0001", "INC-0002", "INC-0003", "INC-0004"}),
        ("estado=CERRADA", set()),
    ],
)
def test_filtros(iniciar_sesion, escenario, consulta, esperados):  # AC-S05-07
    html = iniciar_sesion("coordinador1").get(f"/incidencias/?{consulta}").get_data(as_text=True)
    assert codigos(html) == esperados


def test_filtros_respetan_permisos(iniciar_sesion, escenario):  # AC-S05-08
    html = iniciar_sesion("solicitante1").get("/incidencias/?prioridad=CRITICA").get_data(as_text=True)
    assert codigos(html) == {"INC-0001"}


@pytest.mark.parametrize("consulta", ["estado=BORRADA", "prioridad=URGENTE"])
def test_filtro_invalido(iniciar_sesion, escenario, consulta):  # AC-S05-09
    respuesta = iniciar_sesion("solicitante1").get(f"/incidencias/?{consulta}")
    assert respuesta.status_code == 400
    html = respuesta.get_data(as_text=True)
    assert "Filtro no válido" in html and codigos(html) == set()


def test_historial_completo_y_ordenado(app, iniciar_sesion, reloj):  # AC-S05-10
    with app.app_context():
        codigo = hasta_pendiente(reloj)
        sol, tec = usuario("solicitante1"), usuario("tecnico1")
        servicios.rechazar_solucion(codigo, "El daño sigue presente", sol, reloj)
        servicios.registrar_solucion(codigo, SOLUCION_2, tec, reloj)
        servicios.confirmar_solucion(codigo, sol, reloj)
        reloj.avanzar(hours=2)
        servicios.reabrir_incidencia(codigo, "La falla volvió a aparecer", sol, reloj)
    html = iniciar_sesion("solicitante1").get(f"/incidencias/{codigo}").get_data(as_text=True)
    etiquetas = ["Registró la incidencia", "Asignó la incidencia", "Inició la atención",
                 "Registró una solución", "Rechazó la solución", "Registró una solución",
                 "Confirmó la solución (cierre)", "Reabrió la incidencia"]
    posicion = 0
    for etiqueta in etiquetas:  # cada etiqueta aparece después de la anterior
        posicion = html.index(etiqueta, posicion) + 1
    for texto in (SOLUCION_1, SOLUCION_2, "El daño sigue presente", "La falla volvió a aparecer",
                  "a tecnico1", "2026-10-13 12:00 UTC", "2026-10-13 14:00:00 UTC"):
        assert texto in html


def test_operacion_fallida_no_deja_evento(app, iniciar_sesion, conn, escenario):  # AC-S05-11
    antes = conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
    assert iniciar_sesion("tecnico2").post("/incidencias/INC-0001/iniciar").status_code == 403
    assert conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0] == antes


def test_historial_sin_rutas_de_edicion(iniciar_sesion, conn, escenario):  # AC-S05-12
    client = iniciar_sesion("coordinador1")
    antes = conn.execute("SELECT * FROM eventos ORDER BY id").fetchall()
    assert client.delete("/incidencias/INC-0001").status_code == 405
    assert client.put("/incidencias/INC-0001").status_code == 405
    assert client.post("/incidencias/INC-0001/eventos/1/editar").status_code == 404
    assert conn.execute("SELECT * FROM eventos ORDER BY id").fetchall() == antes


@pytest.mark.parametrize("nombre", ["solicitante1", "tecnico1"])
def test_tablero_restringido(iniciar_sesion, nombre):  # AC-S05-13
    respuesta = iniciar_sesion(nombre).get("/incidencias/tablero")
    assert respuesta.status_code == 403 and "%" not in respuesta.get_data(as_text=True)


def test_tablero_vacio(app, iniciar_sesion):  # AC-S05-14
    with app.app_context():
        t = servicios.calcular_tablero()
    assert t["por_estado"] == {"REGISTRADA": 0, "ASIGNADA": 0, "EN_ATENCION": 0,
                               "PENDIENTE_VALIDACION": 0, "CERRADA": 0}
    assert t["por_prioridad"] == {"CRITICA": 0, "ALTA": 0, "NORMAL": 0}
    assert list(t["criticas_abiertas"]) == [] and t["porcentaje_cierre"] == "0,0 %"
    html = iniciar_sesion("coordinador1").get("/incidencias/tablero").get_data(as_text=True)
    assert "0,0 %" in html and "No hay incidencias críticas abiertas" in html


@pytest.fixture
def cuatro(app, reloj):
    """INC-0001 CERRADA CRITICA · INC-0002 EN_ATENCION CRITICA · INC-0003 REGISTRADA ALTA
    · INC-0004 ASIGNADA NORMAL."""
    with app.app_context():
        primera = hasta_pendiente(reloj)  # CRITICA
        servicios.confirmar_solucion(primera, usuario("solicitante1"), reloj)
        segunda = registrar(CRITICA, "solicitante1", reloj)
        asignar(segunda, "tecnico1", reloj)
        servicios.iniciar_atencion(segunda, usuario("tecnico1"), reloj)
        registrar(ALTA, "solicitante2", reloj)
        cuarta = registrar(NORMAL, "solicitante2", reloj)
        asignar(cuarta, "tecnico2", reloj)


def criticas_html(html):
    return codigos(html[html.index('id="criticas"'):])


def test_tablero_con_datos(app, iniciar_sesion, cuatro):  # AC-S05-15
    with app.app_context():
        t = servicios.calcular_tablero()
    assert t["por_estado"] == {"REGISTRADA": 1, "ASIGNADA": 1, "EN_ATENCION": 1,
                               "PENDIENTE_VALIDACION": 0, "CERRADA": 1}
    assert t["por_prioridad"] == {"CRITICA": 2, "ALTA": 1, "NORMAL": 1}
    assert [f["codigo"] for f in t["criticas_abiertas"]] == ["INC-0002"]
    assert t["porcentaje_cierre"] == "25,0 %"
    html = iniciar_sesion("coordinador1").get("/incidencias/tablero").get_data(as_text=True)
    assert "25,0 %" in html and criticas_html(html) == {"INC-0002"}


def test_reapertura_reduce_el_porcentaje(app, iniciar_sesion, conn, reloj, cuatro):  # AC-S05-16
    with app.app_context():
        reloj.avanzar(hours=1)
        servicios.reabrir_incidencia("INC-0001", "La falla volvió a aparecer", usuario("solicitante1"), reloj)
    html = iniciar_sesion("coordinador1").get("/incidencias/tablero").get_data(as_text=True)
    assert "0,0 %" in html
    assert criticas_html(html) == {"INC-0001", "INC-0002"}
    assert conn.execute("SELECT COUNT(*) FROM cierres").fetchone()[0] == 1


def test_redondeo_un_tercio(app, reloj):  # AC-S05-17
    with app.app_context():
        primera = hasta_pendiente(reloj)
        servicios.confirmar_solucion(primera, usuario("solicitante1"), reloj)
        registrar(NORMAL, "solicitante1", reloj)
        registrar(NORMAL, "solicitante1", reloj)
        assert servicios.calcular_tablero()["porcentaje_cierre"] == "33,3 %"


def test_cien_por_ciento_tras_int01(app, reloj):  # INT-01 (tablero)
    with app.app_context():
        primera = hasta_pendiente(reloj)
        servicios.confirmar_solucion(primera, usuario("solicitante1"), reloj)
        assert servicios.calcular_tablero()["porcentaje_cierre"] == "100,0 %"


def test_textos_escapados_en_consultas(app, iniciar_sesion, reloj):  # AC-S05-18
    with app.app_context():
        codigo = servicios.registrar_incidencia(
            dict(REGISTRO, descripcion="<b>Fuga</b> en el baño del segundo piso"),
            usuario("solicitante1"), reloj)["codigo"]
        asignar(codigo, "tecnico1", reloj)
        servicios.iniciar_atencion(codigo, usuario("tecnico1"), reloj)
        servicios.registrar_solucion(codigo, SOLUCION_1, usuario("tecnico1"), reloj)
        servicios.rechazar_solucion(codigo, "<script>x</script> sigue goteando", usuario("solicitante1"), reloj)
    html = iniciar_sesion("solicitante1").get(f"/incidencias/{codigo}").get_data(as_text=True)
    assert "<b>Fuga</b>" not in html and "&lt;b&gt;Fuga&lt;/b&gt;" in html
    assert "<script>x</script>" not in html and "&lt;script&gt;x&lt;/script&gt;" in html


def test_sin_sesion_redirige(client):
    for ruta in ("/incidencias/", "/incidencias/tablero", "/incidencias/INC-0001"):
        respuesta = client.get(ruta)
        assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"
