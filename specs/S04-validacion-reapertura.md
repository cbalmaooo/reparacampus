# S04 — Validar o reabrir una incidencia

**Requisito relacionado:** RF04  
**Estado:** Borrador, pendiente de revisión  
**Versión:** 0.1

## Historia de usuario

Como solicitante que registró la incidencia, quiero confirmar si la solución funcionó, rechazarla si el daño continúa o reabrir el caso si vuelve a ocurrir, para asegurar que el problema quede resuelto.

## Alcance

El solicitante dueño de la incidencia puede:

- Confirmar una solución cuando está PENDIENTE_VALIDACION. La incidencia pasa a CERRADA.
- Rechazarla indicando un motivo de 10 a 300 caracteres. Vuelve a EN_ATENCION, conserva el mismo técnico y guarda la solución anterior.
- Reabrir una incidencia CERRADA dentro de las 48 horas siguientes al último cierre, indicando un motivo de 10 a 300 caracteres. Vuelve a EN_ATENCION y conserva el mismo técnico.

El sistema calcula el plazo de reapertura con la fecha del servidor en UTC. Al reabrir, conserva los cierres y soluciones anteriores.

## Permisos

Solo el solicitante dueño de la incidencia puede confirmar, rechazar o reabrir. El coordinador y otros solicitantes no pueden hacerlo en su nombre.

## Criterios de aceptación

### AC-S04-01 — Confirmar solución

**Dado** que la incidencia está PENDIENTE_VALIDACION y quien la consulta es su solicitante dueño  
**Cuando** confirma que la solución funcionó  
**Entonces** el sistema cambia el estado a CERRADA y registra el cierre en el historial.

### AC-S04-02 — Rechazar solución con motivo válido

**Dado** que la incidencia está PENDIENTE_VALIDACION y quien la consulta es su solicitante dueño  
**Cuando** rechaza la solución con un motivo de entre 10 y 300 caracteres  
**Entonces** el sistema cambia el estado a EN_ATENCION, conserva el mismo técnico y la solución anterior, y registra el motivo en el historial.

### AC-S04-03 — Rechazo con motivo demasiado corto

**Dado** que la incidencia está PENDIENTE_VALIDACION  
**Cuando** el solicitante dueño intenta rechazar la solución con un motivo de 9 caracteres  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S04-04 — Rechazo con motivo demasiado largo

**Dado** que la incidencia está PENDIENTE_VALIDACION  
**Cuando** el solicitante dueño intenta rechazar la solución con un motivo de 301 caracteres  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S04-05 — Reapertura dentro del plazo

**Dado** que la incidencia está CERRADA y han pasado menos de 48 horas desde el último cierre  
**Cuando** el solicitante dueño la reabre con un motivo de entre 10 y 300 caracteres  
**Entonces** el sistema cambia el estado a EN_ATENCION, conserva el mismo técnico y los cierres y soluciones anteriores, y registra la reapertura.

### AC-S04-06 — Reapertura justo a las 48 horas

**Dado** que la incidencia está CERRADA y han pasado exactamente 48 horas desde el último cierre  
**Cuando** el solicitante dueño intenta reabrirla con un motivo válido  
**Entonces** el sistema acepta la reapertura y cambia el estado a EN_ATENCION.

### AC-S04-07 — Reapertura fuera del plazo

**Dado** que han pasado más de 48 horas desde el último cierre  
**Cuando** el solicitante dueño intenta reabrir la incidencia  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S04-08 — Solicitante distinto del dueño

**Dado** que quien intenta realizar la operación no es el solicitante dueño  
**Cuando** intenta confirmar, rechazar o reabrir la incidencia  
**Entonces** el sistema rechaza la operación y no cambia el estado ni el historial.

### AC-S04-09 — Rol distinto del solicitante

**Dado** que la incidencia está PENDIENTE_VALIDACION o CERRADA  
**Cuando** un coordinador o técnico intenta confirmar, rechazar o reabrirla en nombre del solicitante  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S04-10 — Estado incompatible

**Dado** que la incidencia no está PENDIENTE_VALIDACION para confirmar o rechazar, o no está CERRADA para reabrir  
**Cuando** el solicitante intenta una de esas acciones  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

### AC-S04-11 — Reapertura con motivo inválido

**Dado** que la incidencia está CERRADA  
**Cuando** el solicitante dueño intenta reabrirla con un motivo de menos de 10 o más de 300 caracteres  
**Entonces** el sistema rechaza la operación y conserva el estado y el historial.

## Tareas propuestas

- Permitir al solicitante dueño confirmar una solución.
- Permitir rechazar una solución y validar el motivo.
- Permitir reabrir una incidencia y validar el plazo con fecha UTC del servidor.
- Conservar soluciones y cierres anteriores en el historial.
- Rechazar operaciones de otros usuarios o en estados incompatibles.
- Crear pruebas para los criterios de aceptación.

## Revisión

- **Revisó:** pendiente
- **Fecha:** pendiente
- **Decisión:** pendiente
- **Observaciones:** pendiente
