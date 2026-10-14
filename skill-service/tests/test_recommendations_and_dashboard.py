"""Integration tests for recommendations, dashboard, and system status endpoints."""

from unittest.mock import patch

from clients.opportunity_client import (
    OpportunityInvalidResponseError,
    OpportunityServiceUnavailableError,
)


def test_recommendations_success(client, sample_student, sample_career):
    mock_matches = [
        {
            "opportunity": {
                "_id": "opp123",
                "title": "Backend Engineering Intern",
                "type": "internship",
                "organization": "SaaS Co",
            },
            "match_score": 82.0,
            "matched_skills": ["python (Lv. 2)"],
            "skills_to_learn": ["docker"],
            "reason": "Matches python; opportunity to learn docker.",
        }
    ]

    with patch("clients.opportunity_client.OpportunityClient.match_opportunities", return_value=mock_matches):
        res = client.get(f"/api/students/{sample_student['_id']}/recommendations")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

        payload = data["data"]
        assert payload["student"]["_id"] == sample_student["_id"]
        assert payload["career"]["_id"] == sample_career["_id"]
        assert payload["skill_gap_summary"]["readiness_score"] > 0
        assert len(payload["recommendations"]) == 1
        assert payload["recommendations"][0]["match_score"] == 82.0
        assert payload["opportunity_service"]["status"] == "available"


def test_recommendations_graceful_degradation_when_service_down(client, sample_student, sample_career):
    with patch(
        "clients.opportunity_client.OpportunityClient.match_opportunities",
        side_effect=OpportunityServiceUnavailableError("Connection refused to opportunity service"),
    ):
        res = client.get(f"/api/students/{sample_student['_id']}/recommendations")
        # Returns 200 with local gap analysis intact and empty recommendations + status note
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

        payload = data["data"]
        assert payload["student"]["_id"] == sample_student["_id"]
        assert payload["skill_gap_summary"]["readiness_score"] > 0
        assert payload["recommendations"] == []
        assert payload["opportunity_service"]["status"] == "unavailable"


def test_recommendations_upstream_invalid_response_gives_502(client, sample_student, sample_career):
    with patch(
        "clients.opportunity_client.OpportunityClient.match_opportunities",
        side_effect=OpportunityInvalidResponseError("Malformed JSON upstream"),
    ):
        res = client.get(f"/api/students/{sample_student['_id']}/recommendations")
        assert res.status_code == 502
        data = res.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == "UPSTREAM_INVALID_RESPONSE"


def test_dashboard_success(client, sample_student, sample_career, db):
    # Seed a roadmap for the student so roadmap_progress_percentage is computed
    db.roadmaps.insert_one({
        "student_id": sample_student["_id"],
        "career_id": sample_career["_id"],
        "stages": [
            {"order": 1, "skill": "python", "status": "completed"},
            {"order": 2, "skill": "docker", "status": "in_progress"},
        ],
    })

    mock_matches = [{"opportunity": {"title": "Fullstack Intern"}, "match_score": 75.0}]
    mock_stats = {"total": 32, "by_type": {"internship": 10}}

    with patch("clients.opportunity_client.OpportunityClient.match_opportunities", return_value=mock_matches), \
         patch("clients.opportunity_client.OpportunityClient.get_opportunity_stats", return_value=mock_stats):

        res = client.get(f"/api/students/{sample_student['_id']}/dashboard")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

        payload = data["data"]
        assert "readiness_score" in payload
        assert "category_scores" in payload
        assert payload["skill_counts"]["matched"] >= 0
        assert len(payload["top_priority_skills"]) <= 5
        # 1 out of 2 completed stages = 50.0%
        assert payload["roadmap_progress_percentage"] == 50.0
        assert len(payload["top_recommendations"]) == 1
        assert payload["opportunity_stats"]["total"] == 32
        assert payload["opportunity_service"]["status"] == "available"


def test_dashboard_graceful_degradation(client, sample_student, sample_career):
    with patch(
        "clients.opportunity_client.OpportunityClient.match_opportunities",
        side_effect=OpportunityServiceUnavailableError("Down"),
    ):
        res = client.get(f"/api/students/{sample_student['_id']}/dashboard")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

        payload = data["data"]
        assert payload["readiness_score"] > 0
        assert payload["top_recommendations"] == []
        assert payload["opportunity_stats"] is None
        assert payload["opportunity_service"]["status"] == "unavailable"


def test_system_status_endpoint(client):
    mock_health = {
        "status": "healthy",
        "reachable": True,
        "latency_ms": 12.5,
        "data": {"service": "opportunity-service"},
    }

    with patch("clients.opportunity_client.OpportunityClient.check_health", return_value=mock_health):
        res = client.get("/api/system/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

        status_data = data["data"]
        assert status_data["overall_status"] == "healthy"
        assert status_data["skill_service"]["status"] == "healthy"
        assert status_data["opportunity_service"]["reachable"] is True
        assert status_data["opportunity_service"]["latency_ms"] == 12.5
