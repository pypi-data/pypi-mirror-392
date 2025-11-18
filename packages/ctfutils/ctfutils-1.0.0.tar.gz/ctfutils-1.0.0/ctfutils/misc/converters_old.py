"""Format converters and transformations."""

from typing import List, Union
from ..exceptions import EncodingError


class NumberConverter:
    """Number base conversion utilities."""
    
    @staticmethod
    def decimal_to_binary(number: int, padding: int = 8) -> str:
        """
        Convert decimal to binary.
        
        Args:
            number: Decimal number
            padding: Minimum number of bits
            
        Returns:
            Binary string
        """
        return format(number, f'0{padding}b')

    @staticmethod
    def binary_to_decimal(binary: str) -> int:
        """
        Convert binary to decimal.
        
        Args:
            binary: Binary string
            
        Returns:
            Decimal number
        """
        try:
            return int(binary, 2)
        except ValueError:
            raise EncodingError("Invalid binary string")

    @staticmethod
    def decimal_to_hex(number: int, padding: int = 2) -> str:
        """
        Convert decimal to hexadecimal.
        
        Args:
            number: Decimal number
            padding: Minimum hex digits
            
        Returns:
            Hex string
        """
        return format(number, f'0{padding}x')

    @staticmethod
    def hex_to_decimal(hex_string: str) -> int:
        """
        Convert hexadecimal to decimal.
        
        Args:
            hex_string: Hex string
            
        Returns:
            Decimal number
        """
        try:
            return int(hex_string, 16)
        except ValueError:
            raise EncodingError("Invalid hex string")


class TextConverter:
    """Text and ASCII conversion utilities."""
    
    @staticmethod
    def ascii_to_hex(text: str, separator: str = '') -> str:
        """
        Convert ASCII text to hexadecimal.
        
        Args:
            text: Text to convert
            separator: Separator between hex values
            
        Returns:
            Hex representation
            
        Example:
            >>> TextConverter.ascii_to_hex("ABC", " ")
            '41 42 43'
        """
        hex_values = [format(ord(char), '02x') for char in text]
        return separator.join(hex_values)

    @staticmethod
    def hex_to_ascii(hex_string: str) -> str:
        """
        Convert hexadecimal to ASCII text.
        
        Args:
            hex_string: Hex string (with or without separators)
            
        Returns:
            ASCII text
        """
        # Remove common separators
        hex_string = hex_string.replace(' ', '').replace(':', '').replace('-', '')
        
        try:
            return ''.join([chr(int(hex_string[i:i+2], 16)) for i in range(0, len(hex_string), 2)])
        except Exception as e:
            raise EncodingError(f"Invalid hex string: {e}")

    @staticmethod
    def text_to_ascii_values(text: str, separator: str = ' ') -> str:
        """
        Convert text to ASCII values.
        
        Args:
            text: Input text
            separator: Separator between values
            
        Returns:
            ASCII values string
            
        Example:
            >>> TextConverter.text_to_ascii_values("Hi")
            '72 105'
        """
        return separator.join([str(ord(char)) for char in text])

    @staticmethod
    def ascii_values_to_text(ascii_values: str) -> str:
        """
        Convert ASCII values to text.
        
        Args:
            ascii_values: Space or comma separated ASCII values
            
        Returns:
            Converted text
        """
        try:
            # Handle different separators
            if ',' in ascii_values:
                values = ascii_values.split(',')
            else:
                values = ascii_values.split()
            
            return ''.join([chr(int(val.strip())) for val in values])
        except Exception as e:
            raise EncodingError(f"Invalid ASCII values: {e}")


