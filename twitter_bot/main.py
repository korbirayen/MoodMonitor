from __future__ import annotations

import argparse
from typing import Dict, List, Tuple

from .twitter_client import make_client, search_tweets, user_tweets

# Reuse the existing sentiment + utils from reddit_bot package
try:
    from reddit_bot.sentiment import score_text
    from reddit_bot.utils import write_csv
except Exception:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from reddit_bot.sentiment import score_text  # type: ignore
    from reddit_bot.utils import write_csv  # type: ignore


def _tweet_to_row(tweet, author_username: str | None = None) -> Dict:
    text = (getattr(tweet, "text", "") or "").replace("\r\n", "\n").strip()
    scores = score_text(text)
    label = scores["label"]
    tid = getattr(tweet, "id", "")
    return {
        "type": "tweet",
        "id": str(tid),
        "created_at": getattr(tweet, "created_at", "") and tweet.created_at.isoformat(),
        "author": author_username or "",
        "text": text,
        "url": f"https://x.com/{author_username}/status/{tid}" if author_username else f"https://x.com/i/web/status/{tid}",
        "compound": scores["compound"],
        "pos": scores["pos"],
        "neu": scores["neu"],
        "neg": scores["neg"],
        "label": label,
    }


def analyze_query(client, query: str, limit: int) -> Tuple[List[Dict], Dict]:
    rows: List[Dict] = []
    pos = neu = neg = 0
    total = 0.0
    tweets, author_usernames = search_tweets(client, query=query, limit=limit)
    for t in tweets:
        uname = author_usernames.get(str(getattr(t, "author_id", "")))
        row = _tweet_to_row(t, uname)
        label = row["label"]
        total += float(row["compound"])  # type: ignore
        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1
        rows.append(row)
    n = len(rows) or 1
    summary = {
        "count": len(rows),
        "avg_compound": round(total / n, 4),
        "positive": pos,
        "neutral": neu,
        "negative": neg,
    }
    return rows, summary


def analyze_user(client, username: str, limit: int) -> Tuple[List[Dict], Dict]:
    rows: List[Dict] = []
    pos = neu = neg = 0
    total = 0.0
    tweets = user_tweets(client, username=username, limit=limit)
    for t in tweets:
        row = _tweet_to_row(t, username)
        label = row["label"]
        total += float(row["compound"])  # type: ignore
        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1
        rows.append(row)
    n = len(rows) or 1
    summary = {
        "count": len(rows),
        "avg_compound": round(total / n, 4),
        "positive": pos,
        "neutral": neu,
        "negative": neg,
    }
    return rows, summary


def print_summary(summary: Dict, label: str) -> None:
    print(f"--- Sentiment Summary ({label}) ---")
    print(f"Items:        {summary['count']}")
    print(f"Avg compound: {summary['avg_compound']}")
    print(f"Positive:     {summary['positive']}")
    print(f"Neutral:      {summary['neutral']}")
    print(f"Negative:     {summary['negative']}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="X/Twitter sentiment analysis using official API")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Search query, e.g. 'python lang:en -is:retweet'")
    group.add_argument("--user", help="Username (without @) to fetch tweets from")
    p.add_argument("--limit", type=int, default=50, help="Number of tweets to analyze")
    p.add_argument("--output", choices=["console", "csv"], default="console")
    p.add_argument("--csv-path", default="x_sentiment_report.csv")
    p.add_argument("--bearer-token", dest="bearer_token", default=None, help="X API v2 Bearer token (optional if TWITTER_BEARER_TOKEN is set)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    client = make_client(args.bearer_token)
    if args.query:
        rows, summary = analyze_query(client, args.query, args.limit)
        label = f"query='{args.query}'"
    else:
        rows, summary = analyze_user(client, args.user, args.limit)
        label = f"user='@{args.user}'"

    if args.output == "console":
        print_summary(summary, label)
        if rows:
            worst = sorted(rows, key=lambda r: r["compound"])[:3]
            best = sorted(rows, key=lambda r: r["compound"], reverse=True)[:3]
            print("\nMost Negative:")
            for r in worst:
                print(f"  {r['label']:>8} {r['compound']:>6} - {r['url']}")
            print("\nMost Positive:")
            for r in best:
                print(f"  {r['label']:>8} {r['compound']:>6} - {r['url']}")
    else:
        write_csv(args.csv_path, rows)
        print_summary(summary, label)
        print(f"\nCSV written to: {args.csv_path}")


if __name__ == "__main__":
    main()
