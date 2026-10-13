# S04 — Validar o reabrir una incidencia

**Requisito relacionado:** RF04 (relación con RF03 y RF05)
**Versión:** 1.0
**Estado:** Aprobada
**Autor:** cbalmaooo (v0.1) · Alejandro Borja (cambios v0.2)
**Revisor:** Alejandro Borja
**Fecha:** 2026-10-13

### Historial de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 0.1 | 2026-10-12 | [autor original] | Borrador inicial |
| 0.2 | 2026-10-13 | Alejandro Borja | Correcciones de la revisión v0.1 |
| 1.0 | 2026-10-13 | Alejandro Borja | Aprobación |

## Historia de usuario

Como solicitante que registró la incidencia, quiero confirmar la solución, rechazarla si el daño continúa o reabrir el caso si vuelve a ocurrir poco después del cierre, para asegurar que el problema quede realmente resuelto.

## Alcance y exclusiones

**Incluye:**
- Confirmar una solución: PENDIENTE_VALIDACION → CERRADA, con registro del cierre.
- Rechazar una solución con motivo: PENDIENTE_VALIDACION → EN_ATENCION, con el mismo técnico.
- Reabrir dentro del plazo con motivo: CERRADA → EN_ATENCION, con el mismo técnico.
- Conservación de todas las soluciones, cierres, rechazos y reaperturas.

**Excluye:**
- Cierre automático por tiempo.
- Confirmar, rechazar o reabrir en nombre del solicitante (coordinador incluido).
- Cambiar de técnico al rechazar o reabrir.
- Editar o borrar soluciones, cierres, motivos o eventos.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|---|
| Confirmar | incidencia_id | entero o código | Sí | Debe existir |
| Rechazar | incidencia_id | entero o código | Sí | Debe existir |
| Rechazar | motivo | texto | Sí | De 10 a 300 caracteres después de retirar espacios externos |
| Reabrir | incidencia_id | entero o código | Sí | Debe existir |
| Reabrir | motivo | texto | Sí | De 10 a 300 caracteres después de retirar espacios externos |

Identidad, rol y hora efectiva: los define el servidor. El servidor no acepta fechas ni horas enviadas por el cliente.

## Precondiciones y permisos

- Sesión iniciada con rol SOLICITANTE.
- El solicitante de la sesión es el autor (dueño) de la incidencia.
- Confirmar o rechazar: estado PENDIENTE_VALIDACION.
- Reabrir: estado CERRADA y tiempo transcurrido desde el último cierre menor o igual a 48 horas.
- Coordinador, técnicos y otros solicitantes no pueden ejecutar estas operaciones. El servidor lo comprueba en cada operación.

## Reglas y proceso

**Plazo de reapertura:**
- Último cierre = el registro de cierre más reciente de la incidencia.
- Transcurrido = ahora (UTC, reloj del servidor) − fecha del último cierre (UTC).
- Se acepta si transcurrido ≤ 48 horas exactas; se rechaza si es mayor, aunque sea por un segundo.
- El reloj es inyectable para pruebas; no se modifica el reloj del sistema ni se usa la hora del navegador.

**Confirmar:**
1. Verificar sesión, rol SOLICITANTE, propiedad y estado PENDIENTE_VALIDACION.
2. En una transacción: crear un registro de cierre con fecha UTC y autor, cambiar a CERRADA y registrar el evento CONFIRMAR.

**Rechazar:**
1. Verificar sesión, rol, propiedad y estado PENDIENTE_VALIDACION.
2. Recortar el motivo y validar 10–300.
3. En una transacción: cambiar a EN_ATENCION (mismo técnico, solución anterior intacta) y registrar el evento RECHAZAR con el motivo.

**Reabrir:**
1. Verificar sesión, rol, propiedad y estado CERRADA.
2. Recortar el motivo y validar 10–300.
3. Verificar el plazo de 48 horas desde el último cierre.
4. En una transacción: cambiar a EN_ATENCION (mismo técnico; cierres y soluciones intactos) y registrar el evento REABRIR con el motivo.

Cualquier verificación fallida rechaza la operación sin modificar estado, técnico, soluciones, cierres ni historial.

**Supuesto pendiente de confirmar con el cliente:** no hay límite en el número de rechazos o reaperturas mientras se cumplan las reglas (ver `preguntas-cliente.md`).

## Salidas y cambios persistidos

