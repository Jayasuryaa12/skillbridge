"""Unit and integration tests for career endpoints in skill-service."""

import json


def test_create_career_success(client):
    payload = {
        "title": "Cloud Architect",
        "description": "Designs scalable enterprise cloud architectures.",
        "category": "Cloud Computing",
        "required_skills": [
            {
                "name": "aws",
                "required_level": 4,
                "importance": 5,
                "prerequisites": [],
                "category": "Cloud",
            }
        ],
    }
    response = client.post(
        "/api/careers",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Cloud Architect"
    assert data["data"]["slug"] == "cloud-architect"
    assert len(data["data"]["required_skills"]) == 1


def test_create_career_duplicate_slug(client, sample_career):
    payload = {
        "title": sample_career["title"],
        "slug": sample_career["slug"],
        "description": "Another description with sufficient length",
        "category": "Engineering",
        "required_skills": [
            {
                "name": "python",
                "required_level": 3,
                "importance": 4,
                "category": "Backend",
                "prerequisites": [],
            }
        ],
    }
    response = client.post(
        "/api/careers",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["success"] is False


def test_get_careers_list(client, sample_career):
    response = client.get("/api/careers")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert "pagination" in data


def test_get_careers_filter_category(client, sample_career):
    res = client.get("/api/careers?category=Software Engineering")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

    res = client.get("/api/careers?category=Marketing")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 0


def test_get_career_by_id(client, sample_career):
    career_id = sample_career["_id"]
    response = client.get(f"/api/careers/{career_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["_id"] == career_id


def test_get_career_not_found(client):
    response = client.get("/api/careers/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False


def test_update_career(client, sample_career):
    career_id = sample_career["_id"]
    payload = {"description": "Updated career description"}
    response = client.put(
        f"/api/careers/{career_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["description"] == "Updated career description"


def test_delete_career(client, sample_career):
    career_id = sample_career["_id"]
    response = client.delete(f"/api/careers/{career_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    res = client.get(f"/api/careers/{career_id}")
    assert res.status_code == 404
