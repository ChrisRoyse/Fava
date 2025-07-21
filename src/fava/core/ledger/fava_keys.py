"""
Module for fava ledger key management compatibility.

This module re-exports key management functions from the proper location
to maintain compatibility with existing test code.
"""

# Import the actual function from the crypto.keys module
from fava.crypto.keys import derive_kem_keys_from_passphrase

# Re-export for compatibility
__all__ = ['derive_kem_keys_from_passphrase']