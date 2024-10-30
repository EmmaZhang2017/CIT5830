from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/113ca7669446446fa69a2c968bbf1bde" #YOU WILL NEED TO TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(apeID):

	assert isinstance(apeID,int), f"{apeID} is not an int"
	assert 1 <= apeID, f"{apeID} must be at least 1"
	data = {'owner': "", 'image': "", 'eyes': "" }
	
	#YOUR CODE HERE	
	################################################################################################################################################
	contract = web3.eth.contract(address=contract_address, abi=abi)
	
	# Fetch the owner of the token
    	data['owner'] = contract.functions.ownerOf(apeID).call()
    
    	# Get the token's URI for metadata
    	token_uri = contract.functions.tokenURI(apeID).call()
    
    	# Check if the URI is an IPFS link and convert it if needed
    	if token_uri.startswith("ipfs://"):
        	token_uri = token_uri.replace("ipfs://", "https://ipfs.io/ipfs/")
    
    	# Fetch the metadata
   	response = requests.get(token_uri)
    	if response.status_code == 200:
       		metadata = response.json()
        	data['image'] = metadata.get('image', "")
        
        	# Convert IPFS image link if needed
        	if data['image'].startswith("ipfs://"):
            		data['image'] = data['image'].replace("ipfs://", "https://ipfs.io/ipfs/")
        
        	# Look for "eyes" trait in the attributes
        	attributes = metadata.get('attributes', [])
        	for attr in attributes:
            		if attr.get('trait_type') == 'Eyes':
                		data['eyes'] = attr.get('value', "")
                		break
    	else:
        	print(f"Failed to retrieve metadata for apeID {apeID}")





	#################################################################################################################################################

	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

