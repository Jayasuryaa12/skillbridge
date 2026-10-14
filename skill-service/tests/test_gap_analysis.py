"""Unit and integration tests for Skill Gap Analysis in skill-service."""

from app.services.gap_analysis import analyze_skill_gap


def test_analyze_skill_gap_algorithm_pure():
    """Test the deterministic skill gap calculation with controlled inputs."""
    career = {
        "_id": "career123",
        "title": "Full Stack Dev",
        "required_skills": [
            {
                "name": "python",
                "required_level": 4,
                "importance": 5,
                "category": "Backend",
                "prerequisites": [],
            },
            {
                "name": "react",
                "required_level": 4,
                "importance": 4,
                "category": "Frontend",
                "prerequisites": [],
            },
            {
                "name": "docker",
                "required_level": 3,
                "importance": 3,
                "category": "DevOps",
                "prerequisites": [],
            },
        ],
    }

    # Student has:
    # - python at level 4 (MATCHED: 4/4 * 5 = 5.0)
    # - react at level 2 (DEVELOPING: 2/4 * 4 = 2.0)
    # - docker at level 0 (MISSING: 0/3 * 3 = 0.0)
    # Total weighted = 7.0
    # Total importance = 5 + 4 + 3 = 12
    # Readiness score = (7.0 / 12) * 100 = 58.33%
    student = {
        "_id": "student123",
        "skills": [
            {"name": "python", "level": 4},
            {"name": "react", "level": 2},
        ],
    }

    result = analyze_skill_gap(student, career)

    assert result["readiness_score"] == 58.33
    assert len(result["matched"]) == 1
    assert result["matched"][0]["skill"] == "python"

    assert len(result["developing"]) == 1
    assert result["developing"][0]["skill"] == "react"
    assert result["developing"][0]["gap_size"] == 2

    assert len(result["missing"]) == 1
    assert result["missing"][0]["skill"] == "docker"
    assert result["missing"][0]["gap_size"] == 3

    # Check priority list ordering: MISSING first (docker, imp 3), then DEVELOPING (react, imp 4)
    assert result["priority_list"][0]["skill"] == "docker"
    assert result["priority_list"][1]["skill"] == "react"


def test_analyze_skill_gap_endpoint(client, sample_student, sample_career):
    """Test GET /api/students/<id>/skill-gap endpoint."""
    student_id = sample_student["_id"]
    response = client.get(f"/api/students/{student_id}/skill-gap")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    analysis = data["data"]
    assert "readiness_score" in analysis
    assert "matched" in analysis
    assert "developing" in analysis
    assert "missing" in analysis
    assert "priority_list" in analysis
    assert "category_scores" in analysis


def test_analyze_skill_gap_no_career_goal(client, sample_student, db):
    """Test skill gap when student has no career goal set."""
    from bson import ObjectId
    db.students.update_one(
        {"_id": ObjectId(sample_student["_id"])},
        {"$set": {"career_goal": None}},
    )

    response = client.get(f"/api/students/{sample_student['_id']}/skill-gap")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "career" in data["error"]["message"].lower()
