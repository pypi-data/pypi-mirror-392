"""Modern cryptography utilities."""

import base64
from ..exceptions import CryptoError


def base64_encode(data: str) -> str:
    """
    Encode string to base64.
    
    Args:
        data: String to encode
        
    Returns:
        Base64 encoded string
        
    Example:
        >>> base64_encode("Hello World")
        'SGVsbG8gV29ybGQ='
    """
    if not isinstance(data, str):
        raise CryptoError("Data must be a string")
    
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def base64_decode(data: str) -> str:
    """
    Decode base64 string.
    
    Args:
        data: Base64 encoded string
        
    Returns:
        Decoded string
        
    Example:
        >>> base64_decode("SGVsbG8gV29ybGQ=")
        'Hello World'
    """
    try:
        return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        raise CryptoError(f"Invalid base64 data: {e}")


def is_base64(data: str) -> bool:
    """
    Check if string is valid base64.
    
    Args:
        data: String to check
        
    Returns:
        True if valid base64
        
    Example:
        >>> is_base64("SGVsbG8gV29ybGQ=")
        True
    """
    try:
        if isinstance(data, str):
            sb_bytes = bytes(data, 'ascii')
        elif isinstance(data, bytes):
            sb_bytes = data
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except ValueError:
        return False


def xor_encrypt(data: str, key: str) -> str:
    """
    XOR encrypt data with key.
    
    Args:
        data: Data to encrypt
        key: XOR key
        
    Returns:
        XOR result as hex string
        
    Example:
        >>> xor_encrypt("Hello", "key")
        '03010d0c1b'
    """
    if not data or not key:
        raise CryptoError("Data and key cannot be empty")
    
    result = []
    for i, char in enumerate(data):
        key_char = key[i % len(key)]
        result.append(format(ord(char) ^ ord(key_char), '02x'))
    
    return ''.join(result)


def xor_decrypt_hex(hex_data: str, key: str) -> str:
    """
    Decrypt hex XOR data.
    
    Args:
        hex_data: Hex encoded XOR data
        key: XOR key
        
    Returns:
        Decrypted string
        
    Example:
        >>> xor_decrypt_hex("03010d0c1b", "key")
        'Hello'
    """
    try:
        # Convert hex to bytes
        data_bytes = bytes.fromhex(hex_data)
        result = []
        
        for i, byte in enumerate(data_bytes):
            key_char = key[i % len(key)]
            result.append(chr(byte ^ ord(key_char)))
        
        return ''.join(result)
    except Exception as e:
        raise CryptoError(f"Invalid hex data: {e}")


def xor_brute_force_single_byte(hex_data: str) -> dict:
    """
    Brute force single-byte XOR key.
    
    Args:
        hex_data: Hex encoded XOR data
        
    Returns:
        Dictionary with possible keys and results
        
    Example:
        >>> results = xor_brute_force_single_byte("1b1a1c1c1d")
        >>> # Returns dictionary with possible decryptions
    """
    results = {}
    
    try:
        data_bytes = bytes.fromhex(hex_data)
        
        for key_byte in range(256):
            try:
                decrypted = ''.join([chr(byte ^ key_byte) for byte in data_bytes])
                # Only include printable results
                if all(32 <= ord(c) <= 126 or c in '\n\t' for c in decrypted):
                    results[key_byte] = decrypted
            except:
                continue
                
        return results
    except Exception as e:
        raise CryptoError(f"Invalid hex data: {e}")