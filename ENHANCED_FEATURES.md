# Enhanced Dashboard Features

## 🎉 New Stock Market Integration

The dashboard has been upgraded with comprehensive stock market features for public biotech companies!

### ✨ What's New

#### 1. **Automatic Ticker Detection**
- Automatically identifies public vs. private companies
- Database of 60+ major biotech/pharma companies
- Real-time ticker lookup for all sponsors
- Shows "N/A" for private companies or universities

#### 2. **Company Detail Pages**
Navigate to any company to see:

**Stock Information:**
- Current stock price
- Daily price change (%)
- Today's high/low
- Market capitalization
- Trading volume
- 52-week high/low
- Average volume

**Interactive Stock Charts:**
- Beautiful candlestick charts via Plotly
- Multiple timeframe selection: 1M, 3M, 6M, 1Y, 2Y, 5Y, All Time
- Real-time data from Yahoo Finance
- Professional-grade visualization

**Trial Success Probability** (Prominently Displayed):
- **🟢 High** - ≥70% success probability
- **🟡 Medium** - 40-70% success probability  
- **🔴 Low** - <40% success probability
- Average probability across all company trials
- Breakdown by bucket (High/Medium/Low counts)

**Complete Trial Portfolio:**
- All clinical trials for that company
- Full trial details in sortable table
- Phase, indication, enrollment, completion date
- Individual trial probabilities

#### 3. **Enhanced Main Table**
- **Ticker Column** now shows actual stock symbols
- Filter by "Public Companies Only"
- Click any company to view full details
- Ticker symbols clearly displayed (PFE, MRNA, GILD, etc.)

### 📊 Example Companies with Stock Data

**Public Companies Supported:**
- Pfizer (PFE)
- Moderna (MRNA)
- BioNTech (BNTX)
- Regeneron (REGN)
- Gilead Sciences (GILD)
- Amgen (AMGN)
- Biogen (BIIB)
- Vertex Pharmaceuticals (VRTX)
- Novartis (NVS)
- AstraZeneca (AZN)
- Bristol Myers Squibb (BMY)
- Eli Lilly (LLY)
- Merck (MRK)
- Johnson & Johnson (JNJ)
- AbbVie (ABBV)
- Plus 45+ more!

### 🚀 How to Use

1. **Launch the Dashboard:**
```bash
streamlit run src/biopredict/app/dashboard.py
```

2. **Browse the Main Table:**
   - See ticker symbols in the "Ticker" column
   - Companies with tickers are public/tradeable
   - "N/A" indicates private companies, universities, or hospitals

3. **View Company Details:**
   - Scroll down to "View Company Details" section
   - Select a company from the dropdown
   - Click "View Company Details 📊" button
   - **Bolded probability right next to company name and ticker!**

4. **Explore Stock Charts:**
   - Click timeframe buttons (1M, 3M, 6M, 1Y, 2Y, 5Y, All)
   - See candlestick price charts
   - View key metrics and market data

5. **Analyze Trial Success:**
   - See aggregate success probability prominently displayed
   - View all trials for the company
   - Compare across different companies

### 📈 Data Sources

- **Clinical Trial Data:** ClinicalTrials.gov API
- **Stock Data:** Yahoo Finance (via direct API calls)
- **Ticker Mappings:** Curated database of biotech companies
- **Update Frequency:** Stock data cached for 10 minutes

### 🎯 Key Benefits

1. **Investment Context:** See stock performance alongside trial success predictions
2. **Public vs. Private:** Instantly identify publicly tradeable companies
3. **Comprehensive View:** Full financial + clinical trial picture in one place
4. **Real-time Data:** Live stock prices and historical charts
5. **Professional Quality:** Enterprise-grade visualization and UX

### ⚠️ Important Notes

**Disclaimer:** Not investment advice. For informational purposes only.

**Data Accuracy:**
- Stock prices are real-time from Yahoo Finance
- Ticker mappings based on curated database
- Some companies may not be matched (new IPOs, name changes, etc.)
- Private companies and academic institutions show as "N/A"

**Performance:**
- Stock data is cached for 10 minutes for optimal performance
- Ticker lookups are cached for 1 hour
- First load may take a few seconds while fetching data

### 🔧 Technical Details

**New Dependencies:**
- `plotly` - Interactive charting
- Direct Yahoo Finance API integration (no yfinance library)

**New Files:**
- `src/biopredict/app/stock_utils.py` - Stock data utilities
- Enhanced `dashboard.py` with company detail pages

**Architecture:**
- Session state management for navigation
- Cached API calls for performance
- Graceful handling of missing/invalid tickers
- RESTful API integration with Yahoo Finance

---

## Example Usage Flow

1. **Main View** → See all 1000 trials with ticker symbols
2. **Filter** → Show only public companies
3. **Select Company** → Choose "Moderna" from dropdown  
4. **View Details** → See:
   - **Moderna (MRNA) - 🟢 High** ← Bolded at top!
   - Current price: $85.42
   - Daily change: +2.3%
   - Market cap: $33.2B
   - Stock chart with multiple timeframes
   - 5 clinical trials with probabilities
5. **Switch Timeframe** → Click "5Y" to see 5-year history
6. **Back** → Return to main view, try another company

---

## 🎊 Result

A professional-grade biotech intelligence platform that combines:
✅ Clinical trial success predictions  
✅ Real-time stock market data  
✅ Interactive financial charts  
✅ Company-level analytics  
✅ Public/private company identification  

**All in one beautiful, easy-to-use dashboard!** 🚀

