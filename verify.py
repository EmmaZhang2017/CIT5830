from web3 import Web3
from eth_account.messages import encode_defunct
import random

def signChallenge(challenge):
    w3 = Web3()

    # Replace this with an actual private key
    sk = "0xYOUR_PRIVATE_KEY"  # Enter your private key here

    acct = w3.eth.account.from_key(sk)

    signed_message = w3.eth.account.sign_message(challenge, private_key=acct._private_key)

    return acct.address, signed_message.signature


def verifySig():
    """
    This is essentially the code that the autograder will use to test signChallenge.
    We've added it here for testing.
    """

    challenge_bytes = random.randbytes(32)
    challenge = encode_defunct(challenge_bytes)
    address, sig = signChallenge(challenge)

    w3 = Web3()
    validSig = w3.eth.account.recover_message(challenge, signature=sig) == address  # Assigning validSig here

    return validSig

if __name__ == '__main__':
    """
    Test your function
    """
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")
