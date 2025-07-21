"""FavaLedger - Core ledger module imports."""

from __future__ import annotations

# Import compatibility modules
from . import fava_keys

# Import required functions from crypto_helpers for test compatibility
from .crypto_helpers import (
    PROMPT_USER_FOR_PASSPHRASE_SECURELY,
    RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT,
    WRITE_BYTES_TO_FILE,
    READ_BYTES_FROM_FILE,
    parse_beancount_file_from_source,
)

# Import FavaLedger separately to avoid circular import
# This will be imported lazily when needed

# Re-export for backwards compatibility
__all__ = [
    'fava_keys',
    'PROMPT_USER_FOR_PASSPHRASE_SECURELY',
    'RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT',
    'WRITE_BYTES_TO_FILE',
    'READ_BYTES_FROM_FILE',
    'parse_beancount_file_from_source',
    'FavaLedger',
]