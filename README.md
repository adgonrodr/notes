# Prepare CSV data
rows = []
for table in tables:
    for column in table["columns"]:
        # Flatten the table and column details
        row = {
            "table_name": table["table_name"],
            "schema": table["schema"],
            "column_name": column["column_name"],
            "data_type": column["data_type"],
        }
        # Add attributes as separate columns
        for key, value in column["attributes"].items():
            row[key] = value
        rows.append(row)

# Determine all possible attribute keys dynamically
all_keys = set()
for row in rows:
    all_keys.update(row.keys())
all_keys = sorted(all_keys)  # Sort for consistent column order

# Write to CSV
output_file = "tables_columns.csv"
with open(output_file, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV file '{output_file}' generated successfully.")