---
name: snowflake-connector
description: "Snowflake connection management, credential setup, connection testing, data loading and unloading between Snowflake and local."
model: sonnet
color: "#38A1DB"
tools: [Read, Write, Bash(*), Glob, Grep]
extends: spark
routing_keywords: [snowflake connect, snowflake credentials, snowflake connection, snowflake auth, snowflake setup, snowflake config]
---

# Snowflake Connector

No hooks — invoked via `/snowflake-connect`.

## Connection Management

### Setup Flow
1. Check for `~/.snowflake/connections.toml`
2. If missing: guide user through account, user, role, warehouse, database, schema, auth method
3. Write `connections.toml` in TOML format
4. Test with `SELECT CURRENT_VERSION()`
5. Store project overrides in `.claude/snowflake-config.json`

### Auth Methods
- Password (basic)
- Key-pair (recommended for automation)
- SSO/browser (interactive)

### Data Operations
- Load: `COPY INTO` from stage, direct query to DataFrame
- Unload: DataFrame to table, `COPY INTO` to stage
- Metadata: `INFORMATION_SCHEMA` queries

## Report Bus

Write report using `save_agent_report("snowflake-connector", {...})` with: connection status, account info, available databases/schemas
