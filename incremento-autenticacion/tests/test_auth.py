"""Pruebas de autenticación y control de acceso (AC-S05-01, AC-S05-08; transversal).

Los esperados están escritos a mano. Cada prueba usa su propia base temporal.
"""
from werkzeug.security import generate_password_hash

from app.auth import login_requerido


def iniciar(client, usuario, contrasena):
    return client.post("/login", data={"usuario": usuario, "contrasena": contrasena})


def test_login_correcto_y_vista_de_rol(client):  # AC-S05-01
    respuesta = iniciar(client, "solicitante1", "Solicitante1*2026")
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/"
    inicio = client.get("/")
    assert inicio.status_code == 200
    assert "solicitante1" in inicio.get_data(as_text=True)


def test_logout_invalida_la_sesion(client):  # AC-S05-01
    iniciar(client, "coordinador1", "Coordinador1*2026")
    assert client.post("/logout").status_code == 302
    respuesta = client.get("/")
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"


def test_contrasena_incorrecta_no_crea_sesion(client):  # AC-S05-01
    respuesta = iniciar(client, "tecnico1", "incorrecta")
    assert respuesta.status_code == 401
    assert "Usuario o contraseña incorrectos" in respuesta.get_data(as_text=True)
    with client.session_transaction() as sesion:
        assert "usuario_id" not in sesion


def test_usuario_inexistente_mismo_mensaje(client):  # no revela qué dato falla
    respuesta = iniciar(client, "nadie", "Solicitante1*2026")
    assert respuesta.status_code == 401
    assert "Usuario o contraseña incorrectos" in respuesta.get_data(as_text=True)


def test_tecnico_inactivo_no_inicia_sesion(app, client):  # S02: técnico inactivo
    with app.app_context():
        from app.db import get_db
        get_db().execute(
            "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol, activo) VALUES (?, ?, 'TECNICO', 0)",
            ("tecnico3", generate_password_hash("Tecnico3*2026")),
        )
    respuesta = iniciar(client, "tecnico3", "Tecnico3*2026")
    assert respuesta.status_code == 401


def test_cuenta_desactivada_pierde_la_sesion(app, client):
    iniciar(client, "tecnico2", "Tecnico2*2026")
    with app.app_context():
        from app.db import get_db
        get_db().execute("UPDATE usuarios SET activo = 0 WHERE nombre_usuario = 'tecnico2'")
    respuesta = client.get("/")
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"


def test_sin_sesion_redirige_a_login(client):  # AC-S01-11, AC-S02-08
    respuesta = client.get("/")
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/login"


def test_rol_no_permitido_recibe_403(app):  # AC-S05-13 (mecanismo)
    app.add_url_rule(
        "/solo-coordinador", "solo_coordinador",
        login_requerido("COORDINADOR")(lambda: "ok"),
    )
    client = app.test_client()
    iniciar(client, "solicitante1", "Solicitante1*2026")
    assert client.get("/solo-coordinador").status_code == 403
    client.post("/logout")
    iniciar(client, "coordinador1", "Coordinador1*2026")
    assert client.get("/solo-coordinador").get_data(as_text=True) == "ok"


def test_texto_del_usuario_se_escapa(client):  # AC-S05-18 (mecanismo de escapado)
    respuesta = iniciar(client, "<script>alert(1)</script>", "x")
    html = respuesta.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
