from google.cloud import bigquery
import csv

# Function to read schemas from CSV file and organize by table name
def read_schemas_from_csv(csv_file_path):
    table_schemas = {}
    with open(csv_file_path, mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            table_name = row['table_name']
            if table_name not in table_schemas:
                table_schemas[table_name] = []
            field = bigquery.SchemaField(
                name=row['column_name'],
                field_type=row['data_type'],
                mode='NULLABLE' if row['is_nullable'].lower() == 'true' else 'REQUIRED'
            )
            table_schemas[table_name].append(field)
    return table_schemas

def get_bigquery_table_schema(client, dataset_id, table_id):
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    return table.schema

def report_bigquery_table_schema(client, dataset_id, table_id, new_schema):
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)

    original_schema_dict = {field.name: field for field in table.schema}
    mismatched_fields = []
    missing_fields = []

    # for new_field in new_schema:
    #     if new_field.name in original_schema_dict:
    #         original_field = original_schema_dict[new_field.name]
    #         if new_field.field_type != original_field.field_type or new_field.mode != original_field.mode:
    #             mismatched_fields.append((new_field.name, new_field.field_type, original_field.field_type, new_field.mode, original_field.mode))
    #     else:
    #         missing_fields.append(new_field.name)


    for new_field in new_schema:
        if new_field.name in original_schema_dict:
            original_field = original_schema_dict[new_field.name]
            # Only compare datatypes now
            if new_field.field_type != original_field.field_type: 
                mismatched_fields.append((new_field.name, new_field.field_type, original_field.field_type, new_field.mode, original_field.mode))

    if mismatched_fields:
        for name, new_type, original_type, new_mode, original_mode in mismatched_fields:
            print(f"csv: table {table_id}, field {name}, datatype {new_type}, mode {new_mode}")
            print(f"BQ: table {table_id}, field {name}, datatype {original_type}, mode {original_mode}")
            print("---") 

    if missing_fields:
        print(f"table {table_id}: {len(missing_fields)} fields missing: {', '.join(missing_fields)}")

def main(project_id, csv_file_path, dataset_id):
    client = bigquery.Client(project=project_id)

    # Read schemas from CSV file organized by table
    table_schemas = read_schemas_from_csv(csv_file_path)

    # Loop through each table and compare its schema
    print("Mismatched field datatypes:")
    for table_id, new_schema in table_schemas.items():
        try:
            current_schema = get_bigquery_table_schema(client, dataset_id, table_id)
            report_bigquery_table_schema(client, dataset_id, table_id, new_schema)
        except Exception as e:
            print(f"Failed to process table {table_id}: {e}")

    print("\nNumber of fields missing in BQ dataset:")
    for table_id, new_schema in table_schemas.items():
        try:
            current_schema = get_bigquery_table_schema(client, dataset_id, table_id)
            original_schema_dict = {field.name: field for field in current_schema}
            missing_fields = [field.name for field in new_schema if field.name not in original_schema_dict]
            if missing_fields:
                print(f"table {table_id}: {len(missing_fields)} fields missing: {', '.join(missing_fields)}")
        except Exception as e:
            print(f"Failed to process table {table_id}: {e}")

    print("Schema comparison complete.")

# Run the main function with parameters
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Error: Please enter the correct number of parameters: project_id, csv_file_path, dataset_id")
        sys.exit(1)

    project_id = sys.argv[1]
    csv_file_path = sys.argv[2]
    dataset_id = sys.argv[3]

    main(project_id, csv_file_path, dataset_id)