# S01 — Registrar una incidencia

**Requisito relacionado:** RF01 (relación con RF02 y RF05)
**Versión:** 1.0
**Estado:** Aprobada
**Autor:** cbalmaooo (v0.1) · Alejandro Borja (cambios v0.2)
**Revisor:** Alejandro Borja
**Fecha:** 2026-10-13

### Historial de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 0.1 | 2026-10-12 | cbalmaooo | Borrador inicial |
| 0.2 | 2026-10-13 | Alejandro Borja | Correcciones de la revisión v0.1 |
| 1.0 | 2026-10-13 | Alejandro Borja | Aprobación |

## Historia de usuario

Como solicitante, quiero registrar un daño de infraestructura indicando dónde ocurre, qué pasó, su impacto y si hay riesgo para personas, para que la universidad pueda priorizarlo y atenderlo.

## Alcance y exclusiones

**Incluye:**
- Registro de una incidencia por un solicitante autenticado.
- Generación en el servidor de código, autor, fecha UTC, estado REGISTRADA y prioridad (regla definida en S02).
- Evento de creación en el historial.

**Excluye:**
- Editar o borrar reportes después de registrados.
- Adjuntos y notificaciones.
- Asignación a técnico (S02).

## Entradas

| Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|
| ubicacion | texto | Sí | LAB-01, AULA-201, BIB-01 |
| categoria | texto | Sí | ELECTRICIDAD, HIDRAULICA, MOBILIARIO, TIC |
| descripcion | texto | Sí | 20 a 500 caracteres después de retirar espacios externos |
| impacto | texto | Sí | BAJO, ALTO |
| riesgo_personas | booleano | Sí | true / false (en el formulario: Sí / No) |

El servidor no acepta del cliente los campos código, autor, fecha, estado ni prioridad: si llegan en la petición, los ignora.

## Precondiciones y permisos

- Sesión iniciada con rol SOLICITANTE.
- Coordinador y técnicos no pueden registrar incidencias.
- Identidad y rol se obtienen de la sesión en el servidor; ocultar el formulario no basta.

## Reglas y proceso

1. Verificar sesión y rol SOLICITANTE.
2. Retirar espacios externos de la descripción.
3. Validar que todos los campos estén presentes y tengan valores permitidos, y que la descripción mida de 20 a 500 caracteres.
4. Calcular la prioridad con la regla de S02 (riesgo → CRITICA; sin riesgo y ALTO → ALTA; sin riesgo y BAJO → NORMAL).
5. En una sola transacción: crear la incidencia con código único, autor (usuario de la sesión), fecha UTC del servidor, estado REGISTRADA y prioridad calculada, y registrar el evento de creación.
6. Si cualquier validación falla, rechazar sin crear incidencia ni evento.

**Supuesto pendiente de confirmar con el cliente:** formato del código `INC-0001`, consecutivo y único (ver `preguntas-cliente.md`).

## Salidas y cambios persistidos

**Registro exitoso:**
- La incidencia queda guardada con sus cinco campos, la descripción recortada, código, autor, fecha UTC, estado REGISTRADA y prioridad.
- Se registra un evento con autor, fecha UTC, estado anterior (ninguno), estado nuevo REGISTRADA y acción REGISTRAR.
- La interfaz muestra el código generado.
- Los textos se muestran escapados; no se ejecutan como HTML ni como script.
- Los datos permanecen tras reiniciar el servidor.

**Registro rechazado:** mensaje que indica qué campo falla, sin incidencia ni evento nuevos.

## Errores y efectos que deben evitarse

| Situación | Respuesta esperada | Efecto prohibido |
|---|---|---|
| Sin sesión | Redirigir a inicio de sesión | Crear incidencia |
| Rol distinto de SOLICITANTE | Rechazo por falta de permiso | Crear incidencia |
| Campo obligatorio ausente o vacío | Mensaje con los campos faltantes | Crear incidencia o evento |
| Ubicación, categoría, impacto o riesgo no permitidos | Mensaje de valor inválido | Crear incidencia o evento |
| Descripción fuera de 20–500 tras recortar | Mensaje con el límite incumplido | Crear incidencia o evento |
| Cliente envía código, autor, fecha, estado o prioridad | Se ignoran; el servidor los genera | Aceptar valores del cliente |
| Falla durante la transacción | Rechazo general | Incidencia sin evento o evento sin incidencia |

