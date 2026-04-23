# /snowflake-coldstart

Full Snowflake ML workflow from connection to deployment.

## Usage

```
/snowflake-coldstart <table_or_query> [--target <column>] [--warehouse <wh>]
```

## Workflow

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin. Search paths:
   - Cortex Code: `.cortex/skills/*/templates/ml_utils.py`, `~/.snowflake/cortex/skills/*/templates/ml_utils.py`
   - Claude Code: `~/.claude/plugins/*/templates/ml_utils.py`
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. **Prefer Cortex Code native tools when available:**
   - If the `sql_execute` tool is available, use it for ALL SQL (replaces `snowflake_utils.execute_query()`)
   - Use `#DB.SCHEMA.TABLE` inline syntax to inject table schema/sample into context (replaces manual `DESCRIBE` / `SELECT ... LIMIT 10`)
   - Use `cortex search object "<query>"` for semantic data discovery (replaces `SHOW DATABASES / SCHEMAS / TABLES` loops)
   - Fall back to `snowflake_utils` helpers if running in Claude Code or if native tools are unavailable
4. Verify connection: `sql_execute("SELECT CURRENT_VERSION()")` (Cortex Code) OR `/snowflake-connect --check` (Claude Code)
5. If connection fails, tell the user: `/connections` (Cortex Code interactive UI) or `/snowflake-connect` (Claude Code)

### Stage 1: Connect & Discover

1. **Connect:** `sql_execute("SELECT CURRENT_VERSION()")` (Cortex Code) or `snowflake_utils.get_snowflake_connection()` (Claude Code)
2. **Discover data sources** — prefer these in order:
   - If the user provided natural-language context ("our customer transactions data"): run `cortex search object "<user's description>"` for semantic object discovery across databases
   - If a semantic view exists: `cortex semantic-views discover` and `cortex semantic-views describe <view>` — prefer these over raw tables for business-aligned queries
   - Otherwise, fall back to `SHOW DATABASES / SCHEMAS / TABLES` via `sql_execute` or `snowflake_utils.get_snowflake_metadata()`
3. **Profile the target:**
   - Inject `#DB.SCHEMA.TABLE` in the prompt to get column types, PKs, row count, and sample rows directly in context (Cortex Code)
   - Only run manual `DESCRIBE TABLE` + `SELECT ... LIMIT 100` if deeper profiling (distributions, null rates) is needed
4. If `<table_or_query>` is a query: execute via `sql_execute` and profile results
5. Load data into local DataFrame for EDA (via `snowflake_utils.load_from_snowflake()` — this part still needs the local Python path)
6. Write discovery report via report bus

### Stage 2: SQL Development

1. Based on data profile, generate DDL:
   - Staging table (if loading from external source)
   - Feature table (with clustering keys)
   - Views for common transformations
2. Show SQL for user approval before execution
3. Execute approved SQL

### Stage 3: Snowpark Pipeline

1. Build Snowpark DataFrame transformation pipeline
2. Read EDA report if available from core workflow
3. Generate `src/snowpark_pipeline.py` with:
   - Data loading from Snowflake
   - Transformations (joins, aggregations, feature engineering)
   - Output to feature table
4. Test pipeline locally with sample data

### Stage 4: Train Model

1. Two modes based on user preference:
   - **Snowpark ML**: train sklearn-compatible model in Snowpark
   - **Snowflake ML Functions**: use FORECAST, ANOMALY_DETECTION, etc.
2. Train and evaluate
3. Register model in Snowflake Model Registry
4. Log experiment via core `log_experiment()`

### Stage 5: Evaluate

1. Run model evaluation
2. Write results back to Snowflake table
3. Generate evaluation report
4. Invoke core ml-theory-advisor for methodology review (if ML mode)

### Stage 6: Deploy

1. Register model in Snowflake Model Registry (if not done in Stage 4)
2. Create Streamlit in Snowflake dashboard
3. Create stored procedure for batch inference
4. Set up Snowflake Task for scheduled inference (optional)

### Stage 7: Finalize

1. Generate comprehensive report
2. Document all deployed Snowflake resources
3. Print resource summary table

## Output

Summary of all Snowflake resources created: tables, views, models, stored procedures, Streamlit apps.
