"""Pytest configuration and shared fixtures for skill-service tests."""

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
    # Monkeypatch pymongo.MongoClient in app.db so init_db and _get_client use mongomock
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
    """Direct reference to the mock database for assertions and setup."""
    database = mock_mongo_client[TestingConfig.DB_NAME]
    yield database
    # Clean up collections between tests
    database.students.drop()
    database.careers.drop()
    database.roadmaps.drop()


@pytest.fixture
def sample_career(db):
    """Seed a sample career for tests."""
    from datetime import datetime, timezone
    doc = {
        "title": "Backend Engineer",
        "slug": "backend-engineer",
        "description": "Designs and builds robust APIs and databases.",
        "category": "Software Engineering",
        "required_skills": [
            {
                "name": "python",
                "required_level": 4,
                "importance": 5,
                "prerequisites": [],
                "category": "Programming Languages",
            },
            {
                "name": "flask",
                "required_level": 3,
                "importance": 4,
                "prerequisites": ["python"],
                "category": "Frameworks",
            },
            {
                "name": "docker",
                "required_level": 3,
                "importance": 3,
                "prerequisites": [],
                "category": "DevOps",
            },
        ],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    res = db.careers.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc


@pytest.fixture
def sample_student(db, sample_career):
    """Seed a sample student for tests."""
    from datetime import datetime, timezone
    doc = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "college": "MIT",
        "department": "Computer Science",
        "year": 3,
        "career_goal": sample_career["_id"],
        "skills": [
            {
                "name": "python",
                "level": 2,
                "updated_at": datetime.now(timezone.utc),
            }
        ],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    res = db.students.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc
