# Flask application entry point for opportunity-service

"""
SkillBridge – Opportunity Service
Runs on port 5002.
Start with: python run.py (development) or gunicorn (production).
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=app.config.get("DEBUG", False),
    )
