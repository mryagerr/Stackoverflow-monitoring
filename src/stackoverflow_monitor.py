"""Fetches tag activity and question volume from the Stack Overflow API."""

import time
from datetime import datetime, timedelta
from typing import Optional

import requests

import config


class StackOverflowMonitor:
    def __init__(self, api_key: str = config.SO_API_KEY):
        self.api_key = api_key
        self.base_url = config.SO_API_BASE
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict) -> dict:
        if self.api_key:
            params["key"] = self.api_key
        params.setdefault("site", "stackoverflow")

        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()

        # Respect backoff hint from API
        if data.get("backoff"):
            time.sleep(data["backoff"])

        return data

    def get_tag_stats(self, tags: list[str]) -> list[dict]:
        """Return question count and metadata for each tag."""
        tag_str = ";".join(tags)
        data = self._get("tags", {"inname": tag_str, "pagesize": config.SO_PAGE_SIZE, "order": "desc", "sort": "popular"})
        return [
            {
                "tag": item["name"],
                "question_count": item["count"],
                "has_synonyms": item.get("has_synonyms", False),
                "is_moderator_only": item.get("is_moderator_only", False),
            }
            for item in data.get("items", [])
        ]

    def get_tag_activity(self, tag: str, lookback_days: int = config.LOOKBACK_DAYS) -> dict:
        """Return recent question volume for a tag over the lookback window."""
        since = int((datetime.utcnow() - timedelta(days=lookback_days)).timestamp())
        data = self._get(
            "questions",
            {
                "tagged": tag,
                "fromdate": since,
                "pagesize": 1,
                "filter": "total",
            },
        )
        return {
            "tag": tag,
            "questions_last_n_days": data.get("total", 0),
            "lookback_days": lookback_days,
        }

    def get_multiple_tag_activity(self, tags: list[str], lookback_days: int = config.LOOKBACK_DAYS) -> list[dict]:
        results = []
        for tag in tags:
            results.append(self.get_tag_activity(tag, lookback_days))
            time.sleep(0.2)  # polite rate limiting
        return results

    def get_tag_velocity(self, tags: list[str], lookback_days: int = config.LOOKBACK_DAYS) -> list[dict]:
        """Combine total count with recent activity to produce a velocity score."""
        stats = {s["tag"]: s for s in self.get_tag_stats(tags)}
        activity = {a["tag"]: a for a in self.get_multiple_tag_activity(tags, lookback_days)}

        results = []
        for tag in tags:
            total = stats.get(tag, {}).get("question_count", 0)
            recent = activity.get(tag, {}).get("questions_last_n_days", 0)
            daily_rate = recent / lookback_days if lookback_days else 0
            results.append(
                {
                    "tag": tag,
                    "total_questions": total,
                    f"questions_last_{lookback_days}d": recent,
                    "daily_rate": round(daily_rate, 2),
                }
            )
        return sorted(results, key=lambda x: x["daily_rate"], reverse=True)
