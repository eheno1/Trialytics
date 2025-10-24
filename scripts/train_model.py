"""Train model and generate predictions."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from biopredict.config import RAW_DATA_DIR
from biopredict.utils import load_json
from biopredict.data.build_dataset import build_training_dataset, build_inference_dataset
from biopredict.model.train import train_model, run_inference


def main():
    """Main training pipeline."""
    print("="*60)
    print("MODEL TRAINING PIPELINE")
    print("="*60)
    
    # Step 1: Load raw data
    print("\n[1/5] Loading raw data...")
    try:
        training_trials = load_json(RAW_DATA_DIR / "ctgov_trials_training.json")
        outcomes = load_json(RAW_DATA_DIR / "trial_outcomes.json")
        inference_trials = load_json(RAW_DATA_DIR / "ctgov_trials_inference.json")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please run `python scripts/fetch_data.py` first.")
        return
    
    # Step 2: Build training dataset
    print("\n[2/5] Building training dataset...")
    df_train = build_training_dataset(training_trials, outcomes)
    
    if len(df_train) == 0:
        print("ERROR: No training data available. Exiting.")
        return
    
    # Step 3: Build inference dataset
    print("\n[3/5] Building inference dataset...")
    df_inference = build_inference_dataset(inference_trials)
    
    if len(df_inference) == 0:
        print("ERROR: No inference data available. Exiting.")
        return
    
    # Step 4: Train model
    print("\n[4/5] Training model...")
    model, df_val_pred = train_model(df_train)
    
    # Step 5: Run inference
    print("\n[5/5] Running inference...")
    df_predictions = run_inference(model)
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE")
    print("="*60)
    print(f"Model saved: model/model.pkl")
    print(f"Predictions: {len(df_predictions)} trials")
    print("\nNext step: Run `streamlit run src/biopredict/app/dashboard.py`")


if __name__ == "__main__":
    main()

