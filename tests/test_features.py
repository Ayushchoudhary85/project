"""
Unit tests for Feature Extraction Engine.
"""
import pytest
from feature_extractor import (
    FeatureExtractor, calculate_entropy, is_ip_address,
    detect_brand_impersonation, normalize_url, FEATURE_NAMES
)


def test_url_normalization():
    assert normalize_url("google.com") == "http://google.com"
    assert normalize_url("https://example.com/test") == "https://example.com/test"
    assert normalize_url("") == ""


def test_shannon_entropy():
    # Low entropy (repeated characters)
    low = calculate_entropy("aaaaaaa")
    # High entropy (random diverse string)
    high = calculate_entropy("a8f93bc1z77x9")
    assert low == 0.0
    assert high > 3.0


def test_is_ip_address():
    assert is_ip_address("192.168.1.1") == 1
    assert is_ip_address("10.0.0.1:8080") == 1
    assert is_ip_address("google.com") == 0
    assert is_ip_address("not-an-ip") == 0


def test_brand_impersonation():
    # Typosquatting / subdomain spoofing
    score, brand = detect_brand_impersonation("paypal-security.xyz", "login")
    assert score > 0
    assert brand == "paypal"

    score, brand = detect_brand_impersonation("paypa1.com", "")
    assert score > 0
    assert brand == "paypal"

    # Official domain should not be flagged as impersonation
    score, brand = detect_brand_impersonation("paypal.com", "www")
    assert score == 0.0


def test_feature_vector_structure():
    extractor = FeatureExtractor()
    res = extractor.extract("https://aws.amazon.com/s3/?region=us-east-1")
    
    assert "features" in res
    assert "vector" in res
    assert "components" in res
    assert "indicators" in res
    
    # Must match exact FEATURE_NAMES count
    assert len(res["vector"]) == len(FEATURE_NAMES)
    assert len(res["features"]) == len(FEATURE_NAMES)
