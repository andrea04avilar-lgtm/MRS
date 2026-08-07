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

    # Insert sample data
    movies = [
        (1, "The Shawshank Redemption", "Drama", 9.3),
        (2, "The Godfather", "Crime,Drama", 9.2),
        (3, "The Dark Knight", "Action,Crime,Drama", 9.0),
        (4, "Pulp Fiction", "Crime,Drama", 8.9),
        (5, "Forrest Gump", "Drama,Romance", 8.8)
    ]
    c.executemany('INSERT OR REPLACE INTO movies VALUES (?,?,?,?)', movies)

    ratings = [
        (1, 1, 1, 5.0),
        (2, 1, 2, 4.5),
        (3, 1, 3, 4.0),
        (4, 2, 1, 4.0),
        (5, 2, 4, 4.5)
    ]
    c.executemany('INSERT OR REPLACE INTO ratings VALUES (?,?,?,?)', ratings)

    conn.commit()
    conn.close()

    print(f"Database created successfully at {Config.DATABASE_PATH}")

if __name__ == "__main__":
    create_database()