| Operación | Estado final | Registros nuevos | Evento (autor, fecha UTC, estado anterior → nuevo, acción) |
|---|---|---|---|
| Confirmar | CERRADA | 1 cierre | PENDIENTE_VALIDACION → CERRADA, CONFIRMAR |
| Rechazar | EN_ATENCION | Ninguno además del evento | PENDIENTE_VALIDACION → EN_ATENCION, RECHAZAR, con motivo |
| Reabrir | EN_ATENCION | Ninguno además del evento | CERRADA → EN_ATENCION, REABRIR, con motivo |

En todos los casos el técnico asignado no cambia y no se borra ni modifica ningún registro anterior. Los motivos se muestran escapados, sin ejecutarse como HTML ni como script. Una incidencia reabierta deja de contar como CERRADA en el tablero (S05), pero su cierre anterior permanece en el historial.

## Errores y efectos que deben evitarse

| Situación | Respuesta esperada | Efecto prohibido |
|---|---|---|
| Sin sesión | Redirigir a inicio de sesión | Cualquier cambio |
| Rol distinto de SOLICITANTE | Rechazo por falta de permiso | Actuar en nombre del solicitante |
| Solicitante no dueño | Rechazo; no revela datos de la incidencia | Cualquier cambio |
| Incidencia inexistente | Mensaje "incidencia no encontrada" | Crear registros |
| Estado incompatible | Rechazo por estado incompatible | Cambio de estado o evento |
| Motivo fuera de 10–300 tras recortar | Mensaje con el límite incumplido | Cambio de estado o evento |
| Reapertura con más de 48 h | Rechazo por plazo vencido | Cambio de estado o evento |
| Hora enviada por el cliente | Se ignora | Usarla para el plazo |
| Falla durante la transacción | Rechazo general | Efectos parciales |
| Rechazo o reapertura | Mismo técnico y registros intactos | Borrar o sobrescribir soluciones o cierres |

## Criterios de aceptación

### AC-S04-01 — Confirmar solución
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION con técnico T01 y la solución S1
**Cuando** SOL01 confirma la solución
**Entonces** INC-0001 queda CERRADA, se crea un registro de cierre con fecha UTC y autor SOL01, y se registra el evento PENDIENTE_VALIDACION → CERRADA con acción CONFIRMAR.

### AC-S04-02 — Rechazar con motivo válido
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION con técnico T01 y la solución S1
**Cuando** SOL01 la rechaza con el motivo "El daño sigue presente"
**Entonces** INC-0001 queda EN_ATENCION, conserva T01 y S1, y se registra el evento PENDIENTE_VALIDACION → EN_ATENCION con acción RECHAZAR, autor SOL01, fecha UTC y el motivo.

### AC-S04-03 — Límites del motivo de rechazo
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION
**Cuando** SOL01 rechaza con motivos de 10, 9, 300 y 301 caracteres (intentos independientes)
**Entonces** se aceptan los de 10 y 300, y se rechazan los de 9 y 301 con el mensaje del límite incumplido; en los rechazos, INC-0001 sigue PENDIENTE_VALIDACION sin eventos nuevos.

### AC-S04-04 — Espacios externos en el motivo
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION
**Cuando** SOL01 envía un motivo de 9 caracteres rodeado de espacios, o solo espacios
**Entonces** el sistema mide después de recortar, rechaza la operación y no registra cambios.

### AC-S04-05 — Reapertura dentro del plazo
**Dado** que INC-0001 de SOL01 está CERRADA con técnico T01 y su último cierre fue hace 24 horas según el reloj del servidor
**Cuando** SOL01 la reabre con el motivo "La fuga volvió a aparecer"
**Entonces** INC-0001 queda EN_ATENCION con T01, conserva el registro de cierre y la solución S1, y se registra el evento CERRADA → EN_ATENCION con acción REABRIR y el motivo.

### AC-S04-06 — Reapertura exactamente a las 48 horas
**Dado** que el último cierre de INC-0001 fue el 2026-10-10 12:00:00 UTC y el reloj del servidor marca 2026-10-12 12:00:00 UTC
**Cuando** SOL01 la reabre con un motivo válido
**Entonces** el sistema acepta la reapertura e INC-0001 queda EN_ATENCION.

