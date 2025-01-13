import requests
import pandas as pd
from io import BytesIO

def get_collibra_attachment_as_dataframe(api_base, api_user, api_password, asset_id, attachment_name=None):
    """
    Queries Collibra attachments, downloads the specified Excel file, and loads it as a pandas DataFrame.

    :param api_base: Base URL of the Collibra API
    :param api_user: Username for the Collibra API
    :param api_password: Password for the Collibra API
    :param asset_id: The ID of the asset to query attachments for
    :param attachment_name: Optional name of the attachment to filter by (default is None)
    :return: A pandas DataFrame containing the data from the downloaded Excel file
    :raises Exception: If the API call or file download fails
    """
    # Authenticate with Collibra
    session = requests.Session()
    session.auth = (api_user, api_password)

    # Query attachments for the asset
    attachments_url = f"{api_base}/rest/2.0/attachments?baseResourceId={asset_id}"
    response = session.get(attachments_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve attachments: {response.status_code}, {response.text}")

    attachments = response.json()
    
    # Filter the desired attachment
    attachment = None
    for att in attachments:
        if attachment_name and att['name'] == attachment_name:
            attachment = att
            break
    if not attachment_name and attachments:
        attachment = attachments[0]  # Default to the first attachment if no name specified
    
    if not attachment:
        raise Exception("No matching attachment found.")

    # Download the attachment
    download_url = f"{api_base}/rest/2.0/attachments/{attachment['id']}/file"
    download_response = session.get(download_url)
    
    if download_response.status_code != 200:
        raise Exception(f"Failed to download attachment: {download_response.status_code}, {download_response.text}")

    # Load the Excel file as a pandas DataFrame
    file_content = BytesIO(download_response.content)
    dataframe = pd.read_excel(file_content)

    return dataframe