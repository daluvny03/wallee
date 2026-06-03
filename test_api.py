"""
Test Suite untuk Expense Forecasting API
Jalankan: python test_api.py
"""

import requests
import json
from pathlib import Path

# ============================================================================
# KONFIGURASI
# ============================================================================

BASE_URL = "http://localhost:8000"
DATASET_PATH = r"E:\Latihan Idzar\Coding Camp\capstone project\feature_engineered_finance_dataset.csv"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_response(response, title="Response"):
    """Pretty print response JSON"""
    print(f"\n{'='*70}")
    print(f"📋 {title}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


def test_health():
    """Test 1: Health Check"""
    print("\n" + "🟢"*35)
    print("TEST 1: HEALTH CHECK")
    print("🟢"*35)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "GET /health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"✅ Model Loaded: {data['model_loaded']}")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_train():
    """Test 2: Train Model"""
    print("\n" + "🟢"*35)
    print("TEST 2: TRAIN MODEL (First Time Only)")
    print("🟢"*35)
    
    if not Path(DATASET_PATH).exists():
        print(f"❌ Dataset not found: {DATASET_PATH}")
        return False
    
    try:
        files = {'file': open(DATASET_PATH, 'rb')}
        params = {
            'dl_epochs': 80,
            'dl_batch_size': 32,
            'arima_max_p': 3,
            'arima_max_q': 3
        }
        
        print(f"📤 Uploading file: {DATASET_PATH}")
        print(f"📊 Training parameters: {params}")
        
        response = requests.post(
            f"{BASE_URL}/train",
            files=files,
            params=params
        )
        print_response(response, "POST /train")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Training completed successfully!")
                print(f"   - ARIMA Order: {data.get('arima_order')}")
                print(f"   - SMAPE ARIMA: {data.get('smape_arima')}%")
                print(f"   - SMAPE DL (daily): {data.get('smape_dl_daily')}%")
                print(f"   - Ensemble Forecast: Rp {data.get('ensemble_forecast'):,.0f}")
                print(f"   - Months in data: {data.get('months_in_data')}")
                return True
        else:
            print("❌ Training failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_predict():
    """Test 3: Predict Pengeluaran"""
    print("\n" + "🟢"*35)
    print("TEST 3: PREDICT DAILY EXPENSE")
    print("🟢"*35)
    
    payload = {
        "lag_1": 1500000,           # Pengeluaran hari kemarin
        "lag_2": 1600000,           # Pengeluaran 2 hari lalu
        "lag_3": 1550000,           # Pengeluaran 3 hari lalu
        "rolling_mean_7": 1550000,  # Rata-rata 7 hari
        "transaction_count": 5      # Jumlah transaksi hari ini
        # Opsional: day_of_week, month, is_weekend, mtd_progress akan auto-generated
    }
    
    try:
        print(f"📨 Request Payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload
        )
        print_response(response, "POST /predict")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Prediction successful!")
                print(f"   - Ensemble Forecast: Rp {data.get('ensemble_forecast'):,.0f}")
                print(f"   - Days Forecasted: {data.get('days_forecasted')} hari")
                print(f"   - ARIMA Forecast: Rp {data.get('arima_forecast'):,.0f}")
                
                if data.get('dl_forecast'):
                    dl = data['dl_forecast']
                    print(f"   - DL Forecast: Rp {dl.get('forecast_rupiah'):,.0f}")
                    print(f"   - Confidence Range: Rp {dl.get('confidence_lower'):,.0f} - Rp {dl.get('confidence_upper'):,.0f}")
                    print(f"   - Trend: {dl.get('trend_direction')} {abs(dl.get('trend_pct')):.1f}%")
                
                return True
        else:
            print("❌ Prediction failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_predict_with_optional_params():
    """Test 3B: Predict dengan parameter opsional"""
    print("\n" + "🟡"*35)
    print("TEST 3B: PREDICT DENGAN PARAMETER OPSIONAL")
    print("🟡"*35)
    
    payload = {
        "lag_1": 1500000,
        "lag_2": 1600000,
        "lag_3": 1550000,
        "rolling_mean_7": 1550000,
        "transaction_count": 5,
        "day_of_week": 2,          # Rabu
        "month": 6,                # Juni
        "is_weekend": 0,           # Bukan weekend
        "mtd_progress": 0.5        # 50% hari di bulan ini sudah berlalu
    }
    
    try:
        print(f"📨 Request Payload (dengan optional params):")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload
        )
        print_response(response, "POST /predict (dengan optional params)")
        
        if response.status_code == 200:
            print("✅ Prediction with optional parameters successful!")
            return True
        else:
            print("❌ Prediction failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_budget_analysis():
    """Test 4: Budget Analysis"""
    print("\n" + "🟢"*35)
    print("TEST 4: BUDGET ANALYSIS")
    print("🟢"*35)
    
    payload = {
        "budget_target": 20000000  # Target anggaran: Rp 20 juta
    }
    
    try:
        print(f"💰 Budget Target: Rp {payload['budget_target']:,.0f}")
        
        response = requests.post(
            f"{BASE_URL}/budget-analysis",
            json=payload
        )
        print_response(response, "POST /budget-analysis")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Budget analysis successful!")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Ensemble Forecast: Rp {data.get('ensemble_forecast'):,.0f}")
            print(f"   - Variance: Rp {data.get('variance'):,.0f}")
            print(f"   - Utilization: {data.get('utilization_pct'):.2f}%")
            print(f"   - Message: {data.get('message')}")
            return True
        else:
            print("❌ Budget analysis failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_budget_analysis_over():
    """Test 4B: Budget Analysis - Over Budget Scenario"""
    print("\n" + "🟡"*35)
    print("TEST 4B: BUDGET ANALYSIS - OVER BUDGET SCENARIO")
    print("🟡"*35)
    
    payload = {
        "budget_target": 15000000  # Target lebih kecil = kemungkinan over-budget
    }
    
    try:
        print(f"💰 Budget Target: Rp {payload['budget_target']:,.0f}")
        
        response = requests.post(
            f"{BASE_URL}/budget-analysis",
            json=payload
        )
        print_response(response, "POST /budget-analysis (Over Budget Scenario)")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Budget analysis successful!")
            print(f"   - Status: {data.get('status')}")
            if data.get('status') == "OVER-BUDGET":
                print("   ⚠️  PERHATIAN: Over-budget terdeteksi!")
            return True
        else:
            print("❌ Budget analysis failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_monthly_summary():
    """Test 5: Monthly Summary"""
    print("\n" + "🟢"*35)
    print("TEST 5: MONTHLY SUMMARY")
    print("🟢"*35)
    
    try:
        params = {'n_months': 6}
        print(f"📅 Fetching {params['n_months']} months of historical data...")
        
        response = requests.get(
            f"{BASE_URL}/monthly-summary",
            params=params
        )
        print_response(response, "GET /monthly-summary")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Monthly summary retrieved successfully!")
            print(f"   - Historical Months: {len(data.get('historical', []))}")
            print(f"   - Next Month: {data.get('next_month')}")
            print(f"   - Forecast: Rp {data.get('forecast_rupiah'):,.0f}")
            
            print("\n   📊 Historical Data:")
            for record in data.get('historical', []):
                print(f"      {record['month']}: Rp {record['total_expense']:,.0f}")
            
            return True
        else:
            print("❌ Monthly summary retrieval failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_monthly_summary_custom():
    """Test 5B: Monthly Summary dengan parameter custom"""
    print("\n" + "🟡"*35)
    print("TEST 5B: MONTHLY SUMMARY - CUSTOM MONTHS")
    print("🟡"*35)
    
    try:
        params = {'n_months': 12}  # 12 bulan terakhir
        print(f"📅 Fetching {params['n_months']} months of historical data...")
        
        response = requests.get(
            f"{BASE_URL}/monthly-summary",
            params=params
        )
        print_response(response, "GET /monthly-summary (12 months)")
        
        if response.status_code == 200:
            print("✅ Monthly summary (12 months) retrieved successfully!")
            return True
        else:
            print("❌ Monthly summary retrieval failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_error_handling():
    """Test 6: Error Handling"""
    print("\n" + "🔴"*35)
    print("TEST 6: ERROR HANDLING")
    print("🔴"*35)
    
    # 6A: Missing required field
    print("\n📌 Test 6A: Missing Required Field in /predict")
    payload_invalid = {
        "lag_1": 1500000,
        # lag_2, lag_3, dll missing
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload_invalid
        )
        print_response(response, "POST /predict (Missing Fields)")
        if response.status_code == 422:
            print("✅ Correctly returned 422 Unprocessable Entity!")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6B: Invalid budget_target (negative)
    print("\n📌 Test 6B: Invalid Budget Target")
    payload_invalid_budget = {
        "budget_target": -5000000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/budget-analysis",
            json=payload_invalid_budget
        )
        print_response(response, "POST /budget-analysis (Negative Budget)")
        if response.status_code == 422:
            print("✅ Correctly returned 422 Unprocessable Entity!")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# MAIN TEST SUITE
# ============================================================================

def run_all_tests():
    """Jalankan semua test"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "EXPENSE FORECASTING API TEST SUITE" + " "*19 + "║")
    print("║" + " "*16 + f"Base URL: {BASE_URL}" + " "*32 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test urutan
    results = {
        "1. Health Check": test_health(),
        "2. Train Model": test_train(),
        "3. Predict": test_predict(),
        "3B. Predict (Optional Params)": test_predict_with_optional_params(),
        "4. Budget Analysis": test_budget_analysis(),
        "4B. Budget Analysis (Over Budget)": test_budget_analysis_over(),
        "5. Monthly Summary": test_monthly_summary(),
        "5B. Monthly Summary (12 months)": test_monthly_summary_custom(),
        "6. Error Handling": test_error_handling(),
    }
    
    # Ringkasan
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return passed == total


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n⚠️  PERHATIAN: Pastikan server sudah running di http://localhost:8000")
    print("💡 Jalankan di terminal terpisah:")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nMulai testing dalam 5 detik...\n")
    
    import time
    time.sleep(5)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
