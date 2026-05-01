---
name: Python conventions
description: Loaded when editing Python files anywhere in the repo
paths: ["**/*.py"]
---

# Python conventions

- Python 3.11+ for new code. Use modern syntax (`match`/`case`, `|` unions, PEP 604 annotations).
- Type hints on all public functions; `from __future__ import annotations` if forward references get noisy.
- Format with `black` (line length 100), lint with `ruff`. Do not flag style issues — they belong to the formatter.
- Imports: stdlib → third-party → local, separated by blank lines. `isort`-compatible.
- Avoid bare `except`. Catch the specific exception you mean. If you must use `except Exception`, log the exception and re-raise unless the failure is genuinely non-fatal (and say why in a comment — see CLAUDE.md few-shot example 1).
- Avoid mutable default arguments (`def f(x=[])`). Use `None` and initialize inside. See CLAUDE.md few-shot example 2.
- Compare floats with `math.isclose`, not `==`. See CLAUDE.md few-shot example 3.
- Logging: use `logging`, never `print` in library code. Plugin entry points and CLI commands may use `print`.
