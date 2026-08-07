from unittest.mock import patch


class TestIndexRoute:

    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_contains_expected_title(self, client):
        response = client.get('/')
        assert b'CineMatch' in response.data


class TestRecommendationsRoute:

    def test_recommendations_returns_200(self, client):
        response = client.get('/recommendations?n=3')
        assert response.status_code == 200

    def test_recommendations_returns_json_list(self, client):
        response = client.get('/recommendations?n=3')
        data = response.get_json()
        assert isinstance(data, list)

    def test_recommendations_respects_n_parameter(self, client):
        response = client.get('/recommendations?n=2')
        data = response.get_json()
        assert len(data) <= 2

    def test_recommendations_by_title_calls_tmdb_search(self, client):
        with patch('app.routes.recommendations.search_movies', return_value=[]):
            response = client.get('/recommendations?title=Inception')
            assert response.status_code == 200
            assert response.get_json() == []


class TestMovieDetailRoute:

    def test_movie_details_not_found_returns_404(self, client):
        with patch('app.routes.recommendations.fetch_movie_data', return_value=None):
            response = client.get('/movie/999999')
            assert response.status_code == 404

    def test_movie_details_found_returns_data(self, client):
        fake_movie = {'id': 42, 'title': 'Fake Movie', 'overview': 'A test movie'}
        with patch('app.routes.recommendations.fetch_movie_data', return_value=fake_movie):
            response = client.get('/movie/42')
            assert response.status_code == 200
            assert response.get_json()['title'] == 'Fake Movie'


class TestErrorHandlers:

    def test_unknown_route_returns_404(self, client):
        response = client.get('/this-route-does-not-exist')
        assert response.status_code == 404
