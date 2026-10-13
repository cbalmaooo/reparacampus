"""Registro de eventos del historial (RF05).

Se llama siempre dentro de la misma transacción que el cambio de estado, para que
estado e historial se guarden juntos o no se guarde nada.
"""


def registrar_evento(conn, incidencia_id, usuario_id, accion, estado_anterior, estado_nuevo,
                     creado_en, motivo=None, solucion_id=None):
    conn.execute(
        "INSERT INTO eventos (incidencia_id, usuario_id, accion, estado_anterior, estado_nuevo,"
        " motivo, solucion_id, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (incidencia_id, usuario_id, accion, estado_anterior, estado_nuevo, motivo, solucion_id, creado_en),
    )
