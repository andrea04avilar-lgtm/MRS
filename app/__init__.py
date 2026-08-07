from flask import Flask
from config.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Blueprints
    from app.routes import recommendations
    from app.routes import health

    app.register_blueprint(recommendations.bp)
    app.register_blueprint(health.bp)

    # Cierre limpio de la conexión a la base de datos al final de cada request
    from app.utils.database import close_db
    app.teardown_appcontext(close_db)

    return app
