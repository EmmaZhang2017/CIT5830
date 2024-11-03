from web3 import Web3
import eth_account
from eth_account import Account
import os
from mnemonic import Mnemonic

def get_keys(challenge, keyId=0, filename="eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """
    
    # Step 1: Ensure mnemonic file exists and read existing mnemonics
    if not os.path.exists(filename):
        open(filename, 'w').close()  # Create file if it doesn't exist

    with open(filename, 'r') as f:
        mnemonics = f.readlines()

    # Step 2: Generate new mnemonics if needed and save them
    if len(mnemonics) <= keyId:
        mnemo = Mnemonic("english")
        for i in range(len(mnemonics), keyId + 1):
            new_mnemonic = mnemo.generate(strength=128)  # Generate 12-word mnemonic
            mnemonics.append(new_mnemonic + "\n")
        with open(filename, 'w') as f:
            f.writelines(mnemonics)

    # Retrieve the mnemonic for the current keyId and derive a private key
    mnemonic_phrase = mnemonics[keyId].strip()
    acct = Account.from_mnemonic(mnemonic_phrase)
    private_key = acct.key

    # Step 3: Sign the message
    w3 = Web3()
    msg = eth_account.messages.encode_defunct(challenge)
    sig = w3.eth.account.sign_message(msg, private_key=private_key)
    eth_addr = acct.address

    # Verification
    assert eth_account.Account.recover_message(msg, signature=sig.signature) == eth_addr, \
        "Failed to sign message properly"

    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, keyId=i)
        print(addr)
