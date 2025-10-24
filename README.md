Trialytics - A Biotech Clinical Trials Prediction Application

A machine learning system to predict the probability that Phase 2 or Phase 3 biotech clinical trials will meet their primary endpoints.

## Overview

This MVP predicts trial success using:
- ClinicalTrials.gov API for trial metadata
- Calibrated Logistic Regression model
- Industry benchmark success rates
- Interactive Streamlit dashboard

Trials are categorized as:
- **High** (≥70% probability)
- **Medium** (40-70% probability)
- **Low** (<40% probability)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Verify installation:
```bash
python --version  # Requires Python 3.8+
```

## Usage

### Step 1: Fetch Data
```bash
python scripts/fetch_data.py
```
Fetches trial data from ClinicalTrials.gov and extracts outcomes.

### Step 2: Train Model
```bash
python scripts/train_model.py
```
Builds features, trains the model, and generates predictions.

### Step 3: Launch Dashboard
```bash
streamlit run src/biopredict/app/dashboard.py
```
Opens interactive dashboard at http://localhost:8501

## Project Structure

```
biotech-trial-predictor/
├── data/
│   ├── raw/                      # Raw API data
│   └── processed/                # Processed datasets
├── model/
│   └── model.pkl                 # Trained model
├── scripts/
│   ├── fetch_data.py            # Data collection orchestration
│   └── train_model.py           # Training orchestration
├── src/biopredict/
│   ├── config.py                # Configuration
│   ├── utils.py                 # Utilities
│   ├── scrapers/
│   │   ├── ctgov.py            # ClinicalTrials.gov scraper
│   │   └── sec_press.py        # Outcome extraction
│   ├── data/
│   │   └── build_dataset.py    # Feature engineering
│   ├── model/
│   │   └── train.py            # Model training
│   └── app/
│       └── dashboard.py        # Streamlit UI
├── requirements.txt
├── README.md
└── .env.example
```

## Features Used

- `phase_num`: Clinical trial phase (2 or 3)
- `is_phase3`: Boolean indicator for Phase 3
- `enrollment`: Number of participants
- `sites`: Number of trial locations
- `indication_prior`: Historical success rate by phase

## Scope & Limitations

**Included:**
- Phase 2 and Phase 3 trials only
- ClinicalTrials.gov data
- Basic outcome labeling from trial results
- Calibrated probability predictions

**Excluded:**
- Phase 1 or Phase 4 trials
- PDF/NLP parsing of SEC filings
- Financial modeling
- Real-time updates
- User authentication

## Disclaimer

**Not investment advice.** This tool is for informational and educational purposes only. Clinical trial outcomes are inherently uncertain and subject to many factors not captured in this model.

## License

MIT License - See LICENSE file for details

