#!/bin/python
import hashlib
import os
import random


def mine_block(k, prev_hash, rand_lines):
    """
    k - Number of trailing zeros in the binary representation (integer)
    prev_hash - the hash of the previous block (bytes)
    rand_lines - a set of "transactions," i.e., data to be included in this block (list of strings)
    """
    if not isinstance(k, int) or k < 0:
        print("mine_block expects positive integer")
        return b'\x00'

    # Convert the previous hash to bytes if it's not already
    if isinstance(prev_hash, str):
        prev_hash = bytes.fromhex(prev_hash)

    # Join the random lines into a single string and encode to bytes
    data = ''.join(rand_lines).encode('utf-8')

    # Start with a nonce of 0
    nonce = 0

    while True:
        # Convert the nonce to bytes
        nonce_bytes = nonce.to_bytes((nonce.bit_length() + 7) // 8, byteorder='big') or b'\x00'
        
        # Concatenate the previous hash, data, and nonce
        input_data = prev_hash + data + nonce_bytes
        
        # Calculate the SHA-256 hash
        hash_result = hashlib.sha256(input_data).hexdigest()
        
        # Convert hash to binary and check for trailing binary zeros
        binary_hash = bin(int(hash_result, 16))[2:].zfill(256)  # Ensure 256 bits
        if binary_hash[-k:] == '0' * k:
            print(f"Found nonce: {nonce}, hash: {hash_result}")
            return nonce_bytes
        
        # Increment nonce for the next iteration
        nonce += 1

    return b'\x00'



def get_random_lines(filename, quantity):
    """
    This is a helper function to get the quantity of lines ("transactions")
    as a list from the filename given. 
    Do not modify this function
    """
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line.strip())

    random_lines = []
    for x in range(quantity):
        random_lines.append(lines[random.randint(0, quantity - 1)])
    return random_lines





if __name__ == '__main__':
    filename = "bitcoin_text.txt"
    num_lines = 10  # The number of "transactions" included in the block

    diff = 20
    rand_lines = get_random_lines(filename, num_lines)
    
    # Example of a previous hash (this should be a 32-byte hash in bytes)
    prev_hash = os.urandom(32)  # Generate a random 32-byte previous hash for testing

    nonce = mine_block(diff, prev_hash, rand_lines)
    print(f"Nonce: {nonce.hex()}")
