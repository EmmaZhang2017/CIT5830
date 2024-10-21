import requests
import json


# Infura API endpoint for pinning to IPFS
INFURA_API_URL = "https://ipfs.infura.io:5001/api/v0/add"
INFURA_PROJECT_ID = "113ca7669446446fa69a2c968bbf1bde"
INFURA_PROJECT_SECRET = "3LzF+FZcy3PHHvYIQdKeHaj7vt9QHu/OKT44V+ilBJsFjfbyD5cPqw"

def pin_to_ipfs(data):
    """
    Pin data (JSON-serializable object or file content) to IPFS using Infura API.

    Parameters:
    - data: A dictionary (or JSON-serializable object) to pin.

    Returns:
    - The IPFS hash (CID) of the pinned content.
    """
    # Convert the data to JSON if it's a dictionary
    if isinstance(data, dict):
        data = json.dumps(data)

    try:
        # Make a POST request to Infura's IPFS API with the file or JSON data
        files = {
            'file': ('data.json', data)
        }

        response = requests.post(
            INFURA_API_URL, 
            files=files, 
            auth=HTTPBasicAuth(INFURA_PROJECT_ID, INFURA_PROJECT_SECRET)
        )

        response.raise_for_status()

        # Return the IPFS hash (CID) from the response
        return response.json()["Hash"]

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")




# Infura API base URL for IPFS

def get_from_ipfs(cid, content_type="json"):
    """
    Retrieve data from IPFS using Infura API and the given IPFS CID (Content Identifier).

    Parameters:
    - cid: The IPFS hash (CID) of the pinned content.
    - content_type: The expected content type of the retrieved data. Default is "json". 
                    Supported values are "json", "text", "binary".

    Returns:
    - The content retrieved from IPFS. The format depends on the content_type:
        - If content_type is "json", it returns a parsed JSON object.
        - If content_type is "text", it returns the raw text.
        - If content_type is "binary", it returns the binary data.
    """
    try:
        # Construct the URL to access the IPFS content via Infura gateway
        url = "https://ipfs.infura.io/ipfs/" + cid
        
        # Make a GET request to retrieve the content
        response = requests.get(url)
        response.raise_for_status()

        # Handle different content types
        if content_type == "json":
            return response.json()  # Parse and return JSON
        elif content_type == "text":
            return response.text  # Return raw text
        elif content_type == "binary":
            return response.content  # Return binary data
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except ValueError as val_err:
        print(f"Value error: {val_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
