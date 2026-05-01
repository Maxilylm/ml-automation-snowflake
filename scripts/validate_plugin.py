#!/usr/bin/env python3
"""Validate this plugin's layout consistency: manifest, AGENTS.md, and references.

Two layers of checks:

1. **Required (always run)** — orphan agents/skills (file exists but not in AGENTS.md),
   missing/invalid manifest, missing required manifest fields. Fails CI on violation.

2. **Strict (opt-in via STRICT_PLUGIN_VALIDATION=1)** — bidirectional checks:
   AGENTS.md mentions /foo but no skill/command exists (dangling reference);
   plugin.json arrays must match files on disk.

Manifest arrays (agents/commands/skills) are intentionally metadata-only in this
harness — AGENTS.md is the canonical routing source of truth (PM3-79 decision
2026-05-01: option c). Strict mode's array consistency check is therefore an
opt-in for a hypothetical future state where a registry consumer reads the
manifest arrays. Today, no code reads those arrays; AGENTS.md is the single
source of truth, actively maintained as part of every PR. Enable strict mode
only AFTER running a populate script across all plugins (one-time migration).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRICT = os.environ.get("STRICT_PLUGIN_VALIDATION") == "1"

MANIFEST_REQUIRED = {"name", "version", "description"}


def err(msg: str) -> None:
    print(f"::error::{msg}")


def warn(msg: str) -> None:
    print(f"::warning::{msg}")


def validate() -> int:
    fails = 0

    # ── Manifest ──────────────────────────────────────────────────────────────
    manifest_path = ROOT / ".cortex-plugin" / "plugin.json"
    manifest = None
    if not manifest_path.exists():
        err(f"missing manifest at {manifest_path.relative_to(ROOT)}")
        fails += 1
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            err(f"manifest is not valid JSON: {e}")
            fails += 1
        if manifest:
            missing = MANIFEST_REQUIRED - manifest.keys()
            if missing:
                err(f"manifest missing required fields: {sorted(missing)}")
                fails += 1
            name = manifest.get("name", "")
            if name and not name.startswith("spark-") and STRICT:
                err(f"manifest name '{name}' does not match spark-<domain> pattern (strict mode)")
                fails += 1

    # ── AGENTS.md ─────────────────────────────────────────────────────────────
    agents_md = ROOT / "AGENTS.md"
    if not agents_md.exists():
        err("missing AGENTS.md")
        return fails + 1

    agents_md_text = agents_md.read_text()

    # ── Orphan agent files (file exists, not referenced in AGENTS.md) ─────────
    agents_dir = ROOT / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            name = f.stem
            if not re.search(rf"\b{re.escape(name)}\b", agents_md_text):
                err(f"agents/{name}.md exists but is not referenced in AGENTS.md (orphan)")
                fails += 1

    # ── Orphan skill directories ──────────────────────────────────────────────
    skills_dir = ROOT / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if not d.is_dir():
                continue
            name = d.name
            if not re.search(rf"\b/?{re.escape(name)}\b", agents_md_text):
                err(f"skills/{name}/ exists but is not referenced in AGENTS.md (orphan)")
                fails += 1

            # Skill frontmatter consistency
            sm = d / "SKILL.md"
            if sm.exists():
                fm = sm.read_text(errors="ignore")
                m = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
                if m:
                    declared = m.group(1).strip().strip("\"'")
                    if declared != name:
                        if STRICT:
                            err(f"skills/{name}/SKILL.md frontmatter name='{declared}' != directory name '{name}'")
                            fails += 1
                        else:
                            warn(f"skills/{name}/SKILL.md frontmatter name='{declared}' != directory name '{name}' (warn-only; set STRICT_PLUGIN_VALIDATION=1 to fail)")

    # ── STRICT-only checks (opt-in) ──────────────────────────────────────────
    if STRICT:
        # Dangling AGENTS.md references: /<name> mentioned but no skill or command exists
        slash_refs = set(re.findall(r"`/([a-z][a-z0-9-]*)`", agents_md_text))
        skill_disk = (
            {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()
        )
        cmd_dir = ROOT / "commands"
        cmd_disk = (
            {f.stem for f in cmd_dir.glob("*.md")} if cmd_dir.exists() else set()
        )
        for ref in slash_refs:
            if ref not in skill_disk and ref not in cmd_disk:
                err(f"AGENTS.md references /{ref} but no skill or command found (strict mode)")
                fails += 1

        # Manifest arrays vs disk
        if manifest:
            for arr_name, dir_name, ext in [("agents", "agents", ".md"), ("commands", "commands", ".md")]:
                disk = set()
                d = ROOT / dir_name
                if d.exists():
                    disk = {f.stem for f in d.glob(f"*{ext}")}
                arr = manifest.get(arr_name, [])
                arr_names = {(item.get("name", "") if isinstance(item, dict) else item) for item in arr}
                arr_names.discard("")
                arr_only = arr_names - disk
                disk_only = disk - arr_names
                if arr_only:
                    err(f"manifest {arr_name} declares but no file on disk: {sorted(arr_only)} (strict)")
                    fails += 1
                if disk_only:
                    err(f"{dir_name}/ has files not in manifest {arr_name}: {sorted(disk_only)} (strict)")
                    fails += 1

            arr = manifest.get("skills", [])
            arr_names = {(item.get("name", "") if isinstance(item, dict) else item) for item in arr}
            arr_names.discard("")
            disk = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()
            arr_only = arr_names - disk
            disk_only = disk - arr_names
            if arr_only:
                err(f"manifest skills declares but no dir: {sorted(arr_only)} (strict)")
                fails += 1
            if disk_only:
                err(f"skills/ has dirs not in manifest skills: {sorted(disk_only)} (strict)")
                fails += 1

    if fails == 0:
        mode = "strict" if STRICT else "default"
        print(f"OK ({mode} mode)")
    return fails


if __name__ == "__main__":
    sys.exit(1 if validate() else 0)
