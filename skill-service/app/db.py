"""
MongoDB connection and index management for skill-service.

Uses a module-level singleton client. The `get_db()` helper retrieves a
per-request database instance cached in Flask's `g` object.
"""

import logging
from typing import Optional

from flask import Flask, current_app, g
from pymongo import ASCENDING, MongoClient, TEXT
from pymongo.database import Database

logger = logging.getLogger(__name__)

# Module-level singleton — one client per process
_client: Optional[MongoClient] = None


def _get_client() -> MongoClient:
    """Return the singleton MongoClient, creating it if necessary."""
    global _client
    if _client is None:
        _client = MongoClient(current_app.config["MONGO_URI"])
    return _client


def get_db() -> Database:
    """
    Return the current request's database instance.
    Creates it once per request and caches it in Flask's `g` object.
    """
    if "db" not in g:
        client = _get_client()
        g.db = client[current_app.config["DB_NAME"]]
    return g.db


def init_db(app: Flask) -> None:
    """
    Initialise MongoDB connection and create all required indexes.
    Called once during app factory setup.
    """

    @app.teardown_appcontext
    def close_db(error: Optional[Exception]) -> None:  # noqa: D401
        """Remove cached DB reference at end of each request context."""
        g.pop("db", None)

    with app.app_context():
        try:
            client = MongoClient(app.config["MONGO_URI"])
            db: Database = client[app.config["DB_NAME"]]

            # ── students ──────────────────────────────────────────────────
            try:
                db.students.create_index([("email", ASCENDING)], unique=True, background=True)
                db.students.create_index([("name", TEXT), ("college", TEXT), ("department", TEXT)], background=True)
            except Exception:
                pass
            db.students.create_index([("career_goal", ASCENDING)], background=True)
            db.students.create_index([("year", ASCENDING)], background=True)

            # ── careers ───────────────────────────────────────────────────
            try:
                db.careers.create_index([("slug", ASCENDING)], unique=True, background=True)
                db.careers.create_index([("title", TEXT), ("description", TEXT)], background=True)
            except Exception:
                pass
            db.careers.create_index([("category", ASCENDING)], background=True)

            # ── roadmaps ──────────────────────────────────────────────────
            db.roadmaps.create_index([("student_id", ASCENDING)], background=True)
            db.roadmaps.create_index([("career_id", ASCENDING)], background=True)
            try:
                db.roadmaps.create_index([("student_id", ASCENDING), ("career_id", ASCENDING)], background=True)
            except Exception:
                pass

            client.close()
            logger.info("✅ MongoDB indexes created for skill_db")
        except Exception as exc:
            logger.error("❌ Failed to initialise MongoDB: %s", exc)
            raise
