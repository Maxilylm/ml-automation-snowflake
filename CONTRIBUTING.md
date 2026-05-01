# Contributing to ml-automation-snowflake

This is one of 14 Claude Code plugins in the Blend Spark Harness. Work is tracked in Jira project **[PM3](https://blend360.atlassian.net/jira/core/projects/PM3/board)** — filter by label `plugin:snowflake` for this plugin's slice.

## Branching model

Trunk-based, short-lived feature branches.

- `main` is always shippable.
- Every change lands via PR, never direct push.
- **Branch names must start with `PM3-<ticket>-<slug>`** (e.g., `PM3-12-add-llm-evaluator`). CI rejects branches without the prefix; this is what auto-links your branch to the Jira ticket via the GitHub for Jira app.

## Smart commits

Reference Jira tickets in commit messages — they auto-link in Jira and can transition status without leaving git.

| Keyword | Effect |
|---|---|
| `PM3-12` (anywhere) | Auto-links commit to PM3-12 |
| `PM3-12 #in-progress` | Transitions to In Progress |
| `PM3-12 #done` / `#close` | Transitions to Done |
| `PM3-12 #time 2h` | Logs 2h |
| `PM3-12 #comment <text>` | Adds comment |

Example: `PM3-12 #in-progress add headless wrapper skeleton`.

## Pull requests

`.github/pull_request_template.md` auto-loads. Required:

- **Linked Jira ticket** (`PM3-N` in title or body).
- **Summary** (what + why).
- **Test plan** (how you verified).

PR must:

1. Pass `.github/workflows/claude-review.yml`.
2. Have a CODEOWNERS-routed approval.
3. Reference a PM3-N ticket.

## Code review

Two flavors run on every PR:

1. **Automated Claude review** — `claude -p` invoked headless. Posts inline comments for BUG / SECURITY / CORRECTNESS / BREAKING / CRITICAL only. STYLE filtered out (severity criteria in `CLAUDE.md`).
2. **Human review** — routed by `.github/CODEOWNERS`. Use Claude's findings as a starting point, not a substitute.

The Claude reviewer is *independent* — no conversation context from the author. Iterate the prompt in `.claude/commands/review.md` if it consistently misses something.

## Local development

```bash
git clone git@github.com:BLEND360/ml-automation-snowflake.git
cd ml-automation-snowflake
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"  # if pyproject.toml exists
# else: pip install -r requirements.txt && pip install pytest pytest-cov

pytest                                  # run tests
python scripts/validate_plugin.py       # check plugin layout (manifest, AGENTS.md)
python scripts/claude_review.py --base-ref main  # local dry-run of CI review
```

## Plugin layout invariants

Catch these locally before pushing — `validate_plugin.py` enforces them in CI:

- `.cortex-plugin/plugin.json` is valid JSON with `name`, `version`, `description`.
- Every `agents/<name>.md` is referenced in AGENTS.md.
- Every `skills/<name>/` is referenced in AGENTS.md.
- AGENTS.md routing entries point to existing files.

## Public API rules (BREAKING changes)

The following are **breaking changes** (CI flags as `BREAKING`):

- Removing or renaming an agent/command/skill on `main`.
- Changing a skill's `argument-hint` or `allowed-tools` to narrow accepted input.
- Changing manifest `name`.
- Removing an AGENTS.md entry without removing the underlying file.

Non-breaking (no flag): adding new agents/commands/skills, expanding `paths` globs, adding optional frontmatter.
