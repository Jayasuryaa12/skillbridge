"""
Student routes blueprint — skill-service.

Endpoints
---------
POST   /api/students                              Create student
GET    /api/students                              List students (search, filters, pagination)
GET    /api/students/<id>                         Get single student
PUT    /api/students/<id>                         Update student profile
DELETE /api/students/<id>                         Delete student

POST   /api/students/<id>/skills                  Add / replace a skill
PUT    /api/students/<id>/skills/<skill_name>     Update skill level
DELETE /api/students/<id>/skills/<skill_name>     Remove a skill

GET    /api/students/<id>/skill-gap               Run gap analysis
       ?career_id=<id>  (optional; defaults to student.career_goal)
"""

import logging

from flask import Blueprint, current_app, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError

from app.db import get_db
from app.models.schemas import (
    AddSkillSchema,
    CreateStudentSchema,
    UpdateSkillSchema,
    UpdateStudentSchema,
)
from app.services import career_service, student_service
from app.services.gap_analysis import analyze_skill_gap
from app.utils.helpers import is_valid_object_id, parse_pagination
from app.utils.response import (
    created_response,
    error_response,
    paginated_response,
    success_response,
)

logger = logging.getLogger(__name__)
students_bp = Blueprint("students", __name__)

# ── Schema singletons ──────────────────────────────────────────────────────
_create_schema = CreateStudentSchema()
_update_schema = UpdateStudentSchema()
_add_skill_schema = AddSkillSchema()
_update_skill_schema = UpdateSkillSchema()


# ── Helpers ────────────────────────────────────────────────────────────────

def _validate_id(id_str: str, label: str = "ID"):
    """Return an error response tuple if *id_str* is not a valid ObjectId."""
    if not is_valid_object_id(id_str):
        return error_response(
            code="INVALID_ID",
            message=f"Invalid {label}: '{id_str}' is not a valid ObjectId.",
            status_code=400,
        )
    return None


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT CRUD
# ══════════════════════════════════════════════════════════════════════════════

@students_bp.post("/students")
def create_student():
    """POST /api/students — Create a new student."""
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    try:
        student = student_service.create_student(db, data)
    except DuplicateKeyError:
        return error_response(
            "DUPLICATE_EMAIL", f"A student with email '{data['email']}' already exists.", status_code=409
        )

    logger.info("Student created: %s", student["_id"])
    return created_response(student, "Student created successfully")


@students_bp.get("/students")
def list_students():
    """GET /api/students — List students with optional search/filters."""
    args = request.args
    page, page_size = parse_pagination(
        args,
        default_size=current_app.config["DEFAULT_PAGE_SIZE"],
        max_size=current_app.config["MAX_PAGE_SIZE"],
    )

    year_str = args.get("year")
    year = None
    if year_str:
        try:
            year = int(year_str)
            if year not in range(1, 5):
                return error_response("INVALID_PARAM", "year must be 1–4", status_code=400)
        except ValueError:
            return error_response("INVALID_PARAM", "year must be an integer", status_code=400)

    students, total = student_service.get_all_students(
        db=get_db(),
        page=page,
        page_size=page_size,
        search=args.get("search"),
        department=args.get("department"),
        year=year,
        career_goal=args.get("career_goal"),
    )
    return paginated_response(students, total, page, page_size, "Students retrieved")


@students_bp.get("/students/<student_id>")
def get_student(student_id: str):
    """GET /api/students/<id> — Retrieve a single student."""
    if err := _validate_id(student_id, "student ID"):
        return err

    student = student_service.get_student_by_id(get_db(), student_id)
    if not student:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    return success_response(student, "Student retrieved")


@students_bp.put("/students/<student_id>")
def update_student(student_id: str):
    """PUT /api/students/<id> — Update student profile fields."""
    if err := _validate_id(student_id, "student ID"):
        return err

    try:
        data = _update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()

    # Guard: check student exists
    if not student_service.get_student_by_id(db, student_id):
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    try:
        updated = student_service.update_student(db, student_id, data)
    except DuplicateKeyError:
        return error_response(
            "DUPLICATE_EMAIL", f"Email '{data.get('email')}' is already in use.", status_code=409
        )

    return success_response(updated, "Student updated successfully")


