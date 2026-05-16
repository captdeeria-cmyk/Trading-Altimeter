# ✈ Trading Altimeter
### Navigating the Markets with Cockpit Discipline
**Institutional-grade NSE Stock Analytics & Backtesting Platform**

---

## 📋 Table of Contents
1. [What This App Does](#what-this-app-does)
2. [System Requirements](#system-requirements)
3. [Complete Setup Guide (Non-Technical)](#complete-setup-guide)
4. [Setting Up the .env File (Broker Integration)](#env-file-setup)
5. [Setting Up Logo & Banner Assets](#assets-setup)
6. [Running the App](#running-the-app)
7. [Deploying Online (Streamlit Cloud — Free)](#deploying-online)
8. [Feature Guide](#feature-guide)
9. [File Structure](#file-structure)
10. [Troubleshooting](#troubleshooting)

---

## What This App Does

Trading Altimeter is a desktop web application for Indian stock market (NSE) analysis:

| Feature | Description |
|---------|-------------|
| **Live Dashboard** | Real-time prices for 250 NSE stocks (Nifty 50, Next 50, F&O) |
| **Stock Analysis** | Full chart with 200 HMA, EMA, RSI, MACD + signal detection |
| **Backtester** | Test the 200 HMA crossover strategy on historical data |
| **HMA Scanner** | Scan all 250 stocks for breakout/breakdown signals |
| **Watchlist** | Track custom stocks with persistent storage |
| **Portfolio** | Track holdings with live P&L calculations |
| **Broker Integration** | Paper trading + live Dhan broker orders |

**Core Strategy — 200 Hull Moving Average (HMA):**
- 🚀 **BULLISH BREAKOUT** — Price crosses above the 200 HMA
- 💀 **BEARISH BREAKDOWN** — Price crosses below the 200 HMA
- 👀 **APPROACHING** — Price within 1.5% of the 200 HMA

---

## System Requirements

- **OS:** Windows 10/11, macOS 12+, or Ubuntu 20+
- **RAM:** 4 GB minimum, 8 GB recommended
- **Internet:** Required for live data (yfinance)
- **Python:** 3.10 or higher

---

## Complete Setup Guide

### Step 1 — Install Python

1. Go to https://www.python.org/downloads/
2. Download **Python 3.11** (recommended)
3. During installation on Windows: ✅ **Check "Add Python to PATH"**
4. Verify: Open Terminal / Command Prompt and type:
   ```
   python --version
   ```
   You should see `Python 3.11.x`

### Step 2 — Download the App

Option A — If you have Git:
```bash
git clone <your-repo-url>
cd trading_altimeter
```

Option B — Download ZIP, extract it, and open a terminal in that folder.

### Step 3 — Create a Virtual Environment

Open Terminal / Command Prompt in the `trading_altimeter` folder:

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required libraries. May take 3-5 minutes on first run.

### Step 5 — Run the App

```bash
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**

---

## .env File Setup

The `.env` file stores your API keys securely. Create a file named `.env`
(exactly, no extension) in the `trading_altimeter` folder:

```
# Dhan Broker (for live trading — optional)
DHAN_CLIENT_ID=your_client_id_here
DHAN_ACCESS_TOKEN=your_access_token_here

# News APIs (optional — app works without these using mock data)
FINNHUB_API_KEY=your_finnhub_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### How to get Dhan credentials:
1. Log in to https://web.dhan.co
2. Go to **My Profile → API Access**
3. Generate Client ID and Access Token
4. Paste them in `.env`

### How to get Finnhub API key (free):
1. Go to https://finnhub.io/register
2. Sign up for free
3. Copy your API key from the dashboard
4. Paste as `FINNHUB_API_KEY=your_key`

> ⚠️ **Important:** Never share your `.env` file. Add it to `.gitignore` if using Git.
> The app runs perfectly without any API keys (paper trading + mock news).

---

## Assets Setup

Place your branding images in an `assets/` folder inside the app directory:

```
trading_altimeter/
├── assets/
│   ├── logo.png     ← Square logo (recommended: 200×200 px)
│   └── banner.png   ← Wide banner (recommended: 1200×300 px)
├── app.py
├── ...
```

**To create the assets folder:**

Windows:
```cmd
mkdir assets
```

Mac/Linux:
```bash
mkdir assets
```

Then copy your logo and banner PNG files into the `assets/` folder.

> If the images are missing, the app gracefully shows a styled text banner instead.

---

## Running the App

Every time you want to use the app:

1. Open Terminal in the `trading_altimeter` folder
2. Activate your virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Run: `streamlit run app.py`
4. Browser opens at http://localhost:8501

To stop: Press `Ctrl + C` in the terminal.

---

## Deploying Online (Streamlit Cloud — Free)

You can host this app online so it's accessible from any browser:

1. Create a free account at https://streamlit.io/cloud
2. Push your code to a GitHub repository (make sure `.env` is in `.gitignore`)
3. In Streamlit Cloud, click **New App** → connect your GitHub repo
4. Set `app.py` as the main file
5. Add your secrets in **Advanced Settings → Secrets** (same format as `.env`):
   ```toml
   DHAN_CLIENT_ID = "your_id"
   DHAN_ACCESS_TOKEN = "your_token"
   FINNHUB_API_KEY = "your_key"
   ```
6. Deploy — your app gets a public URL like `https://yourname-trading-altimeter.streamlit.app`

---

## Feature Guide

### 🏠 Dashboard
- Shows live prices for 250 NSE stocks in a grid
- Includes Nifty 50, Sensex, and India VIX indices
- Click any stock card to jump to full analysis
- Use the dropdown to switch between stock groups

### 📈 Stock Analysis
- Select any stock from the 250-stock universe
- View 4-panel chart: Candlestick + HMA, Volume, RSI, MACD
- HMA signal is prominently shown with annotation arrow on chart
- Expand "Latest News & Sentiment" for news + POSITIVE/NEGATIVE/NEUTRAL tags

### 🔬 Backtester
- Select a Nifty 50 stock, date range, and starting capital
- Runs the 200 HMA crossover strategy historically
- Shows: buy/sell markers on chart, equity curve, and 6 performance metrics
- View full trade log in the expandable section

### 🛰 HMA Scanner
- Scans all 250 stocks for 200 HMA signals
- Filter by signal type (Bullish/Bearish/Approaching)
- Results cached for 5 minutes — click a row to jump to analysis

### ⭐ Watchlist
- Add any NSE symbol (not limited to the 250)
- Persists across restarts (saved to `watchlist.json`)
- Shows live LTP, change %, and HMA signal for each stock

### 💼 Portfolio
- Add holdings with quantity and average buy price
- Tracks unrealised P&L, day P&L, and overall portfolio performance
- Persists across restarts (saved to `portfolio.json`)

### 📄 Paper Trading (Sidebar)
- Default ON — all orders are simulated, nothing real is placed
- Toggle to LIVE mode only if Dhan credentials are configured
- Paper trade log visible in sidebar

---

## File Structure

```
trading_altimeter/
├── app.py              ← Main UI and routing
├── utils.py            ← CSS, stock universe, helper functions
├── indicators.py       ← Data fetching, 200 HMA, signals
├── backtester.py       ← Historical backtest engine
├── news_sentiment.py   ← News fetching + VADER sentiment
├── watchlist.py        ← Watchlist persistence and UI
├── portfolio.py        ← Portfolio P&L tracking
├── dhan_broker.py      ← Dhan API + paper trading
├── requirements.txt    ← Python dependencies
├── .env                ← Your API keys (create manually)
├── assets/
│   ├── logo.png        ← App logo (add your own)
│   └── banner.png      ← App banner (add your own)
├── watchlist.json      ← Auto-created when you add stocks
├── portfolio.json      ← Auto-created when you add holdings
└── paper_trades.json   ← Auto-created on first paper trade
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `pandas_ta` install fails | Try `pip install pandas_ta --no-build-isolation` |
| Stock shows no data | May be delisted or market closed; try another stock |
| App won't open in browser | Go to http://localhost:8501 manually |
| Dhan orders failing | Verify `.env` credentials; ensure Paper Mode is OFF |
| Scanner is slow | Expected — scanning 250 stocks takes 2-5 min |
| `venv` not found | Run `python -m venv venv` first |

### Windows-specific
- Use `python` not `python3`
- If activation fails: run `Set-ExecutionPolicy RemoteSigned` in PowerShell

### Data Notes
- yfinance data is delayed ~15 minutes for NSE
- HMA requires 200 bars of history; very new stocks may show no signal
- Weekend/holiday data not available (expected behaviour)

---

## Disclaimer

> Trading Altimeter is for **educational and informational purposes only**.
> It is not financial advice. Past backtest performance does not guarantee
> future results. Always consult a SEBI-registered advisor before trading.
> The developers are not responsible for any trading losses.

---

*Built with ❤ using Python, Streamlit, yfinance, pandas_ta, and Plotly.*
*Strategy inspired by Hull Moving Average analysis for NSE equities.*