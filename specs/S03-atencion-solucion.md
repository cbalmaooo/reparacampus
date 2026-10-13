# S03 — Atender una incidencia y registrar la solución

**Requisito relacionado:** RF03 (relación con RF04 y RF05)
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

Como técnico asignado, quiero iniciar la atención de una incidencia y registrar la solución, para que el solicitante pueda revisar y validar el resultado.

## Alcance y exclusiones

**Incluye:**
- Transición ASIGNADA → EN_ATENCION por el técnico asignado.
- Registro de una solución desde EN_ATENCION, con transición a PENDIENTE_VALIDACION.
- Registro de una nueva solución cuando la incidencia vuelve a EN_ATENCION por rechazo o reapertura (S04), conservando las soluciones anteriores.
- Evento de historial en cada transición exitosa.

**Excluye:**
- Editar o borrar soluciones ya registradas.
- Cerrar la incidencia: solo el solicitante la cierra al confirmar (S04).
- Devolver la incidencia a ASIGNADA o transferirla a otro técnico.
- Adjuntos y notificaciones.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|---|
| Iniciar atención | incidencia_id | entero o código | Sí | Debe existir |
| Registrar solución | incidencia_id | entero o código | Sí | Debe existir |
| Registrar solución | solucion | texto | Sí | De 20 a 800 caracteres después de retirar espacios externos |

Identidad y rol: se obtienen de la sesión en el servidor, nunca de la petición.

## Precondiciones y permisos

- Sesión iniciada con rol TECNICO.
- El técnico de la sesión es el técnico asignado a la incidencia.
- Iniciar atención: el estado actual es ASIGNADA.
- Registrar solución: el estado actual es EN_ATENCION.
- Solicitantes, coordinador y técnicos no asignados no pueden ejecutar estas operaciones. El servidor lo comprueba en cada operación; ocultar botones no basta.

## Reglas y proceso

**Iniciar atención:**
1. Verificar sesión, rol TECNICO y que sea el técnico asignado.
2. Verificar que el estado sea ASIGNADA.
3. En una sola transacción: cambiar el estado a EN_ATENCION y registrar el evento.

**Registrar solución:**
1. Verificar sesión, rol TECNICO y que sea el técnico asignado.
2. Verificar que el estado sea EN_ATENCION.
3. Retirar espacios externos del texto y validar una longitud de 20 a 800 caracteres.
4. En una sola transacción: guardar la solución como un registro nuevo (sin sobrescribir las anteriores), cambiar el estado a PENDIENTE_VALIDACION y registrar el evento.

Cualquier verificación fallida rechaza la operación sin modificar estado, soluciones ni historial. El técnico asignado no cambia en ninguna operación de esta SPEC.

## Salidas y cambios persistidos

**Iniciar atención exitoso:** estado EN_ATENCION y un evento con autor (técnico de la sesión), fecha y hora UTC del servidor, estado anterior ASIGNADA, estado nuevo EN_ATENCION y acción INICIAR_ATENCION.

**Solución exitosa:** un registro de solución nuevo con texto recortado, autor y fecha UTC; estado PENDIENTE_VALIDACION; y un evento con autor, fecha UTC, estado anterior EN_ATENCION, estado nuevo PENDIENTE_VALIDACION, acción REGISTRAR_SOLUCION y referencia a la solución.

**Visualización:** la solución se muestra como texto escapado; no se interpreta como HTML ni se ejecuta como script.

**Operación rechazada:** mensaje de error comprensible, sin cambios en estado, soluciones ni historial.

## Errores y efectos que deben evitarse

| Situación | Respuesta esperada | Efecto prohibido |
|---|---|---|
| Sin sesión | Redirigir a inicio de sesión | Cualquier cambio |
| Rol distinto de TECNICO | Rechazo por falta de permiso | Cualquier cambio |
| Técnico no asignado | Rechazo por falta de permiso | Cualquier cambio |
| Incidencia inexistente | Mensaje "incidencia no encontrada" | Crear registros |
| Iniciar con estado distinto de ASIGNADA | Rechazo por estado incompatible | Cambio de estado o evento |
| Solución con estado distinto de EN_ATENCION | Rechazo por estado incompatible | Guardar solución |
| Solución fuera de 20–800 tras recortar | Mensaje con el límite incumplido | Guardar solución o cambiar estado |
| Falla durante la transacción | Rechazo general | Efectos parciales |
| Nueva solución tras rechazo o reapertura | Se agrega como registro nuevo | Sobrescribir o borrar soluciones anteriores |

## Criterios de aceptación

### AC-S03-01 — Iniciar atención
**Dado** que T01 inició sesión e INC-0001 está ASIGNADA a T01
**Cuando** T01 inicia la atención
**Entonces** INC-0001 queda EN_ATENCION, sigue asignada a T01 y se registra un evento con autor T01, fecha UTC, estado anterior ASIGNADA, estado nuevo EN_ATENCION y acción INICIAR_ATENCION.

