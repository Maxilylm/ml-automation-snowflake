# /snowflake-coldstart

Full Snowflake ML workflow from connection to deployment.

## Usage

```
/snowflake-coldstart <table_or_query> [--target <column>] [--warehouse <wh>]
```

## Workflow

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

### Stage 1: Connect & Discover

1. Connect to Snowflake using `snowflake_utils.get_snowflake_connection()`
2. List available databases, schemas, tables
3. If `<table_or_query>` is a table name: profile it (row count, columns, types, nulls, distributions)
4. If `<table_or_query>` is a SQL query: execute and profile results
5. Load data into local DataFrame for EDA
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
