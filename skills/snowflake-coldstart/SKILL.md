---
name: snowflake-coldstart
description: "Full Snowflake ML workflow — connect, discover data, build pipeline, train model, deploy to Snowflake"
aliases: [sf coldstart, snowflake workflow, snowflake ml pipeline]
extends: ml-automation
user_invocable: true
---

# Snowflake Coldstart

End-to-end orchestration for Snowflake ML projects: establishes connection, discovers and profiles available tables, builds a Snowpark transformation pipeline, trains a model using Snowpark ML or Snowflake ML Functions, and deploys the result to the Model Registry or a Streamlit in Snowflake app. Designed to take a project from zero to a live Snowflake-native ML solution with minimal manual steps.

## Full Specification

See `commands/snowflake-coldstart.md` for the complete workflow.
