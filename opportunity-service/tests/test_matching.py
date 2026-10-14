"""Unit and integration tests for Opportunity Matching algorithm and endpoint."""

from datetime import datetime, timedelta, timezone
import json


def test_match_opportunities_algorithm_logic(client, db):
    now = datetime.now(timezone.utc)

    # Opportunity 1: Good match for Python (Lv. 3), teaches Docker (target missing skill)
    opp1 = {
        "title": "Backend Python Apprentice",
        "type": "internship",
        "organization": "TechCorp",
        "description": "Develop microservices with Python and Docker.",
        "required_skills": [
            {"name": "Python", "min_level": 3},
            {"name": "Docker", "min_level": 2},
        ],
        "difficulty": "intermediate",
        "mode": "remote",
        "status": "open",
        "deadline": (now + timedelta(days=30)).isoformat(),
        "created_at": now,
        "updated_at": now,
    }

    # Opportunity 2: Expired deadline (should be excluded)
    opp2 = {
        "title": "Expired Hackathon",
        "type": "hackathon",
        "organization": "OldOrg",
        "description": "Past event.",
        "required_skills": [{"name": "Python", "min_level": 1}],
        "difficulty": "beginner",
        "mode": "online",
        "status": "open",
        "deadline": (now - timedelta(days=5)).isoformat(),
        "created_at": now,
        "updated_at": now,
    }

    # Opportunity 3: Closed status (should be excluded)
    opp3 = {
        "title": "Closed Workshop",
        "type": "workshop",
        "organization": "ClosedOrg",
        "description": "Closed workshop.",
        "required_skills": [],
        "difficulty": "beginner",
        "mode": "online",
        "status": "closed",
        "deadline": (now + timedelta(days=10)).isoformat(),
        "created_at": now,
        "updated_at": now,
    }

    # Opportunity 4: Hard prerequisites (penalty test)
    opp4 = {
        "title": "Senior Rust Kernel Engineer",
        "type": "project",
        "organization": "KernelOrg",
        "description": "Very advanced low-level programming.",
        "required_skills": [
            {"name": "Rust", "min_level": 5},
            {"name": "C++", "min_level": 4},
        ],
        "difficulty": "advanced",
        "mode": "remote",
        "status": "open",
        "deadline": (now + timedelta(days=20)).isoformat(),
        "created_at": now,
        "updated_at": now,
    }

    db.opportunities.insert_many([opp1, opp2, opp3, opp4])

    payload = {
        "skills": [{"name": "Python", "level": 3}],
        "missing_skills": ["Docker"],
        "developing_skills": [],
        "limit": 10,
    }

    res = client.post(
        "/api/opportunities/match",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    matches = data["data"]

    # Expired and closed must NOT appear
    titles = [m["opportunity"]["title"] for m in matches]
    assert "Expired Hackathon" not in titles
    assert "Closed Workshop" not in titles

    # opp1 should have high score due to meeting Python and bonus for learning Docker
    top_match = next(m for m in matches if m["opportunity"]["title"] == "Backend Python Apprentice")
    assert top_match["match_score"] >= 65.0
    assert any("Python" in s for s in top_match["matched_skills"])
    assert any("Docker" in s for s in top_match["skills_to_learn"])
    assert "targets your career gap skills" in top_match["reason"]

    # opp4 should be scored lower due to severe penalties
    hard_match = next(m for m in matches if m["opportunity"]["title"] == "Senior Rust Kernel Engineer")
    assert hard_match["match_score"] < top_match["match_score"]


def test_match_opportunities_type_filter(client, db):
    now = datetime.now(timezone.utc)
    db.opportunities.insert_many([
        {
            "title": "Cloud Internship",
            "type": "internship",
            "organization": "CloudLab",
            "description": "Cloud infra.",
            "required_skills": [],
            "difficulty": "beginner",
            "mode": "online",
            "status": "open",
            "deadline": None,
            "created_at": now,
            "updated_at": now,
        },
        {
            "title": "AI Hackathon",
            "type": "hackathon",
            "organization": "HackLab",
            "description": "AI hackathon.",
            "required_skills": [],
            "difficulty": "beginner",
            "mode": "online",
            "status": "open",
            "deadline": None,
            "created_at": now,
            "updated_at": now,
        },
    ])

    payload = {
        "skills": [],
        "missing_skills": [],
        "developing_skills": [],
        "types": ["internship"],
    }

    res = client.post(
        "/api/opportunities/match",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert all(m["opportunity"]["type"] == "internship" for m in data["data"])


def test_match_opportunities_auth_key(app, client):
    # Configure shared key
    app.config["INTER_SERVICE_KEY"] = "super-secret-key-123"

    payload = {
        "skills": [{"name": "python", "level": 2}],
        "missing_skills": [],
        "developing_skills": [],
    }

    # 1. Missing header -> 401
    res = client.post(
        "/api/opportunities/match",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "UNAUTHORIZED"

    # 2. Wrong key -> 401
    res = client.post(
        "/api/opportunities/match",
        data=json.dumps(payload),
        headers={"X-Service-Key": "wrong-key"},
        content_type="application/json",
    )
    assert res.status_code == 401

    # 3. Correct key -> 200
    res = client.post(
        "/api/opportunities/match",
        data=json.dumps(payload),
        headers={"X-Service-Key": "super-secret-key-123"},
        content_type="application/json",
    )
    assert res.status_code == 200

    # Cleanup config
    app.config["INTER_SERVICE_KEY"] = None
