---
name: snowflake-train
description: "Train models using Snowpark ML or Snowflake ML Functions (FORECAST, ANOMALY_DETECTION). Registers in Model Registry."
aliases: [sf train, snowpark ml train, snowflake model]
extends: spark
user_invocable: true
---

# Snowflake Train

Train machine learning models directly inside Snowflake using Snowpark ML estimators (scikit-learn-compatible API) or built-in ML Functions such as FORECAST and ANOMALY_DETECTION. Handles train/test splitting, feature preprocessing via Snowpark ML Pipeline, hyperparameter search, evaluation metrics, and automatic registration of the trained model in the Snowflake Model Registry with versioning metadata.

Use this whenever the user wants to train a model on Snowflake data, even if they don't say "train." Also use it when the user mentions "forecast," "anomaly detection," "predict on my Snowflake table," or "build a model in the warehouse."

## When to Use

- The user wants to train a classification or regression model on data stored in Snowflake
- Time series forecasting is needed using Snowflake's built-in FORECAST function
- Anomaly detection or contribution analysis should run natively inside the warehouse
- The user wants to register a trained model in the Snowflake Model Registry with metrics and version tags

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Select mode** -- determine Snowpark ML (sklearn-compatible estimators) or Snowflake ML Functions (FORECAST, ANOMALY_DETECTION, CONTRIBUTION_EXPLORER) based on `--mode` flag or task type
3. **Snowpark ML path** -- load data via Snowpark session, split train/test, build preprocessing pipeline, train model, evaluate on test set
4. **ML Functions path** -- configure and call the appropriate built-in function, collect results
5. **Register model** -- register in Snowflake Model Registry with version name, metrics dict, and tags
6. **Report** -- log experiment via core `log_experiment()` and write report bus entry

**Agent:** snowflake-ml-engineer

## Report Bus Integration

```python
save_agent_report("snowflake_train_report", {
    "model_name": model_name,
    "mode": "snowpark-ml",
    "metrics": {"accuracy": 0.92, "f1": 0.89},
    "registry_version": "v1",
    "target_column": target_col
})
```

## Full Specification

See `commands/snowflake-train.md` for the complete workflow.
