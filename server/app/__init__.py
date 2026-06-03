"""Application factory for LaunchBot."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.api import api_bp
from app.routes.spa import spa_bp
from app.services.thread_service import ensure_database


def create_app(config_object=Config) -> Flask:
    """Create and configure the Flask app."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(config_object)

    # CORS is helpful during local development when Vite runs on port 5173.
    # In production, Flask serves the built React app and CORS is not needed by the browser.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://127.0.0.1:5173", "http://localhost:5173"]
            }
        },
    )

    ensure_database(app.config["DATABASE_PATH"])

    app.register_blueprint(api_bp)
    app.register_blueprint(spa_bp)

    return app
