# S01 — Registrar una incidencia

**Requisito relacionado:** RF01  
**Estado:** Borrador, pendiente de revisión  
**Versión:** 0.1

## Historia de usuario

Como solicitante, quiero registrar un daño de infraestructura indicando dónde ocurre y qué pasó, para que la universidad pueda atenderlo.

## Alcance

Esta especificación cubre el registro de una incidencia. La prioridad y la asignación al técnico se especifican en S02.

## Datos de entrada

El solicitante debe proporcionar:

- Ubicación
- Categoría
- Descripción
- Impacto: BAJO o ALTO
- Riesgo para personas: sí o no

La descripción debe tener entre 20 y 500 caracteres. Todos los campos son obligatorios.

## Comportamiento esperado

Si los datos son válidos, el sistema crea la incidencia y genera su código, autor, fecha y estado inicial REGISTRADA. Si falta un dato o alguno no cumple las reglas, el sistema informa el error y no crea la incidencia.

## Permisos

Solo un usuario autenticado con rol de solicitante puede registrar incidencias.

## Criterios de aceptación

### AC-S01-01 — Registro válido

**Dado** que inició sesión un usuario con rol de solicitante  
**Cuando** completa todos los campos con valores válidos y envía el formulario  
**Entonces** el sistema crea la incidencia con un código, el autor correspondiente, una fecha y estado REGISTRADA.

### AC-S01-02 — Campo obligatorio vacío

**Dado** que el solicitante está llenando el formulario  
**Cuando** deja vacío uno o más campos obligatorios y lo envía  
**Entonces** el sistema muestra qué datos faltan y no crea la incidencia.

### AC-S01-03 — Descripción demasiado corta

**Dado** que el solicitante escribe una descripción de 19 caracteres  
**Cuando** intenta registrar la incidencia  
**Entonces** el sistema rechaza el registro e informa que la descripción debe tener al menos 20 caracteres.

### AC-S01-04 — Descripción en el límite mínimo

**Dado** que el solicitante escribe una descripción de 20 caracteres y completa válidamente los demás campos  
**Cuando** registra la incidencia  
**Entonces** el sistema la acepta.

### AC-S01-05 — Descripción en el límite máximo

**Dado** que el solicitante escribe una descripción de 500 caracteres y completa válidamente los demás campos  
**Cuando** registra la incidencia  
**Entonces** el sistema la acepta.

### AC-S01-06 — Descripción demasiado larga

**Dado** que el solicitante escribe una descripción de 501 caracteres  
**Cuando** intenta registrar la incidencia  
**Entonces** el sistema rechaza el registro e informa que la descripción no puede superar 500 caracteres.

### AC-S01-07 — Impacto inválido

**Dado** que el formulario contiene un impacto distinto de BAJO o ALTO  
**Cuando** el solicitante intenta registrar la incidencia  
**Entonces** el sistema rechaza el registro y no crea la incidencia.

### AC-S01-08 — Riesgo inválido

**Dado** que el formulario contiene un valor de riesgo distinto de sí o no  
**Cuando** el solicitante intenta registrar la incidencia  
**Entonces** el sistema rechaza el registro y no crea la incidencia.

### AC-S01-09 — Usuario sin permiso

**Dado** que inició sesión un usuario que no tiene rol de solicitante  
**Cuando** intenta registrar una incidencia  
**Entonces** el sistema rechaza la operación y no crea la incidencia.

### AC-S01-10 — Usuario sin sesión

**Dado** que una persona no ha iniciado sesión  
**Cuando** intenta registrar una incidencia  
**Entonces** el sistema le solicita iniciar sesión y no crea la incidencia.

### AC-S01-11 — Registro rechazado sin efectos

**Dado** que el formulario tiene datos inválidos  
**Cuando** el sistema rechaza el registro  
**Entonces** la incidencia no se guarda y no se agrega un evento de creación al historial.

## Tareas propuestas

- Crear el formulario de registro.
- Validar los campos en el servidor.
- Guardar los datos válidos y generar código, autor, fecha y estado.
- Mostrar errores sin guardar incidencias inválidas.
- Crear pruebas para los criterios de aceptación.

## Revisión

- **Revisó:** pendiente
- **Fecha:** pendiente
- **Decisión:** pendiente
- **Observaciones:** pendiente
