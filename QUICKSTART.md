# Quick Start Guide

## TL;DR - Try it Now!

The MVP is **already built and running** with data fetched and model trained.

### Launch the Dashboard (30 seconds)

```bash
cd /Users/Eric_1/Trialytics
streamlit run src/biopredict/app/dashboard.py
```

Then open your browser to: **http://localhost:8501**

---

## What You'll See

### Dashboard Features
- **1,000 Phase 2/3 clinical trials** with success predictions
- **156 High-probability trials** (≥70% success chance)
- **Interactive filters**: Phase, Bucket, Enrollment, Indication
- **Detail view**: Click any trial to see full metadata and feature values
- **Color-coded rows**: Green (High), Yellow (Medium), Red (Low)

### Example Trial
**NCT04668352** - Restorbio Inc.  
"A Phase 3 Study to Determine if RTB101 Prevents Clinically Symptomatic Respiratory Illness in the Elderly"  
**Probability:** 76.9% (High Bucket)

---

## Full Pipeline (If You Want to Re-run)

### 1. Install Dependencies
```bash
pip install requests pandas scikit-learn streamlit python-dotenv pyarrow joblib
```

### 2. Fetch Data (~2-3 minutes)
```bash
python scripts/fetch_data.py
```
Fetches 500 training trials + 1,000 inference trials from ClinicalTrials.gov

### 3. Train Model (~30 seconds)
```bash
python scripts/train_model.py
```
Trains calibrated logistic regression and generates predictions

### 4. Validate
```bash
python scripts/validate_pipeline.py
```
Verifies all components are working

### 5. Launch Dashboard
```bash
streamlit run src/biopredict/app/dashboard.py
```

---

## Key Files

- **Model:** `model/model.pkl`
- **Predictions:** `data/processed/predictions.parquet`
- **Training Data:** `data/processed/train.parquet`
- **Raw Trials:** `data/raw/ctgov_trials_*.json`

---

## Model Performance

- **ROC-AUC:** 0.89
- **PR-AUC:** 0.73
- **Accuracy:** 89%
- **Features:** Phase, Enrollment, Sites, Industry Benchmark

---

## Disclaimer

⚠️ **Not investment advice.** For informational purposes only.

---

## Need Help?

See `README.md` for full documentation  
See `MVP_COMPLETION_SUMMARY.md` for technical details

