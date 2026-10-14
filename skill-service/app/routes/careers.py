"""
Career routes blueprint — skill-service.

Endpoints
---------
POST   /api/careers           Create career
GET    /api/careers           List careers (search, category, pagination)
GET    /api/careers/<id>      Get single career
PUT    /api/careers/<id>      Update career
DELETE /api/careers/<id>      Delete career
"""

import logging

from flask import Blueprint, current_app, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError

from app.db import get_db
from app.models.schemas import CreateCareerSchema, UpdateCareerSchema
from app.services import career_service
from app.utils.helpers import is_valid_object_id, parse_pagination
from app.utils.response import (
    created_response,
    error_response,
    paginated_response,
    success_response,
)

logger = logging.getLogger(__name__)
careers_bp = Blueprint("careers", __name__)

_create_schema = CreateCareerSchema()
_update_schema = UpdateCareerSchema()


@careers_bp.post("/careers")
def create_career():
    """POST /api/careers — Create a new career with required skills."""
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    try:
        career = career_service.create_career(db, data)
    except DuplicateKeyError:
        slug = data.get("slug") or data["title"]
        return error_response(
            "DUPLICATE_SLUG", f"A career with slug '{slug}' already exists.", status_code=409
        )

    logger.info("Career created: %s (%s)", career["title"], career["_id"])
    return created_response(career, "Career created successfully")


@careers_bp.get("/careers")
def list_careers():
    """GET /api/careers — List careers with optional search and category filter."""
    args = request.args
    page, page_size = parse_pagination(
        args,
        default_size=current_app.config["DEFAULT_PAGE_SIZE"],
        max_size=current_app.config["MAX_PAGE_SIZE"],
    )

    careers, total = career_service.get_all_careers(
        db=get_db(),
        page=page,
        page_size=page_size,
        search=args.get("search"),
        category=args.get("category"),
    )
    return paginated_response(careers, total, page, page_size, "Careers retrieved")


@careers_bp.get("/careers/<career_id>")
def get_career(career_id: str):
    """GET /api/careers/<id> — Retrieve a single career by ObjectId."""
    if not is_valid_object_id(career_id):
        return error_response(
            "INVALID_ID", f"'{career_id}' is not a valid ObjectId.", status_code=400
        )

    career = career_service.get_career_by_id(get_db(), career_id)
    if not career:
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    return success_response(career, "Career retrieved")


@careers_bp.put("/careers/<career_id>")
def update_career(career_id: str):
    """PUT /api/careers/<id> — Update career fields."""
    if not is_valid_object_id(career_id):
        return error_response(
            "INVALID_ID", f"'{career_id}' is not a valid ObjectId.", status_code=400
        )

    try:
        data = _update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    if not career_service.get_career_by_id(db, career_id):
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    updated = career_service.update_career(db, career_id, data)
    return success_response(updated, "Career updated successfully")


@careers_bp.delete("/careers/<career_id>")
def delete_career(career_id: str):
    """DELETE /api/careers/<id> — Delete a career."""
    if not is_valid_object_id(career_id):
        return error_response(
            "INVALID_ID", f"'{career_id}' is not a valid ObjectId.", status_code=400
        )

    deleted = career_service.delete_career(get_db(), career_id)
    if not deleted:
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    logger.info("Career deleted: %s", career_id)
    return success_response(None, "Career deleted successfully")
