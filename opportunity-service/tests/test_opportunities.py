"""Unit and integration tests for opportunity-service endpoints."""

import json


def test_create_opportunity_success(client):
    payload = {
        "title": "Full Stack Open Source Sprint",
        "type": "project",
        "organization": "OpenSource Foundation",
        "description": "Contribute to web infrastructure tools.",
        "required_skills": [
            {"name": "react", "min_level": 3},
            {"name": "node.js", "min_level": 2},
        ],
        "difficulty": "intermediate",
        "mode": "online",
        "apply_url": "https://example.com/oss-sprint",
        "tags": ["web", "react", "open-source"],
        "status": "open",
    }
    response = client.post(
        "/api/opportunities",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Full Stack Open Source Sprint"
    assert data["data"]["type"] == "project"
    assert "_id" in data["data"]


def test_create_opportunity_invalid(client):
    payload = {
        "title": "Short",
        "type": "invalid_type",  # Must be project, hackathon, internship, workshop
        "difficulty": "super_hard",
    }
    response = client.post(
        "/api/opportunities",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code in [400, 422]
    data = response.get_json()
    assert data["success"] is False


def test_get_opportunities_list(client, sample_opportunity):
    response = client.get("/api/opportunities")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert "pagination" in data
    assert data["pagination"]["total"] >= 1


def test_get_opportunities_filters(client, sample_opportunity):
    # Filter by type
    res = client.get("/api/opportunities?type=internship")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

    # Filter by non-matching type
    res = client.get("/api/opportunities?type=hackathon")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 0

    # Filter by difficulty
    res = client.get("/api/opportunities?difficulty=intermediate")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

    # Filter by mode
    res = client.get("/api/opportunities?mode=hybrid")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

    # Filter by skill
    res = client.get("/api/opportunities?skill=python")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_opportunity_by_id(client, sample_opportunity):
    opp_id = sample_opportunity["_id"]
    response = client.get(f"/api/opportunities/{opp_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["_id"] == opp_id


def test_get_opportunity_not_found(client):
    response = client.get("/api/opportunities/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False


def test_get_opportunity_invalid_id(client):
    response = client.get("/api/opportunities/invalid-id")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_update_opportunity(client, sample_opportunity):
    opp_id = sample_opportunity["_id"]
    payload = {"status": "closed", "stipend": "₹60,000 / month"}
    response = client.put(
        f"/api/opportunities/{opp_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "closed"
    assert data["data"]["stipend"] == "₹60,000 / month"


def test_delete_opportunity(client, sample_opportunity):
    opp_id = sample_opportunity["_id"]
    response = client.delete(f"/api/opportunities/{opp_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    # Verify 404
    res = client.get(f"/api/opportunities/{opp_id}")
    assert res.status_code == 404


def test_opportunity_stats(client, sample_opportunity):
    response = client.get("/api/opportunities/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    stats = data["data"]
    assert stats["total"] >= 1
    assert "by_type" in stats
    assert "by_difficulty" in stats
    assert "by_mode" in stats
    assert "by_status" in stats
    assert stats["by_type"].get("internship", 0) >= 1


def test_health_check(client):
    res1 = client.get("/api/health")
    assert res1.status_code == 200
    assert res1.get_json()["data"]["service"] == "opportunity-service"

    res2 = client.get("/health")
    assert res2.status_code == 200
    assert res2.get_json()["data"]["database"] == "connected"
