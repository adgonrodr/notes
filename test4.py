def extract_field(yaml_content: Union[str, dict], path: str) -> Any:
    """
    Extracts a nested field from YAML content using a dot-delimited path.
    
    :param yaml_content: Either a YAML string or a pre-loaded dict.
    :param path: Dot-delimited path to the field, e.g. "info.name" or "items.0.title".
    :return: The value at that path.
    :raises KeyError: if any part of the path is missing.
    :raises IndexError: if a list index is out of range.
    """
    # Load YAML if given as string
    if isinstance(yaml_content, str):
        data = yaml.safe_load(yaml_content)
    else:
        data = yaml_content

    current = data
    for part in path.split('.'):
        # try list index
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                raise KeyError(f"Expected list index at '{part}' but couldn’t convert to int.")
            try:
                current = current[idx]
            except IndexError:
                raise IndexError(f"List index out of range: {idx}")
        # otherwise dict key
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                raise KeyError(f"Key not found: '{part}'")
        else:
            raise KeyError(f"Can’t descend into non-collection at '{part}'")
    return current


from typing import List, Dict, BinaryIO
import pandas as pd

def dump_dicts_to_excel_with_pandas(data: List[Dict], stream_out: BinaryIO, sheet_name: str = "Sheet1") -> None:
    """
    Dump a list of dictionaries to an Excel sheet using pandas, streaming directly to `stream_out`.

    :param data: List of dicts, all with the same keys (columns).
    :param stream_out: A binary writeable file-like (e.g. open('out.xlsx','wb'), BytesIO, HTTP response).
    :param sheet_name: Optional name of the Excel sheet.
    """
    # turn list of dicts into DataFrame
    df = pd.DataFrame(data)
    # write to the provided stream
    # index=False to omit the DataFrame index column
    df.to_excel(stream_out, sheet_name=sheet_name, index=False)