WITH tag_data AS (
    SELECT 
        object_name, 
        column_name, 
        tag_name, 
        tag_value 
    FROM 
        TABLE(D_SANDBOX1.information_schema.tag_references_all_columns('D_SANDBOX1.PUBLISHED_SANDBOX1.EXCHANGE_RATES', 'TABLE')) 
    WHERE 
        level = 'COLUMN'
),
column_data AS (
    SELECT 
        table_name, 
        column_name, 
        data_type 
    FROM 
        D_SANDBOX1.information_schema.columns
    WHERE 
        table_schema = 'PUBLISHED_SANDBOX1' 
        AND table_name = 'EXCHANGE_RATES'
)
SELECT * 
FROM (
    SELECT 
        td.object_name, 
        td.column_name, 
        cd.data_type, 
        td.tag_name, 
        td.tag_value
    FROM 
        tag_data td
    JOIN 
        column_data cd 
    ON 
        td.object_name = cd.table_name 
        AND td.column_name = cd.column_name
) 
PIVOT (
    MAX(tag_value) 
    FOR tag_name IN ('DMG_DP_ATTRIBUTE_DISPLAY_NAME')
) P;