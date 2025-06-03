"""
Re-exports the HashingService and related utilities from the
fava.crypto.service module to provide a stable import path
as indicated in design documents.
"""

from fava.crypto.service import HashingService, get_hashing_service
from fava.crypto.exceptions import (
    HashingAlgorithmUnavailableError,
    InternalHashingError,
)

__all__ = [
    "HashingService",
    "get_hashing_service",
    "HashingAlgorithmUnavailableError",
    "InternalHashingError",
]