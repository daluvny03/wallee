# 🔗 CONTOH REQUEST - Expense Forecasting API

## 📌 Daftar Isi
1. [Health Check](#1-health-check)
2. [Training Model](#2-training-model)
3. [Predict Pengeluaran](#3-predict-pengeluaran)
4. [Budget Analysis](#4-budget-analysis)
5. [Monthly Summary](#5-monthly-summary)
6. [Error Scenarios](#6-error-scenarios)

---

## 1. Health Check

### cURL
```bash
curl -X GET "http://localhost:8000/health" \
  -H "Accept: application/json"
```

### PowerShell
```powershell
$uri = "http://localhost:8000/health"
$response = Invoke-RestMethod -Uri $uri -Method Get
$response | ConvertTo-Json
```

### Python (requests)
```python
import requests

response = requests.get('http://localhost:8000/health')
print(response.json())
```

### Python (urllib)
```python
import urllib.request
import json

url = 'http://localhost:8000/health'
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    print(data)
```

### JavaScript (fetch)
```javascript
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### JavaScript (axios)
```javascript
const axios = require('axios');

axios.get('http://localhost:8000/health')
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error));
```

---

## 2. Training Model

### cURL
```bash
curl -X POST "http://localhost:8000/train?dl_epochs=80&dl_batch_size=32&arima_max_p=3&arima_max_q=3" \
  -F "file=@E:\Latihan Idzar\Coding Camp\capstone project\feature_engineered_finance_dataset.csv"
```

### PowerShell
```powershell
$uri = "http://localhost:8000/train?dl_epochs=80&dl_batch_size=32&arima_max_p=3&arima_max_q=3"
$filePath = "E:\Latihan Idzar\Coding Camp\capstone project\feature_engineered_finance_dataset.csv"

$fileStream = [System.IO.File]::OpenRead($filePath)
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)

$boundary = [System.Guid]::NewGuid().ToString()
$body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="$(Split-Path $filePath -Leaf)"
Content-Type: text/csv

$([System.Text.Encoding]::UTF8.GetString($fileBytes))
--$boundary--
"@

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "multipart/form-data; boundary=$boundary"
$response | ConvertTo-Json
```

### Python (requests)
```python
import requests

url = 'http://localhost:8000/train'
params = {
    'dl_epochs': 80,
    'dl_batch_size': 32,
    'arima_max_p': 3,
    'arima_max_q': 3
}

files = {
    'file': open(r'E:\Latihan Idzar\Coding Camp\capstone project\feature_engineered_finance_dataset.csv', 'rb')
}

response = requests.post(url, files=files, params=params)
print(response.json())
```

### Python (dengan timeout)
```python
import requests

url = 'http://localhost:8000/train'
params = {
    'dl_epochs': 80,
    'dl_batch_size': 32,
    'arima_max_p': 3,
    'arima_max_q': 3
}

files = {
    'file': open(r'E:\Latihan Idzar\Coding Camp\capstone project\feature_engineered_finance_dataset.csv', 'rb')
}

try:
    response = requests.post(url, files=files, params=params, timeout=300)  # 5 menit timeout
    print(response.json())
except requests.exceptions.Timeout:
    print("Training timeout - proses masih berjalan")
```

### JavaScript (FormData)
```javascript
const fs = require('fs');
const FormData = require('form-data');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('E:\\Latihan Idzar\\Coding Camp\\capstone project\\feature_engineered_finance_dataset.csv'));

axios.post('http://localhost:8000/train?dl_epochs=80&dl_batch_size=32', form, {
  headers: form.getHeaders(),
  timeout: 300000  // 5 menit
})
.then(response => console.log(response.data))
.catch(error => console.error('Error:', error));
```

---

## 3. Predict Pengeluaran

### cURL
```bash
# Contoh 1: Minimal fields
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": 1500000,
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "transaction_count": 5
  }'

# Contoh 2: Dengan semua optional fields
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": 1500000,
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "rolling_mean_30": 1575000,
    "transaction_count": 5,
    "day_of_week": 3,
    "month": 6,
    "is_weekend": 0,
    "mtd_progress": 0.5
  }'
