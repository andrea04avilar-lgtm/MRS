import sqlite3

from flask import g, current_app


def get_db():
    """Devuelve una conexion SQLite reutilizable dentro del contexto de la request
    actual. Lee la ruta de la base de datos desde la configuracion de la app
    (current_app.config), NO desde una constante global, para que sea testeable
    con bases de datos temporales."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
