# Modelo de datos de ReparaCampus

**Estado:** Borrador, pendiente de revisión con las SPECS.

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
