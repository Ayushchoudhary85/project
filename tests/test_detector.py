"""
Unit tests for Phishing Detection Engine.
"""
import pytest
from detector import PhishDetector


@pytest.fixture
def detector():
    return PhishDetector()


def test_whitelisted_domain_fast_path(detector):
    result = detector.analyze_url("https://github.com/torvalds/linux")
    assert result["is_whitelisted"] is True
    assert result["prediction"] == "Likely Legitimate"
    assert result["risk_score"] <= 10
    assert result["risk_level"] == "Low"
    assert result["confidence"] >= 0.90


def test_phishing_detection_accuracy(detector):
    phish_url = "http://paypal-security-account-verification.xyz/login.php"
    result = detector.analyze_url(phish_url)
    assert result["prediction"] == "Potential Phishing"
    assert result["risk_score"] >= 60
    assert result["risk_level"] in ("High", "Critical")
    assert len(result["threat_indicators"]) > 0


def test_raw_ip_phishing_detection(detector):
    ip_url = "http://192.168.1.100:8080/secure/banking/login.php"
    result = detector.analyze_url(ip_url)
    assert result["risk_score"] >= 50
    assert any("IP address" in ind for ind in result["threat_indicators"])


def test_invalid_urls(detector):
    with pytest.raises(ValueError):
        detector.analyze_url("")

    with pytest.raises(ValueError):
        detector.analyze_url("https://" + "a" * 2500 + ".com")
