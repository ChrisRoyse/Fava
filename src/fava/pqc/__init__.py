# src/fava/pqc/__init__.py
"""
Fava Post-Quantum Cryptography (PQC) Agility Package.

This package provides the framework for cryptographic agility within Fava,
allowing for configurable and updatable cryptographic algorithms.
"""

from .exceptions import (
    PQCError,
    CriticalConfigurationError,
    ConfigurationError,
    ParsingError,
    AlgorithmNotFoundError,
    AlgorithmUnavailableError,
    InvalidArgumentError,
    DecryptionError,
    EncryptionFailedError,
    HashingOperationFailedError,
    ApplicationStartupError,
    BundleParsingError,
    CryptoError,
    UnsupportedAlgorithmError,
)
from .global_config import (
    GlobalConfig,
    FAVA_CRYPTO_SETTINGS_PATH,
    FAVA_CRYPTO_SETTINGS_ExpectedSchema
)
from .interfaces import (
    CryptoHandler,
    HybridEncryptedBundle,
    KeyMaterialForEncryption,
    KeyMaterialForDecryption,
    HasherInterface,
)
from .backend_crypto_service import (
    BackendCryptoService,
    HybridPqcCryptoHandler,
    HashingProvider,
    decrypt_data_at_rest_with_agility,
    parse_common_encrypted_bundle_header,
)
from .frontend_crypto_facade import FrontendCryptoFacade
from .app_startup import initialize_backend_crypto_service

__all__ = [
    # Exceptions
    "PQCError",
    "CriticalConfigurationError",
    "ConfigurationError",
    "ParsingError",
    "AlgorithmNotFoundError",
    "AlgorithmUnavailableError",
    "InvalidArgumentError",
    "DecryptionError",
    "EncryptionFailedError",
    "HashingOperationFailedError",
    "ApplicationStartupError",
    "BundleParsingError",
    "CryptoError",
    "UnsupportedAlgorithmError",
    # Global Config
    "GlobalConfig",
    "FAVA_CRYPTO_SETTINGS_PATH",
    "FAVA_CRYPTO_SETTINGS_ExpectedSchema",
    # Interfaces
    "CryptoHandler",
    "HybridEncryptedBundle",
    "KeyMaterialForEncryption",
    "KeyMaterialForDecryption",
    "HasherInterface",
    # Backend Service
    "BackendCryptoService",
    "HybridPqcCryptoHandler",
    "HashingProvider",
    "decrypt_data_at_rest_with_agility",
    "parse_common_encrypted_bundle_header",
    # Frontend Facade (conceptual Python representation)
    "FrontendCryptoFacade",
    # App Startup
    "initialize_backend_crypto_service",
]