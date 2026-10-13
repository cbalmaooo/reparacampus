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
    ubicacion TEXT NOT NULL CHECK (length(trim(ubicacion)) > 0),
    categoria TEXT NOT NULL CHECK (length(trim(categoria)) > 0),
    descripcion TEXT NOT NULL
        CHECK (length(trim(descripcion)) BETWEEN 20 AND 500),
    impacto TEXT NOT NULL CHECK (impacto IN ('BAJO', 'ALTO')),
    riesgo_personas INTEGER NOT NULL CHECK (riesgo_personas IN (0, 1)),
    prioridad TEXT NOT NULL CHECK (prioridad IN ('NORMAL', 'ALTA', 'CRITICA')),
    estado TEXT NOT NULL DEFAULT 'REGISTRADA'
        CHECK (estado IN (
            'REGISTRADA',
            'ASIGNADA',
            'EN_ATENCION',
            'PENDIENTE_VALIDACION',
            'CERRADA'
        )),
    creada_en TEXT NOT NULL,
    ultimo_cierre_en TEXT,
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id)
);

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

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    accion TEXT NOT NULL,
    estado_anterior TEXT,
    estado_nuevo TEXT,
    motivo TEXT,
    creado_en TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Las soluciones anteriores se conservan; no se editan ni se borran.
CREATE TRIGGER IF NOT EXISTS soluciones_sin_edicion
BEFORE UPDATE ON soluciones
BEGIN
    SELECT RAISE(ABORT, 'Las soluciones anteriores no se pueden editar');
END;

CREATE TRIGGER IF NOT EXISTS soluciones_sin_borrado
BEFORE DELETE ON soluciones
BEGIN
    SELECT RAISE(ABORT, 'Las soluciones anteriores no se pueden borrar');
END;

-- El historial es inmutable.
CREATE TRIGGER IF NOT EXISTS eventos_sin_edicion
BEFORE UPDATE ON eventos
BEGIN
    SELECT RAISE(ABORT, 'Los eventos del historial no se pueden editar');
END;

CREATE TRIGGER IF NOT EXISTS eventos_sin_borrado
BEFORE DELETE ON eventos
BEGIN
    SELECT RAISE(ABORT, 'Los eventos del historial no se pueden borrar');
END;
