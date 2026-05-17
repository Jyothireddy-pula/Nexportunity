import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    APP_NAME = "Startup Opportunity Aggregator"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'opportunities.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    ENABLE_SCHEDULER = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def get_config(config_name: str | None = None):
    name = (config_name or os.getenv("FLASK_ENV") or "development").lower()
    if name == "production":
        return ProductionConfig
    if name == "testing":
        return TestingConfig
    return DevelopmentConfig
