"""
PhishGuard - Phishing Website Detection System
Flask Application Factory & Route Definitions
"""
import os
import io
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config, load_settings, save_settings
from database import (
    init_db, insert_scan, get_scan, list_scans,
    delete_scan, clear_all_scans, get_statistics,
    insert_file_scan, get_file_scan, list_file_scans,
    delete_file_scan, clear_all_file_scans, get_file_statistics
)
from detector import PhishDetector
from model_manager import get_model_metadata
from password_analyzer import analyze_password, generate_secure_password
from file_scanner import scan_file_buffer, check_clamav_availability
from report_generator import generate_file_scan_pdf

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

    @app.route("/scanner")
    def scanner():
        """Dedicated Phishing URL Threat Scanner Page."""
        return render_template("scanner.html")

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/analytics")
    def analytics():
        stats = get_statistics()
        return render_template("analytics.html", stats=stats)

    @app.route("/password-analyzer")
    def password_analyzer():
        """Password Security & Entropy Analyzer Page."""
        return render_template("password_analyzer.html")

    @app.route("/file-scanner")
    def file_scanner():
        """File Virus & Anti-Malware Threat Scanner Page."""
        settings = load_settings()
        clam_info = check_clamav_availability(settings.get("clamav_path"))
        max_mb = settings.get("max_upload_size_mb", 16)
        return render_template(
            "file_scanner.html",
            clamav_available=clam_info["available"],
            clamav_path=clam_info["path"],
            max_file_size_mb=max_mb
        )

    @app.route("/file-scanner/<int:file_id>")
    def file_result(file_id):
        """Detailed File Threat Assessment Result Dossier."""
        scan = get_file_scan(file_id)
        if not scan:
            return render_template("dashboard.html", stats=get_statistics(), model_meta=get_model_metadata()), 404

        meta = scan.get("metadata", {})
        scan_view = {
            "id": scan["id"],
            "filename": scan["filename"],
            "sha256": scan["file_hash"],
            "sha1": meta.get("sha1", "-"),
            "md5": meta.get("md5", "-"),
            "file_size": scan["file_size"],
            "size_bytes": scan["file_size"],
            "mime_type": scan["mime_type"],
            "extension": os.path.splitext(scan["filename"])[1],
            "status": scan["status"],
            "risk_score": meta.get("risk_score", 15 if scan["status"] == "Limited Analysis" else (95 if scan["status"] == "Malicious" else (65 if scan["status"] == "Suspicious" else 5))),
            "threat_name": scan["threat_name"],
            "engine": scan["engine_used"],
            "engine_used": scan["engine_used"],
            "antivirus_status": meta.get("antivirus_status", "Offline" if "Unavailable" in scan["engine_used"] or "Offline" in scan["engine_used"] else "Active"),
            "clam_info": meta.get("clam_info") or check_clamav_availability(),
            "entropy": meta.get("entropy", 0.0),
            "entropy_explanation": meta.get("entropy_explanation", ""),
            "is_naturally_compressed": meta.get("is_naturally_compressed", False),
            "timestamp": scan["scan_timestamp"],
            "scan_timestamp": scan["scan_timestamp"],
            "threats": scan.get("threat_indicators", []),
            "structured_findings": meta.get("structured_findings", []),
            "recommendations": scan.get("recommendations", [])
        }
        return render_template("file_result.html", file_scan=scan_view)

    @app.route("/settings")
    def settings():
        """Security Settings and Engine Parameters Page."""
        curr_settings = load_settings()
        clam_info = check_clamav_availability(curr_settings.get("clamav_path"))
        url_stats = get_statistics()
        file_stats = get_file_statistics()

        view_settings = {
            "max_file_size_mb": curr_settings.get("max_upload_size_mb", 16),
            "clamav_path": curr_settings.get("clamav_path", "clamscan"),
            "enable_heuristics": curr_settings.get("enable_heuristics", True)
        }

        return render_template(
            "settings.html",
            settings=view_settings,
            clamav_available=clam_info["available"],
            clamav_resolved_path=clam_info["path"] or "clamscan",
            url_scans_count=url_stats.get("total_scans", 0),
            file_scans_count=file_stats.get("total_files", 0)
        )

    # ==========================================
    # URL Scanner REST API Routes
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

    # ==========================================
    # Password Analyzer REST API Routes
    # ==========================================

    @app.route("/api/password/analyze", methods=["POST"])
    @limiter.limit("120 per minute")
    def api_analyze_password():
        """
        Evaluate password entropy and security characteristics.
        Strict zero-storage policy: input is evaluated in volatile memory and never persisted.
        """
        data = request.get_json(silent=True) or {}
        password = data.get("password", "")

        result = analyze_password(password)
        # Discard password reference immediately
        del password
        del data

        return jsonify({"status": "success", "data": result}), 200

    @app.route("/api/password/generate", methods=["GET", "POST"])
    def api_generate_password():
        """Generate a cryptographically strong random password."""
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args

        try:
            length = int(data.get("length", 16))
        except (ValueError, TypeError):
            length = 16

        def _to_bool(val, default=True):
            if val is None:
                return default
            if isinstance(val, bool):
                return val
            return str(val).lower() in ("true", "1", "yes")

        upper = _to_bool(data.get("include_uppercase", True))
        digits = _to_bool(data.get("include_digits", True))
        symbols = _to_bool(data.get("include_symbols", True))

        pwd = generate_secure_password(
            length=length,
            include_uppercase=upper,
            include_digits=digits,
            include_symbols=symbols
        )

        return jsonify({
            "status": "success",
            "data": {
                "password": pwd,
                "length": len(pwd)
            }
        }), 200

    # ==========================================
    # File Virus Scanner REST API Routes
    # ==========================================

    @app.route("/api/file/scan", methods=["POST"])
    @limiter.limit("30 per minute")
    def api_file_scan():
        """Accept an uploaded file, run static heuristics + ClamAV scan, and store audit record."""
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file part in multipart request."}), 400

        file_storage = request.files["file"]
        if not file_storage or file_storage.filename.strip() == "":
            return jsonify({"status": "error", "message": "No file selected."}), 400

        settings = load_settings()
        clamav_path = settings.get("clamav_path")

        try:
            scan_result = scan_file_buffer(file_storage, custom_clamav_path=clamav_path)

            metadata = {
                "original_filename": scan_result.get("original_filename"),
                "sha1": scan_result.get("sha1"),
                "md5": scan_result.get("md5"),
                "entropy": scan_result.get("entropy"),
                "risk_score": scan_result.get("risk_score", 15),
                "antivirus_status": scan_result.get("antivirus_status"),
                "clam_info": scan_result.get("clam_info"),
                "entropy_explanation": scan_result.get("entropy_explanation"),
                "is_naturally_compressed": scan_result.get("is_naturally_compressed", False),
                "structured_findings": scan_result.get("structured_findings", []),
                "threat_indicators": scan_result.get("threat_indicators", []),
                "is_executable": scan_result.get("is_executable", False),
                "is_spoofed": scan_result.get("is_spoofed", False),
                "has_double_ext": scan_result.get("has_double_ext", False)
            }

            file_id = insert_file_scan(
                filename=scan_result["filename"],
                file_hash=scan_result["sha256"],
                file_size=scan_result["file_size"],
                mime_type=scan_result["mime_type"],
                status=scan_result["status"],
                engine_used=scan_result["engine_used"],
                threat_name=scan_result["threat_name"],
                metadata=metadata,
                recommendations=scan_result.get("recommendations", [])
            )

            scan_result["id"] = file_id
            return jsonify({"status": "success", "data": scan_result}), 200

        except ValueError as ve:
            return jsonify({"status": "error", "message": str(ve)}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"File scan error: {str(e)}"}), 500

    @app.route("/api/file/history", methods=["GET"])
    def api_file_history():
        """Retrieve paginated file scan records."""
        try:
            limit = min(int(request.args.get("limit", 20)), 100)
            offset = max(int(request.args.get("offset", 0)), 0)
            search = request.args.get("search", "").strip()
            status = request.args.get("status", "").strip()

            scans, total_count = list_file_scans(
                limit=limit,
                offset=offset,
                search=search,
                status=status
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

    @app.route("/api/file/history/<int:file_id>", methods=["GET"])
    def api_get_file_scan(file_id):
        """Retrieve a single file scan audit record."""
        scan = get_file_scan(file_id)
        if not scan:
            return jsonify({"status": "error", "message": f"File scan ID {file_id} not found."}), 404
        return jsonify({"status": "success", "data": scan}), 200

    @app.route("/api/file/history/<int:file_id>", methods=["DELETE"])
    def api_delete_file_scan(file_id):
        """Delete an individual file scan audit record."""
        success = delete_file_scan(file_id)
        if not success:
            return jsonify({"status": "error", "message": f"File scan ID {file_id} not found."}), 404
        return jsonify({"status": "success", "message": f"File scan ID {file_id} deleted."}), 200

    @app.route("/api/file/history/clear", methods=["POST"])
    def api_clear_file_history():
        """Clear all file scan logs."""
        deleted = clear_all_file_scans()
        return jsonify({"status": "success", "message": f"Cleared {deleted} file scan records."}), 200

    @app.route("/api/file/report/<int:file_id>", methods=["GET"])
    def api_file_report(file_id):
        """Generate and stream a downloadable PDF security audit report."""
        scan = get_file_scan(file_id)
        if not scan:
            return jsonify({"status": "error", "message": f"File scan ID {file_id} not found."}), 404

        meta = scan.get("metadata") or {}
        scan_dict = {
            "id": scan["id"],
            "filename": scan["filename"],
            "sha256": scan["file_hash"],
            "sha1": meta.get("sha1", "-"),
            "md5": meta.get("md5", "-"),
            "file_size": scan["file_size"],
            "mime_type": scan["mime_type"],
            "status": scan["status"],
            "threat_name": scan["threat_name"],
            "engine_used": scan["engine_used"],
            "scan_timestamp": scan["scan_timestamp"],
            "threat_indicators": scan.get("threat_indicators", []),
            "recommendations": scan.get("recommendations", []),
            "risk_score": meta.get("risk_score", 0),
            "entropy": meta.get("entropy", "N/A"),
            "entropy_assessment": meta.get("entropy_assessment", "Normal")
        }

        try:
            pdf_bytes = generate_file_scan_pdf(scan_dict)
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"phishguard_file_report_{file_id}.pdf"
            )
        except Exception as e:
            return jsonify({"status": "error", "message": f"PDF report generation failed: {str(e)}"}), 500

    # ==========================================
    # Settings REST API Routes
    # ==========================================

    @app.route("/api/settings", methods=["GET", "POST"])
    def api_settings():
        """Retrieve or update system settings."""
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            settings = load_settings()

            if "max_file_size_mb" in data:
                try:
                    val = int(data["max_file_size_mb"])
                    if 1 <= val <= 100:
                        settings["max_upload_size_mb"] = val
                        Config.MAX_CONTENT_LENGTH = val * 1024 * 1024
                except (ValueError, TypeError):
                    pass

            if "clamav_path" in data:
                settings["clamav_path"] = str(data["clamav_path"]).strip() or "clamscan"

            if "enable_heuristics" in data:
                settings["enable_heuristics"] = bool(data["enable_heuristics"])

            save_settings(settings)
            return jsonify({"status": "success", "message": "Settings updated successfully.", "data": settings}), 200

        return jsonify({"status": "success", "data": load_settings()}), 200

    # ==========================================
    # Error Handlers
    # ==========================================

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
