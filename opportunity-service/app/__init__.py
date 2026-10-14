"""
Opportunity-Service — Flask Application Factory
"""

import logging
import time
from typing import Optional

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from app.config import Config, get_config
from app.db import init_db


def create_app(config_class: Optional[type[Config]] = None) -> Flask:
    """Flask application factory for opportunity-service."""
    app = Flask(__name__)

    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.DEBUG if app.config["DEBUG"] else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    init_db(app)

    @app.before_request
    def _before() -> None:
        g.start_time = time.perf_counter()

    @app.after_request
    def _after(response):
        duration_ms = round(
            (time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000, 1
        )
        app.logger.info(
            "%s %s → %d  (%s ms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

    from app.routes.health import health_bp
    from app.routes.opportunities import opportunities_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(opportunities_bp, url_prefix="/api")

    _register_error_handlers(app)

    app.logger.info("✅ Opportunity-service started")
    return app


def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": {"code": "BAD_REQUEST", "message": str(e.description), "details": None}}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "The requested resource was not found.", "details": None}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": {"code": "METHOD_NOT_ALLOWED", "message": str(e.description), "details": None}}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled exception: %s", e)
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "details": None}}), 500
