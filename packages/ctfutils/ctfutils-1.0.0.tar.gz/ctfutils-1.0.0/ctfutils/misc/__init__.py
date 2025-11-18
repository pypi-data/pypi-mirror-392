"""Miscellaneous utilities for CTF challenges."""

# Import encoding functions
from .encodings import (
    hex_encode, hex_decode,
    binary_encode, binary_decode,
    base32_encode, base32_decode,
    url_encode, url_decode,
    html_encode, html_decode,
    morse_encode, morse_decode,
    rot_encode, atbash_encode
)

# Import converter functions
from .converters import (
    decimal_to_binary, binary_to_decimal,
    decimal_to_hex, hex_to_decimal,
    ascii_to_hex, hex_to_ascii,
    text_to_ascii_values, ascii_values_to_text,
    reverse_string, swap_case, remove_whitespace,
    chunk_string, interleave_strings,
    extract_numbers, extract_letters, char_frequency
)

# Import utility functions
from .utils import (
    generate_wordlist, bruteforce_pattern,
    calculate_entropy, find_common_factors,
    gcd, gcd_list, lcm, is_prime, prime_factors,
    validate_input, safe_divide,
    hamming_distance, levenshtein_distance
)

__all__ = [
    # Encodings
    'hex_encode', 'hex_decode',
    'binary_encode', 'binary_decode',
    'base32_encode', 'base32_decode',
    'url_encode', 'url_decode',
    'html_encode', 'html_decode',
    'morse_encode', 'morse_decode',
    'rot_encode', 'atbash_encode',
    
    # Converters
    'decimal_to_binary', 'binary_to_decimal',
    'decimal_to_hex', 'hex_to_decimal',
    'ascii_to_hex', 'hex_to_ascii',
    'text_to_ascii_values', 'ascii_values_to_text',
    'reverse_string', 'swap_case', 'remove_whitespace',
    'chunk_string', 'interleave_strings',
    'extract_numbers', 'extract_letters', 'char_frequency',
    
    # Utils
    'generate_wordlist', 'bruteforce_pattern',
    'calculate_entropy', 'find_common_factors',
    'gcd', 'gcd_list', 'lcm', 'is_prime', 'prime_factors',
    'validate_input', 'safe_divide',
    'hamming_distance', 'levenshtein_distance'
]