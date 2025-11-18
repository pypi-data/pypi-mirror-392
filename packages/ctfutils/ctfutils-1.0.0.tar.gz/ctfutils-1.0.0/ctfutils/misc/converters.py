"""Format converters and transformations."""

from typing import List
from ..exceptions import EncodingError


def decimal_to_binary(number: int, padding: int = 8) -> str:
    """Convert decimal to binary."""
    return format(number, f'0{padding}b')


def binary_to_decimal(binary: str) -> int:
    """Convert binary to decimal."""
    try:
        return int(binary, 2)
    except ValueError:
        raise EncodingError("Invalid binary string")


def decimal_to_hex(number: int, padding: int = 2) -> str:
    """Convert decimal to hexadecimal."""
    return format(number, f'0{padding}x')


def hex_to_decimal(hex_string: str) -> int:
    """Convert hexadecimal to decimal."""
    try:
        return int(hex_string, 16)
    except ValueError:
        raise EncodingError("Invalid hexadecimal string")


def ascii_to_hex(text: str) -> str:
    """Convert ASCII text to hexadecimal."""
    return ''.join([format(ord(char), '02x') for char in text])


def hex_to_ascii(hex_string: str) -> str:
    """Convert hexadecimal to ASCII text."""
    try:
        bytes_data = bytes.fromhex(hex_string)
        return bytes_data.decode('ascii')
    except ValueError:
        raise EncodingError("Invalid hexadecimal string or non-ASCII characters")


def text_to_ascii_values(text: str) -> List[int]:
    """Convert text to list of ASCII values."""
    return [ord(char) for char in text]


def ascii_values_to_text(values: List[int]) -> str:
    """Convert list of ASCII values to text."""
    try:
        return ''.join([chr(val) for val in values])
    except ValueError as e:
        raise EncodingError(f"Invalid ASCII value: {e}")


def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


def swap_case(text: str) -> str:
    """Swap case of all characters in text."""
    return text.swapcase()


def remove_whitespace(text: str) -> str:
    """Remove all whitespace from text."""
    return ''.join(text.split())


def chunk_string(text: str, chunk_size: int) -> List[str]:
    """
    Split string into chunks of specified size.
    
    Args:
        text: String to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of string chunks
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def interleave_strings(str1: str, str2: str) -> str:
    """
    Interleave two strings character by character.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Interleaved string
    """
    result = []
    for c1, c2 in zip(str1, str2):
        result.append(c1)
        result.append(c2)
    
    # Add remaining characters from longer string
    if len(str1) > len(str2):
        result.append(str1[len(str2):])
    elif len(str2) > len(str1):
        result.append(str2[len(str1):])
    
    return ''.join(result)


def extract_numbers(text: str) -> str:
    """Extract all numbers from text."""
    return ''.join(filter(str.isdigit, text))


def extract_letters(text: str) -> str:
    """Extract all letters from text."""
    return ''.join(filter(str.isalpha, text))


def char_frequency(text: str) -> dict:
    """
    Calculate character frequency in text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with character frequencies
    """
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    return freq
