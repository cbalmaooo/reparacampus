"""Cada prueba usa su propia base SQLite en archivo temporal (datos independientes)
y un reloj fijo, para que las fechas esperadas se puedan escribir a mano."""
from datetime import datetime, timezone

import pytest

from app import create_app
from app.db import get_db, init_db
from app.reloj import RelojFijo

CONTRASENAS = {
    "solicitante1": "Solicitante1*2026",
    "solicitante2": "Solicitante2*2026",
    "coordinador1": "Coordinador1*2026",
    "tecnico1": "Tecnico1*2026",
    "tecnico2": "Tecnico2*2026",
}

INSTANTE_INICIAL = datetime(2026, 10, 13, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def reloj():
    return RelojFijo(INSTANTE_INICIAL)


@pytest.fixture
def app(tmp_path, reloj):
    app = create_app({
        "TESTING": True,
        "CSRF_ENABLED": False,  # Las pruebas de flujos prueban negocio; test_csrf valida el control HTTP real.
        "DATABASE": str(tmp_path / "prueba.sqlite"),
        "RELOJ": reloj,
    })
    with app.app_context():
        init_db(con_seed=True)
    return app


@pytest.fixture
def conn(app):
    with app.app_context():
        yield get_db()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def iniciar_sesion(client):
    def _iniciar(usuario):
        respuesta = client.post("/login", data={"usuario": usuario, "contrasena": CONTRASENAS[usuario]})
        assert respuesta.status_code == 302, f"no se pudo iniciar sesión como {usuario}"
        return client
    return _iniciar
