import os
from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
from datetime import datetime
import pandas as pd
import csv

eventfile = 'deposit_logs.csv'

def scanBlocks(chain, start_block, end_block, contract_address):
    """
    Scan blockchain events for 'Deposit' events and log them into a CSV file.

    chain - string: ('bsc' or 'avax')
    start_block - int: Starting block to scan
    end_block - int: Ending block to scan
    contract_address - string: Deployed contract address to monitor
    """
    # Set up the RPC URL for the specified chain
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        print(f"Unsupported chain: {chain}")
        return

    # Initialize Web3 and inject middleware for POA compatibility
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Define the ABI for the Deposit event
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    # Handle block numbers if 'latest' is specified
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    # Validate the block range
    if end_block < start_block:
        print(f"Error: end_block ({end_block}) is less than start_block ({start_block}).")
        return

    if start_block == end_block:
        print(f"Scanning block {start_block} on {chain}")
    else:
        print(f"Scanning blocks {start_block} - {end_block} on {chain}")

    events_data = []

    # Scan blocks for events
    for block_num in range(start_block, end_block + 1):
        try:
            event_filter = contract.events.Deposit.create_filter(
                fromBlock=block_num, toBlock=block_num
            )
            events = event_filter.get_all_entries()
        except Exception as e:
            print(f"Error fetching events for block {block_num}: {e}")
            continue

        for event in events:
            # Print the event to inspect its structure (useful for debugging)
            print(event)

            # Access event attributes safely
            block_number = event.get("blockNumber", "N/A")
            token = event["args"].get("token", "N/A")
            recipient = event["args"].get("recipient", "N/A")
            amount = event["args"].get("amount", 0)
            transaction_hash = event.get("transactionHash", "N/A")

            events_data.append([
                block_number,
                token,
                recipient,
                amount,
                transaction_hash.hex() if isinstance(transaction_hash, bytes) else transaction_hash
            ])

    # Write data to CSV
    write_to_csv(events_data)


def write_to_csv(events_data):
    """
    Write event data to a CSV file, ensuring consistent rows.
    """
    if not events_data:
        print("No events found in the specified block range.")
        return

    # Check if the file already exists
    file_exists = os.path.isfile(eventfile)

    # Open the file in append mode
    with open(eventfile, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write headers if the file is new
        if not file_exists:
            writer.writerow(["block_number", "token", "recipient", "amount", "transaction_hash"])

        # Write event data rows
        for data in events_data:
            writer.writerow(data)

    print(f"Logged {len(events_data)} events to {eventfile}")


def clean_csv_file():
    """
    Clean the CSV file to ensure all rows have the correct number of fields.
    """
    if not os.path.isfile(eventfile):
        print(f"{eventfile} does not exist.")
        return

    valid_rows = []

    # Read the existing CSV file and filter invalid rows
    with open(eventfile, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Save headers
        for row in reader:
            if len(row) == 5:  # Ensure each row has the correct number of fields
                valid_rows.append(row)

    # Rewrite the file with only valid rows
    with open(eventfile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(valid_rows)

    print(f"Cleaned {eventfile}, keeping {len(valid_rows)} valid rows.")
