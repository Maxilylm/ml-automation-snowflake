# /snowflake-connect

Setup and test Snowflake connection. Configures credentials, tests connectivity, stores project overrides.

## Usage

```
/snowflake-connect [--check]
```

- No args: full interactive setup
- `--check`: quick connection test only

## Workflow

### 0) Detect host environment

If running inside Cortex Code, delegate to native connection tooling before manual TOML editing:

1. Run `cortex connections list` — show existing connections
2. If the user needs to add/select one, tell them to use `/connections` (Cortex Code interactive UI) or `cortex connections set --connection <name>`
3. Verify with `sql_execute("SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")`
4. Skip steps 2–4 below (the TOML-writing flow) — Cortex Code manages this file natively
5. Proceed directly to step 5 (project overrides) using `.cortex/snowflake-config.json`

If running under Claude Code (no `sql_execute` tool, no `.cortex/` dir, no `CORTEX_CODE_SESSION` env var), use the manual flow below.

### 1) Check existing connection

Check if `~/.snowflake/connections.toml` exists.

If exists and `--check` flag:
- Test with `SELECT CURRENT_VERSION()` (via `sql_execute` if available, else `snowflake_utils.test_connection()`)
- Report: account, user, role, warehouse, database, schema
- Exit

### 2) Interactive setup (if no connections.toml, Claude Code only)

Prompt user for:
- **Account identifier** (e.g., `xy12345.us-east-1`)
- **Username**
- **Authentication method**: password | key-pair | SSO/browser
- **Role** (default: `SYSADMIN`)
- **Warehouse** (default: `COMPUTE_WH`)
- **Database**
- **Schema** (default: `PUBLIC`)

### 3) Write connections.toml

Write to `~/.snowflake/connections.toml`:

```toml
[default]
account = "<account>"
user = "<user>"
password = "<password>"  # or authenticator = "externalbrowser" for SSO
role = "<role>"
warehouse = "<warehouse>"
database = "<database>"
schema = "<schema>"
```

### 4) Test connection

```python
from snowflake.connector import connect
conn = connect(connection_name="default")
cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
print(cursor.fetchone())
conn.close()
```

### 5) Project overrides

Write to `.cortex/snowflake-config.json` (Cortex Code) or `.claude/snowflake-config.json` (Claude Code). Both files have the same schema; `snowflake_utils.save_project_config()` auto-selects the right path based on host detection:

```json
{
  "connection_name": "default",
  "database": "<database>",
  "schema": "<schema>",
  "warehouse": "<warehouse>",
  "role": "<role>"
}
```

### 6) Report

```python
from ml_utils import save_agent_report
save_agent_report("snowflake-connector", {
    "status": "completed",
    "account": "<account>",
    "user": "<user>",
    "role": "<role>",
    "warehouse": "<warehouse>",
    "database": "<database>",
    "schema": "<schema>",
    "connection_test": "PASSED"
})
```

Print: `Snowflake connection configured and tested. Ready to use.`
