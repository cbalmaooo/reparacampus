-- ReparaCampus · esquema v2 (alineado con S01–S05 v1.0)
-- Cambios frente a v1: tabla cierres (S04), CHECK de valores cerrados (S01),
-- acciones y estados de eventos restringidos (S05), referencia a solución en eventos (S03),
-- triggers de inmutabilidad para asignaciones y cierres; se retira ultimo_cierre_en.
-- Fechas: texto ISO 8601 en UTC, formato 'YYYY-MM-DDTHH:MM:SS+00:00'.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL
        CHECK (rol IN ('SOLICITANTE', 'COORDINADOR', 'TECNICO')),
    activo INTEGER NOT NULL DEFAULT 1
        CHECK (activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS incidencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    solicitante_id INTEGER NOT NULL,
    ubicacion TEXT NOT NULL
        CHECK (ubicacion IN ('LAB-01', 'AULA-201', 'BIB-01')),
    categoria TEXT NOT NULL
        CHECK (categoria IN ('ELECTRICIDAD', 'HIDRAULICA', 'MOBILIARIO', 'TIC')),
    descripcion TEXT NOT NULL
        CHECK (length(trim(descripcion)) BETWEEN 20 AND 500),
    impacto TEXT NOT NULL CHECK (impacto IN ('BAJO', 'ALTO')),
    riesgo_personas INTEGER NOT NULL CHECK (riesgo_personas IN (0, 1)),
    prioridad TEXT NOT NULL CHECK (prioridad IN ('NORMAL', 'ALTA', 'CRITICA')),
    estado TEXT NOT NULL DEFAULT 'REGISTRADA'
        CHECK (estado IN ('REGISTRADA', 'ASIGNADA', 'EN_ATENCION',
                          'PENDIENTE_VALIDACION', 'CERRADA')),
    creada_en TEXT NOT NULL,
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id)
);

-- Una sola asignación por incidencia: la base impide la reasignación (S02).
CREATE TABLE IF NOT EXISTS asignaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL UNIQUE,
    coordinador_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    asignada_en TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (coordinador_id) REFERENCES usuarios(id),
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
);

-- Una incidencia puede tener varias soluciones (S03, rechazo y reapertura).
CREATE TABLE IF NOT EXISTS soluciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL
        CHECK (length(trim(descripcion)) BETWEEN 20 AND 800),
    creada_en TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
);

-- Cada confirmación crea un cierre; el último cierre es MAX(cerrada_en) (S04).
CREATE TABLE IF NOT EXISTS cierres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL,
    solicitante_id INTEGER NOT NULL,
    cerrada_en TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    accion TEXT NOT NULL
        CHECK (accion IN ('REGISTRAR', 'ASIGNAR', 'INICIAR_ATENCION',
                          'REGISTRAR_SOLUCION', 'RECHAZAR', 'CONFIRMAR', 'REABRIR')),
    estado_anterior TEXT
        CHECK (estado_anterior IS NULL OR estado_anterior IN
               ('REGISTRADA', 'ASIGNADA', 'EN_ATENCION', 'PENDIENTE_VALIDACION', 'CERRADA')),
    estado_nuevo TEXT NOT NULL
        CHECK (estado_nuevo IN
               ('REGISTRADA', 'ASIGNADA', 'EN_ATENCION', 'PENDIENTE_VALIDACION', 'CERRADA')),
    motivo TEXT
        CHECK (motivo IS NULL OR length(trim(motivo)) BETWEEN 10 AND 300),
    solucion_id INTEGER,
    creado_en TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (solucion_id) REFERENCES soluciones(id)
);

CREATE INDEX IF NOT EXISTS idx_incidencias_solicitante ON incidencias(solicitante_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_estado_prioridad ON incidencias(estado, prioridad);
CREATE INDEX IF NOT EXISTS idx_eventos_incidencia ON eventos(incidencia_id, id);
CREATE INDEX IF NOT EXISTS idx_cierres_incidencia ON cierres(incidencia_id, cerrada_en);

-- Inmutabilidad (S02, S03, S04, S05): ni la aplicación ni un SQL directo pueden
-- editar o borrar asignaciones, soluciones, cierres ni eventos.
CREATE TRIGGER IF NOT EXISTS asignaciones_sin_edicion BEFORE UPDATE ON asignaciones
BEGIN SELECT RAISE(ABORT, 'Las asignaciones no se pueden editar'); END;
CREATE TRIGGER IF NOT EXISTS asignaciones_sin_borrado BEFORE DELETE ON asignaciones
BEGIN SELECT RAISE(ABORT, 'Las asignaciones no se pueden borrar'); END;

CREATE TRIGGER IF NOT EXISTS soluciones_sin_edicion BEFORE UPDATE ON soluciones
BEGIN SELECT RAISE(ABORT, 'Las soluciones anteriores no se pueden editar'); END;
CREATE TRIGGER IF NOT EXISTS soluciones_sin_borrado BEFORE DELETE ON soluciones
BEGIN SELECT RAISE(ABORT, 'Las soluciones anteriores no se pueden borrar'); END;

CREATE TRIGGER IF NOT EXISTS cierres_sin_edicion BEFORE UPDATE ON cierres
BEGIN SELECT RAISE(ABORT, 'Los cierres no se pueden editar'); END;
CREATE TRIGGER IF NOT EXISTS cierres_sin_borrado BEFORE DELETE ON cierres
BEGIN SELECT RAISE(ABORT, 'Los cierres no se pueden borrar'); END;

CREATE TRIGGER IF NOT EXISTS eventos_sin_edicion BEFORE UPDATE ON eventos
BEGIN SELECT RAISE(ABORT, 'Los eventos del historial no se pueden editar'); END;
CREATE TRIGGER IF NOT EXISTS eventos_sin_borrado BEFORE DELETE ON eventos
BEGIN SELECT RAISE(ABORT, 'Los eventos del historial no se pueden borrar'); END;

-- Los datos del reporte no se editan después de registrados (S01);
-- solo el estado puede cambiar, y lo hacen los servicios de S02–S04.
CREATE TRIGGER IF NOT EXISTS incidencias_datos_inmutables
BEFORE UPDATE OF codigo, solicitante_id, ubicacion, categoria, descripcion,
                 impacto, riesgo_personas, prioridad, creada_en ON incidencias
BEGIN SELECT RAISE(ABORT, 'Los datos del reporte no se pueden editar'); END;

CREATE TRIGGER IF NOT EXISTS incidencias_sin_borrado BEFORE DELETE ON incidencias
BEGIN SELECT RAISE(ABORT, 'Las incidencias no se pueden borrar'); END;
