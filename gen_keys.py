from web3 import Web3
import eth_account
import os


def get_keys(challenge, keyId=0, filename="eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    # Ensure the mnemonic file exists
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass  # Create the file if it doesn't exist

    # Read existing mnemonics from the file
    with open(filename, 'r') as f:
        mnemonics = f.readlines()

    # Check if we have enough mnemonics for the requested keyId
    if len(mnemonics) <= keyId:
        # Generate new mnemonics until we have enough
        mnemo = Mnemonic("english")
        while len(mnemonics) <= keyId:
            new_mnemonic = mnemo.generate(strength=128)
            mnemonics.append(new_mnemonic + '\n')

        # Write all mnemonics back to the file
        with open(filename, 'w') as f:
            f.writelines(mnemonics)

    # Retrieve the mnemonic for the given keyId
    mnemonic = mnemonics[keyId].strip()
    acct = Account.from_mnemonic(mnemonic)

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
