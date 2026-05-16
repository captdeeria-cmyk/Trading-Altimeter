"""
news_sentiment.py — Trading Altimeter
Fetches latest financial news headlines for a given NSE stock and
scores each headline using VADER (Valence Aware Dictionary and sEntiment Reasoner)
sentiment analysis.

VADER is specifically tuned for financial/social text. Compound score:
    >= +0.05  → POSITIVE
    <= -0.05  → NEGATIVE
    between   → NEUTRAL

API Support: Finnhub (free tier). Falls back to mock data if no key is set.
"""

import os
import logging
import datetime
import requests

logger = logging.getLogger(__name__)

# Attempt to load VADER
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _analyzer = SentimentIntensityAnalyzer()
    HAS_VADER = True
except Exception:
    HAS_VADER = False
    _analyzer = None

# ---------------------------------------------------------------------------
# Company name lookup for better news search
# ---------------------------------------------------------------------------
SYMBOL_TO_COMPANY = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "HDFCBANK": "HDFC Bank",
    "INFY": "Infosys",
    "ICICIBANK": "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever",
    "ITC": "ITC Limited",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "LT": "Larsen Toubro",
    "AXISBANK": "Axis Bank",
    "ASIANPAINT": "Asian Paints",
    "MARUTI": "Maruti Suzuki",
    "TITAN": "Titan Company",
    "BAJFINANCE": "Bajaj Finance",
    "WIPRO": "Wipro",
    "SUNPHARMA": "Sun Pharmaceutical",
    "HCLTECH": "HCL Technologies",
    "TATAMOTORS": "Tata Motors",
    "DRREDDY": "Dr Reddy Laboratories",
    "CIPLA": "Cipla",
    "ADANIENT": "Adani Enterprises",
    "NESTLEIND": "Nestle India",
    "ULTRACEMCO": "UltraTech Cement",
    "ONGC": "Oil and Natural Gas Corporation",
    "NTPC": "NTPC Limited",
    "POWERGRID": "Power Grid Corporation",
    "JSWSTEEL": "JSW Steel",
    "TATASTEEL": "Tata Steel",
}


def get_company_name(symbol: str) -> str:
    return SYMBOL_TO_COMPANY.get(symbol, symbol)


# ---------------------------------------------------------------------------
# Sentiment scoring
# ---------------------------------------------------------------------------

def score_headline(headline: str) -> dict:
    """
    Score a single headline using VADER or keyword fallback.

    Returns:
        dict with keys: compound (float), label (str), color (str)
    """
    if HAS_VADER and _analyzer:
        scores = _analyzer.polarity_scores(headline)
        compound = scores["compound"]
    else:
        # Simple keyword fallback
        positive_words = ["profit", "growth", "surge", "gains", "buy",
                          "upgrade", "beat", "strong", "record", "rally",
                          "outperform", "expansion", "dividend", "approved"]
        negative_words = ["loss", "fall", "decline", "sell", "downgrade",
                          "miss", "weak", "cut", "crash", "warning",
                          "fraud", "penalty", "debt", "default", "probe"]
        text = headline.lower()
        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        compound = (pos - neg) * 0.1

    if compound >= 0.05:
        label, color = "POSITIVE", "#00E676"
    elif compound <= -0.05:
        label, color = "NEGATIVE", "#FF1744"
    else:
        label, color = "NEUTRAL", "#8A8D94"

    return {"compound": round(compound, 3), "label": label, "color": color}


# ---------------------------------------------------------------------------
# News Fetching
# ---------------------------------------------------------------------------

def fetch_finnhub_news(symbol: str, api_key: str) -> list:
    """
    Fetch news from Finnhub for a given symbol.
    Uses the free tier endpoint: /company-news
    """
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    # Finnhub uses US ticker format; we use company name as fallback via general news
    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": f"{symbol}.NS",   # Try NSE format
        "from": str(week_ago),
        "to": str(today),
        "token": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[:10]
    except Exception as e:
        logger.warning(f"Finnhub API error for {symbol}: {e}")
    return []


def fetch_newsapi_headlines(company_name: str, api_key: str) -> list:
    """
    Fetch headlines from NewsAPI for a company name query.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{company_name} stock",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            return [{"headline": a["title"], "url": a.get("url", ""),
                     "datetime": a.get("publishedAt", ""),
                     "source": a.get("source", {}).get("name", "")}
                    for a in articles if a.get("title")]
    except Exception as e:
        logger.warning(f"NewsAPI error for {company_name}: {e}")
    return []


def get_mock_news(symbol: str) -> list:
    """Return mock news data when no API key is configured."""
    company = get_company_name(symbol)
    return [
        {
            "headline": f"{company} reports strong quarterly earnings, beats estimates",
            "source": "Economic Times", "url": "#", "datetime": "2025-01-15",
        },
        {
            "headline": f"{company} stock hits 52-week high on positive FII buying",
            "source": "Moneycontrol", "url": "#", "datetime": "2025-01-14",
        },
        {
            "headline": f"Analysts upgrade {company} with revised target price",
            "source": "Business Standard", "url": "#", "datetime": "2025-01-13",
        },
        {
            "headline": f"{company} faces margin pressure due to rising input costs",
            "source": "Mint", "url": "#", "datetime": "2025-01-12",
        },
        {
            "headline": f"Global cues drag {company} lower in morning trade",
            "source": "NDTV Profit", "url": "#", "datetime": "2025-01-11",
        },
        {
            "headline": f"{company} announces new product launch in Q2",
            "source": "Financial Express", "url": "#", "datetime": "2025-01-10",
        },
    ]


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def get_news_with_sentiment(symbol: str) -> list:
    """
    Master function: fetch news for a stock and attach sentiment scores.

    Priority:
    1. Finnhub API (if FINNHUB_API_KEY in .env)
    2. NewsAPI (if NEWSAPI_KEY in .env)
    3. Mock data fallback

    Returns:
        list of dicts with keys: headline, source, url, datetime,
                                  sentiment_label, sentiment_color, compound
    """
    finnhub_key = os.getenv("FINNHUB_API_KEY", "")
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    company = get_company_name(symbol)

    raw_items = []

    if finnhub_key:
        raw = fetch_finnhub_news(symbol, finnhub_key)
        if raw:
            raw_items = [
                {
                    "headline": item.get("headline", ""),
                    "source": item.get("source", ""),
                    "url": item.get("url", "#"),
                    "datetime": str(datetime.datetime.fromtimestamp(
                        item.get("datetime", 0)).date()) if item.get("datetime") else "",
                }
                for item in raw
                if item.get("headline")
            ]

    if not raw_items and newsapi_key:
        raw_items = fetch_newsapi_headlines(company, newsapi_key)

    if not raw_items:
        raw_items = get_mock_news(symbol)

    # Attach sentiment to each item
    result = []
    for item in raw_items:
        sentiment = score_headline(item.get("headline", ""))
        result.append({**item, **sentiment})

    return result