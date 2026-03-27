---
name: snowflake-train
description: "Train models using Snowpark ML or Snowflake ML Functions (FORECAST, ANOMALY_DETECTION). Registers in Model Registry."
aliases: [sf train, snowpark ml train, snowflake model]
extends: ml-automation
user_invocable: true
---

# Snowflake Train

Train machine learning models directly inside Snowflake using Snowpark ML estimators (scikit-learn-compatible API) or built-in ML Functions such as FORECAST and ANOMALY_DETECTION. Handles train/test splitting, feature preprocessing via Snowpark ML Pipeline, hyperparameter search, evaluation metrics, and automatic registration of the trained model in the Snowflake Model Registry with versioning metadata.

## Full Specification

See `commands/snowflake-train.md` for the complete workflow.
