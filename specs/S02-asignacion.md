
# S02 — Priorizar y asignar una incidencia

**Requisito relacionado:** RF02
**Versión:** 0.2
**Estado:** En revisión
**Autor:** cbalmaooo (v0.1)
**Revisor:** Alejandro (MaggLo_1080)
**Fecha:** 2026-10-13

### Historial de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 0.1 | 2026-10-12 | cbalmaooo | Borrador inicial |
| 0.2 | 2026-10-13 | Alejandro | Correcciones de la revisión v0.1: historial, plantilla completa, momento del cálculo de prioridad, reasignación, destinatario inválido, operaciones sin efectos, exclusiones y datos concretos |

## Historia de usuario

Como coordinador, quiero que cada incidencia tenga una prioridad calculada por el sistema y poder asignarla a un técnico activo, para organizar su atención según el riesgo y el impacto.

## Alcance y exclusiones

**Incluye:**
- Cálculo automático de la prioridad en el servidor al registrar la incidencia (S01), a partir del riesgo para personas y el impacto.
- Asignación, por el coordinador, de una incidencia REGISTRADA a un técnico activo, con cambio a ASIGNADA.
- Registro del evento de asignación en el historial.

**Excluye:**
- Modificar la prioridad manualmente: la prioridad no se edita.
- Reasignar una incidencia ya ASIGNADA o en cualquier estado posterior.
- Restricción por especialidad del técnico: cualquier técnico activo puede recibir cualquier categoría.
- Notificaciones al técnico.

## Entradas

**Cálculo de prioridad** (datos ya validados por S01):
| Campo | Tipo | Obligatorio | Valores permitidos |
|---|---|---|---|
| riesgo_personas | booleano | Sí | true / false |
| impacto | texto | Sí | BAJO / ALTO |

**Asignación:**
| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| incidencia_id | entero o código | Sí | Debe existir |
| tecnico_id | entero | Sí | Debe existir, tener rol TECNICO y estar activo |

Identidad y rol del usuario: se obtienen de la sesión en el servidor, nunca de la petición.

## Precondiciones y permisos

- El usuario tiene sesión iniciada y su rol en la sesión es COORDINADOR.
- La incidencia existe y su estado actual es REGISTRADA.
- El destinatario existe, tiene rol TECNICO y está activo.
- Solicitantes y técnicos no pueden asignar. Ocultar el botón en la interfaz no basta: el servidor lo comprueba en cada operación.

## Reglas y proceso

**Prioridad** (se calcula en el servidor al registrar, se guarda y no cambia después):
1. Si riesgo_personas = true → CRITICA, sin importar el impacto.
2. Si riesgo_personas = false e impacto = ALTO → ALTA.
3. Si riesgo_personas = false e impacto = BAJO → NORMAL.

Si la petición de registro incluye un campo de prioridad, el servidor lo ignora.

**Asignación:**
1. Verificar sesión y rol COORDINADOR.
2. Verificar que la incidencia exista y esté REGISTRADA.
3. Verificar que el destinatario exista, sea TECNICO y esté activo.
4. En una sola transacción: guardar el técnico asignado, cambiar el estado a ASIGNADA y registrar el evento de historial.
5. Si cualquier verificación falla, rechazar sin modificar estado, asignación ni historial.

## Salidas y cambios persistidos

**Asignación exitosa:**
- La incidencia queda con estado ASIGNADA y el técnico asignado guardado.
- Se registra un evento de historial con: autor (coordinador de la sesión), fecha y hora UTC del servidor, estado anterior REGISTRADA, estado nuevo ASIGNADA, acción ASIGNAR y técnico asignado.
- La interfaz muestra un mensaje de éxito.

**Operación rechazada:**
- Mensaje de error comprensible.
- Sin cambios en estado, asignación ni historial.

## Errores y efectos que deben evitarse

| Situación | Respuesta esperada | Efecto prohibido |
|---|---|---|
| Sin sesión | Redirigir a inicio de sesión | Cualquier cambio |
| Rol distinto de COORDINADOR | Rechazo por falta de permiso | Cualquier cambio |
| Incidencia inexistente | Mensaje "incidencia no encontrada" | Crear registros |
| Estado distinto de REGISTRADA | Rechazo por estado incompatible | Reasignar o cambiar estado |
| Destinatario inexistente o sin rol TECNICO | Rechazo por técnico no válido | Asignar |
| Técnico inactivo | Rechazo por técnico inactivo | Asignar |
| Falla durante la transacción | Rechazo general | Efectos parciales (estado sin evento o evento sin estado) |

