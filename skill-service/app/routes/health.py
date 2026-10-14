"""Health endpoint for skill-service."""

from flask import Blueprint
from pymongo import MongoClient

from app.db import get_db
from app.utils.response import success_response, error_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health_check():
    """
    GET /api/health

    Returns service status and a lightweight MongoDB ping.
    Used by Render health checks and the frontend status dashboard.
    """
    try:
        db = get_db()
        # Cheap ping — does not require any collection to exist
        db.command("ping")
        mongo_status = "connected"
    except Exception as exc:
        return error_response(
            code="DB_UNAVAILABLE",
            message="MongoDB is unreachable",
            details=str(exc),
            status_code=503,
        )

    return success_response(
        data={
            "service": "skill-service",
            "status": "ok",
            "database": mongo_status,
            "version": "1.0.0",
        },
        message="Skill service is healthy",
    )