```

### PowerShell
```powershell
$uri = "http://localhost:8000/predict"
$body = @{
    lag_1 = 1500000
    lag_2 = 1600000
    lag_3 = 1550000
    rolling_mean_7 = 1550000
    transaction_count = 5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
```

### Python (requests)
```python
import requests
import json

url = 'http://localhost:8000/predict'
payload = {
    "lag_1": 1500000,
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "transaction_count": 5
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Ensemble Forecast: Rp {data['ensemble_forecast']:,.0f}")
print(f"ARIMA Forecast: Rp {data['arima_forecast']:,.0f}")
if data.get('dl_forecast'):
    print(f"DL Forecast: Rp {data['dl_forecast']['forecast_rupiah']:,.0f}")
```

### Python (dengan error handling)
```python
import requests
import json

def predict_expense(lag_1, lag_2, lag_3, rolling_mean_7, transaction_count):
    url = 'http://localhost:8000/predict'
    payload = {
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "rolling_mean_7": rolling_mean_7,
        "transaction_count": transaction_count
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(e.response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    
    return None

# Penggunaan
result = predict_expense(1500000, 1600000, 1550000, 1550000, 5)
if result:
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### JavaScript (fetch)
```javascript
const payload = {
  lag_1: 1500000,
  lag_2: 1600000,
  lag_3: 1550000,
  rolling_mean_7: 1550000,
  transaction_count: 5
};

fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
.then(response => {
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
})
.then(data => {
  console.log('Ensemble Forecast:', `Rp ${data.ensemble_forecast.toLocaleString('id-ID')}`);
  console.log('ARIMA Forecast:', `Rp ${data.arima_forecast.toLocaleString('id-ID')}`);
  if (data.dl_forecast) {
    console.log('DL Forecast:', `Rp ${data.dl_forecast.forecast_rupiah.toLocaleString('id-ID')}`);
  }
})
.catch(error => console.error('Error:', error));
```

### JavaScript (axios)
```javascript
const axios = require('axios');

const payload = {
  lag_1: 1500000,
  lag_2: 1600000,
  lag_3: 1550000,
  rolling_mean_7: 1550000,
  transaction_count: 5
};

axios.post('http://localhost:8000/predict', payload)
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error.response?.data || error.message));
```

---

## 4. Budget Analysis

### cURL
```bash
# Status AMAN
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_target": 20000000
  }'

# Kemungkinan OVER-BUDGET
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_target": 15000000
  }'
```

### PowerShell
```powershell
$uri = "http://localhost:8000/budget-analysis"
$body = @{
    budget_target = 20000000
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"

if ($response.status -eq "AMAN") {
    Write-Host "✅ Status AMAN" -ForegroundColor Green
} else {
    Write-Host "⚠️  Status OVER-BUDGET" -ForegroundColor Red
}

$response | ConvertTo-Json
```

### Python (requests)
```python
import requests

url = 'http://localhost:8000/budget-analysis'
payload = {"budget_target": 20000000}

response = requests.post(url, json=payload)
data = response.json()

print(f"Budget Target: Rp {data['budget_target']:,.0f}")
print(f"Forecast: Rp {data['ensemble_forecast']:,.0f}")
print(f"Variance: Rp {data['variance']:,.0f}")
print(f"Utilization: {data['utilization_pct']:.2f}%")
print(f"Status: {data['status']}")
print(f"Message: {data['message']}")
```

### Python (class wrapper)
```python
import requests

class BudgetAnalyzer:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
    
    def analyze(self, budget_target):
        url = f'{self.base_url}/budget-analysis'
        payload = {'budget_target': budget_target}
        
        response = requests.post(url, json=payload)
        return response.json()

# Penggunaan
analyzer = BudgetAnalyzer()
result = analyzer.analyze(20000000)
print(f"Status: {result['status']}")
print(f"Remaining Budget: Rp {result['variance']:,.0f}")
```

### JavaScript (fetch)
```javascript
const budgetTarget = 20000000;

fetch('http://localhost:8000/budget-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ budget_target: budgetTarget })
})
.then(response => response.json())
.then(data => {
  console.log(`Budget: Rp ${data.budget_target.toLocaleString('id-ID')}`);
  console.log(`Forecast: Rp ${data.ensemble_forecast.toLocaleString('id-ID')}`);
  console.log(`Status: ${data.status}`);
  
  if (data.status === 'AMAN') {
    console.log('✅ Budget Aman!');
  } else {
    console.log('⚠️ Over-budget terdeteksi!');
  }
})
.catch(error => console.error('Error:', error));
```

---

## 5. Monthly Summary

### cURL
```bash
# Default: 6 bulan
curl -X GET "http://localhost:8000/monthly-summary" \
  -H "Accept: application/json"

# Custom: 12 bulan
curl -X GET "http://localhost:8000/monthly-summary?n_months=12" \
  -H "Accept: application/json"

# Custom: 3 bulan
curl -X GET "http://localhost:8000/monthly-summary?n_months=3" \
  -H "Accept: application/json"
```

### PowerShell
```powershell
$uri = "http://localhost:8000/monthly-summary?n_months=6"
$response = Invoke-RestMethod -Uri $uri -Method Get

Write-Host "Ringkasan 6 Bulan Terakhir:" -ForegroundColor Cyan
$response.historical | ForEach-Object {
    Write-Host "$($_.month): Rp $($_.total_expense -as [int64] | ForEach-Object { $_.ToString('N0') })"
}
Write-Host "`nPrediksi Bulan Depan ($($response.next_month)): Rp $($response.forecast_rupiah -as [int64] | ForEach-Object { $_.ToString('N0') })"
```

### Python (requests)
```python
import requests
import pandas as pd

url = 'http://localhost:8000/monthly-summary'
params = {'n_months': 6}

response = requests.get(url, params=params)
data = response.json()

# Convert ke DataFrame untuk analisis lebih mudah
df = pd.DataFrame(data['historical'])
print(df.to_string(index=False))
print(f"\nNext Month ({data['next_month']}): Rp {data['forecast_rupiah']:,.0f}")
```

### Python (visualization)
```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

url = 'http://localhost:8000/monthly-summary'
params = {'n_months': 12}

response = requests.get(url, params=params)
data = response.json()

# Prepare data
months = [record['month'] for record in data['historical']] + [data['next_month']]
values = [record['total_expense'] for record in data['historical']] + [data['forecast_rupiah']]

# Plot
plt.figure(figsize=(12, 6))
plt.plot(months[:-1], values[:-1], marker='o', label='Actual', color='blue')
plt.plot(months[-2:], values[-2:], marker='D', linestyle='--', label='Forecast', color='red')
plt.title('Pengeluaran Bulanan & Prediksi')
plt.xlabel('Month')
plt.ylabel('Rupiah (IDR)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### JavaScript (fetch & table)
```javascript
fetch('http://localhost:8000/monthly-summary?n_months=6')
  .then(response => response.json())
  .then(data => {
    console.table(data.historical);
    console.log(`Forecast untuk ${data.next_month}: Rp ${data.forecast_rupiah.toLocaleString('id-ID')}`);
    
    // Create HTML table
    let html = '<table border="1" cellpadding="10">';
    html += '<tr><th>Bulan</th><th>Total Pengeluaran</th></tr>';
    data.historical.forEach(record => {
      html += `<tr><td>${record.month}</td><td>Rp ${record.total_expense.toLocaleString('id-ID')}</td></tr>`;
    });
    html += `<tr><td>${data.next_month}*</td><td>Rp ${data.forecast_rupiah.toLocaleString('id-ID')}</td></tr>`;
    html += '</table>';
    
    document.getElementById('summary').innerHTML = html;
  })
  .catch(error => console.error('Error:', error));
```

---

## 6. Error Scenarios

### Missing Required Fields
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": 1500000
  }'

# Response 422:
# {
#   "detail": [
#     {
#       "loc": ["body", "lag_2"],
#       "msg": "field required",
#       "type": "value_error.missing"
#     }
#   ]
# }
```

### Invalid Field Types
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": "invalid_string",
    "lag_2": 1600000,
    "lag_3": 1550000,
    "rolling_mean_7": 1550000,
    "transaction_count": 5
  }'

# Response 422:
# {
#   "detail": [
#     {
#       "loc": ["body", "lag_1"],
#       "msg": "value is not a valid number",
#       "type": "type_error.number"
#     }
#   ]
# }
```

### Model Not Loaded
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

# Response 503:
# {
#   "detail": "Model belum tersedia. Jalankan POST /train terlebih dahulu."
# }
```

### Out of Range Values
```bash
curl -X POST "http://localhost:8000/budget-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_target": -5000000
  }'

# Response 422:
# {
#   "detail": [
#     {
#       "loc": ["body", "budget_target"],
#       "msg": "ensure this value is greater than 0",
#       "type": "value_error.number.not_gt",
#       "ctx": {"limit_value": 0}
#     }
#   ]
# }
```

### Invalid File Format
```bash
curl -X POST "http://localhost:8000/train" \
  -F "file=@invalid_file.txt"

# Response 400:
# {
#   "detail": "Gagal baca CSV: [error details]"
# }
```

---

## 📊 Test Flow Recommendation

```
1. GET /health
   ↓
2. POST /train (upload CSV)
   ↓
3. POST /predict (get daily forecast)
   ↓
4. POST /budget-analysis (check budget)
   ↓
5. GET /monthly-summary (view trends)
```

---

## 🎯 Tips & Best Practices

1. **Always check health first**: Pastikan server running sebelum request
2. **Train once**: Hanya perlu training sekali, model tersimpan di disk
3. **Predict daily**: Bisa predict berkali-kali dengan data berbeda
4. **Error handling**: Selalu handle error responses (4xx, 5xx)
5. **Timeout**: Set timeout untuk training (300 detik minimum)
6. **CORS**: API sudah support CORS untuk cross-origin requests
7. **Async**: Training bisa butuh waktu lama, pertimbangkan async client

