"""Scrapes the dbt Hub public registry for package metadata and growth signals."""

import requests

import config


class DbtHubMonitor:
    def __init__(self):
        self.base = config.DBT_HUB_API
        self.session = requests.Session()

    def _get(self, path: str) -> dict:
        response = self.session.get(f"{self.base}/{path}")
        response.raise_for_status()
        return response.json()

    def list_packages(self) -> list[dict]:
        """Return all packages in the dbt Hub registry with metadata."""
        data = self._get("packages")
        packages = data if isinstance(data, list) else data.get("packages", [])
        return [
            {
                "name": pkg.get("name"),
                "namespace": pkg.get("namespace"),
                "latest_version": pkg.get("latest_version"),
                "versions": len(pkg.get("versions", [])),
                "downloads": pkg.get("downloads", 0),
            }
            for pkg in packages
        ]

    def get_package(self, namespace: str, name: str) -> dict:
        """Fetch detail for a single package."""
        return self._get(f"packages/{namespace}/{name}")

    def top_packages(self, n: int = 20) -> list[dict]:
        """Return top n packages by download count."""
        pkgs = self.list_packages()
        return sorted(pkgs, key=lambda x: x.get("downloads", 0), reverse=True)[:n]
