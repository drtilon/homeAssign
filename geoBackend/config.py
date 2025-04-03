# config.py
import os


class Config:
    DB_CONFIG = {
        "user": os.environ.get("DB_USER", "geouser"),
        "password": os.environ.get("DB_PASSWORD", "geopassword"),
        "host": os.environ.get("DB_HOST", "db"),
        "database": os.environ.get("DB_NAME", "geolocation"),
    }

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_change_in_production")
    TOKEN_EXPIRATION = 24

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:3306/{DB_CONFIG['database']}",
    )
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
