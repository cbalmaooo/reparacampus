# Modelo de datos de ReparaCampus

**Estado:** Diagrama alineado con `database/schema.sql`; verificarlo nuevamente si cambia el esquema.

```mermaid
erDiagram
    USUARIO ||--o{ INCIDENCIA : reporta
    INCIDENCIA ||--o| ASIGNACION : tiene
    USUARIO ||--o{ ASIGNACION : coordina
    USUARIO ||--o{ ASIGNACION : recibe
    INCIDENCIA ||--o{ SOLUCION : conserva
    USUARIO ||--o{ SOLUCION : escribe
    INCIDENCIA ||--o{ CIERRE : conserva
    USUARIO ||--o{ CIERRE : confirma
    INCIDENCIA ||--o{ EVENTO : registra
    USUARIO ||--o{ EVENTO : realiza
    SOLUCION o|--o{ EVENTO : referencia

    USUARIO {
        int id PK
        string nombre_usuario UK
        string contrasena_hash
        string rol
        boolean activo
    }

    INCIDENCIA {
        int id PK
        string codigo UK
        int solicitante_id FK
        string ubicacion
        string categoria
        string descripcion
        string impacto
        boolean riesgo_personas
        string prioridad
        string estado
        datetime creada_en
    }

    ASIGNACION {
        int id PK
        int incidencia_id FK_UK
        int coordinador_id FK
        int tecnico_id FK
        datetime asignada_en
    }

    SOLUCION {
        int id PK
        int incidencia_id FK
        int tecnico_id FK
        string descripcion
        datetime creada_en
    }

    CIERRE {
        int id PK
        int incidencia_id FK
        int solicitante_id FK
        datetime cerrada_en
    }

    EVENTO {
        int id PK
        int incidencia_id FK
        int usuario_id FK
        string accion
        string estado_anterior
        string estado_nuevo
        string motivo
        int solucion_id FK
        datetime creado_en
    }
```

## Notas de integridad

- La tabla `cierres` conserva cada cierre confirmado. La fecha del último cierre se obtiene del cierre más reciente; no se almacena en `incidencias`.
- La tabla `asignaciones` admite una asignación por incidencia; la regla de negocio impide reasignar una incidencia después de salir de `REGISTRADA`.
- Las soluciones, cierres y eventos anteriores se conservan para mantener el historial.
- Las claves foráneas, restricciones y triggers concretos están definidos en `database/schema.sql`; ese archivo es la fuente de verdad del esquema.
- Este diagrama documenta la estructura; no sustituye las pruebas de restricciones de `tests/test_schema.py`.
