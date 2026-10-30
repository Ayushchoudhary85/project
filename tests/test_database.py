"""
Unit tests for SQLite Database Layer.
"""
import os
import pytest
from database import (
    init_db, insert_scan, get_scan, list_scans,
    delete_scan, clear_all_scans, get_statistics
)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_phishguard.db"
    monkeypatch.setattr("config.Config.DATABASE_PATH", str(test_db))
    init_db()
    yield
    if test_db.exists():
        test_db.unlink()


def test_insert_and_get_scan():
    scan_id = insert_scan(
        url="http://test-phish.xyz/login",
        domain="test-phish.xyz",
        prediction="Potential Phishing",
        risk_score=85,
        risk_level="Critical",
        confidence=0.92,
        features={"url_length": 30, "domain_entropy": 3.9},
        indicators=["Suspicious TLD"]
    )
    assert scan_id > 0

    scan = get_scan(scan_id)
    assert scan is not None
    assert scan["domain"] == "test-phish.xyz"
    assert scan["risk_score"] == 85
    assert scan["extracted_features"]["domain_entropy"] == 3.9
    assert "Suspicious TLD" in scan["threat_indicators"]


def test_list_and_search_scans():
    insert_scan("https://google.com", "google.com", "Likely Legitimate", 0, "Low", 0.99, {}, [])
    insert_scan("http://bad-site.top", "bad-site.top", "Potential Phishing", 90, "Critical", 0.95, {}, ["Bad TLD"])

    # Search
    scans, count = list_scans(search="google")
    assert count == 1
    assert scans[0]["domain"] == "google.com"

    # Filter by prediction
    scans, count = list_scans(prediction="Potential Phishing")
    assert count == 1
    assert scans[0]["prediction"] == "Potential Phishing"


def test_delete_and_clear_scans():
    sid = insert_scan("http://sample.com", "sample.com", "Likely Legitimate", 10, "Low", 0.9, {}, [])
    assert delete_scan(sid) is True
    assert get_scan(sid) is None

    insert_scan("http://sample1.com", "sample1.com", "Likely Legitimate", 10, "Low", 0.9, {}, [])
    insert_scan("http://sample2.com", "sample2.com", "Likely Legitimate", 10, "Low", 0.9, {}, [])
    cleared = clear_all_scans()
    assert cleared == 2


def test_statistics():
    insert_scan("https://legit.com", "legit.com", "Likely Legitimate", 10, "Low", 0.99, {}, [])
    insert_scan("http://phish.com", "phish.com", "Potential Phishing", 90, "Critical", 0.95, {}, [])

    stats = get_statistics()
    assert stats["total_scans"] == 2
    assert stats["average_risk_score"] == 50.0
    assert stats["phishing_count"] == 1
    assert stats["legitimate_count"] == 1
