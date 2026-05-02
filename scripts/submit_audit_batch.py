#!/usr/bin/env python3
"""Submit a weekly tech-debt audit batch to the Anthropic Batches API.

Reads the repo context (file tree, README, AGENTS.md, recently modified files),
renders prompts/weekly-audit.md, and submits a single-request batch.  Writes
the resulting batch ID to audit-batch-id.txt in the current working directory
(picked up by weekly-audit.yml as an artifact).

Usage (CI — invoked by weekly-audit.yml):
    python scripts/submit_audit_batch.py

Required env vars:
    ANTHROPIC_API_KEY    — Anthropic API key
    GITHUB_REPOSITORY   — owner/repo format (e.g., acme/my-plugin)

Optional env vars:
    AUDIT_MODEL          — model to use (default: claude-opus-4-7)

PM3-89 / PM3-96: when ANTHROPIC_API_KEY first lands on a repo, the workflow runs
end-to-end against the live API. Two failure modes were silent until 2026-05-02:
1. The default model id was unverified — bumped to claude-opus-4-7 (system-attested).
2. _run() swallowed subprocess stderr and returned empty strings on non-zero exit,
   so a broken `git log` call would silently emit an empty audit context. _run()
   now raises with stderr surfaced; the workflow fails fast instead of submitting
   malformed prompts to the Batches API.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib import error, request

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "weekly-audit.md"
SCHEMA_PATH = ROOT / "schemas" / "audit-finding.schema.json"

ANTHROPIC_API_VERSION = "2023-06-01"
BATCHES_URL = "https://api.anthropic.com/v1/messages/batches"
DEFAULT_MODEL = "claude-opus-4-7"
# Pattern of valid Anthropic model IDs (defensive sanity check; not a substitute
# for the live /v1/messages call that ultimately validates).
import re as _re
_MODEL_ID_RE = _re.compile(r"^claude-(?:opus|sonnet|haiku)-\d+(?:-\d+){1,2}(?:-\d{8})?$")
MAX_TOKENS = 8192


# ── Env / config ──────────────────────────────────────────────────────────────

def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: required environment variable {name!r} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


# ── Repo context helpers ───────────────────────────────────────────────────────

def _run(cmd: list[str], *, cwd: Path | None = None) -> str:
    """Run a subprocess, returning stdout. Raises RuntimeError on non-zero exit
    with stderr included — fail-fast so the workflow surfaces the failure instead
    of silently submitting a malformed prompt with empty context (PM3-96)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd or ROOT, check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"could not exec {cmd!r}: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(cmd)!r} exited {result.returncode}\n"
            f"stderr:\n{result.stderr.strip()}"
        )
    return result.stdout


def build_repo_context() -> str:
    """Assemble the {{REPO_CONTEXT}} block injected into the audit prompt."""
    parts: list[str] = []

    # File tree (up to 200 entries, excluding .git)
    tree_output = _run(
        ["find", ".", "-type", "f", "-not", "-path", "./.git/*"],
        cwd=ROOT,
    )
    tree_lines = [l for l in tree_output.splitlines() if l.strip()][:200]
    parts.append("## File tree (up to 200 entries)\n\n```\n" + "\n".join(tree_lines) + "\n```")

    # README
    for readme_name in ("README.md", "README.rst", "README.txt", "README"):
        readme_path = ROOT / readme_name
        if readme_path.exists():
            content = readme_path.read_text(errors="replace")
            if len(content) > 4000:
                content = content[:4000] + "\n... [truncated at 4000 chars]"
            parts.append(f"## {readme_name}\n\n{content}")
            break

    # AGENTS.md (full — it's the plugin contract doc)
    agents_path = ROOT / "AGENTS.md"
    if agents_path.exists():
        parts.append("## AGENTS.md\n\n" + agents_path.read_text(errors="replace"))

    # Recently modified files (last 7 days)
    recent_output = _run(
        [
            "git", "log",
            "--name-only",
            "--since=7 days ago",
            "--pretty=format:",
        ],
        cwd=ROOT,
    )
    recent_files = sorted(
        {f for f in recent_output.splitlines() if f.strip()}
    )[:50]
    if recent_files:
        parts.append(
            "## Files modified in the last 7 days\n\n"
            + "\n".join(f"- {f}" for f in recent_files)
        )
    else:
        parts.append("## Files modified in the last 7 days\n\n_(none)_")

    return "\n\n---\n\n".join(parts)


