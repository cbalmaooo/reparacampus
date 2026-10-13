# Modelo de datos de ReparaCampus

**Versión:** 2.0  
**Fuente:** `database/schema.sql` v2  
**Diagrama:** [datos.png](diagramas/datos.png)  
**Estado:** versión propuesta para revisión del equipo en el pull request #20.

```mermaid
erDiagram
    USUARIO ||--o{ INCIDENCIA : reporta
    USUARIO ||--o{ ASIGNACION : coordina
    USUARIO ||--o{ ASIGNACION : recibe
    INCIDENCIA ||--o| ASIGNACION : tiene
    USUARIO ||--o{ SOLUCION : registra
    INCIDENCIA ||--o{ SOLUCION : conserva
    USUARIO ||--o{ CIERRE : confirma
    INCIDENCIA ||--o{ CIERRE : conserva
    USUARIO ||--o{ EVENTO : ejecuta
    INCIDENCIA ||--o{ EVENTO : conserva
    SOLUCION |o--o{ EVENTO : referencia

    USUARIO {
        int id PK
        string nombre_usuario UK
        string contrasena_hash
        string rol "SOLICITANTE | COORDINADOR | TECNICO"
        int activo "0 | 1"
    }

    INCIDENCIA {
        int id PK
        string codigo UK "INC-0001"
        int solicitante_id FK
        string ubicacion "LAB-01 | AULA-201 | BIB-01"
        string categoria "ELECTRICIDAD | HIDRAULICA | MOBILIARIO | TIC"
        string descripcion "20 a 500"
        string impacto "BAJO | ALTO"
        int riesgo_personas "0 | 1"
        string prioridad "NORMAL | ALTA | CRITICA"
        string estado "REGISTRADA | ASIGNADA | EN_ATENCION | PENDIENTE_VALIDACION | CERRADA"
        string creada_en "ISO 8601 UTC"
    }

    ASIGNACION {
        int id PK
        int incidencia_id FK,UK
        int coordinador_id FK
        int tecnico_id FK
        string asignada_en "ISO 8601 UTC"
    }

    SOLUCION {
        int id PK
        int incidencia_id FK
        int tecnico_id FK
        string descripcion "20 a 800"
        string creada_en "ISO 8601 UTC"
    }

    CIERRE {
        int id PK
        int incidencia_id FK
        int solicitante_id FK
        string cerrada_en "ISO 8601 UTC"
    }

    EVENTO {
        int id PK
        int incidencia_id FK
        int usuario_id FK
        string accion "REGISTRAR | ASIGNAR | INICIAR_ATENCION | REGISTRAR_SOLUCION | RECHAZAR | CONFIRMAR | REABRIR"
        string estado_anterior "opcional"
        string estado_nuevo
        string motivo "10 a 300, opcional"
        int solucion_id FK "opcional"
        string creado_en "ISO 8601 UTC"
    }
```

## Reglas y restricciones

- Cada incidencia tiene una sola asignación: `asignaciones.incidencia_id` es `UNIQUE`; no se permite reasignar.
- Las soluciones se conservan como registros separados, incluso cuando una es rechazada y se registra otra.
- Cada confirmación agrega un registro a `cierres`; la reapertura se calcula a partir del cierre más reciente, sin borrar cierres anteriores.
- Cada creación o transición exitosa registra un evento con actor, fecha UTC, acción y estados; el motivo y la solución se enlazan cuando corresponden.
- Las restricciones `CHECK`, claves foráneas y triggers del esquema protegen valores permitidos e inmutabilidad del historial y los datos originales del reporte.
- El esquema almacena fechas como texto ISO 8601 en UTC. La prioridad solo admite `NORMAL`, `ALTA` o `CRITICA`; la calcula la lógica de negocio.

La tabla `CIERRE` reemplaza el campo `ultimo_cierre_en` de la versión 1, que no conservaba el historial de varios cierres.