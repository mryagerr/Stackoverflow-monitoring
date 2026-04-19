"""Fetches PyPI download statistics via the pypistats.org public API."""

import time
from datetime import date, timedelta

import requests

import config


class PyPIMonitor:
    def __init__(self):
        self.base = config.PYPI_API_BASE
        self.session = requests.Session()

    def _get(self, path: str) -> dict:
        response = self.session.get(f"{self.base}/{path}")
        response.raise_for_status()
        return response.json()

    def overall(self, package: str) -> dict:
        """Total downloads (last 30 days, excluding mirrors)."""
        data = self._get(f"packages/{package}/recent")
        row = data.get("data", {})
        return {
            "package": package,
            "last_day": row.get("last_day", 0),
            "last_week": row.get("last_week", 0),
            "last_month": row.get("last_month", 0),
        }

    def system(self, package: str) -> list[dict]:
        """Downloads broken down by OS."""
        data = self._get(f"packages/{package}/system")
        rows = []
        for item in data.get("data", []):
            rows.append(
                {
                    "package": package,
                    "system": item.get("system", "null"),
                    "downloads": item.get("downloads", 0),
                    "date": item.get("date"),
                }
            )
        return rows

    def python_major(self, package: str) -> list[dict]:
        """Downloads broken down by Python major version."""
        data = self._get(f"packages/{package}/python_major")
        rows = []
        for item in data.get("data", []):
            rows.append(
                {
                    "package": package,
                    "python_major": item.get("python_major", "null"),
                    "downloads": item.get("downloads", 0),
                    "date": item.get("date"),
                }
            )
        return rows

    def bulk_recent(self, packages: list[str] = config.PYPI_PACKAGES) -> list[dict]:
        """Fetch recent download counts for a list of packages."""
        results = []
        for pkg in packages:
            try:
                results.append(self.overall(pkg))
            except requests.HTTPError as e:
                results.append({"package": pkg, "error": str(e)})
            time.sleep(0.3)
        return sorted(results, key=lambda x: x.get("last_month", 0), reverse=True)
