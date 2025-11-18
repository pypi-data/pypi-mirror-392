"""Various encoding and decoding utilities."""

import base64
import urllib.parse
import html
from typing import Dict
from ..exceptions import EncodingError

# Morse code dictionary
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}

def hex_encode(data: str) -> str:
    """
    Encode string to hexadecimal.
    
    Args:
        data: String to encode
        
    Returns:
        Hex encoded string
        
    Example:
        >>> hex_encode("Hello")
        '48656c6c6f'
    """
    if not isinstance(data, str):
        raise EncodingError("Data must be a string")
    
    return data.encode('utf-8').hex()

def hex_decode(hex_data: str) -> str:
    """
    Decode hexadecimal to string.
    
    Args:
        hex_data: Hex string to decode
        
    Returns:
        Decoded string
    """
    try:
        # Remove spaces and convert to lowercase
        hex_data = hex_data.replace(' ', '').lower()
        return bytes.fromhex(hex_data).decode('utf-8')
    except Exception as e:
        raise EncodingError(f"Invalid hex data: {e}")

def binary_encode(data: str) -> str:
    """
    Encode string to binary.
    
    Args:
        data: String to encode
        
    Returns:
        Binary string
        
    Example:
        >>> binary_encode("Hi")
        '0100100001101001'
    """
    if not isinstance(data, str):
        raise EncodingError("Data must be a string")
    
    return ''.join(format(ord(char), '08b') for char in data)

def binary_decode(binary_data: str) -> str:
    """
    Decode binary to string.
    
    Args:
        binary_data: Binary string to decode
        
    Returns:
        Decoded string
    """
    try:
        # Remove spaces
        binary_data = binary_data.replace(' ', '')
        
        if len(binary_data) % 8 != 0:
            raise EncodingError("Binary data length must be multiple of 8")
        
        result = ""
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            result += chr(int(byte, 2))
        
        return result
    except Exception as e:
        raise EncodingError(f"Invalid binary data: {e}")

def base32_encode(data: str) -> str:
    """
    Encode string to base32.
    
    Args:
        data: String to encode
        
    Returns:
        Base32 encoded string
    """
    if not isinstance(data, str):
        raise EncodingError("Data must be a string")
    
    return base64.b32encode(data.encode('utf-8')).decode('utf-8')

def base32_decode(data: str) -> str:
    """
    Decode base32 string.
    
    Args:
        data: Base32 string to decode
        
    Returns:
        Decoded string
    """
    try:
        return base64.b32decode(data).decode('utf-8')
    except Exception as e:
        raise EncodingError(f"Invalid base32 data: {e}")

def url_encode(data: str) -> str:
    """
    URL encode string.
    
    Args:
        data: String to encode
        
    Returns:
        URL encoded string
    """
    return urllib.parse.quote(data)

def url_decode(data: str) -> str:
    """
    URL decode string.
    
    Args:
        data: URL encoded string
        
    Returns:
        Decoded string
    """
    return urllib.parse.unquote(data)

def html_encode(data: str) -> str:
    """
    HTML encode string.
    
    Args:
        data: String to encode
        
    Returns:
        HTML encoded string
    """
    return html.escape(data)

def html_decode(data: str) -> str:
    """
    HTML decode string.
    
    Args:
        data: HTML encoded string
        
    Returns:
        Decoded string
    """
    return html.unescape(data)

def morse_encode(text: str) -> str:
    """
    Encode text to Morse code.
    
    Args:
        text: Text to encode
        
    Returns:
        Morse code string
        
    Example:
        >>> morse_encode("SOS")
        '... --- ...'
    """
    text = text.upper()
    morse_result = []
    
    for char in text:
        if char in MORSE_CODE:
            morse_result.append(MORSE_CODE[char])
        elif char == ' ':
            morse_result.append('/')
        else:
            morse_result.append('?')  # Unknown character
    
    return ' '.join(morse_result)

def morse_decode(morse_code: str) -> str:
    """
    Decode Morse code to text.
    
    Args:
        morse_code: Morse code string
        
    Returns:
        Decoded text
    """
    # Create reverse dictionary
    morse_to_char = {v: k for k, v in MORSE_CODE.items()}
    
    morse_words = morse_code.split('/')
    decoded_words = []
    
    for word in morse_words:
        chars = word.strip().split()
        decoded_chars = []
        
        for char_morse in chars:
            if char_morse in morse_to_char:
                decoded_chars.append(morse_to_char[char_morse])
            else:
                decoded_chars.append('?')
        
        decoded_words.append(''.join(decoded_chars))
    
    return ' '.join(decoded_words)

def rot_encode(text: str, rotation: int) -> str:
    """
    ROT encoding (generalized ROT13).
    
    Args:
        text: Text to encode
        rotation: Number of positions to rotate
        
    Returns:
        ROT encoded text
    """
    result = ""
    
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + rotation) % 26 + base)
        else:
            result += char
    
    return result

def atbash_encode(text: str) -> str:
    """
    Atbash cipher encoding.
    
    Args:
        text: Text to encode
        
    Returns:
        Atbash encoded text
    """
    result = ""
    
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += chr(ord('Z') - (ord(char) - ord('A')))
            else:
                result += chr(ord('z') - (ord(char) - ord('a')))
        else:
            result += char
    
    return result