@students_bp.delete("/students/<student_id>")
def delete_student(student_id: str):
    """DELETE /api/students/<id> — Delete a student and their roadmaps."""
    if err := _validate_id(student_id, "student ID"):
        return err

    deleted = student_service.delete_student(get_db(), student_id)
    if not deleted:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    logger.info("Student deleted: %s", student_id)
    return success_response(None, "Student deleted successfully")


# ══════════════════════════════════════════════════════════════════════════════
# SKILL SUB-RESOURCE
# ══════════════════════════════════════════════════════════════════════════════

@students_bp.post("/students/<student_id>/skills")
def add_skill(student_id: str):
    """POST /api/students/<id>/skills — Add or replace a skill."""
    if err := _validate_id(student_id, "student ID"):
        return err

    try:
        data = _add_skill_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    if not student_service.get_student_by_id(db, student_id):
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    updated = student_service.add_or_replace_skill(db, student_id, data)
    return success_response(updated, f"Skill '{data['name']}' added/updated")


@students_bp.put("/students/<student_id>/skills/<skill_name>")
def update_skill(student_id: str, skill_name: str):
    """PUT /api/students/<id>/skills/<skill_name> — Update a skill's level."""
    if err := _validate_id(student_id, "student ID"):
        return err

    try:
        data = _update_skill_schema.load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error_response("VALIDATION_ERROR", "Invalid input", exc.messages, 422)

    db = get_db()
    updated = student_service.update_skill_level(db, student_id, skill_name, data["level"])
    if not updated:
        return error_response(
            "NOT_FOUND",
            f"Student '{student_id}' or skill '{skill_name}' not found.",
            status_code=404,
        )

    return success_response(updated, f"Skill '{skill_name}' updated to level {data['level']}")


@students_bp.delete("/students/<student_id>/skills/<skill_name>")
def delete_skill(student_id: str, skill_name: str):
    """DELETE /api/students/<id>/skills/<skill_name> — Remove a skill."""
    if err := _validate_id(student_id, "student ID"):
        return err

    db = get_db()
    if not student_service.get_student_by_id(db, student_id):
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    updated = student_service.delete_skill(db, student_id, skill_name)
    return success_response(updated, f"Skill '{skill_name}' removed")


# ══════════════════════════════════════════════════════════════════════════════
# SKILL GAP ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

@students_bp.get("/students/<student_id>/skill-gap")
def skill_gap(student_id: str):
    """
    GET /api/students/<id>/skill-gap?career_id=<optional>

    Runs the rule-based gap analysis. Uses the student's career_goal if
    career_id query param is not provided.
    """
    if err := _validate_id(student_id, "student ID"):
        return err

    db = get_db()
    student = student_service.get_student_by_id(db, student_id)
    if not student:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    # Determine target career
    career_id = request.args.get("career_id") or student.get("career_goal")
    if not career_id:
        return error_response(
            "MISSING_CAREER",
            "No career_id provided and student has no career_goal set.",
            status_code=400,
        )

    if not is_valid_object_id(career_id):
        return error_response("INVALID_ID", f"Invalid career_id: '{career_id}'", status_code=400)

    career = career_service.get_career_by_id(db, career_id)
    if not career:
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    # Re-fetch student as raw doc for the analyzer (needs _id as ObjectId)
    from bson import ObjectId
    raw_student = db.students.find_one({"_id": ObjectId(student_id)})
    raw_career = db.careers.find_one({"_id": ObjectId(career_id)})

    result = analyze_skill_gap(raw_student, raw_career)
    return success_response(result, "Skill gap analysis completed")