### AC-S03-02 — Técnico no asignado
**Dado** que INC-0001 está ASIGNADA a T01
**Cuando** T02 intenta iniciar la atención o registrar una solución
**Entonces** el sistema rechaza la operación por falta de permiso y INC-0001 conserva su estado, su técnico y su historial sin cambios.

### AC-S03-03 — Otros roles y sin sesión
**Dado** que INC-0001 está ASIGNADA a T01
**Cuando** SOL01 o COORD01 intentan iniciar la atención, o se envía la petición sin sesión
**Entonces** el sistema rechaza la operación (o redirige al inicio de sesión) y no modifica la incidencia ni el historial.

### AC-S03-04 — Iniciar atención dos veces
**Dado** que INC-0001 ya está EN_ATENCION con T01
**Cuando** T01 intenta iniciar la atención de nuevo
**Entonces** el sistema rechaza la operación por estado incompatible y el historial conserva un único evento INICIAR_ATENCION.

### AC-S03-05 — Solución válida
**Dado** que INC-0001 está EN_ATENCION con T01
**Cuando** T01 registra la solución "Se reemplazó el tomacorriente dañado del puesto 4"
**Entonces** se guarda la solución con autor T01 y fecha UTC, INC-0001 queda PENDIENTE_VALIDACION y se registra un evento con estado anterior EN_ATENCION, estado nuevo PENDIENTE_VALIDACION y acción REGISTRAR_SOLUCION.

### AC-S03-06 — Límite inferior
**Dado** que INC-0001 está EN_ATENCION con T01
**Cuando** T01 registra una solución de exactamente 20 caracteres, y en otro intento una de 19 caracteres
**Entonces** la de 20 se acepta y la de 19 se rechaza con el mensaje "La solución debe tener al menos 20 caracteres"; en el rechazo, INC-0001 sigue EN_ATENCION sin solución nueva ni evento.

### AC-S03-07 — Límite superior
**Dado** que INC-0001 está EN_ATENCION con T01
**Cuando** T01 registra una solución de exactamente 800 caracteres, y en otro intento una de 801 caracteres
**Entonces** la de 800 se acepta y la de 801 se rechaza con el mensaje "La solución no puede superar 800 caracteres"; en el rechazo, INC-0001 sigue EN_ATENCION sin solución nueva ni evento.

### AC-S03-08 — Espacios externos
**Dado** que INC-0001 está EN_ATENCION con T01
**Cuando** T01 envía 19 caracteres rodeados de espacios, o un texto solo con espacios
**Entonces** el sistema mide la longitud después de retirar los espacios externos y rechaza la solución sin cambios; si envía 20 caracteres rodeados de espacios, la acepta y guarda el texto sin esos espacios.

### AC-S03-09 — Solución antes de iniciar atención
**Dado** que INC-0001 está ASIGNADA a T01
**Cuando** T01 intenta registrar una solución válida sin haber iniciado la atención
**Entonces** el sistema rechaza la operación por estado incompatible, INC-0001 sigue ASIGNADA y no se guarda solución ni evento.

### AC-S03-10 — Otros estados incompatibles
**Dado** que una incidencia asignada a T01 está REGISTRADA, PENDIENTE_VALIDACION o CERRADA
**Cuando** T01 intenta iniciar la atención o registrar una solución
**Entonces** el sistema rechaza la operación y conserva el estado, las soluciones y el historial sin cambios.

### AC-S03-11 — Nueva solución tras rechazo
**Dado** que INC-0001 volvió a EN_ATENCION con T01 después de que SOL01 rechazó la solución S1 (S04)
**Cuando** T01 registra una nueva solución válida S2
**Entonces** INC-0001 queda PENDIENTE_VALIDACION, se conservan S1 y S2 con sus fechas y el historial muestra ambos eventos REGISTRAR_SOLUCION.

### AC-S03-12 — Texto parecido a HTML
**Dado** que INC-0001 está EN_ATENCION con T01
**Cuando** T01 registra la solución "<script>alert('x')</script> cambio de breaker principal"
**Entonces** se guarda como texto y, al consultarla, se muestra literalmente, sin ejecutarse como script.

### AC-S03-13 — Incidencia inexistente
**Dado** que T01 inició sesión y no existe INC-9999
**Cuando** intenta iniciar su atención o registrar una solución
**Entonces** el sistema informa que no la encuentra y no crea registros.

## Diseño y tareas vinculadas a cada AC

**Diseño:**
- Servicio `iniciar_atencion(incidencia_id, usuario_sesion)`.
- Servicio `registrar_solucion(incidencia_id, texto, usuario_sesion)`.
- Validador compartido de texto (recorte y límites), reutilizable en S01 y S04.
- Tabla de soluciones con relación 1:N con incidencia; nunca se actualiza una solución existente.
- Rutas `POST /incidencias/<id>/iniciar` y `POST /incidencias/<id>/solucion`, con la identidad tomada de la sesión.
- Plantillas Jinja con autoescape activo; prohibido usar `|safe` con texto del usuario.

