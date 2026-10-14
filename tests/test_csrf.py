"""Pruebas del control CSRF HTTP en la aplicación configurada con protección activa."""
import re

import pytest

from app import create_app
from app.db import init_db


def cliente_con_csrf(tmp_path):
    app = create_app({
        "TESTING": True,
        "CSRF_ENABLED": True,
        "SECRET_KEY": "test-secret-csrf",
        "DATABASE": str(tmp_path / "csrf.sqlite"),
    })
    with app.app_context():
        init_db(con_seed=True)
    return app.test_client()


def token_de(html):
    coincidencia = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert coincidencia, "El formulario debe incluir token CSRF"
    return coincidencia.group(1)


def test_login_rechaza_post_sin_token_csrf(tmp_path):
    client = cliente_con_csrf(tmp_path)
    respuesta = client.post("/login", data={
        "usuario": "solicitante1",
        "contrasena": "Solicitante1*2026",
    })
    assert respuesta.status_code == 400
    assert "sesión del formulario expiró" in respuesta.get_data(as_text=True).lower()


def test_login_acepta_token_csrf_de_sesion(tmp_path):
    client = cliente_con_csrf(tmp_path)
    pagina = client.get("/login")
    token = token_de(pagina.get_data(as_text=True))
    respuesta = client.post("/login", data={
        "usuario": "solicitante1",
        "contrasena": "Solicitante1*2026",
        "csrf_token": token,
    })
    assert respuesta.status_code == 302


def test_login_rechaza_token_csrf_invalido(tmp_path):
    client = cliente_con_csrf(tmp_path)
    client.get("/login")
    respuesta = client.post("/login", data={
        "usuario": "solicitante1",
        "contrasena": "Solicitante1*2026",
        "csrf_token": "token-falso",
    })
    assert respuesta.status_code == 400

def test_solicitud_mutable_rechaza_post_sin_token_despues_de_login(tmp_path):
    client = cliente_con_csrf(tmp_path)
    token = token_de(client.get("/login").get_data(as_text=True))
    assert client.post("/login", data={
        "usuario": "solicitante1",
        "contrasena": "Solicitante1*2026",
        "csrf_token": token,
    }).status_code == 302
    respuesta = client.post("/logout")
    assert respuesta.status_code == 400
    # La solicitud sin token no debe cerrar la sesión autenticada.
    assert client.get("/").status_code == 200


def test_produccion_exige_secret_key(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"DATABASE": str(tmp_path / "produccion.sqlite")})
