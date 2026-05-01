---
description: Run the team code review checklist against the current diff (or a specified ref range)
argument-hint: "[base-ref] (defaults to main)"
allowed-tools: ["Bash", "Read", "Grep", "Glob"]
---

# /review — Team code review

Run a focused code review on the current branch's diff.

## Steps

1. Determine the base ref. If `$ARGUMENTS` is provided, use it. Otherwise default to `main`.
2. Run `git diff $BASE...HEAD --name-only` to list changed files.
3. For each changed file, read its current content (not just the diff — you need full context to flag correctness issues).
4. **Apply severity criteria from `CLAUDE.md`.** Report only BUG / SECURITY / CORRECTNESS / BREAKING / CRITICAL. Skip style.
5. **Multi-pass when the diff exceeds 8 files:**
   - Pass 1: per-file local analysis (one finding pass per file).
   - Pass 2: cross-file integration (data flow, broken imports, contract changes).
6. Output as JSON conforming to `schemas/finding.schema.json` if invoked from CI; prose otherwise.
7. **Apply the few-shot examples** in CLAUDE.md to ambiguous cases (try/except: pass, mutable defaults, float comparison).

## Anti-patterns to avoid

- Do not report findings for code outside the diff.
- Do not propose stylistic refactors ("I'd extract this into a helper").
- Do not duplicate findings already addressed in prior review comments — when re-running on a PR, ask the user for the prior findings list and skip resolved ones.
- Do not invent fixtures or test infrastructure that doesn't exist (check `.claude/rules/testing.md` for available fixtures).