# ══════════════════════════════════════════════════════════════════════════════
# INTER-SERVICE RECOMMENDATIONS & DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@students_bp.get("/students/<student_id>/recommendations")
def get_recommendations(student_id: str):
    """
    GET /api/students/<id>/recommendations?types=&limit=

    Flow: load student -> run gap analysis -> call Opportunity Service /match
    with the student's skills and gap data -> merge and return.
    Implements graceful degradation when Opportunity Service is unreachable.
    """
    from bson import ObjectId
    from clients.opportunity_client import (
        OpportunityClient,
        OpportunityInvalidResponseError,
        OpportunityServiceUnavailableError,
        OpportunityUnauthorizedError,
    )

    if err := _validate_id(student_id, "student ID"):
        return err

    db = get_db()
    raw_student = db.students.find_one({"_id": ObjectId(student_id)})
    if not raw_student:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    career_id = request.args.get("career_id") or raw_student.get("career_goal")
    if not career_id:
        return error_response(
            "MISSING_CAREER",
            "No career_id provided and student has no career_goal set.",
            status_code=400,
        )

    if not is_valid_object_id(career_id):
        return error_response("INVALID_ID", f"Invalid career_id: '{career_id}'", status_code=400)

    raw_career = db.careers.find_one({"_id": ObjectId(career_id)})
    if not raw_career:
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    # 1. Run gap analysis locally
    gap_result = analyze_skill_gap(raw_student, raw_career)

    # 2. Parse query parameters
    try:
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        limit = 10

    raw_types = request.args.get("types")
    types = [t.strip() for t in raw_types.split(",") if t.strip()] if raw_types else None

    # 3. Call Opportunity Service via client
    opp_client = OpportunityClient()
    student_skills = raw_student.get("skills", [])
    missing_skills = [s["skill"] for s in gap_result.get("missing", [])]
    developing_skills = [s["skill"] for s in gap_result.get("developing", [])]

    student_summary = {
        "_id": str(raw_student["_id"]),
        "name": raw_student["name"],
        "email": raw_student["email"],
        "college": raw_student.get("college"),
        "department": raw_student.get("department"),
        "year": raw_student.get("year"),
    }
    career_summary = {
        "_id": str(raw_career["_id"]),
        "title": raw_career["title"],
        "slug": raw_career.get("slug"),
        "category": raw_career.get("category"),
    }
    gap_summary = {
        "readiness_score": gap_result["readiness_score"],
        "matched_count": len(gap_result.get("matched", [])),
        "developing_count": len(gap_result.get("developing", [])),
        "missing_count": len(gap_result.get("missing", [])),
    }

    try:
        matches = opp_client.match_opportunities(
            skills=student_skills,
            missing_skills=missing_skills,
            developing_skills=developing_skills,
            limit=limit,
            types=types,
        )
        return success_response(
            data={
                "student": student_summary,
                "career": career_summary,
                "skill_gap_summary": gap_summary,
                "recommendations": matches,
                "opportunity_service": {"status": "available"},
            },
            message=f"Retrieved {len(matches)} recommended opportunities",
        )
    except OpportunityServiceUnavailableError as exc:
        logger.warning("Graceful degradation on recommendations: %s", exc)
        return success_response(
            data={
                "student": student_summary,
                "career": career_summary,
                "skill_gap_summary": gap_summary,
                "recommendations": [],
                "opportunity_service": {
                    "status": "unavailable",
                    "message": "Opportunity Service is temporarily unreachable; gap analysis preserved.",
                },
            },
            message="Recommendations partially retrieved (Opportunity Service unavailable)",
        )
    except OpportunityUnauthorizedError as exc:
        return error_response(
            "UPSTREAM_UNAUTHORIZED",
            "Opportunity Service authentication failed.",
            details=str(exc),
            status_code=502,
        )
    except OpportunityInvalidResponseError as exc:
        return error_response(
            "UPSTREAM_INVALID_RESPONSE",
            f"Opportunity Service returned an invalid response: {exc}",
            details=exc.details,
            status_code=502,
        )


