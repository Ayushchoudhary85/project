"""
Unit and integration tests for the File Virus Scanner module, PDF generator, and File API endpoints.
"""
import io
import pytest
from file_security import (
    sanitize_filename, compute_file_hashes,
    calculate_file_entropy, inspect_file_signatures
)
from report_generator import generate_file_scan_pdf
from app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_files.db"
    monkeypatch.setattr("config.Config.DATABASE_PATH", str(test_db))
    monkeypatch.setattr("config.Config.TESTING", True)

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_sanitize_filename():
    # Path traversal attempts
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("test file (1).pdf") == "test_file_1.pdf"
    assert sanitize_filename("") == "unnamed_file"


def test_compute_file_hashes(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"PhishGuard Secure Payload Verification 2026")

    hashes = compute_file_hashes(str(sample))
    assert len(hashes["sha256"]) == 64
    assert len(hashes["sha1"]) == 40
    assert len(hashes["md5"]) == 32


def test_calculate_file_entropy(tmp_path):
    # Homogeneous zero bytes -> low entropy (~0.0)
    flat_file = tmp_path / "flat.bin"
    flat_file.write_bytes(b"\x00" * 1024)
    assert calculate_file_entropy(str(flat_file)) < 0.1

    # Varied bytes -> higher entropy
    random_bytes = bytes([i % 256 for i in range(2048)])
    diverse_file = tmp_path / "diverse.bin"
    diverse_file.write_bytes(random_bytes)
    assert calculate_file_entropy(str(diverse_file)) > 7.0


def test_inspect_file_signatures_and_spoofing(tmp_path):
    # Spoofed file: text content pretending to be PDF
    spoofed = tmp_path / "fake.pdf"
    spoofed.write_bytes(b"This is purely plain text, not a valid PDF header.")

    res = inspect_file_signatures(str(spoofed), "fake.pdf")
    assert res["is_spoofed"] is True
    assert any("spoofing" in ind.lower() for ind in res["threat_indicators"])

    # Double extension detection
    res2 = inspect_file_signatures(str(spoofed), "invoice.pdf.exe")
    assert res2["has_double_ext"] is True


def test_pdf_report_generator():
    scan_mock = {
        "id": 1,
        "filename": "suspicious_payload.exe",
        "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "md5": "d41d8cd98f00b204e9800998ecf8427e",
        "file_size": 1024,
        "mime_type": "application/x-dosexec",
        "status": "Suspicious",
        "threat_name": "Potential PE Anomaly",
        "engine_used": "Static Heuristics",
        "scan_timestamp": "2026-10-30T12:00:00Z",
        "threat_indicators": ["Extension Spoofing Detected", "High Byte Entropy"],
        "recommendations": ["Quarantine immediately.", "Do not execute."]
    }

    pdf_bytes = generate_file_scan_pdf(scan_mock)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_file_api_scan_and_history(client):
    # Upload test file
    test_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    data = {
        "file": (io.BytesIO(test_content), "document.pdf")
    }

    res = client.post("/api/file/scan", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    file_id = json_data["data"]["id"]
    assert file_id > 0
    # ClamAV is not installed, so status MUST be "Limited Analysis" or "Suspicious" (never "Clean")
    assert json_data["data"]["status"] in ("Limited Analysis", "Suspicious")

    # Retrieve history
    hist_res = client.get("/api/file/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.get_json()
    assert hist_data["total"] >= 1
    assert any(s["id"] == file_id for s in hist_data["scans"])

    # Retrieve single record
    single_res = client.get(f"/api/file/history/{file_id}")
    assert single_res.status_code == 200
    assert single_res.get_json()["data"]["id"] == file_id

    # PDF Report Download
    pdf_res = client.get(f"/api/file/report/{file_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.content_type == "application/pdf"
    assert pdf_res.data.startswith(b"%PDF")

    # Delete record
    del_res = client.delete(f"/api/file/history/{file_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["status"] == "success"


def test_file_scan_deduplication_and_natural_compression(client):
    """Verify that uploading the same file reuses/updates the row (no duplicates) and compressed files aren't falsely flagged."""
    # Create fake PDF with high-entropy bytes
    import zlib
    compressed_bytes = zlib.compress(b"PhishGuard security test payload repeating patterns" * 50)
    pdf_content = b"%PDF-1.4\n" + compressed_bytes + b"\n%%EOF"

    data1 = {"file": (io.BytesIO(pdf_content), "legitimate_document.pdf")}
    res1 = client.post("/api/file/scan", data=data1, content_type="multipart/form-data")
    assert res1.status_code == 200
    id1 = res1.get_json()["data"]["id"]
    risk1 = res1.get_json()["data"]["risk_score"]
    # Should not be flagged as high-risk malicious packing
    assert risk1 < 40

    # Upload exact same file again
    data2 = {"file": (io.BytesIO(pdf_content), "legitimate_document.pdf")}
    res2 = client.post("/api/file/scan", data=data2, content_type="multipart/form-data")
    assert res2.status_code == 200
    id2 = res2.get_json()["data"]["id"]
    # Must be the exact same ID (upsert / deduplication)
    assert id1 == id2


def test_settings_api(client):
    # Get current settings
    res = client.get("/api/settings")
    assert res.status_code == 200
    assert "max_upload_size_mb" in res.get_json()["data"]

    # Update settings
    post_res = client.post("/api/settings", json={
        "max_file_size_mb": 32,
        "clamav_path": "clamscan"
    })
    assert post_res.status_code == 200
    assert post_res.get_json()["data"]["max_upload_size_mb"] == 32
