"""Tests for crypto module."""

import pytest
from ctfutils.crypto.classical import caesar_encrypt, caesar_decrypt, vigenere_encrypt, vigenere_decrypt
from ctfutils.crypto.modern import base64_encode, base64_decode, xor_encrypt
from ctfutils.crypto.hashing import md5_hash, sha256_hash, verify_hash
from ctfutils.exceptions import CryptoError

class TestClassical:
    def test_caesar_encrypt(self):
        assert caesar_encrypt("HELLO", 3) == "KHOOR"
        assert caesar_encrypt("hello", 3) == "khoor"
        assert caesar_encrypt("Hello, World!", 13) == "Uryyb, Jbeyq!"
    
    def test_caesar_decrypt(self):
        assert caesar_decrypt("KHOOR", 3) == "HELLO"
        assert caesar_decrypt(caesar_encrypt("TEST", 5), 5) == "TEST"
    
    def test_vigenere_encrypt(self):
        assert vigenere_encrypt("HELLO", "KEY") == "RIJVS"
        assert vigenere_encrypt("hello", "key") == "rijvs"
    
    def test_vigenere_decrypt(self):
        encrypted = vigenere_encrypt("HELLO", "KEY")
        assert vigenere_decrypt(encrypted, "KEY") == "HELLO"
    
    def test_invalid_input(self):
        with pytest.raises(CryptoError):
            caesar_encrypt(123, 3)

class TestModern:
    def test_base64_encode(self):
        assert base64_encode("Hello") == "SGVsbG8="
        assert base64_encode("Hello World") == "SGVsbG8gV29ybGQ="
    
    def test_base64_decode(self):
        assert base64_decode("SGVsbG8=") == "Hello"
        assert base64_decode(base64_encode("Test")) == "Test"
    
    def test_xor_encrypt(self):
        result = xor_encrypt("Hello", "key")
        assert len(result) == 10  # 5 chars * 2 hex digits

class TestHashing:
    def test_md5_hash(self):
        assert md5_hash("Hello") == "8b1a9953c4611296a827abf8c47804d7"
        assert len(md5_hash("test")) == 32
    
    def test_sha256_hash(self):
        result = sha256_hash("Hello")
        assert len(result) == 64
        assert result == "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969"
    
    def test_verify_hash(self):
        text = "Hello World"
        md5_result = md5_hash(text)
        assert verify_hash(text, md5_result, "md5") == True
        assert verify_hash("Different", md5_result, "md5") == False