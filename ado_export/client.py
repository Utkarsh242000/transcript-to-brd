"""Azure DevOps REST API client."""

import re
import time
from typing import Any
from urllib.parse import urlparse, unquote

import requests
from requests.auth import HTTPBasicAuth

API_WIQL = "7.1-preview.2"
API_WORKITEMS = "7.1-preview.3"
API_COMMENTS = "7.1-preview.4"
API_REVISIONS = "7.1-preview.3"

BATCH_SIZE = 200
SLEEP = 0.1


def parse_query_url(url: str) -> tuple[str, str, str]:
    """Parse an Azure DevOps query URL into (org, project, query_id).

    Accepted formats
    ----------------
    https://dev.azure.com/{org}/{project}/_queries/query/{query_id}/
    """
    pattern = (
        r"https://dev\.azure\.com/"
        r"(?P<org>[^/]+)/"
        r"(?P<project>[^/]+)/"
        r"_queries/query/"
        r"(?P<query_id>[0-9a-fA-F-]+)"
    )
    m = re.search(pattern, url)
    if not m:
        raise ValueError(
            "Could not parse Azure DevOps query URL. "
            "Expected format: https://dev.azure.com/{org}/{project}/_queries/query/{query_id}/"
        )
    org = unquote(m.group("org"))
    project = unquote(m.group("project"))
    query_id = m.group("query_id")
    return org, project, query_id


class AzureDevOpsClient:
    """Thin wrapper around the Azure DevOps REST API."""

    def __init__(self, org: str, project: str, pat: str) -> None:
        self.base = f"https://dev.azure.com/{org}/{project}"
        self._auth = HTTPBasicAuth("", pat)
        self._session = requests.Session()
        self._session.auth = self._auth
        self._session.headers.update({"Content-Type": "application/json"})

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get(self, url: str) -> Any:
        resp = self._session.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def run_query(self, query_id: str) -> list[int]:
        """Run a saved WIQL query and return the list of work item IDs."""
        url = f"{self.base}/_apis/wit/wiql/{query_id}?api-version={API_WIQL}"
        data = self._get(url)
        return [wi["id"] for wi in data.get("workItems", [])]

    def get_work_items(self, ids: list[int]) -> list[dict]:
        """Fetch full work item details in batches of BATCH_SIZE."""
        all_items: list[dict] = []
        for i in range(0, len(ids), BATCH_SIZE):
            batch = ids[i : i + BATCH_SIZE]
            ids_str = ",".join(str(x) for x in batch)
            url = (
                f"{self.base}/_apis/wit/workitems"
                f"?ids={ids_str}&$expand=all&api-version={API_WORKITEMS}"
            )
            data = self._get(url)
            all_items.extend(data.get("value", []))
            time.sleep(SLEEP)
        return all_items

    def get_comments(self, work_item_id: int) -> list[dict]:
        """Fetch all comments for a single work item (handles pagination)."""
        comments: list[dict] = []
        url = (
            f"{self.base}/_apis/wit/workItems/{work_item_id}/comments"
            f"?api-version={API_COMMENTS}"
        )
        while url:
            resp = self._session.get(url, timeout=60)
            if resp.status_code == 404:
                break
            resp.raise_for_status()
            data = resp.json()
            comments.extend(data.get("comments", []))
            token = data.get("continuationToken")
            if token:
                url = (
                    f"{self.base}/_apis/wit/workItems/{work_item_id}/comments"
                    f"?continuationToken={token}&api-version={API_COMMENTS}"
                )
            else:
                url = ""
        return comments

    def get_revisions(self, work_item_id: int) -> list[dict]:
        """Fetch all revisions/history for a single work item (handles pagination)."""
        revisions: list[dict] = []
        url = (
            f"{self.base}/_apis/wit/workItems/{work_item_id}/revisions"
            f"?api-version={API_REVISIONS}"
        )
        while url:
            data = self._get(url)
            revisions.extend(data.get("value", []))
            url = data.get("nextLink", "")
        return revisions
