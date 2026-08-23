#!/usr/bin/env python3
"""Report pinned GitHub Action SHAs that differ from their major tag head."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

PINNED = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@([0-9a-f]{40})\s+#\s*v(\d+)")


def latest_sha(repo: str, major: str, token: str) -> str:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "py-review-action-freshness"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/git/ref/tags/v{major}", headers=headers
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    target = payload["object"]
    if target["type"] == "commit":
        return target["sha"]
    if target["type"] != "tag":
        raise ValueError(f"unexpected tag object type: {target['type']}")
    tag_request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/git/tags/{target['sha']}", headers=headers
    )
    with urllib.request.urlopen(tag_request, timeout=20) as response:
        tag_payload = json.load(response)
    if tag_payload.get("object", {}).get("type") != "commit":
        raise ValueError("annotated action tag does not resolve directly to a commit")
    return tag_payload["object"]["sha"]


def main() -> int:
    token = os.environ.get("GH_TOKEN", "")
    rows: list[str] = []
    for path in sorted(Path(".github").rglob("*.yml")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = PINNED.search(line)
            if not match:
                continue
            repo, pinned, major = match.groups()
            try:
                latest = latest_sha(repo, major, token)
                state = "current" if pinned == latest else "update available"
            except (OSError, KeyError, urllib.error.HTTPError) as exc:
                state = f"unknown ({exc})"
            rows.append(f"| `{repo}` | `v{major}` | {state} | `{path}:{number}` |")
    report = "## GitHub Action freshness\n\n| Action | Major | Status | Location |\n|---|---:|---|---|\n"
    report += "\n".join(rows) if rows else "No pinned actions found."
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
