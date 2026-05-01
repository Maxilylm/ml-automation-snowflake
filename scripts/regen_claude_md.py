#!/usr/bin/env python3
"""Regenerate CLAUDE.md's routing section from this plugin's AGENTS.md.

Idempotent. Run when AGENTS.md changes (new agent, new skill, removed entry).
Safe to run when there's nothing to update — exits 0 with no diff.

The routing block is delimited in CLAUDE.md by:
  start: "## Routing — agents and skills in this plugin"
  end:   "(See `AGENTS.md` for the canonical routing table; this section is a reminder for CI-invoked Claude.)"

Everything between (inclusive of both lines) is replaced with content extracted
from AGENTS.md's "Available Agents" and "Available Skills" sections.

Usage:
    cd ml-automation-<plugin>
    python3 scripts/regen_claude_md.py [--check]

--check exits non-zero if a regenerate would produce a diff (CI gate option).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START_MARKER = "## Routing — agents and skills in this plugin"
END_MARKER = "(See `AGENTS.md` for the canonical routing table; this section is a reminder for CI-invoked Claude.)"


def extract_section(text: str, header_re: str) -> str:
    m = re.search(rf"^##+ +{header_re}.*$", text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return f"_(No '{header_re}' section in AGENTS.md.)_"
    start = m.end()
    next_h = re.search(r"^##+ ", text[start:], re.MULTILINE)
    end = start + next_h.start() if next_h else len(text)
    return text[start:end].strip()


def render_routing_block(agents_md_text: str) -> str:
    agents = extract_section(agents_md_text, r"Available Agents")
    skills = extract_section(agents_md_text, r"Available Skills")
    return (
        f"{START_MARKER}\n\n"
        f"### Available agents\n\n{agents}\n\n"
        f"### Available skills\n\n{skills}\n\n"
        f"{END_MARKER}"
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="Exit non-zero if regenerate would produce a diff")
    args = p.parse_args()

    agents_path = ROOT / "AGENTS.md"
    claude_path = ROOT / "CLAUDE.md"
    if not agents_path.exists():
        print(f"::error::AGENTS.md not found at {agents_path}")
        return 2
    if not claude_path.exists():
        print(f"::error::CLAUDE.md not found at {claude_path}")
        return 2

    agents_text = agents_path.read_text()
    claude_text = claude_path.read_text()

    if START_MARKER not in claude_text or END_MARKER not in claude_text:
        print("::error::CLAUDE.md missing routing-section markers; not auto-regenerable")
        print(f"  expected start: {START_MARKER}")
        print(f"  expected end:   {END_MARKER}")
        return 2

    start = claude_text.index(START_MARKER)
    end = claude_text.index(END_MARKER) + len(END_MARKER)
    new_block = render_routing_block(agents_text)
    new_claude = claude_text[:start] + new_block + claude_text[end:]

    if new_claude == claude_text:
        print("OK (no drift between AGENTS.md and CLAUDE.md routing section)")
        return 0

    if args.check:
        print("::error::CLAUDE.md routing section is stale relative to AGENTS.md")
        print("Run `python3 scripts/regen_claude_md.py` to fix.")
        return 1

    claude_path.write_text(new_claude)
    print(f"✓ regenerated CLAUDE.md routing section ({claude_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
