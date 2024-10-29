import random
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider


# If you use one of the suggested infrastructure providers, the url will be of the form
# now_url  = f"https://eth.nownodes.io/{now_token}"
# alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
# infura_url = f"https://mainnet.infura.io/v3/{infura_token}"

def connect_to_eth():
	# TODO insert your code for this method from last week's assignment

  # Replace the provider URL with your specific Ethereum node provider
    provider_url = "https://mainnet.infura.io/v3/113ca7669446446fa69a2c968bbf1bde"
    
    # Establish a connection
    w3 = Web3(Web3.HTTPProvider(provider_url))
    
    # Check if connected
    if w3.is_connected():
        print("Successfully connected to Ethereum")
    else:
        print("Connection failed")

    return w3

	
def connect_with_middleware(contract_json):
    provider_url = "https://bsc-dataseed.binance.org/"
    w3 = Web3(Web3.HTTPProvider(provider_url))
    
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    with open(contract_json) as f:
        contract_data = json.load(f)

    if 'abi' not in contract_data['bsc'] or 'address' not in contract_data['bsc']:
        raise ValueError("Contract JSON must contain 'abi' and 'address' keys.")
    
    abi = contract_data['bsc']['abi']
    address = contract_data['bsc']['address']

    # Check ABI and address types
    if not isinstance(abi, list) or not isinstance(address, str):
        print("Invalid ABI or address format.")
        return None, None

    contract = w3.eth.contract(address=address, abi=abi)
    
    if w3.is_connected():
        print("Successfully connected to BNB testnet and contract instantiated")
    else:
        print("Connection to BNB testnet failed")
    
    return w3, contract






def is_ordered_block(w3, block_num):
    block = w3.eth.get_block(block_num, full_transactions=True)
    base_fee = block.get('baseFeePerGas', 0)
    
    priority_fees = []

    for tx in block.transactions:
        if tx.type == '0x0':
            priority_fee = tx.gasPrice - base_fee
        elif tx.type == '0x2':
            priority_fee = min(tx.maxPriorityFeePerGas, tx.maxFeePerGas - base_fee)
        else:
            continue

        priority_fees.append(priority_fee)
    
    # Check if we have any priority fees to evaluate
    if not priority_fees:
        print(f"Block {block_num} has no relevant transactions. Treating as unordered by default.")
        return False

    # Check if the list is in descending order
    ordered = all(priority_fees[i] >= priority_fees[i + 1] for i in range(len(priority_fees) - 1))
    return ordered



def get_contract_values(contract, admin_address, owner_address):
	"""
	Takes a contract object, and two addresses (as strings) to be used for calling
	the contract to check current on chain values.
	The provided "default_admin_role" is the correctly formatted solidity default
	admin value to use when checking with the contract
	To complete this method you need to make three calls to the contract to get:
	  onchain_root: Get and return the merkleRoot from the provided contract
	  has_role: Verify that the address "admin_address" has the role "default_admin_role" return True/False
	  prime: Call the contract to get and return the prime owned by "owner_address"

	check on available contract functions and transactions on the block explorer at
	https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	"""
	default_admin_role = int.to_bytes(0, 32, byteorder="big")

	# TODO complete the following lines by performing contract calls
	onchain_root = 0  # Get and return the merkleRoot from the provided contract
	has_role = 0  # Check the contract to see if the address "admin_address" has the role "default_admin_role"
	prime = 0  # Call the contract to get the prime owned by "owner_address"

	return onchain_root, has_role, prime


"""
	This might be useful for testing (main is not run by the grader feel free to change 
	this code anyway that is helpful)
"""
if __name__ == "__main__":
	# These are addresses associated with the Merkle contract (check on contract
	# functions and transactions on the block explorer at
	# https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	admin_address = "0xAC55e7d73A792fE1A9e051BDF4A010c33962809A"
	owner_address = "0x793A37a85964D96ACD6368777c7C7050F05b11dE"
	contract_file = "contract_info.json"

	eth_w3 = connect_to_eth()
	cont_w3, contract = connect_with_middleware(contract_file)

	latest_block = eth_w3.eth.get_block_number()
	london_hard_fork_block_num = 12965000
	assert latest_block > london_hard_fork_block_num, f"Error: the chain never got past the London Hard Fork"

	n = 5
	for _ in range(n):
		block_num = random.randint(1, london_hard_fork_block_num - 1)
		ordered = is_ordered_block(block_num)
		if ordered:
			print(f"Block {block_num} is ordered")
		else:
			print(f"Block {block_num} is not ordered")
