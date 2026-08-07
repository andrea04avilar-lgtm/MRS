import logging
from app.data_processing.demographic_filtering import get_top_movies
from app.data_processing.content_based_filtering import prepare_content_based_data, get_recommendations as get_content_recommendations
from app.models.movie import Movie
from config.config import Config

logging.basicConfig(level=logging.INFO)

# Carga perezosa y a prueba de fallos del dataset de Kaggle (The Movies Dataset).
# Si el CSV no está presente (por ejemplo en CI, tests, o un deploy ligero sin el
# dataset descargado), la app NO debe crasharse: simplemente deshabilita el motor
# de recomendación basado en contenido y sigue funcionando con el motor basado en
# la base de datos SQLite.
df, cosine_sim, indices = None, None, None

if Config.ENABLE_CONTENT_BASED:
    try:
        df, cosine_sim, indices = prepare_content_based_data()
        logging.info("Motor de recomendación basado en contenido cargado correctamente")
    except FileNotFoundError as exc:
        logging.warning(
            "Dataset de recomendación basado en contenido no encontrado (%s). "
            "La app continuará usando únicamente el motor basado en base de datos.",
            exc,
        )
    except Exception as exc:  # noqa: BLE001
        logging.warning("No se pudo inicializar el motor basado en contenido: %s", exc)
else:
    logging.info("Motor de recomendación basado en contenido deshabilitado por configuración")

def get_recommendations(genre=None, n=10, start_year=None, end_year=None, min_rating=0):
    """Devuelve las mejores películas. Usa el dataset de Kaggle si está disponible;
    si no, degrada de forma segura a la base de datos SQLite local (demo)."""
    recommendations = None

    if df is not None:
        try:
            top_movies = get_top_movies(n * 2)
            if not top_movies.empty:
                recommendations = [
                    Movie(
                        id=row['id'],
                        title=row['title'],
                        genres=row.get('genres', ''),
                        rating=row.get('vote_average', 0)
                    )
                    for _, row in top_movies.iterrows()
                ]
        except FileNotFoundError:
            logging.warning("Dataset no encontrado al pedir recomendaciones; usando base de datos local")

    if recommendations is None:
        logging.info("Usando motor basado en base de datos (fallback)")
        db_movies = Movie.get_all()
        recommendations = [m for m in db_movies if m.rating is not None]

    logging.info(f"Created {len(recommendations)} movie objects")

    if genre:
        recommendations = [movie for movie in recommendations if genre.lower() in movie.genres.lower()]
        logging.info(f"{len(recommendations)} movies after genre filter")

    if min_rating:
        recommendations = [movie for movie in recommendations if movie.rating >= min_rating]
        logging.info(f"{len(recommendations)} movies after rating filter")

    recommendations.sort(key=lambda x: x.rating or 0, reverse=True)
    final_recommendations = recommendations[:n]
    logging.info(f"Returning {len(final_recommendations)} recommendations")

    return final_recommendations

def get_content_based_recommendations(title, n=10):
    if df is None or cosine_sim is None or indices is None:
        logging.warning("Motor basado en contenido no disponible; devolviendo lista vacía")
        return []

    content_recommendations = get_content_recommendations(title, df, cosine_sim, indices)
    logging.info(f"Retrieved {len(content_recommendations)} content-based recommendations")

    if content_recommendations.empty:
        logging.warning(f"No content-based recommendations found for '{title}'")
        return []

    recommendations = [
        Movie(
            id=df.loc[idx, 'id'],
            title=df.loc[idx, 'title'],
            genres=df.loc[idx, 'genres'],
            rating=df.loc[idx, 'vote_average']
        )
        for idx in content_recommendations.index[:n]
        if idx in df.index
    ]

    logging.info(f"Returning {len(recommendations)} content-based recommendations")
    return recommendations