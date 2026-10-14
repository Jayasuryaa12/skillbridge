"""Unit and integration tests for roadmap endpoints and topological sequencing in skill-service."""

import json


def test_generate_and_get_roadmap(client, sample_student, sample_career):
    student_id = sample_student["_id"]

    # 1. Generate roadmap
    gen_res = client.post(f"/api/students/{student_id}/roadmap/generate")
    assert gen_res.status_code in [200, 201]
    data = gen_res.get_json()
    assert data["success"] is True

    roadmap = data["data"]
    assert roadmap["student_id"] == student_id
    assert roadmap["career_id"] == sample_career["_id"]
    assert len(roadmap["stages"]) > 0

    # In sample_career, 'flask' requires 'python'.
    # Even though student has python level 2 (target 4) and flask level 0 (target 3),
    # python must appear before flask in the stages.
    stage_skills = [s["skill"].lower() for s in roadmap["stages"]]
    if "python" in stage_skills and "flask" in stage_skills:
        assert stage_skills.index("python") < stage_skills.index("flask")

    # Check resources attached
    for stage in roadmap["stages"]:
        assert len(stage["resources"]) > 0
        assert "status" in stage
        assert stage["status"] == "not_started"

    # 2. Retrieve roadmap via GET
    get_res = client.get(f"/api/students/{student_id}/roadmap")
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data["success"] is True
    assert get_data["data"]["student_id"] == student_id
    assert len(get_data["data"]["stages"]) == len(roadmap["stages"])


def test_update_roadmap_stage_status(client, sample_student, sample_career):
    student_id = sample_student["_id"]

    # Generate first
    client.post(f"/api/students/{student_id}/roadmap/generate")

    # Patch stage 1 status to in_progress
    patch_payload = {"status": "in_progress"}
    patch_res = client.patch(
        f"/api/students/{student_id}/roadmap/stages/1",
        data=json.dumps(patch_payload),
        content_type="application/json",
    )
    assert patch_res.status_code == 200
    data = patch_res.get_json()
    assert data["success"] is True

    stages = data["data"]["stages"]
    stage_1 = next(s for s in stages if s["order"] == 1)
    assert stage_1["status"] == "in_progress"

    # Invalid status
    invalid_patch = client.patch(
        f"/api/students/{student_id}/roadmap/stages/1",
        data=json.dumps({"status": "invalid_status"}),
        content_type="application/json",
    )
    assert invalid_patch.status_code in [400, 422]


def test_get_roadmap_not_generated(client, sample_student):
    student_id = sample_student["_id"]
    response = client.get(f"/api/students/{student_id}/roadmap")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
