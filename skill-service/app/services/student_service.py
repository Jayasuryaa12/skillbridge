"""
Student service layer — all MongoDB interactions for the students collection.
Routes call these functions; they never touch the database directly.
"""

from typing import Any, Optional

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.utils.helpers import now_utc, serialize_doc


# ── Read operations ────────────────────────────────────────────────────────

def get_all_students(
    db: Database,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    department: Optional[str] = None,
    year: Optional[int] = None,
    career_goal: Optional[str] = None,
) -> tuple[list[dict], int]:
    """
    Return a paginated list of students with optional filters.

    Parameters
    ----------
    search      : Full-text search across name, college, department.
    department  : Case-insensitive partial match.
    year        : Exact match (1–4).
    career_goal : career _id string — exact match.

    Returns
    -------
    (students_list, total_count)
    """
    query: dict[str, Any] = {}

    if search:
        query["$text"] = {"$search": search}
    if department:
        query["department"] = {"$regex": department, "$options": "i"}
    if year is not None:
        query["year"] = year
    if career_goal:
        query["career_goal"] = career_goal

    total = db.students.count_documents(query)
    skip = (page - 1) * page_size

    cursor = db.students.find(query).skip(skip).limit(page_size).sort("created_at", -1)
    return [serialize_doc(s) for s in cursor], total


def get_student_by_id(db: Database, student_id: str) -> Optional[dict]:
    """Return a single student document by its ObjectId string, or None."""
    doc = db.students.find_one({"_id": ObjectId(student_id)})
    return serialize_doc(doc)


def get_student_by_email(db: Database, email: str) -> Optional[dict]:
    """Return a student by email (case-insensitive), or None."""
    doc = db.students.find_one({"email": email.lower().strip()})
    return serialize_doc(doc)


# ── Write operations ───────────────────────────────────────────────────────

def create_student(db: Database, data: dict[str, Any]) -> dict:
    """
    Insert a new student document.

    Raises
    ------
    DuplicateKeyError
        If the email already exists (caught in the route).
    """
    now = now_utc()
    skills = [
        {**s, "name": s["name"].strip(), "updated_at": now}
        for s in data.get("skills", [])
    ]
    doc = {
        "name": data["name"].strip(),
        "email": data["email"].lower().strip(),
        "college": data["college"].strip(),
        "department": data["department"].strip(),
        "year": data["year"],
        "career_goal": data.get("career_goal"),       # career _id or None
        "skills": skills,
        "created_at": now,
        "updated_at": now,
    }
    result = db.students.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


def update_student(
    db: Database, student_id: str, data: dict[str, Any]
) -> Optional[dict]:
    """
    Update allowed profile fields (not skills — use skill-specific helpers).

    Returns
    -------
    Updated document, or None if not found.
    """
    if "email" in data:
        data["email"] = data["email"].lower().strip()
    data["updated_at"] = now_utc()

    updated = db.students.find_one_and_update(
        {"_id": ObjectId(student_id)},
        {"$set": data},
        return_document=True,
    )
    return serialize_doc(updated)


def delete_student(db: Database, student_id: str) -> bool:
    """
    Delete a student and cascade-delete their roadmaps.

    Returns
    -------
    True if a document was deleted, False if not found.
    """
    result = db.students.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count:
        db.roadmaps.delete_many({"student_id": student_id})
        return True
    return False


# ── Skill sub-resource operations ──────────────────────────────────────────

def add_or_replace_skill(
    db: Database, student_id: str, skill_data: dict[str, Any]
) -> Optional[dict]:
    """
    Add a skill to the student's skills list.
    If a skill with the same name (case-insensitive) already exists, replace it.

    Returns
    -------
    Updated student document, or None if student not found.
    """
    now = now_utc()
    skill_name = skill_data["name"].strip()

    # Remove any existing skill with the same name (case-insensitive)
    db.students.update_one(
        {"_id": ObjectId(student_id)},
        {
            "$pull": {
                "skills": {"name": {"$regex": f"^{skill_name}$", "$options": "i"}}
            }
        },
    )

    # Push the new skill
    new_skill = {"name": skill_name, "level": skill_data["level"], "updated_at": now}
    updated = db.students.find_one_and_update(
        {"_id": ObjectId(student_id)},
        {"$push": {"skills": new_skill}, "$set": {"updated_at": now}},
        return_document=True,
    )
    return serialize_doc(updated)


def update_skill_level(
    db: Database, student_id: str, skill_name: str, level: int
) -> Optional[dict]:
    """
    Update the level of a named skill (case-insensitive match).

    Returns
    -------
    Updated student document, or None if student or skill not found.
    """
    now = now_utc()
    updated = db.students.find_one_and_update(
        {
            "_id": ObjectId(student_id),
            "skills.name": {"$regex": f"^{skill_name}$", "$options": "i"},
        },
        {
            "$set": {
                "skills.$.level": level,
                "skills.$.updated_at": now,
                "updated_at": now,
            }
        },
        return_document=True,
    )
    return serialize_doc(updated)


def delete_skill(
    db: Database, student_id: str, skill_name: str
) -> Optional[dict]:
    """
    Remove a named skill from the student's list.

    Returns
    -------
    Updated student document, or None if student not found.
    """
    now = now_utc()
    updated = db.students.find_one_and_update(
        {"_id": ObjectId(student_id)},
        {
            "$pull": {
                "skills": {"name": {"$regex": f"^{skill_name}$", "$options": "i"}}
            },
            "$set": {"updated_at": now},
        },
        return_document=True,
    )
    return serialize_doc(updated)
