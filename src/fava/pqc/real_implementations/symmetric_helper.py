"""
Real symmetric encryption implementation using AES-256-GCM.

This module replaces the placeholder SymmetricCipherLibraryHelper with actual cryptographic operations.
"""

import logging
from typing import Optional, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .crypto_exceptions import (
    CryptoError,
    UnsupportedAlgorithmError,
    InvalidArgumentError
)
from .common import validate_algorithm_parameter, validate_key_length

logger = logging.getLogger(__name__)


class RealSymmetricCipherLibraryHelper:
    """Real implementation of symmetric encryption using AES-GCM."""
    
    SUPPORTED_ALGORITHMS = {
        "AES256GCM": {
            "key_length": 32,      # 256 bits
            "nonce_length": 12,    # 96 bits (recommended for GCM)
            "tag_length": 16       # 128 bits
        },
        "AES128GCM": {
            "key_length": 16,      # 128 bits
            "nonce_length": 12,    # 96 bits
            "tag_length": 16       # 128 bits
        }
    }
    
    @staticmethod
    def encrypt_aead(
        symmetric_alg: str,
        key: bytes,
        iv: bytes,
        plaintext: bytes,
        aad: Optional[bytes]
    ) -> Dict[str, bytes]:
        """
        Real AES-256-GCM encryption.
        
        Args:
            symmetric_alg: Must be "AES256GCM" or "AES128GCM"
            key: AES key (32 bytes for AES256, 16 bytes for AES128)
            iv: Nonce/IV (12 bytes for GCM)
            plaintext: Data to encrypt
            aad: Additional authenticated data (optional)
            
        Returns:
            Dict with 'ciphertext' and 'authentication_tag'
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
            InvalidArgumentError: If parameters are invalid
            CryptoError: If encryption fails
        """
        validate_algorithm_parameter(
            symmetric_alg,
            RealSymmetricCipherLibraryHelper.SUPPORTED_ALGORITHMS,
            "symmetric encryption"
        )
        
        alg_params = RealSymmetricCipherLibraryHelper.SUPPORTED_ALGORITHMS[symmetric_alg]
        
        # Validate input parameters
        validate_key_length(key, alg_params["key_length"], f"{symmetric_alg} key")
        validate_key_length(iv, alg_params["nonce_length"], f"{symmetric_alg} nonce")
        
        if not isinstance(plaintext, bytes):
            raise InvalidArgumentError("Plaintext must be bytes")
        
        if aad is not None and not isinstance(aad, bytes):
            raise InvalidArgumentError("Additional authenticated data must be bytes")
        
        try:
            aesgcm = AESGCM(key)
            
            # AES-GCM encrypt returns ciphertext + tag concatenated
            ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, aad)
            
            # Split ciphertext and tag (tag is last 16 bytes)
            tag_length = alg_params["tag_length"]
            if len(ciphertext_with_tag) < tag_length:
                raise CryptoError("Encrypted output too short to contain authentication tag")
            
            ciphertext = ciphertext_with_tag[:-tag_length]
            authentication_tag = ciphertext_with_tag[-tag_length:]
            
            logger.debug(f"Successfully encrypted {len(plaintext)} bytes using {symmetric_alg}")
            
            return {
                'ciphertext': ciphertext,
                'authentication_tag': authentication_tag
            }
            
        except Exception as e:
            raise CryptoError(f"{symmetric_alg} encryption failed: {e}") from e
    
    @staticmethod
    def decrypt_aead(
        symmetric_alg: str,
        key: bytes,
        iv: bytes,
        ciphertext: bytes,
        tag: bytes,
        aad: Optional[bytes]
    ) -> Optional[bytes]:
        """
        Real AES-256-GCM decryption.
        
        Args:
            symmetric_alg: Must be "AES256GCM" or "AES128GCM"
            key: AES key (32 bytes for AES256, 16 bytes for AES128)
            iv: Nonce/IV (12 bytes)
            ciphertext: Encrypted data
            tag: Authentication tag (16 bytes)
            aad: Additional authenticated data (optional)
            
        Returns:
            Decrypted plaintext or None if authentication fails
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
            InvalidArgumentError: If parameters are invalid
        """
        validate_algorithm_parameter(
            symmetric_alg,
            RealSymmetricCipherLibraryHelper.SUPPORTED_ALGORITHMS,
            "symmetric decryption"
        )
        
        alg_params = RealSymmetricCipherLibraryHelper.SUPPORTED_ALGORITHMS[symmetric_alg]
        
        # Validate input parameters
        validate_key_length(key, alg_params["key_length"], f"{symmetric_alg} key")
        validate_key_length(iv, alg_params["nonce_length"], f"{symmetric_alg} nonce")
        validate_key_length(tag, alg_params["tag_length"], f"{symmetric_alg} authentication tag")
        
        if not isinstance(ciphertext, bytes):
            raise InvalidArgumentError("Ciphertext must be bytes")
        
        if aad is not None and not isinstance(aad, bytes):
            raise InvalidArgumentError("Additional authenticated data must be bytes")
        
        try:
            aesgcm = AESGCM(key)
            
            # Concatenate ciphertext and tag for decryption
            ciphertext_with_tag = ciphertext + tag
            
            # Decrypt and verify
            plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, aad)
            
            logger.debug(f"Successfully decrypted {len(plaintext)} bytes using {symmetric_alg}")
            return plaintext
            
        except Exception as e:
            # Authentication failure or other decryption error
            logger.warning(f"{symmetric_alg} decryption failed: {e}")
            return None