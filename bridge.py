from web3 import Web3
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
import sys
from pathlib import Path

# Source and destination chain identifiers
source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet

    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet

    else:
        raise ValueError("Invalid chain specified.")

    w3 = Web3(Web3.HTTPProvider(api_url))
    # Inject the POA compatibility middleware to the innermost layer
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def getContractInfo(chain):
    """
    Load the contract_info file into a dictionary.
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r') as f:
            contracts = json.load(f)
    except Exception as e:
        print("Failed to read contract info")
        print("Please contact your instructor")
        print(e)
        sys.exit(1)

    return contracts[chain]

def wrap(chain, event_args):
    """
    Wrap function to handle cross-chain operations.
    """
    w3 = connectTo(chain)
    contract_info = getContractInfo(chain)

    contract_address = Web3.to_checksum_address(contract_info["address"])
    contract_abi = contract_info["abi"]
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Call the wrap function on the destination chain
    tx = contract.functions.wrap(
        event_args["user"],
        event_args["amount"]
    ).build_transaction({
        "from": event_args["user"],
        "nonce": w3.eth.get_transaction_count(event_args["user"]),
        "gas": 300000,
        "gasPrice": w3.to_wei('20', 'gwei')
    })

    # Print the transaction for now (signing required for real execution)
    print(f"Wrap Transaction: {tx}")

def withdraw(chain, event_args):
    """
    Withdraw function to handle cross-chain operations.
    """
    w3 = connectTo(chain)
    contract_info = getContractInfo(chain)

    contract_address = Web3.to_checksum_address(contract_info["address"])
    contract_abi = contract_info["abi"]
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Call the withdraw function on the source chain
    tx = contract.functions.withdraw(
        event_args["user"],
        event_args["amount"]
    ).build_transaction({
        "from": event_args["user"],
        "nonce": w3.eth.get_transaction_count(event_args["user"]),
        "gas": 300000,
        "gasPrice": w3.to_wei('20', 'gwei')
    })

    # Print the transaction for now (signing required for real execution)
    print(f"Withdraw Transaction: {tx}")

def scanBlocks(chain):
    """
    Scan the last 5 blocks of the source and destination chains.
    """
    if chain == "source":
        w3 = connectTo(source_chain)
        contract_info = getContractInfo(source_chain)
    elif chain == "destination":
        w3 = connectTo(destination_chain)
        contract_info = getContractInfo(destination_chain)
    else:
        print(f"Invalid chain: {chain}")
        return

    # Load contract ABI and address
    contract_address = Web3.to_checksum_address(contract_info["address"])
    contract_abi = contract_info["abi"]
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Get the latest block
    latest_block = w3.eth.block_number

    print(f"Scanning the last 5 blocks on {chain} chain:")
    for block_num in range(latest_block - 4, latest_block + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        
        # Process transactions in the block
        for tx in block["transactions"]:
            try:
                # Decode logs from transaction receipts
                receipt = w3.eth.get_transaction_receipt(tx["hash"])
                logs = contract.events.Deposit().process_receipt(receipt) if chain == "source" else contract.events.Unwrap().process_receipt(receipt)
                
                # Process events
                for log in logs:
                    if chain == "source":
                        print(f"Deposit event found: {log['args']}")
                        wrap(destination_chain, log["args"])  # Call wrap function
                    elif chain == "destination":
                        print(f"Unwrap event found: {log['args']}")
                        withdraw(source_chain, log["args"])  # Call withdraw function
            except Exception as e:
                # Ignore transactions that don't match event signatures
                pass
