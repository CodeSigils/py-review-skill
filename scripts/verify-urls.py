#!/usr/bin/env python3
"""Verify reachable HTTP(S) URLs referenced by docs and skills."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https?://[^\s)>]+")


def iter_urls() -> list[tuple[Path, str]]:
    pairs: list[tuple[Path, str]] = []
    for base in (ROOT / "skills", ROOT / "docs", ROOT):
        if base.is_file():
            paths = [base]
        else:
            paths = sorted(base.glob("**/*.md"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for match in URL_RE.finditer(text):
                pairs.append((path, match.group(0).rstrip(".,;")))
    return pairs


def check_url(url: str) -> str | None:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "py-review-skill-url-check"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if 200 <= response.status < 400:
                return None
            return f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            return check_url_get(url)
        return f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - report URL check failure
        return str(exc)


def check_url_get(url: str) -> str | None:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "py-review-skill-url-check"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if 200 <= response.status < 400:
                return None
            return f"HTTP {response.status}"
    except Exception as exc:  # noqa: BLE001 - report URL check failure
        return str(exc)


def main() -> int:
    failures: list[str] = []
    seen: set[str] = set()
    for path, url in iter_urls():
        if url in seen:
            continue
        seen.add(url)
        failure = check_url(url)
        if failure:
            failures.append(f"{path.relative_to(ROOT)}: {url}: {failure}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"verified {len(seen)} URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
