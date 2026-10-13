# Diagrama de estados de una incidencia

**Estado:** Borrador, pendiente de revisión con las SPECS.

```mermaid
stateDiagram-v2
    [*] --> REGISTRADA: solicitante registra

    REGISTRADA --> ASIGNADA: coordinador asigna técnico activo
    ASIGNADA --> EN_ATENCION: técnico asignado inicia atención
    EN_ATENCION --> PENDIENTE_VALIDACION: técnico registra solución

    PENDIENTE_VALIDACION --> CERRADA: solicitante dueño confirma
    PENDIENTE_VALIDACION --> EN_ATENCION: solicitante dueño rechaza
    CERRADA --> EN_ATENCION: solicitante dueño reabre dentro de 48 horas

    note right of PENDIENTE_VALIDACION
        Al rechazar, se conserva
        la solución anterior.
    end note

    note right of EN_ATENCION
        Rechazo y reapertura conservan
        el mismo técnico.
    end note
```

## Regla para operaciones rechazadas

Si una acción no tiene permiso, el estado no corresponde o los datos no son válidos, la incidencia conserva su estado y no se agrega un evento al historial.
