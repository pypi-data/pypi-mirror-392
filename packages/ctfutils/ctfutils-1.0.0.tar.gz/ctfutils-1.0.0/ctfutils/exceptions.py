"""Custom exceptions for ctfutils library."""

class CTFUtilsError(Exception):
    """Base exception for ctfutils library."""
    pass

class CryptoError(CTFUtilsError):
    """Exception for cryptography module errors."""
    pass

class SteganographyError(CTFUtilsError):
    """Exception for steganography module errors."""
    pass

class ForensicsError(CTFUtilsError):
    """Exception for forensics module errors."""
    pass

class EncodingError(CTFUtilsError):
    """Exception for encoding/decoding errors."""
    pass