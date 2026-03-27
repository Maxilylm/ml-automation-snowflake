---
name: snowflake-connect
description: "Setup and test Snowflake connection. Configures credentials, tests connectivity, stores project-specific overrides."
aliases: [sf connect, snowflake setup, snowflake auth]
extends: ml-automation
user_invocable: true
---

# Snowflake Connect

Configure and validate your Snowflake connection for the current project. Accepts credentials via environment variables, config file, or interactive prompts, then runs a connectivity smoke test and persists project-specific overrides so subsequent commands can connect without re-entering credentials.

## Full Specification

See `commands/snowflake-connect.md` for the complete workflow.
