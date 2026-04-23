# /snowflake-sql

Generate and execute Snowflake SQL from natural language.

## Usage

```
/snowflake-sql <description>
```

Example: `/snowflake-sql create a table for customer transactions with clustering on date`

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin. Search paths:
   - Cortex Code: `.cortex/skills/*/templates/ml_utils.py`, `~/.snowflake/cortex/skills/*/templates/ml_utils.py`
   - Claude Code: `~/.claude/plugins/*/templates/ml_utils.py`
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. **Prefer Cortex Code native tools when available:**
   - Before generating SQL manually, check if a semantic view exists: `cortex semantic-views discover` or `cortex semantic-views search "<domain>"`. If found, route the request through `cortex analyst query "<user's natural-language request>"` instead of LLM-based SQL generation — it produces business-aligned queries with explanations.
   - Use `sql_execute` (not `snowflake_utils.execute_query()`) to run the approved SQL when available.
   - Fall back to manual LLM SQL generation + `snowflake_utils.execute_query()` only when no semantic model exists or when running under Claude Code.
4. Verify connection: `sql_execute("SELECT CURRENT_VERSION()")` or `/snowflake-connect --check`
5. If connection fails, tell the user to run `/connections` (Cortex Code) or `/snowflake-connect` (Claude Code)

### 1) Generate SQL

Route based on the request type and available tooling:

1. **Semantic-model path (preferred when available):**
   - Run `cortex semantic-views search "<domain keywords>"` to see if a semantic view covers the data
   - If found: delegate to `cortex analyst query "<user's natural-language request>" --model=<semantic-model.yaml>`
   - Cortex Analyst returns generated SQL with explanation and suggested follow-ups — present these to the user instead of running your own LLM generation pass
2. **Manual generation path (fallback):**
   - Used for DDL (CREATE TABLE / STAGE / STREAM), one-off analytical queries, or when no semantic model exists
   - Using the snowflake-data-engineer agent: parse the natural language description, generate Snowflake-optimized SQL with comments explaining design choices
   - If the target table is already in context, inject `#DB.SCHEMA.TABLE` to ground the LLM in the actual schema

### 2) Show for approval

Display the generated SQL and ask: "Execute this SQL? (yes/no/edit)". The plugin's approval gate is authoritative — do not auto-execute even if Cortex Analyst returned the SQL.

### 3) Execute

If approved:
- `sql_execute("<approved SQL>")` (Cortex Code) or `snowflake_utils.execute_query()` (Claude Code)
- Display results (for SELECT) or confirmation (for DDL/DML)
- Optionally save to `sql/<descriptive_name>.sql`

### 4) Report

Log the executed SQL and results in the report bus.
