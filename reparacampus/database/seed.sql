-- ReparaCampus · seed v2: cinco cuentas ficticias (enunciado: dos solicitantes,
-- un coordinador y dos técnicos activos). Hashes generados con
-- werkzeug.security.generate_password_hash(method="pbkdf2:sha256:600000").
-- Contraseñas ficticias, solo para el prototipo (documentadas también en el README):
--   usuario       contraseña         rol
--   solicitante1  Solicitante1*2026  SOLICITANTE
--   solicitante2  Solicitante2*2026  SOLICITANTE
--   coordinador1  Coordinador1*2026  COORDINADOR
--   tecnico1      Tecnico1*2026      TECNICO
--   tecnico2      Tecnico2*2026      TECNICO
PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO usuarios
    (nombre_usuario, contrasena_hash, rol, activo)
VALUES
    ('solicitante1', 'pbkdf2:sha256:600000$KkJHAVC3IwDqwsmM$b06662f4c1393319dfdb8e998e61ec33a9aefc7aaf1074afc849313eb81a01b7', 'SOLICITANTE', 1),
    ('solicitante2', 'pbkdf2:sha256:600000$oBFnNY4XA0OOWomL$6870d22e2858f68ff7236e3c5411af6df6a3c858cf66e8765615cb59ab663d52', 'SOLICITANTE', 1),
    ('coordinador1', 'pbkdf2:sha256:600000$3lN7TRFzXmL7g0AE$33c59d5b9b316af00bedef500f093915e3fe4dc46c214c2e368ee1955b7b809e', 'COORDINADOR', 1),
    ('tecnico1', 'pbkdf2:sha256:600000$2jFWEoCglSpMQ221$d40fb35ddf432f7a05b87606796d3c68170e467f124ea2c31fd0d852a36a6f87', 'TECNICO', 1),
    ('tecnico2', 'pbkdf2:sha256:600000$dRzkA4arbWL5GrcD$98ad9a16f0db732042c83caa8332193db879cb7d97b676a97618108476e8cc89', 'TECNICO', 1);
