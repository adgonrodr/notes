from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

# ---------------- Configuration ----------------
DATABASE_NAME = "MY_DB"
EXCLUDE_SCHEMAS = ["PUBLIC", "INFORMATION_SCHEMA"]   # add others to exclude
LOOKBACK_DAYS = 30                                    # how far back to scan for DML

# ---------------- Helper ----------------
def _ident(name: str) -> str:
    """Double-quote a Snowflake identifier safely."""
    return '"' + name.replace('"', '""') + '"'

def list_tables_views_last_dml(session: Session,
                               database: str = DATABASE_NAME,
                               exclude_schemas: list[str] | None = None,
                               lookback_days: int = LOOKBACK_DAYS):
    """
    Build a Snowpark DataFrame listing all tables and views in `database`,
    with creation_date, last_insert_date, last_update_date.

    Preferred path:
      - SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY (flatten objects_modified)
      - Join to SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY on query_id to get query_type
    Fallback:
      - INFORMATION_SCHEMA.QUERY_HISTORY table function (best-effort via DIRECT_OBJECTS_ACCESSED)
    """
    db_upper = database.upper()
    db_q = _ident(database)
    exclude_schemas = [s.upper() for s in (exclude_schemas or [])]

    exclude_pred_entities = ""
    if exclude_schemas:
        exclude_pred_entities = "AND UPPER(table_schema) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")"

    exclude_pred_hist = ""
    if exclude_schemas:
        exclude_pred_hist = "AND UPPER(schema) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")"

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
        {exclude_pred_entities}
      UNION ALL
      SELECT
        table_catalog AS db,
        table_schema  AS schema,
        table_name    AS entity_name,
        created       AS creation_date,
        'VIEW'        AS entity_type
      FROM {db_q}.INFORMATION_SCHEMA.VIEWS
      WHERE 1=1
        {exclude_pred_entities}
    )
    """

    # ---------- Preferred: ACCESS_HISTORY + QUERY_HISTORY ----------
    # ACCESS_HISTORY.objects_modified contains fully-qualified object names (DB.SCHEMA.OBJECT).
    # We parse them and then join to QUERY_HISTORY to classify DML types.
    account_usage_sql = f"""
    {entities_sql},
    ah_flat AS (
      SELECT
        SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 1) AS db,
        SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 2) AS schema,
        SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 3) AS entity_name,
        ah.query_id,
        ah.query_start_time AS start_time
      FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah,
           LATERAL FLATTEN(input => ah.OBJECTS_MODIFIED) m
      WHERE ah.query_start_time >= DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP())
        AND SPLIT_PART(UPPER(m.value:"objectName"::string), '.', 1) = '{db_upper}'
    ),
    q AS (
      SELECT
        f.db, f.schema, f.entity_name,
        qh.query_type,
        f.start_time
      FROM ah_flat f
      JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
        ON qh.query_id = f.query_id
      WHERE qh.query_type IN ('INSERT','UPDATE','MERGE','COPY')
        {("AND UPPER(f.schema) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")") if exclude_schemas else ""}
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

    # ---------- Fallback: INFORMATION_SCHEMA.QUERY_HISTORY ----------
    # Best-effort using DIRECT_OBJECTS_ACCESSED (7-day window; may not perfectly map object modified).
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
        {("AND UPPER(SCHEMA_NAME) NOT IN (" + ", ".join(f"'{s}'" for s in exclude_schemas) + ")") if exclude_schemas else ""}
    ),
    q AS (
      SELECT
        SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 1) AS db,
        SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 2) AS schema,
        SPLIT_PART(UPPER(obj.value:"objectName"::string), '.', 3) AS entity_name,
        qh.QUERY_TYPE                                    AS query_type,
        qh.START_TIME                                    AS start_time
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

    # Try ACCESS_HISTORY path first; on permission errors, fall back to INFORMATION_SCHEMA
    try:
        df = session.sql(account_usage_sql)
        df.limit(1).collect()  # validate access
        return df
    except SnowparkSQLException:
        df_fb = session.sql(info_schema_sql)
        df_fb.limit(1).collect()
        return df_fb

# -------------- Example usage --------------
# session = Session.builder.configs({...}).create()
# result_df = list_tables_views_last_dml(session,
#                                        database=DATABASE_NAME,
#                                        exclude_schemas=EXCLUDE_SCHEMAS,
#                                        lookback_days=LOOKBACK_DAYS)
# result_df.show()
# pdf = result_df.to_pandas()