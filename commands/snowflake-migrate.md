# /snowflake-migrate

Migrate existing Python ML code to Snowpark equivalents.

## Usage

```
/snowflake-migrate [<file_or_directory>]
```

Default: scan current project for Python files with pandas/sklearn imports.

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin. Search paths:
   - Cortex Code: `.cortex/skills/*/templates/ml_utils.py`, `~/.snowflake/cortex/skills/*/templates/ml_utils.py`
   - Claude Code: `~/.claude/plugins/*/templates/ml_utils.py`
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. **Prefer Cortex Code native tools when available:** `sql_execute` for any test queries against the migrated code. Fall back to `snowflake_utils` under Claude Code.
4. Verify connection: `sql_execute("SELECT CURRENT_VERSION()")` or `/snowflake-connect --check`
5. If connection fails, tell the user to run `/connections` (Cortex Code) or `/snowflake-connect` (Claude Code)

### 1) Scan for migration candidates

- Find Python files with: `import pandas`, `from sklearn`, `pd.read_csv`, etc.
- List files and their pandas/sklearn usage

### 2) Generate Snowpark equivalents

For each file, generate migration:

| pandas | Snowpark |
|---|---|
| `pd.read_csv()` | `session.table()` or `session.read.csv()` |
| `df.merge()` | `df.join()` |
| `df.groupby().agg()` | `df.group_by().agg()` |
| `df.fillna()` | `df.fillna()` (same API) |
| `sklearn.Pipeline` | `snowflake.ml.modeling.pipeline.Pipeline` |

### 3) Show diff for approval

Display side-by-side comparison of original vs. migrated code.

### 4) Write migrated code

Write to `src/snowpark_<original_name>.py` or replace in-place (user choice).

### Report

Log migration: files changed, API translations, compatibility notes.
