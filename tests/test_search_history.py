from app.models.search_history import SearchHistory


class TestSearchHistoryModel:

    def test_log_search_saves_a_record(self, app):
        with app.app_context():
            SearchHistory.log_search('title', 'Inception', 5)
            recent = SearchHistory.get_recent(10)
            assert len(recent) == 1
            assert recent[0].query == 'Inception'
            assert recent[0].search_type == 'title'
            assert recent[0].results_count == 5

    def test_log_search_ignores_empty_query(self, app):
        with app.app_context():
            SearchHistory.log_search('title', '', 0)
            recent = SearchHistory.get_recent(10)
            assert recent == []

    def test_get_recent_returns_most_recent_first(self, app):
        with app.app_context():
            SearchHistory.log_search('genre', 'Drama', 3)
            SearchHistory.log_search('title', 'The Godfather', 1)
            recent = SearchHistory.get_recent(10)
            assert recent[0].query == 'The Godfather'
            assert recent[1].query == 'Drama'

    def test_get_recent_respects_limit(self, app):
        with app.app_context():
            for i in range(5):
                SearchHistory.log_search('genre', f'Genre{i}', 1)
            recent = SearchHistory.get_recent(2)
            assert len(recent) == 2

    def test_to_dict_has_expected_keys(self, app):
        with app.app_context():
            SearchHistory.log_search('title', 'Interstellar', 7)
            recent = SearchHistory.get_recent(1)
            data = recent[0].to_dict()
            assert set(data.keys()) == {'id', 'type', 'query', 'results_count', 'searched_at'}


class TestSearchHistoryEndpoint:

    def test_history_endpoint_returns_200(self, client):
        response = client.get('/api/history')
        assert response.status_code == 200

    def test_history_endpoint_returns_list(self, client):
        response = client.get('/api/history')
        assert isinstance(response.get_json(), list)

    def test_history_populates_after_recommendation_search(self, client):
        client.get('/recommendations?genre=Drama&n=3')
        response = client.get('/api/history')
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['type'] == 'genre'

    def test_history_endpoint_respects_limit_param(self, client):
        for genre in ['Drama', 'Action', 'Comedy']:
            client.get(f'/recommendations?genre={genre}&n=1')
        response = client.get('/api/history?limit=2')
        assert len(response.get_json()) == 2
