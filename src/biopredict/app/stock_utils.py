"""Stock market utilities for company information."""
import pandas as pd
import streamlit as st
from typing import Optional, Dict
import re
import yfinance as yf


# Common biotech/pharma ticker mappings
KNOWN_TICKERS = {
    "pfizer": "PFE",
    "moderna": "MRNA",
    "biontech": "BNTX",
    "regeneron": "REGN",
    "gilead": "GILD",
    "gilead sciences": "GILD",
    "amgen": "AMGN",
    "biogen": "BIIB",
    "vertex": "VRTX",
    "vertex pharmaceuticals": "VRTX",
    "alexion": "ALXN",
    "biomarin": "BMRN",
    "incyte": "INCY",
    "seattle genetics": "SGEN",
    "seagen": "SGEN",
    "bluebird bio": "BLUE",
    "bluebird": "BLUE",
    "crispr therapeutics": "CRSP",
    "editas medicine": "EDIT",
    "intellia therapeutics": "NTLA",
    "alnylam": "ALNY",
    "alnylam pharmaceuticals": "ALNY",
    "ionis": "IONS",
    "ionis pharmaceuticals": "IONS",
    "sarepta": "SRPT",
    "sarepta therapeutics": "SRPT",
    "novavax": "NVAX",
    "bioxcel therapeutics": "BTAI",
    "cara therapeutics": "CARA",
    "neurocrine": "NBIX",
    "neurocrine biosciences": "NBIX",
    "sage therapeutics": "SAGE",
    "axsome therapeutics": "AXSM",
    "acadia pharmaceuticals": "ACAD",
    "geron": "GERN",
    "geron corporation": "GERN",
    "fate therapeutics": "FATE",
    "spark therapeutics": "ONCE",
    "ultragenyx": "RARE",
    "ultragenyx pharmaceutical": "RARE",
    "sangamo therapeutics": "SGMO",
    "regenxbio": "RGNX",
    "takeda": "TAK",
    "novartis": "NVS",
    "sanofi": "SNY",
    "glaxosmithkline": "GSK",
    "gsk": "GSK",
    "astrazeneca": "AZN",
    "bristol myers squibb": "BMY",
    "bristol-myers squibb": "BMY",
    "bms": "BMY",
    "eli lilly": "LLY",
    "lilly": "LLY",
    "merck": "MRK",
    "johnson & johnson": "JNJ",
    "j&j": "JNJ",
    "jnj": "JNJ",
    "abbvie": "ABBV",
    "jazz pharmaceuticals": "JAZZ",
    "immunomedics": "IMMU",
    "blueprint medicines": "BPMC",
    "argenx": "ARGX",
    "beigene": "BGNE",
    "immunogen": "IMGN",
    "mirati therapeutics": "MRTX",
    "deciphera": "DCPH",
    "arcus biosciences": "RCUS",
    "genmab": "GMAB",
    "exact sciences": "EXAS",
    "guardant health": "GH",
    "natera": "NTRA",
    "invitae": "NVTA",
    "illumina": "ILMN",
    "10x genomics": "TXG",
    "adaptive biotechnologies": "ADPT",
    "allogene therapeutics": "ALLO",
    "bluerock therapeutics": "BRT",
    "voyager therapeutics": "VYGR",
}


@st.cache_data(ttl=3600)
def lookup_ticker(company_name: str) -> Optional[str]:
    """Attempt to find ticker symbol for a company.
    
    Args:
        company_name: Company name
        
    Returns:
        Ticker symbol or None if not found
    """
    if not company_name:
        return None
    
    # Normalize company name
    normalized = company_name.lower().strip()
    
    # Remove common suffixes
    normalized = re.sub(r'\s+(inc\.?|incorporated|corp\.?|corporation|ltd\.?|limited|llc|co\.?|company|pharmaceuticals?|therapeutics?|biosciences?|biotechnology|plc)$', '', normalized, flags=re.IGNORECASE)
    normalized = normalized.strip()
    
    # Check exact match
    if normalized in KNOWN_TICKERS:
        return KNOWN_TICKERS[normalized]
    
    # Check partial match
    for key, ticker in KNOWN_TICKERS.items():
        if key in normalized or normalized in key:
            return KNOWN_TICKERS[key]
    
    return None


@st.cache_data(ttl=600)
def get_stock_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch stock data using yfinance.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        
    Returns:
        DataFrame with OHLCV data or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df is not None and not df.empty:
            return df
        return None
            
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


@st.cache_data(ttl=600)
def get_stock_info(ticker: str) -> Optional[Dict]:
    """Get stock information using yfinance.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with stock info or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if info and len(info) > 1:  # info has at least some data
            return info
        
        return None
        
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return None


def format_price(price: float) -> str:
    """Format price for display."""
    if price is None:
        return "N/A"
    return f"${price:,.2f}"


def format_large_number(num: float) -> str:
    """Format large numbers (market cap, etc.)."""
    if num is None:
        return "N/A"
    
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.0f}"


def get_period_label(period: str) -> str:
    """Get human-readable label for period."""
    labels = {
        "1mo": "1 Month",
        "3mo": "3 Months",
        "6mo": "6 Months",
        "1y": "1 Year",
        "2y": "2 Years",
        "5y": "5 Years",
        "max": "All Time"
    }
    return labels.get(period, period)
