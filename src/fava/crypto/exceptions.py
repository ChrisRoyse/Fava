"""Custom exceptions for PQC-related cryptographic operations in Fava."""

class HashingAlgorithmUnavailableError(Exception):
    """Raised when a configured hashing algorithm is not available."""
    pass

class InternalHashingError(Exception):
    """Raised for unexpected internal errors during hashing operations."""
    pass

class CryptoError(Exception):
    """Base class for general PQC crypto errors."""
    pass

class KeyGenerationError(CryptoError):
    """Raised when key generation fails."""
    pass

class InvalidKeyError(CryptoError):
    """Raised when an invalid key is encountered."""
    pass

class UnsupportedAlgorithmError(CryptoError):
    """Raised when an unsupported cryptographic algorithm is requested."""
    pass

class DecryptionError(CryptoError):
    """Raised when decryption operations fail."""
    pass

class EncryptionError(CryptoError):
    """Raised when encryption operations fail."""
    pass

class KeyManagementError(CryptoError):
    """Raised when key management operations fail."""
    pass