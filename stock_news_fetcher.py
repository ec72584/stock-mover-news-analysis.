import pandas as pd
import feedparser
from urllib.parse import quote

# Read data from clipboard
df = pd.read_clipboard()

# Calculate percentage change from Open to Close
df['% Change'] = df[['Open', 'Close']].pct_change(axis=1)['Close']

# Get top and bottom 5 performers
top_5 = df.nlargest(5, '% Change')
bottom_5 = df.nsmallest(5, '% Change')

# Combine into one DataFrame
nstocks = pd.concat([top_5, bottom_5])

# Get Google News RSS headlines
def get_google_news_rss(ticker):
    query = quote(f"{ticker} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:3]:  # Limit to top 3 headlines
        articles.append(f"{entry.title} ({entry.published})\n{entry.link}")
    return "\n\n".join(articles)

# Apply news fetching
nstocks['News'] = nstocks['Ticker'].apply(get_google_news_rss)

# Output to clipboard
nstocks.to_clipboard()
