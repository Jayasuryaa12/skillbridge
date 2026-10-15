"""
Configuration classes for skill-service.
All settings are loaded from environment variables via python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def parse_cors_origins() -> list[str]:
    """Parse ALLOWED_ORIGINS (or fallback CORS_ORIGINS) into a list."""
    raw = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    if not raw or raw.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


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
    ALLOWED_ORIGINS: list[str] = parse_cors_origins()
    CORS_ORIGINS: list[str] = ALLOWED_ORIGINS  # Backwards compatibility

    # ── Inter-Service Integration ──────────────────────────────────────────
    OPPORTUNITY_SERVICE_URL: str = os.getenv("OPPORTUNITY_SERVICE_URL", "http://127.0.0.1:5002")
    INTER_SERVICE_KEY: str | None = os.getenv("INTER_SERVICE_KEY", None)
    OPPORTUNITY_CONNECT_TIMEOUT: float = float(os.getenv("OPPORTUNITY_CONNECT_TIMEOUT", "15.0"))
    OPPORTUNITY_READ_TIMEOUT: float = float(os.getenv("OPPORTUNITY_READ_TIMEOUT", "25.0"))

    # ── Pagination ─────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))


class DevelopmentConfig(Config):
    """Development environment — verbose logging, debug mode on."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Production environment — debug off, strict production settings."""

    DEBUG: bool = False
    TESTING: bool = False


class TestingConfig(Config):
    """Testing environment — uses an isolated test database."""

    TESTING: bool = True
    DEBUG: bool = True
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
