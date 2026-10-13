"""Rutas HTTP de incidencias. La identidad viene siempre de la sesión (g.usuario)."""
from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from .auth import login_requerido
from .dominio import (
    CATEGORIAS,
    UBICACIONES,
    ErrorEstado,
    ErrorNoEncontrada,
    ErrorPermiso,
    ErrorValidacion,
)
from .servicios import (
    CAMPOS_REGISTRO,
    asignar_incidencia,
    listar_por_asignar,
    listar_tecnicos_activos,
    registrar_incidencia,
)

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


def _por_asignar(error=None, estado=200):
    return render_template(
        "incidencias/por_asignar.html",
        incidencias=listar_por_asignar(), tecnicos=listar_tecnicos_activos(), error=error,
    ), estado


@bp.get("/por-asignar")
@login_requerido("COORDINADOR")
def por_asignar():  # S02: vista del coordinador
    return _por_asignar()


@bp.post("/<codigo>/asignar")
@login_requerido("COORDINADOR")
def asignar(codigo):  # S02
    try:
        asignar_incidencia(codigo, request.form.get("tecnico_id"), g.usuario, current_app.config["RELOJ"])
    except ErrorPermiso:
        abort(403)
    except ErrorNoEncontrada as error:
        return _por_asignar(str(error), 404)
    except ErrorEstado as error:
        return _por_asignar(str(error), 409)
    except ErrorValidacion as error:
        return _por_asignar(" ".join(error.args), 400)
    flash(f"Incidencia {codigo} asignada.")
    return redirect(url_for("incidencias.por_asignar"))
