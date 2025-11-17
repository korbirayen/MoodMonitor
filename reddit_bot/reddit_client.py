from __future__ import annotations

import os
from typing import Iterable, Literal

from dotenv import load_dotenv
import praw


SortType = Literal["hot", "new", "top"]


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}.\n"
            "Create a Reddit 'script' app at https://www.reddit.com/prefs/apps,\n"
            "then set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT in a .env file."
        )
    return value


def make_client() -> praw.Reddit:
    # Load from .env located at project root
    load_dotenv()

    client_id = _get_env("REDDIT_CLIENT_ID")
    client_secret = _get_env("REDDIT_CLIENT_SECRET")
    user_agent = _get_env("REDDIT_USER_AGENT")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False,
    )


def fetch_posts(
    client: praw.Reddit,
    subreddit_name: str,
    limit: int = 50,
    sort: SortType = "hot",
) -> Iterable[praw.models.Submission]:
    subreddit = client.subreddit(subreddit_name)
    if sort == "hot":
        return subreddit.hot(limit=limit)
    if sort == "new":
        return subreddit.new(limit=limit)
    if sort == "top":
        return subreddit.top(limit=limit)
    raise ValueError(f"Unsupported sort: {sort}")


def fetch_comments(
    client: praw.Reddit,
    subreddit_name: str,
    limit: int = 50,
) -> Iterable[praw.models.Comment]:
    subreddit = client.subreddit(subreddit_name)
    # Fetch latest comments across the subreddit
    return subreddit.comments(limit=limit)
