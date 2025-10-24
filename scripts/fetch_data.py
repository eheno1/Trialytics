"""Fetch data from ClinicalTrials.gov and extract outcomes."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from biopredict.scrapers.ctgov import fetch_trials_for_training, fetch_trials_for_inference
from biopredict.scrapers.sec_press import extract_outcomes_from_trials


def main():
    """Main data fetching pipeline."""
    print("="*60)
    print("DATA FETCHING PIPELINE")
    print("="*60)
    
    # Step 1: Fetch training trials (completed with potential outcomes)
    print("\n[1/3] Fetching training trials...")
    training_trials = fetch_trials_for_training(max_trials=500)
    
    if not training_trials:
        print("ERROR: No training trials fetched. Exiting.")
        return
    
    # Step 2: Extract outcomes from training trials
    print("\n[2/3] Extracting outcomes...")
    outcomes = extract_outcomes_from_trials(training_trials)
    
    if not outcomes:
        print("ERROR: No outcomes extracted. Exiting.")
        return
    
    # Step 3: Fetch inference trials (all recent Phase 2/3)
    print("\n[3/3] Fetching inference trials...")
    inference_trials = fetch_trials_for_inference(max_trials=1000)
    
    if not inference_trials:
        print("ERROR: No inference trials fetched. Exiting.")
        return
    
    print("\n" + "="*60)
    print("DATA FETCHING COMPLETE")
    print("="*60)
    print(f"Training trials: {len(training_trials)}")
    print(f"Outcomes labeled: {len(outcomes)}")
    print(f"Inference trials: {len(inference_trials)}")
    print("\nNext step: Run `python scripts/train_model.py`")


if __name__ == "__main__":
    main()

