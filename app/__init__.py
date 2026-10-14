import hmac
import os
import secrets

from flask import Flask, abort, g, render_template, request, session

from . import db
from .reloj import RelojSistema


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get("SECRET_KEY")
    if os.environ.get("APP_ENV", "development").lower() == "production" and not secret_key:
        raise RuntimeError("En producción debes configurar SECRET_KEY con un valor aleatorio fuera del repositorio.")
    app.config.from_mapping(
        SECRET_KEY=secret_key or "solo-desarrollo-local",
        DATABASE=os.path.join(app.instance_path, "reparacampus.sqlite"),
        RELOJ=RelojSistema(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("APP_ENV", "development").lower() == "production",
        CSRF_ENABLED=True,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    def csrf_token():
        token = session.get("_csrf_token")
        if token is None:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    @app.context_processor
    def inyectar_csrf_token():
        return {"csrf_token": csrf_token}

    @app.before_request
    def proteger_formularios():
        if not app.config.get("CSRF_ENABLED", True) or request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        esperado = session.get("_csrf_token")
        recibido = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        if not esperado or not recibido or not hmac.compare_digest(esperado, recibido):
            abort(400, description="Token CSRF ausente o inválido")

    from . import auth, rutas_incidencias

    app.register_blueprint(auth.bp)
    app.register_blueprint(rutas_incidencias.bp)

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

    @app.errorhandler(400)
    def solicitud_invalida(error):
        if request.path == "/login" and request.method == "POST":
            return render_template("auth/login.html", error="La sesión del formulario expiró. Recarga la página e inténtalo de nuevo."), 400
        return render_template("errores/400.html", mensaje="La solicitud no es válida o el token de seguridad expiró."), 400

    return app
