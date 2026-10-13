PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO usuarios
    (nombre_usuario, contrasena_hash, rol, activo)
VALUES
    ('solicitante1', 'pbkdf2:sha256:600000$solicita01$efd038e985b424180ccd86fb731f8853ce9ddbcfb8bb756220309379a0ac7be8', 'SOLICITANTE', 1),
    ('solicitante2', 'pbkdf2:sha256:600000$solicita02$2ea2e28edcda3351b136e3036817daaebd9419fbbde8a9c9d5cd0f2daa9732af', 'SOLICITANTE', 1),
    ('coordinador1', 'pbkdf2:sha256:600000$coordina01$566f8e0c80227295b5204d0f0d07ded63f422b60635c7c3e4d2439e986120ec9', 'COORDINADOR', 1),
    ('tecnico1', 'pbkdf2:sha256:600000$tecnico001$9c756644e5814461f056c5c01e211c4ce2382813811dabaaa0c56fb1d830d849', 'TECNICO', 1),
    ('tecnico2', 'pbkdf2:sha256:600000$tecnico002$9e4f0a49e06738dcb7c6404411c10a22a39bded0ae34c11f5ce0fd200cc37312', 'TECNICO', 1);
