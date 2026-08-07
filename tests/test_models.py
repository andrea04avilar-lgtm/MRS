from app.models.movie import Movie


class TestMovieModel:

    def test_movie_creation_sets_attributes(self):
        movie = Movie(1, "Test Movie", "Action,Drama", 8.5)
        assert movie.id == 1
        assert movie.title == "Test Movie"
        assert movie.genres == "Action,Drama"
        assert movie.rating == 8.5

    def test_movie_creation_default_rating_is_none(self):
        movie = Movie(2, "No Rating Movie", "Comedy")
        assert movie.rating is None

    def test_get_all_returns_seeded_movies(self, app):
        with app.app_context():
            movies = Movie.get_all()
            assert len(movies) == 5
            titles = [m.title for m in movies]
            assert "The Godfather" in titles

    def test_get_movies_by_genre_filters_correctly(self, app):
        with app.app_context():
            movies = Movie.get_movies_by_genre("Drama")
            assert len(movies) >= 1
            assert all("Drama" in m.genres for m in movies)

    def test_get_movies_by_genre_no_match_returns_empty(self, app):
        with app.app_context():
            movies = Movie.get_movies_by_genre("Documentary")
            assert movies == []

    def test_get_movie_details_found(self, app):
        with app.app_context():
            movie = Movie.get_movie_details(1)
            assert movie is not None
            assert movie.title == "The Shawshank Redemption"

    def test_get_movie_details_not_found_returns_none(self, app):
        with app.app_context():
            movie = Movie.get_movie_details(9999)
            assert movie is None

    def test_get_movies_by_title_partial_match(self, app):
        with app.app_context():
            movies = Movie.get_movies_by_title("Godfather")
            assert len(movies) == 1
            assert movies[0].title == "The Godfather"
