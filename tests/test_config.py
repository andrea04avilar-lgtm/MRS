import os

from config.config import Config, TestingConfig, ProductionConfig


class TestConfig:

    def test_default_config_has_tmdb_base_url(self):
        assert Config.TMDB_BASE_URL == 'https://api.themoviedb.org/3'

    def test_testing_config_enables_testing_flag(self):
        assert TestingConfig.TESTING is True

    def test_testing_config_disables_content_based_engine(self):
        assert TestingConfig.ENABLE_CONTENT_BASED is False

    def test_production_config_disables_debug(self):
        assert ProductionConfig.DEBUG is False

    def test_secret_key_reads_from_environment(self, monkeypatch):
        monkeypatch.setenv('SECRET_KEY', 'super-secret-test-value')
        # Se recarga el módulo para tomar la variable de entorno actualizada
        import importlib
        from config import config as config_module
        importlib.reload(config_module)
        assert config_module.Config.SECRET_KEY == 'super-secret-test-value'
        importlib.reload(config_module)  # restaurar estado por defecto para otras pruebas
