from extentions import db
import time
from sqlalchemy.exc import OperationalError
from flask import current_app


def wait_for_mysql(app):
    """Retry MySQL connection until it's available."""
    max_retries = 10
    retries = 0
    while retries < max_retries:
        try:
            with app.app_context():
                app.logger.info("Running db.create_all()...")
                db.create_all()
                current_app.logger.info("Database connection successful!")
            return
        except OperationalError as e:
            current_app.logger.error(
                f"MySQL not ready yet ({e}). Retrying in 5 seconds..."
            )
            time.sleep(5)
            retries += 1

    current_app.logger.error("Failed to connect to MySQL after multiple attempts.")
    exit(1)
