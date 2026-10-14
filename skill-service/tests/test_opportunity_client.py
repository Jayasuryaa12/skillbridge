"""Unit tests for the OpportunityClient integration layer."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from clients.opportunity_client import (
    OpportunityClient,
    OpportunityInvalidResponseError,
    OpportunityServiceUnavailableError,
    OpportunityUnauthorizedError,
)


def test_client_init_and_headers():
    client = OpportunityClient(
        base_url="http://mock-service:5002/",
        service_key="secret123",
        timeout=(2.0, 5.0),
    )
    assert client.base_url == "http://mock-service:5002"
    assert client.timeout == (2.0, 5.0)
    assert client.session.headers["X-Service-Key"] == "secret123"
    assert client.session.headers["Content-Type"] == "application/json"


def test_match_opportunities_success():
    client = OpportunityClient(base_url="http://test:5002")

    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "success": True,
        "data": [
            {
                "opportunity": {"title": "AI Intern"},
                "match_score": 88.5,
                "matched_skills": ["Python (Lv. 3)"],
                "skills_to_learn": ["Docker"],
                "reason": "Good match",
            }
        ],
    }

    with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
        results = client.match_opportunities(
            skills=[{"name": "Python", "level": 3}],
            missing_skills=["Docker"],
            developing_skills=[],
            limit=5,
        )

        assert len(results) == 1
        assert results[0]["match_score"] == 88.5
        mock_req.assert_called_once()
        args, kwargs = mock_req.call_args
        assert kwargs["json"]["limit"] == 5
        assert kwargs["json"]["skills"] == [{"name": "Python", "level": 3}]


def test_client_timeout_raises_unavailable():
    client = OpportunityClient(base_url="http://test:5002")

    with patch.object(client.session, "request", side_effect=requests.Timeout("Connection timed out")):
        with pytest.raises(OpportunityServiceUnavailableError) as exc_info:
            client.match_opportunities([], [], [])
        assert "unavailable" in str(exc_info.value).lower()


def test_client_connection_error_raises_unavailable():
    client = OpportunityClient(base_url="http://test:5002")

    with patch.object(client.session, "request", side_effect=requests.ConnectionError("Connection refused")):
        with pytest.raises(OpportunityServiceUnavailableError):
            client.get_opportunity_stats()


def test_client_500_status_raises_unavailable():
    client = OpportunityClient(base_url="http://test:5002")

    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.ok = False

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(OpportunityServiceUnavailableError):
            client.match_opportunities([], [], [])


def test_client_malformed_json_raises_invalid_response():
    client = OpportunityClient(base_url="http://test:5002")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True
    mock_resp.json.side_effect = ValueError("Invalid JSON in body")

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(OpportunityInvalidResponseError):
            client.match_opportunities([], [], [])


def test_client_401_raises_unauthorized():
    client = OpportunityClient(base_url="http://test:5002")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.ok = False

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(OpportunityUnauthorizedError):
            client.match_opportunities([], [], [])


def test_client_check_health_reachable():
    client = OpportunityClient(base_url="http://test:5002")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True
    mock_resp.json.return_value = {
        "success": True,
        "data": {"status": "healthy", "service": "opportunity-service"},
    }

    with patch.object(client.session, "request", return_value=mock_resp):
        res = client.check_health()
        assert res["reachable"] is True
        assert res["status"] == "healthy"
        assert res["latency_ms"] >= 0


def test_client_check_health_unreachable():
    client = OpportunityClient(base_url="http://test:5002")

    with patch.object(client.session, "request", side_effect=requests.ConnectionError("Offline")):
        res = client.check_health()
        assert res["reachable"] is False
        assert res["status"] == "unavailable"
