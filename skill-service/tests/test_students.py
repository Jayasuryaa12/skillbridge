"""Unit and integration tests for student endpoints in skill-service."""

import json


def test_create_student_success(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "college": "Stanford",
        "department": "Electrical Engineering",
        "year": 2,
        "skills": [{"name": "python", "level": 3}],
    }
    response = client.post(
        "/api/students",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Jane Doe"
    assert data["data"]["email"] == "jane.doe@example.com"
    assert len(data["data"]["skills"]) == 1
    assert "_id" in data["data"]


def test_create_student_invalid_payload(client):
    payload = {
        "name": "",
        "email": "invalid-email",
        "year": 5,  # Valid range is 1-4
    }
    response = client.post(
        "/api/students",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code in [400, 422]
    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


def test_create_student_duplicate_email(client, sample_student):
    payload = {
        "name": "Another Name",
        "email": sample_student["email"],
        "college": "MIT",
        "department": "Computer Science",
        "year": 1,
    }
    response = client.post(
        "/api/students",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["success"] is False


def test_get_students_list(client, sample_student):
    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert "pagination" in data
    assert data["pagination"]["total"] >= 1


def test_get_students_filtered(client, sample_student):
    # Match department
    res = client.get("/api/students?department=Computer Science")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

    # Non-matching department
    res = client.get("/api/students?department=Mechanical")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 0

    # Match year
    res = client.get("/api/students?year=3")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_student_by_id(client, sample_student):
    student_id = sample_student["_id"]
    response = client.get(f"/api/students/{student_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["_id"] == student_id


def test_get_student_not_found(client):
    response = client.get("/api/students/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False


def test_get_student_invalid_id(client):
    response = client.get("/api/students/not-a-valid-id")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_update_student(client, sample_student):
    student_id = sample_student["_id"]
    payload = {"year": 4, "college": "Harvard"}
    response = client.put(
        f"/api/students/{student_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["year"] == 4
    assert data["data"]["college"] == "Harvard"


def test_delete_student(client, sample_student):
    student_id = sample_student["_id"]
    response = client.delete(f"/api/students/{student_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    # Confirm it's gone
    res = client.get(f"/api/students/{student_id}")
    assert res.status_code == 404


def test_add_skill_to_student(client, sample_student):
    student_id = sample_student["_id"]
    payload = {"name": "react", "level": 4}
    response = client.post(
        f"/api/students/{student_id}/skills",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data["success"] is True
    skill_names = [s["name"] for s in data["data"]["skills"]]
    assert "react" in skill_names


def test_update_student_skill(client, sample_student):
    student_id = sample_student["_id"]
    payload = {"level": 5}
    response = client.put(
        f"/api/students/{student_id}/skills/python",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    python_skill = next(s for s in data["data"]["skills"] if s["name"] == "python")
    assert python_skill["level"] == 5


def test_delete_student_skill(client, sample_student):
    student_id = sample_student["_id"]
    response = client.delete(f"/api/students/{student_id}/skills/python")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    skill_names = [s["name"] for s in data["data"]["skills"]]
    assert "python" not in skill_names
