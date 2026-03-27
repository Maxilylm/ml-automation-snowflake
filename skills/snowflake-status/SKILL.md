---
name: snowflake-status
description: "Check Snowflake resources — warehouse usage, deployed models, Streamlit apps, stored procedures, recent queries"
aliases: [sf status, snowflake resources, snowflake info]
extends: ml-automation
user_invocable: true
---

# Snowflake Status

Query and summarize the current state of Snowflake resources relevant to the project: virtual warehouse credit consumption, Model Registry versions and their deployment stage, running Streamlit in Snowflake apps, registered stored procedures, and the query history for recent pipeline or inference runs. Presents a unified status table to help quickly spot idle warehouses, stale model versions, or failing jobs.

## Full Specification

See `commands/snowflake-status.md` for the complete workflow.
