
# fastapi/anomaly_service.py
# Core service class — encapsulates model loading and prediction logic

import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from typing import Optional, List, Dict, Any


class FeatureNoiseLayer(tf.keras.layers.Layer):
    """Must be registered to load the .keras model."""
    def __init__(self, stddev: float = 0.05, **kwargs):
        super().__init__(**kwargs)
        self.stddev = stddev
    def call(self, inputs, training=False):
        if training:
            return inputs + tf.random.normal(tf.shape(inputs), stddev=self.stddev)
        return inputs
    def get_config(self):
        config = super().get_config()
        config.update({"stddev": self.stddev})
        return config


class AnomalyService:
    """Loads artifacts once and exposes a predict() method."""

    def __init__(self, model_path, scaler_path, features_path, threshold_path):
        self.model     = load_model(model_path, custom_objects={"FeatureNoiseLayer": FeatureNoiseLayer})
        self.scaler    = joblib.load(scaler_path)
        self.features  = joblib.load(features_path)
        self.threshold = joblib.load(threshold_path)
        self.p95 = self.threshold["p95"]
        self.p99 = self.threshold["p99"]
        print(f"AnomalyService ready. Features: {len(self.features)}, p95={self.p95:.6f}, p99={self.p99:.6f}")

    def _classify_severity(self, score: float) -> str:
        if score >= self.p99:
            return "high"
        elif score >= self.p95:
            return "warning"
        return "normal"

    def _detect_anomaly_types(self, data: Dict[str, Any]) -> List[str]:
        types = []
        if data.get("amount_rolling_ratio", 0) > 3.0:
            types.append("SPENDING_SPIKE")
        if data.get("merchant_freq_ratio", 0) > 0.8:
            types.append("MERCHANT_FREQUENCY_SPIKE")
        if data.get("is_unusual_hour", 0) == 1:
            types.append("UNUSUAL_TIME")
        if data.get("category_freq_ratio", 0) > 0.7:
            types.append("CATEGORY_FREQUENCY_SPIKE")
        return types if types else ["GENERAL_ANOMALY"]

    def predict(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Predict anomaly for a single transaction dict.

        Args:
            transaction: dict matching TransactionRequest fields.

        Returns:
            dict with keys: transaction_id, anomaly_score, is_anomaly, severity, anomaly_types
        """
        # Build aligned feature row
        row = {col: 0.0 for col in self.features}
        for col in self.features:
            if col in transaction and transaction[col] is not None:
                row[col] = float(transaction[col])

        X = np.array([[row[c] for c in self.features]], dtype=np.float32)
        X_scaled = self.scaler.transform(X)

        reconstructed = self.model.predict(X_scaled, verbose=0)
        score = float(np.mean(np.square(X_scaled - reconstructed)))

        severity = self._classify_severity(score)
        anomaly_types = self._detect_anomaly_types(transaction)

        return {
            "transaction_id": transaction.get("transaction_id"),
            "anomaly_score" : round(score, 8),
            "is_anomaly"    : score >= self.p95,
            "severity"      : severity,
            "anomaly_types" : anomaly_types if severity != "normal" else [],
        }
