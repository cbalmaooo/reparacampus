# S03 — Atender una incidencia y registrar la solución

**Requisito relacionado:** RF03  
**Estado:** Borrador, pendiente de revisión  
**Versión:** 0.1

## Historia de usuario

Como técnico asignado, quiero iniciar la atención de una incidencia y registrar la solución, para que el solicitante pueda revisar el resultado.

## Alcance

El técnico asignado puede cambiar una incidencia de ASIGNADA a EN_ATENCION. Cuando ya está EN_ATENCION, puede registrar una solución. La incidencia pasa entonces a PENDIENTE_VALIDACION.

La solución debe tener entre 20 y 800 caracteres.

## Permisos

Solo el técnico asignado a la incidencia puede iniciar su atención y registrar una solución.

## Criterios de aceptación

### AC-S03-01 — Iniciar atención

**Dado** que una incidencia está ASIGNADA a un técnico  
**Cuando** ese técnico inicia la atención  
**Entonces** el sistema cambia su estado a EN_ATENCION y guarda el evento en el historial.

### AC-S03-02 — Técnico diferente

**Dado** que una incidencia está asignada a un técnico  
**Cuando** otro técnico intenta iniciar la atención  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S03-03 — Solución válida

**Dado** que la incidencia está EN_ATENCION y la atiende el técnico asignado  
**Cuando** registra una solución de entre 20 y 800 caracteres  
**Entonces** el sistema guarda la solución y cambia el estado a PENDIENTE_VALIDACION.

### AC-S03-04 — Solución demasiado corta

**Dado** que la incidencia está EN_ATENCION  
**Cuando** el técnico registra una solución de 19 caracteres  
**Entonces** el sistema rechaza la solución e informa que debe tener al menos 20 caracteres.

### AC-S03-05 — Solución demasiado larga

**Dado** que la incidencia está EN_ATENCION  
**Cuando** el técnico registra una solución de 801 caracteres  
**Entonces** el sistema rechaza la solución e informa que no puede superar 800 caracteres.

### AC-S03-06 — Solución antes de iniciar atención

**Dado** que una incidencia está ASIGNADA  
**Cuando** el técnico intenta registrar una solución sin haber iniciado la atención  
**Entonces** el sistema rechaza la operación y la incidencia sigue ASIGNADA.

### AC-S03-07 — Estado incompatible

**Dado** que una incidencia no está ASIGNADA ni EN_ATENCION, según la operación solicitada  
**Cuando** el técnico intenta iniciar su atención o registrar una solución  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S03-08 — Solución guardada en el historial

**Dado** que el técnico asignado registra una solución válida  
**Cuando** el sistema la acepta  
**Entonces** guarda el texto de la solución y el evento correspondiente en el historial de la incidencia.

## Tareas propuestas

- Permitir al técnico asignado iniciar la atención.
- Permitir registrar y validar el texto de la solución.
- Cambiar el estado a EN_ATENCION o PENDIENTE_VALIDACION cuando corresponda.
- Guardar los eventos y la solución en el historial.
- Crear pruebas para los criterios de aceptación.

## Revisión

- **Revisó:** pendiente
- **Fecha:** pendiente
- **Decisión:** pendiente
- **Observaciones:** pendiente
