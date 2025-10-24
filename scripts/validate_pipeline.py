"""Validation script to verify pipeline output."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from biopredict.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_PATH
import pandas as pd
import joblib


def main():
    """Validate pipeline outputs."""
    print("="*60)
    print("PIPELINE VALIDATION")
    print("="*60)
    
    errors = []
    
    # Check raw data files
    print("\n[1/4] Checking raw data files...")
    raw_files = [
        "ctgov_trials_training.json",
        "ctgov_trials_inference.json",
        "trial_outcomes.json"
    ]
    for file in raw_files:
        path = RAW_DATA_DIR / file
        if path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file}")
            errors.append(f"Missing raw data: {file}")
    
    # Check processed data files
    print("\n[2/4] Checking processed data files...")
    processed_files = [
        "train.parquet",
        "inference_universe.parquet",
        "predictions.parquet"
    ]
    for file in processed_files:
        path = PROCESSED_DATA_DIR / file
        if path.exists():
            df = pd.read_parquet(path)
            print(f"  [OK] {file} ({len(df)} rows)")
        else:
            print(f"  [MISSING] {file}")
            errors.append(f"Missing processed data: {file}")
    
    # Check model file
    print("\n[3/4] Checking model file...")
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        print(f"  [OK] model.pkl (type: {type(model).__name__})")
    else:
        print(f"  [MISSING] model.pkl")
        errors.append("Missing model file")
    
    # Check predictions quality
    print("\n[4/4] Checking predictions quality...")
    try:
        df_pred = pd.read_parquet(PROCESSED_DATA_DIR / "predictions.parquet")
        
        # Check for required columns
        required_cols = ["nct_id", "sponsor_name", "brief_title", "probability", "bucket"]
        missing_cols = [col for col in required_cols if col not in df_pred.columns]
        if missing_cols:
            print(f"  [MISSING] Columns: {missing_cols}")
            errors.append(f"Missing columns: {missing_cols}")
        else:
            print(f"  [OK] All required columns present")
        
        # Check bucket distribution
        bucket_counts = df_pred["bucket"].value_counts()
        print(f"\n  Bucket Distribution:")
        for bucket in ["High", "Medium", "Low"]:
            count = bucket_counts.get(bucket, 0)
            print(f"    {bucket:10s}: {count:4d} ({count/len(df_pred)*100:5.1f}%)")
        
        # Check for at least one trial with probability and bucket
        high_trials = df_pred[df_pred["bucket"] == "High"]
        if len(high_trials) > 0:
            sample = high_trials.iloc[0]
            print(f"\n  Sample High-Probability Trial:")
            print(f"    NCT ID: {sample['nct_id']}")
            print(f"    Title: {sample['brief_title'][:60]}...")
            print(f"    Probability: {sample['probability']:.1%}")
            print(f"    Bucket: {sample['bucket']}")
            print(f"  [OK] At least one trial with probability and bucket")
        else:
            print(f"  [FAIL] No high-probability trials found")
            errors.append("No high-probability trials")
            
    except Exception as e:
        print(f"  [ERROR] Error checking predictions: {e}")
        errors.append(f"Prediction check error: {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print("VALIDATION FAILED")
        print("="*60)
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("VALIDATION PASSED")
        print("="*60)
        print("\nAll requirements met:")
        print("  [OK] Data fetched from ClinicalTrials.gov")
        print("  [OK] Model trained and saved")
        print("  [OK] Predictions generated")
        print("  [OK] At least one trial with probability and bucket")
        print("\nReady to launch dashboard:")
        print("  streamlit run src/biopredict/app/dashboard.py")
        return 0


if __name__ == "__main__":
    sys.exit(main())

