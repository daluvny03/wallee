from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.anomaly_service import AnomalyService

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Personal Finance — Anomaly Detection API",
    version="2.0.0",
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

class RelatedItem(BaseModel):
    item_name: str
    usual_price: Optional[int] = None
    current_price: Optional[int] = None


class AnomalyItem(BaseModel):
    id: str
    type: str
    message: str
    related_items: List[RelatedItem] = []
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

    # ==========================================
    # DEMO RULES
    # ==========================================

    if transaction.amount > 300000:

        anomalies.append(
            AnomalyItem(
                id="an_001",
                type="SPENDING_SPIKE",
                message="Pengeluaran lebih tinggi dari biasanya",
                dismissed=False
            )
        )

    if transaction.time.startswith("00") \
       or transaction.time.startswith("01") \
       or transaction.time.startswith("02") \
       or transaction.time.startswith("03"):

        anomalies.append(
            AnomalyItem(
                id="an_002",
                type="UNUSUAL_TIME",
                message="Transaksi di luar jam biasa",
                dismissed=False
            )
        )

    for item in transaction.items:

        if item.unit_price > 30000:

            anomalies.append(
                AnomalyItem(
                    id="an_003",
                    type="PRICE_SPIKE",
                    message="Harga item naik 3× dari biasanya",
                    related_items=[
                        RelatedItem(
                            item_name=item.item_name,
                            usual_price=12000,
                            current_price=item.unit_price
                        )
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