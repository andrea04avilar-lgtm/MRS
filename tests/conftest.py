import os
import sqlite3
import tempfile

import pytest

from app import create_app
from config.config import TestingConfig


@pytest.fixture()
def app():
    """Crea una instancia de la aplicación Flask configurada para pruebas,
    con una base de datos SQLite temporal (no la de producción)."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    class _TestConfig(TestingConfig):
        DATABASE_PATH = db_path

    flask_app = create_app(_TestConfig)
    flask_app.config.update({"TESTING": True})

    with flask_app.app_context():
        _seed_test_database(db_path)

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed_test_database(db_path):
    """Crea el esquema y datos mínimos para que las pruebas sean deterministas."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS movies
           (id INTEGER PRIMARY KEY, title TEXT NOT NULL, genres TEXT NOT NULL,
            vote_average REAL DEFAULT 0)"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS search_history
           (id INTEGER PRIMARY KEY AUTOINCREMENT, search_type TEXT NOT NULL,
            query TEXT NOT NULL, results_count INTEGER DEFAULT 0,
            searched_at TEXT NOT NULL DEFAULT (datetime('now')))"""
    )
    cur.executemany(
        "INSERT OR REPLACE INTO movies (id, title, genres, vote_average) VALUES (?, ?, ?, ?)",
        [
            (1, "The Shawshank Redemption", "Drama", 9.3),
            (2, "The Godfather", "Crime,Drama", 9.2),
            (3, "The Dark Knight", "Action,Crime,Drama", 9.0),
            (4, "Pulp Fiction", "Crime,Drama", 8.9),
            (5, "Forrest Gump", "Drama,Romance", 8.8),
        ],
    )
    conn.commit()
    conn.close()