## Criterios de aceptación

### AC-S02-01 — Riesgo con impacto BAJO
**Dado** que SOL01 registra una incidencia con riesgo_personas = true e impacto = BAJO
**Cuando** el sistema calcula su prioridad
**Entonces** la incidencia queda guardada con prioridad CRITICA.

### AC-S02-02 — Riesgo con impacto ALTO
**Dado** que SOL01 registra una incidencia con riesgo_personas = true e impacto = ALTO
**Cuando** el sistema calcula su prioridad
**Entonces** la incidencia queda guardada con prioridad CRITICA.

### AC-S02-03 — Impacto ALTO sin riesgo
**Dado** que SOL01 registra una incidencia con riesgo_personas = false e impacto = ALTO
**Cuando** el sistema calcula su prioridad
**Entonces** la incidencia queda guardada con prioridad ALTA.

### AC-S02-04 — Impacto BAJO sin riesgo
**Dado** que SOL01 registra una incidencia con riesgo_personas = false e impacto = BAJO
**Cuando** el sistema calcula su prioridad
**Entonces** la incidencia queda guardada con prioridad NORMAL.

### AC-S02-05 — Prioridad enviada por el cliente
**Dado** que SOL01 envía un registro con riesgo_personas = false, impacto = BAJO y un campo prioridad = CRITICA
**Cuando** el servidor procesa el registro
**Entonces** ignora el campo enviado y guarda la prioridad NORMAL.

### AC-S02-06 — Asignación válida
**Dado** que COORD01 inició sesión y la incidencia INC-0001 está REGISTRADA
**Cuando** la asigna al técnico activo T01
**Entonces** INC-0001 queda ASIGNADA con técnico T01 y se registra un evento con autor COORD01, fecha UTC, estado anterior REGISTRADA, estado nuevo ASIGNADA y acción ASIGNAR.

### AC-S02-07 — Rol sin permiso
**Dado** que SOL01 o T01 inició sesión y INC-0001 está REGISTRADA
**Cuando** intenta asignarla a T02
**Entonces** el sistema rechaza la operación por falta de permiso, INC-0001 sigue REGISTRADA sin técnico y no se registra ningún evento.

### AC-S02-08 — Sin sesión
**Dado** que no hay sesión iniciada
**Cuando** se envía una petición para asignar INC-0001
**Entonces** el sistema redirige al inicio de sesión y no modifica la incidencia ni el historial.

### AC-S02-09 — Técnico inactivo
**Dado** que COORD01 inició sesión, INC-0001 está REGISTRADA y T03 es un técnico inactivo
**Cuando** intenta asignarla a T03
**Entonces** el sistema rechaza la operación, INC-0001 sigue REGISTRADA sin técnico y no se registra ningún evento.

### AC-S02-10 — Destinatario inválido
**Dado** que COORD01 inició sesión e INC-0001 está REGISTRADA
**Cuando** intenta asignarla a SOL02 (que no es técnico) o a un id de usuario inexistente
**Entonces** el sistema rechaza la operación, INC-0001 sigue REGISTRADA sin técnico y no se registra ningún evento.

### AC-S02-11 — Reasignación prohibida
**Dado** que INC-0001 está ASIGNADA a T01
**Cuando** COORD01 intenta asignarla a T02, o de nuevo a T01
**Entonces** el sistema rechaza la operación, INC-0001 sigue ASIGNADA a T01 y el historial conserva un único evento de asignación.

### AC-S02-12 — Otros estados incompatibles
**Dado** que una incidencia está EN_ATENCION, PENDIENTE_VALIDACION o CERRADA
**Cuando** COORD01 intenta asignarla
**Entonces** el sistema rechaza la operación y conserva su estado, su técnico y su historial sin cambios.

### AC-S02-13 — Incidencia inexistente
**Dado** que COORD01 inició sesión y no existe la incidencia INC-9999
**Cuando** intenta asignarla a T01
**Entonces** el sistema informa que no la encuentra y no crea asignaciones ni eventos.

## Diseño y tareas vinculadas a cada AC

**Diseño:**
- Función de dominio `calcular_prioridad(riesgo_personas, impacto)`, usada por el registro (S01).
- Servicio `asignar_incidencia(incidencia_id, tecnico_id, usuario_sesion)` con las verificaciones de permiso, estado y técnico, y una transacción única para estado, técnico y evento.
- Ruta `POST /incidencias/<id>/asignar`, que solo lee la identidad de la sesión.
- Vista del coordinador con incidencias REGISTRADAS y un selector de técnicos activos.

