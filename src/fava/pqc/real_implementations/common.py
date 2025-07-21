"""
Common utilities and base classes for real cryptographic implementations.
"""

import secrets
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SecureMemoryManager:
    """Handles secure memory operations for cryptographic data."""
    
    @staticmethod
    def secure_zero(data: bytearray) -> None:
        """Securely zero memory."""
        if isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = 0
    
    @staticmethod
    def generate_secure_random(length: int) -> bytes:
        """Generate cryptographically secure random bytes."""
        if not isinstance(length, int) or length < 1 or length > 1024:
            raise ValueError(f"Invalid random bytes length: {length} (must be 1-1024)")
        return secrets.token_bytes(length)
    
    @staticmethod
    def secure_compare(a: bytes, b: bytes) -> bool:
        """Constant-time comparison to prevent timing attacks."""
        return secrets.compare_digest(a, b)


def validate_algorithm_parameter(algorithm: str, supported_algorithms: Dict[str, Any], 
                                operation_name: str) -> None:
    """
    Validate that an algorithm parameter is supported.
    
    Args:
        algorithm: Algorithm name to validate
        supported_algorithms: Dictionary of supported algorithms
        operation_name: Name of the operation for error messages
        
    Raises:
        UnsupportedAlgorithmError: If algorithm is not supported
    """
    from .crypto_exceptions import UnsupportedAlgorithmError
    
    if algorithm not in supported_algorithms:
        raise UnsupportedAlgorithmError(
            f"Unsupported algorithm for {operation_name}: {algorithm}. "
            f"Supported: {list(supported_algorithms.keys())}"
        )


def validate_key_length(key: bytes, expected_length: int, key_type: str) -> None:
    """
    Validate that a key has the expected length.
    
    Args:
        key: Key bytes to validate
        expected_length: Expected length in bytes
        key_type: Description of key type for error messages
        
    Raises:
        CryptoError: If key length is invalid
    """
    from .crypto_exceptions import CryptoError
    
    if not isinstance(key, bytes):
        raise CryptoError(f"{key_type} must be bytes")
        
    if len(key) != expected_length:
        raise CryptoError(
            f"Invalid {key_type} length: {len(key)} bytes (expected {expected_length})"
        )