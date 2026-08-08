import sqlite3
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

def create_database():
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    # Create tables (vote_average agregado: el modelo Movie y las rutas lo requieren)
    c.execute('''CREATE TABLE IF NOT EXISTS movies
                 (id INTEGER PRIMARY KEY, title TEXT NOT NULL, genres TEXT NOT NULL,
                  vote_average REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                 (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, 
                  movie_id INTEGER NOT NULL, rating FLOAT NOT NULL,
                  FOREIGN KEY (movie_id) REFERENCES movies (id))''')
    # Historial de busqueda (funcionalidad agregada durante la reingenieria)
    c.execute('''CREATE TABLE IF NOT EXISTS search_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  search_type TEXT NOT NULL,
                  query TEXT NOT NULL,
                  results_count INTEGER DEFAULT 0,
                  searched_at TEXT NOT NULL DEFAULT (datetime('now')))''')

    # Insert sample data
    # IMPORTANTE: los ids usados aqui son los IDs REALES de TMDB para estas
    # peliculas (no numeros arbitrarios 1-5). Esto es necesario porque
    # process_movie_from_db() usa movie.id para pedirle el poster/sinopsis
    # a la API de TMDB — si el id no coincide con el id real de TMDB, la
    # app pide datos de una pelicula distinta (o de ninguna) y el poster
    # sale en blanco. Bug encontrado y corregido durante la reingenieria.
    movies = [
        (278, "The Shawshank Redemption", "Drama", 9.3),
        (238, "The Godfather", "Crime,Drama", 9.2),
        (155, "The Dark Knight", "Action,Crime,Drama", 9.0),
        (680, "Pulp Fiction", "Crime,Drama", 8.9),
        (13, "Forrest Gump", "Drama,Romance", 8.8)
    ]
    c.executemany('INSERT OR REPLACE INTO movies VALUES (?,?,?,?)', movies)

    ratings = [
        (1, 1, 278, 5.0),
        (2, 1, 238, 4.5),
        (3, 1, 155, 4.0),
        (4, 2, 278, 4.0),
        (5, 2, 680, 4.5)
    ]
    c.executemany('INSERT OR REPLACE INTO ratings VALUES (?,?,?,?)', ratings)

    conn.commit()
    conn.close()

    print(f"Database created successfully at {Config.DATABASE_PATH}")

if __name__ == "__main__":
    create_database()
