import numpy as np
import joblib
import tensorflow as tf

from tensorflow.keras.models import load_model
from typing import List, Dict, Any

class FeatureNoiseLayer(tf.keras.layers.Layer):

    def __init__(self, stddev: float = 0.05, **kwargs):
        super().__init__(**kwargs)
        self.stddev = stddev

    def call(self, inputs, training=False):
        if training:
            return inputs + tf.random.normal(
                tf.shape(inputs),
                stddev=self.stddev
            )
        return inputs

    def get_config(self):
        config = super().get_config()
        config.update({"stddev": self.stddev})
        return config

class AnomalyService:

    def __init__(
        self,
        model_path,
        scaler_path,
        features_path,
        threshold_path
    ):

        self.model = load_model(
            model_path,
            custom_objects={
                "FeatureNoiseLayer": FeatureNoiseLayer
            }
        )

        self.scaler = joblib.load(scaler_path)
        self.features = joblib.load(features_path)
        self.threshold = joblib.load(threshold_path)

        self.p95 = self.threshold["p95"]
        self.p99 = self.threshold["p99"]

        print(
            f"AnomalyService ready. "
            f"Features={len(self.features)} "
            f"p95={self.p95:.6f} "
            f"p99={self.p99:.6f}"
        )

    # =====================================================
    # AUTOENCODER
    # =====================================================

    def _autoencoder_score(
        self,
        enriched: Dict[str, Any]
    ) -> float:

        row = {col: 0.0 for col in self.features}

        for col in self.features:

            value = enriched.get(col)

            if value is None:
                continue

            try:
                row[col] = float(value)
            except Exception:
                pass

        X = np.array(
            [[row[c] for c in self.features]],
            dtype=np.float32
        )

        X_scaled = self.scaler.transform(X)

        reconstructed = self.model.predict(
            X_scaled,
            verbose=0
        )

        score = float(
            np.mean(
                np.square(
                    X_scaled - reconstructed
                )
            )
        )

        return score

    # =====================================================
    # MAIN DETECTION
    # =====================================================

    def detect(
        self,
        transaction_id: str,
        enriched: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        anomalies = []

        anomaly_counter = 1

        # =================================================
        # SPENDING SPIKE
        # =================================================

        amount_ratio = enriched.get(
            "amount_ratio",
            0
        )

        if amount_ratio > 3:

            anomalies.append(
                {
                    "id": f"an_{anomaly_counter:03d}",
                    "type": "SPENDING_SPIKE",
                    "message": "Pengeluaran lebih tinggi dari biasanya",
                    "detail": [
                        {
                            "usual_amount":
                                round(
                                    enriched.get(
                                        "historical_avg_amount",
                                        0
                                    ),
                                    2
                                ),
                            "current_amount":
                                enriched.get(
                                    "amount",
                                    0
                                ),
                            "ratio":
                                round(
                                    amount_ratio,
                                    2
                                )
                        }
                    ],
                    "dismissed": False
                }
            )

            anomaly_counter += 1

        # =================================================
        # UNUSUAL TIME
        # =================================================

        if enriched.get(
            "is_unusual_hour",
            0
        ) == 1:

            anomalies.append(
                {
                    "id": f"an_{anomaly_counter:03d}",
                    "type": "UNUSUAL_TIME",
                    "message": "Transaksi di luar jam biasa",
                    "detail": [
                        {
                            "usual_hour_range":
                                f"{enriched.get('usual_hour_min', 0):02d}:00 - "
                                f"{enriched.get('usual_hour_max', 23):02d}:00",
                            "detected_hour":
                                enriched.get(
                                    "time",
                                    ""
                                )
                        }
                    ],
                    "dismissed": False
                }
            )

            anomaly_counter += 1

        # =================================================
        # FREQUENCY SPIKE
        # =================================================

        merchant_freq_ratio = enriched.get(
            "merchant_freq_ratio",
            0
        )

        if merchant_freq_ratio > 3:

            anomalies.append(
                {
                    "id": f"an_{anomaly_counter:03d}",
                    "type": "FREQUENCY_SPIKE",
                    "message": "Frekuensi transaksi lebih tinggi dari biasanya",
                    "detail": [
                        {
                            "merchant":
                                enriched.get(
                                    "merchant",
                                    ""
                                ),
                            "usual_frequency":
                                round(
                                    enriched.get(
                                        "merchant_avg_freq",
                                        0
                                    ),
                                    2
                                ),
                            "current_frequency":
                                enriched.get(
                                    "merchant_monthly_freq",
                                    0
                                ),
                            "ratio":
                                round(
                                    merchant_freq_ratio,
                                    2
                                )
                        }
                    ],
                    "dismissed": False
                }
            )

            anomaly_counter += 1

        # =================================================
        # PRICE SPIKE
        # =================================================

        for item in enriched.get(
            "items",
            []
        ):

            usual_price = item.get(
                "usual_price"
            )

            current_price = item.get(
                "harga"
            )

            if not usual_price:
                continue

            ratio = (
                current_price /
                usual_price
            )

            if ratio > 3:

                anomalies.append(
                    {
                        "id": f"an_{anomaly_counter:03d}",
                        "type": "PRICE_SPIKE",
                        "message": "Harga item naik 3× dari biasanya",
                        "detail": [
                            {
                                "item_name":
                                    item.get(
                                        "item_name"
                                    ),
                                "usual_price":
                                    round(
                                        usual_price,
                                        0
                                    ),
                                "current_price":
                                    current_price,
                                "ratio":
                                    round(
                                        ratio,
                                        2
                                    )
                            }
                        ],
                        "dismissed": False
                    }
                )

                anomaly_counter += 1

        # =================================================
        # AUTOENCODER
        # =================================================

        score = self._autoencoder_score(
            enriched
        )

        if (
            score > self.p95
            and len(anomalies) == 0
        ):

            anomalies.append(
                {
                    "id": f"an_{anomaly_counter:03d}",
                    "type": "AUTOENCODER_ANOMALY",
                    "message": "Pola transaksi tidak biasa",
                    "detail": [
                        {
                            "anomaly_score":
                                round(
                                    score,
                                    8
                                ),
                            "threshold":
                                round(
                                    self.p95,
                                    8
                                )
                        }
                    ],
                    "dismissed": False
                }
            )

        return anomalies