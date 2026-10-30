"""
Model Manager for PhishGuard.
Handles model loading, caching, inference formatting, and metadata persistence.
"""
import json
import os
import joblib
from config import Config

_MODEL_INSTANCE = None
_METADATA_INSTANCE = None


def load_model():
    """Load trained model from disk with in-memory caching."""
    global _MODEL_INSTANCE, _METADATA_INSTANCE

    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE, _METADATA_INSTANCE

    if not os.path.exists(Config.MODEL_PATH):
        return None, None

    try:
        _MODEL_INSTANCE = joblib.load(Config.MODEL_PATH)
        if os.path.exists(Config.MODEL_METADATA_PATH):
            with open(Config.MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
                _METADATA_INSTANCE = json.load(f)
        else:
            _METADATA_INSTANCE = {"status": "trained", "model_type": "RandomForestClassifier"}
        return _MODEL_INSTANCE, _METADATA_INSTANCE
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None


def save_model(model, metadata: dict):
    """Save trained model and associated evaluation metadata to disk."""
    global _MODEL_INSTANCE, _METADATA_INSTANCE

    os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
    joblib.dump(model, Config.MODEL_PATH)

    with open(Config.MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    _MODEL_INSTANCE = model
    _METADATA_INSTANCE = metadata


def get_model_metadata():
    """Retrieve metadata about the currently deployed model."""
    global _METADATA_INSTANCE
    if _METADATA_INSTANCE is not None:
        return _METADATA_INSTANCE

    if os.path.exists(Config.MODEL_METADATA_PATH):
        with open(Config.MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
            _METADATA_INSTANCE = json.load(f)
        return _METADATA_INSTANCE
    return None
