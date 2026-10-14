"""
Opportunity service layer — all MongoDB interactions for the opportunities collection.
"""

from typing import Any, Optional

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from app.utils.helpers import now_utc, serialize_doc


# ── Read operations ────────────────────────────────────────────────────────

def get_all_opportunities(
    db: Database,
    page: int = 1,
    page_size: int = 20,
    opp_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    mode: Optional[str] = None,
    status: Optional[str] = None,
    skill: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "newest",
) -> tuple[list[dict], int]:
    """
    Return a paginated, filtered list of opportunities.

    Filter parameters
    -----------------
    opp_type   : Exact match on ``type`` field.
    difficulty : Exact match.
    mode       : Exact match.
    status     : Exact match (default shows all).
    skill      : Case-insensitive match on required_skills.name.
    search     : Full-text search on title, description, organization.
    sort       : ``"deadline"`` (soonest first) | ``"newest"`` (default, created_at DESC).
    """
    query: dict[str, Any] = {}

    if search:
        query["$text"] = {"$search": search}
    if opp_type:
        query["type"] = opp_type
    if difficulty:
        query["difficulty"] = difficulty
    if mode:
        query["mode"] = mode
    if status:
        query["status"] = status
    if skill:
        query["required_skills.name"] = {"$regex": skill, "$options": "i"}

    total = db.opportunities.count_documents(query)
    skip = (page - 1) * page_size

    sort_key = ("deadline", ASCENDING) if sort == "deadline" else ("created_at", DESCENDING)

    cursor = (
        db.opportunities.find(query).skip(skip).limit(page_size).sort(*sort_key)
    )
    return [serialize_doc(o) for o in cursor], total


def get_opportunity_by_id(db: Database, opp_id: str) -> Optional[dict]:
    """Return a single opportunity by ObjectId, or None."""
    doc = db.opportunities.find_one({"_id": ObjectId(opp_id)})
    return serialize_doc(doc)


def get_stats(db: Database) -> dict[str, Any]:
    """
    Return aggregated counts:
    - Total opportunities
    - Counts by type
    - Counts by status
    - Counts by difficulty
    """
    pipeline_by_type = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    pipeline_by_status = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    pipeline_by_difficulty = [
        {"$group": {"_id": "$difficulty", "count": {"$sum": 1}}},
    ]
    pipeline_by_mode = [
        {"$group": {"_id": "$mode", "count": {"$sum": 1}}},
    ]

    by_type = {r["_id"]: r["count"] for r in db.opportunities.aggregate(pipeline_by_type)}
    by_status = {r["_id"]: r["count"] for r in db.opportunities.aggregate(pipeline_by_status)}
    by_difficulty = {r["_id"]: r["count"] for r in db.opportunities.aggregate(pipeline_by_difficulty)}
    by_mode = {r["_id"]: r["count"] for r in db.opportunities.aggregate(pipeline_by_mode)}

    return {
        "total": db.opportunities.count_documents({}),
        "by_type": by_type,
        "by_status": by_status,
        "by_difficulty": by_difficulty,
        "by_mode": by_mode,
    }


# ── Write operations ───────────────────────────────────────────────────────

def create_opportunity(db: Database, data: dict[str, Any]) -> dict:
    """Insert a new opportunity document."""
    now = now_utc()
    doc = {
        **data,
        "status": data.get("status", "open"),
        "created_at": now,
        "updated_at": now,
    }
    result = db.opportunities.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


def update_opportunity(
    db: Database, opp_id: str, data: dict[str, Any]
) -> Optional[dict]:
    """Update allowed opportunity fields. Returns updated doc or None."""
    data["updated_at"] = now_utc()
    updated = db.opportunities.find_one_and_update(
        {"_id": ObjectId(opp_id)},
        {"$set": data},
        return_document=True,
    )
    return serialize_doc(updated)


def delete_opportunity(db: Database, opp_id: str) -> bool:
    """Delete an opportunity. Returns True if deleted, False if not found."""
    result = db.opportunities.delete_one({"_id": ObjectId(opp_id)})
    return bool(result.deleted_count)
