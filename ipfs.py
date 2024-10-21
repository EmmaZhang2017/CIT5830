import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE


  json_data = json.dumps(data).encode()  # Convert dict to JSON bytes
    
  # Assuming you have a configured IPFS client (replace with your preferred method)
  ipfs_client =  # Initialize your IPFS client
  cid = ipfs_client.add(json_data)["Hash"]  # Add data to IPFS and get CID
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
