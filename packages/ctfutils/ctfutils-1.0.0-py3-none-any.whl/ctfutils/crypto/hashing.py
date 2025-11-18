"""Hashing and hash analysis utilities."""

import hashlib
from ..exceptions import CryptoError


def md5_hash(data: str) -> str:
    """
    Generate MD5 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        MD5 hash as hex string
        
    Example:
        >>> md5_hash("Hello World")
        'b10a8db164e0754105b7a99be72e3fe5'
    """
    if not isinstance(data, str):
        raise CryptoError("Data must be a string")
    
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def sha1_hash(data: str) -> str:
    """
    Generate SHA1 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        SHA1 hash as hex string
        
    Example:
        >>> sha1_hash("Hello World")
        '0a4d55a8d778e5022fab701977c5d840bbc486d0'
    """
    if not isinstance(data, str):
        raise CryptoError("Data must be a string")
    
    return hashlib.sha1(data.encode('utf-8')).hexdigest()


def sha256_hash(data: str) -> str:
    """
    Generate SHA256 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        SHA256 hash as hex string
        
    Example:
        >>> sha256_hash("Hello World")
        'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'
    """
    if not isinstance(data, str):
        raise CryptoError("Data must be a string")
    
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def sha512_hash(data: str) -> str:
    """
    Generate SHA512 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        SHA512 hash as hex string
        
    Example:
        >>> sha512_hash("Hello World")
        '2c74fd17edafd80e8447b0d46741ee243b7eb74dd2149a0ab1b9246fb30382f27e853d8585719e0e67cbda0daa8f51671064615d645ae27acb15bfb1447f459b'
    """
    if not isinstance(data, str):
        raise CryptoError("Data must be a string")
    
    return hashlib.sha512(data.encode('utf-8')).hexdigest()


def identify_hash(hash_string: str) -> str:
    """
    Try to identify hash type based on length.
    
    Args:
        hash_string: Hash to identify
        
    Returns:
        Possible hash type
        
    Example:
        >>> identify_hash("5d41402abc4b2a76b9719d911017c592")
        'MD5'
    """
    hash_length = len(hash_string)
    
    if hash_length == 32:
        return "MD5"
    elif hash_length == 40:
        return "SHA1"
    elif hash_length == 64:
        return "SHA256"
    elif hash_length == 128:
        return "SHA512"
    else:
        return "Unknown"


def verify_hash(data: str, hash_value: str, hash_type: str = "md5") -> bool:
    """
    Verify if data matches the given hash.
    
    Args:
        data: Original data
        hash_value: Hash to verify against
        hash_type: Type of hash (md5, sha1, sha256, sha512)
        
    Returns:
        True if hash matches
        
    Example:
        >>> verify_hash("hello", "5d41402abc4b2a76b9719d911017c592", "md5")
        True
    """
    hash_functions = {
        'md5': md5_hash,
        'sha1': sha1_hash,
        'sha256': sha256_hash,
        'sha512': sha512_hash
    }
    
    if hash_type.lower() not in hash_functions:
        raise CryptoError(f"Unsupported hash type: {hash_type}")
    
    computed_hash = hash_functions[hash_type.lower()](data)
    return computed_hash.lower() == hash_value.lower()


def hash_all_types(data: str) -> dict:
    """
    Generate all supported hash types for data.
    
    Args:
        data: Data to hash
        
    Returns:
        Dictionary with all hash types
        
    Example:
        >>> hashes = hash_all_types("hello")
        >>> 'md5' in hashes
        True
    """
    return {
        'md5': md5_hash(data),
        'sha1': sha1_hash(data),
        'sha256': sha256_hash(data),
        'sha512': sha512_hash(data)
    }