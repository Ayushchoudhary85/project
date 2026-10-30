"""
Model Training Script for PhishGuard.
Extracts hybrid features from URL dataset, trains a RandomForestClassifier,
evaluates performance metrics, and serializes the model and metadata.
"""
import os
import sys
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from config import Config
from feature_extractor import FeatureExtractor, FEATURE_NAMES
from model_manager import save_model


def train_phishing_model(csv_path: str = None) -> dict:
    """Train RandomForest on the URL dataset and save artifacts."""
    if csv_path is None:
        csv_path = os.path.join(Config.DATASET_DIR, "phishing.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")

    print(f"[*] Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)

    # Validate dataset structure
    if "url" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'url' and 'label' columns.")

    # Clean duplicates and nulls
    initial_len = len(df)
    df = df.dropna(subset=["url", "label"])
    df = df.drop_duplicates(subset=["url"])
    print(f"[*] Processed {len(df)} unique URLs (removed {initial_len - len(df)} duplicates/nulls)")

    extractor = FeatureExtractor()

    print("[*] Extracting hybrid features for all URLs...")
    feature_rows = []
    labels = []

    for idx, row in df.iterrows():
        try:
            res = extractor.extract(str(row["url"]))
            feature_rows.append(res["vector"])
            labels.append(int(row["label"]))
        except Exception as e:
            print(f"[!] Warning: Failed extracting features for '{row['url']}': {e}")

    X = np.array(feature_rows)
    y = np.array(labels)

    print(f"[*] Feature matrix shape: {X.shape}, Target distribution: {dict(pd.Series(y).value_counts())}")

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"[*] Training RandomForestClassifier on {len(X_train)} samples...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature importances
    importances = {
        name: round(float(imp), 4)
        for name, imp in zip(FEATURE_NAMES, clf.feature_importances_)
    }
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    metadata = {
        "model_type": "RandomForestClassifier",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "total_samples": int(len(df)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "feature_names": FEATURE_NAMES,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm
        },
        "top_features": dict(list(sorted_importances.items())[:10])
    }

    save_model(clf, metadata)
    print("\n" + "=" * 50)
    print(" MODEL TRAINING & EVALUATION REPORT ")
    print("=" * 50)
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"Confusion Matrix: {cm}")
    print("\nTop 5 Most Informative Features:")
    for feat, imp in list(sorted_importances.items())[:5]:
        print(f"  - {feat}: {imp:.4f}")
    print("=" * 50)
    print(f"[+] Model saved to {Config.MODEL_PATH}")
    print(f"[+] Metadata saved to {Config.MODEL_METADATA_PATH}")

    return metadata


if __name__ == "__main__":
    train_phishing_model()
