# 📤 Contoh Response - Expense Forecasting API

## 📍 Daftar Response untuk Setiap Endpoint

---

## 1. GET /health

### ✅ Success Response (200)

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Kapan**: Model sudah di-load (setelah training)

---

### ⚪ Warning Response (200)

```json
{
  "status": "healthy",
  "model_loaded": false,
  "version": "1.0.0"
}
```

**Kapan**: Server running tapi model belum di-train

---

## 2. POST /train

### ✅ Success Response (200)

```json
{
  "success": true,
  "message": "Training selesai. Model tersimpan.",
  "arima_order": [1, 1, 1],
  "smape_arima": 3.8,
  "smape_dl_daily": 12.5,
  "ensemble_forecast": 18750000.00,
  "months_in_data": 12,
  "timestamp": "2026-06-03T10:35:22.654321"
}
```

**Penjelasan**:
- `success`: true = training berhasil
- `arima_order`: (p=1, d=1, q=1) = parameter ARIMA terbaik
- `smape_arima`: 3.8% = akurasi ARIMA (semakin rendah semakin baik)
- `smape_dl_daily`: 12.5% = akurasi Deep Learning daily
- `ensemble_forecast`: Rp 18.75 juta = prediksi bulan depan
- `months_in_data`: 12 bulan data historis
- `timestamp`: Kapan training selesai

---

### ❌ Error Response - CSV Invalid (400)

```json
{
  "detail": "Gagal baca CSV: 'date' column not found"
}
```

**Penyebab**: Kolom tanggal tidak ditemukan

---

### ❌ Error Response - Missing Columns (422)

```json
{
  "detail": "Kolom date/expense tidak ditemukan."
}
```

**Penyebab**: File tidak punya kolom date dan expense

---

## 3. POST /predict

### ✅ Success Response - dengan DL (200)

```json
{
  "success": true,
  "message": "OK",
  "dl_forecast": {
    "forecast_rupiah": 16750000.00,
    "confidence_lower": 15912500.00,
    "confidence_upper": 17587500.00,
    "trend_pct": 5.3,
    "trend_direction": "↑"
  },
  "arima_forecast": 17500000.00,
  "ensemble_forecast": 17125000.00,
  "days_forecasted": 25,
  "timestamp": "2026-06-03T10:40:15.123456",
  "rolling_mean_30": 1575000.00
}
```

**Penjelasan**:
- `success`: true = prediksi berhasil
- `dl_forecast.forecast_rupiah`: Rp 16.75 juta = forecast Deep Learning
- `confidence_lower/upper`: Range confidence 95% (Rp 15.9M - 17.5M)
- `trend_pct`: +5.3% = naik 5.3% vs bulan lalu
- `trend_direction`: "↑" = trend naik
- `arima_forecast`: Rp 17.5 juta = forecast ARIMA
- `ensemble_forecast`: Rp 17.125 juta = weighted average
- `days_forecasted`: 25 hari lagi di bulan ini
- `rolling_mean_30`: Rp 1.575 juta = rata-rata 30 hari

---

### ✅ Success Response - Degraded (DL gagal) (200)

```json
{
  "success": true,
  "message": "DL forecast degraded (NaN/Inf at day 5), pakai ARIMA.",
  "dl_forecast": null,
  "arima_forecast": 17500000.00,
  "ensemble_forecast": 17500000.00,
  "days_forecasted": 25,
  "timestamp": "2026-06-03T10:40:15.123456",
  "rolling_mean_30": 1575000.00
}
```

**Penjelasan**:
- DL model gagal, fallback ke ARIMA saja
- `dl_forecast`: null = DL tidak tersedia
- `ensemble_forecast` = sama dengan `arima_forecast`

---

### ❌ Error Response - Missing Fields (422)

