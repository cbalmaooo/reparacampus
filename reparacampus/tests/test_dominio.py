"""Pruebas unitarias de reglas de dominio.

Los resultados esperados están escritos a mano; no se calculan con funciones
de producción.
"""
from datetime import datetime, timezone

import pytest

from app.dominio import (
    ErrorValidacion,
    calcular_prioridad,
    dentro_de_plazo_reapertura,
    parsear_riesgo,
    porcentaje_cierre,
    validar_descripcion,
    validar_motivo,
    validar_opcion,
    validar_solucion,
    UBICACIONES,
)


# --- S02: prioridad (P-S02-01 a P-S02-04) ---
@pytest.mark.parametrize(
    "riesgo, impacto, esperado",
    [
        (True, "BAJO", "CRITICA"),   # AC-S02-01
        (True, "ALTO", "CRITICA"),   # AC-S02-02
        (False, "ALTO", "ALTA"),     # AC-S02-03
        (False, "BAJO", "NORMAL"),   # AC-S02-04
    ],
)
def test_prioridad(riesgo, impacto, esperado):
    assert calcular_prioridad(riesgo, impacto) == esperado


def test_prioridad_impacto_invalido():  # AC-S01-04
    with pytest.raises(ErrorValidacion):
        calcular_prioridad(False, "MEDIO")


# --- S01: descripción (P-S01-06 a P-S01-08) ---
def test_descripcion_limites():
    assert validar_descripcion("A" * 20) == "A" * 20
    assert validar_descripcion("A" * 500) == "A" * 500
    with pytest.raises(ErrorValidacion, match="al menos 20"):
        validar_descripcion("A" * 19)
    with pytest.raises(ErrorValidacion, match="no puede superar 500"):
        validar_descripcion("A" * 501)


def test_descripcion_recorta_espacios():  # AC-S01-08
    assert validar_descripcion("   " + "A" * 20 + "   ") == "A" * 20
    with pytest.raises(ErrorValidacion):
        validar_descripcion("   " + "A" * 19 + "   ")
    with pytest.raises(ErrorValidacion):
        validar_descripcion("      ")
    with pytest.raises(ErrorValidacion):
        validar_descripcion(None)


# --- S03: solución ---
def test_solucion_limites():  # AC-S03-06, AC-S03-07
    assert validar_solucion("A" * 20) == "A" * 20
    assert validar_solucion("A" * 800) == "A" * 800
    with pytest.raises(ErrorValidacion):
        validar_solucion("A" * 19)
    with pytest.raises(ErrorValidacion):
        validar_solucion("A" * 801)


# --- S04: motivo ---
def test_motivo_limites():  # AC-S04-03, AC-S04-04
    assert validar_motivo("A" * 10) == "A" * 10
    assert validar_motivo("A" * 300) == "A" * 300
    with pytest.raises(ErrorValidacion):
        validar_motivo("A" * 9)
    with pytest.raises(ErrorValidacion):
        validar_motivo("A" * 301)
    with pytest.raises(ErrorValidacion):
        validar_motivo("   " + "A" * 9 + "   ")


# --- S01: valores cerrados y riesgo ---
def test_opciones_y_riesgo():  # AC-S01-03, AC-S01-05
    assert validar_opcion("LAB-01", UBICACIONES, "ubicación") == "LAB-01"
    with pytest.raises(ErrorValidacion):
        validar_opcion("LAB-99", UBICACIONES, "ubicación")
    assert parsear_riesgo("true") is True
    assert parsear_riesgo("false") is False
    with pytest.raises(ErrorValidacion):
        parsear_riesgo("quizas")


# --- S04: plazo de 48 h (P-S04-06, P-S04-07) ---
CIERRE = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)


def test_reapertura_exactamente_48h():  # AC-S04-06
    assert dentro_de_plazo_reapertura(CIERRE, datetime(2026, 10, 12, 12, 0, 0, tzinfo=timezone.utc))


def test_reapertura_un_segundo_despues():  # AC-S04-07
    assert not dentro_de_plazo_reapertura(CIERRE, datetime(2026, 10, 12, 12, 0, 1, tzinfo=timezone.utc))


def test_plazo_rechaza_fechas_sin_zona():
    with pytest.raises(ValueError):
        dentro_de_plazo_reapertura(datetime(2026, 10, 10, 12, 0, 0), CIERRE)


# --- S05: porcentaje (P-S05-12, P-S05-13, P-S05-15) ---
@pytest.mark.parametrize(
    "cerradas, total, esperado",
    [
        (0, 0, "0,0 %"),     # AC-S05-14
        (1, 4, "25,0 %"),    # AC-S05-15
        (0, 4, "0,0 %"),     # AC-S05-16
        (1, 3, "33,3 %"),    # AC-S05-17
        (1, 16, "6,3 %"),    # AC-S05-17 (half-up)
        (5, 5, "100,0 %"),   # INT-01
    ],
)
def test_porcentaje_cierre(cerradas, total, esperado):
    assert porcentaje_cierre(cerradas, total) == esperado
