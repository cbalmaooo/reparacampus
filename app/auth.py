"""Autenticación y control de acceso (S05: AC-S05-01, AC-S05-02; transversal a S01–S04).

- La identidad se guarda en la sesión solo como id; el rol y el estado activo se leen
  de la base en cada petición, de modo que nunca se confía en datos del cliente.
- No existe selector de rol: el rol sale de la cuenta autenticada.
"""
import functools

from flask import Blueprint, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)

MENSAJE_CREDENCIALES = "Usuario o contraseña incorrectos"


@bp.before_app_request
def cargar_usuario():
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return
    fila = get_db().execute(
        "SELECT id, nombre_usuario, rol, activo FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    if fila is not None and fila["activo"] == 1:
        g.usuario = fila
    else:
        session.clear()  # cuenta borrada o desactivada: la sesión deja de valer


def login_requerido(*roles):
    """Exige sesión iniciada y, si se indican, uno de los roles permitidos."""

    def decorador(vista):
        @functools.wraps(vista)
        def envoltura(**kwargs):
            if g.usuario is None:
                return redirect(url_for("auth.login"))
            if roles and g.usuario["rol"] not in roles:
                abort(403)
            return vista(**kwargs)

        return envoltura

    return decorador


@bp.route("/login", methods=("GET", "POST"))
def login():
    if g.usuario is not None:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")
        fila = get_db().execute(
            "SELECT id, contrasena_hash, activo FROM usuarios WHERE nombre_usuario = ?", (nombre,)
        ).fetchone()
        valido = (
            fila is not None
            and fila["activo"] == 1
            and check_password_hash(fila["contrasena_hash"], contrasena)
        )
        if not valido:
            # Mismo mensaje para usuario inexistente, inactivo o contraseña errónea.
            return render_template("auth/login.html", error=MENSAJE_CREDENCIALES, usuario=nombre), 401
        session.clear()
        session["usuario_id"] = fila["id"]
        return redirect(url_for("inicio"))

    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
