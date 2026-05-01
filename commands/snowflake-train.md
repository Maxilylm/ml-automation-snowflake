# /snowflake-train

Train a model using Snowpark ML or Snowflake ML Functions.

## Usage

```
/snowflake-train <table> --target <column> [--mode snowpark-ml|ml-functions] [--model-name <name>]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin. Search paths:
   - Cortex Code: `.cortex/skills/*/templates/ml_utils.py`, `~/.snowflake/cortex/skills/*/templates/ml_utils.py`
   - Claude Code: `~/.claude/plugins/*/templates/ml_utils.py`
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. **Prefer Cortex Code native tools when available:**
   - `sql_execute` for SQL — including `SELECT CURRENT_VERSION()` and model registry queries
   - `#DB.SCHEMA.TABLE` to inject training-table metadata into prompts
   - Fall back to `snowflake_utils` helpers under Claude Code
4. Verify connection: `sql_execute("SELECT CURRENT_VERSION()")` or `/snowflake-connect --check`
5. If connection fails, tell the user to run `/connections` (Cortex Code) or `/snowflake-connect` (Claude Code)

### Mode 1: Snowpark ML

1. Load data via Snowpark session
2. Split: train/test using Snowpark DataFrame operations
3. Build preprocessing pipeline (Snowpark ML Pipeline)
4. Train model (RandomForestClassifier, XGBClassifier, etc.)
5. Evaluate on test set
6. Register in Snowflake Model Registry

### Mode 2: Snowflake ML Functions

1. Call built-in functions:
   - `FORECAST` for time series
   - `ANOMALY_DETECTION` for outlier detection
   - `CONTRIBUTION_EXPLORER` for feature attribution
2. Configure function parameters
3. Execute and collect results

### Register Model

```python
from snowflake.ml.registry import Registry
reg = Registry(session)
mv = reg.log_model(model, model_name=model_name, version_name="v1",
                   metrics={"accuracy": acc, "f1": f1})
```

### Report

Log experiment via core `log_experiment()` and write report bus entry.
