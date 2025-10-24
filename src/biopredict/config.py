"""Configuration settings for the biopredict package."""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model directory
MODEL_DIR = PROJECT_ROOT / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"

# ClinicalTrials.gov API
CTGOV_API_URL = "https://clinicaltrials.gov/api/v2/studies"

# Model parameters
FEATURES = ["phase_num", "is_phase3", "enrollment", "sites", "indication_prior"]
TARGET = "outcome_label"

# Industry benchmark success rates by phase
PHASE_SUCCESS_RATES = {
    2: 0.30,  # 30% for Phase 2
    3: 0.50,  # 50% for Phase 3
}

# Bucket thresholds
BUCKET_THRESHOLDS = {
    "High": 0.70,
    "Medium": 0.40,
}

# Training parameters
TRAIN_TEST_SPLIT = 0.80  # 80% train, 20% validation
RANDOM_STATE = 42

