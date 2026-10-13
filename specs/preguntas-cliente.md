# Preguntas al cliente y supuestos

**Versión:** 0.2
**Autor:** cbalmaooo (v0.1) · Alejandro Borja (cambios v0.2)
**Fecha:** 2026-10-13
**Estado:** Preguntas pendientes de respuesta del cliente; supuestos vigentes mientras no responda.

> Una respuesta de IA no es una decisión del cliente. Los supuestos son decisiones provisionales del equipo y se revisarán si el cliente responde distinto.

## Historial de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 0.1 | 2026-10-12 | cbalmaooo | Borrador inicial |
| 0.2 | 2026-10-13 | Alejandro Borja | Se reemplazan las preguntas 1 y 2, ya resueltas por el enunciado; se agregan los supuestos referenciados por S01, S04 y S05 |

## Preguntas al cliente

| # | Pregunta | Por qué importa | Supuesto mientras no responda | SPEC afectada |
|---|---|---|---|---|
| P1 | ¿Qué formato debe tener el código de la incidencia y debe ser consecutivo? | El enunciado exige generar un código, pero no define su forma | `INC-0001`, consecutivo, único y generado por el servidor | S01 |
| P2 | ¿Hay un límite de rechazos de solución o de reaperturas por incidencia? | El enunciado no fija un máximo; un límite cambiaría las reglas de S04 | Sin límite, mientras se cumplan estado, propiedad, motivo y plazo de 48 h | S04 |
| P3 | Cuando un usuario intenta ver una incidencia que no le pertenece, ¿el sistema debe indicar falta de permiso o comportarse como si no existiera? | Define qué información se revela a otros solicitantes | Responder "Incidencia no encontrada", sin confirmar que existe | S04, S05 |

## Decisiones ya definidas por el enunciado (no requieren pregunta)

| Tema | Definición del enunciado | Pregunta retirada de v0.1 |
|---|---|---|
| Categorías | ELECTRICIDAD, HIDRAULICA, MOBILIARIO, TIC | P1 de v0.1 |
| Ubicaciones | LAB-01, AULA-201, BIB-01 (lista cerrada) | P2 de v0.1 |
| Comentario al confirmar | RF04 solo exige motivo para rechazar o reabrir; confirmar no lo requiere | P3 de v0.1 |

## Otros supuestos del equipo

- El reloj de referencia para el plazo de 48 h es el del servidor en UTC; la hora del cliente se ignora.
- Los textos se guardan después de retirar los espacios externos.
- El técnico inactivo usado en las pruebas existe solo en la base de prueba; el seed oficial tiene dos técnicos activos.

## Revisión

- Revisor: cbalmaooo
- Fecha: 13/10/2026
- Decisión: Aprobado
