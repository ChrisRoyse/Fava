"""
Real utility functions for cryptographic operations.

This module replaces the placeholder UtilityLibraryHelper with actual implementations.
"""

import logging
import secrets
from typing import Dict

from .crypto_exceptions import (
    CryptoError,
    UnsupportedAlgorithmError,
    InvalidArgumentError
)

logger = logging.getLogger(__name__)


class RealUtilityLibraryHelper:
    """Real utility functions for cryptographic operations."""
    
    # Algorithm parameter lookup tables
    SYMMETRIC_KEY_LENGTHS = {
        "AES256GCM": 32,           # 256 bits
        "AES128GCM": 16,           # 128 bits
        "ChaCha20Poly1305": 32,    # 256 bits
    }
    
    IV_LENGTHS = {
        "AES256GCM": 12,           # 96 bits (recommended for GCM)
        "AES128GCM": 12,           # 96 bits
        "ChaCha20Poly1305": 12,    # 96 bits
    }
    
    # Safety limits for random byte generation
    MIN_RANDOM_BYTES = 1
    MAX_RANDOM_BYTES = 1024
    
    @staticmethod
    def generate_random_bytes(length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.
        
        Args:
            length: Number of bytes to generate (1-1024 for safety)
            
        Returns:
            Secure random bytes
            
        Raises:
            InvalidArgumentError: If length is invalid
            CryptoError: If random generation fails
        """
        if not isinstance(length, int):
            raise InvalidArgumentError("Length must be an integer")
        
        if length < RealUtilityLibraryHelper.MIN_RANDOM_BYTES or length > RealUtilityLibraryHelper.MAX_RANDOM_BYTES:
            raise InvalidArgumentError(
                f"Invalid random bytes length: {length} "
                f"(must be {RealUtilityLibraryHelper.MIN_RANDOM_BYTES}-{RealUtilityLibraryHelper.MAX_RANDOM_BYTES})"
            )
        
        try:
            random_bytes = secrets.token_bytes(length)
            logger.debug(f"Generated {length} cryptographically secure random bytes")
            return random_bytes
        except Exception as e:
            raise CryptoError(f"Random byte generation failed: {e}") from e
    
    @staticmethod
    def get_symmetric_key_length(symmetric_alg: str) -> int:
        """
        Get key length for symmetric algorithm.
        
        Args:
            symmetric_alg: Algorithm name
            
        Returns:
            Key length in bytes
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
        """
        if not isinstance(symmetric_alg, str):
            raise InvalidArgumentError("Algorithm name must be a string")
        
        if symmetric_alg not in RealUtilityLibraryHelper.SYMMETRIC_KEY_LENGTHS:
            supported_algs = list(RealUtilityLibraryHelper.SYMMETRIC_KEY_LENGTHS.keys())
            raise UnsupportedAlgorithmError(
                f"Unknown symmetric algorithm: {symmetric_alg}. "
                f"Supported: {supported_algs}"
            )
        
        return RealUtilityLibraryHelper.SYMMETRIC_KEY_LENGTHS[symmetric_alg]
    
    @staticmethod
    def get_iv_length(symmetric_alg: str) -> int:
        """
        Get IV/nonce length for symmetric algorithm.
        
        Args:
            symmetric_alg: Algorithm name
            
        Returns:
            IV length in bytes
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
        """
        if not isinstance(symmetric_alg, str):
            raise InvalidArgumentError("Algorithm name must be a string")
        
        if symmetric_alg not in RealUtilityLibraryHelper.IV_LENGTHS:
            supported_algs = list(RealUtilityLibraryHelper.IV_LENGTHS.keys())
            raise UnsupportedAlgorithmError(
                f"Unknown symmetric algorithm: {symmetric_alg}. "
                f"Supported: {supported_algs}"
            )
        
        return RealUtilityLibraryHelper.IV_LENGTHS[symmetric_alg]
    
    @staticmethod
    def secure_compare(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks.
        
        Args:
            a: First byte sequence
            b: Second byte sequence
            
        Returns:
            True if sequences are equal, False otherwise
            
        Raises:
            InvalidArgumentError: If inputs are not bytes
        """
        if not isinstance(a, bytes) or not isinstance(b, bytes):
            raise InvalidArgumentError("Both inputs must be bytes")
        
        return secrets.compare_digest(a, b)