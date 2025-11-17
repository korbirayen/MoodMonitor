from __future__ import annotations

from typing import Dict

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


_analyzer = SentimentIntensityAnalyzer()


def score_text(text: str) -> Dict[str, float | str]:
    scores = _analyzer.polarity_scores(text or "")
    compound = scores.get("compound", 0.0)
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {
        "compound": compound,
        "pos": scores.get("pos", 0.0),
        "neu": scores.get("neu", 0.0),
        "neg": scores.get("neg", 0.0),
        "label": label,
    }
