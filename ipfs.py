import requests
import json




def pin_to_ipfs(data):
    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)
    
    # Define the IPFS API endpoint
    ipfs_api_url = 'https://mainnet.infura.io/v3/113ca7669446446fa69a2c968bbf1bde'
    
    # Use the 'add' endpoint to upload the JSON data
    response = requests.post(ipfs_api_url + 'add', files={'file': json_data})
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract the CID from the response
        cid = response.json()['Hash']
        return cid
    else:
        raise Exception(f"Error uploading to IPFS: {response.text}")


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), "get_from_ipfs accepts a cid in the form of a string"
    
    # Define the IPFS API endpoint
    ipfs_api_url = 'https://mainnet.infura.io/v3/113ca7669446446fa69a2c968bbf1bde/cat?arg={cid}'
    
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
