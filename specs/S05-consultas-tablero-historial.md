# S05 — Consultar incidencias, tablero e historial

**Requisito relacionado:** RF05  
**Estado:** Borrador, pendiente de revisión  
**Versión:** 0.1

## Historia de usuario

Como usuario del sistema, quiero consultar las incidencias que me corresponden. Como coordinador, también quiero ver un tablero con el estado general para organizar el mantenimiento.

## Alcance

El sistema permite listar incidencias con filtros por estado y prioridad. La información visible depende del rol:

- **Solicitante:** consulta sus propias incidencias.
- **Técnico:** consulta las incidencias que tiene asignadas.
- **Coordinador:** consulta todas las incidencias y accede al tablero.

Cada creación y transición exitosa se registra en el historial con autor, fecha, estado anterior, estado nuevo y acción. El historial conserva las soluciones, motivos, cierres y reaperturas. No se permite editarlo ni borrarlo.

El tablero del coordinador muestra cantidades por estado y prioridad, incidencias CRITICA que no estén cerradas y porcentaje de cierre. El porcentaje se calcula así: incidencias CERRADAS ÷ total de incidencias × 100, con un decimal. Si no hay incidencias, muestra 0,0 %.

## Permisos

Cada usuario solo puede consultar las incidencias permitidas para su rol. Solo el coordinador puede consultar todas las incidencias y ver el tablero general.

## Criterios de aceptación

### AC-S05-01 — Solicitante consulta las propias

**Dado** que inició sesión un solicitante  
**Cuando** consulta la lista de incidencias  
**Entonces** el sistema muestra únicamente las incidencias registradas por ese solicitante.

### AC-S05-02 — Técnico consulta sus asignaciones

**Dado** que inició sesión un técnico  
**Cuando** consulta la lista de incidencias  
**Entonces** el sistema muestra únicamente las incidencias asignadas a ese técnico.

### AC-S05-03 — Coordinador consulta todas

**Dado** que inició sesión un coordinador  
**Cuando** consulta la lista de incidencias  
**Entonces** el sistema muestra todas las incidencias.

### AC-S05-04 — Filtro por estado

**Dado** que el usuario puede consultar ciertas incidencias  
**Cuando** filtra por un estado  
**Entonces** el sistema muestra solo las incidencias permitidas que tienen ese estado.

### AC-S05-05 — Filtro por prioridad

**Dado** que el usuario puede consultar ciertas incidencias  
**Cuando** filtra por una prioridad  
**Entonces** el sistema muestra solo las incidencias permitidas que tienen esa prioridad.

### AC-S05-06 — Historial de una transición exitosa

**Dado** que ocurre una transición válida en una incidencia  
**Cuando** el sistema la completa  
**Entonces** registra en el historial el autor, la fecha, el estado anterior, el estado nuevo y la acción.

### AC-S05-07 — Historial de soluciones y motivos

**Dado** que una incidencia tiene soluciones, rechazos, cierres o reaperturas  
**Cuando** un usuario autorizado consulta su historial  
**Entonces** puede ver esos datos y los eventos anteriores, sin que se sobrescriban.

### AC-S05-08 — Historial no editable

**Dado** que un usuario consulta el historial  
**Cuando** intenta editar o borrar un evento  
**Entonces** el sistema rechaza la operación y conserva el historial.

### AC-S05-09 — Tablero del coordinador

**Dado** que inició sesión un coordinador  
**Cuando** consulta el tablero  
**Entonces** ve las cantidades de incidencias por estado y prioridad, las incidencias CRITICA no cerradas y el porcentaje de cierre con un decimal.

### AC-S05-10 — Tablero vacío

**Dado** que no hay incidencias registradas  
**Cuando** el coordinador consulta el tablero  
**Entonces** el porcentaje de cierre es 0,0 %.

### AC-S05-11 — Cálculo del porcentaje

**Dado** que hay cuatro incidencias y una está CERRADA  
**Cuando** el coordinador consulta el tablero  
**Entonces** el porcentaje de cierre es 25,0 %.

### AC-S05-12 — Incidencia crítica no cerrada

**Dado** que hay una incidencia con prioridad CRITICA cuyo estado no es CERRADA  
**Cuando** el coordinador consulta el tablero  
**Entonces** esa incidencia aparece entre las CRITICA no cerradas.

### AC-S05-13 — El tablero refleja la reapertura y conserva el cierre

**Dado** que hay cuatro incidencias, una está CERRADA y su evento de cierre consta en el historial  
**Cuando** su solicitante dueño la reabre dentro de las 48 horas con un motivo válido  
**Entonces** el porcentaje de cierre baja de 25,0 % a 0,0 %, la incidencia queda EN_ATENCION y el evento del cierre anterior permanece en el historial.

## Tareas propuestas

- Crear la lista de incidencias con visibilidad según el rol.
- Agregar filtros por estado y prioridad.
- Mostrar el historial completo y protegerlo contra edición o borrado.
- Crear el tablero del coordinador con sus cantidades e indicadores.
- Verificar que la reapertura reduzca el porcentaje de cierre y conserve los cierres anteriores.
- Crear pruebas para los criterios de aceptación.

## Revisión

- **Revisó:** pendiente
- **Fecha:** pendiente
- **Decisión:** pendiente
- **Observaciones:** pendiente
