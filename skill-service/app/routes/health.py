"""Health endpoint for skill-service."""

from flask import Blueprint
from pymongo import MongoClient

from app.db import get_db
from app.utils.response import success_response, error_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
@health_bp.get("/health")
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


@health_bp.get("/api/system/status")
def system_status():
    """
    GET /api/system/status

    Composite system status reporting Skill Service status plus
    Opportunity Service reachability and round-trip latency.
    """
    from datetime import datetime, timezone
    from clients.opportunity_client import OpportunityClient

    # 1. Skill service DB status
    try:
        db = get_db()
        db.command("ping")
        skill_db_status = "connected"
    except Exception as exc:
        skill_db_status = f"unreachable: {exc}"

    # 2. Opportunity service status
    client = OpportunityClient()
    opp_status = client.check_health()
    opp_status["url"] = client.base_url

    overall_status = "healthy"
    if skill_db_status != "connected":
        overall_status = "unhealthy"
    elif not opp_status.get("reachable"):
        overall_status = "degraded"

    return success_response(
        data={
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_service": {
                "service": "skill-service",
                "status": "healthy" if skill_db_status == "connected" else "unhealthy",
                "database": skill_db_status,
            },
            "opportunity_service": opp_status,
        },
        message="System status retrieved",
    )
