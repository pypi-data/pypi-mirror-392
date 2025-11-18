"""Cryptography utilities for CTF challenges."""

# Import classical crypto functions
from .classical import (
    caesar_encrypt, 
    caesar_decrypt, 
    caesar_brute_force,
    vigenere_encrypt, 
    vigenere_decrypt
)

# Import modern crypto functions
from .modern import (
    base64_encode, 
    base64_decode, 
    is_base64,
    xor_encrypt,
    xor_decrypt_hex,
    xor_brute_force_single_byte
)

# Import hashing functions
from .hashing import (
    md5_hash,
    sha1_hash,
    sha256_hash,
    sha512_hash,
    identify_hash,
    verify_hash,
    hash_all_types
)

__all__ = [
    # Classical cryptography
    'caesar_encrypt', 
    'caesar_decrypt', 
    'caesar_brute_force',
    'vigenere_encrypt', 
    'vigenere_decrypt',
    
    # Modern cryptography
    'base64_encode', 
    'base64_decode', 
    'is_base64',
    'xor_encrypt',
    'xor_decrypt_hex',
    'xor_brute_force_single_byte',
    
    # Hashing
    'md5_hash',
    'sha1_hash',
    'sha256_hash',
    'sha512_hash',
    'identify_hash',
    'verify_hash',
    'hash_all_types'
]