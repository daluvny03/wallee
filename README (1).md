# 💰 Finance Forecast & Budget Tracker API

Proyek ini menyediakan layanan API untuk memprediksi pengeluaran harian dan bulanan menggunakan model Deep Learning (TensorFlow) dan Ensemble (ARIMA-Heavy).

## 🛠️ Fitur Utama
- **Forecasting**: Prediksi pengeluaran berdasarkan data historis.
- **Budget Tracker**: Konsolidasi data pengeluaran riil (MTD) dengan sisa hari hasil prediksi.
- **FastAPI Integration**: Siap dideploy sebagai layanan web.

## 📂 Struktur File
- `main.py`: Server FastAPI untuk inference.
- `test_api.py`: Skrip untuk menguji koneksi API.
- `forecast_model.keras`: Model Deep Learning yang sudah dilatih.
- `scaler_X.save` & `scaler_y.save`: File normalisasi fitur.
- `requirements.txt`: Daftar dependensi library.

## 🚀 Cara Menjalankan

### 1. Instalasi
```bash
pip install -r requirements.txt
```

### 2. Jalankan Server
```bash
uvicorn main:app --reload
```

## 📊 Format Data (Request)
Endpoint `/predict` menerima data JSON dengan struktur:
- `lag_1, lag_2, lag_3`: Pengeluaran 1-3 hari sebelumnya.
- `rolling_mean_7`: Rata-rata seminggu terakhir.
- `transaction_count`: Jumlah transaksi harian.
- `day_of_week`, `month`, `is_weekend`, `mtd_progress`: Fitur temporal.

## 📈 Interpretasi Hasil
Response akan memberikan `forecast_idr`. Jika hasil akumulasi prediksi + pengeluaran riil melebihi target budget, sistem akan menandainya sebagai 'OVER-BUDGET'.
