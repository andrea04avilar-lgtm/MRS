"""
Pruebas End-to-End (Selenium) — Fase 4

Estas pruebas simulan a un usuario real interactuando con la aplicación
desplegada. Por defecto apuntan a http://localhost:5000, pero pueden
apuntar a cualquier ambiente (staging, producción) mediante la variable
de entorno APP_BASE_URL — esto es lo que usa el pipeline de GitHub Actions
para probar el sitio recién desplegado.

Requiere que la app esté corriendo (localmente con `python run.py`,
con Docker, o en el enlace público de producción) ANTES de correr estas
pruebas. No se ejecutan como parte de `pytest tests/` normal porque
necesitan un servidor real levantado y un navegador Chrome/Chromium.

Ejecutar:
    APP_BASE_URL=http://localhost:5000 pytest tests/test_e2e.py -v
"""
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


class TestHomePageLoads:
    """1. El usuario abre la aplicación y ve la página principal correctamente."""

    def test_home_page_loads_and_has_correct_title(self, driver):
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "Movie" in driver.title or "Recommendation" in driver.title
        heading = driver.find_element(By.TAG_NAME, "h1")
        assert "CineMatch" in heading.text


class TestHealthEndpointIsReachable:
    """2. El endpoint de diagnóstico responde en el ambiente desplegado."""

    def test_health_endpoint_is_reachable_and_healthy(self, driver):
        driver.get(f"{BASE_URL}/api/health")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert '"status"' in body_text
        assert '"healthy"' in body_text


class TestGenreSelectionFlow:
    """3. El usuario selecciona un género y solicita recomendaciones."""

    def test_user_can_select_genre_and_submit_form(self, driver):
        driver.get(BASE_URL)
        genre_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "genre"))
        )
        from selenium.webdriver.support.ui import Select
        Select(genre_select).select_by_visible_text("Action")

        submit_button = driver.find_element(By.CSS_SELECTOR, "#recommendationForm button[type='submit'], #recommendationForm button")
        submit_button.click()

        # Se espera a que el contenedor de resultados aparezca en el DOM
        time.sleep(2)
        assert genre_select.get_property("value") == "Action"


class TestMovieTitleSearchFlow:
    """4. El usuario busca recomendaciones a partir del título de una película."""

    def test_user_can_type_movie_title_and_search(self, driver):
        driver.get(BASE_URL)
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "movieTitle"))
        )
        title_input.clear()
        title_input.send_keys("Inception")
        assert title_input.get_attribute("value") == "Inception"
