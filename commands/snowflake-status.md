# /snowflake-status

Check Snowflake resources and usage.

## Usage

```
/snowflake-status [--detailed]
```

### Stage 0: Ensure Snowflake Connection

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `snowflake_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/snowflake_utils.py`
3. Run `/snowflake-connect --check` to verify connection is active
4. If connection fails, stop and tell user to run `/snowflake-connect`

### 1) Query Snowflake metadata

Execute these queries:

**Warehouses:**
```sql
SHOW WAREHOUSES;
```

**Deployed Models (Model Registry):**
```sql
SELECT * FROM INFORMATION_SCHEMA.ML_MODEL_VERSIONS
ORDER BY CREATION_TIME DESC LIMIT 10;
```

**Streamlit Apps:**
```sql
SHOW STREAMLITS;
```

**Stored Procedures:**
```sql
SHOW PROCEDURES;
```

**Recent Queries (last 24h):**
```sql
SELECT QUERY_ID, QUERY_TEXT, EXECUTION_STATUS, TOTAL_ELAPSED_TIME
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(
  DATEADD('hours', -24, CURRENT_TIMESTAMP()), CURRENT_TIMESTAMP()))
ORDER BY START_TIME DESC LIMIT 20;
```

### 2) Format output

Display as tables:

```
## Warehouses
| Name | Size | State | Auto-Suspend |
|---|---|---|---|

## Deployed Models
| Model | Version | Created | Metrics |
|---|---|---|---|

## Streamlit Apps
| Name | URL | Status |
|---|---|---|

## Stored Procedures
| Name | Schema | Language |
|---|---|---|

## Recent Queries (24h)
| ID | Status | Duration | Query (truncated) |
|---|---|---|---|
```

### 3) Report

Write status report via report bus.
