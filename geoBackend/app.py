from flask import Flask
from config import Config
from flasgger import Swagger
from extentions import db, jwt, bcrypt, limiter
from initialized.init_user import ensure_admin_user_exists
from modles import user, ip_record
from initialized.db_init import wait_for_mysql
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/app.log",
)
logger = logging.getLogger(__name__)


def create_app():
    try:
        app = Flask(__name__)
        app.config.from_object(Config)

        db.init_app(app)
        jwt.init_app(app)
        bcrypt.init_app(app)
        limiter.init_app(app)
        Swagger(app)

        with app.app_context():
            wait_for_mysql(app)
            ensure_admin_user_exists()

        from routes.geo_route import geo_bp
        from routes.auth_route import auth_bp

        app.register_blueprint(geo_bp)
        app.register_blueprint(auth_bp)

        return app

    except Exception as e:
        logger.critical(f"Critical error creating the Flask app: {e}")
        return None


if __name__ == "__main__":
    app = create_app()
    if app:
        app.run(debug=False, host="0.0.0.0", port=5000)
    else:
        print("Application failed to start due to errors. Check logs for details.")
