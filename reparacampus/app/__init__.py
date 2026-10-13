import os

from flask import Flask

from . import db
from .reloj import RelojSistema


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "solo-desarrollo-local"),
        DATABASE=os.path.join(app.instance_path, "reparacampus.sqlite"),
        RELOJ=RelojSistema(),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    @app.get("/salud")
    def salud():
        return {"estado": "ok"}

    return app
