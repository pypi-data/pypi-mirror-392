import datetime as dt
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urlparse

import requests

TIMEOUT_CONNECT_DEFAULT = 6
TIMEOUT_READ_DEFAULT = 60


def fetch_issues(api_url: str) -> list[dict[str, Any]]:
    logging.info("Fetching issues from %s", urlparse(api_url).hostname)
    issues: list[dict[str, Any]] = []
    next_url = api_url
    while next_url:
        logging.debug("Getting %s", next_url)
        resp = requests.get(
            next_url, timeout=(TIMEOUT_CONNECT_DEFAULT, TIMEOUT_READ_DEFAULT)
        )
        if resp.status_code == 403:
            return issues  # Rate limit exceeded
        issues.extend(resp.json())
        next_url = resp.links.get("next", {}).get("url")
    return issues


def fetch_pull_request(issue: dict[str, Any]) -> None:
    if issue.get("pull_request") is None:
        issue["files"] = []
        return
    files_url = issue["url"].replace("/issues/", "/pulls/") + "/files/"
    logging.debug("Getting %s", files_url)
    resp = requests.get(
        files_url, timeout=(TIMEOUT_CONNECT_DEFAULT, TIMEOUT_READ_DEFAULT)
    )
    if resp.status_code == 403:
        return  # Rate limit exceeded
    issue["files"] = [
        file["filename"] for file in resp.json() if file["filename"].endswith(".po")
    ]


def fetch_pull_requests(issues: list[dict[str, Any]]) -> None:
    with ThreadPoolExecutor() as pool:
        pool.map(fetch_pull_request, issues)


def get_issue_reservations(api_url: str) -> dict[str, tuple[str, dt.date]]:
    """Give all files found in issues titles and PRs."""
    issues = fetch_issues(api_url)
    fetch_pull_requests(issues)
    logging.debug("Found %s issues", len(issues))
    reservations = {}
    for issue in issues:
        files_from_title = re.findall(r"[^ ]+\.po", issue["title"])
        files_from_pr = issue["files"]
        files = files_from_title + files_from_pr
        creation_date = dt.datetime.fromisoformat(issue["created_at"]).date()
        reservations.update(
            {file: (issue["html_url"], creation_date) for file in files}
        )
    logging.debug("Found %s reservations", len(reservations))
    return reservations
