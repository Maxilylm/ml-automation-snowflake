---
name: Plugin layout & manifest conventions
description: Loaded when editing plugin-public-API files (AGENTS.md, agents/, commands/, skills/, manifest)
paths: ["AGENTS.md", "agents/**", "commands/**", "skills/**", ".cortex-plugin/**"]
---

# Plugin conventions

This repo IS one Claude Code plugin. The following files are the plugin's **public API** — changes here are higher-risk than changes inside skill bodies.

## Required files

| File | Why |
|---|---|
| `AGENTS.md` | Routing table — agents, skills, when-to-use |
| `README.md` | Human-facing overview |
| `.cortex-plugin/plugin.json` | Plugin manifest (must be valid JSON) |
| `agents/<name>.md` | Per-agent definitions referenced from AGENTS.md |
| `commands/<name>.md` | Slash commands |
| `skills/<name>/SKILL.md` | Skill bodies |

## Public API rules

**BREAKING changes (CI flags as `BREAKING`):**

- Removing or renaming an agent/command/skill that exists on `main`.
- Changing a skill's `argument-hint` or `allowed-tools` to narrow accepted input.
- Changing manifest `name`.
- Removing an AGENTS.md row without removing the underlying file.

**Non-breaking (no flag):**

- Adding new agents/commands/skills.
- Improving descriptions.
- Adding optional frontmatter fields.

## Consistency requirements

- Every AGENTS.md "Available Agents" entry has a matching `agents/<name>.md`.
- Every "Available Skills" entry has a matching `skills/<name>/SKILL.md`.
- Every command file is referenced from somewhere (AGENTS.md or routing logic).
- Files in `agents/` or `skills/` not in AGENTS.md are **orphans** — flag as `BUG`.

## Manifest minimum

```json
{
  "name": "spark-<domain>",
  "version": "0.1.0",
  "description": "...",
  "agents": [...],
  "commands": [...],
  "skills": [...]
}
```

`scripts/validate_plugin.py` enforces required fields in CI. Schema violations fail the build.
