"""
Roadmap routes blueprint — skill-service.

Endpoints
---------
POST   /api/students/<id>/roadmap/generate         Generate (or regenerate) roadmap
GET    /api/students/<id>/roadmap                  Retrieve the student's roadmap
PATCH  /api/students/<id>/roadmap/stages/<order>   Update a stage's status
"""

import logging

from bson import ObjectId
from flask import Blueprint, request
from marshmallow import ValidationError

from app.db import get_db
from app.models.schemas import UpdateStageStatusSchema
from app.services import career_service, student_service
from app.services.gap_analysis import analyze_skill_gap
from app.services.roadmap_service import generate_roadmap
from app.utils.helpers import is_valid_object_id, now_utc, serialize_doc
from app.utils.response import created_response, error_response, success_response

logger = logging.getLogger(__name__)
roadmaps_bp = Blueprint("roadmaps", __name__)

_stage_schema = UpdateStageStatusSchema()


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_student_and_career(db, student_id: str, career_id: str | None = None):
    """
    Fetch the raw student document (with ObjectId) and resolve the target career.
    Returns (raw_student, raw_career, error_response_or_None).
    """
    raw_student = db.students.find_one({"_id": ObjectId(student_id)})
    if not raw_student:
        return None, None, error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    cid = career_id or raw_student.get("career_goal")
    if not cid:
        return raw_student, None, error_response(
            "MISSING_CAREER",
            "No career_id provided and student has no career_goal set.",
            status_code=400,
        )
    if not is_valid_object_id(cid):
        return raw_student, None, error_response("INVALID_ID", f"Invalid career_id: '{cid}'", status_code=400)

    raw_career = db.careers.find_one({"_id": ObjectId(cid)})
    if not raw_career:
        return raw_student, None, error_response("NOT_FOUND", f"Career '{cid}' not found.", status_code=404)

    return raw_student, raw_career, None


# ══════════════════════════════════════════════════════════════════════════════
# ROADMAP ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@roadmaps_bp.post("/students/<student_id>/roadmap/generate")
def generate_student_roadmap(student_id: str):
    """
    POST /api/students/<id>/roadmap/generate

    Generates (or regenerates) a personalised roadmap.
    Accepts optional ``career_id`` in the JSON body to override the student's
    default career_goal.
    """
    if not is_valid_object_id(student_id):
        return error_response("INVALID_ID", f"Invalid student ID: '{student_id}'", status_code=400)

    body = request.get_json(silent=True) or {}
    career_id = body.get("career_id")

    db = get_db()
    raw_student, raw_career, err = _get_student_and_career(db, student_id, career_id)
    if err:
        return err

    # Run gap analysis first
    gap = analyze_skill_gap(raw_student, raw_career)

    # Build roadmap document
    roadmap_doc = generate_roadmap(raw_student, raw_career, gap)

    # Upsert into roadmaps collection (one roadmap per student+career pair)
    db.roadmaps.replace_one(
        {
            "student_id": str(raw_student["_id"]),
            "career_id": str(raw_career["_id"]),
        },
        roadmap_doc,
        upsert=True,
    )

    # Fetch the saved doc to return with _id
    saved = db.roadmaps.find_one(
        {
            "student_id": str(raw_student["_id"]),
            "career_id": str(raw_career["_id"]),
        }
    )
    result = serialize_doc(saved)
    result["gap_summary"] = gap["summary"]
    result["readiness_score"] = gap["readiness_score"]

    logger.info(
        "Roadmap generated for student=%s career=%s stages=%d",
        student_id,
        str(raw_career["_id"]),
        len(roadmap_doc.get("stages", [])),
    )
    return created_response(result, "Roadmap generated successfully")


@roadmaps_bp.get("/students/<student_id>/roadmap")
def get_student_roadmap(student_id: str):
    """
    GET /api/students/<id>/roadmap

    Returns the stored roadmap. Accepts optional ``career_id`` query param
    to retrieve a roadmap for a specific career (defaults to career_goal).
    """
    if not is_valid_object_id(student_id):
        return error_response("INVALID_ID", f"Invalid student ID: '{student_id}'", status_code=400)

    db = get_db()
    raw_student = db.students.find_one({"_id": ObjectId(student_id)})
    if not raw_student:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    career_id = request.args.get("career_id") or raw_student.get("career_goal")

    query: dict = {"student_id": student_id}
    if career_id:
        query["career_id"] = career_id

    roadmap = db.roadmaps.find_one(query, sort=[("generated_at", -1)])
    if not roadmap:
        return error_response(
            "NOT_FOUND",
            "No roadmap found. Generate one first via POST /roadmap/generate.",
            status_code=404,
        )

    return success_response(serialize_doc(roadmap), "Roadmap retrieved")


@roadmaps_bp.patch("/students/<student_id>/roadmap/stages/<int:order>")
def update_stage_status(student_id: str, order: int):
    """
    PATCH /api/students/<id>/roadmap/stages/<order>

    Update the ``status`` of a single roadmap stage.
    Valid values: not_started | in_progress | completed
    """
    if not is_valid_object_id(student_id):
        return error_response("INVALID_ID", f"Invalid student ID: '{student_id}'", status_code=400)

    try:
        data = _stage_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    career_id = request.args.get("career_id")
    query: dict = {"student_id": student_id}
    if career_id:
        query["career_id"] = career_id

    roadmap = db.roadmaps.find_one(query, sort=[("generated_at", -1)])
    if not roadmap:
        return error_response(
            "NOT_FOUND",
            "No roadmap found for this student. Generate one first.",
            status_code=404,
        )

    # Validate stage order exists
    stages: list[dict] = roadmap.get("stages", [])
    stage_orders = [s["order"] for s in stages]
    if order not in stage_orders:
        return error_response(
            "NOT_FOUND",
            f"Stage {order} not found in this roadmap.",
            status_code=404,
        )

    # Update the specific stage's status
    result = db.roadmaps.find_one_and_update(
        {**query, "stages.order": order},
        {"$set": {"stages.$.status": data["status"]}},
        return_document=True,
    )

    logger.info("Stage %d marked '%s' for student %s", order, data["status"], student_id)
    return success_response(serialize_doc(result), f"Stage {order} marked as '{data['status']}'")
