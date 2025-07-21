"""
Standalone exception classes for real cryptographic implementations.

This module provides exception classes without any circular dependencies,
allowing the real_implementations modules to be imported independently.
"""


class CryptoError(Exception):
    """Base exception for all cryptographic errors."""
    pass


class UnsupportedAlgorithmError(CryptoError):
    """Raised when an unsupported algorithm is requested."""
    pass


class InvalidArgumentError(CryptoError):
    """Raised when invalid arguments are provided to crypto functions."""
    pass


class KeyGenerationError(CryptoError):
    """Raised when key generation fails."""
    pass


class EncryptionFailedError(CryptoError):
    """Raised when encryption operations fail."""
    pass


class DecryptionError(CryptoError):
    """Raised when decryption operations fail."""
    pass


class HashingOperationFailedError(CryptoError):
    """Raised when hashing operations fail."""
    pass


class InvalidKeyError(CryptoError):
    """Raised when a key is invalid or corrupted."""
    pass


class KeyManagementError(CryptoError):
    """Raised when key management operations fail."""
    pass