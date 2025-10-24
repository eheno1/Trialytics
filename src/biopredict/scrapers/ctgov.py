"""ClinicalTrials.gov API scraper."""
import requests
import time
from typing import Dict, List, Optional
from pathlib import Path

from ..config import CTGOV_API_URL, RAW_DATA_DIR
from ..utils import save_json


def fetch_trials_for_training(max_trials: int = 500) -> List[Dict]:
    """Fetch completed Phase 2/3 trials with results for training.
    
    Args:
        max_trials: Maximum number of trials to fetch
        
    Returns:
        List of trial data dictionaries
    """
    print(f"Fetching training trials (completed with results)...")
    
    params = {
        "filter.advanced": "AREA[Phase](PHASE2 OR PHASE3) AND AREA[OverallStatus]COMPLETED",
        "pageSize": 100,
    }
    
    trials = []
    next_page_token = None
    
    while len(trials) < max_trials:
        if next_page_token:
            params["pageToken"] = next_page_token
        
        try:
            response = requests.get(CTGOV_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            studies = data.get("studies", [])
            if not studies:
                break
            
            for study in studies:
                trial_data = _extract_trial_data(study)
                if trial_data:
                    trials.append(trial_data)
                
                if len(trials) >= max_trials:
                    break
            
            print(f"Fetched {len(trials)} trials so far...")
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching trials: {e}")
            break
    
    print(f"Fetched {len(trials)} completed trials total")
    
    # Save to file
    output_path = RAW_DATA_DIR / "ctgov_trials_training.json"
    save_json(trials, output_path)
    
    return trials


def fetch_trials_for_inference(max_trials: int = 1000) -> List[Dict]:
    """Fetch recent Phase 2/3 trials for inference (any status).
    
    Args:
        max_trials: Maximum number of trials to fetch
        
    Returns:
        List of trial data dictionaries
    """
    print(f"Fetching inference trials (recent Phase 2/3)...")
    
    params = {
        "filter.advanced": "AREA[Phase](PHASE2 OR PHASE3)",
        "pageSize": 100,
    }
    
    trials = []
    next_page_token = None
    
    while len(trials) < max_trials:
        if next_page_token:
            params["pageToken"] = next_page_token
        
        try:
            response = requests.get(CTGOV_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            studies = data.get("studies", [])
            if not studies:
                break
            
            for study in studies:
                trial_data = _extract_trial_data(study)
                if trial_data:
                    trials.append(trial_data)
                
                if len(trials) >= max_trials:
                    break
            
            print(f"Fetched {len(trials)} trials so far...")
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching trials: {e}")
            break
    
    print(f"Fetched {len(trials)} inference trials total")
    
    # Save to file
    output_path = RAW_DATA_DIR / "ctgov_trials_inference.json"
    save_json(trials, output_path)
    
    return trials


def _extract_trial_data(study: Dict) -> Optional[Dict]:
    """Extract relevant fields from a study record.
    
    Args:
        study: Study data from API
        
    Returns:
        Extracted trial data or None if invalid
    """
    try:
        protocol = study.get("protocolSection", {})
        
        # Identification
        ident = protocol.get("identificationModule", {})
        nct_id = ident.get("nctId", "")
        if not nct_id:
            return None
        
        brief_title = ident.get("briefTitle", "")
        org = ident.get("organization", {})
        
        # Status
        status = protocol.get("statusModule", {})
        overall_status = status.get("overallStatus", "")
        primary_completion = status.get("primaryCompletionDateStruct", {})
        primary_completion_date = primary_completion.get("date", "")
        
        # Design
        design = protocol.get("designModule", {})
        phases = design.get("phases", [])
        enrollment_info = design.get("enrollmentInfo", {})
        enrollment_count = enrollment_info.get("count", 0)
        
        # Conditions
        conditions = protocol.get("conditionsModule", {})
        condition_list = conditions.get("conditions", [])
        condition = condition_list[0] if condition_list else ""
        
        # Sponsor
        sponsor_collab = protocol.get("sponsorCollaboratorsModule", {})
        lead_sponsor = sponsor_collab.get("leadSponsor", {})
        sponsor_name = lead_sponsor.get("name", "")
        
        # Locations
        contacts_locations = protocol.get("contactsLocationsModule", {})
        locations = contacts_locations.get("locations", [])
        locations_count = len(locations)
        
        # Results (if available)
        has_results = study.get("hasResults", False)
        results_section = study.get("resultsSection", {})
        
        trial_data = {
            "nct_id": nct_id,
            "brief_title": brief_title,
            "phase": phases,
            "condition": condition,
            "enrollment": enrollment_count,
            "locations_count": locations_count,
            "primary_completion_date": primary_completion_date,
            "sponsor_name": sponsor_name,
            "overall_status": overall_status,
            "has_results": has_results,
            "results_section": results_section if has_results else None,
        }
        
        return trial_data
        
    except Exception as e:
        print(f"Error extracting trial data: {e}")
        return None

