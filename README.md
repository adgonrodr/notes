{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "SimpleDataContractSpecification",
  "properties": {
    "dataContractSpecification": {
      "type": "string",
      "title": "DataContractSpecificationVersion",
      "enum": ["1.1.0", "0.9.3", "0.9.2", "0.9.1", "0.9.0"],
      "description": "Specifies the Data Contract Specification being used."
    },
    "id": {
      "type": "string",
      "description": "Specifies the identifier of the data contract."
    },
    "info": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The title of the data contract."
        },
        "dmg_tenant": {
          "type": "string",
          "description": "Specifies the tenant associated with the data contract."
        },
        "dmg_tla": {
          "type": "string",
          "description": "Specifies the three-letter acronym (TLA) for the data contract."
        },
        "version": {
          "type": "string",
          "description": "The version of the data contract document."
        },
        "dmg_published_schema": {
          "type": "string",
          "description": "Specifies the published schema for the data contract."
        },
        "dmg_data_product_name": {
          "type": "string",
          "description": "Specifies the data product name."
        },
        "dmg_data_product_prefix": {
          "type": "string",
          "description": "Specifies the prefix for the data product."
        },
        "owner": {
          "type": "string",
          "description": "The owner responsible for managing the data contract."
        },
        "_dmg_steward": {
          "type": "string",
          "description": "Specifies the steward for the data contract."
        },
        "dmg_custodian": {
          "type": "string",
          "description": "Specifies the custodian of the data contract."
        }
      },
      "required": [
        "title",
        "dmg_tenant",
        "dmg_tla",
        "version",
        "dmg_published_schema",
        "dmg_data_product_name",
        "dmg_data_product_prefix",
        "owner",
        "_dmg_steward",
        "dmg_custodian"
      ],
      "description": "Metadata and life cycle information about the data contract."
    }
  },
  "required": ["dataContractSpecification", "id", "info"]
}