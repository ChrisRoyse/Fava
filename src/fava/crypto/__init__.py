"""
Fava Cryptographic Services Module

This module provides post-quantum cryptographic capabilities for data at rest encryption.
It implements a hybrid PQC scheme using Kyber ML-KEM-768 + X25519 + AES-256-GCM.
"""

__version__ = "1.0.0"
__all__ = ["keys", "handlers", "locator", "exceptions"]