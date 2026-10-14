"""
Seed script for opportunity-service.
===================================
Populates opportunity_db with:
- 32 diverse opportunities (internships, hackathons, projects, workshops)

Usage:
    python scripts/seed.py [--drop]

Flags:
    --drop    Drop existing opportunities collection before seeding.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, TEXT

CURRENT_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(SERVICE_ROOT))

# Load .env from opportunity-service root
load_dotenv(SERVICE_ROOT / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "opportunity_db")
DATA_DIR = SERVICE_ROOT / "data"


def now_utc():
    return datetime.now(timezone.utc)


def seed():
    parser = argparse.ArgumentParser(description="Seed MongoDB for opportunity-service")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing opportunities collection before seeding",
    )
    args = parser.parse_args()

    print(f"Connecting to MongoDB at {MONGO_URI} (Database: {DB_NAME})...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    if args.drop:
        print("⚠️  --drop flag provided. Dropping opportunities collection...")
        db.opportunities.drop()
        print("✅ Opportunities collection dropped.")

    # Create indexes
    print("Creating indexes...")
    db.opportunities.create_index(
        [("title", TEXT), ("description", TEXT), ("organization", TEXT)],
        background=True,
    )
    db.opportunities.create_index([("type", ASCENDING)], background=True)
    db.opportunities.create_index([("difficulty", ASCENDING)], background=True)
    db.opportunities.create_index([("mode", ASCENDING)], background=True)
    db.opportunities.create_index([("status", ASCENDING)], background=True)
    db.opportunities.create_index([("deadline", ASCENDING)], background=True)
    db.opportunities.create_index([("tags", ASCENDING)], background=True)
    db.opportunities.create_index([("required_skills.name", ASCENDING)], background=True)

    opportunities_file = DATA_DIR / "opportunities.json"
    if not opportunities_file.exists():
        print(f"❌ Error: {opportunities_file} does not exist.")
        sys.exit(1)

    with open(opportunities_file, "r", encoding="utf-8") as f:
        opps_data = json.load(f)

    inserted = 0
    updated = 0
    now = now_utc()

    for opp in opps_data:
        title = opp["title"].strip()
        org = opp["organization"].strip()

        # Deduplicate based on title + organization
        existing = db.opportunities.find_one({"title": title, "organization": org})

        doc_data = {
            "title": title,
            "type": opp["type"],
            "organization": org,
            "description": opp["description"].strip(),
            "required_skills": opp.get("required_skills", []),
            "difficulty": opp["difficulty"],
            "mode": opp["mode"],
            "location": opp.get("location"),
            "start_date": opp.get("start_date"),
            "deadline": opp.get("deadline"),
            "duration": opp.get("duration"),
            "stipend": opp.get("stipend"),
            "prize": opp.get("prize"),
            "apply_url": opp["apply_url"].strip(),
            "tags": opp.get("tags", []),
            "status": opp.get("status", "open"),
            "updated_at": now,
        }

        if existing:
            db.opportunities.update_one({"_id": existing["_id"]}, {"$set": doc_data})
            updated += 1
        else:
            doc_data["created_at"] = now
            db.opportunities.insert_one(doc_data)
            inserted += 1

    print(f"✅ Opportunities: {inserted} inserted, {updated} updated (Total: {len(opps_data)} processed).")
    client.close()
    print("🎉 Opportunity-service database seeding completed successfully!")


if __name__ == "__main__":
    seed()