## Criterios de aceptación

### AC-S01-01 — Registro válido
**Dado** que SOL01 inició sesión
**Cuando** registra ubicación LAB-01, categoría ELECTRICIDAD, descripción "El tomacorriente del puesto 4 hace chispas", impacto ALTO y riesgo true
**Entonces** se crea una incidencia con código único, autor SOL01, fecha UTC, estado REGISTRADA y prioridad CRITICA, y se registra un evento con autor SOL01, estado nuevo REGISTRADA y acción REGISTRAR.

### AC-S01-02 — Campo obligatorio vacío
**Dado** que SOL01 inició sesión
**Cuando** envía el formulario sin categoría y sin impacto
**Entonces** el sistema indica que faltan categoría e impacto y no crea incidencia ni evento.

### AC-S01-03 — Ubicación o categoría inválidas
**Dado** que SOL01 inició sesión
**Cuando** envía ubicación "LAB-99" o categoría "PINTURA" con los demás campos válidos
**Entonces** el sistema rechaza el registro por valor no permitido y no crea incidencia ni evento.

### AC-S01-04 — Impacto inválido
**Dado** que SOL01 inició sesión
**Cuando** envía impacto "MEDIO" con los demás campos válidos
**Entonces** el sistema rechaza el registro y no crea incidencia ni evento.

### AC-S01-05 — Riesgo inválido
**Dado** que SOL01 inició sesión
**Cuando** envía riesgo_personas "quizas" con los demás campos válidos
**Entonces** el sistema rechaza el registro y no crea incidencia ni evento.

### AC-S01-06 — Límite inferior de la descripción
**Dado** que SOL01 inició sesión y los demás campos son válidos
**Cuando** envía una descripción de exactamente 20 caracteres, y en otro intento una de 19
**Entonces** la de 20 se acepta y la de 19 se rechaza con el mensaje "La descripción debe tener al menos 20 caracteres", sin incidencia ni evento.

### AC-S01-07 — Límite superior de la descripción
**Dado** que SOL01 inició sesión y los demás campos son válidos
**Cuando** envía una descripción de exactamente 500 caracteres, y en otro intento una de 501
**Entonces** la de 500 se acepta y la de 501 se rechaza con el mensaje "La descripción no puede superar 500 caracteres", sin incidencia ni evento.

### AC-S01-08 — Espacios externos
**Dado** que SOL01 inició sesión y los demás campos son válidos
**Cuando** envía 19 caracteres rodeados de espacios, o una descripción solo de espacios
**Entonces** el sistema mide después de recortar y rechaza el registro sin cambios; si envía 20 caracteres rodeados de espacios, lo acepta y guarda el texto recortado.

### AC-S01-09 — Campos generados por el servidor
**Dado** que SOL01 inició sesión
**Cuando** envía un registro válido con riesgo false e impacto BAJO, más los campos estado = CERRADA, prioridad = CRITICA y autor = SOL02
**Entonces** el sistema ignora esos campos y crea la incidencia con estado REGISTRADA, prioridad NORMAL y autor SOL01.

### AC-S01-10 — Rol sin permiso
**Dado** que COORD01 o T01 inició sesión
**Cuando** intenta registrar una incidencia con datos válidos
**Entonces** el sistema rechaza la operación por falta de permiso y no crea incidencia ni evento.

### AC-S01-11 — Sin sesión
**Dado** que no hay sesión iniciada
**Cuando** se envía una petición de registro con datos válidos
**Entonces** el sistema redirige al inicio de sesión y no crea incidencia ni evento.

### AC-S01-12 — Texto parecido a HTML
**Dado** que SOL01 inició sesión
**Cuando** registra la descripción "<b>Fuga</b> de agua en el baño del segundo piso"
**Entonces** se guarda como texto y, al consultarla, se muestra literalmente, sin interpretarse como HTML.

### AC-S01-13 — Persistencia
**Dado** que SOL01 registró una incidencia válida
**Cuando** se reinicia el servidor y SOL01 vuelve a iniciar sesión
**Entonces** la incidencia y su evento de creación siguen disponibles con los mismos datos.

## Diseño y tareas vinculadas a cada AC

