"""Pruebas del esquema contra SQLite real: restricciones e inmutabilidad."""
import sqlite3

import pytest

AHORA = "2026-10-13T12:00:00+00:00"


def _id(conn, usuario):
    return conn.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (usuario,)).fetchone()["id"]


def _incidencia(conn, codigo="INC-0001"):
    conn.execute(
        "INSERT INTO incidencias (codigo, solicitante_id, ubicacion, categoria, descripcion,"
        " impacto, riesgo_personas, prioridad, creada_en)"
        " VALUES (?, ?, 'LAB-01', 'ELECTRICIDAD', 'El tomacorriente hace chispas', 'ALTO', 1, 'CRITICA', ?)",
        (codigo, _id(conn, "solicitante1"), AHORA),
    )
    return conn.execute("SELECT id FROM incidencias WHERE codigo = ?", (codigo,)).fetchone()["id"]


def test_seed_cinco_cuentas_con_hash(conn):  # AC-S05-02 (formato)
    filas = conn.execute("SELECT rol, contrasena_hash, activo FROM usuarios").fetchall()
    roles = sorted(f["rol"] for f in filas)
    assert roles == ["COORDINADOR", "SOLICITANTE", "SOLICITANTE", "TECNICO", "TECNICO"]
    assert all(f["contrasena_hash"].startswith("pbkdf2:sha256:") and f["activo"] == 1 for f in filas)


def test_ubicacion_no_permitida(conn):  # AC-S01-03 (defensa en base)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO incidencias (codigo, solicitante_id, ubicacion, categoria, descripcion,"
            " impacto, riesgo_personas, prioridad, creada_en)"
            " VALUES ('INC-0009', 1, 'LAB-99', 'TIC', 'Descripcion suficientemente larga', 'BAJO', 0, 'NORMAL', ?)",
            (AHORA,),
        )


def test_reasignacion_bloqueada_por_la_base(conn):  # AC-S02-11 (defensa en base)
    inc = _incidencia(conn)
    coord, t1, t2 = _id(conn, "coordinador1"), _id(conn, "tecnico1"), _id(conn, "tecnico2")
    conn.execute("INSERT INTO asignaciones (incidencia_id, coordinador_id, tecnico_id, asignada_en)"
                 " VALUES (?, ?, ?, ?)", (inc, coord, t1, AHORA))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO asignaciones (incidencia_id, coordinador_id, tecnico_id, asignada_en)"
                     " VALUES (?, ?, ?, ?)", (inc, coord, t2, AHORA))
    with pytest.raises(sqlite3.IntegrityError, match="no se pueden editar"):
        conn.execute("UPDATE asignaciones SET tecnico_id = ? WHERE incidencia_id = ?", (t2, inc))


@pytest.mark.parametrize("tabla", ["eventos", "cierres"])
def test_historial_y_cierres_inmutables(conn, tabla):  # AC-S05-12, AC-S04-08
    inc = _incidencia(conn)
    sol = _id(conn, "solicitante1")
    if tabla == "eventos":
        conn.execute("INSERT INTO eventos (incidencia_id, usuario_id, accion, estado_nuevo, creado_en)"
                     " VALUES (?, ?, 'REGISTRAR', 'REGISTRADA', ?)", (inc, sol, AHORA))
    else:
        conn.execute("INSERT INTO cierres (incidencia_id, solicitante_id, cerrada_en)"
                     " VALUES (?, ?, ?)", (inc, sol, AHORA))
    with pytest.raises(sqlite3.IntegrityError, match="no se pueden editar"):
        conn.execute(f"UPDATE {tabla} SET incidencia_id = incidencia_id")
    with pytest.raises(sqlite3.IntegrityError, match="no se pueden borrar"):
        conn.execute(f"DELETE FROM {tabla}")
    assert conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] == 1


def test_datos_del_reporte_inmutables_pero_estado_cambia(conn):  # S01 exclusiones
    inc = _incidencia(conn)
    with pytest.raises(sqlite3.IntegrityError, match="no se pueden editar"):
        conn.execute("UPDATE incidencias SET descripcion = 'Otra descripcion cualquiera' WHERE id = ?", (inc,))
    conn.execute("UPDATE incidencias SET estado = 'ASIGNADA' WHERE id = ?", (inc,))
    assert conn.execute("SELECT estado FROM incidencias WHERE id = ?", (inc,)).fetchone()["estado"] == "ASIGNADA"


def test_accion_de_evento_no_permitida(conn):  # AC-S05-10 (acciones cerradas)
    inc = _incidencia(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO eventos (incidencia_id, usuario_id, accion, estado_nuevo, creado_en)"
                     " VALUES (?, 1, 'CERRAR_AUTOMATICO', 'CERRADA', ?)", (inc, AHORA))
