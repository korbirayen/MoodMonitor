from __future__ import annotations

import argparse
from typing import Dict, List, Tuple

# Support running both as a module (python -m reddit_bot.main)
# and as a script (python reddit_bot/main.py)
try:  # relative imports when executed as a module
    from .reddit_client import make_client, fetch_posts, fetch_comments
    from .sentiment import score_text
    from .utils import to_utc_iso, write_csv
except ImportError:  # absolute imports when executed as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from reddit_bot.reddit_client import make_client, fetch_posts, fetch_comments
    from reddit_bot.sentiment import score_text
    from reddit_bot.utils import to_utc_iso, write_csv


def analyze_posts(subreddit: str, limit: int, sort: str) -> Tuple[List[Dict], Dict]:
    client = make_client()
    items = []
    pos = neu = neg = 0
    total_compound = 0.0

    for s in fetch_posts(client, subreddit, limit=limit, sort=sort):
        title = s.title or ""
        text = f"{title}\n\n{s.selftext or ''}".strip()
        scores = score_text(text)
        label = scores["label"]
        total_compound += float(scores["compound"])  # type: ignore[arg-type]
        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1
        items.append(
            {
                "type": "submission",
                "id": s.id,
                "created_utc": to_utc_iso(getattr(s, "created_utc", None)),
                "author": getattr(getattr(s, "author", None), "name", None) or "",
                "subreddit": subreddit,
                "title": title,
                "text": s.selftext or "",
                "permalink": f"https://reddit.com{s.permalink}",
                "compound": scores["compound"],
                "pos": scores["pos"],
                "neu": scores["neu"],
                "neg": scores["neg"],
                "label": label,
            }
        )

    n = len(items) or 1
    summary = {
        "count": len(items),
        "avg_compound": round(total_compound / n, 4),
        "positive": pos,
        "neutral": neu,
        "negative": neg,
    }
    return items, summary


def analyze_comments(subreddit: str, limit: int) -> Tuple[List[Dict], Dict]:
    client = make_client()
    items = []
    pos = neu = neg = 0
    total_compound = 0.0

    for c in fetch_comments(client, subreddit, limit=limit):
        body = c.body or ""
        scores = score_text(body)
        label = scores["label"]
        total_compound += float(scores["compound"])  # type: ignore[arg-type]
        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1
        items.append(
            {
                "type": "comment",
                "id": c.id,
                "created_utc": to_utc_iso(getattr(c, "created_utc", None)),
                "author": getattr(getattr(c, "author", None), "name", None) or "",
                "subreddit": subreddit,
                "title": "",
                "text": body,
                "permalink": f"https://reddit.com{c.permalink}",
                "compound": scores["compound"],
                "pos": scores["pos"],
                "neu": scores["neu"],
                "neg": scores["neg"],
                "label": label,
            }
        )

    n = len(items) or 1
    summary = {
        "count": len(items),
        "avg_compound": round(total_compound / n, 4),
        "positive": pos,
        "neutral": neu,
        "negative": neg,
    }
    return items, summary


def print_summary(summary: Dict) -> None:
    print("--- Sentiment Summary ---")
    print(f"Items:        {summary['count']}")
    print(f"Avg compound: {summary['avg_compound']}")
    print(f"Positive:     {summary['positive']}")
    print(f"Neutral:      {summary['neutral']}")
    print(f"Negative:     {summary['negative']}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simple Reddit sentiment analysis bot")
    p.add_argument("--subreddit", required=True, help="Subreddit name (without r/)")
    p.add_argument("--limit", type=int, default=50, help="Number of items to analyze")
    p.add_argument(
        "--target",
        choices=["posts", "comments"],
        default="posts",
        help="Analyze subreddit posts or comments",
    )
    p.add_argument(
        "--sort",
        choices=["hot", "new", "top"],
        default="hot",
        help="Post sorting method (for target=posts)",
    )
    p.add_argument(
        "--output",
        choices=["console", "csv"],
        default="console",
        help="Where to write results",
    )
    p.add_argument(
        "--csv-path",
        default="reddit_sentiment_report.csv",
        help="Output CSV path if --output=csv",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.target == "posts":
        rows, summary = analyze_posts(args.subreddit, args.limit, args.sort)
    else:
        rows, summary = analyze_comments(args.subreddit, args.limit)

    if args.output == "console":
        print_summary(summary)
        # Show a few extremes for quick feel
        if rows:
            worst = sorted(rows, key=lambda r: r["compound"])[:3]
            best = sorted(rows, key=lambda r: r["compound"], reverse=True)[:3]
            print("\nMost Negative:")
            for r in worst:
                print(f"  {r['label']:>8} {r['compound']:>6} - {r['permalink']}")
            print("\nMost Positive:")
            for r in best:
                print(f"  {r['label']:>8} {r['compound']:>6} - {r['permalink']}")
    else:
        write_csv(args.csv_path, rows)
        print_summary(summary)
        print(f"\nCSV written to: {args.csv_path}")


if __name__ == "__main__":
    main()
