#!/bin/bash
set -e

DB_PATH="${DATABASE_PATH:-/app/data/movies.db}"

if [ ! -f "$DB_PATH" ]; then
    echo "[entrypoint] No se encontró base de datos en $DB_PATH, inicializando datos de demo..."
    python scripts/database_setup.py
else
    echo "[entrypoint] Base de datos existente encontrada en $DB_PATH"
fi

exec "$@"
