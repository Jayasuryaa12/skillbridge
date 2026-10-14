"""
Career service layer — all MongoDB interactions for the careers collection.
"""

from typing import Any, Optional

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.utils.helpers import now_utc, serialize_doc, slugify


# ── Read operations ────────────────────────────────────────────────────────

def get_all_careers(
    db: Database,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
) -> tuple[list[dict], int]:
    """
    Return a paginated list of careers with optional filters.

    Parameters
    ----------
    search   : Full-text search on title + description.
    category : Case-insensitive partial match.
    """
    query: dict[str, Any] = {}

    if search:
        query["$text"] = {"$search": search}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}

    total = db.careers.count_documents(query)
    skip = (page - 1) * page_size

    cursor = db.careers.find(query).skip(skip).limit(page_size).sort("title", 1)
    return [serialize_doc(c) for c in cursor], total


def get_career_by_id(db: Database, career_id: str) -> Optional[dict]:
    """
    Return a career by its ObjectId.

    Returns
    -------
    Serialised career document, or None if not found.
    """
    doc = db.careers.find_one({"_id": ObjectId(career_id)})
    return serialize_doc(doc)


def get_career_by_slug(db: Database, slug: str) -> Optional[dict]:
    """Return a career by slug, or None."""
    doc = db.careers.find_one({"slug": slug})
    return serialize_doc(doc)


# ── Write operations ───────────────────────────────────────────────────────

def create_career(db: Database, data: dict[str, Any]) -> dict:
    """
    Insert a new career document.

    Auto-generates a slug from the title if not provided.

    Raises
    ------
    DuplicateKeyError if slug already exists (caught in route).
    """
    now = now_utc()
    slug = (data.get("slug") or "").strip() or slugify(data["title"])

    if db.careers.find_one({"slug": slug}):
        raise DuplicateKeyError(f"Career with slug '{slug}' already exists.")

    doc = {
        "title": data["title"].strip(),
        "slug": slug,
        "description": data["description"].strip(),
        "category": data["category"].strip(),
        "required_skills": data["required_skills"],
        "created_at": now,
        "updated_at": now,
    }
    result = db.careers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


def update_career(
    db: Database, career_id: str, data: dict[str, Any]
) -> Optional[dict]:
    """
    Update allowed career fields.

    Returns
    -------
    Updated document, or None if not found.
    """
    data["updated_at"] = now_utc()
    updated = db.careers.find_one_and_update(
        {"_id": ObjectId(career_id)},
        {"$set": data},
        return_document=True,
    )
    return serialize_doc(updated)


def delete_career(db: Database, career_id: str) -> bool:
    """
    Delete a career.

    Returns
    -------
    True if deleted, False if not found.
    """
    result = db.careers.delete_one({"_id": ObjectId(career_id)})
    return bool(result.deleted_count)
