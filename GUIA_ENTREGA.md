# 📋 Guía paso a paso para tu Entrega Final de Reingeniería

Este documento te dice **exactamente qué hacer**, en orden, para cumplir
las 6 fases con el código que ya está en este paquete.

---

## Fase 1 — Ingeniería reversa y refactorización ✅ (ya hecho)

El código en `app/`, `config/`, `scripts/` ya está reestructurado. Solo
debes:

1. Reemplaza el contenido de tu repositorio local `MRS` con los archivos
   de este paquete (o clona tu repo y copia estos archivos encima).
2. Revisa el `README.md` — ya documenta la arquitectura legada vs. la nueva
   (es tu entregable de "Documentación Técnica").
3. Sube los cambios:
   ```bash
   git add .
   git commit -m "Fase 1: refactorización a arquitectura modular"
   git push origin main
   ```

**Importante (según la nota de tu profesor):** debes poder **mostrar
también la aplicación antigua tal cual está en GitHub**
(https://github.com/raviraj-p/MRS, la que no has tocado). No borres ni
sobreescribas ese repo original si es una entrega distinta — si vas a
modernizar el mismo repo, considera dejar un tag o branch `legacy` con el
código original antes de refactorizar:
```bash
git tag legacy-original
git push origin legacy-original
```
Así puedes mostrar `git show legacy-original` o cambiar de branch en vivo
durante tu presentación para exhibir el "antes".

---

## Fase 2 — Docker (local)

1. Instala Docker Desktop si no lo tienes: https://www.docker.com/products/docker-desktop/
2. Desde la raíz del proyecto:
   ```bash
   docker build -t cinematch .
   docker run -p 5000:5000 cinematch
   ```
3. Abre http://localhost:5000 y confirma que funciona.
4. **Toma tu captura de pantalla** de Docker Desktop mostrando el
   contenedor `cinematch` corriendo (esto es tu "Evidencia de
   Funcionamiento Local").
5. Sube `Dockerfile`, `.dockerignore`, `docker-compose.yml`:
   ```bash
   git add Dockerfile .dockerignore docker-compose.yml docker-entrypoint.sh
   git commit -m "Fase 2: contenedorización con Docker"
   git push
   ```

---

## Fase 3 — Pytest (ya incluido, 45 pruebas, 81% cobertura)

```bash
pip install -r requirements-dev.txt
pytest tests/ --ignore=tests/test_e2e.py --cov=app --cov=config --cov-report=term-missing
```

Toma captura de la terminal mostrando "45 passed" y el % de cobertura
(≥80%, ya lo cumples con 81%). Sube:
```bash
git add tests/ requirements-dev.txt pytest.ini
git commit -m "Fase 3: suite de pruebas unitarias con 81% de cobertura"
git push
```

---

## Fase 4 — Selenium E2E

1. Instala Chrome/Chromium en tu máquina si no lo tienes.
2. Corre la app en una terminal: `python run.py`
3. En otra terminal:
   ```bash
   APP_BASE_URL=http://localhost:5000 pytest tests/test_e2e.py -v
   ```
   (Quita `--headless=new` de `tests/test_e2e.py` temporalmente si quieres
   ver el navegador abrirse en modo visual para tu evidencia/captura, tal
   como pide el enunciado — "modo visual con todas las aserciones en
   verde").
4. Toma tu captura/video de las 4 pruebas en verde.

---

## Fase 5 — GitHub Actions

1. El archivo `.github/workflows/ci-cd.yml` ya está listo. Solo necesitas
   configurar (opcional pero recomendado) estos **Secrets/Variables** en
   tu repo: `Settings → Secrets and variables → Actions`:
   - `DEPLOY_HOOK_URL` (secret) — la URL de deploy hook de tu plataforma
     de hosting (ver Fase 6).
   - `PROD_URL` (variable) — la URL pública de tu app ya desplegada.
   - Opcional si quieres publicar la imagen en Docker Hub:
     `DOCKERHUB_USERNAME` (variable) y `DOCKERHUB_TOKEN` (secret).

2. Sube el pipeline:
   ```bash
   git add .github/
   git commit -m "Fase 5: pipeline CI/CD con GitHub Actions"
   git push
   ```
3. Ve a la pestaña **Actions** de tu repo en GitHub y confirma que corre
   y termina en verde. Ese enlace es tu "Historial de Ejecución".

---

## Fase 6 — Deploy y entrega final

### Desplegar a producción (opción recomendada para estudiantes: Render, gratis)

1. Crea cuenta en https://render.com y conecta tu GitHub.
2. **New → Web Service** → selecciona tu repo `MRS`.
3. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python scripts/database_setup.py && gunicorn --bind 0.0.0.0:$PORT run:app`
   - **Environment:** agrega las variables de `.env.example` (como
     mínimo `SECRET_KEY`; `TMDB_API_KEY` si tienes una).
4. Deploy. Render te da una URL pública tipo
   `https://cinematch.onrender.com` — esa es tu "Enlace Público de
   Producción".
5. En Render, ve a **Settings → Deploy Hook**, copia esa URL y pégala como
   secret `DEPLOY_HOOK_URL` en GitHub (paso de la Fase 5). Así, cada
   `git push` a `main` dispara un redeploy automático — es justo lo que
   vas a demostrar en vivo.
6. Verifica: `curl https://tu-app.onrender.com/api/health`

*(Alternativas equivalentes: Railway, Fly.io, PythonAnywhere — todas
tienen su propio "deploy hook" o webhook similar; el pipeline ya está
preparado para cualquiera de ellas, solo cambia la URL del secret.)*

### Guion sugerido para tu presentación en vivo

1. **Muestra la app modernizada** funcionando desde el enlace público.
   Navega, busca una película, muestra `/api/health` en el navegador.
2. **Muestra brevemente el repo legado** (`raviraj-p/MRS` o tu branch/tag
   `legacy-original`) para contrastar con la nueva arquitectura — según
   la instrucción adicional de tu profesor.
3. **Haz un cambio menor en vivo:** por ejemplo, cambia un texto en
   `templates/index.html` (el `<p class="tagline">`).
4. **`git push`** ante la audiencia.
5. **Abre la pestaña Actions de GitHub** y muestra en vivo cómo se
   dispara el pipeline: pruebas unitarias → seguridad → E2E → build de
   Docker → deploy.
6. Cuando termine en verde, **recarga el enlace público** y muestra que
   el cambio ya está reflejado en producción.

---

## Checklist final de entregables

- [ ] Repo modular en GitHub con README documentando arquitectura antes/después
- [ ] Dockerfile + .dockerignore + captura de Docker Desktop funcionando
- [ ] ≥15 pruebas unitarias, cobertura ≥80% (tienes 45 pruebas, 81%)
- [ ] 3-4 pruebas Selenium E2E en verde, modo visual
- [ ] Pipeline de GitHub Actions en verde (link al historial de Actions)
- [ ] `/api/health` respondiendo en producción
- [ ] Enlace público de producción activo
- [ ] Presentación en vivo: demo + cambio en vivo + pipeline autónomo
- [ ] Mostrar también la app antigua (repo legado en GitHub)
