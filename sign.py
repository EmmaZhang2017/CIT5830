import eth_account
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account


def sign(m):
    w3 = Web3()

    # Create a new Ethereum account with a private key
    account = Account.create()  # This generates a new Ethereum account
    eth_address = account.address  # Retrieve the Ethereum address from the account
    private_key = account.key  # Retrieve the private key from the account

    # Prepare the message to be signed
    message = encode_defunct(text=m)

    # Sign the message using the private key
    signed_message = Account.sign_message(message, private_key=private_key)

    # Ensure that the signed_message is an instance of SignedMessage
    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)

    return eth_address, signed_message
