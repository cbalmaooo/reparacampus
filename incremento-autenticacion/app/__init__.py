import os

from flask import Flask, g, render_template

from . import db
from .reloj import RelojSistema


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "solo-desarrollo-local"),
        DATABASE=os.path.join(app.instance_path, "reparacampus.sqlite"),
        RELOJ=RelojSistema(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    @app.get("/")
    @auth.login_requerido()
    def inicio():
        return render_template("inicio.html", usuario=g.usuario)

    @app.get("/salud")
    def salud():
        return {"estado": "ok"}

    @app.errorhandler(403)
    def prohibido(_error):
        return render_template("errores/403.html"), 403

    return app
