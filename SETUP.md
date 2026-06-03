# ✅ Setup & Implementation Checklist

## 🚀 Phase 1: Initial Setup (30 minutes)

- [ ] **Read Documentation**
  - [ ] Read README.md (overview)
  - [ ] Read QUICK_REFERENCE.md (cheat sheet)
  
- [ ] **Install Dependencies**
  ```bash
  pip install -r requirements.txt
  ```
  - [ ] Verify installation: `python -c "import tensorflow, pandas, fastapi; print('✅ All libraries installed')"`

- [ ] **Start Server**
  ```bash
  # Option 1: From notebook
  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  
  # Option 2: Direct
  python main.py
  ```
  - [ ] Check server running: `curl http://localhost:8000/health`
  - [ ] Open browser: http://localhost:8000/docs

- [ ] **Test Health Endpoint**
  - [ ] GET /health returns 200 status
  - [ ] model_loaded should be false (until training)


## 🔧 Phase 2: Model Training (15-20 minutes)

- [ ] **Prepare Dataset**
  - [ ] CSV file ready
  - [ ] Columns: `date` (or `tanggal`) and `expense` (or `total_harga`)
  - [ ] Data range: minimum 6 months
  - [ ] Sample: ✅ feature_engineered_finance_dataset.csv

- [ ] **Upload & Train**
  ```bash
  curl -X POST "http://localhost:8000/train" \
    -F "file=@feature_engineered_finance_dataset.csv"
  ```
  - [ ] Wait for completion (5-15 minutes)
  - [ ] Response contains arima_order, smape values
  - [ ] Check models created: `ls models/`
    - [ ] forecast_model.keras
    - [ ] scaler_X.save
    - [ ] scaler_y.save
    - [ ] arima_model.save
    - [ ] metadata.save

- [ ] **Verify Training Success**
  - [ ] GET /health returns model_loaded: true
  - [ ] Response shows SMAPE metrics (accuracy)


## 🎯 Phase 3: Testing (20 minutes)

- [ ] **Run Automated Tests**
  ```bash
  python test_api.py
  ```
  - [ ] All tests pass
  - [ ] Check specific endpoint: Health, Train, Predict, Budget, Summary

- [ ] **Manual Testing**
  - [ ] Test POST /predict (daily forecast)
  - [ ] Test POST /budget-analysis (budget check)
  - [ ] Test GET /monthly-summary (trends)

- [ ] **Test Error Handling**
  - [ ] Missing required field → 422
  - [ ] Model not loaded → 503
  - [ ] Invalid data type → 422


## 📊 Phase 4: Integration (depends on use case)

- [ ] **Integrate to Frontend** (if applicable)
  - [ ] Update API endpoint URLs
  - [ ] Handle CORS headers
  - [ ] Implement error messages

- [ ] **Integrate to Backend** (if applicable)
  - [ ] Add authentication
  - [ ] Add rate limiting
  - [ ] Add request logging

- [ ] **Setup Monitoring**
  - [ ] Log API responses
  - [ ] Monitor error rates
  - [ ] Track response times


## 🚀 Phase 5: Deployment (if needed)

- [ ] **Prepare Production**
  - [ ] Review security settings
  - [ ] Add authentication (JWT/API Key)
  - [ ] Enable HTTPS/SSL
  - [ ] Setup load balancer

- [ ] **Deploy**
  - [ ] Choose hosting (AWS, GCP, Azure, VPS)
  - [ ] Configure environment variables
  - [ ] Setup model backup/persistence
  - [ ] Configure monitoring & alerts

- [ ] **Post-Deployment**
  - [ ] Test all endpoints
  - [ ] Monitor performance
  - [ ] Setup auto-scaling (if needed)


## 📚 Reference Checklist

