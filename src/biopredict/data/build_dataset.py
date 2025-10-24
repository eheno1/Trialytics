"""Feature engineering and dataset building."""
import pandas as pd
from typing import List, Dict
from pathlib import Path

from ..config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    FEATURES,
    TARGET,
    PHASE_SUCCESS_RATES
)
from ..utils import load_json, extract_phase_number


def build_training_dataset(trials: List[Dict], outcomes: List[Dict]) -> pd.DataFrame:
    """Build training dataset with features and labels.
    
    Args:
        trials: List of trial data dictionaries
        outcomes: List of outcome records with labels
        
    Returns:
        DataFrame with features and target
    """
    print("Building training dataset...")
    
    # Convert to DataFrames
    df_trials = pd.DataFrame(trials)
    df_outcomes = pd.DataFrame(outcomes)
    
    # Merge on nct_id
    df = df_trials.merge(df_outcomes[["nct_id", "outcome_label"]], on="nct_id", how="inner")
    
    print(f"Merged {len(df)} trials with outcomes")
    
    # Engineer features
    df = _engineer_features(df)
    
    # Select feature columns and target
    required_cols = FEATURES + [TARGET, "nct_id", "brief_title", "sponsor_name", 
                                "primary_completion_date", "condition"]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        print(f"Warning: Missing columns: {missing_cols}")
    
    available_cols = [col for col in required_cols if col in df.columns]
    df = df[available_cols]
    
    # Drop rows with missing features
    initial_count = len(df)
    df = df.dropna(subset=FEATURES + [TARGET])
    final_count = len(df)
    
    if initial_count > final_count:
        print(f"Dropped {initial_count - final_count} rows with missing features")
    
    print(f"Training dataset: {len(df)} samples")
    print(f"  Positive class: {df[TARGET].sum()} ({df[TARGET].mean():.2%})")
    
    # Save processed training data
    output_path = PROCESSED_DATA_DIR / "train.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Saved training data to {output_path}")
    
    return df


def build_inference_dataset(trials: List[Dict]) -> pd.DataFrame:
    """Build inference dataset with features (no labels).
    
    Args:
        trials: List of trial data dictionaries
        
    Returns:
        DataFrame with features
    """
    print("Building inference dataset...")
    
    # Convert to DataFrame
    df = pd.DataFrame(trials)
    
    # Engineer features
    df = _engineer_features(df)
    
    # Keep all metadata columns for display
    print(f"Inference dataset: {len(df)} samples")
    
    # Fill missing feature values with medians/defaults
    for feature in FEATURES:
        if feature in df.columns:
            if df[feature].dtype in ['float64', 'int64']:
                median_val = df[feature].median()
                df[feature].fillna(median_val, inplace=True)
            else:
                df[feature].fillna(0, inplace=True)
    
    # Save processed inference data
    output_path = PROCESSED_DATA_DIR / "inference_universe.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Saved inference data to {output_path}")
    
    return df


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features from trial metadata.
    
    Args:
        df: DataFrame with trial data
        
    Returns:
        DataFrame with engineered features
    """
    # Phase number
    df["phase_num"] = df["phase"].apply(extract_phase_number)
    
    # Is Phase 3
    df["is_phase3"] = (df["phase_num"] == 3).astype(int)
    
    # Enrollment (handle missing)
    df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce")
    
    # Sites/locations count
    df["sites"] = pd.to_numeric(df["locations_count"], errors="coerce")
    
    # Indication prior - use industry benchmark by phase
    df["indication_prior"] = df["phase_num"].map(PHASE_SUCCESS_RATES)
    
    return df


def load_training_data() -> pd.DataFrame:
    """Load processed training data.
    
    Returns:
        Training DataFrame
    """
    train_path = PROCESSED_DATA_DIR / "train.parquet"
    df = pd.read_parquet(train_path)
    print(f"Loaded training data: {len(df)} samples")
    return df


def load_inference_data() -> pd.DataFrame:
    """Load processed inference data.
    
    Returns:
        Inference DataFrame
    """
    inference_path = PROCESSED_DATA_DIR / "inference_universe.parquet"
    df = pd.read_parquet(inference_path)
    print(f"Loaded inference data: {len(df)} samples")
    return df