**Diseño:**
- Servicio `registrar_incidencia(datos, usuario_sesion)`, que usa `calcular_prioridad` (S02) y el validador de texto compartido (S03 y S04).
- Generador de código único en el servidor.
- Listas de valores permitidos definidas en un solo módulo de constantes.
- Ruta `POST /incidencias`, con identidad tomada de la sesión.
- Plantilla Jinja con autoescape activo; prohibido usar `|safe` con texto del usuario.

| Tarea | Descripción | AC cubiertos |
|---|---|---|
| T-S01-01 | Formulario de registro con listas de valores permitidos | 01 |
| T-S01-02 | Validación en servidor de obligatoriedad y valores permitidos | 02, 03, 04, 05 |
| T-S01-03 | Validación de descripción con recorte y límites | 06, 07, 08 |
| T-S01-04 | Servicio de registro con código, autor, fecha, estado, prioridad y evento en una transacción | 01, 09 |
| T-S01-05 | Verificación de sesión y rol | 10, 11 |
| T-S01-06 | Visualización escapada de textos | 12 |
| T-S01-07 | Persistencia en SQLite | 13 |
| T-S01-08 | Pruebas automatizadas | 01–13 |

## Pruebas y resultados esperados

Los resultados esperados se escriben a mano y no se calculan con funciones de producción. Se usa una base de prueba independiente.

| Prueba | AC | Entrada | Resultado esperado |
|---|---|---|---|
| P-S01-01 | 01 | Registro válido con riesgo true | REGISTRADA; CRITICA; autor SOL01; 1 evento REGISTRAR |
| P-S01-02 | 02 | Sin categoría ni impacto | Rechazo; 0 incidencias |
| P-S01-03 | 03 | Ubicación LAB-99 | Rechazo; 0 incidencias |
| P-S01-04 | 04 | Impacto MEDIO | Rechazo; 0 incidencias |
| P-S01-05 | 05 | Riesgo "quizas" | Rechazo; 0 incidencias |
| P-S01-06a | 06 | "A" × 20 | Aceptada |
| P-S01-06b | 06 | "A" × 19 | Rechazo; 0 incidencias |
| P-S01-07a | 07 | "A" × 500 | Aceptada |
| P-S01-07b | 07 | "A" × 501 | Rechazo; 0 incidencias |
| P-S01-08 | 08 | "   " + "A" × 19 + "   " | Rechazo; 0 incidencias |
| P-S01-09 | 09 | Envía estado, prioridad y autor falsos | REGISTRADA; NORMAL; autor SOL01 |
| P-S01-10 | 10 | COORD01 registra | Rechazo; 0 incidencias |
| P-S01-11 | 11 | Sin sesión | Redirección a login; 0 incidencias |
| P-S01-12 | 12 | Descripción con `<b>` | La respuesta contiene `&lt;b&gt;` |
| P-S01-13 | 13 | Registro, reinicio de la app y consulta | La incidencia y su evento persisten |

## Decisión de revisión

**Revisión de v0.1**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Requiere cambios
- Observaciones:
  1. Faltaba el evento de creación en el historial (RF05).
  2. No se especificaban los valores permitidos de ubicación y categoría ni criterios que los rechazaran.
  3. No se exigía medir la descripción después de retirar espacios externos.
  4. No se indicaba que código, autor, fecha, estado y prioridad los genera el servidor e ignora los del cliente (coherencia con AC-S02-05).
  5. No se indicaba el cálculo de la prioridad al registrar.
  6. Faltaban los casos de texto parecido a HTML y de persistencia tras reinicio.
  7. Plantilla incompleta: entradas con tipos, salidas, errores, diseño, tareas vinculadas a AC y pruebas.
  8. Inconsistencia: el encabezado indicaba v0.1 y el bloque de revisión, v1.0.

**Revisión de v0.2**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Aprobada → v1.0
- Observaciones: se verificó, contra RF01, RF02, RF05, los datos del prototipo y las reglas que no pueden cambiarse, que los ocho hallazgos quedaron resueltos (AC-S01-01 a AC-S01-13 y plantilla completa).
- Condiciones: el formato del código queda como supuesto hasta que el cliente responda; el validador de texto y `calcular_prioridad` se comparten con S02, S03 y S04.
- Nota de trazabilidad: los cambios de v0.2 fueron redactados por el revisor con apoyo de IA (ver bitácora); se solicita la conformidad del autor original.

**Conformidad del autor original**
- Autor: cbalmaooo
- Fecha: 13/10/2026
- Decisión: Cambios Aceptados.
