"""Health endpoint for opportunity-service."""

from flask import Blueprint

from app.db import get_db
from app.utils.response import error_response, success_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health_check():
    """
    GET /api/health

    Returns service status and a lightweight MongoDB ping.
    """
    try:
        db = get_db()
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
            "service": "opportunity-service",
            "status": "ok",
            "database": mongo_status,
            "version": "1.0.0",
        },
        message="Opportunity service is healthy",
    )
