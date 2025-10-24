"""Utility functions for the biopredict package."""
import json
from pathlib import Path
from typing import Any, Dict, List


def save_json(data: Any, filepath: Path) -> None:
    """Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save JSON file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved JSON to {filepath}")


def load_json(filepath: Path) -> Any:
    """Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded JSON from {filepath}")
    return data


def assign_bucket(probability: float) -> str:
    """Assign bucket category based on probability.
    
    Args:
        probability: Success probability (0-1)
        
    Returns:
        Bucket category: "High", "Medium", or "Low"
    """
    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    else:
        return "Low"


def extract_phase_number(phase_str: str) -> int:
    """Extract numeric phase from phase string.
    
    Args:
        phase_str: Phase string like "PHASE2", "PHASE3", etc.
        
    Returns:
        Phase number (2 or 3), defaults to 2 if unknown
    """
    if isinstance(phase_str, list):
        # Take the highest phase if multiple
        phases = [p for p in phase_str if 'PHASE2' in p or 'PHASE3' in p]
        if phases:
            phase_str = phases[-1]
        else:
            phase_str = phase_str[0] if phase_str else ""
    
    if "PHASE3" in str(phase_str).upper():
        return 3
    elif "PHASE2" in str(phase_str).upper():
        return 2
    else:
        return 2  # Default to Phase 2