### AC-S04-07 — Reapertura después de 48 horas
**Dado** que el último cierre de INC-0001 fue el 2026-10-10 12:00:00 UTC y el reloj del servidor marca 2026-10-12 12:00:01 UTC
**Cuando** SOL01 intenta reabrirla con un motivo válido
**Entonces** el sistema rechaza la operación por plazo vencido, INC-0001 sigue CERRADA y no se registran eventos.

### AC-S04-08 — Plazo contado desde el último cierre
**Dado** que INC-0001 se cerró el 2026-10-01, se reabrió, recibió una nueva solución S2 y se volvió a cerrar el 2026-10-12 10:00:00 UTC
**Cuando** SOL01 la reabre el 2026-10-13 10:00:00 UTC con un motivo válido
**Entonces** el sistema acepta la reapertura, porque cuenta desde el cierre más reciente, y conserva los dos cierres y las soluciones S1 y S2.

### AC-S04-09 — Límites del motivo de reapertura
**Dado** que INC-0001 de SOL01 está CERRADA dentro del plazo
**Cuando** SOL01 intenta reabrirla con motivos de 9 y 301 caracteres
**Entonces** el sistema rechaza ambos intentos, INC-0001 sigue CERRADA y no se registran eventos.

### AC-S04-10 — Solicitante no dueño
**Dado** que INC-0001 pertenece a SOL01
**Cuando** SOL02 intenta confirmarla, rechazarla o reabrirla
**Entonces** el sistema rechaza la operación sin revelar datos de la incidencia y no modifica estado, registros ni historial.

### AC-S04-11 — Coordinador o técnico
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION o CERRADA
**Cuando** COORD01 o T01 intentan confirmar, rechazar o reabrirla
**Entonces** el sistema rechaza la operación por falta de permiso y no modifica estado, registros ni historial.

### AC-S04-12 — Sin sesión e incidencia inexistente
**Dado** que no hay sesión iniciada, o que SOL01 inició sesión y no existe INC-9999
**Cuando** se intenta confirmar, rechazar o reabrir
**Entonces** el sistema redirige al inicio de sesión o informa que la incidencia no existe, y no crea registros.

### AC-S04-13 — Estados incompatibles
**Dado** que INC-0001 de SOL01 está REGISTRADA, ASIGNADA o EN_ATENCION
**Cuando** SOL01 intenta confirmar, rechazar o reabrirla; o la incidencia está PENDIENTE_VALIDACION y SOL01 intenta reabrirla; o está CERRADA y SOL01 intenta confirmarla o rechazarla
**Entonces** el sistema rechaza la operación por estado incompatible y conserva estado, registros e historial.

### AC-S04-14 — Texto parecido a HTML en el motivo
**Dado** que INC-0001 de SOL01 está PENDIENTE_VALIDACION
**Cuando** SOL01 la rechaza con el motivo "<script>x</script> sigue goteando"
**Entonces** el motivo se guarda como texto y en el historial se muestra literalmente, sin ejecutarse.

## Diseño y tareas vinculadas a cada AC

**Diseño:**
- Servicios `confirmar_solucion`, `rechazar_solucion(motivo)` y `reabrir_incidencia(motivo)`, todos con `usuario_sesion` y un parámetro `reloj` inyectable (por defecto, la hora UTC del servidor).
- Tabla de cierres con relación 1:N con incidencia; "último cierre" = la fecha máxima.
- Las soluciones se conservan en la tabla de S03; ninguna operación de S04 las modifica.
- Validador de texto compartido con S01 y S03.
- Rutas `POST /incidencias/<id>/confirmar`, `/rechazar` y `/reabrir`.
- Fechas guardadas en UTC con formato ISO 8601.

| Tarea | Descripción | AC cubiertos |
|---|---|---|
| T-S04-01 | Servicio confirmar con registro de cierre y evento | 01 |
| T-S04-02 | Servicio rechazar con motivo y evento, conservando técnico y solución | 02, 03, 04 |
| T-S04-03 | Reloj inyectable y cálculo del plazo desde el último cierre | 06, 07, 08 |
| T-S04-04 | Servicio reabrir con motivo y evento, conservando cierres y soluciones | 05, 08, 09 |
| T-S04-05 | Verificación de sesión, rol y propiedad | 10, 11, 12 |
| T-S04-06 | Validación de estados por operación | 13 |
| T-S04-07 | Visualización escapada de motivos | 14 |
| T-S04-08 | Pruebas unitarias e integración | 01–14 |