class StringManipulator:
    """String manipulation and transformation utilities."""
    
    @staticmethod
    def reverse_string(text: str) -> str:
        """
        Reverse a string.
        
        Args:
            text: Input text
            
        Returns:
            Reversed text
        """
        return text[::-1]

    @staticmethod
    def swap_case(text: str) -> str:
        """
        Swap case of all letters.
        
        Args:
            text: Input text
            
        Returns:
            Case-swapped text
        """
        return text.swapcase()

    @staticmethod
    def remove_whitespace(text: str, replace_with: str = '') -> str:
        """
        Remove all whitespace from text.
        
        Args:
            text: Input text
            replace_with: What to replace whitespace with
            
        Returns:
            Text without whitespace
        """
        import re
        return re.sub(r'\s+', replace_with, text)

    @staticmethod
    def chunk_string(text: str, chunk_size: int) -> List[str]:
        """
        Split string into chunks of specified size.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    @staticmethod
    def interleave_strings(str1: str, str2: str) -> str:
        """
        Interleave characters from two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Interleaved string
        """
        result = ""
        max_len = max(len(str1), len(str2))
        
        for i in range(max_len):
            if i < len(str1):
                result += str1[i]
            if i < len(str2):
                result += str2[i]
        
        return result

    @staticmethod
    def extract_numbers(text: str) -> List[int]:
        """
        Extract all numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of numbers found
        """
        import re
        return [int(match) for match in re.findall(r'-?\d+', text)]

    @staticmethod
    def extract_letters(text: str) -> str:
        """
        Extract only letters from text.
        
        Args:
            text: Input text
            
        Returns:
            Only letters
        """
        return ''.join([char for char in text if char.isalpha()])

    @staticmethod
    def char_frequency(text: str) -> dict:
        """
        Calculate character frequency.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with character frequencies
        """
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        return frequency


# Backward compatibility functions
def ascii_to_hex(text: str, separator: str = '') -> str:
    """Backward compatibility function."""
    return TextConverter.ascii_to_hex(text, separator)


def hex_to_ascii(hex_string: str) -> str:
    """Backward compatibility function."""
    return TextConverter.hex_to_ascii(hex_string)


def decimal_to_binary(number: int, padding: int = 8) -> str:
    """Backward compatibility function."""
    return NumberConverter.decimal_to_binary(number, padding)


def binary_to_decimal(binary: str) -> int:
    """Backward compatibility function."""
    return NumberConverter.binary_to_decimal(binary)


def decimal_to_hex(number: int, padding: int = 2) -> str:
    """Backward compatibility function."""
    return NumberConverter.decimal_to_hex(number, padding)


def hex_to_decimal(hex_string: str) -> int:
    """Backward compatibility function."""
    return NumberConverter.hex_to_decimal(hex_string)


def text_to_ascii_values(text: str, separator: str = ' ') -> str:
    """Backward compatibility function."""
    return TextConverter.text_to_ascii_values(text, separator)


def ascii_values_to_text(ascii_values: str) -> str:
    """Backward compatibility function."""
    return TextConverter.ascii_values_to_text(ascii_values)


def reverse_string(text: str) -> str:
    """Backward compatibility function."""
    return StringManipulator.reverse_string(text)


def swap_case(text: str) -> str:
    """Backward compatibility function."""
    return StringManipulator.swap_case(text)


def remove_whitespace(text: str, replace_with: str = '') -> str:
    """Backward compatibility function."""
    return StringManipulator.remove_whitespace(text, replace_with)


def chunk_string(text: str, chunk_size: int) -> List[str]:
    """Backward compatibility function."""
    return StringManipulator.chunk_string(text, chunk_size)


def interleave_strings(str1: str, str2: str) -> str:
    """Backward compatibility function."""
    return StringManipulator.interleave_strings(str1, str2)


def extract_numbers(text: str) -> List[int]:
    """Backward compatibility function."""
    return StringManipulator.extract_numbers(text)


def extract_letters(text: str) -> str:
    """Backward compatibility function."""
    return StringManipulator.extract_letters(text)


def char_frequency(text: str) -> dict:
    """Backward compatibility function."""
    return StringManipulator.char_frequency(text)
    try:
        # Handle different separators
        if ',' in ascii_values:
            values = ascii_values.split(',')
        else:
            values = ascii_values.split()
        
        return ''.join([chr(int(val.strip())) for val in values])
    except Exception as e:
        raise EncodingError(f"Invalid ASCII values: {e}")

def reverse_string(text: str) -> str:
    """
    Reverse a string.
    
    Args:
        text: Input text
        
    Returns:
        Reversed text
    """
    return text[::-1]

def swap_case(text: str) -> str:
    """
    Swap case of all letters.
    
    Args:
        text: Input text
        
    Returns:
        Case-swapped text
    """
    return text.swapcase()

def remove_whitespace(text: str, replace_with: str = '') -> str:
    """
    Remove all whitespace from text.
    
    Args:
        text: Input text
        replace_with: What to replace whitespace with
        
    Returns:
        Text without whitespace
    """
    import re
    return re.sub(r'\s+', replace_with, text)

def chunk_string(text: str, chunk_size: int) -> List[str]:
    """
    Split string into chunks of specified size.
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def interleave_strings(str1: str, str2: str) -> str:
    """
    Interleave characters from two strings.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Interleaved string
    """
    result = ""
    max_len = max(len(str1), len(str2))
    
    for i in range(max_len):
        if i < len(str1):
            result += str1[i]
        if i < len(str2):
            result += str2[i]
    
    return result

def extract_numbers(text: str) -> List[int]:
    """
    Extract all numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of numbers found
    """
    import re
    return [int(match) for match in re.findall(r'-?\d+', text)]

def extract_letters(text: str) -> str:
    """
    Extract only letters from text.
    
    Args:
        text: Input text
        
    Returns:
        Only letters
    """
    return ''.join([char for char in text if char.isalpha()])

def char_frequency(text: str) -> dict:
    """
    Calculate character frequency.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with character frequencies
    """
    frequency = {}
    for char in text:
        frequency[char] = frequency.get(char, 0) + 1
    return frequency