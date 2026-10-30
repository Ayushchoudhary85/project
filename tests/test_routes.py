"""
Unit and integration tests for Flask API and Page Routes.
"""
import pytest
from app import create_app
from database import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_routes.db"
    monkeypatch.setattr("config.Config.DATABASE_PATH", str(test_db))
    monkeypatch.setattr("config.Config.TESTING", True)
    
    app = create_app()
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client


def test_html_pages(client):
    res = client.get("/")
    assert res.status_code == 302  # Redirects to /dashboard

    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"PHISHGUARD" in res.data
    assert b"Live URL Threat Scanner" in res.data

    res = client.get("/scanner")
    assert res.status_code == 200
    assert b"PHISHGUARD" in res.data
    assert b"Live URL Threat Scanner" in res.data

    res = client.get("/history")
    assert res.status_code == 200
    assert b"Security Audit History" in res.data

    res = client.get("/analytics")
    assert res.status_code == 200
    assert b"Cyber Threat Analytics" in res.data

    res = client.get("/password-analyzer")
    assert res.status_code == 200
    assert b"Password Security Analyzer" in res.data

    res = client.get("/file-scanner")
    assert res.status_code == 200
    assert b"File Virus Scanner" in res.data

    res = client.get("/settings")
    assert res.status_code == 200
    assert b"Security Settings &amp; Configuration" in res.data or b"Security Settings & Configuration" in res.data


def test_api_scan_endpoint(client):
    # Valid scan
    res = client.post("/api/scan", json={"url": "https://en.wikipedia.org/wiki/Computer_security"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "prediction" in data["data"]
    assert "risk_score" in data["data"]
    assert "id" in data["data"]

    # Invalid empty payload
    res = client.post("/api/scan", json={})
    assert res.status_code == 400

    # Invalid blank URL
    res = client.post("/api/scan", json={"url": "   "})
    assert res.status_code == 400


def test_api_history_and_statistics(client):
    # Scan a URL first
    client.post("/api/scan", json={"url": "http://paypal-verification-account.xyz/login.php"})

    # Check history API
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["total"] >= 1
    scan_id = data["scans"][0]["id"]

    # Check single scan API
    res = client.get(f"/api/history/{scan_id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == scan_id

    # Verify URL Deduplication: scanning identical URL should update existing record, not increment total count
    hist_before = client.get("/api/history").get_json()["total"]
    res_dup = client.post("/api/scan", json={"url": "http://paypal-verification-account.xyz/login.php"})
    assert res_dup.status_code == 200
    assert res_dup.get_json()["data"]["id"] == scan_id
    hist_after = client.get("/api/history").get_json()["total"]
    assert hist_before == hist_after

    # Check statistics API
    res = client.get("/api/statistics")
    assert res.status_code == 200
    assert res.get_json()["data"]["total_scans"] >= 1

    # Check analytics API
    res = client.get("/api/analytics")
    assert res.status_code == 200
    assert "statistics" in res.get_json()["data"]

    # Delete scan
    res = client.delete(f"/api/history/{scan_id}")
    assert res.status_code == 200
    assert res.get_json()["status"] == "success"
