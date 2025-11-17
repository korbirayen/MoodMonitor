from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import os
from dotenv import load_dotenv
import tweepy


def make_client(bearer_token: str | None = None) -> tweepy.Client:
    load_dotenv()
    token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        raise ValueError(
            "Missing Twitter bearer token. Provide via --bearer-token or TWITTER_BEARER_TOKEN in .env"
        )
    return tweepy.Client(bearer_token=token, wait_on_rate_limit=True)


def search_tweets(
    client: tweepy.Client,
    query: str,
    limit: int = 50,
) -> Tuple[List[tweepy.Tweet], Dict[str, str]]:
    tweets: List[tweepy.Tweet] = []
    author_usernames: Dict[str, str] = {}

    paginator = tweepy.Paginator(
        client.search_recent_tweets,
        query=query,
        tweet_fields=["created_at", "lang", "author_id"],
        expansions=["author_id"],
        user_fields=["username"],
        max_results=100,
    )
    for page in paginator:
        if page.includes and "users" in page.includes:
            for u in page.includes["users"]:
                author_usernames[str(u.id)] = u.username
        if page.data:
            for t in page.data:
                tweets.append(t)
                if len(tweets) >= limit:
                    return tweets, author_usernames
        if not page.meta or not page.meta.get("next_token"):
            break
    return tweets, author_usernames


def user_tweets(
    client: tweepy.Client,
    username: str,
    limit: int = 50,
) -> List[tweepy.Tweet]:
    u = client.get_user(username=username)
    if not u.data:
        return []
    user_id = u.data.id
    tweets: List[tweepy.Tweet] = []
    paginator = tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        tweet_fields=["created_at", "lang", "author_id"],
        max_results=100,
    )
    for page in paginator:
        if page.data:
            for t in page.data:
                tweets.append(t)
                if len(tweets) >= limit:
                    return tweets
        if not page.meta or not page.meta.get("next_token"):
            break
    return tweets
