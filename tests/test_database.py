from app.utils.database import get_db, close_db


class TestDatabaseUtils:

    def test_get_db_returns_connection(self, app):
        with app.app_context():
            db = get_db()
            assert db is not None

    def test_get_db_reuses_connection_within_context(self, app):
        with app.app_context():
            db1 = get_db()
            db2 = get_db()
            assert db1 is db2

    def test_close_db_removes_connection_from_context(self, app):
        with app.app_context():
            get_db()
            close_db()
            # Tras cerrar, una nueva llamada debe abrir una conexión nueva sin error
            new_db = get_db()
            assert new_db is not None
