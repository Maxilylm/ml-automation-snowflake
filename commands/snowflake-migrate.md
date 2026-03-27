# /snowflake-migrate

Migrate existing Python ML code to Snowpark equivalents.

## Usage

```
/snowflake-migrate [<file_or_directory>]
```

Default: scan current project for Python files with pandas/sklearn imports.

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

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
