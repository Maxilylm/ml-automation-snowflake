#!/usr/bin/env python3
"""Post structured findings as a single inline-comment PR review on GitHub.

Reads findings.json (output of claude_review.py) and submits them as a batched
review via the GitHub Pulls Reviews API. Batching avoids spamming N separate
comments — one review with N inline comments, much cleaner.

Required env:
    GITHUB_TOKEN   (auth)
    GITHUB_REPOSITORY  (owner/repo)
    PR_NUMBER

Usage (CI):
    python scripts/post_findings.py --findings findings.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import request, error


def gh_api(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    url = f"https://api.github.com/repos/{repo}{path}"
    req = request.Request(
        url, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode() if body else None,
    )
    try:
        with request.urlopen(req) as r:
            return json.loads(r.read().decode() or "{}")
    except error.HTTPError as e:
        sys.stderr.write(f"GH {method} {path} -> {e.code}\n{e.read().decode()}\n")
        raise


def severity_emoji(sev: str) -> str:
    return {
        "CRITICAL": "🔴",
        "SECURITY": "🛡️",
        "BREAKING": "💥",
        "BUG": "🐞",
        "CORRECTNESS": "⚠️",
    }.get(sev, "•")


def format_comment(f: dict) -> str:
    lines = [
        f"**{severity_emoji(f['severity'])} {f['severity']}** · `{f['category']}`",
        "",
        f["message"],
    ]
    if f.get("suggested_fix"):
        lines += ["", "**Suggested fix:**", "```", f["suggested_fix"], "```"]
    if f.get("detected_pattern"):
        lines += ["", f"<sub>rule: `{f['detected_pattern']}`</sub>"]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--findings", required=True)
    args = p.parse_args()

    pr = os.environ["PR_NUMBER"]
    findings = json.loads(Path(args.findings).read_text())
    new_findings = [f for f in findings if f.get("is_new", True)]

    if not new_findings:
        print("no new findings; skipping comment post")
        return 0

    comments = [
        {"path": f["file"], "line": f["line"], "side": "RIGHT", "body": format_comment(f)}
        for f in new_findings
    ]

    body = (
        f"### Claude review\n\n"
        f"{len(new_findings)} new finding(s). "
        f"See inline comments. Severity criteria: see `CLAUDE.md`."
    )
    review = gh_api("POST", f"/pulls/{pr}/reviews", {
        "event": "COMMENT", "body": body, "comments": comments,
    })
    print(f"posted review {review.get('id')} with {len(comments)} comment(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
