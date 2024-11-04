from web3 import Web3
import eth_account
import os
from eth_account import Account

def get_keys(challenge, keyId=0, filename="eth_private_keys.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store private keys

    Each private key is stored on a separate line
    If fewer than (keyId+1) keys have been generated, generate a new one and return that
    """

    # Ensure the private key file exists
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass  # Create the file if it doesn't exist

    # Read existing private keys from the file
    with open(filename, 'r') as f:
        private_keys = f.readlines()

    # Check if we have enough keys for the requested keyId
    if len(private_keys) <= keyId:
        # Generate new private keys until we have enough
        while len(private_keys) <= keyId:
            new_key = Account.create().key.hex()
            private_keys.append(new_key + '\n')

        # Write all private keys back to the file
        with open(filename, 'w') as f:
            f.writelines(private_keys)

    # Retrieve the private key for the given keyId
    private_key = private_keys[keyId].strip()
    acct = Account.from_key(private_key)

    # Sign the challenge
    msg = eth_account.messages.encode_defunct(challenge)
    sig = acct.sign_message(msg)

    # Verify the signature
    eth_addr = acct.address
    assert Account.recover_message(msg, signature=sig.signature) == eth_addr, "Failed to sign message properly"

    # Return signature and address
    return sig, eth_addr




if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )
