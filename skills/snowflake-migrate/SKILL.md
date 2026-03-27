---
name: snowflake-migrate
description: "Migrate existing Python ML code (pandas, sklearn) to Snowpark equivalents"
aliases: [sf migrate, pandas to snowpark, snowpark migration]
extends: ml-automation
user_invocable: true
---

# Snowflake Migrate

Analyze existing pandas and scikit-learn ML code and produce equivalent Snowpark Python implementations that run entirely inside the Snowflake warehouse. Maps DataFrame operations to Snowpark API calls, replaces sklearn preprocessing with Snowpark ML Pipeline transformers, and flags any patterns that have no direct Snowpark equivalent with recommended workarounds.

## Full Specification

See `commands/snowflake-migrate.md` for the complete workflow.
