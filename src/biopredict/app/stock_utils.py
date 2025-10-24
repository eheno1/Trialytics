"""Stock market utilities for company information."""
import pandas as pd
import streamlit as st
from typing import Optional, Dict
import re
import requests
from datetime import datetime, timedelta

# Try to import yfinance (optional for Python 3.8 compatibility)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except (ImportError, TypeError) as e:
    YFINANCE_AVAILABLE = False
    print(f"yfinance not available (Python 3.8 compatibility): {e}")

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = "FSN3QRJSDJ2W8VK9"


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
def get_alpha_vantage_daily(ticker: str, outputsize: str = "compact") -> Optional[pd.DataFrame]:
    """Get daily stock data from Alpha Vantage.
    
    Args:
        ticker: Stock ticker symbol
        outputsize: 'compact' (100 days) or 'full' (20+ years)
        
    Returns:
        DataFrame with OHLCV data
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": outputsize,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                # Rename columns to match yfinance format
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                
                return df
        
        return None
        
    except Exception as e:
        print(f"Error fetching Alpha Vantage daily data for {ticker}: {e}")
        return None


@st.cache_data(ttl=600)
def get_stock_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch stock data using Alpha Vantage or yfinance (fallback).
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        
    Returns:
        DataFrame with OHLCV data or None if failed
    """
    try:
        # Determine Alpha Vantage output size based on period
        if period in ['1mo', '3mo']:
            outputsize = 'compact'  # 100 days
        else:
            outputsize = 'full'  # 20+ years
        
        # Try Alpha Vantage first
        df = get_alpha_vantage_daily(ticker, outputsize)
        
        if df is not None and not df.empty:
            # Filter to requested period
            period_days = {
                "1mo": 30,
                "3mo": 90,
                "6mo": 180,
                "1y": 365,
                "2y": 730,
                "5y": 1825,
                "max": 7300
            }
            
            days = period_days.get(period, 365)
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df.index >= cutoff_date]
            
            return df
        
        # Fallback to yfinance if available
        if YFINANCE_AVAILABLE:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df is not None and not df.empty:
                return df
        
        return None
            
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


@st.cache_data(ttl=600)
def get_alpha_vantage_overview(ticker: str) -> Optional[Dict]:
    """Get company overview from Alpha Vantage.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with company overview data
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and "Symbol" in data:
                return data
        
        return None
        
    except Exception as e:
        print(f"Error fetching Alpha Vantage overview for {ticker}: {e}")
        return None


@st.cache_data(ttl=600)
def get_alpha_vantage_quote(ticker: str) -> Optional[Dict]:
    """Get real-time quote from Alpha Vantage.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with quote data
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "Global Quote" in data and data["Global Quote"]:
                return data["Global Quote"]
        
        return None
        
    except Exception as e:
        print(f"Error fetching Alpha Vantage quote for {ticker}: {e}")
        return None


@st.cache_data(ttl=600)
def get_stock_info(ticker: str) -> Optional[Dict]:
    """Get comprehensive stock information combining Alpha Vantage and yfinance.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with stock info or None if failed
    """
    try:
        # Try Alpha Vantage first for more detailed data
        av_overview = get_alpha_vantage_overview(ticker)
        av_quote = get_alpha_vantage_quote(ticker)
        
        # Get yfinance data as supplement (if available)
        yf_info = {}
        if YFINANCE_AVAILABLE:
            try:
                stock = yf.Ticker(ticker)
                yf_info = stock.info if stock else {}
            except:
                yf_info = {}
        
        # Merge data from both sources
        info = {}
        
        # Price data (prefer Alpha Vantage for real-time)
        if av_quote:
            info['currentPrice'] = float(av_quote.get('05. price', 0)) if av_quote.get('05. price') else None
            info['previousClose'] = float(av_quote.get('08. previous close', 0)) if av_quote.get('08. previous close') else None
            info['dayHigh'] = float(av_quote.get('03. high', 0)) if av_quote.get('03. high') else None
            info['dayLow'] = float(av_quote.get('04. low', 0)) if av_quote.get('04. low') else None
            info['volume'] = int(av_quote.get('06. volume', 0)) if av_quote.get('06. volume') else None
        elif yf_info:
            info['currentPrice'] = yf_info.get('currentPrice') or yf_info.get('regularMarketPrice')
            info['previousClose'] = yf_info.get('previousClose')
            info['dayHigh'] = yf_info.get('dayHigh')
            info['dayLow'] = yf_info.get('dayLow')
            info['volume'] = yf_info.get('volume')
        
        # Company fundamentals from Alpha Vantage
        if av_overview:
            info['marketCap'] = float(av_overview.get('MarketCapitalization', 0)) if av_overview.get('MarketCapitalization') else None
            info['totalRevenue'] = float(av_overview.get('RevenueTTM', 0)) if av_overview.get('RevenueTTM') else None
            info['profitMargins'] = float(av_overview.get('ProfitMargin', 0)) if av_overview.get('ProfitMargin') else None
            info['trailingPE'] = float(av_overview.get('TrailingPE', 0)) if av_overview.get('TrailingPE') else None
            info['forwardPE'] = float(av_overview.get('ForwardPE', 0)) if av_overview.get('ForwardPE') else None
            info['priceToBook'] = float(av_overview.get('PriceToBookRatio', 0)) if av_overview.get('PriceToBookRatio') else None
            info['pegRatio'] = float(av_overview.get('PEGRatio', 0)) if av_overview.get('PEGRatio') else None
            info['debtToEquity'] = float(av_overview.get('DebtToEquity', 0)) if av_overview.get('DebtToEquity') else None
            info['dividendYield'] = float(av_overview.get('DividendYield', 0)) if av_overview.get('DividendYield') else None
            info['beta'] = float(av_overview.get('Beta', 0)) if av_overview.get('Beta') else None
            info['fiftyTwoWeekHigh'] = float(av_overview.get('52WeekHigh', 0)) if av_overview.get('52WeekHigh') else None
            info['fiftyTwoWeekLow'] = float(av_overview.get('52WeekLow', 0)) if av_overview.get('52WeekLow') else None
            info['shortName'] = av_overview.get('Name')
            info['sector'] = av_overview.get('Sector')
            info['industry'] = av_overview.get('Industry')
            info['description'] = av_overview.get('Description')
            info['employees'] = av_overview.get('FullTimeEmployees')
        
        # Fill in any gaps with yfinance data
        if yf_info:
            for key in ['marketCap', 'totalRevenue', 'profitMargins', 'trailingPE', 'forwardPE', 
                       'priceToBook', 'pegRatio', 'debtToEquity', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
                       'averageVolume', 'totalCash', 'totalDebt', 'enterpriseToRevenue', 'enterpriseToEbitda']:
                if not info.get(key) and yf_info.get(key):
                    info[key] = yf_info.get(key)
        
        if info and len(info) > 1:
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
