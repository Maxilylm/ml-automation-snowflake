# /snowflake-sql

Generate and execute Snowflake SQL from natural language.

## Usage

```
/snowflake-sql <description>
```

Example: `/snowflake-sql create a table for customer transactions with clustering on date`

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

### 1) Generate SQL

Using the snowflake-data-engineer agent:
- Parse natural language description
- Generate Snowflake-optimized SQL
- Include comments explaining design choices

### 2) Show for approval

Display the generated SQL and ask: "Execute this SQL? (yes/no/edit)"

### 3) Execute

If approved:
- Execute via `snowflake_utils.execute_query()`
- Display results (for SELECT) or confirmation (for DDL/DML)
- Optionally save to `sql/<descriptive_name>.sql`

### 4) Report

Log the executed SQL and results in the report bus.
