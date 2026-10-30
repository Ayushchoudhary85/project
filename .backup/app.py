"""
PhishGuard - Phishing Website Detection System
Flask Application Factory & Route Definitions
"""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from database import (
    init_db, insert_scan, get_scan, list_scans,
    delete_scan, clear_all_scans, get_statistics
)
from detector import PhishDetector
from model_manager import get_model_metadata

detector = PhishDetector()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLite database
    init_db()

    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[Config.RATELIMIT_DEFAULT],
        storage_uri=Config.RATELIMIT_STORAGE_URI
    )

    # ==========================================
    # HTML Page Routes
    # ==========================================

    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        stats = get_statistics()
        model_meta = get_model_metadata()
        return render_template("dashboard.html", stats=stats, model_meta=model_meta)

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/analytics")
    def analytics():
        stats = get_statistics()
        return render_template("analytics.html", stats=stats)

    # ==========================================
    # REST API Routes
    # ==========================================

    @app.route("/api/scan", methods=["POST"])
    @limiter.limit("60 per minute")
    def api_scan():
        """Scan a submitted URL and store the result in the database."""
        data = request.get_json(silent=True)
        if not data or "url" not in data:
            return jsonify({"status": "error", "message": "Missing 'url' parameter in request body."}), 400

        url = data.get("url", "").strip()
        if not url:
            return jsonify({"status": "error", "message": "URL cannot be empty."}), 400

        if len(url) > 2048:
            return jsonify({"status": "error", "message": "URL exceeds maximum length of 2048 characters."}), 400

        try:
            result = detector.analyze_url(url)
            # Store in SQLite
            scan_id = insert_scan(
                url=result["url"],
                domain=result["domain"],
                prediction=result["prediction"],
                risk_score=result["risk_score"],
                risk_level=result["risk_level"],
                confidence=result["confidence"],
                features=result["extracted_features"],
                indicators=result["threat_indicators"]
            )
            result["id"] = scan_id
            return jsonify({"status": "success", "data": result}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/history", methods=["GET"])
    def api_history():
        """Retrieve paginated scan records with optional search and filters."""
        try:
            limit = min(int(request.args.get("limit", 20)), 100)
            offset = max(int(request.args.get("offset", 0)), 0)
            search = request.args.get("search", "").strip()
            prediction = request.args.get("prediction", "").strip()
            risk_level = request.args.get("risk_level", "").strip()

            scans, total_count = list_scans(
                limit=limit,
                offset=offset,
                search=search,
                prediction=prediction,
                risk_level=risk_level
            )
            return jsonify({
                "status": "success",
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "scans": scans
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/history/<int:scan_id>", methods=["GET"])
    def api_get_scan(scan_id):
        """Retrieve a single scan record."""
        scan = get_scan(scan_id)
        if not scan:
            return jsonify({"status": "error", "message": f"Scan ID {scan_id} not found."}), 404
        return jsonify({"status": "success", "data": scan}), 200

    @app.route("/api/history/<int:scan_id>", methods=["DELETE"])
    def api_delete_scan(scan_id):
        """Delete an individual scan record."""
        success = delete_scan(scan_id)
        if not success:
            return jsonify({"status": "error", "message": f"Scan ID {scan_id} not found or could not be deleted."}), 404
        return jsonify({"status": "success", "message": f"Scan ID {scan_id} deleted."}), 200

    @app.route("/api/history/clear", methods=["POST"])
    def api_clear_history():
        """Delete all scan history records."""
        deleted_count = clear_all_scans()
        return jsonify({"status": "success", "message": f"Cleared {deleted_count} scan records."}), 200

    @app.route("/api/statistics", methods=["GET"])
    def api_statistics():
        """Return aggregated statistics."""
        stats = get_statistics()
        return jsonify({"status": "success", "data": stats}), 200

    @app.route("/api/analytics", methods=["GET"])
    def api_analytics():
        """Return full analytics dataset for charts."""
        stats = get_statistics()
        scans, total = list_scans(limit=100)

        # Compute indicator frequency
        indicator_counts = {}
        for s in scans:
            for ind in s.get("threat_indicators", []):
                # Normalize indicator label
                key = ind.split("(")[0].strip()
                indicator_counts[key] = indicator_counts.get(key, 0) + 1

        top_indicators = sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True)[:6]

        analytics_data = {
            "statistics": stats,
            "recent_scans": scans[:10],
            "top_threat_indicators": [
                {"indicator": k, "count": v} for k, v in top_indicators
            ]
        }
        return jsonify({"status": "success", "data": analytics_data}), 200

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"status": "error", "message": f"Rate limit exceeded: {e.description}"}), 429

    @app.errorhandler(404)
    def not_found_handler(e):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "API endpoint not found."}), 404
        return render_template("dashboard.html", stats=get_statistics(), model_meta=get_model_metadata()), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Internal server error occurred."}), 500
        return "Internal Server Error", 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
