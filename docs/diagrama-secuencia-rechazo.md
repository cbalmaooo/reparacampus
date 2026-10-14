# Secuencia: rechazar una solución

**Estado:** Diagrama de referencia alineado con el flujo de ruta → servicio → base de datos. Confirmar contra la implementación si cambian las rutas o el modelo.

```mermaid
sequenceDiagram
    actor Solicitante
    participant Interfaz
    participant Ruta as Ruta Flask
    participant Servicio as Servicio de negocio
    participant BD as Base de datos

    Solicitante->>Interfaz: Escribe motivo y pulsa Rechazar
    Interfaz->>Ruta: POST con código y motivo
    Ruta->>Servicio: rechazar_solucion(código, usuario autenticado, motivo, reloj)
    Servicio->>BD: Consultar incidencia, dueño, estado y técnico
    BD-->>Servicio: Devuelve los datos actuales
    Servicio->>Servicio: Validar identidad, propiedad, estado y motivo

    alt Datos válidos
        Servicio->>BD: Abrir transacción
        Servicio->>BD: Cambiar estado a EN_ATENCION
        Servicio->>BD: Guardar evento de rechazo con motivo
        Servicio->>BD: Confirmar transacción
        Note over Servicio,BD: Conserva técnico y soluciones anteriores
        Servicio-->>Ruta: Operación exitosa
        Ruta-->>Interfaz: Redirigir y mostrar mensaje
        Interfaz-->>Solicitante: Mostrar EN_ATENCION
    else Operación no válida
        Servicio-->>Ruta: Error de permiso, estado o validación
        Ruta-->>Interfaz: Rechazar la operación
        Note over Servicio,BD: No se persisten cambios ni evento
        Interfaz-->>Solicitante: Mostrar el error
    end
```

El diagrama representa el flujo esperado y no es evidencia por sí mismo. La prueba de integración debe verificar tanto el caso exitoso como la ausencia de efectos parciales en el rechazo.
