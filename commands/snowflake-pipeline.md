# /snowflake-pipeline

Build a Snowpark data transformation pipeline.

## Usage

```
/snowflake-pipeline <source_table> [--output <target_table>]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin. Search paths:
   - Cortex Code: `.cortex/skills/*/templates/ml_utils.py`, `~/.snowflake/cortex/skills/*/templates/ml_utils.py`
   - Claude Code: `~/.claude/plugins/*/templates/ml_utils.py`
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. **Prefer Cortex Code native tools when available:**
   - `#DB.SCHEMA.TABLE` to inject source-table schema/sample before designing the pipeline — replaces manual `SHOW TABLES` / `DESCRIBE TABLE`
   - `sql_execute` for test runs on sample data
   - Fall back to `snowflake_utils` under Claude Code
4. Verify connection: `sql_execute("SELECT CURRENT_VERSION()")` or `/snowflake-connect --check`
5. If connection fails, tell the user to run `/connections` (Cortex Code) or `/snowflake-connect` (Claude Code)

### 1) Profile source table

- Connect and describe `<source_table>`
- Get column types, row count, sample data
- Read EDA report from core if available

### 2) Design pipeline

Using snowflake-data-engineer agent:
- Identify required transformations (joins, aggregations, type casts, null handling)
- Design Snowpark DataFrame operations
- Include data quality checks

### 3) Generate code

Write `src/snowpark_pipeline.py`:

```python
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when, avg, count

def build_pipeline(session: Session, source_table: str, target_table: str):
    df = session.table(source_table)
    # transformations...
    df.write.mode("overwrite").save_as_table(target_table)
    return df
```

### 4) Test

Run pipeline on a sample (LIMIT 1000) to verify.

### 5) Report

Log pipeline configuration and results.
