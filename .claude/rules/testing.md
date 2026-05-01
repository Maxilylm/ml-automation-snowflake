---
name: Testing conventions
description: Loaded when editing test files (test_*.py, *_test.py, conftest.py)
paths: ["**/test_*.py", "**/*_test.py", "**/conftest.py", "**/tests/**/*.py"]
---

# Testing conventions

- **Pytest** is the framework. No unittest classes for new tests.
- Use **fixtures** over setup/teardown. Check `conftest.py` in the plugin root and `benchmark/conftest.py` before inventing a new fixture — most common needs already have one.
- **Never hit real APIs** in unit tests. Mock LLM responses, cloud SDK calls, and database connections.
- Integration tests requiring real services live under `tests/integration/` and are gated behind `pytest.mark.integration`. CI runs them only when the `INTEGRATION=1` env var is set.
- Each plugin maintains its own coverage floor (default 70%, configured per plugin in `pyproject.toml`). Do not lower it without an explicit ticket.
- **Test names describe behavior, not function names.** `test_evaluator_flags_hallucinations_when_evidence_missing` over `test_evaluate_1`.
- Parametrize for table-driven tests: `@pytest.mark.parametrize("input,expected", [...])`.

## Available shared fixtures

| Fixture | Where | Returns |
|---|---|---|
| `mock_llm_response` | per-plugin `conftest.py` | Deterministic LLM output for evaluation |
| `sample_dataset` | per-plugin `conftest.py` | Small in-memory pandas/dict dataset |
| `temp_workspace` | per-plugin `conftest.py` | Isolated `tmp_path` for FS operations |
| `gold_standard_loader` | `benchmark/conftest.py` | Loads gold-standard outputs by task ID |
| `rubric_scorer` | `benchmark/conftest.py` | Scores a candidate output against a rubric |

If you propose creating a fixture that duplicates one above, expect human review to reject.

## Anti-patterns to flag

- Tests that pass against an empty mock (mock returns `MagicMock()` and assertions check truthy).
- `time.sleep` in tests — use `freezegun` or fixture-driven time control.
- Snapshots without an explicit golden file — non-reproducible.
- Tests that depend on test execution order.
