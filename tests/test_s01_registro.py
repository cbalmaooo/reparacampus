"""S01 — Registrar una incidencia (AC-S01-01 a AC-S01-13).

Esperados escritos a mano; reloj fijo en 2026-10-13T12:00:00+00:00.
"""
import pytest

from app import create_app, servicios
from app.db import get_db
from app.dominio import ErrorValidacion

VALIDOS = {
    "ubicacion": "LAB-01",
    "categoria": "ELECTRICIDAD",
    "descripcion": "El tomacorriente del puesto 4 hace chispas",
    "impacto": "ALTO",
    "riesgo_personas": "true",
}


def con(**cambios):
    datos = dict(VALIDOS)
    datos.update(cambios)
    return {k: v for k, v in datos.items() if v is not None}


def contar(conn, tabla):
    return conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def registrar(client, datos):
    return client.post("/incidencias/", data=datos)


def test_registro_valido(iniciar_sesion, conn):  # AC-S01-01
    respuesta = registrar(iniciar_sesion("solicitante1"), VALIDOS)
    assert respuesta.status_code == 302
    fila = conn.execute(
        "SELECT i.*, u.nombre_usuario FROM incidencias i JOIN usuarios u ON u.id = i.solicitante_id"
    ).fetchone()
    assert fila["codigo"] == "INC-0001"
    assert fila["nombre_usuario"] == "solicitante1"
    assert fila["estado"] == "REGISTRADA"
    assert fila["prioridad"] == "CRITICA"
    assert fila["creada_en"] == "2026-10-13T12:00:00+00:00"
    eventos = conn.execute("SELECT * FROM eventos").fetchall()
    assert len(eventos) == 1
    assert eventos[0]["accion"] == "REGISTRAR"
    assert eventos[0]["estado_anterior"] is None and eventos[0]["estado_nuevo"] == "REGISTRADA"
    assert eventos[0]["usuario_id"] == fila["solicitante_id"]
    assert eventos[0]["creado_en"] == "2026-10-13T12:00:00+00:00"


def test_mensaje_de_exito_con_codigo(iniciar_sesion):  # AC-S01-01 (salida visible)
    client = iniciar_sesion("solicitante1")
    respuesta = client.post("/incidencias/", data=VALIDOS, follow_redirects=True)
    assert "Incidencia INC-0001 registrada con prioridad CRITICA." in respuesta.get_data(as_text=True)


def test_codigo_consecutivo(iniciar_sesion, conn):  # supuesto P1
    client = iniciar_sesion("solicitante1")
    registrar(client, VALIDOS)
    registrar(client, VALIDOS)
    codigos = [f[0] for f in conn.execute("SELECT codigo FROM incidencias ORDER BY id")]
    assert codigos == ["INC-0001", "INC-0002"]


def test_campos_obligatorios_vacios(iniciar_sesion, conn):  # AC-S01-02
    respuesta = registrar(iniciar_sesion("solicitante1"), con(categoria=None, impacto=""))
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 400
    assert "Falta el campo categoría" in html and "Falta el campo impacto" in html
    assert contar(conn, "incidencias") == 0 and contar(conn, "eventos") == 0


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("ubicacion", "LAB-99"),          # AC-S01-03
        ("categoria", "PINTURA"),         # AC-S01-03
        ("impacto", "MEDIO"),             # AC-S01-04
        ("riesgo_personas", "quizas"),    # AC-S01-05
    ],
)
def test_valores_no_permitidos(iniciar_sesion, conn, campo, valor):
    respuesta = registrar(iniciar_sesion("solicitante1"), con(**{campo: valor}))
    assert respuesta.status_code == 400
    assert contar(conn, "incidencias") == 0 and contar(conn, "eventos") == 0


@pytest.mark.parametrize(
    "longitud, aceptada",
    [(20, True), (19, False), (500, True), (501, False)],  # AC-S01-06, AC-S01-07
)
def test_limites_de_descripcion(iniciar_sesion, conn, longitud, aceptada):
    respuesta = registrar(iniciar_sesion("solicitante1"), con(descripcion="A" * longitud))
    assert (respuesta.status_code == 302) is aceptada
    assert contar(conn, "incidencias") == (1 if aceptada else 0)


def test_mensajes_de_limite(iniciar_sesion):  # AC-S01-06, AC-S01-07
    client = iniciar_sesion("solicitante1")
    corta = registrar(client, con(descripcion="A" * 19)).get_data(as_text=True)
    larga = registrar(client, con(descripcion="A" * 501)).get_data(as_text=True)
    assert "La descripción debe tener al menos 20 caracteres" in corta
    assert "La descripción no puede superar 500 caracteres" in larga


