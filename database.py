"""
SQLite Database Layer for PhishGuard.
Provides parameterized thread-safe CRUD operations and aggregate statistics
for both URL Phishing Scans and File Virus Scans.
"""
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from config import Config


def get_db_connection():
    """Establish a connection to the SQLite database with row factory enabled."""
    db_path = Config.DATABASE_PATH
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    """Initialize database tables and indexes."""
    conn = get_db_connection()
    with conn:
        # 1. URL Phishing Scans Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                prediction TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                scan_timestamp TEXT NOT NULL,
                extracted_features TEXT NOT NULL,
                threat_indicators TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_domain ON scans(domain)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(scan_timestamp DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_prediction ON scans(prediction)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_risk_level ON scans(risk_level)")

        # 2. File Virus Scans Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                status TEXT NOT NULL,
                engine_used TEXT NOT NULL,
                threat_name TEXT,
                scan_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                recommendations_json TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_scans_hash ON file_scans(file_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_scans_status ON file_scans(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_scans_timestamp ON file_scans(scan_timestamp DESC)")

    conn.close()


# =========================================================================
# URL Scan Operations
# =========================================================================

def insert_scan(url: str, domain: str, prediction: str, risk_score: int,
                risk_level: str, confidence: float, features: dict,
                indicators: list) -> int:
    """Insert or update a URL scan result to prevent duplicate history records."""
    conn = get_db_connection()
    timestamp = datetime.now(timezone.utc).isoformat()
    features_json = json.dumps(features)
    indicators_json = json.dumps(indicators)

    try:
        with conn:
            cursor = conn.execute("SELECT id FROM scans WHERE url = ? ORDER BY id DESC LIMIT 1", (url,))
            existing = cursor.fetchone()
            if existing:
                scan_id = existing[0]
                conn.execute("""
                    UPDATE scans SET
                        domain = ?,
                        prediction = ?,
                        risk_score = ?,
                        risk_level = ?,
                        confidence = ?,
                        scan_timestamp = ?,
                        extracted_features = ?,
                        threat_indicators = ?
                    WHERE id = ?
                """, (
                    domain, prediction, risk_score, risk_level,
                    confidence, timestamp, features_json, indicators_json, scan_id
                ))
                return scan_id

            cursor = conn.execute("""
                INSERT INTO scans (
                    url, domain, prediction, risk_score, risk_level,
                    confidence, scan_timestamp, extracted_features, threat_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url, domain, prediction, risk_score, risk_level,
                confidence, timestamp, features_json, indicators_json
            ))
            scan_id = cursor.lastrowid
            return scan_id
    finally:
        conn.close()


def get_scan(scan_id: int) -> dict | None:
    """Retrieve a single URL scan record by ID."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    data = dict(row)
    data["extracted_features"] = json.loads(data["extracted_features"])
    data["threat_indicators"] = json.loads(data["threat_indicators"])
    return data


def list_scans(limit: int = 50, offset: int = 0, search: str = "",
               prediction: str = "", risk_level: str = "") -> tuple[list[dict], int]:
    """List and search URL scans with pagination and filters."""
    conn = get_db_connection()
    query = "SELECT * FROM scans WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM scans WHERE 1=1"
    params = []

    if search:
        search_param = f"%{search}%"
        query += " AND (url LIKE ? OR domain LIKE ?)"
        count_query += " AND (url LIKE ? OR domain LIKE ?)"
        params.extend([search_param, search_param])

    if prediction:
        query += " AND prediction = ?"
        count_query += " AND prediction = ?"
        params.append(prediction)

    if risk_level:
        query += " AND risk_level = ?"
        count_query += " AND risk_level = ?"
        params.append(risk_level)

    count_cursor = conn.execute(count_query, params)
    total_count = count_cursor.fetchone()[0]

    query += " ORDER BY scan_timestamp DESC LIMIT ? OFFSET ?"
    query_params = params + [limit, offset]

    cursor = conn.execute(query, query_params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        item["extracted_features"] = json.loads(item["extracted_features"])
        item["threat_indicators"] = json.loads(item["threat_indicators"])
        results.append(item)

    return results, total_count


def delete_scan(scan_id: int) -> bool:
    """Delete a single URL scan by ID."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_all_scans() -> int:
    """Clear all URL scans from the database."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM scans")
        count = cursor.rowcount
    conn.close()
    return count


def get_statistics() -> dict:
    """Calculate aggregated metrics for the URL dashboard."""
    conn = get_db_connection()

    total_cursor = conn.execute("SELECT COUNT(*), AVG(risk_score) FROM scans")
    total_row = total_cursor.fetchone()
    total_scans = total_row[0] or 0
    avg_risk = round(total_row[1] or 0.0, 1)

    pred_cursor = conn.execute("""
        SELECT prediction, COUNT(*) FROM scans GROUP BY prediction
    """)
    pred_counts = {
        "Likely Legitimate": 0,
        "Suspicious": 0,
        "Potential Phishing": 0
    }
    for row in pred_cursor.fetchall():
        pred_counts[row[0]] = row[1]

    risk_cursor = conn.execute("""
        SELECT risk_level, COUNT(*) FROM scans GROUP BY risk_level
    """)
    risk_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0
    }
    for row in risk_cursor.fetchall():
        risk_counts[row[0]] = row[1]

    recent_cursor = conn.execute("""
        SELECT id, url, domain, prediction, risk_score, risk_level, scan_timestamp
        FROM scans ORDER BY scan_timestamp DESC LIMIT 5
    """)
    recent_scans = [dict(r) for r in recent_cursor.fetchall()]

    conn.close()

    return {
        "total_scans": total_scans,
        "average_risk_score": avg_risk,
        "phishing_count": pred_counts.get("Potential Phishing", 0),
        "suspicious_count": pred_counts.get("Suspicious", 0),
        "legitimate_count": pred_counts.get("Likely Legitimate", 0),
        "risk_distribution": risk_counts,
        "prediction_distribution": pred_counts,
        "recent_scans": recent_scans
    }


# =========================================================================
# File Scan Operations
# =========================================================================

def insert_file_scan(filename: str, file_hash: str, file_size: int,
                     mime_type: str, status: str, engine_used: str,
                     threat_name: str | None, metadata: dict,
                     recommendations: list) -> int:
    """Insert or update a file scan record by file_hash to prevent duplicate entries."""
    conn = get_db_connection()
    timestamp = datetime.now(timezone.utc).isoformat()
    meta_json = json.dumps(metadata)
    rec_json = json.dumps(recommendations)

    try:
        with conn:
            cursor = conn.execute("SELECT id FROM file_scans WHERE file_hash = ? ORDER BY id DESC LIMIT 1", (file_hash,))
            existing = cursor.fetchone()
            if existing:
                file_id = existing[0]
                conn.execute("""
                    UPDATE file_scans SET
                        filename = ?,
                        file_size = ?,
                        mime_type = ?,
                        status = ?,
                        engine_used = ?,
                        threat_name = ?,
                        scan_timestamp = ?,
                        metadata_json = ?,
                        recommendations_json = ?
                    WHERE id = ?
                """, (
                    filename, file_size, mime_type, status,
                    engine_used, threat_name, timestamp, meta_json, rec_json, file_id
                ))
                return file_id

            cursor = conn.execute("""
                INSERT INTO file_scans (
                    filename, file_hash, file_size, mime_type, status,
                    engine_used, threat_name, scan_timestamp,
                    metadata_json, recommendations_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename, file_hash, file_size, mime_type, status,
                engine_used, threat_name, timestamp, meta_json, rec_json
            ))
            file_id = cursor.lastrowid
            return file_id
    finally:
        conn.close()


def get_file_scan(file_id: int) -> dict | None:
    """Retrieve a single file scan record by ID."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM file_scans WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    data = dict(row)
    data["metadata"] = json.loads(data["metadata_json"])
    data["recommendations"] = json.loads(data["recommendations_json"])
    data["threat_indicators"] = data["metadata"].get("threat_indicators", [])
    data["sha256"] = data["file_hash"]
    return data


def list_file_scans(limit: int = 50, offset: int = 0, search: str = "",
                    status: str = "") -> tuple[list[dict], int]:
    """List and search file scans with pagination and filters."""
    conn = get_db_connection()
    query = "SELECT * FROM file_scans WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM file_scans WHERE 1=1"
    params = []

    if search:
        search_param = f"%{search}%"
        query += " AND (filename LIKE ? OR file_hash LIKE ? OR threat_name LIKE ?)"
        count_query += " AND (filename LIKE ? OR file_hash LIKE ? OR threat_name LIKE ?)"
        params.extend([search_param, search_param, search_param])

    if status:
        query += " AND status = ?"
        count_query += " AND status = ?"
        params.append(status)

    count_cursor = conn.execute(count_query, params)
    total_count = count_cursor.fetchone()[0]

    query += " ORDER BY scan_timestamp DESC LIMIT ? OFFSET ?"
    query_params = params + [limit, offset]

    cursor = conn.execute(query, query_params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        item["metadata"] = json.loads(item["metadata_json"])
        item["recommendations"] = json.loads(item["recommendations_json"])
        item["sha256"] = item["file_hash"]
        results.append(item)

    return results, total_count


def delete_file_scan(file_id: int) -> bool:
    """Delete a single file scan by ID."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM file_scans WHERE id = ?", (file_id,))
        deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_all_file_scans() -> int:
    """Clear all file scans from the database."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM file_scans")
        count = cursor.rowcount
    conn.close()
    return count


def get_file_statistics() -> dict:
    """Calculate aggregated metrics for the file virus scanner."""
    conn = get_db_connection()

    total_cursor = conn.execute("SELECT COUNT(*) FROM file_scans")
    total_files = total_cursor.fetchone()[0] or 0

    status_cursor = conn.execute("""
        SELECT status, COUNT(*) FROM file_scans GROUP BY status
    """)
    status_counts = {
        "Clean": 0,
        "Suspicious": 0,
        "Malicious": 0,
        "Limited Analysis": 0,
        "Scan Error": 0
    }
    for row in status_cursor.fetchall():
        status_counts[row[0]] = row[1]

    recent_cursor = conn.execute("""
        SELECT id, filename, file_hash, file_size, status, threat_name, scan_timestamp
        FROM file_scans ORDER BY scan_timestamp DESC LIMIT 5
    """)
    recent_scans = [dict(r) for r in recent_cursor.fetchall()]

    conn.close()

    return {
        "total_files": total_files,
        "clean_count": status_counts.get("Clean", 0),
        "suspicious_count": status_counts.get("Suspicious", 0),
        "malicious_count": status_counts.get("Malicious", 0),
        "limited_count": status_counts.get("Limited Analysis", 0),
        "error_count": status_counts.get("Scan Error", 0),
        "status_distribution": status_counts,
        "recent_scans": recent_scans
    }
