import unittest
from unittest.mock import patch, mock_open
import os
import jsonschema
import logging
import jhashcode

# Import the functions from the main module
from main_module import (
    load_cols_definitions, generate_kafka_valid_name, validate_json,
    validate_table, validate_entity_def, validate_tasks_statement, validate_view,
    validate_stage, validate_file_format, validate_stream, validate_proc,
    validate_kafka, append_tenant_schema, generate_data_contract, init_parser,
    init_logger, init_folders
)

class TestMainModule(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="column_name,column_type,nullable\nname,VARCHAR,Y\n")
    def test_load_cols_definitions(self, mock_file):
        resources_dir = "resources"
        columns_filename = "columns.csv"
        result = load_cols_definitions(resources_dir, columns_filename)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["column_name"], "name")

    def test_generate_kafka_valid_name(self):
        self.assertEqual(generate_kafka_valid_name("validName"), "validName")
        self.assertNotEqual(generate_kafka_valid_name("Invalid Name"), "Invalid Name")
    
    def test_validate_json(self):
        valid_json = {"name": "example"}
        schema_json = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(schema_json))):
            validate_json(valid_json, "schema.json")
        
        invalid_json = {"name": 123}
        with patch("builtins.open", mock_open(read_data=json.dumps(schema_json))):
            with self.assertRaises(ValueError):
                validate_json(invalid_json, "schema.json")
    
    @patch("main_module.load_cols_definitions")
    def test_validate_table(self, mock_load_cols_definitions):
        resources_dir = "resources"
        table = {
            "schema": "valid_schema",
            "name": "example_table",
            "columns": ["columns.csv"]
        }
        schemas = ["valid_schema"]
        validate_table(resources_dir, table, schemas)
        mock_load_cols_definitions.assert_called_once_with(resources_dir, "columns.csv")
    
    @patch("main_module.load_cols_definitions")
    def test_validate_entity_def(self, mock_load_cols_definitions):
        resources_dir = "resources"
        entity = {
            "schema": "valid_schema",
            "name": "example_entity",
            "columns": ["columns.csv"]
        }
        validate_entity_def(resources_dir, entity)
        mock_load_cols_definitions.assert_called_once_with(resources_dir, "columns.csv")

    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM example;")
    def test_validate_tasks_statement(self, mock_file):
        tasks_config = {
            "tasks": [
                {"sql_file": "task.sql", "log_level": "info"}
            ]
        }
        resources_dir = "resources"
        validate_tasks_statement(tasks_config, resources_dir)
        mock_file.assert_called_once_with("resources/templates/task_sql/task.sql", "r")

    def test_validate_view(self):
        view = {
            "schema": "valid_schema",
            "name": "example_view",
            "columns": ["columns.csv"]
        }
        schemas = ["valid_schema"]
        validate_view(view, schemas)

    def test_validate_stage(self):
        stage = {
            "schema": "valid_schema",
            "name": "example_stage"
        }
        schemas = ["valid_schema"]
        validate_stage(stage, schemas)

    def test_validate_file_format(self):
        file_format = {
            "schema": "valid_schema",
            "name": "example_file_format"
        }
        schemas = ["valid_schema"]
        validate_file_format(file_format, schemas)

    def test_validate_stream(self):
        stream = {
            "schema": "valid_schema",
            "name": "example_stream"
        }
        schemas = ["valid_schema"]
        validate_stream(stream, schemas)

    def test_validate_proc(self):
        proc = {
            "schema": "valid_schema",
            "name": "example_proc",
            "columns": ["columns.csv"]
        }
        schemas = ["valid_schema"]
        validate_proc(proc, schemas)

    def test_validate_kafka(self):
        kafka = {
            "snowflake_schema": "valid_schema",
            "name": "example_kafka"
        }
        schemas = ["valid_schema"]
        validate_kafka(kafka, schemas)

    def test_append_tenant_schema(self):
        schema_list = []
        schema_name = "example_schema"
        schema_description = "Example description"
        append_tenant_schema(schema_list, schema_name, schema_description)
        self.assertEqual(len(schema_list), 1)
        self.assertEqual(schema_list[0]["name"], schema_name)
        self.assertEqual(schema_list[0]["description"], schema_description)

    @patch("main_module.generate_data_contract")
    def test_generate_data_contract(self, mock_generate_data_contract):
        resources_dir = "resources"
        output_dir = "output"
        env = "test"
        generate_data_contract(resources_dir, output_dir, env)
        mock_generate_data_contract.assert_called_once_with(resources_dir, output_dir, env)

    def test_init_parser(self):
        parser = init_parser()
        self.assertIsNotNone(parser)
        args = parser.parse_args(["--resources-dir", "resources", "--environment", "test"])
        self.assertEqual(args.resources_dir, "resources")
        self.assertEqual(args.environment, "test")

    @patch("main_module.logging")
    def test_init_logger(self, mock_logging):
        init_logger("info")
        mock_logging.setLevel.assert_called_once_with(logging.INFO)

    @patch("os.path.isdir")
    @patch("os.makedirs")
    def test_init_folders(self, mock_makedirs, mock_isdir):
        mock_isdir.return_value = True
        resources_dir = "resources"
        output_dir = "output"
        init_folders(resources_dir, output_dir)
        mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)

if __name__ == "__main__":
    unittest.main()
