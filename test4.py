from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

# ---------- Configuration (edit as needed) ----------
DATABASE_NAME = "MY_DB"
EXCLUDE_SCHEMAS = ["PUBLIC", "INFORMATION_SCHEMA"]  # schemas to skip
LOOKBACK_DAYS = 30  # set < 0 to remove the time filter altogether

def _ident(name: str) -> str:
    """Safely double-quote a Snowflake identifier (for DB/SCHEMA names in SQL)."""
    return '"' + name.replace('"', '""') + '"'

def list_tables_views_last_dml(
    session: Session,
    database: str = DATABASE_NAME,
    exclude_schemas: list[str] | None = None,
    lookback_days: int = LOOKBACK_DAYS,
):
    """
    Returns a Snowpark DataFrame with:
      db, schema, entity_name, creation_date, last_insert_date, last_update_date

    Logic:
      - Get all tables + views from INFORMATION_SCHEMA (with creation_date).
      - Preferred path: ACCOUNT_USAGE.ACCESS_HISTORY (flatten objects_modified) joined to
        ACCOUNT_USAGE.QUERY_HISTORY to classify DML. This is accurate and avoids false positives.
      - Fallback path: INFORMATION_SCHEMA.QUERY_HISTORY table function (best-effort).
    Improvements:
      - If lookback_days < 0, no time filter is applied (scan full retention).
      - Quote stripping from objectName to ensure joins match metadata (handles "DB"."SCHEMA"."TABLE").
    """
    db_upper = database.upper()
    db_q = _ident(database)

    exclude_schemas = [s.upper() for s in (exclude_schemas or [])]
    exclude_entities_pred = (
        "AND UPPER(table_schema) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")"
        if exclude_schemas else ""
    )
    exclude_hist_pred = (
        "AND UPPER(schema) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")"
        if exclude_schemas else ""
    )

    # Time filter pieces (removed entirely if lookback_days < 0)
    time_filter_ah = (
        "" if lookback_days is None or lookback_days < 0
        else f"AND ah.query_start_time >= DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP())"
    )
    # Build the argument list for the table function dynamically
    if lookback_days is None or lookback_days < 0:
        qh_fn_args = "RESULT_LIMIT => 100000"
    else:
        qh_fn_args = (
            f"END_TIME_RANGE_START => DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP()), "
            "RESULT_LIMIT => 100000"
        )

    # Base entities (tables + views) with creation dates
    entities_sql = f"""
    WITH entities AS (
      SELECT
        table_catalog AS db,
        table_schema  AS schema,
        table_name    AS entity_name,
        created       AS creation_date,
        'TABLE'       AS entity_type
      FROM {db_q}.INFORMATION_SCHEMA.TABLES
      WHERE table_type = 'BASE TABLE'
        {exclude_entities_pred}
      UNION ALL
      SELECT
        table_catalog AS db,
        table_schema  AS schema,
        table_name    AS entity_name,
        created       AS creation_date,
        'VIEW'        AS entity_type
      FROM {db_q}.INFORMATION_SCHEMA.VIEWS
      WHERE 1=1
        {exclude_entities_pred}
    )
    """

    # -------- Preferred: ACCESS_HISTORY + QUERY_HISTORY (accurate) --------
    # Strip quotes from each part of objectName, then UPPER for consistent joins.
    account_usage_sql = f"""
    {entities_sql},
    ah_flat AS (
      SELECT
        REPLACE(SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 1), '"', '') AS db,
        REPLACE(SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 2), '"', '') AS schema,
        REPLACE(SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 3), '"', '') AS entity_name,
        ah.query_id,
        ah.query_start_time AS start_time
      FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah,
           LATERAL FLATTEN(input => ah.OBJECTS_MODIFIED) m
      WHERE SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 1) = '{db_upper}'
        {time_filter_ah}
    ),
    q AS (
      SELECT
        f.db, f.schema, f.entity_name,
        qh.QUERY_TYPE AS query_type,
        f.start_time
      FROM ah_flat f
      JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
        ON qh.query_id = f.query_id
      WHERE qh.QUERY_TYPE IN ('INSERT','UPDATE','MERGE','COPY')
        {exclude_hist_pred}
    ),
    last_insert AS (
      SELECT db, schema, entity_name, MAX(start_time) AS last_insert_date
      FROM q
      WHERE query_type IN ('INSERT','MERGE','COPY')
      GROUP BY 1,2,3
    ),
    last_update AS (
      SELECT db, schema, entity_name, MAX(start_time) AS last_update_date
      FROM q
      WHERE query_type IN ('UPDATE','MERGE')
      GROUP BY 1,2,3
    )
    SELECT
      e.db,
      e.schema,
      e.entity_name,
      e.creation_date,
      li.last_insert_date,
      lu.last_update_date
    FROM entities e
    LEFT JOIN last_insert li
      ON UPPER(e.db)=li.db AND UPPER(e.schema)=li.schema AND UPPER(e.entity_name)=li.entity_name
    LEFT JOIN last_update lu
      ON UPPER(e.db)=lu.db AND UPPER(e.schema)=lu.schema AND UPPER(e.entity_name)=lu.entity_name
    ORDER BY e.schema, e.entity_name
    """

    # -------- Fallback: INFORMATION_SCHEMA.QUERY_HISTORY (best-effort) --------
    # Strip quotes from objectName parts here as well.
    info_schema_sql = f"""
    {entities_sql},
    qh AS (
      SELECT * FROM TABLE(
        {db_q}.INFORMATION_SCHEMA.QUERY_HISTORY({qh_fn_args})
      )
      WHERE query_type IN ('INSERT','UPDATE','MERGE','COPY')
        AND DATABASE_NAME = '{db_upper}'
        {("AND UPPER(SCHEMA_NAME) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")") if exclude_schemas else ""}
    ),
    q AS (
      SELECT
        REPLACE(SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 1), '"', '') AS db,
        REPLACE(SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 2), '"', '') AS schema,
        REPLACE(SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 3), '"', '') AS entity_name,
        qh.QUERY_TYPE AS query_type,
        qh.START_TIME AS start_time
      FROM qh,
           LATERAL FLATTEN(input => qh.DIRECT_OBJECTS_ACCESSED) obj
      WHERE obj.value:"objectDomain"::string IN ('Table')
    ),
    last_insert AS (
      SELECT db, schema, entity_name, MAX(start_time) AS last_insert_date
      FROM q
      WHERE query_type IN ('INSERT','MERGE','COPY')
      GROUP BY 1,2,3
    ),
    last_update AS (
      SELECT db, schema, entity_name, MAX(start_time) AS last_update_date
      FROM q
      WHERE query_type IN ('UPDATE','MERGE')
      GROUP BY 1,2,3
    )
    SELECT
      e.db,
      e.schema,
      e.entity_name,
      e.creation_date,
      li.last_insert_date,
      lu.last_update_date
    FROM entities e
    LEFT JOIN last_insert li
      ON UPPER(e.db)=li.db AND UPPER(e.schema)=li.schema AND UPPER(e.entity_name)=li.entity_name
    LEFT JOIN last_update lu
      ON UPPER(e.db)=lu.db AND UPPER(e.schema)=lu.schema AND UPPER(e.entity_name)=lu.entity_name
    ORDER BY e.schema, e.entity_name
    """

    # Try ACCESS_HISTORY first; fall back if not permitted
    try:
        df = session.sql(account_usage_sql)
        df.limit(1).collect()  # validate access
        return df
    except SnowparkSQLException:
        df_fb = session.sql(info_schema_sql)
        df_fb.limit(1).collect()
        return df_fb

# ---------- Example usage ----------
# session = Session.builder.configs({...}).create()
# df_result = list_tables_views_last_dml(
#     session,
#     database=DATABASE_NAME,
#     exclude_schemas=EXCLUDE_SCHEMAS,
#     lookback_days=-1,  # < 0 disables time filter
# )
# df_result.show()