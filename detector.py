"""
Phishing Detection Engine for PhishGuard.
Combines Fast-Path Allowlist, Machine Learning Inference,
and Deterministic Threat Heuristics for Calibrated Risk Scoring.
"""
from datetime import datetime, timezone
import numpy as np
from config import Config
from feature_extractor import FeatureExtractor, normalize_url
from model_manager import load_model, get_model_metadata


class PhishDetector:
    """Unified URL analyzer and risk classification engine."""

    def __init__(self):
        self.extractor = FeatureExtractor()

    def analyze_url(self, raw_url: str) -> dict:
        """
        Analyze a URL and return a comprehensive cybersecurity threat assessment.
        """
        if not raw_url or not isinstance(raw_url, str):
            raise ValueError("Invalid URL: URL cannot be empty.")

        cleaned_url = raw_url.strip()
        if len(cleaned_url) > 2048:
            raise ValueError("URL exceeds maximum permissible length (2048 characters).")

        normalized = normalize_url(cleaned_url)

        # 1. Extract hybrid features and threat indicators
        extracted = self.extractor.extract(normalized)
        features = extracted["features"]
        vector = extracted["vector"]
        components = extracted["components"]
        indicators = extracted["indicators"]
        is_whitelisted = components["is_whitelisted"]

        # 2. Check Fast-Path Allowlist
        # If domain is in trusted apex domains and has no spoofing indicators
        if is_whitelisted and features["brand_impersonation_score"] == 0.0 and not features["has_punycode"]:
            risk_score = 5 if not features["is_https"] else 0
            risk_level = "Low"
            prediction = "Likely Legitimate"
            confidence = 0.99
            ml_phish_prob = 0.01

            recommendations = [
                "Domain belongs to a verified high-trust global authority.",
                "Safe for regular navigational use; practice standard security precautions."
            ]

            return self._build_result(
                url=normalized,
                domain=components["domain"],
                prediction=prediction,
                risk_score=risk_score,
                risk_level=risk_level,
                confidence=confidence,
                ml_prob=ml_phish_prob,
                features=features,
                indicators=indicators,
                recommendations=recommendations,
                is_whitelisted=True
            )

        # 3. Machine Learning Inference
        model, metadata = load_model()
        if model is None:
            # Fallback if model hasn't been trained yet
            ml_phish_prob = 0.5
            ml_confidence = 0.5
        else:
            X = np.array([vector])
            probabilities = model.predict_proba(X)[0]
            ml_phish_prob = float(probabilities[1])
            ml_confidence = float(max(probabilities))

        # 4. Calibrated Composite Risk Score Calculation
        # ML baseline contributes up to 70 points
        base_ml_score = ml_phish_prob * 70.0

        # Deterministic threat adjustments (up to +30 points)
        heuristic_bonus = 0.0

        if features["has_ip"]:
            heuristic_bonus += 15.0
        if features["has_punycode"]:
            heuristic_bonus += 20.0
        if features["brand_impersonation_score"] > 0:
            heuristic_bonus += 20.0 * features["brand_impersonation_score"]
        if features["is_suspicious_tld"]:
            heuristic_bonus += 15.0
        if features["suspicious_keyword_count"] >= 2:
            heuristic_bonus += 10.0
        if features["has_at_symbol"]:
            heuristic_bonus += 15.0
        if features["domain_entropy"] > 3.8:
            heuristic_bonus += 10.0
        if not features["is_https"] and features["suspicious_keyword_count"] > 0:
            heuristic_bonus += 10.0
        if features["has_unusual_port"]:
            heuristic_bonus += 10.0

        raw_score = base_ml_score + min(30.0, heuristic_bonus)
        risk_score = int(min(100, max(0, round(raw_score))))

        # 5. Determine Risk Level & Prediction
        if risk_score <= 29:
            risk_level = "Low"
            prediction = "Likely Legitimate"
        elif risk_score <= 59:
            risk_level = "Medium"
            prediction = "Suspicious"
        else:
            risk_level = "Critical" if risk_score >= 80 else "High"
            prediction = "Potential Phishing"

        # 6. Overall Confidence Calculation
        # Confidence reflects certainty in the categorized verdict
        if prediction == "Potential Phishing":
            confidence = round(max(ml_phish_prob, (risk_score / 100)), 2)
        elif prediction == "Likely Legitimate":
            confidence = round(max(1.0 - ml_phish_prob, 1.0 - (risk_score / 100)), 2)
        else:
            confidence = round(ml_confidence, 2)

        # 7. Actionable Security Recommendations
        recommendations = []
        if risk_level in ("High", "Critical"):
            recommendations.append("DO NOT enter login credentials, passwords, or personal identity details.")
            recommendations.append("DO NOT download or execute any file attachments from this address.")
            recommendations.append("Report this domain to your security team or hosting provider abuse desk.")
        elif risk_level == "Medium":
            recommendations.append("Proceed with caution. Verify the sender's identity before interacting.")
            recommendations.append("Inspect the browser address bar to ensure the domain matches the intended brand.")
        else:
            recommendations.append("No immediate structural anomalies detected. Standard precautions apply.")
            recommendations.append("Ensure HTTPS remains green and valid in your browser.")

        return self._build_result(
            url=normalized,
            domain=components["domain"],
            prediction=prediction,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=min(0.99, max(0.50, confidence)),
            ml_prob=round(ml_phish_prob, 4),
            features=features,
            indicators=indicators,
            recommendations=recommendations,
            is_whitelisted=False
        )

    def _build_result(self, url: str, domain: str, prediction: str, risk_score: int,
                      risk_level: str, confidence: float, ml_prob: float,
                      features: dict, indicators: list, recommendations: list,
                      is_whitelisted: bool) -> dict:
        return {
            "url": url,
            "domain": domain,
            "prediction": prediction,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "ml_probability": ml_prob,
            "extracted_features": features,
            "threat_indicators": indicators,
            "recommendations": recommendations,
            "is_whitelisted": is_whitelisted,
            "scan_timestamp": datetime.now(timezone.utc).isoformat()
        }
