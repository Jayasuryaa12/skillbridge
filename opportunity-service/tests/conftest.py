"""Pytest configuration and shared fixtures for opportunity-service tests."""

import mongomock
import pytest

from app import create_app
import app.db as app_db
from app.config import TestingConfig


@pytest.fixture(scope="session")
def mock_mongo_client():
    """Create a session-wide mongomock MongoClient instance."""
    return mongomock.MongoClient()


@pytest.fixture
def app(monkeypatch, mock_mongo_client):
    """Create a test Flask application with mocked MongoDB."""
    monkeypatch.setattr(app_db, "MongoClient", lambda *args, **kwargs: mock_mongo_client)
    monkeypatch.setattr(app_db, "_client", mock_mongo_client)

    application = create_app(TestingConfig)
    application.config["TESTING"] = True
    yield application


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def db(mock_mongo_client):
    """Direct reference to the mock database for assertions and cleanup."""
    database = mock_mongo_client[TestingConfig.DB_NAME]
    yield database
    # Clean up opportunities collection between tests
    database.opportunities.drop()


@pytest.fixture
def sample_opportunity(db):
    """Seed a sample opportunity for tests."""
    from datetime import datetime, timezone
    doc = {
        "title": "Machine Learning Research Intern",
        "type": "internship",
        "organization": "AI Research Lab",
        "description": "Work on state-of-the-art vision models.",
        "required_skills": [
            {"name": "python", "min_level": 3},
            {"name": "pytorch", "min_level": 3},
        ],
        "difficulty": "intermediate",
        "mode": "hybrid",
        "location": "Bengaluru",
        "start_date": "2026-06-01T00:00:00Z",
        "deadline": "2026-05-15T23:59:59Z",
        "duration": "6 months",
        "stipend": "₹50,000 / month",
        "prize": None,
        "apply_url": "https://example.com/apply",
        "tags": ["ml", "pytorch", "research"],
        "status": "open",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    res = db.opportunities.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc
