from __future__ import annotations

import csv
from datetime import datetime, timezone
from typing import Iterable, Mapping


def to_utc_iso(ts: float | int | None) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except Exception:
        return ""


def write_csv(path: str, rows: Iterable[Mapping[str, object]]) -> None:
    rows = list(rows)
    if not rows:
        # Create an empty file with no headers if nothing to write
        open(path, "w", newline="").close()
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
