"""Crypto helper functions for FavaLedger."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, Any

from beancount.loader import load_string, LoadError as BeancountLoaderError
from beancount.core.data import Directive as BeancountDirective

log = logging.getLogger(__name__)


def PROMPT_USER_FOR_PASSPHRASE_SECURELY(prompt: str) -> str:
    # In a real app, this would securely prompt the user.
    # For tests, this will be mocked.
    return "default_mock_passphrase_if_not_mocked"


def RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(context_id: str, salt_len: int = 16) -> bytes:
    """
    Retrieve or generate a salt for a given context.
    
    In a production environment, this would:
    - Check a secure storage for existing salts by context_id
    - Generate a new cryptographically secure salt if not found
    - Store the salt securely for future use
    
    Args:
        context_id: Unique identifier for the context requiring a salt
        salt_len: Desired length of the salt in bytes (default: 16)
    
    Returns:
        A bytes object containing the salt
    """
    # For development/testing, generate a deterministic salt based on context_id
    # In production, this should use os.urandom(salt_len) and proper storage
    import hashlib
    context_bytes = context_id.encode('utf-8')
    # Create a deterministic but unique salt for each context
    salt_seed = hashlib.sha256(context_bytes).digest()
    
    # Extend or truncate to requested length
    if salt_len <= 32:
        return salt_seed[:salt_len]
    else:
        # For longer salts, repeat and hash
        result = salt_seed
        while len(result) < salt_len:
            result += hashlib.sha256(result).digest()
        return result[:salt_len]


def WRITE_BYTES_TO_FILE(file_path: str, data: bytes) -> None:
    Path(file_path).write_bytes(data)  # Basic implementation for now


def READ_BYTES_FROM_FILE(file_path: str) -> bytes:
    return Path(file_path).read_bytes()  # Basic implementation for now


def parse_beancount_file_from_source(source: str) -> Tuple[list[BeancountDirective], list[Any], dict[str, Any]]:
    """Parse Beancount directives from a string source.
    
    Args:
        source: The Beancount source code as a string.
        
    Returns:
        A tuple of (entries, errors, options_map) as returned by beancount.loader.
    """
    try:
        return load_string(source, dedent=True)
    except BeancountLoaderError as e:
        log.error(f"Beancount parsing error: {e}")
        return [], [f"Beancount parsing error: {e}"], {}
    except Exception as e:
        log.error(f"Unexpected error parsing Beancount source: {e}")
        return [], [f"Unexpected parsing error: {e}"], {}