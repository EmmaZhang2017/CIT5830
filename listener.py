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
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        print(f"Unsupported chain: {chain}")
        return

    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

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
            event_filter = contract.events.Deposit.create_filter(
                fromBlock=block_num, toBlock=block_num
            )
            events = event_filter.get_all_entries()
        except Exception as e:
            print(f"Error fetching events for block {block_num}: {e}")
            continue

        for event in events:
            try:
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
    if not events_data:
        print("No events found in the specified block range.")
        return

    file_exists = os.path.isfile(eventfile)

    with open(eventfile, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["block_number", "token", "recipient", "amount", "transaction_hash"])

        for data in events_data:
            if len(data) == 5:
                writer.writerow(data)
            else:
                print(f"Skipping invalid data: {data}")


def clean_csv_file():
    if not os.path.isfile(eventfile):
        print(f"{eventfile} does not exist.")
        return

    valid_rows = []

    with open(eventfile, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)  # Get headers
        if headers is None or len(headers) != 5:
            print("Invalid CSV format: missing or incorrect headers.")
            return

        for row in reader:
            if len(row) == 5:
                valid_rows.append(row)
            else:
                print(f"Invalid row skipped: {row}")

    with open(eventfile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(valid_rows)

    print(f"Cleaned {eventfile}, keeping {len(valid_rows)} valid rows.")
