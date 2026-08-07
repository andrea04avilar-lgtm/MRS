# ---------- Etapa 1: build de dependencias ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Dependencias del sistema necesarias solo para compilar wheels (pandas/scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ---------- Etapa 2: imagen final (runtime, sin herramientas de build) ----------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Usuario no-root por seguridad
RUN useradd --create-home --shell /bin/bash appuser

# Copiamos solo los paquetes ya instalados desde la etapa builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiamos el código fuente de la aplicación
COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY static/ ./static/
COPY templates/ ./templates/
COPY run.py .
COPY docker-entrypoint.sh .

RUN chmod +x docker-entrypoint.sh \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 5000

# Healthcheck nativo de Docker: usa el mismo endpoint /api/health de la Fase 6
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:5000/api/health').status==200 else sys.exit(1)"

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "run:app"]