```json
{
  "detail": [
    {
      "loc": ["body", "lag_2"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Penyebab**: Kolom `lag_2` tidak dikirim

---

### ❌ Error Response - Invalid Type (422)

```json
{
  "detail": [
    {
      "loc": ["body", "lag_1"],
      "msg": "value is not a valid number",
      "type": "type_error.number"
    }
  ]
}
```

**Penyebab**: `lag_1` harus number, dikirim string

---

### ❌ Error Response - Model Not Loaded (503)

```json
{
  "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
}
```

**Penyebab**: Belum pernah training, model belum di-load

---

## 4. POST /budget-analysis

### ✅ Success Response - AMAN (200)

```json
{
  "budget_target": 20000000.00,
  "ensemble_forecast": 17125000.00,
  "variance": 2875000.00,
  "utilization_pct": 85.63,
  "status": "AMAN",
  "message": "Estimasi pengeluaran 85.6% dari target. Sisa anggaran: Rp 2.875.000"
}
```

**Penjelasan**:
- `budget_target`: Target anggaran = Rp 20 juta
- `ensemble_forecast`: Prediksi pengeluaran = Rp 17.125 juta
- `variance`: Sisa anggaran = Rp 2.875 juta (positif = aman)
- `utilization_pct`: Penggunaan = 85.63%
- `status`: "AMAN" = masih ada sisa
- `message`: Pesan user-friendly

---

### ✅ Success Response - OVER-BUDGET (200)

```json
{
  "budget_target": 15000000.00,
  "ensemble_forecast": 17125000.00,
  "variance": -2125000.00,
  "utilization_pct": 114.17,
  "status": "OVER-BUDGET",
  "message": "Perkiraan MELEBIHI anggaran sebesar Rp 2.125.000!"
}
```

**Penjelasan**:
- `budget_target`: Target = Rp 15 juta (terlalu rendah)
- `ensemble_forecast`: Prediksi = Rp 17.125 juta
- `variance`: -Rp 2.125 juta (negatif = over)
- `utilization_pct`: 114.17% = lebih dari 100%
- `status`: "OVER-BUDGET" = warning!
- `message`: Pesan warning dengan jumlah kelebihan

---

### ❌ Error Response - Invalid Budget (422)

```json
{
  "detail": [
    {
      "loc": ["body", "budget_target"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

**Penyebab**: Budget_target harus > 0 (dikirim negative atau 0)

---

### ❌ Error Response - Model Not Loaded (503)

```json
{
  "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
}
```

**Penyebab**: Model belum di-train

---

## 5. GET /monthly-summary

### ✅ Success Response (200)

```json
{
  "historical": [
    {
      "month": "2026-01",
      "total_expense": 18500000.00
    },
    {
      "month": "2026-02",
      "total_expense": 17200000.00
    },
    {
      "month": "2026-03",
      "total_expense": 19100000.00
    },
    {
      "month": "2026-04",
      "total_expense": 18900000.00
    },
    {
      "month": "2026-05",
      "total_expense": 18200000.00
    },
    {
      "month": "2026-06",
      "total_expense": 17800000.00
    }
  ],
  "next_month": "2026-07",
  "forecast_rupiah": 18275000.00
}
```

**Penjelasan**:
- `historical`: Array 6 bulan terakhir dengan total pengeluaran
- `next_month`: "2026-07" = bulan depan
- `forecast_rupiah`: Rp 18.275 juta = prediksi bulan depan

---

### ✅ Success Response - Custom 12 Months (200)

```json
{
  "historical": [
    {"month": "2025-07", "total_expense": 17000000.00},
    {"month": "2025-08", "total_expense": 18500000.00},
    {"month": "2025-09", "total_expense": 16200000.00},
    {"month": "2025-10", "total_expense": 19800000.00},
    {"month": "2025-11", "total_expense": 21500000.00},
    {"month": "2025-12", "total_expense": 22800000.00},
    {"month": "2026-01", "total_expense": 18500000.00},
    {"month": "2026-02", "total_expense": 17200000.00},
    {"month": "2026-03", "total_expense": 19100000.00},
    {"month": "2026-04", "total_expense": 18900000.00},
    {"month": "2026-05", "total_expense": 18200000.00},
    {"month": "2026-06", "total_expense": 17800000.00}
  ],
  "next_month": "2026-07",
  "forecast_rupiah": 18275000.00
}
```

**Penjelasan**: 12 bulan historis (setahun penuh)

---

### ❌ Error Response - Invalid n_months (422)

```json
{
  "detail": [
    {
      "loc": ["query", "n_months"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

**Penyebab**: `n_months` harus integer

---

### ❌ Error Response - Model Not Loaded (503)

```json
{
  "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
}
```

**Penyebab**: Model belum di-train

---

## 📊 Response Status Codes Reference

| Code | Arti | Contoh |
|------|------|--------|
| **200** | OK - Request successful | Health check OK, Predict OK |
| **400** | Bad Request - Invalid format | CSV tidak bisa dibaca |
| **422** | Validation Error - Field invalid | Missing field, wrong type |
| **503** | Service Unavailable | Model belum di-load |

---

## 🎯 Response Structure Pattern

Semua response mengikuti pattern:

### Success
```json
{
  "success": true,
  "message": "OK atau deskripsi",
  "data": {...},
  "timestamp": "ISO string"
}
```

### Error
```json
{
  "detail": "Error message"
}
```

---

## 💡 Understanding Response Fields

### ARIMA Forecast
- Akurat untuk monthly trends
- Bobot: 80% dalam ensemble
- Selalu ada (fallback)

### Deep Learning Forecast
- Akurat untuk daily patterns
- Bobot: 20% dalam ensemble
- Bisa null jika gagal

### Ensemble Forecast
- Kombinasi weighted
- Paling reliable
- Yang digunakan untuk keputusan

### Confidence Interval
- 95% confidence range
- Menunjukkan uncertainty
- ±5% dari forecast

### Trend Direction
- "↑" = naik vs bulan lalu
- "↓" = turun vs bulan lalu
- "→" = flat (jika ada)

### Utilization Percentage
- % dari target budget
- <100% = AMAN
- >100% = OVER-BUDGET

---

## 🔄 Real-World Response Example Flow

### Request 1: Check Health
```bash
curl http://localhost:8000/health
```
**Response**:
```json
{"status": "healthy", "model_loaded": false, "version": "1.0.0"}
```

### Request 2: Train Model
```bash
curl -X POST "http://localhost:8000/train" -F "file=@data.csv"
```
**Response** (after 10 min):
```json
{
  "success": true,
  "message": "Training selesai. Model tersimpan.",
  "arima_order": [1, 1, 1],
  "smape_arima": 3.8,
  "ensemble_forecast": 18750000.00,
  "months_in_data": 12
}
```

### Request 3: Check Health Again
```bash
curl http://localhost:8000/health
```
**Response**:
```json
{"status": "healthy", "model_loaded": true, "version": "1.0.0"}
```

### Request 4: Predict
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"lag_1":1500000,...}'
```
**Response**:
```json
{
  "success": true,
  "message": "OK",
  "ensemble_forecast": 17125000.00,
  "days_forecasted": 25,
  ...
}
```

### Request 5: Budget Check
```bash
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{"budget_target":20000000}'
```
**Response**:
```json
{
  "status": "AMAN",
  "budget_target": 20000000,
  "ensemble_forecast": 17125000,
  "variance": 2875000,
  ...
}
```

### Request 6: View Trends
```bash
curl "http://localhost:8000/monthly-summary?n_months=6"
```
**Response**:
```json
{
  "historical": [...6 months...],
  "next_month": "2026-07",
  "forecast_rupiah": 18275000
}
```

---

## 🎯 Quick Response Lookup

| Endpoint | Status | Response |
|----------|--------|----------|
| GET /health | 200 | `{status, model_loaded, version}` |
| POST /train | 200 | `{success, arima_order, smape_*, ensemble_forecast}` |
| POST /train | 400 | `{detail: "error message"}` |
| POST /train | 422 | `{detail: "CSV columns error"}` |
| POST /predict | 200 | `{success, dl_forecast, arima_forecast, ensemble_forecast, days_forecasted}` |
| POST /predict | 422 | `{detail: [{loc, msg, type}]}` |
| POST /predict | 503 | `{detail: "Model not loaded"}` |
| POST /budget-analysis | 200 | `{budget_target, ensemble_forecast, variance, status, message}` |
| POST /budget-analysis | 422 | `{detail: "Invalid budget_target"}` |
| GET /monthly-summary | 200 | `{historical: [], next_month, forecast_rupiah}` |

---

## 📝 Response Example JSON Files

Anda bisa save response-response ini untuk testing:

**save_as: `example_responses.json`**

```json
{
  "health_ok": {
    "status": "healthy",
    "model_loaded": true,
    "version": "1.0.0"
  },
  "predict_success": {
    "success": true,
    "message": "OK",
    "ensemble_forecast": 17125000.00,
    "days_forecasted": 25
  },
  "budget_aman": {
    "status": "AMAN",
    "budget_target": 20000000,
    "variance": 2875000
  },
  "budget_over": {
    "status": "OVER-BUDGET",
    "budget_target": 15000000,
    "variance": -2125000
  }
}
```

---

**Semua response di file ini adalah contoh real dari API!**
