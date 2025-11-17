# MoodMonitor 😎
Quick vibes checker for X (Twitter). It looks at tweets (by search or by user) and tells you if people are feeling positive, neutral, or negative. Basically: is the timeline chill or salty?

## What is this?
- It grabs tweets and runs VADER sentiment on them.
- You can print a tiny summary in the terminal or dump everything to CSV.
- No complicated setup. One token, a couple commands, done.

## What you need
- Python 3.9+ (3.11 recommended)
- An X API v2 Bearer Token (paste it in `.env` or pass via flag)

## Setup (Windows PowerShell)
```
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Now put your token in `.env` like this (no quotes):
```
TWITTER_BEARER_TOKEN=your_super_secret_token_here
```
Don’t commit your token. It’s already ignored by `.gitignore`.

## Run it
- Search query (prints a quick summary):
```
python -m twitter_bot.main --query "python lang:en -is:retweet" --limit 50 --output console
```

- User timeline (saves a CSV):
```
python -m twitter_bot.main --user jack --limit 100 --output csv --csv-path .\x_jack_sentiment.csv
```

Tip: If you don’t want to use `.env`, just add `--bearer-token <YOUR_TOKEN>` to the command.

## What you get
- Console shows: total tweets, average sentiment score, counts of positive/neutral/negative, plus a few most negative/positive links.
- CSV contains: tweet id, time, author, text, URL, and sentiment scores (pos/neu/neg/compound + label).

## Pro tips
- English-only? Add `lang:en` to your query. No retweets? Add `-is:retweet`.
- Big limits can hit rate limits. Start small (like `--limit 25`).
- VADER is great for short social text. Want fancier? We can plug in a transformer later.

## Troubleshooting
- 401 Unauthorized: your token is missing/invalid. Update `.env` or pass `--bearer-token`.
- Rate limit: you’ll see a pause message—try a smaller limit or wait a bit.
- Import errors: run `pip install -r requirements.txt` again in your active venv.

Have ideas? Want charts or a live dashboard? We can add a tiny Streamlit page to make it look ✨ legit ✨.

