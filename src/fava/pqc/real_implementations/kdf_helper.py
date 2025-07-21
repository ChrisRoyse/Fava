"""
Real KDF (Key Derivation Function) implementation using HKDF and Argon2id.

This module replaces the placeholder KDFLibraryHelper with actual cryptographic operations.
"""

import logging
from typing import Optional
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from argon2.low_level import hash_secret_raw, Type
import secrets

from .crypto_exceptions import (
    CryptoError,
    UnsupportedAlgorithmError,
    InvalidArgumentError
)
from .common import validate_algorithm_parameter, SecureMemoryManager

logger = logging.getLogger(__name__)


class RealKDFLibraryHelper:
    """Real implementation of KDF operations using HKDF and Argon2id."""
    
    SUPPORTED_ALGORITHMS = {
        "HKDF-SHA3-512": {
            "hash_algorithm": hashes.SHA3_512(),
            "max_output_length": 16320  # RFC 5869 limit for SHA3-512
        },
        "HKDF-SHA256": {
            "hash_algorithm": hashes.SHA256(),
            "max_output_length": 8160   # RFC 5869 limit for SHA256
        },
        "Argon2id": {
            "min_salt_length": 8,
            "max_output_length": 4294967295,  # 2^32 - 1 bytes
            "default_time_cost": 2,
            "default_memory_cost": 122880,    # 120 MiB
            "default_parallelism": 1
        }
    }
    
    @staticmethod
    def derive(
        input_key_material: bytes,
        salt: Optional[bytes],
        kdf_alg: str,
        output_length: int,
        context: str
    ) -> bytes:
        """
        Real key derivation using HKDF or Argon2id.
        
        Args:
            input_key_material: Source key material
            salt: Salt for derivation (optional for HKDF, required for Argon2id)
            kdf_alg: "HKDF-SHA3-512", "HKDF-SHA256", or "Argon2id"
            output_length: Desired output length in bytes
            context: Context string for domain separation
            
        Returns:
            Derived key material
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
            InvalidArgumentError: If parameters are invalid
            CryptoError: If derivation fails
        """
        validate_algorithm_parameter(
            kdf_alg,
            RealKDFLibraryHelper.SUPPORTED_ALGORITHMS,
            "KDF"
        )
        
        if not isinstance(input_key_material, bytes):
            raise InvalidArgumentError("Input key material must be bytes")
        
        if not isinstance(output_length, int) or output_length < 1:
            raise InvalidArgumentError("Output length must be a positive integer")
        
        if not isinstance(context, str):
            raise InvalidArgumentError("Context must be a string")
        
        # Check output length limits
        alg_params = RealKDFLibraryHelper.SUPPORTED_ALGORITHMS[kdf_alg]
        max_length = alg_params.get("max_output_length", 1024)
        if output_length > max_length:
            raise InvalidArgumentError(f"Output length {output_length} exceeds maximum {max_length} for {kdf_alg}")
        
        if kdf_alg.startswith("HKDF-"):
            return RealKDFLibraryHelper._hkdf_derive(
                input_key_material, salt, alg_params["hash_algorithm"], output_length, context
            )
        elif kdf_alg == "Argon2id":
            return RealKDFLibraryHelper._argon2id_derive(
                input_key_material, salt, output_length, context
            )
        else:
            # This should never be reached due to validate_algorithm_parameter
            raise UnsupportedAlgorithmError(f"Unsupported KDF algorithm: {kdf_alg}")
    
    @staticmethod
    def _hkdf_derive(ikm: bytes, salt: Optional[bytes], hash_alg, length: int, info: str) -> bytes:
        """HKDF derivation implementation."""
        try:
            hkdf = HKDF(
                algorithm=hash_alg,
                length=length,
                salt=salt,
                info=info.encode('utf-8'),
                backend=default_backend()
            )
            derived_key = hkdf.derive(ikm)
            
            logger.debug(f"Successfully derived {length} bytes using HKDF")
            return derived_key
            
        except Exception as e:
            raise CryptoError(f"HKDF derivation failed: {e}") from e
    
    @staticmethod
    def _argon2id_derive(password: bytes, salt: Optional[bytes], length: int, info: str) -> bytes:
        """Argon2id derivation implementation."""
        alg_params = RealKDFLibraryHelper.SUPPORTED_ALGORITHMS["Argon2id"]
        
        # Generate salt if not provided
        if salt is None:
            salt = SecureMemoryManager.generate_secure_random(16)
            logger.debug("Generated random salt for Argon2id")
        elif len(salt) < alg_params["min_salt_length"]:
            raise InvalidArgumentError(
                f"Argon2id salt must be at least {alg_params['min_salt_length']} bytes"
            )
        
        try:
            # Use OWASP recommended parameters
            derived_key = hash_secret_raw(
                secret=password,
                salt=salt,
                time_cost=alg_params["default_time_cost"],
                memory_cost=alg_params["default_memory_cost"],
                parallelism=alg_params["default_parallelism"],
                hash_len=length,
                type=Type.ID
            )
            
            logger.debug(f"Successfully derived {length} bytes using Argon2id")
            return derived_key
            
        except Exception as e:
            raise CryptoError(f"Argon2id derivation failed: {e}") from e