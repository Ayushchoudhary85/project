"""
Unit tests for the Password Security Analyzer module and API endpoints.
"""
import pytest
from password_analyzer import analyze_password, generate_secure_password
from app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_password.db"
    monkeypatch.setattr("config.Config.DATABASE_PATH", str(test_db))
    monkeypatch.setattr("config.Config.TESTING", True)

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_empty_password():
    res = analyze_password("")
    assert res["score"] == 0
    assert res["category"] == "Very Weak"
    assert res["entropy_bits"] == 0.0
    assert res["length"] == 0


def test_common_weak_passwords():
    # Known top common passwords
    for weak in ["123456", "password", "qwerty", "admin", "welcome"]:
        res = analyze_password(weak)
        assert res["score"] <= 1
        assert res["category"] in ("Very Weak", "Weak")
        assert res["is_common"] is True
        assert any("common" in r.lower() for r in res["recommendations"])


def test_pattern_detection():
    # Repeated characters
    res = analyze_password("aaaaaaaaaaaa")
    assert res["has_repeated"] is True
    assert res["score"] <= 1

    # Sequential characters
    res = analyze_password("abcdefghijk")
    assert res["has_sequential"] is True
    assert res["score"] <= 1

    # Keyboard row walk
    res = analyze_password("qwertyuiop")
    assert res["has_keyboard_pattern"] is True


def test_strong_password():
    strong = "K9#mQ!vL2$pZ9*wA"
    res = analyze_password(strong)
    assert res["score"] >= 3
    assert res["category"] in ("Strong", "Very Strong")
    assert res["entropy_bits"] >= 60.0
    assert res["is_common"] is False
    assert res["meets_length"] is True
    assert res["has_uppercase"] is True
    assert res["has_lowercase"] is True
    assert res["has_digit"] is True
    assert res["has_symbol"] is True


def test_secure_password_generator():
    # Default 16 chars
    pwd = generate_secure_password(length=16)
    assert len(pwd) == 16

    # Length clamping
    pwd_short = generate_secure_password(length=4)
    assert len(pwd_short) >= 8

    pwd_long = generate_secure_password(length=100)
    assert len(pwd_long) <= 64

    # Charset restrictions
    pwd_no_sym = generate_secure_password(length=20, include_symbols=False)
    assert not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd_no_sym)


def test_api_password_analyze(client):
    res = client.post("/api/password/analyze", json={"password": "TestPassword123!"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "score" in data["data"]
    assert "entropy_bits" in data["data"]
    assert "category" in data["data"]
    # Verify strict zero-storage / privacy: raw password is NOT echoed back
    assert "password" not in data["data"]


def test_api_password_generate(client):
    res = client.post("/api/password/generate", json={"length": 24, "include_symbols": True})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]["password"]) == 24
