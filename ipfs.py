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






def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), "get_from_ipfs accepts a cid in the form of a string"
    
    # Define the IPFS API endpoint
    ipfs_api_url = "https://mainnet.infura.io/v3/113ca7669446446fa69a2c968bbf1bde/cat?arg={cid}"
    
    # Make a GET request to retrieve the data
    response = requests.get(ipfs_api_url)

    # Check if the request was successful
    if response.status_code == 200:
        if content_type == "json":
            # Parse the response as JSON
            data = json.loads(response.text)
        else:
            # Return plain text or other formats as needed
            data = response.text
        
        assert isinstance(data, dict), "get_from_ipfs should return a dict"
        return data
    else:
        raise Exception(f"Error retrieving from IPFS: {response.text}")
