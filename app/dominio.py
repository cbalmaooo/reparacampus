"""Reglas de dominio de ReparaCampus.

Funciones puras, sin Flask ni base de datos, para poder probarlas de forma aislada.
Trazabilidad: S01 (valores y descripción), S02 (prioridad), S03 (solución),
S04 (motivo y plazo de 48 h), S05 (porcentaje de cierre).
"""
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Valores permitidos del caso (enunciado, "Datos y límites del prototipo")
UBICACIONES = ("LAB-01", "AULA-201", "BIB-01")
CATEGORIAS = ("ELECTRICIDAD", "HIDRAULICA", "MOBILIARIO", "TIC")
IMPACTOS = ("BAJO", "ALTO")
PRIORIDADES = ("CRITICA", "ALTA", "NORMAL")
ESTADOS = ("REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA")

PLAZO_REAPERTURA = timedelta(hours=48)


class ErrorValidacion(ValueError):
    """Dato de entrada inválido. La operación debe rechazarse sin efectos.

    Puede llevar varios mensajes: ErrorValidacion("a", "b") -> error.args == ("a", "b").
    """


class ErrorPermiso(Exception):
    """El usuario de la sesión no puede ejecutar la operación."""


def validar_texto(valor, minimo, maximo, etiqueta):
    """Retira espacios externos y valida la longitud. Devuelve el texto recortado."""
    limpio = valor.strip() if isinstance(valor, str) else ""
    if len(limpio) < minimo:
        raise ErrorValidacion(f"{etiqueta} debe tener al menos {minimo} caracteres")
    if len(limpio) > maximo:
        raise ErrorValidacion(f"{etiqueta} no puede superar {maximo} caracteres")
    return limpio


def validar_descripcion(valor):  # S01: 20 a 500
    return validar_texto(valor, 20, 500, "La descripción")


def validar_solucion(valor):  # S03: 20 a 800
    return validar_texto(valor, 20, 800, "La solución")


def validar_motivo(valor):  # S04: 10 a 300
    return validar_texto(valor, 10, 300, "El motivo")


def validar_opcion(valor, permitidos, campo):
    """Valida que el valor pertenezca a la lista cerrada del caso."""
    if valor not in permitidos:
        raise ErrorValidacion(f"Valor no permitido para {campo}")
    return valor


def parsear_riesgo(valor):
    """Convierte el riesgo del formulario a booleano. Solo acepta true/false."""
    if isinstance(valor, bool):
        return valor
    if valor == "true":
        return True
    if valor == "false":
        return False
    raise ErrorValidacion("Valor no permitido para riesgo para personas")


def calcular_prioridad(riesgo_personas, impacto):
    """S02: el riesgo para personas tiene precedencia sobre el impacto."""
    if not isinstance(riesgo_personas, bool):
        raise ErrorValidacion("Valor no permitido para riesgo para personas")
    validar_opcion(impacto, IMPACTOS, "impacto")
    if riesgo_personas:
        return "CRITICA"
    return "ALTA" if impacto == "ALTO" else "NORMAL"


def dentro_de_plazo_reapertura(ultimo_cierre, ahora):
    """S04: acepta si lo transcurrido desde el último cierre es <= 48 h (UTC).

    Ambas fechas deben tener zona horaria; nunca se usa la hora del cliente.
    """
    for fecha in (ultimo_cierre, ahora):
        if not isinstance(fecha, datetime) or fecha.tzinfo is None:
            raise ValueError("Las fechas del plazo deben ser datetime con zona horaria UTC")
    return ahora - ultimo_cierre <= PLAZO_REAPERTURA


def porcentaje_cierre(cerradas, total):
    """S05: CERRADAS / total x 100, un decimal, half-up, coma decimal."""
    if total == 0:
        return "0,0 %"
    valor = (Decimal(cerradas) * 100 / Decimal(total)).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    return f"{valor} %".replace(".", ",")
