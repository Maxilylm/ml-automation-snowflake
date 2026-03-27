# /snowflake-pipeline

Build a Snowpark data transformation pipeline.

## Usage

```
/snowflake-pipeline <source_table> [--output <target_table>]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

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
