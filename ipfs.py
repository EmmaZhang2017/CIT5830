import requests
import json




def pin_to_ipfs(data):

    json_data = json.dumps(data)
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files, auth=('113ca7669446446fa69a2c968bbf1bde','3LzF+FZcy3PHHvYIQdKeHaj7vt9QHu/OKT44V+ilBJsFjfbyD5cPqw'))
    
    if response.status_code == 200:
        cid = response.json()['Hash']
        return cid
    else:
        print(f"Error: {response.status_code} - {response.text}")
        raise Exception("Error uploading to IPFS.")


https://ipfs.infura.io:5001/api/v0/add



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
