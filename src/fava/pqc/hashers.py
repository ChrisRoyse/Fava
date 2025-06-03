# src/fava/pqc/hashers.py
"""
Concrete hasher implementations.
"""
import hashlib
from .interfaces import HasherInterface

class SHA256HasherImpl(HasherInterface):
    """
    A SHA256 hasher implementation.
    """
    def hash(self, data: bytes) -> bytes:
        """Computes the SHA256 hash of the given data."""
        return hashlib.sha256(data).digest()

    def hash_string_to_hex(self, data_str: str) -> str:
        """Computes the SHA256 hash of a string and returns hex digest."""
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

class SHA3_256HasherImpl(HasherInterface):
    """
    A SHA3-256 hasher implementation.
    """
    def hash(self, data: bytes) -> bytes:
        """Computes the SHA3-256 hash of the given data."""
        return hashlib.sha3_256(data).digest()

    def hash_string_to_hex(self, data_str: str) -> str:
        """Computes the SHA3-256 hash of a string and returns hex digest."""
        return hashlib.sha3_256(data_str.encode('utf-8')).hexdigest()

# Add other hasher implementations as needed.