from app.utils.database import get_db


class SearchHistory:
    """Registra cada búsqueda de recomendaciones que hace un usuario
    (por título o por género), para poder mostrar un historial reciente
    en la interfaz. Funcionalidad agregada durante la reingeniería."""

    def __init__(self, id, search_type, query, results_count, searched_at):
        self.id = id
        self.search_type = search_type
        self.query = query
        self.results_count = results_count
        self.searched_at = searched_at

    @staticmethod
    def log_search(search_type, query, results_count):
        """Guarda una búsqueda. Si algo falla (ej. base de datos no
        disponible), no debe interrumpir la respuesta al usuario —
        el historial es una funcionalidad complementaria, no crítica."""
        if not query:
            return
        try:
            db = get_db()
            db.execute(
                "INSERT INTO search_history (search_type, query, results_count) VALUES (?, ?, ?)",
                (search_type, query, results_count),
            )
            db.commit()
        except Exception:  # noqa: BLE001
            pass

    @staticmethod
    def get_recent(limit=10):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, search_type, query, results_count, searched_at "
            "FROM search_history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [SearchHistory(*row) for row in cursor.fetchall()]

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.search_type,
            "query": self.query,
            "results_count": self.results_count,
            "searched_at": self.searched_at,
        }
