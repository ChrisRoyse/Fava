"""
Cryptographic exceptions for the Fava PQC module.
"""


class CryptoError(Exception):
    """Base exception for cryptographic operations."""
    pass


class KeyGenerationError(CryptoError):
    """Raised when key generation fails."""
    pass


class EncryptionError(CryptoError):
    """Raised when encryption operations fail."""
    pass


class DecryptionError(CryptoError):
    """Raised when decryption operations fail."""
    pass


class InvalidKeyError(CryptoError):
    """Raised when a key is invalid or corrupted."""
    pass


class UnsupportedAlgorithmError(CryptoError):
    """Raised when an unsupported algorithm is requested."""
    pass