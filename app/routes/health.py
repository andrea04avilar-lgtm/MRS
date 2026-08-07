import os
import time
from datetime import datetime, timezone

from flask import Blueprint, jsonify, current_app

from app.utils.database import get_db

bp = Blueprint('health', __name__)

_START_TIME = time.time()


@bp.route('/api/health')
def health_check():
    """Endpoint de diagnóstico para monitoreo en tiempo real.

    Verifica:
      - Que el proceso Flask está vivo y respondiendo.
      - Que la conexión a la base de datos funciona.
      - Si el dataset de recomendación basado en contenido está cargado.

    Devuelve HTTP 200 si todo está saludable, o 503 si algún chequeo crítico falla.
    """
    checks = {}
    overall_status = "healthy"

    # 1. Chequeo de base de datos
    try:
        db = get_db()
        db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc}"
        overall_status = "unhealthy"

    # 2. Chequeo del motor de recomendación basado en contenido (opcional/degradable)
    try:
        from app.services import recommendation_service as rs
        checks["content_based_engine"] = "loaded" if rs.df is not None else "disabled (fallback a base de datos)"
    except Exception as exc:  # noqa: BLE001
        checks["content_based_engine"] = f"error: {exc}"

    response = {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - _START_TIME, 2),
        "environment": os.environ.get("FLASK_ENV", "development"),
        "checks": checks,
    }

    status_code = 200 if overall_status == "healthy" else 503
    return jsonify(response), status_code
