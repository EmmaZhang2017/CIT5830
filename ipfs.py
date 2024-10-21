def pin_to_ipfs(data):
    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)
    
    # Define the IPFS API endpoint
    ipfs_api_url = 'http://localhost:5001/api/v0/'
    
    # Use the 'add' endpoint to upload the JSON data
    response = requests.post(ipfs_api_url + 'add', files={'file': json_data})
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract the CID from the response
        cid = response.json()['Hash']
        return cid
    else:
        raise Exception(f"Error uploading to IPFS: {response.text}")
