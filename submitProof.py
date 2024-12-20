import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware  # Necessary for POA chains


def merkle_assignment():
    """
        The only modifications you need to make to this method are to assign
        your "random_leaf_index" and uncomment the last line when you are
        ready to attempt to claim a prime. You will need to complete the
        methods called by this method to generate the proof.
    """
    # Generate the list of primes as integers
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    # Create a version of the list of primes in bytes32 format
    leaves = convert_leaves(primes)

    # Build a Merkle tree using the bytes32 leaves as the Merkle tree's leaves
    tree = build_merkle(leaves)

    # Select a random leaf and create a proof for that leaf
    random_leaf_index = 0 #TODO generate a random index from primes to claim (0 is already claimed)
    proof = prove_merkle(tree, random_leaf_index)

    # This is the same way the grader generates a challenge for sign_challenge()
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    # Sign the challenge to prove to the grader you hold the account
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        tx_hash = '0x'
        # TODO, when you are ready to attempt to claim a prime (and pay gas fees),
        #  complete this method and run your code with the following line un-commented
        # tx_hash = send_signed_msg(proof, leaves[random_leaf_index])


def generate_primes(num_primes):
    primes_list = []
    candidate = 2
    while len(primes_list) < num_primes:
        for p in primes_list:
            if candidate % p == 0:
                break
        else:
            primes_list.append(candidate)
        candidate += 1
    return primes_list




def convert_leaves(primes_list):
    return [int(prime).to_bytes(32, byteorder='big') for prime in primes_list]





def build_merkle(leaves):
    tree = [leaves]
    current_level = leaves
    while len(current_level) > 1:
        parent_level = []
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                parent_level.append(hash_pair(current_level[i], current_level[i + 1]))
            else:
                parent_level.append(current_level[i])  # Handle odd number of leaves
        tree.append(parent_level)
        current_level = parent_level
    return tree




def prove_merkle(merkle_tree, random_indx):
    """
        Takes a random_index to create a proof of inclusion for and a complete Merkle tree
        as a list of lists where index 0 is the list of leaves, index 1 is the list of
        parent hash values, up to index -1 which is the list of the root hash.
        returns a proof of inclusion as list of values
    """
    merkle_proof = []
    index = random_indx
    
    # Traverse from the leaves up to the root
    for level in range(len(merkle_tree) - 1):
        # If the index is even, we take the right sibling
        if index % 2 == 0:  
            # Check if there's a right sibling
            if index + 1 < len(merkle_tree[level]):
                merkle_proof.append(merkle_tree[level][index + 1])
        else:  # If the index is odd, we take the left sibling
            merkle_proof.append(merkle_tree[level][index - 1])
        
        # Move to the parent level
        index //= 2
    
    return merkle_proof
    



def sign_challenge(challenge):
    acct = get_account()
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    eth_sig = acct.sign_message(eth_encoded_msg)
    return acct.address, eth_sig.signature.hex()  # Convert the signature to hex string



def send_signed_msg(proof, random_leaf):
    w3 = connect_to('bsc')  # or 'avax'
    acct = get_account()
    contract_address, abi = get_contract_info('bsc')  # adjust as needed
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    tx = contract.functions.claimPrime(random_leaf, proof).buildTransaction({
        'chainId': 97,  # BSC testnet ID
        'gas': 2000000,
        'gasPrice': w3.toWei('10', 'gwei'),
        'nonce': w3.eth.getTransactionCount(acct.address),
    })
    
    signed_tx = w3.eth.account.signTransaction(tx, acct.key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash.hex()
  


# Helper functions that do not need to be modified
def connect_to(chain):
    """
        Takes a chain ('avax' or 'bsc') and returns a web3 instance
        connected to that chain.
    """
    if chain not in ['avax','bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    else:
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    w3 = Web3(Web3.HTTPProvider(api_url))
    # inject the poa compatibility middleware to the innermost layer
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


def get_account():
    """
        Returns an account object recovered from the secret key
        in "sk.txt"
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().rstrip()
    if sk[0:2] == "0x":
        sk = sk[2:]
    return eth_account.Account.from_key(sk)


def get_contract_info(chain):
    """
        Returns a contract address and contract abi from "contract_info.json"
        for the given chain
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("contract_info.json"), "r") as f:
        d = json.load(f)
        d = d[chain]
    return d['address'], d['abi']


def sign_challenge_verify(challenge, addr, sig):
    """
        Helper to verify signatures, verifies sign_challenge(challenge)
        the same way the grader will. No changes are needed for this method
    """
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)

    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False


def hash_pair(a, b):
    """
        The OpenZeppelin Merkle Tree Validator we use sorts the leaves
        https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/MerkleProof.sol#L217
        So you must sort the leaves as well

        Also, hash functions like keccak are very sensitive to input encoding, so the solidity_keccak function is the function to use

        Another potential gotcha, if you have a prime number (as an int) bytes(prime) will *not* give you the byte representation of the integer prime
        Instead, you must call int.to_bytes(prime,'big').
    """
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])


if __name__ == "__main__":
    merkle_assignment()
