---
name: snowflake-deploy
description: "Deploy to Snowflake — Model Registry, Streamlit in Snowflake, or stored procedure inference endpoint"
aliases: [sf deploy, snowflake model deploy, streamlit in snowflake]
extends: ml-automation
user_invocable: true
---

# Snowflake Deploy

Package and deploy ML artifacts to Snowflake-native targets: promote a registered model version to production in the Model Registry, publish an interactive Streamlit in Snowflake app for stakeholder exploration, or wrap model inference in a vectorized stored procedure for SQL-callable batch prediction. Validates deployment health and prints the live endpoint or app URL on completion.

## Full Specification

See `commands/snowflake-deploy.md` for the complete workflow.