| Tarea | Descripción | AC cubiertos |
|---|---|---|
| T-S03-01 | Servicio iniciar_atencion con transacción y evento | 01, 04 |
| T-S03-02 | Verificación de sesión, rol y técnico asignado | 02, 03 |
| T-S03-03 | Validador de texto con recorte y límites | 06, 07, 08 |
| T-S03-04 | Servicio registrar_solucion con transacción, solución nueva y evento | 05, 11 |
| T-S03-05 | Validación de estados por operación | 09, 10 |
| T-S03-06 | Manejo de incidencia inexistente | 13 |
| T-S03-07 | Vista del técnico: botones Iniciar y Registrar solución, texto escapado | 01, 05, 12 |
| T-S03-08 | Pruebas automatizadas | 01–13 |

## Pruebas y resultados esperados

Los resultados esperados se escriben a mano y no se calculan con funciones de producción. Se usa una base de prueba independiente. Los textos de longitud exacta se construyen en la prueba (por ejemplo, "A" × 20).

| Prueba | AC | Entrada | Resultado esperado |
|---|---|---|---|
| P-S03-01 | 01 | T01 inicia INC-0001 ASIGNADA | EN_ATENCION; técnico T01; 1 evento INICIAR_ATENCION |
| P-S03-02 | 02 | T02 inicia INC-0001 de T01 | Rechazo; ASIGNADA; 0 eventos nuevos |
| P-S03-03 | 03 | SOL01 inicia INC-0001 | Rechazo; sin cambios |
| P-S03-04 | 04 | T01 inicia INC-0001 ya EN_ATENCION | Rechazo; 1 solo evento INICIAR_ATENCION |
| P-S03-05 | 05 | T01 registra texto válido | PENDIENTE_VALIDACION; 1 solución; 1 evento REGISTRAR_SOLUCION |
| P-S03-06a | 06 | "A" × 20 | Aceptada |
| P-S03-06b | 06 | "A" × 19 | Rechazo; EN_ATENCION; 0 soluciones |
| P-S03-07a | 07 | "A" × 800 | Aceptada |
| P-S03-07b | 07 | "A" × 801 | Rechazo; EN_ATENCION; 0 soluciones |
| P-S03-08 | 08 | "   " + "A" × 19 + "   " | Rechazo; sin cambios |
| P-S03-09 | 09 | Solución con INC-0001 ASIGNADA | Rechazo; ASIGNADA; 0 soluciones |
| P-S03-10 | 10 | Solución con incidencia CERRADA | Rechazo; estado y soluciones sin cambios |
| P-S03-11 | 11 | Rechazo de S1 y nueva solución S2 | PENDIENTE_VALIDACION; 2 soluciones guardadas |
| P-S03-12 | 12 | Texto con `<script>` | La respuesta HTML contiene `&lt;script&gt;` |
| P-S03-13 | 13 | T01 inicia INC-9999 | "No encontrada"; sin registros nuevos |

## Decisión de revisión

**Revisión de v0.1**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Requiere cambios
- Observaciones:
  1. No contemplaba una nueva solución tras rechazo o reapertura (RF04): riesgo de sobrescribir la anterior.
  2. No exigía medir la longitud después de retirar espacios externos ni probaba los límites exactos de 20 y 800.
  3. Los rechazos por longitud no indicaban "sin cambios de estado ni eventos".
  4. AC-S03-03 no exigía el evento de historial con autor, fecha, estados y acción.
  5. Faltaban casos de solicitante o coordinador, sin sesión, iniciar dos veces e incidencia inexistente.
  6. Faltaba el caso de texto parecido a HTML.
  7. Plantilla incompleta: entradas, precondiciones, salidas, errores, diseño, tareas vinculadas a AC y pruebas.
  8. Criterios sin datos concretos.

**Revisión de v0.2**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Aprobada → v1.0
- Observaciones: se verificó, contra RF03, RF04, RF05 y las reglas que no pueden cambiarse, que los ocho hallazgos quedaron resueltos (AC-S03-01 a AC-S03-13 y secciones completas de la plantilla).
- Condiciones: S04 debe conservar el mismo técnico y las soluciones anteriores al rechazar o reabrir, en coherencia con AC-S03-11; el validador de texto se comparte con S01 y S04.
- Nota de trazabilidad: los cambios de v0.2 fueron redactados por el revisor con apoyo de IA (ver bitácora); se solicita la conformidad del autor original.

**Conformidad del autor original**
- Autor: cbalmaooo
- Fecha: 13/10/2026
- Decisión: Cambios aceptados
