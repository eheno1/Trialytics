"""Streamlit dashboard for biotech trial predictions."""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from biopredict.config import PROCESSED_DATA_DIR
from biopredict.model.train import load_predictions


def load_data() -> pd.DataFrame:
    """Load prediction data for dashboard."""
    try:
        df = load_predictions()
        return df
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        st.info("Please run `python scripts/train_model.py` first to generate predictions.")
        return pd.DataFrame()


def format_trial_url(nct_id: str) -> str:
    """Format ClinicalTrials.gov URL."""
    return f"https://clinicaltrials.gov/study/{nct_id}"


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Biotech Trial Success Predictor",
        page_icon="🧬",
        layout="wide"
    )
    
    st.title("🧬 Biotech Trial Success Predictor")
    st.markdown("Predicting Phase 2 & 3 clinical trial success probabilities")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No prediction data available. Please run the data pipeline first.")
        st.code("""
# Run these commands to generate predictions:
python scripts/fetch_data.py
python scripts/train_model.py
        """)
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Phase filter
    phase_options = ["All"] + sorted(df["phase_num"].unique().tolist())
    selected_phase = st.sidebar.selectbox("Phase", phase_options)
    
    # Bucket filter
    bucket_options = st.sidebar.multiselect(
        "Bucket",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )
    
    # Enrollment filter
    max_enrollment = int(df["enrollment"].max()) if df["enrollment"].max() > 0 else 5000
    min_enrollment = st.sidebar.slider(
        "Minimum Enrollment",
        min_value=0,
        max_value=max_enrollment,
        value=0,
        step=10
    )
    
    # Indication filter
    indication_search = st.sidebar.text_input("Indication Contains", "")
    
    # Apply filters
    df_filtered = df.copy()
    
    if selected_phase != "All":
        df_filtered = df_filtered[df_filtered["phase_num"] == selected_phase]
    
    if bucket_options:
        df_filtered = df_filtered[df_filtered["bucket"].isin(bucket_options)]
    
    df_filtered = df_filtered[df_filtered["enrollment"] >= min_enrollment]
    
    if indication_search:
        df_filtered = df_filtered[
            df_filtered["condition"].str.contains(indication_search, case=False, na=False)
        ]
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trials", len(df_filtered))
    
    with col2:
        high_count = len(df_filtered[df_filtered["bucket"] == "High"])
        st.metric("High Probability", high_count)
    
    with col3:
        medium_count = len(df_filtered[df_filtered["bucket"] == "Medium"])
        st.metric("Medium Probability", medium_count)
    
    with col4:
        low_count = len(df_filtered[df_filtered["bucket"] == "Low"])
        st.metric("Low Probability", low_count)
    
    st.markdown("---")
    
    # Main table
    st.subheader("Clinical Trials")
    
    if len(df_filtered) == 0:
        st.info("No trials match the selected filters.")
        return
    
    # Prepare display DataFrame
    display_df = df_filtered[[
        "sponsor_name",
        "nct_id",
        "brief_title",
        "phase_num",
        "condition",
        "probability",
        "bucket",
        "primary_completion_date",
    ]].copy()
    
    # Rename columns for display
    display_df.columns = [
        "Company",
        "Trial ID",
        "Title",
        "Phase",
        "Indication",
        "Probability",
        "Bucket",
        "Primary Completion Date",
    ]
    
    # Add ticker placeholder
    display_df.insert(1, "Ticker", "N/A")
    
    # Format probability as percentage
    display_df["Probability"] = display_df["Probability"].apply(lambda x: f"{x:.1%}")
    
    # Format phase
    display_df["Phase"] = display_df["Phase"].apply(lambda x: f"Phase {int(x)}")
    
    # Sort by probability (descending)
    display_df = display_df.sort_values("Probability", ascending=False)
    
    # Display table with color coding
    def highlight_bucket(row):
        """Color code rows by bucket."""
        if row["Bucket"] == "High":
            return ["background-color: #d4edda"] * len(row)
        elif row["Bucket"] == "Medium":
            return ["background-color: #fff3cd"] * len(row)
        else:
            return ["background-color: #f8d7da"] * len(row)
    
    styled_df = display_df.style.apply(highlight_bucket, axis=1)
    st.dataframe(styled_df, use_container_width=True, height=600)
    
    # Detail view
    st.markdown("---")
    st.subheader("Trial Details")
    
    # Trial selection
    trial_ids = df_filtered["nct_id"].tolist()
    if trial_ids:
        selected_trial = st.selectbox(
            "Select a trial to view details:",
            options=trial_ids,
            format_func=lambda x: f"{x} - {df_filtered[df_filtered['nct_id'] == x]['brief_title'].iloc[0][:60]}..."
        )
        
        if selected_trial:
            trial_data = df_filtered[df_filtered["nct_id"] == selected_trial].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Trial Information**")
                st.write(f"**Trial ID:** {trial_data['nct_id']}")
                st.write(f"**Title:** {trial_data['brief_title']}")
                st.write(f"**Sponsor:** {trial_data['sponsor_name']}")
                st.write(f"**Phase:** Phase {int(trial_data['phase_num'])}")
                st.write(f"**Indication:** {trial_data['condition']}")
                st.write(f"**Primary Completion:** {trial_data['primary_completion_date']}")
                
                trial_url = format_trial_url(trial_data['nct_id'])
                st.markdown(f"**Source:** [ClinicalTrials.gov]({trial_url})")
            
            with col2:
                st.markdown("**Prediction**")
                st.write(f"**Probability:** {trial_data['probability']:.1%}")
                st.write(f"**Bucket:** {trial_data['bucket']}")
                
                st.markdown("**Feature Values**")
                st.write(f"- Phase Number: {trial_data['phase_num']}")
                st.write(f"- Is Phase 3: {trial_data['is_phase3']}")
                st.write(f"- Enrollment: {int(trial_data['enrollment'])}")
                st.write(f"- Sites: {int(trial_data['sites'])}")
                st.write(f"- Indication Prior: {trial_data['indication_prior']:.2f}")
    
    # Disclaimer
    st.markdown("---")
    st.warning("⚠️ **Disclaimer:** Not investment advice. For informational purposes only.")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        Biotech Trial Success Predictor MVP | Data from ClinicalTrials.gov
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

