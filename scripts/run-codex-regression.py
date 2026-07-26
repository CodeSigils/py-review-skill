#!/usr/bin/env python3
"""Run isolated, structured Codex regressions for the py-review skill."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/codex/cases.json"
SCHEMA = ROOT / "evals/codex/review-result.schema.json"
GRADER = ROOT / "scripts/grade-codex-regression.py"
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens")


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))


def run_checked(command: list[str], cwd: Path) -> None:
    """Run fixture setup commands and preserve actionable failure details."""
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")


def prepare_fixture(root: Path, case_id: str) -> None:
    """Create one isolated git repository for a behavioral case."""
    if root.exists():
        raise FileExistsError(f"fixture already exists: {root}")
    (root / ".agents/skills").mkdir(parents=True)
    shutil.copytree(ROOT / "skills", root / ".agents/skills", dirs_exist_ok=True)
    (root / "src").mkdir()
    (root / "scripts").mkdir()
    files = {
        ".gitignore": "__pycache__/\n*.pyc\n",
        "pyproject.toml": (
            "[project]\n"
            'name = "py-review-regression-fixture"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.10"\n'
        ),
        "src/__init__.py": '"""Regression fixture."""\n',
        "scripts/verify_workspace.py": (
            '"""Verify that a normal developer checkout is writable."""\n\n'
            "from pathlib import Path\n\n"
            'probe = Path(".verification-probe")\n'
            'probe.write_text("ok", encoding="utf-8")\n'
            "probe.unlink()\n"
            'print("workspace verification passed")\n'
        ),
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    run_checked(["git", "init", "-b", "main"], root)
    run_checked(["git", "config", "user.name", "Codex Eval"], root)
    run_checked(["git", "config", "user.email", "codex-eval@example.invalid"], root)
    run_checked(["git", "config", "commit.gpgsign", "false"], root)
    run_checked(["git", "add", "."], root)
    run_checked(["git", "commit", "-m", "test: create review fixture"], root)

    if case_id == "untracked-defect":
        (root / "src/reader.py").write_text(
            '"""Read a text file."""\n\n'
            "from pathlib import Path\n\n\n"
            "def read_text(path: Path) -> str:\n"
            '    handle = path.open("r", encoding="utf-8")\n'
            "    return handle.read()\n",
            encoding="utf-8",
        )
    elif case_id == "sandbox-limitation":
        (root / "src/message.py").write_text(
            '"""Format a status message."""\n\n\n'
            "def status_message(name: str) -> str:\n"
            '    return f"{name}: ready"\n',
            encoding="utf-8",
        )
    else:
        raise ValueError(f"unknown case: {case_id}")


def codex_command(
    codex_bin: str, fixture: Path, prompt: str, output: Path, model: str | None
) -> list[str]:
    """Build a controlled, non-interactive Codex invocation."""
    command = [
        codex_bin,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--cd",
        str(fixture),
        "--output-schema",
        str(SCHEMA),
        "--output-last-message",
        str(output),
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    return command


def transcript_usage(path: Path) -> dict[str, int] | None:
    """Extract token usage from a completed JSONL transcript."""
    usage = {field: 0 for field in TOKEN_FIELDS}
    found = False
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_usage = event.get("usage")
        if event.get("type") != "turn.completed" or not isinstance(event_usage, dict):
            continue
        found = True
        for field in TOKEN_FIELDS:
            value = event_usage.get(field)
            if isinstance(value, int):
                usage[field] += value
    return usage if found else None


def execute(
    command: list[str], transcript: Path, stderr_path: Path, timeout: int
) -> tuple[str, str | None, float]:
    """Run Codex while preserving stdout, stderr, status, and duration."""
    started = monotonic()
    with (
        transcript.open("w", encoding="utf-8") as stdout_file,
        stderr_path.open("w", encoding="utf-8") as stderr_file,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                text=True,
                check=False,
                timeout=timeout,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired:
            return "timeout", f"exceeded {timeout} seconds", monotonic() - started
    if result.returncode:
        return "failed", f"Codex exited {result.returncode}", monotonic() - started
    return "completed", None, monotonic() - started


def run_checked_status(fixture: Path) -> str:
    """Return porcelain status for fixture assertions."""
    return subprocess.run(
        ["git", "status", "--short"],
        cwd=fixture,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def run_self_test() -> int:
    """Validate fixtures and command construction without a model call."""
    cases = read_json(CASES)["cases"]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for case in cases:
            fixture = root / case["id"]
            prepare_fixture(fixture, case["id"])
            status = run_checked_status(fixture)
            expected = case["expected"]["reviewed_path"]
            assert status == f"?? {expected}\n"
            command = codex_command(
                "codex", fixture, case["prompt"], root / "result.json", None
            )
            assert "--output-schema" in command
            assert command[-1] == case["prompt"]
        assert isinstance(read_json(SCHEMA), dict)
    print(f"validated runner fixtures for {len(cases)} cases")
    return 0


def run_checked_commit() -> str | None:
    """Return the repository commit when available."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def codex_version(codex_bin: str) -> str | None:
    """Return the CLI version without making it a regression prerequisite."""
    try:
        result = subprocess.run(
            [codex_bin, "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    version = result.stdout.strip() or result.stderr.strip()
    return version if result.returncode == 0 and version else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/codex"))
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture_base = (
        args.fixture_dir.resolve()
        if args.fixture_dir
        else Path(tempfile.mkdtemp(prefix="py-review-codex-"))
    )
    fixture_base.mkdir(parents=True, exist_ok=True)
    cases = read_json(CASES)["cases"]
    summary: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit": run_checked_commit(),
        "codex_binary": args.codex_bin,
        "codex_version": codex_version(args.codex_bin),
        "requested_model": args.model,
        "cases": [],
    }
    for case in cases:
        fixture = fixture_base / case["id"]
        prepare_fixture(fixture, case["id"])
        record: dict[str, Any] = {
            "id": case["id"],
            "prompt": case["prompt"],
            "fixture": str(fixture),
            "status": "prepared",
            "duration_seconds": 0,
            "usage": None,
        }
        if not args.prepare_only:
            transcript = output_dir / f"{case['id']}-transcript.jsonl"
            stderr_path = output_dir / f"{case['id']}-stderr.log"
            result_path = output_dir / f"{case['id']}-result.json"
            command = codex_command(
                args.codex_bin, fixture, case["prompt"], result_path, args.model
            )
            status, error, duration = execute(
                command, transcript, stderr_path, args.timeout
            )
            record.update(
                status=status,
                error=error,
                duration_seconds=round(duration, 3),
                usage=transcript_usage(transcript),
                transcript=str(transcript),
                result=str(result_path),
                stderr=str(stderr_path),
            )
        summary["cases"].append(record)

    summary["ended_at"] = datetime.now(timezone.utc).isoformat()
    summary_path = output_dir / "run-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.prepare_only:
        print(f"prepared {len(cases)} fixtures under {fixture_base}")
        return 0
    if any(case["status"] != "completed" for case in summary["cases"]):
        return 1
    return subprocess.run(
        [
            sys.executable,
            str(GRADER),
            "--results-dir",
            str(output_dir),
            "--output",
            str(output_dir / "grade.json"),
        ],
        cwd=ROOT,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
