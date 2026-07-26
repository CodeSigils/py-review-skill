#!/usr/bin/env python3
"""Grade py-review Codex regression results deterministically."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals/codex/cases.json"


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))


def contains_any(values: list[str], terms: list[str]) -> bool:
    """Return whether normalized values contain at least one expected term."""
    haystack = " ".join(values).lower()
    return any(term.lower() in haystack for term in terms)


def grade_case(case: dict[str, Any], result: dict[str, Any]) -> list[str]:
    """Grade one structured review result against its case contract."""
    errors: list[str] = []
    case_id = case["id"]
    skills = result.get("skills_used", [])
    if "py-review" not in skills:
        errors.append(f"{case_id}: py-review was not recorded in skills_used")

    expected = case["expected"]
    reviewed_paths = result.get("reviewed_paths", [])
    if expected["reviewed_path"] not in reviewed_paths:
        errors.append(f"{case_id}: did not inspect {expected['reviewed_path']}")

    findings = result.get("findings", [])
    if "finding_path" in expected:
        matching = [
            finding
            for finding in findings
            if isinstance(finding, dict)
            and finding.get("path") == expected["finding_path"]
        ]
        if not matching:
            errors.append(
                f"{case_id}: did not report the seeded finding in "
                f"{expected['finding_path']}"
            )
        else:
            finding_text = [
                f"{finding.get('title', '')} {finding.get('reason', '')}"
                for finding in matching
            ]
            if not contains_any(finding_text, expected["finding_terms"]):
                errors.append(f"{case_id}: finding does not identify resource cleanup")

    if "finding_count" in expected and len(findings) != expected["finding_count"]:
        errors.append(
            f"{case_id}: expected {expected['finding_count']} findings, "
            f"received {len(findings)}"
        )

    if "environment_terms" in expected:
        limitations = result.get("environment_limitations", [])
        if not contains_any(limitations, expected["environment_terms"]):
            errors.append(f"{case_id}: did not record the sandbox limitation")
    return errors


def grade_results(cases_path: Path, results_dir: Path) -> dict[str, Any]:
    """Grade all configured cases and return a machine-readable summary."""
    cases = read_json(cases_path)["cases"]
    case_results: list[dict[str, Any]] = []
    all_errors: list[str] = []
    for case in cases:
        result_path = results_dir / f"{case['id']}-result.json"
        try:
            result = read_json(result_path)
            errors = malformed_result_errors(case, result)
            if not errors:
                errors = grade_case(case, result)
        except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
            errors = [f"{case['id']}: unreadable result: {exc}"]
        case_results.append(
            {"id": case["id"], "passed": not errors, "errors": errors}
        )
        all_errors.extend(errors)
    return {
        "passed": not all_errors,
        "case_count": len(cases),
        "cases": case_results,
    }


def malformed_result_errors(case: dict[str, Any], result: Any) -> list[str]:
    """Return contract errors that should not escape as grader crashes."""
    if not isinstance(result, dict):
        return [f"{case['id']}: result must be a JSON object"]
    required_lists = (
        "skills_used",
        "reviewed_paths",
        "findings",
        "environment_limitations",
    )
    return [
        f"{case['id']}: {field} must be a list"
        for field in required_lists
        if not isinstance(result.get(field), list)
    ]


def run_self_test() -> int:
    """Exercise both passing and failing grading paths."""
    cases = read_json(DEFAULT_CASES)["cases"]
    passing = {
        "untracked-defect": {
            "skills_used": ["py-review", "py-anti-patterns"],
            "reviewed_paths": ["src/reader.py"],
            "findings": [{
                "path": "src/reader.py",
                "line": 7,
                "title": "File handle is not closed",
                "reason": "Use a context manager to release the resource.",
            }],
            "environment_limitations": [],
        },
        "sandbox-limitation": {
            "skills_used": ["py-review"],
            "reviewed_paths": ["src/message.py"],
            "findings": [],
            "environment_limitations": [
                "Verification could not write in the read-only sandbox."
            ],
        },
    }
    with tempfile.TemporaryDirectory() as directory:
        results_dir = Path(directory)
        for case_id, result in passing.items():
            (results_dir / f"{case_id}-result.json").write_text(
                json.dumps(result), encoding="utf-8"
            )
        summary = grade_results(DEFAULT_CASES, results_dir)
        assert summary["passed"] is True
        passing["sandbox-limitation"]["findings"] = [{
            "path": "scripts/verify_workspace.py",
            "line": 7,
            "title": "Permission failure",
            "reason": "The sandbox rejected a write.",
        }]
        (results_dir / "sandbox-limitation-result.json").write_text(
            json.dumps(passing["sandbox-limitation"]), encoding="utf-8"
        )
        summary = grade_results(DEFAULT_CASES, results_dir)
        assert summary["passed"] is False
    print(f"validated grader against {len(cases)} cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if args.results_dir is None:
        parser.error("--results-dir is required unless --self-test is used")
    summary = grade_results(args.cases, args.results_dir)
    rendered = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
