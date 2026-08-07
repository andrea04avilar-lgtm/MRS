import os

# Carga variables de entorno desde un archivo .env si existe (no falla si no está instalado python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuración base. Todos los valores sensibles vienen de variables de entorno,
    nunca hardcodeados en el código fuente (requisito de la Fase 1: centralización de
    variables de entorno)."""

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    # Base de datos
    DATABASE_PATH = os.environ.get(
        'DATABASE_PATH',
        os.path.join(BASE_DIR, 'data', 'movies.db')
    )

    # Dataset (Kaggle "The Movies Dataset") — opcional. Si no está presente,
    # la app degrada de forma segura al motor basado en la base de datos SQLite.
    MOVIES_METADATA_PATH = os.environ.get(
        'MOVIES_METADATA_PATH',
        os.path.join(BASE_DIR, 'data', 'tmdb_5000_movies.csv')
    )
    CREDITS_PATH = os.environ.get(
        'CREDITS_PATH',
        os.path.join(BASE_DIR, 'data', 'tmdb_5000_credits.csv')
    )

    # TMDB API
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    TMDB_BASE_URL = os.environ.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')

    # Flag para habilitar/deshabilitar el motor de recomendación basado en contenido
    ENABLE_CONTENT_BASED = os.environ.get('ENABLE_CONTENT_BASED', 'True').lower() == 'true'


class TestingConfig(Config):
    """Configuración usada por la suite de Pytest: base de datos en memoria y
    motor de contenido deshabilitado para que las pruebas sean rápidas y no
    dependan del dataset de Kaggle."""

    TESTING = True
    DATABASE_PATH = os.environ.get('TEST_DATABASE_PATH', ':memory:')
    ENABLE_CONTENT_BASED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_by_name = {
    'development': Config,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
