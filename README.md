def extract_entities_from_data_contract(data_contract_path):
    """
    Extracts entities from a data contract file conforming to the Data Contract CLI specification.

    :param data_contract_path: Path to the JSON file containing the data contract.
    :return: A list of entities extracted from the data contract.
    """
    try:
        with open(data_contract_path, 'r') as file:
            data_contract = json.load(file)
        
        # Extract entities based on the specification
        entities = data_contract.get("entities", [])
        extracted_entities = []

        for entity in entities:
            entity_name = entity.get("name")
            attributes = entity.get("attributes", [])
            extracted_attributes = []

            for attribute in attributes:
                extracted_attributes.append({
                    "name": attribute.get("name"),
                    "type": attribute.get("type"),
                    "nullable": attribute.get("nullable", True),
                    "sensitive": attribute.get("sensitive", False)
                })

            extracted_entities.append({
                "entity_name": entity_name,
                "attributes": extracted_attributes
            })

        return extracted_entities

    except FileNotFoundError:
        print(f"Error: File not found at {data_contract_path}")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the data contract file.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return []