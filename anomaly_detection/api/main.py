from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.anomaly_service import AnomalyService

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Personal Finance — Anomaly Detection API",
    version="2.1.0",
    description="Detects unusual spending behaviour using a TensorFlow Autoencoder.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

service = AnomalyService(
    model_path=str(BASE_DIR / "models" / "anomaly_autoencoder.keras"),
    scaler_path=str(BASE_DIR / "models" / "scaler.pkl"),
    features_path=str(BASE_DIR / "models" / "feature_columns.pkl"),
    threshold_path=str(BASE_DIR / "models" / "threshold.pkl"),
)

# ==================================================
# REQUEST MODELS
# ==================================================

class TransactionItemRequest(BaseModel):
    item_name: str
    qty: int
    unit_price: int
    category: Optional[str] = None


class TransactionRequest(BaseModel):
    id: str
    merchant: str
    amount: int
    date: str
    time: str
    item_count: int
    items: List[TransactionItemRequest]


# ==================================================
# RESPONSE MODELS
# ==================================================

class AnomalyItem(BaseModel):
    id: str
    type: str
    message: str
    detail: List[Dict[str, Any]] = []
    dismissed: bool = False


class TransactionDetailResponse(BaseModel):
    id: str
    merchant: str
    amount: int
    date: str
    time: str
    item_count: int
    anomalies: List[AnomalyItem]


# ==================================================
# ROUTES
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "anomaly_autoencoder"
    }


@app.post(
    "/predict",
    response_model=TransactionDetailResponse
)
def predict_transaction(transaction: TransactionRequest):

    anomalies = []

    # ==================================================
    # DEMO RULES
    # (sementara untuk Swagger/API contract)
    # ==================================================

    # SPENDING SPIKE
    if transaction.amount > 300000:

        anomalies.append(
            AnomalyItem(
                id="an_001",
                type="SPENDING_SPIKE",
                message="Pengeluaran lebih tinggi dari biasanya",
                detail=[
                    {
                        "usual_amount": 100000,
                        "current_amount": transaction.amount,
                        "ratio": round(transaction.amount / 100000, 2)
                    }
                ],
                dismissed=False
            )
        )

    # UNUSUAL TIME
    if transaction.time.startswith(("00", "01", "02", "03")):

        anomalies.append(
            AnomalyItem(
                id="an_002",
                type="UNUSUAL_TIME",
                message="Transaksi di luar jam biasa",
                detail=[
                    {
                        "usual_hour_range": "08:00 - 22:00",
                        "detected_hour": transaction.time
                    }
                ],
                dismissed=False
            )
        )

    # PRICE SPIKE
    for item in transaction.items:

        if item.unit_price > 30000:

            anomalies.append(
                AnomalyItem(
                    id="an_003",
                    type="PRICE_SPIKE",
                    message="Harga item naik 3× dari biasanya",
                    detail=[
                        {
                            "item_name": item.item_name,
                            "usual_price": 12000,
                            "current_price": item.unit_price
                        }
                    ],
                    dismissed=False
                )
            )

    # FREQUENCY SPIKE
    if transaction.merchant.lower() == "steam":

        anomalies.append(
            AnomalyItem(
                id="an_004",
                type="FREQUENCY_SPIKE",
                message="Frekuensi transaksi lebih tinggi dari biasanya",
                detail=[
                    {
                        "merchant": transaction.merchant,
                        "usual_frequency": 1,
                        "current_frequency": 4,
                        "period": "bulan"
                    }
                ],
                dismissed=False
            )
        )

    return TransactionDetailResponse(
        id=transaction.id,
        merchant=transaction.merchant,
        amount=transaction.amount,
        date=transaction.date,
        time=transaction.time,
        item_count=transaction.item_count,
        anomalies=anomalies
    )


@app.post(
    "/predict/batch",
    response_model=List[TransactionDetailResponse]
)
def predict_batch(
    transactions: List[TransactionRequest]
):

    results = []

    for trx in transactions:
        results.append(
            predict_transaction(trx)
        )

    return results