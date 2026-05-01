#!/usr/bin/env python3
"""Validate this plugin's layout consistency: manifest, AGENTS.md, and references.

Single-plugin mode: runs against the current repo (assumed to BE one plugin).
Catches structural drift (orphan agent/skill files, AGENTS.md rows missing
implementations, manifest schema violations) before Claude review sees them —
these are deterministic checks, not LLM judgment.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MANIFEST_REQUIRED = {"name", "version", "description"}


def err(msg: str) -> None:
    print(f"::error::{msg}")


def validate() -> int:
    fails = 0

    manifest_path = ROOT / ".cortex-plugin" / "plugin.json"
    if not manifest_path.exists():
        err(f"missing manifest at {manifest_path.relative_to(ROOT)}")
        fails += 1
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            err(f"manifest is not valid JSON: {e}")
            fails += 1
            manifest = None
        if manifest:
            missing = MANIFEST_REQUIRED - manifest.keys()
            if missing:
                err(f"manifest missing required fields: {sorted(missing)}")
                fails += 1

    agents_md = ROOT / "AGENTS.md"
    if not agents_md.exists():
        err("missing AGENTS.md")
        return fails + 1

    agents_md_text = agents_md.read_text()

    agents_dir = ROOT / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            name = f.stem
            if not re.search(rf"\b{re.escape(name)}\b", agents_md_text):
                err(f"agents/{name}.md exists but is not referenced in AGENTS.md (orphan)")
                fails += 1

    skills_dir = ROOT / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                name = d.name
                if not re.search(rf"\b/?{re.escape(name)}\b", agents_md_text):
                    err(f"skills/{name}/ exists but is not referenced in AGENTS.md (orphan)")
                    fails += 1

    if fails == 0:
        print("OK")
    return fails


if __name__ == "__main__":
    sys.exit(1 if validate() else 0)
