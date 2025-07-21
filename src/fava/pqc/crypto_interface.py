"""
Crypto interface module to decouple cryptographic operations from core modules.

This module provides the cryptographic functions needed by core modules
without creating circular dependencies.
"""

from typing import Any, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


def decrypt_data_at_rest_with_agility(
    raw_encrypted_bytes: bytes, 
    key_material_input: Any
) -> bytes:
    """
    Wrapper function that imports backend_crypto_service dynamically to avoid circular imports.
    
    Args:
        raw_encrypted_bytes: The encrypted data to decrypt
        key_material_input: Key material for decryption
        
    Returns:
        Decrypted bytes
        
    Raises:
        DecryptionError: If decryption fails
    """
    # Import here to avoid circular dependency
    from .backend_crypto_service import decrypt_data_at_rest_with_agility as _decrypt
    return _decrypt(raw_encrypted_bytes, key_material_input)


def get_backend_crypto_service():
    """
    Get the BackendCryptoService class dynamically to avoid circular imports.
    
    Returns:
        BackendCryptoService class
    """
    # Import here to avoid circular dependency
    from .backend_crypto_service import BackendCryptoService
    return BackendCryptoService


def parse_encrypted_bundle(raw_encrypted_bytes: Union[bytes, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse an encrypted bundle header dynamically to avoid circular imports.
    
    Args:
        raw_encrypted_bytes: Raw encrypted data or pre-parsed dictionary
        
    Returns:
        Dictionary with parsing results
    """
    # Import here to avoid circular dependency
    from .backend_crypto_service import parse_common_encrypted_bundle_header
    return parse_common_encrypted_bundle_header(raw_encrypted_bytes)