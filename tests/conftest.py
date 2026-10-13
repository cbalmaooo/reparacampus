"""Cada prueba usa su propia base SQLite en archivo temporal (datos independientes)."""
import pytest

from app import create_app
from app.db import get_db, init_db


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "prueba.sqlite")})
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
