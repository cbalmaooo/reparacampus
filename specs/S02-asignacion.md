# S02 — Priorizar y asignar una incidencia

**Requisito relacionado:** RF02  
**Estado:** Borrador, pendiente de revisión  
**Versión:** 0.1

## Historia de usuario

Como coordinador, quiero que cada incidencia tenga una prioridad calculada y poder asignarla a un técnico activo, para organizar su atención.

## Alcance

El sistema calcula la prioridad según el riesgo para personas y el impacto reportado. El coordinador puede asignar una incidencia que esté en estado REGISTRADA a un técnico activo. Al asignarla, pasa a estado ASIGNADA.

## Reglas de prioridad

- Si hay riesgo para personas, la prioridad es CRITICA.
- Si no hay riesgo y el impacto es ALTO, la prioridad es ALTA.
- Si no hay riesgo y el impacto es BAJO, la prioridad es NORMAL.

El riesgo tiene prioridad sobre el impacto. Por ejemplo, riesgo sí e impacto BAJO produce prioridad CRITICA.

## Permisos

Solo el coordinador puede asignar incidencias. Solo se puede asignar a un técnico activo.

## Criterios de aceptación

### AC-S02-01 — Riesgo para personas

**Dado** que una incidencia tiene riesgo para personas  
**Cuando** el sistema calcula su prioridad  
**Entonces** la prioridad es CRITICA, sin importar si el impacto es BAJO o ALTO.

### AC-S02-02 — Impacto alto sin riesgo

**Dado** que una incidencia no tiene riesgo para personas y su impacto es ALTO  
**Cuando** el sistema calcula su prioridad  
**Entonces** la prioridad es ALTA.

### AC-S02-03 — Impacto bajo sin riesgo

**Dado** que una incidencia no tiene riesgo para personas y su impacto es BAJO  
**Cuando** el sistema calcula su prioridad  
**Entonces** la prioridad es NORMAL.

### AC-S02-04 — Asignación válida

**Dado** que inició sesión un coordinador y una incidencia está REGISTRADA  
**Cuando** la asigna a un técnico activo  
**Entonces** el sistema guarda la asignación y cambia la incidencia a ASIGNADA.

### AC-S02-05 — Usuario sin permiso

**Dado** que inició sesión alguien que no es coordinador  
**Cuando** intenta asignar una incidencia  
**Entonces** el sistema rechaza la operación y no cambia la incidencia ni su historial.

### AC-S02-06 — Técnico inactivo

**Dado** que la incidencia está REGISTRADA  
**Cuando** el coordinador intenta asignarla a un técnico inactivo  
**Entonces** el sistema rechaza la operación y la incidencia sigue REGISTRADA.

### AC-S02-07 — Estado incompatible

**Dado** que una incidencia ya está ASIGNADA o tiene otro estado distinto de REGISTRADA  
**Cuando** el coordinador intenta asignarla  
**Entonces** el sistema rechaza la operación y conserva su estado y asignación actuales.

### AC-S02-08 — Incidencia inexistente

**Dado** que no existe la incidencia indicada  
**Cuando** el coordinador intenta asignarla  
**Entonces** el sistema informa que no la encuentra y no registra cambios.

## Tareas propuestas

- Calcular y guardar la prioridad según las reglas.
- Mostrar al coordinador las incidencias REGISTRADAS y los técnicos activos.
- Permitir asignar una incidencia y cambiarla a ASIGNADA.
- Rechazar asignaciones sin permiso, a técnicos inactivos o en estados incompatibles.
- Crear pruebas para los criterios de aceptación.

## Revisión

- **Revisó:** pendiente
- **Fecha:** pendiente
- **Decisión:** pendiente
- **Observaciones:** pendiente
