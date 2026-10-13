"""S02 — Asignar una incidencia (AC-S02-06 a AC-S02-13).

AC-S02-01 a 05 (prioridad) se prueban en test_dominio.py y test_s01_registro.py.
Esperados escritos a mano; reloj fijo en 2026-10-13T12:00:00+00:00.
"""
import pytest
from werkzeug.security import generate_password_hash

from app import servicios
from app.db import get_db

REGISTRO = {
    "ubicacion": "AULA-201",
    "categoria": "MOBILIARIO",
    "descripcion": "La silla del docente tiene una pata rota",
    "impacto": "BAJO",
    "riesgo_personas": "false",
}


@pytest.fixture
def incidencia(app, reloj):
    """Crea INC-0001 REGISTRADA de solicitante1 usando el servicio de S01."""
    with app.app_context():
        usuario = get_db().execute(
            "SELECT id, rol FROM usuarios WHERE nombre_usuario = 'solicitante1'"
        ).fetchone()
        return servicios.registrar_incidencia(REGISTRO, usuario, reloj)["codigo"]


def uid(conn, nombre):
    return conn.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (nombre,)).fetchone()[0]


def estado(conn, codigo="INC-0001"):
    return conn.execute("SELECT estado FROM incidencias WHERE codigo = ?", (codigo,)).fetchone()[0]


def contar(conn, sql):
    return conn.execute(sql).fetchone()[0]


def asignar(client, codigo, tecnico_id):
    return client.post(f"/incidencias/{codigo}/asignar", data={"tecnico_id": str(tecnico_id)})


def test_asignacion_valida(iniciar_sesion, conn, incidencia):  # AC-S02-06
    respuesta = asignar(iniciar_sesion("coordinador1"), incidencia, uid(conn, "tecnico1"))
    assert respuesta.status_code == 302
    assert estado(conn) == "ASIGNADA"
    asignacion = conn.execute("SELECT * FROM asignaciones").fetchone()
    assert asignacion["tecnico_id"] == uid(conn, "tecnico1")
    assert asignacion["coordinador_id"] == uid(conn, "coordinador1")
    assert asignacion["asignada_en"] == "2026-10-13T12:00:00+00:00"
    evento = conn.execute("SELECT * FROM eventos WHERE accion = 'ASIGNAR'").fetchone()
    assert evento["usuario_id"] == uid(conn, "coordinador1")
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("REGISTRADA", "ASIGNADA")
    assert evento["creado_en"] == "2026-10-13T12:00:00+00:00"
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 2  # REGISTRAR + ASIGNAR


@pytest.mark.parametrize("usuario", ["solicitante1", "tecnico1"])
def test_rol_sin_permiso(iniciar_sesion, conn, incidencia, usuario):  # AC-S02-07
    client = iniciar_sesion(usuario)
    assert asignar(client, incidencia, uid(conn, "tecnico2")).status_code == 403
    assert client.get("/incidencias/por-asignar").status_code == 403
    assert estado(conn) == "REGISTRADA"
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 1


def test_sin_sesion(client, conn, incidencia):  # AC-S02-08
    respuesta = asignar(client, incidencia, uid(conn, "tecnico1"))
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"
    assert estado(conn) == "REGISTRADA"


def test_tecnico_inactivo(iniciar_sesion, conn, incidencia):  # AC-S02-09
    conn.execute(
        "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol, activo) VALUES ('tecnico3', ?, 'TECNICO', 0)",
        (generate_password_hash("Tecnico3*2026"),),
    )
    respuesta = asignar(iniciar_sesion("coordinador1"), incidencia, uid(conn, "tecnico3"))
    assert respuesta.status_code == 400
    assert "El técnico seleccionado está inactivo" in respuesta.get_data(as_text=True)
    assert estado(conn) == "REGISTRADA"
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 1


@pytest.mark.parametrize("destino", ["solicitante2", 9999, "abc", ""])
def test_destinatario_invalido(iniciar_sesion, conn, incidencia, destino):  # AC-S02-10
    tecnico_id = uid(conn, destino) if destino == "solicitante2" else destino
    respuesta = asignar(iniciar_sesion("coordinador1"), incidencia, tecnico_id)
    assert respuesta.status_code == 400
    assert estado(conn) == "REGISTRADA"
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 1


@pytest.mark.parametrize("segundo", ["tecnico2", "tecnico1"])
def test_reasignacion_prohibida(iniciar_sesion, conn, incidencia, segundo):  # AC-S02-11
    client = iniciar_sesion("coordinador1")
    asignar(client, incidencia, uid(conn, "tecnico1"))
    respuesta = asignar(client, incidencia, uid(conn, segundo))
    assert respuesta.status_code == 409
    assert conn.execute("SELECT tecnico_id FROM asignaciones").fetchone()[0] == uid(conn, "tecnico1")
    assert contar(conn, "SELECT COUNT(*) FROM eventos WHERE accion = 'ASIGNAR'") == 1


@pytest.mark.parametrize("estado_actual", ["EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA"])
def test_otros_estados_incompatibles(iniciar_sesion, conn, incidencia, estado_actual):  # AC-S02-12
    conn.execute("UPDATE incidencias SET estado = ? WHERE codigo = ?", (estado_actual, incidencia))
    respuesta = asignar(iniciar_sesion("coordinador1"), incidencia, uid(conn, "tecnico1"))
    assert respuesta.status_code == 409
    assert estado(conn) == estado_actual
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 1


def test_incidencia_inexistente(iniciar_sesion, conn):  # AC-S02-13
    respuesta = asignar(iniciar_sesion("coordinador1"), "INC-9999", uid(conn, "tecnico1"))
    assert respuesta.status_code == 404
    assert "Incidencia no encontrada" in respuesta.get_data(as_text=True)
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
    assert contar(conn, "SELECT COUNT(*) FROM eventos") == 0


def test_vista_muestra_solo_registradas_y_tecnicos_activos(iniciar_sesion, conn, app, reloj):  # T-S02-08
    with app.app_context():
        usuario = get_db().execute("SELECT id, rol FROM usuarios WHERE nombre_usuario = 'solicitante1'").fetchone()
        servicios.registrar_incidencia(REGISTRO, usuario, reloj)  # INC-0001
        servicios.registrar_incidencia(REGISTRO, usuario, reloj)  # INC-0002
    conn.execute("UPDATE incidencias SET estado = 'ASIGNADA' WHERE codigo = 'INC-0002'")
    conn.execute(
        "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol, activo) VALUES ('tecnico3', 'x', 'TECNICO', 0)"
    )
    html = iniciar_sesion("coordinador1").get("/incidencias/por-asignar").get_data(as_text=True)
    assert "INC-0001" in html and "INC-0002" not in html
    assert "tecnico1" in html and "tecnico2" in html
    assert "tecnico3" not in html and "solicitante2" not in html


def test_sin_efectos_parciales(app, monkeypatch, reloj, conn, incidencia):  # S02: falla en la transacción
    def falla(*_args, **_kwargs):
        raise RuntimeError("falla simulada al guardar el evento")

    monkeypatch.setattr(servicios, "registrar_evento", falla)
    with app.app_context():
        db = get_db()
        coordinador = db.execute("SELECT id, rol FROM usuarios WHERE nombre_usuario = 'coordinador1'").fetchone()
        with pytest.raises(RuntimeError):
            servicios.asignar_incidencia(incidencia, uid(db, "tecnico1"), coordinador, reloj)
    assert estado(conn) == "REGISTRADA"
    assert contar(conn, "SELECT COUNT(*) FROM asignaciones") == 0
