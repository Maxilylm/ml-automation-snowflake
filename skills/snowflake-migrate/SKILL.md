---
name: snowflake-migrate
description: "Migrate existing Python ML code (pandas, sklearn) to Snowpark equivalents"
aliases: [sf migrate, pandas to snowpark, snowpark migration]
extends: ml-automation
user_invocable: true
---

# Snowflake Migrate

Analyze existing pandas and scikit-learn ML code and produce equivalent Snowpark Python implementations that run entirely inside the Snowflake warehouse. Maps DataFrame operations to Snowpark API calls, replaces sklearn preprocessing with Snowpark ML Pipeline transformers, and flags any patterns that have no direct Snowpark equivalent with recommended workarounds.

Use this whenever the user has existing Python ML code and wants it to run inside Snowflake, even if they don't say "migrate." Also use it when the user says "convert to Snowpark," "move my pandas code to Snowflake," or "rewrite for the warehouse."

## When to Use

- The user has pandas or scikit-learn code that should run inside Snowflake instead of locally
- An existing ML pipeline needs to be converted to Snowpark for scale or governance reasons
- The user wants a side-by-side comparison of their current code vs. the Snowpark equivalent
- Migration of `pd.read_csv` / `pd.merge` / `sklearn.Pipeline` patterns to Snowpark is needed

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Scan candidates** -- find Python files with `import pandas`, `from sklearn`, `pd.read_csv`, etc.; list files and their pandas/sklearn usage
3. **Generate equivalents** -- for each file, map pandas operations to Snowpark API calls (`pd.read_csv` to `session.table()`, `df.merge` to `df.join()`, `sklearn.Pipeline` to `snowflake.ml.modeling.pipeline.Pipeline`, etc.)
4. **Show diff** -- display side-by-side comparison of original vs. migrated code for user approval
5. **Write migrated code** -- write to `src/snowpark_<original_name>.py` or replace in-place (user choice)
6. **Report** -- log migration details: files changed, API translations, compatibility notes

## Report Bus Integration

```python
save_agent_report("snowflake_migrate_report", {
    "files_scanned": 12,
    "files_migrated": 4,
    "translations": ["pd.read_csv -> session.table", "df.merge -> df.join"],
    "unsupported_patterns": ["matplotlib inline plots"]
})
```

## Full Specification

See `commands/snowflake-migrate.md` for the complete workflow.
