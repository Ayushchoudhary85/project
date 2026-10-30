"""
Configuration settings for PhishGuard.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

DATASET_DIR = BASE_DIR / "dataset"
DATASET_DIR.mkdir(exist_ok=True)


class Config:
    BASE_DIR = BASE_DIR
    INSTANCE_DIR = INSTANCE_DIR
    MODELS_DIR = MODELS_DIR
    DATASET_DIR = DATASET_DIR
    SECRET_KEY = os.environ.get("SECRET_KEY", "phishguard-insecure-dev-secret-key-38294719")
    TESTING = False
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "phishguard.db"))
    MODEL_PATH = str(MODELS_DIR / "phishing_model.pkl")
    MODEL_METADATA_PATH = str(MODELS_DIR / "model_metadata.json")

    # Rate Limiting
    RATELIMIT_DEFAULT = "120 per minute"
    RATELIMIT_STORAGE_URI = "memory://"

    # High Abuse / Suspicious TLDs (based on Spamhaus & Global Threat Intel)
    SUSPICIOUS_TLDS = {
        "xyz", "top", "buzz", "fit", "icu", "tk", "click", "monster",
        "work", "rest", "gq", "cf", "ml", "ga", "country", "stream",
        "cam", "download", "racing", "win", "bid", "loan", "party"
    }

    # High-Value Brands Targeted for Typosquatting & Subdomain Spoofing
    TARGET_BRANDS = [
        "paypal", "microsoft", "apple", "google", "amazon", "netflix",
        "chase", "wellsfargo", "bankofamerica", "facebook", "instagram",
        "whatsapp", "twitter", "steam", "binance", "coinbase", "dropbox",
        "adobe", "linkedin", "roblox", "github", "discord", "spotify",
        "yahoo", "outlook", "office365", "citibank", "dhl", "fedex", "usps"
    ]

    # Fast-Path Whitelist / Allowlist of universally trusted apex domains
    # Prevents false positives on complex deep links (e.g. github auth, google drive links)
    TRUSTED_APEX_DOMAINS = {
        "google.com", "youtube.com", "microsoft.com", "apple.com", "github.com",
        "amazon.com", "wikipedia.org", "linkedin.com", "netflix.com", "cloudflare.com",
        "wordpress.org", "mozilla.org", "adobe.com", "stackoverflow.com", "gitlab.com",
        "medium.com", "reddit.com", "yahoo.com", "bing.com", "twitter.com", "x.com"
    }

    # Suspicious keywords commonly found in credential harvesting / phishing paths
    SUSPICIOUS_KEYWORDS = [
        "login", "signin", "verify", "verification", "secure", "security",
        "account", "update", "banking", "billing", "confirm", "wallet",
        "recover", "authenticate", "passcode", "password", "suspended",
        "re-activate", "validation", "support", "service-notice", "auth"
    ]

    # Risk Categories Thresholds
    RISK_THRESHOLDS = {
        "low": (0, 29),
        "medium": (30, 59),
        "high": (60, 79),
        "critical": (80, 100)
    }
