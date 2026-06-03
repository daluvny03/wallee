# ⚡ QUICK REFERENCE - Expense Forecasting API

## 🚀 Quick Start

```bash
# 1. Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 2. View interactive docs
# Browser: http://localhost:8000/docs

# 3. Run tests
python test_api.py
```

---

## 📍 Endpoint Summary

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| **GET** | `/health` | Server health check | ✅ Ready |
| **POST** | `/train` | Train models (first time) | ⚠️ Long-running |
| **POST** | `/predict` | Daily expense forecast | ✅ Fast |
| **POST** | `/budget-analysis` | Budget vs forecast analysis | ✅ Fast |
| **GET** | `/monthly-summary` | Historical trend + forecast | ✅ Fast |

---

## 📝 Request Format Cheat Sheet

### 1️⃣ GET /health
```json
// No body needed
```

### 2️⃣ POST /train
```
Content-Type: multipart/form-data

file: [CSV file]
?dl_epochs=80&dl_batch_size=32&arima_max_p=3&arima_max_q=3
```

### 3️⃣ POST /predict
```json
{
  "lag_1": 1500000,          // REQUIRED: expense yesterday
  "lag_2": 1600000,          // REQUIRED: 2 days ago
  "lag_3": 1550000,          // REQUIRED: 3 days ago
  "rolling_mean_7": 1550000, // REQUIRED: 7-day avg
  "transaction_count": 5,    // REQUIRED: today's txn count
  
  "day_of_week": 3,          // OPTIONAL (auto-generated)
  "month": 6,                // OPTIONAL (auto-generated)
  "is_weekend": 0,           // OPTIONAL (auto-generated)
  "mtd_progress": 0.5        // OPTIONAL (auto-generated)
}
```

### 4️⃣ POST /budget-analysis
```json
{
  "budget_target": 20000000  // REQUIRED: budget limit (Rp)
}
```

### 5️⃣ GET /monthly-summary
```
?n_months=6  // OPTIONAL: default 6
```

---

## 🔄 Response Structure

### Success (200)
```json
{
  "success": true,
  "message": "OK",
  "data": { /* endpoint-specific */ },
  "timestamp": "2026-06-03T10:30:45.123456"
}
```

### Error (4xx/5xx)
```json
{
  "detail": "Error message here"
}
```

---

## ⏱️ Estimated Timings

| Operation | Duration | Notes |
|-----------|----------|-------|
| Health Check | <100ms | Instant |
| Training | 5-15 min | Depends on dataset size |
| Prediction | <500ms | Very fast |
| Budget Analysis | <500ms | Very fast |
| Monthly Summary | <1s | Depends on n_months |

---

## 🎯 Response Fields by Endpoint

### /health
```
✓ status: "healthy"
✓ model_loaded: true/false
✓ version: "1.0.0"
```

### /train
```
✓ success: true/false
✓ message: string
✓ arima_order: (p,d,q)
✓ smape_arima: float (%)
✓ smape_dl_daily: float (%)
✓ ensemble_forecast: float (Rp)
✓ months_in_data: int
✓ timestamp: ISO string
```

### /predict
```
✓ success: true/false
✓ message: string
✓ dl_forecast: {
    forecast_rupiah: float (Rp),
    confidence_lower: float (Rp),
    confidence_upper: float (Rp),
    trend_pct: float (%),
    trend_direction: "↑" or "↓"
  }
✓ arima_forecast: float (Rp)
✓ ensemble_forecast: float (Rp)
✓ days_forecasted: int
✓ rolling_mean_30: float (Rp)
✓ timestamp: ISO string
```

### /budget-analysis
```
✓ budget_target: float (Rp)
✓ ensemble_forecast: float (Rp)
✓ variance: float (Rp)
✓ utilization_pct: float (%)
✓ status: "AMAN" or "OVER-BUDGET"
✓ message: string
```

### /monthly-summary
```
✓ historical: [
    { month: "2026-01", total_expense: 18500000 },
    ...
  ]
✓ next_month: "2026-07"
✓ forecast_rupiah: float (Rp)
```

---

## 💡 Usage Examples

### Minimal Predict Request
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1":1500000,"lag_2":1600000,"lag_3":1550000,
    "rolling_mean_7":1550000,"transaction_count":5
  }' | jq '.ensemble_forecast'
