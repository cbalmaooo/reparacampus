# Modelo de datos de ReparaCampus

**Estado:** Aprobado por el equipo; falta registrar revisor, fecha y observaciones.

```mermaid
erDiagram
    USUARIO ||--o{ INCIDENCIA : reporta
    INCIDENCIA ||--o| ASIGNACION : tiene
    USUARIO ||--o{ ASIGNACION : coordina
    USUARIO ||--o{ ASIGNACION : recibe
    INCIDENCIA ||--o{ SOLUCION : conserva
    USUARIO ||--o{ SOLUCION : escribe
    INCIDENCIA ||--o{ EVENTO : registra
    USUARIO ||--o{ EVENTO : realiza

    USUARIO {
        int id PK
        string nombre_usuario
        string contrasena_hash
        string rol
        boolean activo
    }

    INCIDENCIA {
        int id PK
        string codigo
        int solicitante_id FK
        string ubicacion
        string categoria
        string descripcion
        string impacto
        boolean riesgo_personas
        string prioridad
        string estado
        datetime creada_en
        datetime ultimo_cierre_en
    }

    ASIGNACION {
        int id PK
        int incidencia_id FK
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

    EVENTO {
        int id PK
        int incidencia_id FK
        int usuario_id FK
        string accion
        string estado_anterior
        string estado_nuevo
        string motivo
        datetime creado_en
    }
```

## Reglas del modelo

- Cada incidencia pertenece a un solicitante.
- Una incidencia puede tener cero o una asignación; si se asigna, se conserva el coordinador y el técnico responsables.
- Una incidencia puede conservar varias soluciones. Una solución rechazada no se reemplaza ni se borra.
- Cada acción exitosa genera un evento con el actor, la acción, la fecha, el estado anterior y el nuevo; los rechazos y reaperturas guardan también el motivo.
- `ultimo_cierre_en` guarda la fecha del cierre más reciente y sirve para calcular el plazo de reapertura de 48 horas. Al reabrir no se borra ese valor; un cierre posterior lo actualiza.
- Los cierres anteriores permanecen en `EVENTO`, incluso después de una reapertura.
- Las fechas se guardan en UTC. Las restricciones de claves foráneas, valores permitidos e inmutabilidad se implementan en SQLite según `database/schema.sql`.

## Registro de revisión

- **Revisor:** por registrar
- **Fecha:** por registrar
- **Decisión:** aprobado por el equipo
- **Observaciones:** por registrar
