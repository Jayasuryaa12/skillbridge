"""
Opportunities routes blueprint — opportunity-service.

Endpoints
---------
POST   /api/opportunities           Create opportunity
GET    /api/opportunities           List with filters + pagination
GET    /api/opportunities/stats     Aggregated counts
GET    /api/opportunities/<id>      Get single opportunity
PUT    /api/opportunities/<id>      Update opportunity
DELETE /api/opportunities/<id>      Delete opportunity
"""

import logging

from flask import Blueprint, current_app, request
from marshmallow import ValidationError

from app.db import get_db
from app.models.schemas import CreateOpportunitySchema, UpdateOpportunitySchema
from app.services import opportunity_service
from app.utils.helpers import is_valid_object_id, parse_pagination
from app.utils.response import (
    created_response,
    error_response,
    paginated_response,
    success_response,
)

logger = logging.getLogger(__name__)
opportunities_bp = Blueprint("opportunities", __name__)

_create_schema = CreateOpportunitySchema()
_update_schema = UpdateOpportunitySchema()

# Valid sort values
_VALID_SORTS = {"deadline", "newest"}
# Valid filter enums
_VALID_TYPES = {"project", "hackathon", "internship", "workshop"}
_VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
_VALID_MODES = {"online", "offline", "hybrid"}
_VALID_STATUSES = {"open", "closed"}


@opportunities_bp.post("/opportunities")
def create_opportunity():
    """POST /api/opportunities — Create a new opportunity."""
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    opp = opportunity_service.create_opportunity(get_db(), data)
    logger.info("Opportunity created: %s", opp["_id"])
    return created_response(opp, "Opportunity created successfully")


@opportunities_bp.get("/opportunities/stats")
def get_stats():
    """GET /api/opportunities/stats — Aggregated counts by type, status, difficulty."""
    stats = opportunity_service.get_stats(get_db())
    return success_response(stats, "Stats retrieved")


@opportunities_bp.get("/opportunities")
def list_opportunities():
    """
    GET /api/opportunities — Paginated list with filters.

    Query params
    ------------
    type        : project | hackathon | internship | workshop
    difficulty  : beginner | intermediate | advanced
    mode        : online | offline | hybrid
    status      : open | closed
    skill       : skill name substring (case-insensitive)
    search      : full-text search
    sort        : deadline | newest (default)
    page        : int (default 1)
    page_size   : int (default 20, max 100)
    """
    args = request.args

    # Validate enum filters
    opp_type = args.get("type")
    if opp_type and opp_type not in _VALID_TYPES:
        return error_response("INVALID_PARAM", f"type must be one of {_VALID_TYPES}", status_code=400)

    difficulty = args.get("difficulty")
    if difficulty and difficulty not in _VALID_DIFFICULTIES:
        return error_response("INVALID_PARAM", f"difficulty must be one of {_VALID_DIFFICULTIES}", status_code=400)

    mode = args.get("mode")
    if mode and mode not in _VALID_MODES:
        return error_response("INVALID_PARAM", f"mode must be one of {_VALID_MODES}", status_code=400)

    status = args.get("status")
    if status and status not in _VALID_STATUSES:
        return error_response("INVALID_PARAM", f"status must be one of {_VALID_STATUSES}", status_code=400)

    sort = args.get("sort", "newest")
    if sort not in _VALID_SORTS:
        return error_response("INVALID_PARAM", f"sort must be one of {_VALID_SORTS}", status_code=400)

    page, page_size = parse_pagination(
        args,
        default_size=current_app.config["DEFAULT_PAGE_SIZE"],
        max_size=current_app.config["MAX_PAGE_SIZE"],
    )

    opportunities, total = opportunity_service.get_all_opportunities(
        db=get_db(),
        page=page,
        page_size=page_size,
        opp_type=opp_type,
        difficulty=difficulty,
        mode=mode,
        status=status,
        skill=args.get("skill"),
        search=args.get("search"),
        sort=sort,
    )
    return paginated_response(opportunities, total, page, page_size, "Opportunities retrieved")


@opportunities_bp.get("/opportunities/<opp_id>")
def get_opportunity(opp_id: str):
    """GET /api/opportunities/<id> — Retrieve a single opportunity."""
    if not is_valid_object_id(opp_id):
        return error_response("INVALID_ID", f"'{opp_id}' is not a valid ObjectId.", status_code=400)

    opp = opportunity_service.get_opportunity_by_id(get_db(), opp_id)
    if not opp:
        return error_response("NOT_FOUND", f"Opportunity '{opp_id}' not found.", status_code=404)

    return success_response(opp, "Opportunity retrieved")


@opportunities_bp.put("/opportunities/<opp_id>")
def update_opportunity(opp_id: str):
    """PUT /api/opportunities/<id> — Update an opportunity."""
    if not is_valid_object_id(opp_id):
        return error_response("INVALID_ID", f"'{opp_id}' is not a valid ObjectId.", status_code=400)

    try:
        data = _update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    if not opportunity_service.get_opportunity_by_id(db, opp_id):
        return error_response("NOT_FOUND", f"Opportunity '{opp_id}' not found.", status_code=404)

    updated = opportunity_service.update_opportunity(db, opp_id, data)
    return success_response(updated, "Opportunity updated successfully")


@opportunities_bp.delete("/opportunities/<opp_id>")
def delete_opportunity(opp_id: str):
    """DELETE /api/opportunities/<id> — Delete an opportunity."""
    if not is_valid_object_id(opp_id):
        return error_response("INVALID_ID", f"'{opp_id}' is not a valid ObjectId.", status_code=400)

    deleted = opportunity_service.delete_opportunity(get_db(), opp_id)
    if not deleted:
        return error_response("NOT_FOUND", f"Opportunity '{opp_id}' not found.", status_code=404)

    logger.info("Opportunity deleted: %s", opp_id)
    return success_response(None, "Opportunity deleted successfully")
