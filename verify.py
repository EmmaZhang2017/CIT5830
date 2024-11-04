from web3 import Web3
from eth_account.messages import encode_defunct
import random

def signChallenge(challenge):
    w3 = Web3()

    # Replace this with the actual private key securely
    sk = "YOUR_SECRET_KEY_HERE"

    acct = w3.eth.account.from_key(sk)
    signed_message = w3.eth.account.sign_message(challenge, private_key=acct.key)

    return acct.address, signed_message.signature


def verifySig():
    """
    Test function to verify if the signChallenge function works correctly.
    """
    challenge_bytes = random.getrandbits(256).to_bytes(32, 'big')
    challenge = encode_defunct(challenge_bytes)
    address, sig = signChallenge(challenge)

    w3 = Web3()
    recovered_address = w3.eth.account.recover_message(challenge, signature=sig)
    
    return recovered_address == address


if __name__ == '__main__':
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")
