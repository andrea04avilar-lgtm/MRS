# 🎬 CineMatch — Movie Recommendation System (Modernizado)

Proyecto Final de Reingeniería de Software. Este repositorio contiene la
refactorización, contenedorización, pruebas automatizadas, pipeline de CI/CD
y despliegue continuo de un sistema legado Flask de recomendación de
películas.

---

## 📜 Arquitectura Legada (estado original)

El proyecto original (`raviraj-p/MRS`) ya tenía una separación básica en
capas (`app/models`, `app/routes`, `app/services`, `app/data_processing`),
pero presentaba varios problemas típicos de un sistema legado:

- **Configuración hardcodeada**: la API Key de TMDB estaba escrita
  directamente en `config/config.py`, expuesta en el control de versiones.
- **Acoplamiento fuerte a un dataset externo**: `recommendation_service.py`
  cargaba el CSV de Kaggle **al momento de importar el módulo**. Si el
  archivo no existía, **toda la aplicación crasheaba al arrancar**
  (imposible de dockerizar o desplegar sin el dataset de varios cientos
  de MB incluido).
- **Firma de función inconsistente**: la ruta `/recommendations` llamaba
  a `get_recommendations(genre, n, start_year, end_year, min_rating)`,
  pero la función del servicio solo aceptaba `(genre, n, min_rating)` —
  esto producía un error en tiempo de ejecución.
- **Esquema de base de datos incompleto**: `scripts/database_setup.py`
  creaba la tabla `movies` sin la columna `vote_average`, pero el modelo
  `Movie` y las rutas sí la consultaban.
- **Pruebas rotas**: `tests/test_recommendations.py` importaba una función
  (`content_based_recommendations`) que no existía en el código.
- **Sin pruebas E2E, sin Docker, sin CI/CD, sin endpoint de salud.**

## 🏗️ Arquitectura Nueva (modernizada)

- **Configuración centralizada por entorno**: `config/config.py` usa
  `os.environ` + `python-dotenv`, con clases `Config` / `TestingConfig` /
  `ProductionConfig`. Ningún secreto vive en el código fuente.
- **Degradación segura (graceful degradation)**: el motor de recomendación
  basado en contenido se carga de forma perezosa y con manejo de
  excepciones. Si el dataset de Kaggle no está presente, la app **sigue
  funcionando** usando el motor basado en la base de datos SQLite, en vez
  de crashear. Esto es lo que permite dockerizar y desplegar la app sin
  necesitar el dataset completo dentro de la imagen.
- **`app/utils/database.py`** ahora lee la ruta de la base de datos desde
  `current_app.config` en vez de una constante global — hace la app
  testeable con bases de datos temporales aisladas por prueba.
- **Endpoint de diagnóstico `/api/health`**: reporta el estado del proceso,
  la conexión a base de datos y si el motor de contenido está cargado.
  Usado tanto por Docker `HEALTHCHECK` como por el pipeline de CI/CD para
  verificar el despliegue.
- **45 pruebas unitarias con Pytest** (`tests/`), 81% de cobertura de
  código, cubriendo modelos, rutas HTML/JSON, configuración, base de datos
  y los algoritmos de recomendación (con fixtures CSV sintéticos para no
  depender del dataset real de Kaggle).
- **4 pruebas E2E con Selenium** (`tests/test_e2e.py`) que simulan un
  usuario real: cargar la home, seleccionar género, buscar por título y
  verificar el endpoint de salud contra el ambiente desplegado.
- **Docker multi-etapa** (`Dockerfile`): imagen `python:3.12-slim`,
  usuario no-root, `HEALTHCHECK` nativo, `docker-compose.yml` para
  levantar todo con un comando.
- **Pipeline de GitHub Actions** (`.github/workflows/ci-cd.yml`): pruebas
  unitarias + cobertura, reportes de seguridad (`pip-audit`, `bandit`),
  pruebas E2E, build de imagen Docker, y deploy automático a producción.
- **Historial de búsquedas** (`app/models/search_history.py`,
  `/api/history`): cada búsqueda de recomendaciones (por título o género)
  queda registrada en SQLite y se muestra en la página principal, como
  funcionalidad adicional agregada durante la reingeniería — no se
  limita a estabilizar lo existente, también aporta valor nuevo al
  usuario final.

---

## 🚀 Cómo correr el proyecto

### Localmente (sin Docker)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env              # y edita tus valores
python scripts/database_setup.py
python run.py
```

Visita http://localhost:5000

### Con Docker

```bash
docker build -t cinematch .
docker run -p 5000:5000 --env-file .env cinematch
```

o con Docker Compose:

```bash
docker compose up --build
```

### Pruebas

```bash
# Unitarias + cobertura
pytest tests/ --ignore=tests/test_e2e.py --cov=app --cov=config --cov-report=term-missing

# E2E (requiere la app corriendo en localhost:5000 y Chrome instalado)
APP_BASE_URL=http://localhost:5000 pytest tests/test_e2e.py -v
```

### Endpoint de salud

```bash
curl http://localhost:5000/api/health
```

---

## 📁 Estructura del proyecto

```
app/
├── data_processing/   # Filtrado por contenido y demográfico (Kaggle dataset)
├── models/            # Modelo Movie (acceso a SQLite)
├── routes/            # Blueprints: recommendations, health
├── services/          # Lógica de negocio / orquestación
└── utils/             # Conexión a base de datos
config/                # Configuración por entorno (env vars)
scripts/                # Inicialización de base de datos demo
tests/                 # 45 pruebas unitarias + 4 E2E Selenium
.github/workflows/     # Pipeline CI/CD
Dockerfile, docker-compose.yml, .dockerignore
```

## 🔗 Enlaces

- **Repositorio legado (código original sin modificar):** https://github.com/raviraj-p/MRS
- **Enlace público de producción:** https://mrs-k93i.onrender.com
