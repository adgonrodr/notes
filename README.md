-- See only actually dropped tables, with a deadline for UNDROP
SELECT
  table_catalog,
  table_schema,
  table_name,
  created,
  dropped_on,
  data_retention_time_in_days,
  DATEADD('day', data_retention_time_in_days, dropped_on) AS undrop_deadline,
  CASE
    WHEN DATEADD('day', data_retention_time_in_days, dropped_on) > CURRENT_TIMESTAMP()
      THEN 'UNDROP still possible'
    ELSE 'Time Travel expired (Fail-safe only)'
  END AS recovery_status
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
WHERE deleted = TRUE               -- only dropped ones
  AND table_catalog = 'MYDB'       -- optional filter(s)
  AND table_schema  = 'MYSCHEMA'
ORDER BY dropped_on DESC;