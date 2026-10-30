"""
Configuration settings for PhishGuard.
"""
import os
import json
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

if IS_SERVERLESS:
    INSTANCE_DIR = Path(tempfile.gettempdir()) / "phishguard_instance"
else:
    INSTANCE_DIR = BASE_DIR / "instance"

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

MODELS_DIR = BASE_DIR / "models"
if not IS_SERVERLESS:
    MODELS_DIR.mkdir(exist_ok=True)

DATASET_DIR = BASE_DIR / "dataset"
if not IS_SERVERLESS:
    DATASET_DIR.mkdir(exist_ok=True)

UPLOADS_DIR = INSTANCE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = INSTANCE_DIR / "settings.json"


def load_settings() -> dict:
    """Load configurable application settings or return defaults."""
    default_settings = {
        "max_upload_size_mb": 16,
        "clamav_path": "clamscan",
        "enable_heuristics": True,
        "entropy_threshold": 7.2
    }
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_settings.update(saved)
        except Exception:
            pass
    return default_settings


def save_settings(settings: dict):
    """Persist settings to settings.json."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


class Config:
    BASE_DIR = BASE_DIR
    INSTANCE_DIR = INSTANCE_DIR
    MODELS_DIR = MODELS_DIR
    DATASET_DIR = DATASET_DIR
    UPLOADS_DIR = UPLOADS_DIR
    SECRET_KEY = os.environ.get("SECRET_KEY", "phishguard-insecure-dev-secret-key-38294719")
    TESTING = False
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "phishguard.db"))
    MODEL_PATH = str(MODELS_DIR / "phishing_model.pkl")
    MODEL_METADATA_PATH = str(MODELS_DIR / "model_metadata.json")

    # Rate Limiting
    RATELIMIT_DEFAULT = "120 per minute"
    RATELIMIT_STORAGE_URI = "memory://"

    # File Upload Limits
    _settings = load_settings()
    MAX_CONTENT_LENGTH = int(_settings.get("max_upload_size_mb", 16)) * 1024 * 1024
    CLAMAV_PATH = os.environ.get("CLAMAV_PATH", _settings.get("clamav_path", "clamscan"))

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
