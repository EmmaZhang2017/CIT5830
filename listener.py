import os
from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
from datetime import datetime
import pandas as pd
import csv

import tempfile  # Add this import for temporary file handling


eventfile = 'deposit_logs.csv'



def scanBlocks(chain, start_block, end_block, contract_address):
    """Scan blockchain blocks for Deposit events."""
    # Define RPC URLs for supported chains
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        print(f"Unsupported chain: {chain}")
        return

    try:
        # Initialize Web3 connection
        w3 = Web3(Web3.HTTPProvider(api_url))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    except Exception as e:
        print(f"Error connecting to {chain} RPC: {e}")
        return

    # Define the ABI for the Deposit event
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    # Resolve block numbers
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    if end_block < start_block:
        print(f"Error: end_block ({end_block}) is less than start_block ({start_block}).")
        return

    print(f"Scanning blocks {start_block} - {end_block} on {chain}")

    events_data = []

    for block_num in range(start_block, end_block + 1):
        try:
            # Create event filter for the current block
            event_filter = contract.events.Deposit.create_filter(
                fromBlock=block_num, toBlock=block_num
            )
            events = event_filter.get_all_entries()
        except Exception as e:
            print(f"Error fetching events for block {block_num}: {e}")
            continue

        for event in events:
            try:
                # Extract event details
                block_number = event.get("blockNumber", "N/A")
                token = event["args"].get("token", "N/A")
                recipient = event["args"].get("recipient", "N/A")
                amount = event["args"].get("amount", 0)
                transaction_hash = event.get("transactionHash", "N/A")

                # Ensure valid formatting for transaction_hash
                transaction_hash = (
                    transaction_hash.hex()
                    if isinstance(transaction_hash, bytes)
                    else str(transaction_hash)
                )

                events_data.append([
                    block_number,
                    token,
                    recipient,
                    amount,
                    transaction_hash
                ])
            except KeyError as e:
                print(f"Error processing event: {e}")
                continue

    write_to_csv(events_data)


def write_to_csv(events_data):
    """Write event data to the deposit logs CSV file."""
    if not events_data:
        print("No events found in the specified block range.")
        return

    file_exists = os.path.isfile(eventfile)

    with tempfile.NamedTemporaryFile('w', delete=False, newline='', encoding='utf-8') as tempf:
        writer = csv.writer(tempf)

        # Write headers if the file doesn't exist
        if not file_exists:
            writer.writerow(["block_number", "token", "recipient", "amount", "transaction_hash"])

        for data in events_data:
            if len(data) == 5:
                writer.writerow(data)
            else:
                print(f"Skipping invalid data: {data}")

    # Replace the original file with the new one
    os.replace(tempf.name, eventfile)
    print(f"Events written to {eventfile}")


import shutil  # Import shutil for moving files across devices

def write_to_csv(events_data):
    """Write event data to the deposit logs CSV file."""
    if not events_data:
        print("No events found in the specified block range.")
        return

    file_exists = os.path.isfile(eventfile)

    with tempfile.NamedTemporaryFile('w', delete=False, newline='', encoding='utf-8') as tempf:
        writer = csv.writer(tempf)

        # Write headers if the file doesn't exist
        if not file_exists:
            writer.writerow(["block_number", "token", "recipient", "amount", "transaction_hash"])

        for data in events_data:
            if len(data) == 5:
                writer.writerow(data)
            else:
                print(f"Skipping invalid data: {data}")

    # Use shutil.move to handle cross-device file moves
    shutil.move(tempf.name, eventfile)
    print(f"Events written to {eventfile}")

