"""
Configuration classes for skill-service.
All settings are loaded from environment variables via python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = False

    # ── MongoDB ────────────────────────────────────────────────────────────
    MONGO_URI: str = os.getenv(
        "MONGO_URI", "mongodb://localhost:27017/skill_db"
    )
    DB_NAME: str = os.getenv("DB_NAME", "skill_db")

    # ── CORS ───────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # ── Pagination ─────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))


class DevelopmentConfig(Config):
    """Development environment — verbose logging, debug mode on."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Production environment — debug off, stricter settings."""

    DEBUG: bool = False


class TestingConfig(Config):
    """Testing environment — uses an isolated test database."""

    TESTING: bool = True
    DEBUG: bool = True
    # Tests will be run against mongomock; URI is irrelevant but kept for clarity
    MONGO_URI: str = os.getenv(
        "TEST_MONGO_URI", "mongodb://localhost:27017/skill_db_test"
    )
    DB_NAME: str = "skill_db_test"


# ── Config selector ────────────────────────────────────────────────────────
_CONFIG_MAP: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> type[Config]:
    """Return the appropriate config class based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return _CONFIG_MAP.get(env, DevelopmentConfig)
