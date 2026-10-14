"""
Skill-Service — Flask Application Factory
==========================================
Usage:
    from app import create_app
    app = create_app()          # production / development
    app = create_app(TestingConfig)   # tests
"""

import logging
import time
from typing import Optional

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from app.config import Config, get_config
from app.db import init_db


def create_app(config_class: Optional[type[Config]] = None) -> Flask:
    """
    Flask application factory.

    Parameters
    ----------
    config_class : Config subclass (optional).
        Defaults to the class resolved from ``FLASK_ENV`` env var.

    Returns
    -------
    Configured Flask application instance.
    """
    app = Flask(__name__)

    # ── Load configuration ─────────────────────────────────────────────────
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # ── Logging ────────────────────────────────────────────────────────────
    log_format = "%(asctime)s [%(levelname)s] %(name)s [service=skill-service]: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── CORS ───────────────────────────────────────────────────────────────
    allowed_origins = app.config.get("ALLOWED_ORIGINS", app.config.get("CORS_ORIGINS", ["*"]))
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    # ── Database ───────────────────────────────────────────────────────────
    init_db(app)

    # ── Request logging middleware ─────────────────────────────────────────
    @app.before_request
    def _before() -> None:
        g.start_time = time.perf_counter()

    @app.after_request
    def _after(response):
        duration_ms = round((time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000, 1)
        app.logger.info(
            "HTTP %s %s status=%d duration_ms=%s ip=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        return response

    # ── Blueprints ─────────────────────────────────────────────────────────
    from app.routes.careers import careers_bp
    from app.routes.health import health_bp
    from app.routes.roadmaps import roadmaps_bp
    from app.routes.students import students_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(students_bp, url_prefix="/api")
    app.register_blueprint(careers_bp, url_prefix="/api")
    app.register_blueprint(roadmaps_bp, url_prefix="/api")

    # ── Swagger / OpenAPI Documentation ────────────────────────────────────
    from flasgger import Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "SkillBridge — Skill Service API",
            "description": "Interactive API specification for students, skills, careers, roadmaps, and inter-service recommendations.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http", "https"],
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # ── Global error handlers ──────────────────────────────────────────────
    _register_error_handlers(app)

    # Add root redirect to /apidocs for convenience
    @app.route("/apidocs")
    def apidocs_redirect():
        from flask import redirect
        return redirect("/apidocs/")

    app.logger.info("✅ Skill-service started (env=%s)", app.config.get("FLASK_ENV", "development"))
    return app


def _register_error_handlers(app: Flask) -> None:
    """Register application-wide JSON error responses."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": {"code": "BAD_REQUEST", "message": str(e.description), "details": None}}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "The requested resource was not found.", "details": None}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": {"code": "METHOD_NOT_ALLOWED", "message": str(e.description), "details": None}}), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"success": False, "error": {"code": "UNPROCESSABLE", "message": str(e.description), "details": None}}), 422

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled exception: %s", e)
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "details": None}}), 500
