# spark-snowflake — Cortex Code Extension

Snowflake development and ML automation. SQL authoring, Snowpark pipelines, Snowpark ML training, model registry, and Streamlit in Snowflake deployment. Requires spark-core installed.

## Connection

Uses `~/.snowflake/connections.toml` for authentication — the same file Cortex Code CLI uses. No additional setup needed when running inside Cortex Code.

## Available Agents

| Agent | When to use |
|---|---|
| `snowflake-data-engineer` | User wants to write SQL, design tables, build Snowpark pipelines, create stages/streams/tasks, or optimize queries |
| `snowflake-ml-engineer` | User wants to train a model in Snowpark ML, use FORECAST or ANOMALY_DETECTION, or register a model in the Snowflake Model Registry |
| `snowflake-reviewer` | User wants SQL quality review, cost optimization, or Snowflake best practices feedback |
| `snowflake-deployer` | User wants to deploy to Model Registry, create Streamlit in Snowflake, or build a stored procedure |
| `snowflake-connector` | User wants to set up a Snowflake connection, load data, or configure credentials |

## Available Skills

| Skill | Trigger |
|---|---|
| `/snowflake-connect` | "connect to Snowflake", "set up Snowflake connection", "test my Snowflake credentials" |
| `/snowflake-coldstart` | "full Snowflake ML workflow", "end to end on my Snowflake table", "snowflake coldstart" |
| `/snowflake-sql` | "write SQL for Snowflake", "natural language to SQL", "generate a Snowflake query" |
| `/snowflake-pipeline` | "build a Snowpark pipeline", "transform data with Snowpark", "create a data pipeline in Snowflake" |
| `/snowflake-train` | "train a model on Snowflake data", "use Snowpark ML", "forecast with Snowflake", "anomaly detection in Snowflake" |
| `/snowflake-deploy` | "deploy to Snowflake Model Registry", "create Streamlit in Snowflake", "deploy as stored procedure" |
| `/snowflake-migrate` | "migrate pandas code to Snowpark", "convert sklearn to Snowpark ML", "port this to Snowflake" |
| `/snowflake-status` | "show Snowflake resources", "list my Snowflake models", "check warehouse usage" |

## Routing

- SQL development, table design, Snowpark transformations → `snowflake-data-engineer`
- Model training, FORECAST, ANOMALY_DETECTION, Model Registry → `snowflake-ml-engineer`
- SQL review, cost, performance → `snowflake-reviewer`
- Streamlit in Snowflake, stored procedures, deployment → `snowflake-deployer`
- Connection setup, data loading → `snowflake-connector`
- Fallback → spark-core orchestrator
