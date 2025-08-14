from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

# ---------- Configuration ----------
DATABASE_NAME = "MY_DB"
EXCLUDE_SCHEMAS = ["PUBLIC", "INFORMATION_SCHEMA"]  # add any others you want to exclude
LOOKBACK_DAYS = 30  # how far back to search query history for last DML

# ---------- Helper ----------
def _ident(name: str) -> str:
    """
    Quote a Snowflake identifier with double quotes, escaping internal quotes.
    Use for database/schema/table identifiers (not string literals).
    """
    return '"' + name.replace('"', '""') + '"'

def list_tables_and_views_with_last_dml(session: Session,
                                        database: str,
                                        exclude_schemas: list[str] | None = None,
                                        lookback_days: int = 30):
    """
    Build a Snowpark DataFrame listing all tables and views in the given database,
    along with creation_date, last_insert_date, and last_update_date.

    - creation_date: from INFORMATION_SCHEMA metadata.
    - last_insert_date / last_update_date:
        Derived from QUERY_HISTORY. Prefer ACCOUNT_USAGE (accurate via OBJECTS_MODIFIED);
        fallback to INFORMATION_SCHEMA (best-effort via DIRECT_OBJECTS_ACCESSED).

    Columns in the result:
        db, schema, entity_name, creation_date, last_insert_date, last_update_date
    """
    db_upper = database.upper()
    db_q = _ident(database)

    # Build exclusion predicate for schemas
    exclude_schemas = [s.upper() for s in (exclude_schemas or [])]
    if exclude_schemas:
        exclude_in = ", ".join(f"'{s}'" for s in exclude_schemas)
        exclude_pred = f"AND UPPER(table_schema) NOT IN ({exclude_in})"
    else:
        exclude_pred = ""

    # CTE aggregating base entities (tables + views) with creation dates
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
        {exclude_pred}
      UNION ALL
      SELECT
        table_catalog AS db,
        table_schema  AS schema,
        table_name    AS entity_name,
        created       AS creation_date,
        'VIEW'        AS entity_type
      FROM {db_q}.INFORMATION_SCHEMA.VIEWS
      WHERE 1=1
        {exclude_pred}
    )
    """

    # Preferred approach: ACCOUNT_USAGE with OBJECTS_MODIFIED (more accurate)
    account_usage_sql = f"""
    {entities_sql},
    q AS (
      SELECT
        h.DATABASE_NAME                                AS db,
        h.SCHEMA_NAME                                  AS schema,
        UPPER(m.value:"objectName"::string)            AS entity_name_u,
        h.QUERY_TYPE                                   AS query_type,
        h.START_TIME                                   AS start_time
      FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY h,
           LATERAL FLATTEN(input => h.OBJECTS_MODIFIED) m
      WHERE h.START_TIME >= DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP())
        AND h.DATABASE_NAME = '{db_upper}'
        AND h.QUERY_TYPE IN ('INSERT','UPDATE','MERGE','COPY')
        -- Optional: ignore excluded schemas if present in history rows
        {"AND UPPER(h.SCHEMA_NAME) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")" if exclude_schemas else ""}
    ),
    last_insert AS (
      SELECT db, schema, entity_name_u, MAX(start_time) AS last_insert_date
      FROM q
      WHERE query_type IN ('INSERT','MERGE','COPY')
      GROUP BY 1,2,3
    ),
    last_update AS (
      SELECT db, schema, entity_name_u, MAX(start_time) AS last_update_date
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
      ON UPPER(e.db)=li.db AND UPPER(e.schema)=li.schema AND UPPER(e.entity_name)=li.entity_name_u
    LEFT JOIN last_update lu
      ON UPPER(e.db)=lu.db AND UPPER(e.schema)=lu.schema AND UPPER(e.entity_name)=lu.entity_name_u
    ORDER BY e.schema, e.entity_name
    """

    # Fallback: INFORMATION_SCHEMA.QUERY_HISTORY (uses DIRECT_OBJECTS_ACCESSED; best-effort)
    info_schema_sql = f"""
    {entities_sql},
    qh AS (
      SELECT * FROM TABLE(
        {db_q}.INFORMATION_SCHEMA.QUERY_HISTORY(
          END_TIME_RANGE_START => DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP()),
          RESULT_LIMIT => 100000
        )
      )
      WHERE query_type IN ('INSERT','UPDATE','MERGE','COPY')
        AND DATABASE_NAME = '{db_upper}'
        {"AND UPPER(SCHEMA_NAME) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")" if exclude_schemas else ""}
    ),
    q AS (
      SELECT
        qh.DATABASE_NAME AS db,
        qh.SCHEMA_NAME   AS schema,
        UPPER(obj.value:"objectName"::string) AS entity_name_u,
        qh.QUERY_TYPE    AS query_type,
        qh.START_TIME    AS start_time
      FROM qh,
           LATERAL FLATTEN(input => qh.DIRECT_OBJECTS_ACCESSED) obj
      WHERE obj.value:"objectDomain"::string IN ('Table')
    ),
    last_insert AS (
      SELECT db, schema, entity_name_u, MAX(start_time) AS last_insert_date
      FROM q
      WHERE query_type IN ('INSERT','MERGE','COPY')
      GROUP BY 1,2,3
    ),
    last_update AS (
      SELECT db, schema, entity_name_u, MAX(start_time) AS last_update_date
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
      ON UPPER(e.db)=li.db AND UPPER(e.schema)=li.schema AND UPPER(e.entity_name)=li.entity_name_u
    LEFT JOIN last_update lu
      ON UPPER(e.db)=lu.db AND UPPER(e.schema)=lu.schema AND UPPER(e.entity_name)=lu.entity_name_u
    ORDER BY e.schema, e.entity_name
    """

    # Try ACCOUNT_USAGE first (most accurate). If permission denied, fall back.
    try:
        df = session.sql(account_usage_sql)
        # Touch the plan to verify we can read; collect 1 row
        df.limit(1).collect()
        return df
    except SnowparkSQLException:
        df_fb = session.sql(info_schema_sql)
        df_fb.limit(1).collect()
        return df_fb

# ---------- Example usage ----------
# session = Session.builder.configs({...}).create()
# result_df = list_tables_and_views_with_last_dml(session,
#                                                 database=DATABASE_NAME,
#                                                 exclude_schemas=EXCLUDE_SCHEMAS,
#                                                 lookback_days=LOOKBACK_DAYS)
# result_df.show()           # Show in Snowpark
# pdf = result_df.to_pandas()  # Convert to pandas if needed