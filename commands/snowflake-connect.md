# /snowflake-connect

Setup and test Snowflake connection. Configures credentials, tests connectivity, stores project overrides.

## Usage

```
/snowflake-connect [--check]
```

- No args: full interactive setup
- `--check`: quick connection test only

## Workflow

### 1) Check existing connection

Check if `~/.snowflake/connections.toml` exists.

If exists and `--check` flag:
- Test with `SELECT CURRENT_VERSION()`
- Report: account, user, role, warehouse, database, schema
- Exit

### 2) Interactive setup (if no connections.toml)

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

Write `.claude/snowflake-config.json`:

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
