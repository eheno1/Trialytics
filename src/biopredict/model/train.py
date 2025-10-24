"""Model training and inference."""
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    roc_auc_score,
)
from typing import Tuple

from ..config import (
    FEATURES,
    TARGET,
    TRAIN_TEST_SPLIT,
    RANDOM_STATE,
    MODEL_PATH,
    PROCESSED_DATA_DIR,
)
from ..utils import assign_bucket
from ..data.build_dataset import load_training_data, load_inference_data


def train_model(df_train: pd.DataFrame) -> Tuple[CalibratedClassifierCV, pd.DataFrame]:
    """Train and calibrate logistic regression model.
    
    Args:
        df_train: Training DataFrame with features and target
        
    Returns:
        Tuple of (trained model, validation predictions DataFrame)
    """
    print("\n" + "="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    # Sort by date for time-based split
    if "primary_completion_date" in df_train.columns:
        df_train = df_train.sort_values("primary_completion_date").reset_index(drop=True)
    
    # Split into train/validation
    split_idx = int(len(df_train) * TRAIN_TEST_SPLIT)
    df_train_split = df_train.iloc[:split_idx]
    df_val_split = df_train.iloc[split_idx:]
    
    print(f"\nDataset split:")
    print(f"  Training: {len(df_train_split)} samples")
    print(f"  Validation: {len(df_val_split)} samples")
    
    X_train = df_train_split[FEATURES]
    y_train = df_train_split[TARGET]
    X_val = df_val_split[FEATURES]
    y_val = df_val_split[TARGET]
    
    print(f"\nTraining set class distribution:")
    print(f"  Positive: {y_train.sum()} ({y_train.mean():.2%})")
    print(f"  Negative: {len(y_train) - y_train.sum()} ({1 - y_train.mean():.2%})")
    
    # Train logistic regression
    print(f"\nTraining Logistic Regression (class_weight='balanced')...")
    lr = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
        solver="lbfgs"
    )
    lr.fit(X_train, y_train)
    
    # Calibrate probabilities
    print("Calibrating probabilities (Isotonic)...")
    calibrated_model = CalibratedClassifierCV(
        lr,
        method="isotonic",
        cv="prefit"
    )
    calibrated_model.fit(X_val, y_val)
    
    # Evaluate on validation set
    print("\n" + "-"*60)
    print("VALIDATION METRICS")
    print("-"*60)
    
    y_pred_proba = calibrated_model.predict_proba(X_val)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Metrics
    pr_auc = average_precision_score(y_val, y_pred_proba)
    brier = brier_score_loss(y_val, y_pred_proba)
    
    try:
        roc_auc = roc_auc_score(y_val, y_pred_proba)
        print(f"ROC-AUC: {roc_auc:.4f}")
    except:
        print("ROC-AUC: N/A (need both classes in validation)")
    
    print(f"PR-AUC: {pr_auc:.4f}")
    print(f"Brier Score: {brier:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_val, y_pred, target_names=["Failure", "Success"]))
    
    # Feature importance
    print("\nFeature Coefficients:")
    for feature, coef in zip(FEATURES, lr.coef_[0]):
        print(f"  {feature:20s}: {coef:8.4f}")
    
    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated_model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    
    # Create validation predictions DataFrame
    df_val_pred = df_val_split.copy()
    df_val_pred["probability"] = y_pred_proba
    df_val_pred["prediction"] = y_pred
    df_val_pred["bucket"] = df_val_pred["probability"].apply(assign_bucket)
    
    return calibrated_model, df_val_pred


def run_inference(model: CalibratedClassifierCV = None) -> pd.DataFrame:
    """Run inference on the inference universe.
    
    Args:
        model: Trained model (if None, loads from file)
        
    Returns:
        DataFrame with predictions
    """
    print("\n" + "="*60)
    print("RUNNING INFERENCE")
    print("="*60)
    
    # Load model if not provided
    if model is None:
        print(f"Loading model from {MODEL_PATH}...")
        model = joblib.load(MODEL_PATH)
    
    # Load inference data
    df_inference = load_inference_data()
    
    # Check for required features
    missing_features = set(FEATURES) - set(df_inference.columns)
    if missing_features:
        raise ValueError(f"Missing features in inference data: {missing_features}")
    
    # Predict probabilities
    X_inference = df_inference[FEATURES]
    probabilities = model.predict_proba(X_inference)[:, 1]
    
    # Add predictions to DataFrame
    df_inference["probability"] = probabilities
    df_inference["bucket"] = df_inference["probability"].apply(assign_bucket)
    
    # Summary
    print(f"\nInference complete for {len(df_inference)} trials")
    print("\nBucket Distribution:")
    bucket_counts = df_inference["bucket"].value_counts()
    for bucket in ["High", "Medium", "Low"]:
        count = bucket_counts.get(bucket, 0)
        pct = count / len(df_inference) * 100
        print(f"  {bucket:10s}: {count:4d} ({pct:5.1f}%)")
    
    # Save predictions
    predictions_path = PROCESSED_DATA_DIR / "predictions.parquet"
    df_inference.to_parquet(predictions_path, index=False)
    print(f"\nPredictions saved to {predictions_path}")
    
    return df_inference


def load_predictions() -> pd.DataFrame:
    """Load saved predictions.
    
    Returns:
        DataFrame with predictions
    """
    predictions_path = PROCESSED_DATA_DIR / "predictions.parquet"
    df = pd.read_parquet(predictions_path)
    print(f"Loaded predictions: {len(df)} trials")
    return df