# ── Prompt rendering ───────────────────────────────────────────────────────────

def render_prompt(repo_context: str) -> str:
    template = PROMPT_PATH.read_text()
    return template.replace("{{REPO_CONTEXT}}", repo_context)


# ── Tool schema construction ───────────────────────────────────────────────────

def build_tool_schema() -> dict:
    """Wrap audit-finding.schema.json as the input_schema for report_findings."""
    finding_schema = json.loads(SCHEMA_PATH.read_text())
    # Strip $schema / $id — they're not valid inside Anthropic tool input_schema.
    # title / description are intentionally kept: the API uses them for tool documentation.
    for key in ("$schema", "$id"):
        finding_schema.pop(key, None)
    return {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "description": "List of tech-debt findings. Empty array if the codebase is clean.",
                "items": finding_schema,
            }
        },
        "required": ["findings"],
    }


# ── Batch submission ───────────────────────────────────────────────────────────

def submit_batch(
    *,
    api_key: str,
    repo: str,
    model: str,
    rendered_prompt: str,
    tool_schema: dict,
) -> str:
    """POST to /v1/messages/batches and return the batch ID."""
    repo_name = repo.split("/")[-1]  # custom_id: just the repo slug

    payload = {
        "requests": [
            {
                "custom_id": repo_name,
                "params": {
                    "model": model,
                    "max_tokens": MAX_TOKENS,
                    "tools": [
                        {
                            "name": "report_findings",
                            "description": (
                                "Report all tech-debt findings discovered during the weekly audit. "
                                "Call this exactly once with the complete findings array."
                            ),
                            "input_schema": tool_schema,
                        }
                    ],
                    "tool_choice": {"type": "tool", "name": "report_findings"},
                    "messages": [
                        {"role": "user", "content": rendered_prompt}
                    ],
                },
            }
        ]
    }

    body = json.dumps(payload).encode()
    req = request.Request(
        BATCHES_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req) as resp:
            response_body = resp.read()
    except error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        print(
            f"ERROR: Anthropic API returned HTTP {exc.code}: {body_text}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = json.loads(response_body)
    batch_id: str = data["id"]
    return batch_id


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = require_env("ANTHROPIC_API_KEY")
    repo = require_env("GITHUB_REPOSITORY")
    model = os.environ.get("AUDIT_MODEL", "").strip() or DEFAULT_MODEL

    # Defensive shape check (PM3-89). The live API call below is the
    # authoritative validator; this catches obvious typos before we burn the
    # batch submission round-trip.
    if not _MODEL_ID_RE.match(model):
        print(
            f"::error::AUDIT_MODEL={model!r} does not match the expected shape "
            f"(claude-{{opus|sonnet|haiku}}-N-M[-N][-YYYYMMDD]). "
            f"Override with the AUDIT_MODEL env var or update DEFAULT_MODEL.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"model:  {model}")
    print(f"repo:   {repo}")
    print(f"prompt: {PROMPT_PATH}")
    print(f"schema: {SCHEMA_PATH}")

    print("building repo context …")
    repo_context = build_repo_context()

    print("rendering prompt …")
    rendered_prompt = render_prompt(repo_context)

    print("building tool schema …")
    tool_schema = build_tool_schema()

    print("submitting batch to Anthropic …")
    batch_id = submit_batch(
        api_key=api_key,
        repo=repo,
        model=model,
        rendered_prompt=rendered_prompt,
        tool_schema=tool_schema,
    )

    out_path = Path("audit-batch-id.txt")
    out_path.write_text(batch_id)
    print(f"batch ID: {batch_id}")
    print(f"written to {out_path}")


if __name__ == "__main__":
    main()
