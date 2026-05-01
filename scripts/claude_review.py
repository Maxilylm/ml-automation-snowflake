#!/usr/bin/env python3
"""Headless Claude code review wrapper for CI.

Single-plugin mode: invoked inside one ml-automation-* repo. Reviews the PR diff
against `--base-ref`, calls `claude -p` with structured JSON output, posts
findings via post_findings.py.

Usage (CI):
    python scripts/claude_review.py --base-ref origin/main \\
        --pr-number "$PR_NUMBER" --output findings.json

Usage (local dry-run):
    python scripts/claude_review.py --base-ref main
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "finding.schema.json"
FAIL_SEVERITIES = {"CRITICAL", "SECURITY", "BREAKING"}


def changed_files(base_ref: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", f"{base_ref}...HEAD", "--name-only"],
        capture_output=True, text=True, check=True, cwd=ROOT,
    )
    return [f for f in out.stdout.splitlines() if f.strip()]


def build_review_prompt(files: list[str], prior_findings: list[dict]) -> str:
    file_list = "\n".join(f"- {f}" for f in files)
    prior_block = ""
    if prior_findings:
        prior_block = (
            "\nThe following findings were already reported on previous CI runs of this PR. "
            "Report only NEW or STILL-UNADDRESSED issues. Set `is_new: false` if you re-surface "
            "an existing finding because it has not been addressed:\n\n"
            + json.dumps(prior_findings, indent=2)
        )
    return f"""You are running as the CI code reviewer for this Claude Code plugin in the Blend Spark Harness.

Read CLAUDE.md and the relevant `.claude/rules/` files for severity criteria, few-shot examples, and conventions. You are an INDEPENDENT reviewer — you do not have the conversation context of the author.

Files changed in this PR:
{file_list}

For each file:
1. Read the full current contents (not just the diff — needed for correctness analysis).
2. Apply severity criteria from CLAUDE.md (only BUG / SECURITY / CORRECTNESS / BREAKING / CRITICAL are reportable).
3. Apply the few-shot examples for ambiguous cases.
4. Check `.claude/rules/plugin.md` for plugin-API breaking-change rules (removed agents/skills, manifest schema violations).
5. If the diff exceeds 8 files, do per-file local analysis first, then a separate cross-file integration pass.

Output: a JSON array of findings conforming to schemas/finding.schema.json. No prose. No empty findings. If the diff is clean, return [].

Set `is_new: true` for findings not in the prior list; `is_new: false` if you are re-surfacing an unaddressed prior finding.
{prior_block}
"""


def run_claude(prompt: str) -> list[dict]:
    # `claude --json-schema` expects an inline JSON Schema STRING, not a file
    # path (verified against `claude --help`: "Example: {"type":"object",...}").
    # Read the schema file and pass its contents.
    schema_text = SCHEMA_PATH.read_text()
    cmd = [
        "claude", "-p",
        "--output-format", "json",
        "--json-schema", schema_text,
        prompt,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exited {result.returncode}\nstderr:\n{result.stderr}")
    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"claude returned non-JSON output: {e}\nstdout:\n{result.stdout[:2000]}")
    if not isinstance(findings, list):
        raise RuntimeError(f"Expected JSON array of findings, got {type(findings).__name__}")
    return findings


def load_prior_findings(pr_number: str | None) -> list[dict]:
    if not pr_number:
        return []
    cache_dir = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "claude-review-cache"
    cache_file = cache_dir / f"pr-{pr_number}-prior.json"
    if not cache_file.exists():
        return []
    try:
        return json.loads(cache_file.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-ref", default="main")
    p.add_argument("--pr-number", default=None)
    p.add_argument("--output", default="findings.json")
    args = p.parse_args()

    files = changed_files(args.base_ref)
    if not files:
        print("no changed files; writing empty findings list")
        Path(args.output).write_text("[]\n")
        return 0

    prior = load_prior_findings(args.pr_number)
    prompt = build_review_prompt(files, prior)
    print(f"reviewing {len(files)} file(s); {len(prior)} prior finding(s)")
    findings = run_claude(prompt)
    print(f"{len(findings)} finding(s) returned")

    Path(args.output).write_text(json.dumps(findings, indent=2) + "\n")

    failing = [f for f in findings if f.get("severity") in FAIL_SEVERITIES]
    if failing:
        print(f"{len(failing)} blocking finding(s) — failing build")
        for f in failing:
            print(f"  {f['severity']:10s} {f['file']}:{f['line']}  {f['message'][:80]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
