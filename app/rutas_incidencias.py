"""Rutas HTTP de incidencias. La identidad viene siempre de la sesión (g.usuario)."""
from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from .auth import login_requerido
from .dominio import CATEGORIAS, UBICACIONES, ErrorPermiso, ErrorValidacion
from .servicios import CAMPOS_REGISTRO, registrar_incidencia

bp = Blueprint("incidencias", __name__, url_prefix="/incidencias")


def _formulario(datos=None, errores=(), estado=200):
    return render_template(
        "incidencias/nueva.html",
        datos=datos or {}, errores=errores, ubicaciones=UBICACIONES, categorias=CATEGORIAS,
    ), estado


@bp.get("/nueva")
@login_requerido("SOLICITANTE")
def nueva():
    return _formulario()


@bp.post("/")
@login_requerido("SOLICITANTE")
def crear():  # S01
    datos = {campo: request.form.get(campo) for campo in CAMPOS_REGISTRO}
    try:
        resultado = registrar_incidencia(datos, g.usuario, current_app.config["RELOJ"])
    except ErrorValidacion as error:
        return _formulario(datos, error.args, 400)
    except ErrorPermiso:
        abort(403)
    flash(f"Incidencia {resultado['codigo']} registrada con prioridad {resultado['prioridad']}.")
    return redirect(url_for("inicio"))
