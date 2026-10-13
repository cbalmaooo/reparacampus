"""Acceso a SQLite.

La conexión trabaja en modo autocommit (isolation_level=None) y toda escritura
pasa por transaccion(): estado e historial se guardan juntos o no se guarda nada.
"""
import os
import sqlite3
from contextlib import contextmanager

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"], isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@contextmanager
def transaccion():
    """Ejecuta un bloque de escrituras de forma atómica."""
    conn = get_db()
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def ruta_sql(nombre):
    return os.path.join(os.path.dirname(current_app.root_path), "database", nombre)


def ejecutar_sql(nombre):
    with open(ruta_sql(nombre), encoding="utf-8") as archivo:
        get_db().executescript(archivo.read())


def init_db(con_seed=False):
    """Crea las tablas; con_seed carga las cinco cuentas ficticias."""
    ejecutar_sql("schema.sql")
    if con_seed:
        ejecutar_sql("seed.sql")


@click.command("init-db")
@click.option("--seed", is_flag=True, help="Carga las cuentas ficticias de database/seed.sql.")
def init_db_command(seed):
    """Crea las tablas a partir de database/schema.sql."""
    init_db(con_seed=seed)
    click.echo("Base de datos inicializada" + (" con seed." if seed else "."))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
