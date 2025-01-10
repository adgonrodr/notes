def extract_entities_from_dataframe(df, mapping):
    """
    Extract entities and their attributes from a DataFrame based on a mapping dictionary.
    
    Args:
        df (pd.DataFrame): The input dataframe.
        mapping (dict): A dictionary where keys are field names and values are column indices.
        
    Returns:
        list: A list of dictionaries representing entities and their attributes.
    """
    entities = {}
    
    for _, row in df.iterrows():
        # Extract relevant fields based on the mapping
        data_entity = row[mapping["data_entity"]]
        data_attribute = row[mapping["data_attribute"]]
        data_type = row[mapping["data_type"]]
        pii = row[mapping["PII"]]
        
        # If PII is a string like 'True', 'False', convert to boolean
        if isinstance(pii, str):
            pii = pii.lower() in ['true', 'yes', '1']
        
        # Initialize the entity if not already done
        if data_entity not in entities:
            entities[data_entity] = {"data_entity": data_entity, "attributes": []}
        
        # Append the attribute details to the entity's attributes list
        entities[data_entity]["attributes"].append({
            "data_attribute": data_attribute,
            "data_type": data_type,
            "PII": pii
        })
    
    # Convert the entities dictionary to a list
    return list(entities.values())

def excel_column_to_index(column_label):
        """
        Converts an Excel-style column label (e.g., 'A', 'AA') to a zero-based index.
        """
        column_index = 0
        for char in column_label:
            column_index = column_index * 26 + (ord(char.upper()) - ord('A') + 1)
        return column_index - 1  # Convert to zero-based index