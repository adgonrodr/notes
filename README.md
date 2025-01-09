# cell_mapping.py
"""
    Contains the mapping of logical names to cell references for Excel processing.
    
    :example: {
        "owner": "E14",
        "custodian": "E15"
    }
"""
cell_reference_dict = {
    "owner": "E14",
    "custodian": "E15"
}

    def get_cell_value(self, cell_reference):
        """
        Retrieves the value of a specific cell based on its reference (e.g., "E14").

        :param cell_reference: Cell reference in Excel (e.g., "E14")
        :return: Value of the specified cell
        """
        column = ord(cell_reference[0].upper()) - ord('A')  # Convert column letter to index
        row = int(cell_reference[1:]) - 1  # Convert row number to zero-based index
        return self.dataframe.iat[row, column]

    def create_dict(self, cell_mapping):
        """
        Creates a dictionary from an Excel file where keys are provided logical names,
        and values are the contents of specified cell references.

        :param cell_mapping: Dictionary mapping logical names to cell references
        :return: Dictionary with logical names as keys and cell values as values
        """
        result_dict = {}
        for key, cell_reference in cell_mapping.items():
            result_dict[key] = self.get_cell_value(cell_reference)
        return result_dict


    def create_dict_from_column(file_path, key_column, value_column, sheet_name=0):
    """
    Creates a dictionary from an Excel file where keys and values are based on specified columns.
    
    :param file_path: Path to the Excel file
    :param key_column: Column name to use as keys
    :param value_column: Column name to use as values
    :param sheet_name: Name or index of the sheet to read (default is the first sheet)
    :return: Dictionary with keys and values from the specified columns
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Drop rows where either key or value columns have missing data
        df.dropna(subset=[key_column, value_column], inplace=True)

        # Create dictionary
        result_dict = df.set_index(key_column)[value_column].to_dict()

        return result_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}