| Tarea | Descripción | AC cubiertos |
|---|---|---|
| T-S02-01 | Implementar `calcular_prioridad` y usarla en el registro | 01, 02, 03, 04 |
| T-S02-02 | Ignorar prioridad enviada por el cliente | 05 |
| T-S02-03 | Servicio de asignación con transacción y evento | 06 |
| T-S02-04 | Verificación de sesión y rol en el servidor | 07, 08 |
| T-S02-05 | Validación del destinatario (existe, es técnico, activo) | 09, 10 |
| T-S02-06 | Validación de estado REGISTRADA; sin reasignación | 11, 12 |
| T-S02-07 | Manejo de incidencia inexistente | 13 |
| T-S02-08 | Vista del coordinador: incidencias REGISTRADAS y técnicos activos | 06 |
| T-S02-09 | Pruebas automatizadas | 01–13 |

## Pruebas y resultados esperados

Los resultados esperados se escriben a mano y no se calculan con la función de producción. Se usa una base de prueba independiente. T03 (técnico inactivo) existe solo en la base de prueba.

| Prueba | AC | Entrada | Resultado esperado |
|---|---|---|---|
| P-S02-01 | 01 | riesgo=true, impacto=BAJO | prioridad CRITICA |
| P-S02-02 | 02 | riesgo=true, impacto=ALTO | prioridad CRITICA |
| P-S02-03 | 03 | riesgo=false, impacto=ALTO | prioridad ALTA |
| P-S02-04 | 04 | riesgo=false, impacto=BAJO | prioridad NORMAL |
| P-S02-05 | 05 | riesgo=false, impacto=BAJO, prioridad=CRITICA | prioridad NORMAL |
| P-S02-06 | 06 | COORD01 asigna INC-0001 a T01 | ASIGNADA, técnico T01, 1 evento ASIGNAR |
| P-S02-07 | 07 | SOL01 asigna INC-0001 a T02 | Rechazo; REGISTRADA; 0 eventos nuevos |
| P-S02-08 | 08 | Sin sesión | Redirección a login; sin cambios |
| P-S02-09 | 09 | COORD01 asigna a T03 inactivo | Rechazo; REGISTRADA; 0 eventos nuevos |
| P-S02-10 | 10 | COORD01 asigna a SOL02 | Rechazo; REGISTRADA; 0 eventos nuevos |
| P-S02-11 | 11 | INC-0001 ASIGNADA a T01; COORD01 asigna a T02 | Rechazo; sigue T01; 1 solo evento ASIGNAR |
| P-S02-12 | 12 | Incidencia EN_ATENCION; COORD01 asigna | Rechazo; estado y técnico sin cambios |
| P-S02-13 | 13 | COORD01 asigna INC-9999 | "No encontrada"; sin registros nuevos |

## Decisión de revisión

**Revisión de v0.1**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Requiere cambios
- Observaciones: faltaba el evento de historial en la asignación, campos de la plantilla, momento del cálculo de prioridad, prohibición explícita de reasignación, destinatario inválido, ausencia de efectos en rechazos, exclusiones y datos concretos. Resuelto en v0.2.

**Revisión de v0.2**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Aprobada → v1.0
- Observaciones: se verificó, contra el enunciado de RF02, RF05 y las reglas que no pueden
  cambiarse, que los ocho hallazgos de la revisión v0.1 quedaron resueltos:
  1. AC-S02-06 exige el evento de historial con autor, fecha UTC, estados y acción.
  2. La plantilla está completa: entradas, precondiciones, salidas, errores, diseño,
     tareas y pruebas.
  3. La prioridad se calcula en el servidor al registrar, no se edita y se ignora
     si la envía el cliente (AC-S02-05).
  4. La reasignación está prohibida explícitamente (AC-S02-11).
  5. Se cubre el destinatario inexistente o sin rol técnico (AC-S02-10).
  6. Todos los rechazos indican que no hay cambios de estado, asignación ni historial.
  7. Las exclusiones incluyen la especialidad del técnico y la reasignación.
  8. Los criterios usan datos concretos y verificables.
- Condiciones: S01 debe alinearse con AC-S02-05 (el registro no recibe prioridad), y T03
  (técnico inactivo) se crea solo en la base de prueba, sin modificar el seed oficial.
- Nota de trazabilidad: los cambios de v0.2 fueron redactados por el revisor con apoyo de IA
  (ver bitácora); se solicita la conformidad del autor original.

**Conformidad del autor original**
- Autor: cbalmaooo
- Fecha: 2026-10-10
- Decisión: Se aceptan los cambios de revisión.
