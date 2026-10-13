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
    confirmar_solucion,
    listar_reportes_de,
    reabrir_incidencia,
    rechazar_solucion,
    iniciar_atencion,
    listar_asignaciones_de,
    listar_por_asignar,
    listar_tecnicos_activos,
    registrar_incidencia,
    registrar_solucion,
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
    return redirect(url_for("incidencias.mis_reportes"))


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


def _mis_asignaciones(error=None, estado=200, borrador=None):
    return render_template(
        "incidencias/mis_asignaciones.html",
        incidencias=listar_asignaciones_de(g.usuario["id"]), error=error, borrador=borrador or {},
    ), estado


@bp.get("/mis-asignaciones")
@login_requerido("TECNICO")
def mis_asignaciones():  # S03: vista del técnico
    return _mis_asignaciones()


def _atender(operacion, codigo, mensaje_exito, borrador=None):
    try:
        operacion()
    except ErrorPermiso:
        abort(403)
    except ErrorNoEncontrada as error:
        return _mis_asignaciones(str(error), 404)
    except ErrorEstado as error:
        return _mis_asignaciones(str(error), 409)
    except ErrorValidacion as error:
        return _mis_asignaciones(" ".join(error.args), 400, borrador)
    flash(mensaje_exito)
    return redirect(url_for("incidencias.mis_asignaciones"))


@bp.post("/<codigo>/iniciar")
@login_requerido("TECNICO")
def iniciar(codigo):  # S03
    reloj = current_app.config["RELOJ"]
    return _atender(lambda: iniciar_atencion(codigo, g.usuario, reloj), codigo,
                    f"Atención de {codigo} iniciada.")


@bp.post("/<codigo>/solucion")
@login_requerido("TECNICO")
def solucion(codigo):  # S03
    texto = request.form.get("solucion")
    reloj = current_app.config["RELOJ"]
    return _atender(lambda: registrar_solucion(codigo, texto, g.usuario, reloj), codigo,
                    f"Solución de {codigo} registrada. Queda pendiente de validación del solicitante.",
                    borrador={codigo: texto})


def _mis_reportes(error=None, estado=200, borrador=None):
    return render_template(
        "incidencias/mis_reportes.html",
        reportes=listar_reportes_de(g.usuario["id"], current_app.config["RELOJ"]),
        error=error, borrador=borrador or {},
    ), estado


@bp.get("/mis-reportes")
@login_requerido("SOLICITANTE")
def mis_reportes():  # S04: vista del solicitante
    return _mis_reportes()


def _validar(operacion, mensaje_exito, borrador=None):
    try:
        operacion()
    except ErrorPermiso:
        abort(403)
    except ErrorNoEncontrada as error:
        return _mis_reportes(str(error), 404)
    except ErrorEstado as error:
        return _mis_reportes(str(error), 409)
    except ErrorValidacion as error:
        return _mis_reportes(" ".join(error.args), 400, borrador)
    flash(mensaje_exito)
    return redirect(url_for("incidencias.mis_reportes"))


@bp.post("/<codigo>/confirmar")
@login_requerido("SOLICITANTE")
def confirmar(codigo):  # S04
    reloj = current_app.config["RELOJ"]
    return _validar(lambda: confirmar_solucion(codigo, g.usuario, reloj),
                    f"Confirmaste la solución. {codigo} quedó cerrada.")


@bp.post("/<codigo>/rechazar")
@login_requerido("SOLICITANTE")
def rechazar(codigo):  # S04
    motivo = request.form.get("motivo")
    reloj = current_app.config["RELOJ"]
    return _validar(lambda: rechazar_solucion(codigo, motivo, g.usuario, reloj),
                    f"Rechazaste la solución. {codigo} volvió al mismo técnico.",
                    borrador={f"rechazar-{codigo}": motivo})


@bp.post("/<codigo>/reabrir")
@login_requerido("SOLICITANTE")
def reabrir(codigo):  # S04
    motivo = request.form.get("motivo")
    reloj = current_app.config["RELOJ"]
    return _validar(lambda: reabrir_incidencia(codigo, motivo, g.usuario, reloj),
                    f"Reabriste {codigo}. Volvió al mismo técnico.",
                    borrador={f"reabrir-{codigo}": motivo})
