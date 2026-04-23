---
name: snowflake-connect
description: "Setup and test Snowflake connection. Configures credentials, tests connectivity, stores project-specific overrides. Triggers: sf connect, snowflake setup, snowflake auth, connect to snowflake."
aliases: [sf connect, snowflake setup, snowflake auth]
extends: spark
user_invocable: true
tools: [Read, Write, Bash, sql_execute]
---

# Snowflake Connect

Configure and validate your Snowflake connection for the current project. Accepts credentials via environment variables, config file, or interactive prompts, then runs a connectivity smoke test and persists project-specific overrides so subsequent commands can connect without re-entering credentials.

Use this whenever the user wants to set up Snowflake access, even if they just say "connect to Snowflake" or "set up my warehouse." Also use it when any other Snowflake command fails with a connection error.

## When to Use

- The user is starting a new Snowflake project and needs to configure credentials
- A connection test is needed before running other Snowflake commands
- The user wants to switch accounts, roles, warehouses, or databases for the current project
- Another Snowflake command has failed with an authentication or connectivity error

## Workflow

1. **Check existing connection** -- look for `~/.snowflake/connections.toml`; if present and `--check` flag is set, test with `SELECT CURRENT_VERSION()` and report account, role, warehouse, database, schema
2. **Interactive setup** -- if no connections.toml exists, prompt for account identifier, username, authentication method (password / key-pair / SSO), role, warehouse, database, and schema
3. **Write connections.toml** -- persist configuration to `~/.snowflake/connections.toml` in standard TOML format
4. **Test connection** -- execute a smoke-test query, confirm connectivity, and save project-specific overrides to `.claude/snowflake-config.json`

**Agent:** snowflake-connector

## Report Bus Integration

```python
save_agent_report("snowflake_connection_report", {
    "status": "connected",
    "account": account,
    "role": role,
    "warehouse": warehouse,
    "database": database,
    "schema": schema
})
```

## Full Specification

See `commands/snowflake-connect.md` for the complete workflow.
