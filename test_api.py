import requests
import json

url = "http://127.0.0.1:8000/predict"

# Data request dummy berdasarkan fitur yang dibutuhkan
payload = {
    "lag_1": 50000.0,
    "lag_2": 45000.0,
    "lag_3": 60000.0,
    "rolling_mean_7": 52000.0,
    "rolling_mean_30": 50000.0,
    "day_of_week": 2, # Wednesday
    "month": 5,
    "is_weekend": 0,
    "mtd_progress": 0.5,
    "transaction_count": 3
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error: Pastikan server uvicorn sudah jalan di port 8000.", e)
