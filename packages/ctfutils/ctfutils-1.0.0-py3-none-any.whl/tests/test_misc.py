"""Tests for misc module."""

import pytest
from ctfutils.misc.encodings import hex_encode, hex_decode, binary_encode, binary_decode, morse_encode, morse_decode
from ctfutils.misc.converters import ascii_to_hex, hex_to_ascii, decimal_to_binary, binary_to_decimal
from ctfutils.misc.utils import calculate_entropy, gcd, is_prime, hamming_distance
from ctfutils.exceptions import EncodingError

class TestEncodings:
    def test_hex_encode_decode(self):
        text = "Hello"
        encoded = hex_encode(text)
        assert encoded == "48656c6c6f"
        assert hex_decode(encoded) == text
    
    def test_binary_encode_decode(self):
        text = "Hi"
        encoded = binary_encode(text)
        decoded = binary_decode(encoded)
        assert decoded == text
    
    def test_morse_encode_decode(self):
        text = "SOS"
        encoded = morse_encode(text)
        assert encoded == "... --- ..."
        decoded = morse_decode(encoded)
        assert decoded == text

class TestConverters:
    def test_ascii_to_hex(self):
        assert ascii_to_hex("ABC") == "414243"
        assert ascii_to_hex("ABC", " ") == "41 42 43"
    
    def test_hex_to_ascii(self):
        assert hex_to_ascii("414243") == "ABC"
        assert hex_to_ascii("41 42 43") == "ABC"
    
    def test_decimal_binary_conversion(self):
        assert decimal_to_binary(10) == "00001010"
        assert binary_to_decimal("00001010") == 10

class TestUtils:
    def test_calculate_entropy(self):
        # High entropy (random-ish)
        high_entropy = calculate_entropy("abcdefghijklmnopqrstuvwxyz")
        # Low entropy (repetitive)
        low_entropy = calculate_entropy("aaaaaaaaaa")
        assert high_entropy > low_entropy
    
    def test_gcd(self):
        assert gcd(12, 8) == 4
        assert gcd(17, 13) == 1
        assert gcd(100, 25) == 25
    
    def test_is_prime(self):
        assert is_prime(2) == True
        assert is_prime(17) == True
        assert is_prime(4) == False
        assert is_prime(1) == False
    
    def test_hamming_distance(self):
        assert hamming_distance("abc", "abd") == 1
        assert hamming_distance("abc", "abc") == 0
        assert hamming_distance("abc", "xyz") == 3