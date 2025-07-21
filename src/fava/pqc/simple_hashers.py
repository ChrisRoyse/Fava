"""
Simple PQC Hashers

This module provides standalone hashing functionality to avoid circular imports.
It implements the required hashers without dependencies on the full crypto service.
"""

import hashlib
from typing import Protocol


class SimpleHasher(Protocol):
    """Simple hasher interface."""
    
    def hash(self, data: bytes) -> bytes:
        """Hash data and return bytes."""
        ...
    
    def hash_str(self, data: str) -> str:
        """Hash string data and return hex string."""
        ...


class SHA256Hasher:
    """Simple SHA256 hasher implementation."""
    
    def hash(self, data: bytes) -> bytes:
        """Hash data and return bytes."""
        return hashlib.sha256(data).digest()
    
    def hash_str(self, data: str) -> str:
        """Hash string data and return hex string."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


class SHA3_256Hasher:
    """Simple SHA3-256 hasher implementation."""
    
    def hash(self, data: bytes) -> bytes:
        """Hash data and return bytes."""
        return hashlib.sha3_256(data).digest()
    
    def hash_str(self, data: str) -> str:
        """Hash string data and return hex string."""
        return hashlib.sha3_256(data.encode('utf-8')).hexdigest()


# Default hasher for basic operations
_default_hasher = SHA256Hasher()


def get_simple_hasher(algorithm: str = "SHA256") -> SimpleHasher:
    """Get a simple hasher by algorithm name."""
    if algorithm.upper() == "SHA256":
        return SHA256Hasher()
    elif algorithm.upper() == "SHA3-256":
        return SHA3_256Hasher()
    else:
        return SHA256Hasher()  # Default fallback


def simple_sha256_str(data: str) -> str:
    """Simple SHA256 string hashing function to replace _sha256_str."""
    return _default_hasher.hash_str(data)


def simple_hash_bytes(data: bytes, algorithm: str = "SHA256") -> bytes:
    """Simple byte hashing function."""
    hasher = get_simple_hasher(algorithm)
    return hasher.hash(data)