"""
Snowflake utilities for the ml-automation-snowflake extension plugin.

Requires ml_utils.py from the ml-automation core plugin to be present
in the same directory (copied via Stage 0 of Snowflake commands).
"""

import os
import json
from pathlib import Path

from ml_utils import save_agent_report  # noqa: F401 — re-exported for extension commands


# --- Connection Management ---

CONNECTIONS_TOML_PATH = Path.home() / ".snowflake" / "connections.toml"
PROJECT_CONFIG_PATH = Path(".claude") / "snowflake-config.json"


def get_snowflake_connection(connection_name="default"):
    """Get Snowflake connection using connections.toml or project config.

    Args:
        connection_name: name of the connection in connections.toml

    Returns:
        snowflake.connector.Connection object
    """
    try:
        from snowflake.connector import connect
        conn = connect(connection_name=connection_name)
        return conn
    except ImportError:
        raise ImportError(
            "snowflake-connector-python is required. "
            "Install with: pip install snowflake-connector-python"
        )


def get_project_config():
    """Load project-specific Snowflake config from .claude/snowflake-config.json.

    Returns:
        dict with connection overrides, or empty dict if no config
    """
    if PROJECT_CONFIG_PATH.exists():
        with open(PROJECT_CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_project_config(config):
    """Save project-specific Snowflake config.

    Args:
        config: dict with connection_name, database, schema, warehouse, role
    """
    PROJECT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def test_connection(connection=None):
    """Test Snowflake connection and return version info.

    Returns:
        dict with version, account, role, warehouse, or error message
    """
    try:
        conn = connection or get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), "
            "CURRENT_ROLE(), CURRENT_WAREHOUSE()"
        )
        row = cursor.fetchone()
        if connection is None:
            conn.close()
        return {
            "status": "connected",
            "version": row[0],
            "account": row[1],
            "role": row[2],
            "warehouse": row[3],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Query Execution ---

def execute_query(query, connection=None):
    """Execute a Snowflake SQL query and return results as list of dicts.

    Args:
        query: SQL query string
        connection: optional existing connection (creates new if None)

    Returns:
        list of dicts (one per row) with column names as keys
    """
    conn = connection or get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    if connection is None:
        conn.close()
    return [dict(zip(columns, row)) for row in rows]


# --- Data Loading ---

def load_from_snowflake(query_or_table, connection=None):
    """Load data from Snowflake into a pandas DataFrame.

    Args:
        query_or_table: SQL query or table name
        connection: optional existing connection

    Returns:
        pandas DataFrame
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for load_from_snowflake")

    conn = connection or get_snowflake_connection()
    cursor = conn.cursor()

    # Detect if input is a table name (no spaces/keywords) or a query
    if " " not in query_or_table.strip():
        query = f"SELECT * FROM {query_or_table}"
    else:
        query = query_or_table

    cursor.execute(query)
    df = cursor.fetch_pandas_all()
    if connection is None:
        conn.close()
    return df


def write_to_snowflake(df, table_name, database=None, schema=None,
                       mode="append", connection=None):
    """Write a pandas DataFrame to a Snowflake table.

    Args:
        df: pandas DataFrame
        table_name: target table name
        database: optional database override
        schema: optional schema override
        mode: 'append' or 'overwrite'
        connection: optional existing connection
    """
    from snowflake.connector.pandas_tools import write_pandas

    conn = connection or get_snowflake_connection()
    config = get_project_config()

    db = database or config.get("database")
    sch = schema or config.get("schema", "PUBLIC")

    overwrite = mode == "overwrite"
    write_pandas(conn, df, table_name, database=db, schema=sch,
                 overwrite=overwrite, auto_create_table=True)

    if connection is None:
        conn.close()


# --- Snowpark Session ---

def get_snowpark_session(connection_name="default"):
    """Create a Snowpark session for ML operations.

    Returns:
        snowflake.snowpark.Session object
    """
    try:
        from snowflake.snowpark import Session
        session = Session.builder.config("connection_name", connection_name).create()
        return session
    except ImportError:
        raise ImportError(
            "snowflake-snowpark-python is required. "
            "Install with: pip install snowflake-snowpark-python"
        )


# --- Relevance Detection ---

SNOWFLAKE_INDICATORS = {
    "connections.toml",
    "snowflake-connector-python",
    "snowflake-snowpark-python",
    "snowpark",
    "snowflake.connector",
    "snowflake.snowpark",
    "SNOWFLAKE://",
}


def detect_snowflake_relevance(project_path="."):
    """Check if project has Snowflake indicators for relevance gating.

    Checks: connections.toml, .sql files, snowflake imports in requirements,
    Snowpark code patterns, SNOWFLAKE:// URIs.

    Returns:
        dict with 'is_snowflake': bool, 'indicators': list of found indicators
    """
    indicators = []
    project = Path(project_path)

    # Check global connections.toml
    if CONNECTIONS_TOML_PATH.exists():
        indicators.append("~/.snowflake/connections.toml exists")

    # Check project config
    if (project / ".claude" / "snowflake-config.json").exists():
        indicators.append(".claude/snowflake-config.json exists")

    # Check for .sql files
    sql_files = list(project.glob("**/*.sql"))
    if sql_files:
        indicators.append(f"{len(sql_files)} .sql files found")

    # Check requirements for snowflake packages
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py"]:
        req_path = project / req_file
        if req_path.exists():
            content = req_path.read_text().lower()
            for pkg in ["snowflake-connector-python", "snowflake-snowpark-python",
                        "snowflake-ml-python"]:
                if pkg in content:
                    indicators.append(f"{pkg} in {req_file}")

    return {
        "is_snowflake": len(indicators) > 0,
        "indicators": indicators,
    }


# --- Metadata Queries ---

def get_snowflake_metadata(connection=None):
    """Query INFORMATION_SCHEMA for databases, schemas, tables, columns.

    Returns:
        dict with databases, schemas, tables lists
    """
    conn = connection or get_snowflake_connection()
    cursor = conn.cursor()

    # Get databases
    cursor.execute("SHOW DATABASES")
    databases = [row[1] for row in cursor.fetchall()]

    # Get schemas in current database
    cursor.execute("SHOW SCHEMAS")
    schemas = [row[1] for row in cursor.fetchall()]

    # Get tables in current schema
    cursor.execute("SHOW TABLES")
    tables = [{"name": row[1], "database": row[2], "schema": row[3],
               "rows": row[5]} for row in cursor.fetchall()]

    if connection is None:
        conn.close()

    return {
        "databases": databases,
        "schemas": schemas,
        "tables": tables,
    }


# --- Model Registry ---

def register_model_to_registry(session, model, model_name, version=None,
                                metrics=None):
    """Register a trained model in Snowflake Model Registry.

    Args:
        session: Snowpark Session
        model: trained model object (sklearn-compatible)
        model_name: name for the registry
        version: version string (auto-generated if None)
        metrics: dict of metric_name: value

    Returns:
        ModelVersion object from registry
    """
    from snowflake.ml.registry import Registry

    reg = Registry(session)
    version_name = version or "v1"
    mv = reg.log_model(
        model,
        model_name=model_name,
        version_name=version_name,
        metrics=metrics or {},
    )
    return mv