```

### Full Predict Request
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1":1500000,"lag_2":1600000,"lag_3":1550000,
    "rolling_mean_7":1550000,"rolling_mean_30":1575000,
    "transaction_count":5,"day_of_week":3,"month":6,
    "is_weekend":0,"mtd_progress":0.5
  }' | jq '.'
```

### Budget Analysis
```bash
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{"budget_target":20000000}' | jq '.status'
```

### Monthly Trend
```bash
curl -X GET "http://localhost:8000/monthly-summary?n_months=12" | \
  jq '.historical[] | "\(.month): \(.total_expense)"'
```

---

## 🚨 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 503 Service Unavailable | Model not loaded | Run POST /train first |
| 422 Unprocessable Entity | Missing required field | Check request body |
| 400 Bad Request | Invalid CSV format | Use correct date/expense columns |
| Connection refused | Server not running | `python -m uvicorn main:app ...` |
| Timeout | Training too long | Increase timeout or reduce epochs |

---

## 📊 Feature Index for /predict

```
Index  Feature               Type      Range/Unit
-----  -------               ----      -----------
0      lag_1                 float     Rp (required)
1      lag_2                 float     Rp (required)
2      lag_3                 float     Rp (required)
3      rolling_mean_7        float     Rp (required)
4      rolling_mean_30       float     Rp (calculated)
5      day_of_week           int       0-6 (auto)
6      month                 int       1-12 (auto)
7      is_weekend            int       0-1 (auto)
8      mtd_progress          float     0.0-1.0 (auto)
9      transaction_count     int       0-∞ (required)
```

---

## 🔐 CORS & Security

- CORS: ✅ Enabled for all origins (`*`)
- Authentication: ❌ Not required (open API)
- Rate limiting: ❌ Not implemented
- SSL/TLS: ❌ HTTP only (add reverse proxy for HTTPS)

**Recommendation**: For production, add:
- Rate limiting (slowapi)
- Authentication (JWT/API key)
- HTTPS (nginx/traefik)

---

## 📁 Project Structure

```
capstone project/
├── expense_forecasting_notebook.ipynb  (Notebook dengan FastAPI code)
├── API_DOCUMENTATION.md                (Full docs - Anda membaca ini)
├── CONTOH_REQUEST.md                   (Request examples)
├── QUICK_REFERENCE.md                  (Ini - cheat sheet)
├── test_api.py                         (Automated tests)
├── main.py                             (Standalone FastAPI app)
├── feature_engineered_finance_dataset.csv
├── forecast_model.keras
├── models/                             (Model files directory)
│   ├── forecast_model.keras
│   ├── scaler_X.save
│   ├── scaler_y.save
│   ├── scaler_exog.save
│   ├── arima_model.save
│   └── metadata.save
└── wallee/                             (Main project)
    ├── BE/ (Backend - Node.js)
    └── FE/ (Frontend - React)
```

---

## 🔗 API URL Patterns

```
Base URL: http://localhost:8000

Endpoints:
  GET     http://localhost:8000/health
  POST    http://localhost:8000/train
  POST    http://localhost:8000/predict
  POST    http://localhost:8000/budget-analysis
  GET     http://localhost:8000/monthly-summary?n_months=6

Docs:
  GET     http://localhost:8000/docs          (Swagger UI)
  GET     http://localhost:8000/redoc         (ReDoc)
  GET     http://localhost:8000/openapi.json  (OpenAPI spec)
```

---

## 📞 Quick Commands

```bash
# Check if server running
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs

# Run tests
python test_api.py

# Download OpenAPI spec
curl http://localhost:8000/openapi.json > openapi.json

# Format output
curl http://localhost:8000/health | jq '.'

# Save response to file
curl http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"lag_1":1500000,...}' > prediction.json
```

---

## 🎓 Learning Path

1. **Basics**: Run `GET /health` → understand response
2. **Training**: Run `POST /train` → wait for completion
3. **Prediction**: Run `POST /predict` → see 3 forecasts
4. **Analysis**: Run `POST /budget-analysis` → compare vs target
5. **Trends**: Run `GET /monthly-summary` → analyze history
6. **Integration**: Integrate into dashboard/mobile app

---

## 📞 Support

**Documentation**: See `API_DOCUMENTATION.md`
**Examples**: See `CONTOH_REQUEST.md`
**Tests**: Run `python test_api.py`
**Swagger**: Open `http://localhost:8000/docs`

---

*Last Updated: 2026-06-03*
*API Version: 1.0.0*
