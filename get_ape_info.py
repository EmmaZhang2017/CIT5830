from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

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

    	# Define the API endpoint    

	# Make the API request
	response = requests.get(api_url)
	response.raise_for_status()
        ape_data = response.json()

        # Extract owner, image, and eye attribute
        data['owner'] = ape_data['owner']['address']
        data['image'] = ape_data['image_url']

        # Find the "eyes" attribute if it exists
        attributes = ape_data.get('traits', [])
        for trait in attributes:
            if trait['trait_type'].lower() == 'eyes':
                data['eyes'] = trait['value']
                break

	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