@students_bp.get("/students/<student_id>/dashboard")
def get_dashboard(student_id: str):
    """
    GET /api/students/<id>/dashboard

    Unified dashboard endpoint for the frontend combining:
    - readiness score
    - category scores (for radar chart)
    - matched, developing, missing counts
    - top 5 priority skills to learn
    - roadmap progress percentage
    - top 5 recommended opportunities (from Opportunity Service)
    - opportunity catalog stats (from Opportunity Service)
    """
    from bson import ObjectId
    from clients.opportunity_client import (
        OpportunityClient,
        OpportunityInvalidResponseError,
        OpportunityServiceUnavailableError,
        OpportunityUnauthorizedError,
    )

    if err := _validate_id(student_id, "student ID"):
        return err

    db = get_db()
    raw_student = db.students.find_one({"_id": ObjectId(student_id)})
    if not raw_student:
        return error_response("NOT_FOUND", f"Student '{student_id}' not found.", status_code=404)

    career_id = request.args.get("career_id") or raw_student.get("career_goal")
    if not career_id:
        return error_response(
            "MISSING_CAREER",
            "No career_id provided and student has no career_goal set.",
            status_code=400,
        )

    if not is_valid_object_id(career_id):
        return error_response("INVALID_ID", f"Invalid career_id: '{career_id}'", status_code=400)

    raw_career = db.careers.find_one({"_id": ObjectId(career_id)})
    if not raw_career:
        return error_response("NOT_FOUND", f"Career '{career_id}' not found.", status_code=404)

    # 1. Skill Gap Analysis
    gap_result = analyze_skill_gap(raw_student, raw_career)

    # 2. Roadmap progress calculation
    roadmap = db.roadmaps.find_one({"student_id": student_id})
    if not roadmap:
        roadmap = db.roadmaps.find_one({"student_id": ObjectId(student_id)})

    roadmap_progress = 0.0
    if roadmap and roadmap.get("stages"):
        stages = roadmap["stages"]
        completed = sum(1 for s in stages if s.get("status") == "completed")
        roadmap_progress = round((completed / len(stages)) * 100, 1)

    # 3. Outbound calls to Opportunity Service
    opp_client = OpportunityClient()
    student_skills = raw_student.get("skills", [])
    missing_skills = [s["skill"] for s in gap_result.get("missing", [])]
    developing_skills = [s["skill"] for s in gap_result.get("developing", [])]

    top_recommendations = []
    opportunity_stats = None
    opp_service_status = {"status": "available"}

    try:
        top_recommendations = opp_client.match_opportunities(
            skills=student_skills,
            missing_skills=missing_skills,
            developing_skills=developing_skills,
            limit=5,
        )
        opportunity_stats = opp_client.get_opportunity_stats()
    except OpportunityServiceUnavailableError as exc:
        logger.warning("Graceful degradation on dashboard: %s", exc)
        opp_service_status = {
            "status": "unavailable",
            "message": "Opportunity Service is unreachable; showing local student profile.",
        }
    except OpportunityUnauthorizedError as exc:
        return error_response(
            "UPSTREAM_UNAUTHORIZED",
            "Opportunity Service authentication failed.",
            details=str(exc),
            status_code=502,
        )
    except OpportunityInvalidResponseError as exc:
        return error_response(
            "UPSTREAM_INVALID_RESPONSE",
            f"Opportunity Service returned an invalid response: {exc}",
            details=exc.details,
            status_code=502,
        )

    dashboard_data = {
        "student": {
            "_id": str(raw_student["_id"]),
            "name": raw_student["name"],
            "email": raw_student["email"],
            "college": raw_student.get("college"),
            "department": raw_student.get("department"),
            "year": raw_student.get("year"),
        },
        "career": {
            "_id": str(raw_career["_id"]),
            "title": raw_career["title"],
            "slug": raw_career.get("slug"),
            "category": raw_career.get("category"),
        },
        "readiness_score": gap_result["readiness_score"],
        "category_scores": gap_result["category_scores"],
        "skill_counts": {
            "matched": len(gap_result.get("matched", [])),
            "developing": len(gap_result.get("developing", [])),
            "missing": len(gap_result.get("missing", [])),
        },
        "top_priority_skills": gap_result.get("priority_list", [])[:5],
        "roadmap_progress_percentage": roadmap_progress,
        "top_recommendations": top_recommendations,
        "opportunity_stats": opportunity_stats,
        "opportunity_service": opp_service_status,
    }

    return success_response(dashboard_data, "Dashboard data retrieved successfully")
