# Modelo de datos de ReparaCampus

**Versión:** 2.0 · **Fuente:** `database/schema.sql` v2 · **Diagrama:** `docs/diagramas/datos.png`

```mermaid
erDiagram
    USUARIO ||--o{ INCIDENCIA : registra
    INCIDENCIA ||--o| ASIGNACION : tiene
    USUARIO ||--o{ ASIGNACION : "coordina / recibe"
    INCIDENCIA ||--o{ SOLUCION : conserva
    INCIDENCIA ||--o{ CIERRE : conserva
    INCIDENCIA ||--o{ EVENTO : registra
    USUARIO ||--o{ EVENTO : realiza
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
        string prioridad "CRITICA | ALTA | NORMAL"
        string estado
        string creada_en "UTC"
    }
    ASIGNACION {
        int id PK
        int incidencia_id FK,UK
        int coordinador_id FK
        int tecnico_id FK
        string asignada_en
    }
    SOLUCION {
        int id PK
        int incidencia_id FK
        int tecnico_id FK
        string descripcion "20 a 800"
        string creada_en
    }
    CIERRE {
        int id PK
        int incidencia_id FK
        int solicitante_id FK
        string cerrada_en
    }
    EVENTO {
        int id PK
        int incidencia_id FK
        int usuario_id FK
        string accion "7 acciones"
        string estado_anterior
        string estado_nuevo
        string motivo "10 a 300, opcional"
        int solucion_id FK "opcional"
        string creado_en
    }
```

## Reglas del modelo

- Cada incidencia pertenece a un solicitante y tiene como máximo una asignación (`UNIQUE` en `incidencia_id`): no hay reasignación.
- Cada solución y cada confirmación crean un registro nuevo. El último cierre es `MAX(cerrada_en)` y sirve para el plazo de reapertura de 48 horas.
- Cada creación y transición exitosa genera un evento con autor, fecha UTC, estados, acción y, si aplica, motivo o solución.
- Triggers impiden editar o borrar asignaciones, soluciones, cierres y eventos, y modificar los datos del reporte; solo cambia el estado.
- Cambio respecto a la versión 1: la columna `ultimo_cierre_en` se reemplazó por la tabla `cierres`, porque se sobrescribía y no permitía conservar todos los cierres (S04 v1.0, PR #12).

## Registro de revisión

- Revisor: [nombre de quien revise el PR]
- Fecha: [fecha]
- Decisión: [Aprobado | Requiere cambios]
