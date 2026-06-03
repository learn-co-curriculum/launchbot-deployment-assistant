"""Routes for serving the React single-page application."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from jinja2 import TemplateNotFound


spa_bp = Blueprint("spa", __name__)


@spa_bp.get("/")
@spa_bp.get("/<path:path>")
def serve_react_app(path: str = ""):
    """Serve React for non-API routes after the Vite build has been copied into Flask."""
    if path.startswith("api/"):
        return jsonify({"error": "not_found", "message": "API route not found."}), 404

    try:
        return render_template("index.html")
    except TemplateNotFound:
        return (
            jsonify(
                {
                    "message": "React build not found.",
                    "next_step": "From the client folder, run: npm run build:flask",
                    "api_health": "/api/health",
                }
            ),
            200,
        )