def test_espacios_externos(iniciar_sesion, conn):  # AC-S01-08
    client = iniciar_sesion("solicitante1")
    assert registrar(client, con(descripcion="   " + "A" * 19 + "   ")).status_code == 400
    assert registrar(client, con(descripcion="        ")).status_code == 400
    assert contar(conn, "incidencias") == 0
    assert registrar(client, con(descripcion="   " + "A" * 20 + "   ")).status_code == 302
    assert conn.execute("SELECT descripcion FROM incidencias").fetchone()[0] == "A" * 20


def test_campos_del_servidor_ignoran_al_cliente(iniciar_sesion, conn):  # AC-S01-09, AC-S02-05
    datos = con(riesgo_personas="false", impacto="BAJO")
    datos.update({"estado": "CERRADA", "prioridad": "CRITICA", "solicitante_id": "2", "codigo": "X-1"})
    registrar(iniciar_sesion("solicitante1"), datos)
    fila = conn.execute(
        "SELECT i.estado, i.prioridad, i.codigo, u.nombre_usuario FROM incidencias i"
        " JOIN usuarios u ON u.id = i.solicitante_id"
    ).fetchone()
    assert (fila["estado"], fila["prioridad"], fila["codigo"], fila["nombre_usuario"]) == (
        "REGISTRADA", "NORMAL", "INC-0001", "solicitante1"
    )


@pytest.mark.parametrize("usuario", ["coordinador1", "tecnico1"])
def test_rol_sin_permiso(iniciar_sesion, conn, usuario):  # AC-S01-10
    client = iniciar_sesion(usuario)
    assert client.get("/incidencias/nueva").status_code == 403
    assert registrar(client, VALIDOS).status_code == 403
    assert contar(conn, "incidencias") == 0 and contar(conn, "eventos") == 0


def test_sin_sesion(client, conn):  # AC-S01-11
    respuesta = registrar(client, VALIDOS)
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"
    assert contar(conn, "incidencias") == 0


def test_texto_parecido_a_html(iniciar_sesion, conn):  # AC-S01-12
    client = iniciar_sesion("solicitante1")
    texto = "<b>Fuga</b> de agua en el baño del segundo piso"
    registrar(client, con(descripcion=texto))
    assert conn.execute("SELECT descripcion FROM incidencias").fetchone()[0] == texto
    # Al volver a mostrar el formulario con error, el texto aparece escapado.
    html = registrar(client, con(descripcion="<b>corta</b>")).get_data(as_text=True)
    assert "<b>corta</b>" not in html and "&lt;b&gt;corta&lt;/b&gt;" in html


def test_persistencia_tras_reinicio(app, iniciar_sesion, reloj):  # AC-S01-13
    registrar(iniciar_sesion("solicitante1"), VALIDOS)
    reiniciada = create_app({"TESTING": True, "DATABASE": app.config["DATABASE"], "RELOJ": reloj})
    with reiniciada.app_context():
        db = get_db()
        assert db.execute("SELECT codigo FROM incidencias").fetchone()[0] == "INC-0001"
        assert db.execute("SELECT COUNT(*) FROM eventos").fetchone()[0] == 1


def test_sin_efectos_parciales(app, monkeypatch, reloj):  # S01: falla durante la transacción
    def falla(*_args, **_kwargs):
        raise RuntimeError("falla simulada al guardar el evento")

    monkeypatch.setattr(servicios, "registrar_evento", falla)
    with app.app_context():
        usuario = get_db().execute(
            "SELECT id, rol FROM usuarios WHERE nombre_usuario = 'solicitante1'"
        ).fetchone()
        with pytest.raises(RuntimeError):
            servicios.registrar_incidencia(VALIDOS, usuario, reloj)
        assert get_db().execute("SELECT COUNT(*) FROM incidencias").fetchone()[0] == 0


def test_servicio_reporta_todos_los_errores(app, reloj):  # AC-S01-02 (capa de servicio)
    with app.app_context():
        usuario = get_db().execute(
            "SELECT id, rol FROM usuarios WHERE nombre_usuario = 'solicitante1'"
        ).fetchone()
        with pytest.raises(ErrorValidacion) as error:
            servicios.registrar_incidencia({"descripcion": "corta"}, usuario, reloj)
    assert len(error.value.args) == 5
