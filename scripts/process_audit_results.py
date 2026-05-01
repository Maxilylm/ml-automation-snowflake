#!/usr/bin/env python3
"""Poll an Anthropic Batch result and file GitHub issues for tech-debt findings.

Invoked by audit-poll.yml for each pending audit-batch-* artifact.

Steps:
  1. GET /v1/messages/batches/<id> — check processing_status.
     If not "ended", exit 0 without writing the marker (poller retries later).
  2. Fetch results_url (JSONL).
  3. Parse the single result; extract tool_use findings array.
  4. For each finding (severity != STYLE → STYLE is excluded from the schema, but
     handled defensively): deduplicate against open GH issues, then file an issue.
  5. File ONE summary tracker issue.
  6. Write audit-complete-<batch_id>.marker in cwd (signals the poller that we're done).

Usage (CI — invoked by audit-poll.yml):
    python scripts/process_audit_results.py --batch-id <id> --repo owner/repo

Required env vars:
    ANTHROPIC_API_KEY    — Anthropic API key
    GH_TOKEN             — GitHub token (secrets.GITHUB_TOKEN in CI)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, parse, request

ANTHROPIC_API_VERSION = "2023-06-01"
BATCHES_BASE = "https://api.anthropic.com/v1/messages/batches"
GH_API_BASE = "https://api.github.com"

# Severities that warrant a GitHub issue (STYLE is not in the schema, but guard anyway)
ISSUE_SEVERITIES = {"CRITICAL", "SECURITY", "BREAKING", "BUG", "TECH_DEBT"}


# ── Env helpers ───────────────────────────────────────────────────────────────

def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: required environment variable {name!r} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _anthropic_headers(api_key: str) -> dict[str, str]:
    return {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type": "application/json",
    }


def _gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _http_get(url: str, headers: dict[str, str]) -> bytes:
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req) as resp:
            return resp.read()
    except error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        raise RuntimeError(f"Anthropic API GET {url} failed with HTTP {exc.code}: {body_text}") from exc


def _gh_post(url: str, token: str, payload: dict) -> dict:
    """POST to the GH API; handle primary (403) and secondary (429) rate limits once."""
    body = json.dumps(payload).encode()
    req = request.Request(url, data=body, headers=_gh_headers(token), method="POST")
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read())
    except error.HTTPError as exc:
        if exc.code == 403:
            remaining = exc.headers.get("X-RateLimit-Remaining", "1")
            reset_ts = exc.headers.get("X-RateLimit-Reset")
            if (int(remaining.strip()) if remaining else 0) == 0 and reset_ts:
                wait = max(0, int(reset_ts) - int(time.time())) + 2
                print(f"GH primary rate limit hit; sleeping {wait}s …")
                time.sleep(wait)
                # Retry once
                with request.urlopen(
                    request.Request(url, data=body, headers=_gh_headers(token), method="POST")
                ) as resp:
                    return json.loads(resp.read())
        elif exc.code == 429:
            retry_after = exc.headers.get("Retry-After", "60")
            wait = int(retry_after.strip()) if retry_after else 60
            print(f"GH secondary rate limit (429); sleeping {wait}s …")
            time.sleep(wait)
            # Retry once
            with request.urlopen(
                request.Request(url, data=body, headers=_gh_headers(token), method="POST")
            ) as resp:
                return json.loads(resp.read())
        body_text = exc.read().decode(errors="replace")
        raise RuntimeError(f"GH API POST {url} failed with HTTP {exc.code}: {body_text}") from exc


def _gh_search_issues(token: str, repo: str, query: str) -> list[dict]:
    """Search GH issues with `query`. Returns the items list."""
    full_query = f"repo:{repo} {query}"
    encoded = parse.urlencode({"q": full_query, "per_page": "5"})
    url = f"{GH_API_BASE}/search/issues?{encoded}"
    req = request.Request(url, headers=_gh_headers(token), method="GET")
    try:
        with request.urlopen(req) as resp:
            data = json.loads(resp.read())
        return data.get("items", [])
    except error.HTTPError as exc:
        if exc.code == 403:
            remaining = exc.headers.get("X-RateLimit-Remaining", "1")
            reset_ts = exc.headers.get("X-RateLimit-Reset")
            if (int(remaining.strip()) if remaining else 0) == 0 and reset_ts:
                wait = max(0, int(reset_ts) - int(time.time())) + 2
                print(f"GH primary rate limit hit; sleeping {wait}s …")
                time.sleep(wait)
                with request.urlopen(
                    request.Request(url, headers=_gh_headers(token), method="GET")
                ) as resp:
                    data = json.loads(resp.read())
                return data.get("items", [])
        elif exc.code == 429:
            retry_after = exc.headers.get("Retry-After", "60")
            wait = int(retry_after.strip()) if retry_after else 60
            print(f"GH secondary rate limit (429); sleeping {wait}s …")
            time.sleep(wait)
            with request.urlopen(
                request.Request(url, headers=_gh_headers(token), method="GET")
            ) as resp:
                data = json.loads(resp.read())
            return data.get("items", [])
        print(f"WARNING: GH search failed (HTTP {exc.code}); assuming no duplicate.", file=sys.stderr)
        return []


# ── Anthropic Batch API ────────────────────────────────────────────────────────

def get_batch_status(batch_id: str, api_key: str) -> dict:
    url = f"{BATCHES_BASE}/{batch_id}"
    data = _http_get(url, _anthropic_headers(api_key))
    return json.loads(data)


def fetch_results(results_url: str, api_key: str) -> list[dict]:
    """Fetch the JSONL results file and parse into a list of result objects."""
    data = _http_get(results_url, _anthropic_headers(api_key))
    lines = [l for l in data.decode().splitlines() if l.strip()]
    return [json.loads(l) for l in lines]


def extract_findings(results: list[dict]) -> list[dict]:
    """Extract the `findings` array from the first tool_use block in results.

    Raises RuntimeError if every result was non-succeeded (indicating a batch
    failure rather than a legitimately empty codebase).
    """
    failed: list[str] = []
    for result in results:
        result_obj = result.get("result", {})
        if result_obj.get("type") != "succeeded":
            error_type = result_obj.get("type", "unknown")
            print(f"WARNING: result type is not 'succeeded': {error_type}", file=sys.stderr)
            failed.append(error_type)
            continue
        message = result_obj.get("message", {})
        for block in message.get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "report_findings":
                findings = block.get("input", {}).get("findings", [])
                return findings
    if failed:
        raise RuntimeError(
            f"All batch results were non-succeeded; will not write marker. "
            f"Failed result types: {failed}"
        )
    return []


# ── GitHub issue creation ──────────────────────────────────────────────────────

def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def _ensure_labels(token: str, repo: str, labels: list[str]) -> None:
    """Best-effort: create missing labels (GH returns 422 if they exist — ignore)."""
    url = f"{GH_API_BASE}/repos/{repo}/labels"
    for label in labels:
        # Assign a neutral color per label family
        if label.startswith("severity:"):
            color = "d93f0b"
        elif label.startswith("category:"):
            color = "0075ca"
        elif label == "auto-fixable":
            color = "0e8a16"
        elif label == "tracker":
            color = "e4e669"
        else:
            color = "cccccc"
        try:
            _gh_post(url, token, {"name": label, "color": color})
        except (RuntimeError, error.HTTPError) as exc:
            # Non-fatal: label may already exist (GH returns 422) or permissions
            # are insufficient. Log so CI operators can see the failure.
            print(f"::warning::Could not create label {label!r}: {exc}", file=sys.stderr)


def file_finding_issue(
    token: str,
    repo: str,
    finding: dict,
    run_url: str,
) -> int | None:
    """Create a GH issue for a finding. Returns the issue number or None on skip/error."""
    severity = finding.get("severity", "")
    if severity not in ISSUE_SEVERITIES:
        return None

    file_path = finding.get("file", "")
    if not file_path or not file_path.strip():
        return None

    line = finding.get("line")
    file_ref = f"{file_path}:{line}" if line else file_path
    # Strip quotes so the dedup search query parser doesn't break if the model
    # emits a file path containing double-quote characters.
    file_ref = file_ref.replace('"', "")
    message = finding.get("message", "")
    category = finding.get("category", "other")
    effort = finding.get("effort_estimate")
    auto_fixable = finding.get("auto_fixable", False)
    suggested_fix = finding.get("suggested_fix")
    code_snippet = finding.get("code_snippet")

    # Deduplication: search for existing open issues that mention this file:line
    dedup_query = f'is:open is:issue label:weekly-audit "{file_ref}" in:body'
    existing = _gh_search_issues(token, repo, dedup_query)
    if existing:
        print(f"  SKIP (duplicate): {file_ref} — #{existing[0]['number']} already open")
        return None

    title = f"[weekly-audit] {severity} · {category}: {_truncate(message, 80)}"

    body_lines = [
        f"**Severity:** `{severity}`",
        f"**Category:** `{category}`",
        f"**File:** `{file_path}`" + (f" line {line}" if line else ""),
    ]
    if effort:
        body_lines.append(f"**Effort estimate:** `{effort}`")
    body_lines.append(f"**Auto-fixable:** {'yes' if auto_fixable else 'no'}")
    body_lines.append("")
    body_lines.append("### Finding")
    body_lines.append(message)
    if code_snippet:
        body_lines.append("")
        body_lines.append("### Offending code")
        body_lines.append(f"```\n{code_snippet}\n```")
    if suggested_fix:
        body_lines.append("")
        body_lines.append("### Suggested fix")
        body_lines.append(suggested_fix)
    body_lines.append("")
    body_lines.append(f"---")
    body_lines.append(f"_Filed by the [weekly-audit pipeline]({run_url})._")

    issue_labels = [
        "weekly-audit",
        "tech-debt",
        f"severity:{severity.lower()}",
        f"category:{category}",
    ]
    if auto_fixable:
        issue_labels.append("auto-fixable")

    _ensure_labels(token, repo, issue_labels)

    try:
        result = _gh_post(
            f"{GH_API_BASE}/repos/{repo}/issues",
            token,
            {
                "title": title,
                "body": "\n".join(body_lines),
                "labels": issue_labels,
            },
        )
        issue_number: int = result["number"]
        print(f"  FILED: #{issue_number} — {title[:70]}")
        return issue_number
    except RuntimeError as exc:
        print(f"  ERROR filing issue for {file_ref}: {exc}", file=sys.stderr)
        return None


def file_summary_issue(
    token: str,
    repo: str,
    batch_id: str,
    findings: list[dict],
    filed_issue_numbers: list[int],
    skipped_findings: list[dict],
    run_url: str,
) -> int | None:
    """Create the summary tracker issue for this audit run."""
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    n_total = len(findings)
    title = f"[weekly-audit] {today} summary: {n_total} finding(s)"

    body_lines = [
        f"## Weekly audit summary — {today}",
        f"",
        f"**Batch ID:** `{batch_id}`",
        f"**Total findings:** {n_total}",
        f"**Issues filed:** {len(filed_issue_numbers)}",
        f"**Skipped (duplicate or style):** {len(skipped_findings)}",
        "",
    ]

    if filed_issue_numbers:
        body_lines.append("### Filed issues")
        for num in filed_issue_numbers:
            body_lines.append(f"- #{num}")
        body_lines.append("")

    if skipped_findings:
        body_lines.append("### Findings not filed (deduplication / style filter)")
        for f in skipped_findings:
            file_ref = f"{f.get('file', '')}:{f.get('line')}" if f.get("line") else f.get("file", "")
            body_lines.append(
                f"- `{f.get('severity')}` `{f.get('category')}` — {file_ref}: "
                + _truncate(f.get("message", ""), 80)
            )
        body_lines.append("")

    body_lines.append(f"---")
    body_lines.append(f"_Generated by the [weekly-audit pipeline]({run_url})._")

    summary_labels = ["weekly-audit", "tracker"]
    _ensure_labels(token, repo, summary_labels)

    try:
        result = _gh_post(
            f"{GH_API_BASE}/repos/{repo}/issues",
            token,
            {
                "title": title,
                "body": "\n".join(body_lines),
                "labels": summary_labels,
            },
        )
        issue_number: int = result["number"]
        print(f"  SUMMARY: #{issue_number} — {title}")
        return issue_number
    except RuntimeError as exc:
        print(f"  ERROR filing summary issue: {exc}", file=sys.stderr)
        return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-id", required=True, help="Anthropic batch ID")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/repo format")
    args = parser.parse_args()

    batch_id: str = args.batch_id
    repo: str = args.repo

    api_key = require_env("ANTHROPIC_API_KEY")
    gh_token = require_env("GH_TOKEN")

    # Build a run URL for back-links in issues (best-effort; may be empty in local runs)
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = (
        f"https://github.com/{repo}/actions/runs/{run_id}"
        if run_id
        else f"https://github.com/{repo}/actions"
    )

    # ── Step 1: check batch status ─────────────────────────────────────────────
    print(f"checking batch status for {batch_id} …")
    batch_info = get_batch_status(batch_id, api_key)
    processing_status = batch_info.get("processing_status", "")
    print(f"  processing_status: {processing_status}")

    if processing_status != "ended":
        # Batch not ready yet — exit 0 so the poller doesn't mark this as an error.
        # The marker file is NOT written; poller will retry on next schedule.
        print("Batch not yet ended — will retry on next scheduled poll.")
        sys.exit(0)

    # ── Step 2: fetch results ──────────────────────────────────────────────────
    results_url = batch_info.get("results_url")
    if not results_url:
        print("ERROR: batch ended but no results_url present.", file=sys.stderr)
        sys.exit(1)

    print(f"fetching results from {results_url} …")
    results = fetch_results(results_url, api_key)
    print(f"  {len(results)} result line(s) in JSONL")

    # ── Step 3: extract findings ───────────────────────────────────────────────
    try:
        findings = extract_findings(results)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(findings)} finding(s) extracted")

    if not findings:
        print("No findings — writing marker and exiting.")
        Path(f"audit-complete-{batch_id}.marker").write_text("")
        sys.exit(0)

    # ── Step 4: file individual issues ────────────────────────────────────────
    filed_issue_numbers: list[int] = []
    skipped_findings: list[dict] = []

    for finding in findings:
        severity = finding.get("severity", "")
        if severity not in ISSUE_SEVERITIES:
            print(f"  SKIP (non-reportable severity {severity!r})")
            skipped_findings.append(finding)
            continue

        issue_number = file_finding_issue(
            token=gh_token,
            repo=repo,
            finding=finding,
            run_url=run_url,
        )
        if issue_number is not None:
            filed_issue_numbers.append(issue_number)
        else:
            skipped_findings.append(finding)

    print(
        f"filed {len(filed_issue_numbers)} issue(s); "
        f"skipped {len(skipped_findings)} finding(s)"
    )

    # ── Step 5: file summary tracker issue ────────────────────────────────────
    file_summary_issue(
        token=gh_token,
        repo=repo,
        batch_id=batch_id,
        findings=findings,
        filed_issue_numbers=filed_issue_numbers,
        skipped_findings=skipped_findings,
        run_url=run_url,
    )

    # ── Step 6: write completion marker ───────────────────────────────────────
    # This MUST happen only when processing_status == "ended" (guaranteed by
    # the early-exit above).  The poller reads this file's existence to decide
    # whether to upload the idempotency artifact.
    marker_content = "\n".join(str(n) for n in filed_issue_numbers)
    Path(f"audit-complete-{batch_id}.marker").write_text(marker_content)
    print(f"marker written: audit-complete-{batch_id}.marker")


if __name__ == "__main__":
    main()
