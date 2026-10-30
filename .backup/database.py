"""
SQLite Database Layer for PhishGuard.
Provides parameterized thread-safe CRUD operations and aggregate statistics.
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
    conn.close()


def insert_scan(url: str, domain: str, prediction: str, risk_score: int,
                risk_level: str, confidence: float, features: dict,
                indicators: list) -> int:
    """Insert a new scan result into SQLite and return its ID."""
    conn = get_db_connection()
    timestamp = datetime.now(timezone.utc).isoformat()
    features_json = json.dumps(features)
    indicators_json = json.dumps(indicators)

    with conn:
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
    conn.close()
    return scan_id


def get_scan(scan_id: int) -> dict | None:
    """Retrieve a single scan record by ID."""
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
    """List and search scans with pagination and filters."""
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

    # Get total count matching criteria
    count_cursor = conn.execute(count_query, params)
    total_count = count_cursor.fetchone()[0]

    # Add order and pagination
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
    """Delete a single scan by ID."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_all_scans() -> int:
    """Clear all scans from the database."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM scans")
        count = cursor.rowcount
    conn.close()
    return count


def get_statistics() -> dict:
    """Calculate aggregated metrics for the dashboard."""
    conn = get_db_connection()

    total_cursor = conn.execute("SELECT COUNT(*), AVG(risk_score) FROM scans")
    total_row = total_cursor.fetchone()
    total_scans = total_row[0] or 0
    avg_risk = round(total_row[1] or 0.0, 1)

    # Counts by prediction
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

    # Counts by risk level
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

    # Recent 5 scans
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