## Pruebas y resultados esperados

Los resultados esperados se escriben a mano. El reloj de prueba se fija en valores conocidos; nunca se espera tiempo real ni se cambia el reloj del sistema. Se usa una base de prueba independiente.

| Prueba | AC | Entrada | Resultado esperado |
|---|---|---|---|
| P-S04-01 | 01 | SOL01 confirma | CERRADA; 1 cierre; evento CONFIRMAR |
| P-S04-02 | 02 | SOL01 rechaza con motivo válido | EN_ATENCION; técnico T01; S1 conservada; evento RECHAZAR con motivo |
| P-S04-03 | 03 | Motivos de 9 y 301 | Rechazo; PENDIENTE_VALIDACION; 0 eventos nuevos |
| P-S04-04 | 04 | "   " + "A" × 9 + "   " | Rechazo; sin cambios |
| P-S04-05 | 05 | Reapertura a las 24 h | EN_ATENCION; T01; cierre y S1 conservados |
| P-S04-06 | 06 | Cierre 10/10 12:00:00; reloj 12/10 12:00:00 | Aceptada |
| P-S04-07 | 07 | Cierre 10/10 12:00:00; reloj 12/10 12:00:01 | Rechazo; CERRADA; 0 eventos nuevos |
| P-S04-08 | 08 | Dos cierres; reapertura a 24 h del segundo | Aceptada; 2 cierres; S1 y S2 conservadas |
| P-S04-09 | 09 | Reabrir con motivo de 301 | Rechazo; CERRADA |
| P-S04-10 | 10 | SOL02 confirma INC-0001 de SOL01 | Rechazo; sin cambios |
| P-S04-11 | 11 | COORD01 reabre INC-0001 | Rechazo; sin cambios |
| P-S04-12 | 12 | SOL01 confirma INC-9999 | "No encontrada"; sin registros |
| P-S04-13 | 13 | Confirmar una incidencia EN_ATENCION | Rechazo; sin cambios |
| P-S04-14 | 14 | Motivo con `<script>` | La respuesta contiene `&lt;script&gt;` |
| INT-02 | 02, S03-11 | Registrar → asignar → iniciar → solución S1 → rechazar → solución S2 → confirmar (SQLite real) | CERRADA; S1 y S2; T01 sin cambios; eventos completos en orden |
| INT-03 | 05, 08 | Cierre → reabrir → solución S2 → nuevo cierre (SQLite real) | CERRADA; 2 cierres; evento REABRIR con motivo |

## Decisión de revisión

**Revisión de v0.1**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Requiere cambios
- Observaciones:
  1. No definía el registro de cierre ni el "último cierre": impedía conservar todos los cierres y calcular el plazo tras varias reaperturas.
  2. El límite de 48 h no precisaba el instante posterior, el reloj inyectable ni que se ignora la hora del cliente.
  3. Los eventos no especificaban autor, fecha UTC, estados, acción y motivo.
  4. Faltaban el recorte de espacios y los límites exactos de 10 y 300 en el motivo.
  5. AC-S04-07 no indicaba el estado CERRADA ni un motivo válido, de modo que el rechazo no se atribuía de forma inequívoca al plazo.
  6. Faltaban los casos de sin sesión, incidencia inexistente, texto parecido a HTML y ciclo completo con segundo cierre.
  7. Plantilla incompleta: entradas, salidas, errores, diseño, tareas vinculadas a AC y pruebas, incluidas las de integración.
  8. Criterios sin datos concretos.

**Revisión de v0.2**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Aprobada → v1.0
- Observaciones: se verificó, contra RF04, RF05 y las reglas que no pueden cambiarse, que los ocho hallazgos quedaron resueltos (AC-S04-01 a AC-S04-14, pruebas INT-02 e INT-03 y plantilla completa).
- Condiciones: S05 debe calcular el porcentaje de cierre con el estado actual (una incidencia reabierta no cuenta como CERRADA) y mostrar los cierres anteriores en el historial; el número de reaperturas sin límite queda como supuesto hasta que el cliente responda.
- Nota de trazabilidad: los cambios de v0.2 fueron redactados por el revisor con apoyo de IA (ver bitácora); se solicita la conformidad del autor original.

**Conformidad del autor original**
- Autor: cbalmaooo
- Fecha: 13/10/2026
- Decisión: Cambios Aceptados
