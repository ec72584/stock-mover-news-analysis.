# Top/Bottom Stock Mover News Fetcher

This script:
- Grabs the top and bottom 5 S&P 500 stocks for a single day
- Calculates percent change from Open to Close
- Uses Google News RSS to fetch headlines explaining the movement

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python stock_news_fetcher.py
```

The script expects stock data to be copied to your clipboard (e.g., from Yahoo Finance exports).
It outputs a DataFrame with tickers, percent change, and related news.
