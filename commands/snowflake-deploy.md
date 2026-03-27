# /snowflake-deploy

Deploy models and apps to Snowflake.

## Usage

```
/snowflake-deploy [--target model-registry|streamlit|stored-procedure] [--model-name <name>]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

### Target 1: Model Registry

1. Find trained model artifacts (local or already in registry)
2. Register with version, metrics, tags
3. Optionally promote to "production" alias

### Target 2: Streamlit in Snowflake

1. Generate Streamlit app code based on project artifacts
2. Create Snowflake stage for app files
3. Deploy using `CREATE STREAMLIT` DDL
4. Report: app URL, access permissions

### Target 3: Stored Procedure

1. Package model + inference code
2. Create stored procedure:
   ```sql
   CREATE OR REPLACE PROCEDURE predict(input_table VARCHAR, output_table VARCHAR)
   RETURNS VARCHAR
   LANGUAGE PYTHON
   RUNTIME_VERSION = '3.10'
   PACKAGES = ('snowflake-snowpark-python', 'scikit-learn', 'joblib')
   HANDLER = 'run'
   AS $$ ... $$;
   ```
3. Optionally create Snowflake Task for scheduled batch inference
4. Report: procedure name, schedule

### Report

Write deployment report with all resource details.
