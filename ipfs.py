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




INFURA_API_URL_1 = "https://ipfs.infura.io/ipfs/"

def get_from_ipfs(ipfs_hash):
    """
    Retrieve data from IPFS using Infura API and the given IPFS hash (CID).

    Parameters:
    - ipfs_hash: The IPFS hash (CID) of the pinned content.

    Returns:
    - The content retrieved from IPFS as text.
    """
    try:
        # Construct the URL to access the IPFS content via Infura gateway
        url = INFURA_API_URL_1 + ipfs_hash
        
        # Make a GET request to retrieve the content
        response = requests.get(url)
        response.raise_for_status()
        
        # Return the content as text (or you can handle binary data depending on the content)
        return response.text
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
