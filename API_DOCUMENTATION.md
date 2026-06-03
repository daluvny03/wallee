# 📋 Dokumentasi API - Expense Forecasting

## 🔧 Konfigurasi Server
- **Base URL**: `http://localhost:8000`
- **Framework**: FastAPI
- **CORS**: Enabled untuk semua origin (`*`)
- **Model Directory**: `./models/` (auto-created)

---

## 📍 Endpoint Reference

### 1. **Health Check**
```
GET /health
```
**Fungsi**: Cek status server dan status model

**Request**: (Tidak ada body)

**Response Success (200)**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Response Failed**:
```json
{
  "status": "healthy",
  "model_loaded": false,
  "version": "1.0.0"
}
```

---

### 2. **Training Model** ⚠️ *Wajib dipanggil pertama kali*
```
POST /train
```
**Fungsi**: Upload CSV dataset dan latih semua model (ARIMA + Deep Learning)

**Request Format**: `multipart/form-data`

**Parameter URL Query**:
```
?dl_epochs=80           # Default: 80, Range: 1-500
&dl_batch_size=32       # Default: 32, Range: 8-256
&arima_max_p=3          # Default: 3, Range: 1-5
&arima_max_q=3          # Default: 3, Range: 1-5
```

**File Upload**:
- Field: `file` (required)
- Type: CSV file
- Expected Columns:
  - Kolom tanggal: `date` atau `tanggal`
  - Kolom pengeluaran: `total_harga` atau `expense`
  - Kolom kategori (opsional): `kategori` atau `category`

**Contoh Request (cURL)**:
```bash
curl -X POST "http://localhost:8000/train?dl_epochs=80&dl_batch_size=32" \
  -F "file=@feature_engineered_finance_dataset.csv"
```

**Contoh Request (Python)**:
```python
import requests

files = {'file': open('feature_engineered_finance_dataset.csv', 'rb')}
params = {
    'dl_epochs': 80,
    'dl_batch_size': 32,
    'arima_max_p': 3,
    'arima_max_q': 3
}

response = requests.post('http://localhost:8000/train', 
                         files=files, 
                         params=params)
print(response.json())
```

**Response Success (200)**:
```json
{
  "success": true,
  "message": "Training selesai. Model tersimpan.",
  "arima_order": [1, 1, 1],
  "smape_arima": 3.8,
  "smape_dl_daily": 12.5,
  "ensemble_forecast": 18750000.00,
  "months_in_data": 12,
  "timestamp": "2026-06-03T10:30:45.123456"
}
```

---

### 3. **Prediksi Pengeluaran**
```
POST /predict
```
**Fungsi**: Prediksi pengeluaran sisa bulan ini menggunakan Ensemble model

**Request Format**: `application/json`

**Body Schema**:
```json
{
  "lag_1": 1500000,              // Pengeluaran hari kemarin (Rp) [REQUIRED]
  "lag_2": 1600000,              // Pengeluaran 2 hari lalu (Rp) [REQUIRED]
  "lag_3": 1550000,              // Pengeluaran 3 hari lalu (Rp) [REQUIRED]
  "rolling_mean_7": 1550000,     // Rata-rata 7 hari (Rp) [REQUIRED]
  "transaction_count": 5,        // Jumlah transaksi hari ini [REQUIRED]
  
  "day_of_week": 3,              // 0=Senin, 6=Minggu [OPTIONAL - auto-generated]
  "month": 6,                    // 1-12 [OPTIONAL - auto-generated]
  "is_weekend": 0,               // 0 atau 1 [OPTIONAL - auto-generated]
  "mtd_progress": 0.5            // 0.0-1.0 [OPTIONAL - auto-generated]
}
```

**Contoh Request (cURL)**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": 1500000,
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "transaction_count": 5
  }'
```

**Contoh Request (Python)**:
```python
import requests

payload = {
    "lag_1": 1500000,
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "transaction_count": 5
}

response = requests.post('http://localhost:8000/predict', json=payload)
print(response.json())
```

**Response Success (200)**:
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
  "timestamp": "2026-06-03T10:35:22.654321",
  "rolling_mean_30": 1575000.00
}
```

**Response Error (503 - Model Not Loaded)**:
```json
{
  "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
}
```

---

### 4. **Analisis Anggaran**
```
POST /budget-analysis
```
**Fungsi**: Bandingkan target anggaran dengan prediksi ensemble

**Request Format**: `application/json`

**Body Schema**:
```json
{
  "budget_target": 20000000  // Target anggaran bulanan (Rp) [REQUIRED]
}
```

**Contoh Request (cURL)**:
```bash
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_target": 20000000
  }'
```

**Contoh Request (Python)**:
```python
import requests

payload = {"budget_target": 20000000}

response = requests.post('http://localhost:8000/budget-analysis', json=payload)
print(response.json())
```

**Response Success (200)**:
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

**Response Alternative (Over-Budget)**:
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

---

### 5. **Ringkasan Bulanan**
```
GET /monthly-summary
```
**Fungsi**: Ringkasan pengeluaran bulanan historis + prediksi bulan depan

**Request Format**: Query parameters

**Parameters**:
```
?n_months=6  # Jumlah bulan historis (default: 6)
```

**Contoh Request (cURL)**:
```bash
curl -X GET "http://localhost:8000/monthly-summary?n_months=6"
```

**Contoh Request (Python)**:
```python
import requests

params = {'n_months': 6}
response = requests.get('http://localhost:8000/monthly-summary', params=params)
print(response.json())
```

**Response Success (200)**:
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

---

## 🔄 Workflow Rekomendasi

```
1. GET /health
   ↓ Pastikan server running
   
2. POST /train (dengan CSV file)
   ↓ Latih model pertama kali
   
3. POST /predict (dengan fitur harian)
   ↓ Dapatkan prediksi sisa bulan
   
4. POST /budget-analysis (dengan budget target)
   ↓ Analisis kepatuhan anggaran
   
5. GET /monthly-summary
   ↓ Lihat tren historis
```

---

## 🚀 Cara Menjalankan Server

**Option 1: Direct (dari notebook cell terakhir)**
```python
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

**Option 2: Save as standalone file lalu jalankan**
```bash
# Simpan kode FastAPI ke file: app.py
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Access API Documentation**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ⚙️ Error Handling

### 400 - Bad Request
```json
{
  "detail": "Gagal baca CSV: [error message]"
}
```

### 422 - Unprocessable Entity
```json
{
  "detail": "Kolom date/expense tidak ditemukan."
}
```

### 503 - Service Unavailable
```json
{
  "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
}
```

---

## 📊 Model & Scaling Information

**Feature Names** (urutan penting untuk `/predict`):
```python
[
  'lag_1', 'lag_2', 'lag_3',
  'rolling_mean_7', 'rolling_mean_30',
  'day_of_week', 'month', 
  'is_weekend', 'mtd_progress',
  'transaction_count'
]
```

**Saved Files** (`./models/` directory):
```
├── forecast_model.keras      # Deep Learning model
├── scaler_X.save            # Input scaler
├── scaler_y.save            # Output scaler
├── scaler_exog.save         # Exogenous features scaler
├── arima_model.save         # ARIMA model
└── metadata.save            # Feature names & ARIMA order
```

---

## ✅ Testing Checklist

- [ ] Server running di port 8000
- [ ] `/health` returns `model_loaded: true`
- [ ] `/train` berhasil dengan CSV valid
- [ ] `/predict` returns forecast dengan semua 3 model
- [ ] `/budget-analysis` menampilkan status AMAN/OVER-BUDGET
- [ ] `/monthly-summary` menampilkan tren historis
