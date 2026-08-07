import os

import pytest

from config.config import Config
from app.data_processing.content_based_filtering import (
    prepare_content_based_data,
    get_recommendations,
    get_director,
    get_list,
    clean_data,
    safe_literal_eval,
)
from app.data_processing.demographic_filtering import load_and_process_data, get_top_movies

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture()
def fixture_paths(monkeypatch):
    """Apunta la configuración a CSVs sintéticos pequeños en lugar del dataset
    real de Kaggle, para poder probar la lógica de procesamiento de datos
    sin depender de un archivo externo de varios cientos de MB."""
    monkeypatch.setattr(Config, 'MOVIES_METADATA_PATH', os.path.join(FIXTURES_DIR, 'mini_movies.csv'))
    monkeypatch.setattr(Config, 'CREDITS_PATH', os.path.join(FIXTURES_DIR, 'mini_credits.csv'))


class TestContentBasedFiltering:

    def test_get_director_finds_director_job(self):
        crew = [{'job': 'Producer', 'name': 'P'}, {'job': 'Director', 'name': 'D. Villeneuve'}]
        assert get_director(crew) == 'D. Villeneuve'

    def test_get_director_returns_nan_when_missing(self):
        import math
        crew = [{'job': 'Producer', 'name': 'P'}]
        assert math.isnan(get_director(crew))

    def test_get_list_truncates_to_three(self):
        items = [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}, {'name': 'D'}]
        assert get_list(items) == ['A', 'B', 'C']

    def test_get_list_handles_non_list_input(self):
        assert get_list(None) == []

    def test_clean_data_lowercases_and_strips_spaces_list(self):
        assert clean_data(['New York', 'LA']) == ['newyork', 'la']

    def test_clean_data_handles_string(self):
        assert clean_data('New York') == 'newyork'

    def test_clean_data_handles_missing_value(self):
        assert clean_data(None) == ''

    def test_safe_literal_eval_parses_valid_list(self):
        assert safe_literal_eval("[1, 2, 3]") == [1, 2, 3]

    def test_safe_literal_eval_returns_empty_on_invalid(self):
        assert safe_literal_eval("not a python literal {{{") == []

    def test_prepare_content_based_data_builds_similarity_matrix(self, fixture_paths):
        df, cosine_sim, indices = prepare_content_based_data()
        assert len(df) == 4
        assert cosine_sim.shape == (4, 4)
        assert 'Alpha Quest' in indices.index

    def test_get_recommendations_finds_similar_movie(self, fixture_paths):
        df, cosine_sim, indices = prepare_content_based_data()
        recs = get_recommendations('Alpha Quest', df, cosine_sim, indices)
        # "Delta Rising" comparte director, keyword y sinopsis muy similar a "Alpha Quest"
        assert 'Delta Rising' in recs.values

    def test_get_recommendations_unknown_title_returns_empty(self, fixture_paths):
        df, cosine_sim, indices = prepare_content_based_data()
        recs = get_recommendations('Movie That Does Not Exist', df, cosine_sim, indices)
        assert recs.empty


class TestDemographicFiltering:

    def test_load_and_process_data_computes_weighted_score(self, fixture_paths):
        result = load_and_process_data()
        assert 'score' in result.columns
        assert len(result) > 0

    def test_get_top_movies_returns_requested_count(self, fixture_paths):
        top = get_top_movies(2)
        assert len(top) <= 2

    def test_get_top_movies_sorted_descending_by_score(self, fixture_paths):
        top = get_top_movies(10)
        scores = top['score'].tolist()
        assert scores == sorted(scores, reverse=True)
