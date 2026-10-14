"""
Seed script for skill-service.
==============================
Populates skill_db with:
- 5 comprehensive career paths (from data/careers.json)
- 4 realistic student profiles (from data/students.json) with resolved career_goal IDs

Usage:
    python scripts/seed.py [--drop]

Flags:
    --drop    Drop existing students, careers, and roadmaps collections before seeding.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, TEXT

# Add project root to sys.path so app imports work if needed
CURRENT_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(SERVICE_ROOT))

# Load .env from skill-service root
load_dotenv(SERVICE_ROOT / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "skill_db")
DATA_DIR = SERVICE_ROOT / "data"


def now_utc():
    return datetime.now(timezone.utc)


def seed():
    parser = argparse.ArgumentParser(description="Seed MongoDB for skill-service")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing collections before seeding",
    )
    args = parser.parse_args()

    print(f"Connecting to MongoDB at {MONGO_URI} (Database: {DB_NAME})...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    if args.drop:
        print("⚠️  --drop flag provided. Dropping collections: students, careers, roadmaps...")
        db.students.drop()
        db.careers.drop()
        db.roadmaps.drop()
        print("✅ Collections dropped.")

    # Create indexes
    print("Creating indexes...")
    db.students.create_index([("email", ASCENDING)], unique=True, background=True)
    db.students.create_index(
        [("name", TEXT), ("college", TEXT), ("department", TEXT)],
        background=True,
    )
    db.students.create_index([("career_goal", ASCENDING)], background=True)
    db.students.create_index([("year", ASCENDING)], background=True)

    db.careers.create_index([("slug", ASCENDING)], unique=True, background=True)
    db.careers.create_index([("title", TEXT), ("description", TEXT)], background=True)
    db.careers.create_index([("category", ASCENDING)], background=True)

    db.roadmaps.create_index([("student_id", ASCENDING)], background=True)
    db.roadmaps.create_index([("career_id", ASCENDING)], background=True)
    db.roadmaps.create_index([("student_id", ASCENDING), ("career_id", ASCENDING)], background=True)

    # 1. Seed Careers
    careers_file = DATA_DIR / "careers.json"
    if not careers_file.exists():
        print(f"❌ Error: {careers_file} does not exist.")
        sys.exit(1)

    with open(careers_file, "r", encoding="utf-8") as f:
        careers_data = json.load(f)

    slug_to_id = {}
    careers_inserted = 0
    careers_updated = 0

    now = now_utc()
    for career in careers_data:
        slug = career["slug"]
        existing = db.careers.find_one({"slug": slug})
        if existing:
            db.careers.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "title": career["title"],
                        "description": career["description"],
                        "category": career["category"],
                        "required_skills": career["required_skills"],
                        "updated_at": now,
                    }
                },
            )
            slug_to_id[slug] = str(existing["_id"])
            careers_updated += 1
        else:
            career_doc = {
                "title": career["title"],
                "slug": slug,
                "description": career["description"],
                "category": career["category"],
                "required_skills": career["required_skills"],
                "created_at": now,
                "updated_at": now,
            }
            res = db.careers.insert_one(career_doc)
            slug_to_id[slug] = str(res.inserted_id)
            careers_inserted += 1

    print(f"✅ Careers: {careers_inserted} inserted, {careers_updated} updated.")

    # 2. Seed Students
    students_file = DATA_DIR / "students.json"
    if not students_file.exists():
        print(f"❌ Error: {students_file} does not exist.")
        sys.exit(1)

    with open(students_file, "r", encoding="utf-8") as f:
        students_data = json.load(f)

    students_inserted = 0
    students_updated = 0

    for student in students_data:
        email = student["email"].lower().strip()
        career_slug = student.get("career_goal_slug")
        career_id = slug_to_id.get(career_slug) if career_slug else None

        skills_list = [
            {
                "name": s["name"].strip(),
                "level": s["level"],
                "updated_at": now,
            }
            for s in student.get("skills", [])
        ]

        existing = db.students.find_one({"email": email})
        if existing:
            db.students.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "name": student["name"],
                        "college": student["college"],
                        "department": student["department"],
                        "year": student["year"],
                        "career_goal": career_id,
                        "skills": skills_list,
                        "updated_at": now,
                    }
                },
            )
            students_updated += 1
        else:
            doc = {
                "name": student["name"],
                "email": email,
                "college": student["college"],
                "department": student["department"],
                "year": student["year"],
                "career_goal": career_id,
                "skills": skills_list,
                "created_at": now,
                "updated_at": now,
            }
            db.students.insert_one(doc)
            students_inserted += 1

    print(f"✅ Students: {students_inserted} inserted, {students_updated} updated.")
    client.close()
    print("🎉 Skill-service database seeding completed successfully!")


if __name__ == "__main__":
    seed()
