"""
Expense Forecasting API - Standalone FastAPI Application
Extracted from: expense_forecasting_notebook (3).ipynb

Installation:
  pip install fastapi uvicorn scikit-learn joblib pandas numpy tensorflow statsmodels

Run:
  python main.py
  
Or:
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  
Then open:
  http://localhost:8000/docs          (Swagger UI)
  http://localhost:8000/redoc         (ReDoc)
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from itertools import product
from typing import Optional, List
import joblib
import io

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from contextlib import asynccontextmanager

# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model & scalers saat startup."""
    load_models()
    yield
    # cleanup (opsional)


app = FastAPI(
    title="Expense Forecasting API",
    description=(
        "API untuk prediksi pengeluaran bulanan menggunakan Ensemble Model "
        "(ARIMA + SARIMAX + Deep Learning). Upload CSV untuk training atau "
        "gunakan endpoint /predict untuk inferensi langsung."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE
# ============================================================================

model_state: dict = {
    "dl_model": None,
    "scaler_X": None,
    "scaler_y": None,
    "scaler_exog": None,
    "arima_model": None,
    "sarimax_model": None,
    "monthly_data": None,
    "feature_names": None,
    "best_order": None,
    "loaded": False,
}

MODEL_DIR = os.getenv("MODEL_DIR", "models")


def load_models():
    """Muat semua model & scaler dari disk jika tersedia."""
    paths = {
        "dl_model":    os.path.join(MODEL_DIR, "forecast_model.keras"),
        "scaler_X":    os.path.join(MODEL_DIR, "scaler_X.save"),
        "scaler_y":    os.path.join(MODEL_DIR, "scaler_y.save"),
        "scaler_exog": os.path.join(MODEL_DIR, "scaler_exog.save"),
        "arima_model": os.path.join(MODEL_DIR, "arima_model.save"),
        "metadata":    os.path.join(MODEL_DIR, "metadata.save"),
    }

    all_exist = all(os.path.exists(p) for p in paths.values())
    if not all_exist:
        print("⚠️  Model files not found — jalankan /train terlebih dahulu.")
        return

    try:
        import tensorflow as tf
        model_state["dl_model"]    = tf.keras.models.load_model(paths["dl_model"])
        model_state["scaler_X"]    = joblib.load(paths["scaler_X"])
        model_state["scaler_y"]    = joblib.load(paths["scaler_y"])
        model_state["scaler_exog"] = joblib.load(paths["scaler_exog"])
        model_state["arima_model"] = joblib.load(paths["arima_model"])
        meta = joblib.load(paths["metadata"])
        model_state["monthly_data"]   = meta["monthly_data"]
        model_state["feature_names"]  = meta["feature_names"]
        model_state["best_order"]     = meta["best_order"]
        model_state["loaded"] = True
        print(f"✅ Models loaded from '{MODEL_DIR}'")
    except Exception as e:
        print(f"❌ Error loading models: {e}")


def require_models():
    """Dependency — raise 503 jika model belum dimuat."""
    if not model_state["loaded"]:
        raise HTTPException(
            status_code=503,
            detail="Model belum tersedia. Jalankan POST /train terlebih dahulu.",
        )


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class TrainRequest(BaseModel):
    dl_epochs:    int   = Field(80,  ge=1,  le=500,  description="Jumlah epoch training DL")
    dl_batch_size:int   = Field(32,  ge=8,  le=256,  description="Batch size DL")
    arima_max_p:  int   = Field(3,   ge=1,  le=5,    description="ARIMA max P")
    arima_max_q:  int   = Field(3,   ge=1,  le=5,    description="ARIMA max Q")


class PredictRequest(BaseModel):
    lag_1:             float = Field(..., description="Pengeluaran hari lalu (Rp)")
    lag_2:             float = Field(..., description="Pengeluaran 2 hari lalu (Rp)")
    lag_3:             float = Field(..., description="Pengeluaran 3 hari lalu (Rp)")
    rolling_mean_7:    float = Field(..., description="Rata-rata 7 hari terakhir (Rp)")
    transaction_count: int   = Field(..., ge=0, description="Jumlah transaksi hari ini")
    day_of_week:       Optional[int]   = Field(None, ge=0, le=6)
    month:             Optional[int]   = Field(None, ge=1, le=12)
    is_weekend:        Optional[int]   = Field(None, ge=0, le=1)
    mtd_progress:      Optional[float] = Field(None, ge=0.0, le=1.0)


class BudgetAnalysisRequest(BaseModel):
    budget_target: float = Field(..., gt=0, description="Target anggaran bulanan (Rp)")


class ForecastResult(BaseModel):
    forecast_rupiah:    float
    confidence_lower:   float
    confidence_upper:   float
    trend_pct:          float
    trend_direction:    str


class PredictResponse(BaseModel):
    success:           bool
    message:           str
    dl_forecast:       Optional[ForecastResult] = None
    arima_forecast:    Optional[float]           = None
    ensemble_forecast: Optional[float]           = None
    days_forecasted:   Optional[int]             = None
    timestamp:         str                       = Field(default_factory=lambda: datetime.now().isoformat())
    rolling_mean_30: float


class TrainResponse(BaseModel):
    success:          bool
    message:          str
    arima_order:      Optional[tuple]  = None
    smape_arima:      Optional[float]  = None
    smape_dl_daily:   Optional[float]  = None
    ensemble_forecast:Optional[float]  = None
    months_in_data:   Optional[int]    = None
    timestamp:        str              = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    status:       str
    model_loaded: bool
    version:      str = "1.0.0"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_features(df_daily: pd.DataFrame, df_raw: pd.DataFrame,
                    date_col: str, expense_col: str) -> pd.DataFrame:
    """Feature engineering untuk daily expenses."""
    feats = df_daily.copy()
    
    # Lags & rolling means
    for lag in [1, 2, 3, 7, 30]:
        feats[f"lag_{lag}"] = feats["daily_expense"].shift(lag)
    
    for w in [7, 30]:
        feats[f"rolling_mean_{w}"] = feats["daily_expense"].rolling(w, min_periods=1).mean()
    
    # Temporal features
    feats["day_of_week"]   = feats["date"].dt.dayofweek
    feats["month"]         = feats["date"].dt.month
    feats["day_of_month"]  = feats["date"].dt.day
    feats["is_weekend"]    = (feats["day_of_week"] >= 5).astype(int)
    feats["days_in_month"] = feats["date"].dt.days_in_month
    feats["mtd_progress"]  = ((feats["day_of_month"] - 1) / (feats["days_in_month"] - 1)).clip(0, 1)
    
    # Transaction count
    txn = df_raw.groupby(df_raw[date_col].dt.date).size().reset_index()
    txn.columns = ["date", "transaction_count"]
    txn["date"] = pd.to_datetime(txn["date"])
    feats = feats.merge(txn, on="date", how="left")
    feats["transaction_count"] = feats["transaction_count"].fillna(0)
    
    return feats


def recursive_forecast(start_features: np.ndarray, remaining_days: int,
                        model, scaler_X, scaler_y,
                        feature_names: List[str]):
    """Recursive daily forecasting untuk monthly total."""
    current = start_features.copy()
    daily_preds = []
    
    try:
        for day in range(remaining_days):
            scaled = scaler_X.transform(current)
            pred_scaled = model.predict(scaled, verbose=0)
            pred = float(scaler_y.inverse_transform(pred_scaled).flatten()[0])
            
            if np.isnan(pred) or np.isinf(pred):
                return 0.0, False, f"NaN/Inf at day {day}", daily_preds
            
            pred = max(0.0, pred)
            daily_preds.append(pred)

            # Update features
            new = current[0].copy()
            
            def fi(name):
                return feature_names.index(name) if name in feature_names else None

            if fi("lag_3") is not None: new[fi("lag_3")] = new[fi("lag_2")] if fi("lag_2") is not None else 0
            if fi("lag_2") is not None: new[fi("lag_2")] = new[fi("lag_1")] if fi("lag_1") is not None else 0
            if fi("lag_1") is not None: new[fi("lag_1")] = pred
            if fi("rolling_mean_7") is not None:
                new[fi("rolling_mean_7")] = 0.3 * pred + 0.7 * new[fi("rolling_mean_7")]
            if fi("mtd_progress") is not None:
                new[fi("mtd_progress")] = min(1.0, new[fi("mtd_progress")] + 1 / 30)
            if fi("day_of_month") is not None:
                new[fi("day_of_month")] += 1
            
            current = new.reshape(1, -1)

        return sum(daily_preds), True, "OK", daily_preds
    except Exception as e:
        return 0.0, False, str(e), daily_preds


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric Mean Absolute Percentage Error."""
    return float(
        100 * np.mean(
            2 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred) + 1e-8)
        )
    )


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Utility"])
def health():
    """Cek status server dan model."""
    return HealthResponse(status="healthy", model_loaded=model_state["loaded"])


@app.post("/train", response_model=TrainResponse, tags=["Training"])
async def train(
    file: UploadFile = File(..., description="CSV dataset pengeluaran"),
    dl_epochs: int = Field(80, ge=1, le=500),
    dl_batch_size: int = Field(32, ge=8, le=256),
    arima_max_p: int = Field(3, ge=1, le=5),
    arima_max_q: int = Field(3, ge=1, le=5),
):
    """Upload CSV dan latih semua model (ARIMA + Deep Learning)."""
    import tensorflow as tf
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from tensorflow.keras import layers, Model, Input
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

    try:
        content   = await file.read()
        df_raw    = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal baca CSV: {e}")

    # Auto-detect kolom
    date_col = expense_col = cat_col = None
    for col in df_raw.columns:
        low = col.lower()
        if "date" in low or "tanggal" in low: date_col    = col
        if "total_harga" in low or "expense" in low: expense_col = col
        if "kategori" in low or "category" in low: cat_col     = col

    if not date_col or not expense_col:
        raise HTTPException(status_code=422, detail="Kolom date/expense tidak ditemukan.")

    df_raw[date_col] = pd.to_datetime(df_raw[date_col])
    df_raw = df_raw.dropna(subset=[date_col])

    # Daily & monthly aggregation
    daily = (df_raw.groupby(date_col)[expense_col].sum()
               .reset_index().rename(columns={date_col: "date", expense_col: "daily_expense"})
               .set_index("date").asfreq("D", fill_value=0).reset_index())

    monthly = (df_raw.groupby(df_raw[date_col].dt.to_period("M"))[expense_col]
                 .sum().reset_index())
    monthly.columns = ["month", "total_expense"]
    monthly["month"] = monthly["month"].astype(str)

    # Feature engineering
    feature_df = create_features(daily, df_raw, date_col, expense_col)

    # ── ARIMA ───────────────────────────────────────────────
    monthly_vals = monthly["total_expense"].values
    best_aic, best_order = np.inf, (1, 1, 1)
    
    for p, d, q in product(range(arima_max_p), range(2), range(arima_max_q)):
        if p == 0 and q == 0: continue
        try:
            m = ARIMA(monthly_vals, order=(p, d, q)).fit()
            if m.aic < best_aic:
                best_aic, best_order = m.aic, (p, d, q)
        except:
            continue

    arima_model   = ARIMA(monthly_vals, order=best_order).fit()
    arima_forecast = arima_model.forecast(steps=2)

    arima_smape = 0.0
    if len(monthly_vals) > 3:
        arima_eval   = ARIMA(monthly_vals[:-3], order=best_order).fit()
        pred_arima   = arima_eval.forecast(3)
        arima_smape  = smape(monthly_vals[-3:], pred_arima)

    # ── Deep Learning ────────────────────────────────────────
    dl_feats  = ["lag_1","lag_2","lag_3","rolling_mean_7","rolling_mean_30",
                 "day_of_week","month","is_weekend","mtd_progress","transaction_count"]
    available = [f for f in dl_feats if f in feature_df.columns]
    
    X = feature_df[available].fillna(0).values
    y = feature_df["daily_expense"].shift(-1).fillna(0).values[:-1]
    X = X[:-1]

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_train_s = scaler_X.fit_transform(X_train)
    X_test_s  = scaler_X.transform(X_test)
    y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_test_s  = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

    # Build DL model
    inputs  = Input(shape=(X_train_s.shape[1],))
    x       = layers.Dense(128, activation="relu")(inputs)
    x       = layers.Dropout(0.2)(x)
    x       = layers.Dense(64, activation="relu")(x)
    x       = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1)(x)
    dl_model = Model(inputs, outputs)
    dl_model.compile(optimizer="adam", loss="huber", metrics=["mae"])

    # Train
    dl_model.fit(
        X_train_s, y_train_s,
        validation_data=(X_test_s, y_test_s),
        epochs=dl_epochs,
        batch_size=dl_batch_size,
        callbacks=[
            EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5),
        ],
        verbose=0,
    )

    # Evaluate DL
    y_pred_dl = scaler_y.inverse_transform(
        dl_model.predict(X_test_s, verbose=0)
    ).flatten()
    dl_smape = smape(y_test, y_pred_dl)

    # Ensemble forecast
    last_feats = feature_df[available].fillna(0).values[-1].reshape(1, -1)
    now        = datetime.now()
    days_left  = max(1, (now.replace(day=1, month=now.month % 12 + 1, year=now.year + (1 if now.month == 12 else 0)) - now).days)
    
    dl_total, dl_ok, _, _ = recursive_forecast(last_feats, days_left, dl_model, scaler_X, scaler_y, available)

    arima_next = float(arima_forecast[0])
    if dl_ok and dl_total > 0:
        ensemble = 0.8 * arima_next + 0.2 * dl_total
    else:
        ensemble = arima_next

    # SARIMAX scaler
    monthly_exog = daily.copy()
    monthly_exog["month_period"] = daily["date"].dt.to_period("M")
    me = monthly_exog.groupby("month_period").agg(
        total_expense=("daily_expense","sum"), days_in_month=("date","count")
    ).reset_index()
    txn_m = df_raw.groupby(df_raw[date_col].dt.to_period("M")).size().reset_index()
    txn_m.columns = ["month_period", "transaction_count"]
    me = me.merge(txn_m, on="month_period", how="left").fillna(0)
    scaler_exog = StandardScaler()
    scaler_exog.fit(me[["days_in_month","transaction_count"]])

    # Save models
    os.makedirs(MODEL_DIR, exist_ok=True)
    dl_model.save(os.path.join(MODEL_DIR, "forecast_model.keras"))
    joblib.dump(scaler_X,    os.path.join(MODEL_DIR, "scaler_X.save"))
    joblib.dump(scaler_y,    os.path.join(MODEL_DIR, "scaler_y.save"))
    joblib.dump(scaler_exog, os.path.join(MODEL_DIR, "scaler_exog.save"))
    joblib.dump(arima_model, os.path.join(MODEL_DIR, "arima_model.save"))
    joblib.dump({
        "monthly_data":  monthly.to_dict(orient="records"),
        "feature_names": available,
        "best_order":    best_order,
    }, os.path.join(MODEL_DIR, "metadata.save"))

    # Update state
    model_state.update({
        "dl_model":     dl_model,
        "scaler_X":     scaler_X,
        "scaler_y":     scaler_y,
        "scaler_exog":  scaler_exog,
        "arima_model":  arima_model,
        "monthly_data": monthly.to_dict(orient="records"),
        "feature_names":available,
        "best_order":   best_order,
        "loaded":       True,
    })

    return TrainResponse(
        success=True,
        message="Training selesai. Model tersimpan.",
        arima_order=best_order,
        smape_arima=round(arima_smape, 2),
        smape_dl_daily=round(dl_smape, 2),
        ensemble_forecast=round(ensemble, 2),
        months_in_data=len(monthly),
    )


@app.post("/predict", response_model=PredictResponse, tags=["Inference"],
          dependencies=[Depends(require_models)])
def predict(req: PredictRequest):
    """Prediksi pengeluaran sisa bulan ini."""
    now = datetime.now()
    dow  = req.day_of_week if req.day_of_week is not None else now.weekday()
    mon  = req.month        if req.month        is not None else now.month
    we   = req.is_weekend   if req.is_weekend   is not None else int(dow >= 5)
    
    if req.mtd_progress is None:
        dim = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        mt  = (now.day - 1) / max(1, dim.day - 1)
    else:
        mt = req.mtd_progress

    feature_names = model_state["feature_names"]
    n_feat        = model_state["scaler_X"].n_features_in_

    # Build feature vector
    feat_map = {
        "lag_1":             req.lag_1,
        "lag_2":             req.lag_2,
        "lag_3":             req.lag_3,
        "rolling_mean_7":    req.rolling_mean_7,
        "rolling_mean_30":   req.rolling_mean_7,
        "day_of_week":       dow,
        "month":             mon,
        "is_weekend":        we,
        "mtd_progress":      mt,
        "transaction_count": req.transaction_count,
    }
    feat_vec = np.array([[feat_map.get(f, 0) for f in feature_names]], dtype=np.float32)
    if feat_vec.shape[1] != n_feat:
        feat_vec = feat_vec[:, :n_feat]

    # Days left in month
    next_month   = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
    days_left    = max(1, (next_month - now).days)

    # DL recursive forecast
    dl_total, dl_ok, dl_msg, _ = recursive_forecast(
        feat_vec, days_left,
        model_state["dl_model"],
        model_state["scaler_X"],
        model_state["scaler_y"],
        feature_names,
    )

    # ARIMA forecast
    arima_model   = model_state["arima_model"]
    arima_vals    = arima_model.forecast(steps=1)
    arima_next    = float(arima_vals[0])

    # Ensemble
    if dl_ok and dl_total > 0:
        ensemble = 0.8 * arima_next + 0.2 * dl_total
    else:
        ensemble = arima_next

    # Trend calculation
    monthly_data = pd.DataFrame(model_state["monthly_data"])
    last_actual  = float(monthly_data["total_expense"].iloc[-1]) if len(monthly_data) else ensemble
    pct          = (ensemble - last_actual) / max(1, last_actual) * 100
    ci_margin    = ensemble * 0.05

    dl_result = None
    if dl_ok:
        dl_pct = (dl_total - last_actual) / max(1, last_actual) * 100
        dl_result = ForecastResult(
            forecast_rupiah=round(dl_total, 2),
            confidence_lower=round(dl_total * 0.95, 2),
            confidence_upper=round(dl_total * 1.05, 2),
            trend_pct=round(dl_pct, 2),
            trend_direction="↑" if dl_pct >= 0 else "↓",
        )

    return PredictResponse(
        success=True,
        message="OK" if dl_ok else f"DL forecast degraded ({dl_msg}), pakai ARIMA.",
        dl_forecast=dl_result,
        arima_forecast=round(arima_next, 2),
        ensemble_forecast=round(ensemble, 2),
        days_forecasted=days_left,
        rolling_mean_30=req.rolling_mean_7,
    )


@app.post("/budget-analysis", tags=["Analysis"],
          dependencies=[Depends(require_models)])
def budget_analysis(req: BudgetAnalysisRequest):
    """Analisis budget vs forecast."""
    arima_vals = model_state["arima_model"].forecast(steps=1)
    ensemble   = float(arima_vals[0])
    variance   = req.budget_target - ensemble
    utilization = (ensemble / req.budget_target) * 100

    return {
        "budget_target":    round(req.budget_target, 2),
        "ensemble_forecast":round(ensemble, 2),
        "variance":         round(variance, 2),
        "utilization_pct":  round(utilization, 2),
        "status":           "AMAN" if variance >= 0 else "OVER-BUDGET",
        "message": (
            f"Estimasi pengeluaran {round(utilization,1)}% dari target."
            f" Sisa anggaran: Rp {variance:,.0f}"
            if variance >= 0
            else f"Perkiraan MELEBIHI anggaran sebesar Rp {abs(variance):,.0f}!"
        ),
    }


@app.get("/monthly-summary", tags=["Analysis"],
         dependencies=[Depends(require_models)])
def monthly_summary(n_months: int = 6):
    """Ringkasan pengeluaran bulanan."""
    monthly_data  = pd.DataFrame(model_state["monthly_data"])
    last_n        = monthly_data.tail(n_months).to_dict(orient="records")
    arima_vals    = model_state["arima_model"].forecast(steps=1)
    next_forecast = float(arima_vals[0])
    next_month    = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1)

    return {
        "historical":      last_n,
        "next_month":      next_month.strftime("%Y-%m"),
        "forecast_rupiah": round(next_forecast, 2),
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Expense Forecasting API")
    print("="*70)
    print("📍 Starting server on http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔄 Reload: Enabled")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
