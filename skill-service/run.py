# Flask application entry point for skill-service

"""
SkillBridge – Skill Service
Runs on port 5001.
Start with: python run.py (development) or gunicorn (production).
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        use_reloader=False,
    )
