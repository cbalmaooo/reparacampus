"""AC-S05-02: las contraseñas del seed están en hash y verifican con su contraseña ficticia."""
import pytest
from werkzeug.security import check_password_hash

CUENTAS = {
    "solicitante1": ("Solicitante1*2026", "SOLICITANTE"),
    "solicitante2": ("Solicitante2*2026", "SOLICITANTE"),
    "coordinador1": ("Coordinador1*2026", "COORDINADOR"),
    "tecnico1": ("Tecnico1*2026", "TECNICO"),
    "tecnico2": ("Tecnico2*2026", "TECNICO"),
}


@pytest.mark.parametrize("usuario", sorted(CUENTAS))
def test_contrasena_en_hash_y_verificable(conn, usuario):
    contrasena, rol = CUENTAS[usuario]
    fila = conn.execute(
        "SELECT contrasena_hash, rol, activo FROM usuarios WHERE nombre_usuario = ?", (usuario,)
    ).fetchone()
    assert fila is not None
    assert fila["contrasena_hash"] != contrasena          # no está en texto plano
    assert check_password_hash(fila["contrasena_hash"], contrasena)
    assert not check_password_hash(fila["contrasena_hash"], "incorrecta123")
    assert fila["rol"] == rol and fila["activo"] == 1
