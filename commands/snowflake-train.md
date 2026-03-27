# /snowflake-train

Train a model using Snowpark ML or Snowflake ML Functions.

## Usage

```
/snowflake-train <table> --target <column> [--mode snowpark-ml|ml-functions] [--model-name <name>]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

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
