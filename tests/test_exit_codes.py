"""Regression tests for maintainer validation exit-code handling."""

from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import exit_codes  # noqa: E402

VERIFY_URLS_SPEC = spec_from_file_location("verify_urls", SCRIPTS / "verify-urls.py")
assert VERIFY_URLS_SPEC is not None and VERIFY_URLS_SPEC.loader is not None
verify_urls = module_from_spec(VERIFY_URLS_SPEC)
sys.modules[VERIFY_URLS_SPEC.name] = verify_urls
VERIFY_URLS_SPEC.loader.exec_module(verify_urls)


class ExitCodeTests(unittest.TestCase):
    def test_missing_required_input_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.txt"
            stderr = StringIO()
            with redirect_stderr(stderr):
                result = exit_codes.run(lambda: (exit_codes.read_text(missing), 0)[1])
        self.assertEqual(result, exit_codes.COULD_NOT_RUN)
        self.assertIn("COULD NOT RUN", stderr.getvalue())

    def test_clean_result_is_preserved(self) -> None:
        self.assertEqual(exit_codes.run(lambda: exit_codes.CLEAN), exit_codes.CLEAN)

    def test_url_checker_exits_2_when_a_monitored_url_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "evidence-urls.json"
            manifest.write_text(
                '{"urls": [{"name": "Example", "url": "https://example.invalid", '
                '"expected_statuses": [200]}]}',
                encoding="utf-8",
            )
            with (
                patch.object(verify_urls, "MANIFEST_PATH", manifest),
                patch.object(
                    verify_urls,
                    "check_url",
                    return_value=verify_urls.UrlCheckResult("ERROR", 0, "unavailable"),
                ),
                patch.object(sys, "argv", ["verify-urls.py"]),
            ):
                self.assertEqual(verify_urls.main(), exit_codes.COULD_NOT_RUN)
