import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np
import time, random
import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import quote
import xlsxwriter


# Wikipedia URL for the S&P 500 companies list
wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Read the tables on the page
wiki_tables = pd.read_html(wiki_url)

# First table on the page is the one we want
sp500_tickers = wiki_tables[0]['Symbol'].str.replace('.', '-', regex=False).tolist()

# Timer to delay code execution so Yahoo servers will not be overburdened
time.sleep(random.uniform(30, 60))

# Step 1: Download 1-day data for selected tickers
df_yahoo = yf.download(sp500_tickers, period='1d', interval='1d', auto_adjust=False, threads=True)

# Step 2: Ensure MultiIndex columns are in tuple format
df_yahoo.columns = pd.MultiIndex.from_tuples(df_yahoo.columns)

# Step 3: Stack to move ticker level into rows
df_sp500 = df_yahoo.stack(level=1).reset_index()

# Trading Day
td = df_sp500.iloc[0, 0].strftime('M.D.Y')

# Step 4: Rename columns for clarity
df_sp500 = df_sp500.rename(columns={"level_1": "Ticker"})

# Step 5: Optional – Reorder for aesthetics
df_sp500 = df_sp500[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

# Calculate percentage change from Open to Close
df_sp500['% Change'] = df_sp500[['Open', 'Close']].pct_change(axis=1)['Close']

# Get top and bottom 5 performers
top_5 = df_sp500.nlargest(5, '% Change')
bottom_5 = df_sp500.nsmallest(5, '% Change')
nstocks = pd.concat([top_5, bottom_5])

# ✅ FIXED: URL-encode the query
def get_news_by_ticker(ticker):
    query = quote(f"{ticker} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:3]:
        articles.append(f"{entry.title} ({entry.published})\n{entry.link}")
    return "\n\n".join(articles) if articles else "No articles found"

# Apply function to get news for each ticker
nstocks['News'] = nstocks['Ticker'].apply(get_news_by_ticker)

# Copy final result to clipboard
nstocks.to_clipboard(index=False)

# Top/Bottom 5 to CSV
nstocks.to_csv('top_bottom_stocks.csv', index=False)

# S&P for the day to CSV
df_sp500.to_csv('s&p_500.csv', index=False)

# Both Top/Bottom and S&P to XLSX
with pd.ExcelWriter("daily_stock_movers_with_news.xlsx", engine='xlsxwriter') as writer:
    df_sp500.to_excel(writer, sheet_name='All S&P 500 Data', index=False)
    nstocks.to_excel(writer, sheet_name='Top & Bottom 5 w News', index=False)