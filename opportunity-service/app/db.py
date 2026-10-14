"""
MongoDB connection and index management for opportunity-service.
"""

import logging
from typing import Optional

from flask import Flask, current_app, g
from pymongo import ASCENDING, MongoClient, TEXT
from pymongo.database import Database

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None


def _get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(current_app.config["MONGO_URI"])
    return _client


def get_db() -> Database:
    """Return the current request's database instance (cached in g)."""
    if "db" not in g:
        client = _get_client()
        g.db = client[current_app.config["DB_NAME"]]
    return g.db


def init_db(app: Flask) -> None:
    """Initialise MongoDB connection and create required indexes."""

    @app.teardown_appcontext
    def close_db(error: Optional[Exception]) -> None:
        g.pop("db", None)

    with app.app_context():
        try:
            client = MongoClient(app.config["MONGO_URI"])
            db: Database = client[app.config["DB_NAME"]]

            # ── opportunities ─────────────────────────────────────────────
            try:
                db.opportunities.create_index(
                    [("title", TEXT), ("description", TEXT), ("organization", TEXT)],
                    background=True,
                )
            except Exception:
                pass
            db.opportunities.create_index([("type", ASCENDING)], background=True)
            db.opportunities.create_index([("difficulty", ASCENDING)], background=True)
            db.opportunities.create_index([("mode", ASCENDING)], background=True)
            db.opportunities.create_index([("status", ASCENDING)], background=True)
            db.opportunities.create_index([("deadline", ASCENDING)], background=True)
            db.opportunities.create_index([("tags", ASCENDING)], background=True)
            db.opportunities.create_index(
                [("required_skills.name", ASCENDING)], background=True
            )

            client.close()
            logger.info("✅ MongoDB indexes created for opportunity_db")
        except Exception as exc:
            logger.error("❌ Failed to initialise MongoDB: %s", exc)
            raise