### File Organization
```
capstone project/
├── ✅ README.md                   ← Overview & quick start
├── ✅ QUICK_REFERENCE.md          ← Cheat sheet (5 min read)
├── ✅ API_DOCUMENTATION.md        ← Full docs (30 min read)
├── ✅ CONTOH_REQUEST.md           ← Code examples
├── ✅ test_api.py                 ← Automated tests
├── ✅ main.py                     ← Standalone app
├── ✅ requirements.txt            ← Dependencies
├── ✅ this file                   ← Setup checklist
│
├── expense_forecasting_notebook (3).ipynb
├── feature_engineered_finance_dataset.csv
│
└── models/                        ← Auto-created after training
```

### Commands Reference
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Test health
curl http://localhost:8000/health

# Train model
curl -X POST "http://localhost:8000/train" \
  -F "file=@feature_engineered_finance_dataset.csv"

# Make prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"lag_1":1500000,"lag_2":1600000,"lag_3":1550000,"rolling_mean_7":1550000,"transaction_count":5}'

# Run tests
python test_api.py

# View docs
# Browser: http://localhost:8000/docs
```

### API Endpoints Reference
```
GET  /health                 ← Check server & model status
POST /train                  ← Train models (first time)
POST /predict                ← Get daily forecast
POST /budget-analysis        ← Check budget vs forecast
GET  /monthly-summary        ← View historical trends

Docs: http://localhost:8000/docs
```

### Request Format Reference
```json
// POST /predict
{
  "lag_1": 1500000,
  "lag_2": 1600000,
  "lag_3": 1550000,
  "rolling_mean_7": 1550000,
  "transaction_count": 5
}

// POST /budget-analysis
{
  "budget_target": 20000000
}

// GET /monthly-summary?n_months=6
```

### Common Issues & Solutions
```
Issue: "Model belum tersedia"
→ Solution: Run POST /train first

Issue: "Kolom date/expense tidak ditemukan"
→ Solution: Ensure CSV has correct columns (date, expense)

Issue: "Connection refused"
→ Solution: Start server with python main.py

Issue: Timeout on training
→ Solution: Increase timeout, reduce epochs, or use better hardware
```


## 🎯 Success Criteria

Phase 1 Success ✅
- [ ] Server running without errors
- [ ] /health endpoint responds
- [ ] Swagger UI accessible

Phase 2 Success ✅
- [ ] Training completes without errors
- [ ] Model files created in models/ directory
- [ ] model_loaded returns true

Phase 3 Success ✅
- [ ] All automated tests pass
- [ ] Manual tests successful
- [ ] Error handling works correctly

Phase 4 Success ✅
- [ ] Integration complete
- [ ] Application working as expected
- [ ] No API errors

Phase 5 Success ✅
- [ ] Production deployment successful
- [ ] Monitoring & alerts configured
- [ ] Team trained on usage


## 📞 Support Resources

**Quick Help**: QUICK_REFERENCE.md
**Full Docs**: API_DOCUMENTATION.md
**Code Examples**: CONTOH_REQUEST.md
**Run Tests**: `python test_api.py`
**Interactive API**: http://localhost:8000/docs


## 🔄 Regular Maintenance

- [ ] **Weekly**
  - Check API response times
  - Monitor error rates
  - Check disk space (models)

- [ ] **Monthly**
  - Review accuracy metrics
  - Update data if available
  - Retrain model with new data

- [ ] **Quarterly**
  - Review security settings
  - Update dependencies (pip list --outdated)
  - Performance optimization review


## ⏱️ Estimated Timeline

| Task | Time | Difficulty |
|------|------|-----------|
| Phase 1 (Setup) | 30 min | Easy |
| Phase 2 (Training) | 15-20 min | Easy |
| Phase 3 (Testing) | 20 min | Medium |
| Phase 4 (Integration) | Varies | Medium-Hard |
| Phase 5 (Deployment) | Varies | Hard |

**Total for basic setup**: ~1 hour

---

**Start here**: ✅ Follow Phase 1 first
**Questions?**: 📚 See README.md or QUICK_REFERENCE.md
**Need examples?**: 📖 See CONTOH_REQUEST.md

Good luck! 🚀
