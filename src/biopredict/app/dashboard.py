"""Streamlit dashboard for biotech trial predictions."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from biopredict.config import PROCESSED_DATA_DIR
from biopredict.model.train import load_predictions
from biopredict.app.stock_utils import (
    lookup_ticker, get_stock_data, get_stock_info,
    format_price, format_large_number, get_period_label
)


def load_data() -> pd.DataFrame:
    """Load prediction data for dashboard."""
    try:
        df = load_predictions()
        # Add ticker column
        df['ticker'] = df['sponsor_name'].apply(lookup_ticker)
        return df
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        st.info("Please run `python scripts/train_model.py` first to generate predictions.")
        return pd.DataFrame()


def format_trial_url(nct_id: str) -> str:
    """Format ClinicalTrials.gov URL."""
    return f"https://clinicaltrials.gov/study/{nct_id}"


def get_rating(value: float, low_threshold: float, high_threshold: float, higher_better: bool = True) -> int:
    """Convert a metric to a 1-5 rating.
    
    Args:
        value: The metric value
        low_threshold: Threshold for rating 1 (if higher_better) or 5 (if not)
        high_threshold: Threshold for rating 5 (if higher_better) or 1 (if not)
        higher_better: If True, higher values get better ratings
        
    Returns:
        Rating from 1-5
    """
    if value is None:
        return 3
    
    if higher_better:
        if value >= high_threshold:
            return 5
        elif value >= (high_threshold + low_threshold) / 2:
            return 4
        elif value >= low_threshold:
            return 3
        elif value >= low_threshold / 2:
            return 2
        else:
            return 1
    else:
        if value <= high_threshold:
            return 5
        elif value <= (high_threshold + low_threshold) / 2:
            return 4
        elif value <= low_threshold:
            return 3
        elif value <= low_threshold * 1.5:
            return 2
        else:
            return 1


def get_rating_color(rating: int) -> str:
    """Get color for rating."""
    colors = {
        1: "#d32f2f",  # Red
        2: "#f57c00",  # Orange
        3: "#fbc02d",  # Yellow
        4: "#689f38",  # Light green
        5: "#388e3c",  # Green
    }
    return colors.get(rating, "#757575")


def get_daily_change_color(change_pct: float) -> str:
    """Get color for daily change percentage."""
    if change_pct > 0:
        return "#28a745"  # Green for positive
    elif change_pct < 0:
        return "#dc3545"  # Red for negative
    else:
        return "#6c757d"  # Gray for neutral


def get_probability_bucket_color(bucket: str) -> str:
    """Get color for probability bucket."""
    if bucket == "High":
        return "#28a745"  # Green
    elif bucket == "Medium":
        return "#ffc107"  # Yellow
    else:  # Low
        return "#dc3545"  # Red


def apply_row_coloring(df: pd.DataFrame) -> pd.DataFrame:
    """Apply color coding to dataframe rows based on probability bucket."""
    # Return the dataframe without styling to avoid jinja2 dependency issues
    # Color coding will be handled in the display logic instead
    return df


def display_colored_table(df: pd.DataFrame, height: int = 600):
    """Display dataframe with color indicators for probability buckets."""
    if df.empty:
        st.info("No data to display")
        return
    
    # Add color indicators to the dataframe
    df_display = df.copy()
    
    # Add color indicators based on bucket
    def add_color_indicator(bucket):
        if bucket == "High":
            return "🟢 High"
        elif bucket == "Medium":
            return "🟡 Medium"
        else:
            return "🔴 Low"
    
    if 'Rating' in df_display.columns:
        df_display['Rating'] = df_display['Rating'].apply(add_color_indicator)
    elif 'Bucket' in df_display.columns:
        df_display['Bucket'] = df_display['Bucket'].apply(add_color_indicator)
    elif 'bucket' in df_display.columns:
        df_display['bucket'] = df_display['bucket'].apply(add_color_indicator)
    
    # Add custom CSS for column widths to prevent text cutoff
    st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
    }
    .dataframe th {
        background-color: #f0f2f6;
        font-weight: bold;
        text-align: left;
        padding: 8px;
    }
    .dataframe td {
        padding: 8px;
        white-space: nowrap;
        overflow: visible;
    }
    /* Ensure Rating column has enough width */
    .dataframe th:nth-child(2), .dataframe td:nth-child(2) {
        min-width: 130px;
        width: 130px;
    }
    /* Company column */
    .dataframe th:nth-child(1), .dataframe td:nth-child(1) {
        min-width: 150px;
        width: 150px;
    }
    /* Probability column */
    .dataframe th:nth-child(3), .dataframe td:nth-child(3) {
        min-width: 100px;
        width: 100px;
    }
    /* Ticker column */
    .dataframe th:nth-child(4), .dataframe td:nth-child(4) {
        min-width: 80px;
        width: 80px;
    }
    /* Trial ID column */
    .dataframe th:nth-child(5), .dataframe td:nth-child(5) {
        min-width: 120px;
        width: 120px;
    }
    /* Title column - flexible width */
    .dataframe th:nth-child(6), .dataframe td:nth-child(6) {
        min-width: 200px;
    }
    /* Phase column */
    .dataframe th:nth-child(7), .dataframe td:nth-child(7) {
        min-width: 80px;
        width: 80px;
    }
    /* Indication column - flexible width */
    .dataframe th:nth-child(8), .dataframe td:nth-child(8) {
        min-width: 200px;
    }
    /* Primary Completion Date column */
    .dataframe th:nth-child(9), .dataframe td:nth-child(9) {
        min-width: 140px;
        width: 140px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the dataframe
    st.dataframe(df_display, use_container_width=True, height=height)


def show_stock_chart(ticker: str, period: str):
    """Display stock price chart."""
    try:
        df = get_stock_data(ticker, period)
        
        if df is None or df.empty:
            st.warning(f"Unable to load stock data for {ticker}. This may be due to API rate limits or ticker availability.")
            return
    except Exception as e:
        st.error(f"Error loading chart: {str(e)}")
        return
    
    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    )])
    
    fig.update_layout(
        title=f"{ticker} Stock Price - {get_period_label(period)}",
        yaxis_title="Price ($)",
        xaxis_title="Date",
        height=500,
        template="plotly_white",
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_company_detail(company_name: str, ticker: str, df_all: pd.DataFrame):
    """Display detailed company page with stock info and trials."""
    st.title(f"{company_name}")
    
    # Get all trials for this company
    company_trials = df_all[df_all['sponsor_name'] == company_name].copy()
    
    # Calculate aggregate probability
    avg_prob = company_trials['probability'].mean()
    bucket_counts = company_trials['bucket'].value_counts()
    
    # Header with company info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if ticker:
            st.markdown(f"## **{company_name}** (${ticker})")
        else:
            st.markdown(f"## **{company_name}** (Private/Unknown Ticker)")
    
    with col2:
        # Determine overall bucket based on average
        if avg_prob >= 0.70:
            overall_bucket = "High"
        elif avg_prob >= 0.40:
            overall_bucket = "Medium"
        else:
            overall_bucket = "Low"
        # Color code the success probability
        if overall_bucket == "High":
            color = "#4CAF50"  # Lighter, more lively green
        elif overall_bucket == "Medium":
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red
        
        st.markdown(f"### **Success Probability: <span style='color:{color}; font-weight: bold;'>{overall_bucket}</span>**", unsafe_allow_html=True)
    
    with col3:
        st.metric("Avg Probability", f"{avg_prob:.1%}")
    
    st.markdown("---")
    
    # Get stock info early for valuation analysis
    info = None
    if ticker:
        info = get_stock_info(ticker)
    
    # Valuation Analysis Section (moved above stock information)
    if ticker and info:
        # Determine valuation assessment
        pe_ratio = info.get('trailingPE')
        industry_pe = 20  # Biotech industry average approximation
        ev_to_revenue = info.get('enterpriseToRevenue')
        
        valuation_score = 0
        total_metrics = 0
        
        if pe_ratio:
            total_metrics += 1
            if pe_ratio < industry_pe * 0.8:
                valuation_score += 1  # Undervalued
            elif pe_ratio > industry_pe * 1.2:
                valuation_score -= 1  # Overvalued
        
        if ev_to_revenue:
            total_metrics += 1
            if ev_to_revenue < 3:
                valuation_score += 1
            elif ev_to_revenue > 8:
                valuation_score -= 1
        
        # Determine rating
        if total_metrics > 0:
            avg_score = valuation_score / total_metrics
            if avg_score > 0.3:
                valuation_rating = "Underperform"
                explanation = "The company appears overvalued compared to industry peers."
            elif avg_score < -0.3:
                valuation_rating = "Outperform"
                explanation = "The company appears undervalued, presenting potential upside."
            else:
                valuation_rating = "Market Perform"
                explanation = "The company is fairly valued relative to industry benchmarks."
        else:
            valuation_rating = "Market Perform"
            explanation = "Insufficient data for comprehensive valuation analysis."
        
        # Color code the valuation rating
        if valuation_rating == "Outperform":
            rating_color = "#4CAF50"  # Green
        elif valuation_rating == "Underperform":
            rating_color = "#F44336"  # Red
        else:  # Market Perform
            rating_color = "#FFC107"  # Yellow
        
        st.markdown(f"## Valuation Analysis: <span style='color:{rating_color}; font-weight: bold;'>{valuation_rating}</span>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Valuation Metrics vs Industry")
            if pe_ratio:
                st.write(f"**P/E Ratio:** {pe_ratio:.2f} (Industry avg: ~{industry_pe})")
                if pe_ratio < industry_pe:
                    st.success("Below industry average - potentially undervalued")
                elif pe_ratio > industry_pe * 1.2:
                    st.warning("Above industry average - potentially overvalued")
                else:
                    st.info("In line with industry average")
            
            if ev_to_revenue:
                st.write(f"**EV/Revenue:** {ev_to_revenue:.2f} (Biotech range: 2-8)")
                if ev_to_revenue < 3:
                    st.success("Low multiple - efficient valuation")
                elif ev_to_revenue > 8:
                    st.warning("High multiple - premium valuation")
                else:
                    st.info("Moderate valuation multiple")
        
        with col2:
            st.markdown("##### Assessment")
            st.write(explanation)
            
            # Trial success impact
            if avg_prob >= 0.70:
                st.write("**Pipeline Strength:** High trial success probability could drive upside.")
            elif avg_prob >= 0.40:
                st.write("**Pipeline Strength:** Moderate trial success probability.")
            else:
                st.write("**Pipeline Strength:** Lower trial success probability may pressure valuation.")
            
            st.info("**Note:** This is a simplified analysis. Full valuation requires detailed financial modeling, peer comparison, and market analysis.")
        
        st.markdown("---")
    
    # Stock information (if ticker available)
    if ticker:
        st.subheader("Stock Information & Financials")
        
        if info:
            # Price metrics
            st.markdown("#### Market Data")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                st.metric("Current Price", format_price(current_price))
            
            with col2:
                prev_close = info.get('previousClose')
                if current_price and prev_close:
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    color = get_daily_change_color(change_pct)
                    st.markdown(f"**Daily Change**<br><span style='color:{color}; font-size: 1.5em; font-weight: bold;'>{change_pct:+.2f}%</span>", unsafe_allow_html=True)
                else:
                    st.metric("Daily Change", "N/A")
            
            with col3:
                market_cap = info.get('marketCap')
                st.metric("Market Cap", format_large_number(market_cap))
            
            with col4:
                volume = info.get('volume')
                if volume:
                    st.metric("Volume", f"${volume:,}")
                else:
                    st.metric("Volume", "N/A")
            
            # Financial metrics
            st.markdown("#### Financial Health")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                revenue = info.get('totalRevenue')
                st.metric("Total Revenue", format_large_number(revenue))
            
            with col2:
                profit_margin = info.get('profitMargins')
                if profit_margin:
                    rating = get_rating(profit_margin, 0.05, 0.15, higher_better=True)
                    color = get_rating_color(rating)
                    st.metric("Profit Margin", f"{profit_margin*100:.1f}%")
                    st.markdown(f"<span style='color:{color}'>Rating: {rating}/5</span>", unsafe_allow_html=True)
                else:
                    st.metric("Profit Margin", "N/A")
            
            with col3:
                debt_to_equity = info.get('debtToEquity')
                if debt_to_equity:
                    rating = get_rating(debt_to_equity, 100, 50, higher_better=False)
                    color = get_rating_color(rating)
                    st.metric("Debt/Equity", f"{debt_to_equity:.1f}")
                    st.markdown(f"<span style='color:{color}'>Rating: {rating}/5</span>", unsafe_allow_html=True)
                else:
                    st.metric("Debt/Equity", "N/A")
            
            with col4:
                cash = info.get('totalCash')
                st.metric("Cash Position", format_large_number(cash))
            
            # Valuation metrics
            st.markdown("#### Valuation Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pe_ratio = info.get('trailingPE')
                st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
            
            with col2:
                peg_ratio = info.get('pegRatio')
                st.metric("PEG Ratio", f"{peg_ratio:.2f}" if peg_ratio else "N/A")
            
            with col3:
                price_to_book = info.get('priceToBook')
                st.metric("Price/Book", f"{price_to_book:.2f}" if price_to_book else "N/A")
            
            with col4:
                ev_to_revenue = info.get('enterpriseToRevenue')
                st.metric("EV/Revenue", f"{ev_to_revenue:.2f}" if ev_to_revenue else "N/A")
        
        st.markdown("---")
        
        # Stock chart with timeframe selector
        st.subheader("Stock Price Chart")
        
        timeframe_cols = st.columns(7)
        timeframes = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        timeframe_labels = ["1M", "3M", "6M", "1Y", "2Y", "5Y", "All"]
        
        # Create buttons for timeframe selection
        selected_period = st.session_state.get('selected_period', '1y')
        
        for i, (period, label) in enumerate(zip(timeframes, timeframe_labels)):
            with timeframe_cols[i]:
                if st.button(label, key=f"tf_{period}_{company_name}"):
                    st.session_state['selected_period'] = period
                    selected_period = period
        
        show_stock_chart(ticker, selected_period)
        
        st.markdown("---")
    else:
        st.info("This company appears to be private or ticker information is not available.")
        st.markdown("---")
    
    # Clinical trials for this company
    st.subheader("Clinical Trials Portfolio")
    
    # Trial summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trials", len(company_trials))
    
    with col2:
        high_count = bucket_counts.get("High", 0)
        st.metric("High Probability", high_count)
    
    with col3:
        medium_count = bucket_counts.get("Medium", 0)
        st.metric("Medium Probability", medium_count)
    
    with col4:
        low_count = bucket_counts.get("Low", 0)
        st.metric("Low Probability", low_count)
    
    # Trials table
    st.markdown("##### Trials Details")
    
    display_trials = company_trials[[
        'nct_id', 'brief_title', 'phase_num', 'condition',
        'enrollment', 'probability', 'bucket', 'primary_completion_date'
    ]].copy()
    
    display_trials.columns = [
        'Trial ID', 'Title', 'Phase', 'Indication',
        'Enrollment', 'Probability', 'Rating', 'Completion Date'
    ]
    
    display_trials['Probability'] = display_trials['Probability'].apply(lambda x: f"{x:.1%}")
    display_trials['Phase'] = display_trials['Phase'].apply(lambda x: f"Phase {int(x)}")
    display_trials = display_trials.sort_values('Probability', ascending=False)
    
    # Display table with color-coded rows
    display_colored_table(display_trials, height=400)
    
    
    # Back button
    st.markdown("---")
    if st.button("Back to All Trials"):
        st.session_state['view'] = 'main'
        st.session_state['selected_company'] = None
        st.rerun()


def show_main_view():
    """Display main trials table view."""
    # Display logo with reduced spacing
    logo_path = Path(__file__).parent.parent.parent.parent / "logo" / "svg-logo.svg"
    if logo_path.exists():
        # Add custom CSS to reduce spacing
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display logo with minimal margin
        st.markdown('<div style="margin-top: -2rem; margin-bottom: -1rem;">', unsafe_allow_html=True)
        st.image(str(logo_path), use_container_width=False, width=400)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("Biotech Trial Success Predictor")
    
    # Subtitle with reduced spacing
    st.markdown('<p style="margin-top: 0.5rem; font-size: 1.1rem;">Predicting Phase 2 & 3 clinical trial success probabilities</p>', unsafe_allow_html=True)
    
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
    
    # Company type filter - PROMINENT at top
    public_company_count = df["ticker"].notna().sum()
    total_trials = len(df)
    st.sidebar.markdown("### Company Type")
    show_public_only = st.sidebar.checkbox(
        f"Show only public companies ({public_company_count} of {total_trials} trials)",
        value=False,
        help="Filter to show only trials from publicly traded biotech/pharma companies with stock tickers"
    )
    st.sidebar.markdown("---")
    
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
    
    if show_public_only:
        df_filtered = df_filtered[df_filtered["ticker"].notna()]
    
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
    
    # Show active filters
    if show_public_only:
        st.info(f"**Showing {len(df_filtered)} trials from publicly traded companies only** (Filter active in sidebar)")
    
    if len(df_filtered) == 0:
        st.info("No trials match the selected filters.")
        return
    
    # Prepare display DataFrame
    display_df = df_filtered[[
        "sponsor_name",
        "bucket",
        "probability",
        "ticker",
        "nct_id",
        "brief_title",
        "phase_num",
        "condition",
        "primary_completion_date",
    ]].copy()
    
    # Rename columns for display
    display_df.columns = [
        "Company",
        "Rating",
        "Probability",
        "Ticker",
        "Trial ID",
        "Title",
        "Phase",
        "Indication",
        "Primary Completion Date",
    ]
    
    # Fill N/A for missing tickers
    display_df["Ticker"] = display_df["Ticker"].fillna("N/A")
    
    # Format probability as percentage
    display_df["Probability"] = display_df["Probability"].apply(lambda x: f"{x:.1%}")
    
    # Format phase
    display_df["Phase"] = display_df["Phase"].apply(lambda x: f"Phase {int(x)}")
    
    # Sort by probability (descending)
    display_df = display_df.sort_values("Probability", ascending=False)
    
    # Display table with clickable companies and color coding
    st.markdown("**Tip:** Select a company below to view detailed stock information and trial portfolio")
    
    # Display table with color-coded rows
    display_colored_table(display_df)
    
    # Company selection for detail view
    st.markdown("---")
    st.subheader("View Company Details")
    
    # Get unique companies with their tickers
    companies = df_filtered[['sponsor_name', 'ticker']].drop_duplicates().sort_values('sponsor_name')
    company_list = companies['sponsor_name'].tolist()
    
    selected_company = st.selectbox(
        "Select a company to view detailed information:",
        options=company_list,
        format_func=lambda x: f"{x} ({companies[companies['sponsor_name'] == x]['ticker'].iloc[0] if companies[companies['sponsor_name'] == x]['ticker'].iloc[0] else 'Private'})"
    )
    
    if st.button("View Company Details"):
        company_ticker = companies[companies['sponsor_name'] == selected_company]['ticker'].iloc[0]
        st.session_state['view'] = 'company'
        st.session_state['selected_company'] = selected_company
        st.session_state['selected_ticker'] = company_ticker if pd.notna(company_ticker) else None
        st.rerun()
    
    # Disclaimer
    st.markdown("---")
    st.warning("**Disclaimer:** Not investment advice. For informational purposes only.")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        Biotech Trial Success Predictor MVP | Data from ClinicalTrials.gov & Yahoo Finance
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Biotech Trial Success Predictor",
        page_icon="",
        layout="wide"
    )
    
    # Initialize session state
    if 'view' not in st.session_state:
        st.session_state['view'] = 'main'
    if 'selected_company' not in st.session_state:
        st.session_state['selected_company'] = None
    if 'selected_ticker' not in st.session_state:
        st.session_state['selected_ticker'] = None
    
    # Route to appropriate view
    if st.session_state['view'] == 'company' and st.session_state['selected_company']:
        df_all = load_data()
        show_company_detail(
            st.session_state['selected_company'],
            st.session_state['selected_ticker'],
            df_all
        )
    else:
        show_main_view()


if __name__ == "__main__":
    main()
