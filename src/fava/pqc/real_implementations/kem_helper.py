"""
Real KEM (Key Encapsulation Mechanism) implementation using liboqs and cryptography.

This module replaces the placeholder KEMLibraryHelper with actual cryptographic operations.
"""

import logging
from typing import Dict, Any
import oqs
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

from .crypto_exceptions import (
    CryptoError, 
    UnsupportedAlgorithmError,
    InvalidArgumentError
)
from .common import validate_algorithm_parameter, validate_key_length, SecureMemoryManager

logger = logging.getLogger(__name__)


class RealKEMLibraryHelper:
    """Real implementation of KEM operations using liboqs and cryptography."""
    
    # Supported algorithms with their parameters
    SUPPORTED_PQC_KEMS = {
        "Kyber768": {
            "public_key_length": 1184,
            "secret_key_length": 2400,
            "ciphertext_length": 1088,
            "shared_secret_length": 32
        }
    }
    
    SUPPORTED_CLASSICAL_KEMS = {
        "X25519": {
            "public_key_length": 32,
            "private_key_length": 32,
            "shared_secret_length": 32
        }
    }
    
    @staticmethod
    def pqc_kem_encapsulate(pqc_kem_alg: str, pqc_recipient_pk: bytes) -> Dict[str, bytes]:
        """
        Real Kyber768 encapsulation.
        
        Args:
            pqc_kem_alg: Must be "Kyber768"
            pqc_recipient_pk: Recipient's Kyber768 public key (1184 bytes)
            
        Returns:
            Dict with 'shared_secret' and 'encapsulated_key'
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
            CryptoError: If encapsulation fails
        """
        validate_algorithm_parameter(
            pqc_kem_alg, 
            RealKEMLibraryHelper.SUPPORTED_PQC_KEMS,
            "PQC KEM encapsulation"
        )
        
        if not isinstance(pqc_recipient_pk, bytes):
            raise InvalidArgumentError("PQC recipient public key must be bytes")
        
        kem_params = RealKEMLibraryHelper.SUPPORTED_PQC_KEMS[pqc_kem_alg]
        validate_key_length(
            pqc_recipient_pk, 
            kem_params["public_key_length"], 
            f"{pqc_kem_alg} public key"
        )
        
        try:
            with oqs.KeyEncapsulation(pqc_kem_alg) as kem:
                # Encapsulate to generate shared secret and ciphertext
                ciphertext, shared_secret = kem.encap_secret(pqc_recipient_pk)
                
                # Validate output lengths
                if len(shared_secret) != kem_params["shared_secret_length"]:
                    raise CryptoError(f"Unexpected shared secret length: {len(shared_secret)}")
                if len(ciphertext) != kem_params["ciphertext_length"]:
                    raise CryptoError(f"Unexpected ciphertext length: {len(ciphertext)}")
                
                logger.debug(f"Successfully performed {pqc_kem_alg} encapsulation")
                
                return {
                    'shared_secret': shared_secret,
                    'encapsulated_key': ciphertext
                }
                
        except oqs.MechanismNotSupportedError as e:
            raise UnsupportedAlgorithmError(f"{pqc_kem_alg} not supported by liboqs: {e}") from e
        except Exception as e:
            raise CryptoError(f"{pqc_kem_alg} encapsulation failed: {e}") from e
    
    @staticmethod
    def pqc_kem_decapsulate(pqc_kem_alg: str, encapsulated_key: bytes, recipient_sk: bytes) -> bytes:
        """
        Real Kyber768 decapsulation.
        
        Args:
            pqc_kem_alg: Must be "Kyber768"
            encapsulated_key: Ciphertext from encapsulation (1088 bytes)
            recipient_sk: Recipient's Kyber768 secret key (2400 bytes)
            
        Returns:
            Shared secret (32 bytes)
            
        Raises:
            UnsupportedAlgorithmError: If algorithm not supported
            CryptoError: If decapsulation fails
        """
        validate_algorithm_parameter(
            pqc_kem_alg,
            RealKEMLibraryHelper.SUPPORTED_PQC_KEMS,
            "PQC KEM decapsulation"
        )
        
        kem_params = RealKEMLibraryHelper.SUPPORTED_PQC_KEMS[pqc_kem_alg]
        
        validate_key_length(
            encapsulated_key,
            kem_params["ciphertext_length"],
            f"{pqc_kem_alg} ciphertext"
        )
        
        validate_key_length(
            recipient_sk,
            kem_params["secret_key_length"],
            f"{pqc_kem_alg} secret key"
        )
        
        try:
            with oqs.KeyEncapsulation(pqc_kem_alg, secret_key=recipient_sk) as kem:
                # Decapsulate to recover shared secret
                shared_secret = kem.decap_secret(encapsulated_key)
                
                # Validate output length
                if len(shared_secret) != kem_params["shared_secret_length"]:
                    raise CryptoError(f"Unexpected shared secret length: {len(shared_secret)}")
                
                logger.debug(f"Successfully performed {pqc_kem_alg} decapsulation")
                return shared_secret
                
        except oqs.MechanismNotSupportedError as e:
            raise UnsupportedAlgorithmError(f"{pqc_kem_alg} not supported by liboqs: {e}") from e
        except Exception as e:
            raise CryptoError(f"{pqc_kem_alg} decapsulation failed: {e}") from e
    
    @staticmethod
    def hybrid_kem_classical_encapsulate(classical_kem_alg: str, classical_recipient_pk: bytes) -> Dict[str, bytes]:
        """
        Real X25519 encapsulation.
        
        Args:
            classical_kem_alg: Must be "X25519"
            classical_recipient_pk: X25519 public key (32 bytes)
            
        Returns:
            Dict with 'shared_secret' and 'ephemeral_public_key'
        """
        validate_algorithm_parameter(
            classical_kem_alg,
            RealKEMLibraryHelper.SUPPORTED_CLASSICAL_KEMS,
            "Classical KEM encapsulation"
        )
        
        kem_params = RealKEMLibraryHelper.SUPPORTED_CLASSICAL_KEMS[classical_kem_alg]
        validate_key_length(
            classical_recipient_pk,
            kem_params["public_key_length"],
            f"{classical_kem_alg} public key"
        )
        
        try:
            # Load recipient's public key
            recipient_public_key = x25519.X25519PublicKey.from_public_bytes(classical_recipient_pk)
            
            # Generate ephemeral key pair
            ephemeral_private_key = x25519.X25519PrivateKey.generate()
            ephemeral_public_key_bytes = ephemeral_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            # Perform ECDH to get shared secret
            shared_secret = ephemeral_private_key.exchange(recipient_public_key)
            
            # Validate output lengths
            if len(shared_secret) != kem_params["shared_secret_length"]:
                raise CryptoError(f"Unexpected shared secret length: {len(shared_secret)}")
            if len(ephemeral_public_key_bytes) != kem_params["public_key_length"]:
                raise CryptoError(f"Unexpected ephemeral public key length: {len(ephemeral_public_key_bytes)}")
            
            logger.debug(f"Successfully performed {classical_kem_alg} encapsulation")
            
            return {
                'shared_secret': shared_secret,
                'ephemeral_public_key': ephemeral_public_key_bytes
            }
            
        except Exception as e:
            raise CryptoError(f"{classical_kem_alg} encapsulation failed: {e}") from e
    
    @staticmethod
    def hybrid_kem_classical_decapsulate(classical_kem_alg: str, ephemeral_pk: bytes, recipient_sk: bytes) -> bytes:
        """
        Real X25519 decapsulation.
        
        Args:
            classical_kem_alg: Must be "X25519"
            ephemeral_pk: Sender's ephemeral public key (32 bytes)
            recipient_sk: Recipient's X25519 private key (32 bytes)
            
        Returns:
            Shared secret (32 bytes)
        """
        validate_algorithm_parameter(
            classical_kem_alg,
            RealKEMLibraryHelper.SUPPORTED_CLASSICAL_KEMS,
            "Classical KEM decapsulation"
        )
        
        kem_params = RealKEMLibraryHelper.SUPPORTED_CLASSICAL_KEMS[classical_kem_alg]
        
        validate_key_length(
            ephemeral_pk,
            kem_params["public_key_length"],
            f"{classical_kem_alg} ephemeral public key"
        )
        
        validate_key_length(
            recipient_sk,
            kem_params["private_key_length"],
            f"{classical_kem_alg} private key"
        )
        
        try:
            # Load keys
            ephemeral_public_key = x25519.X25519PublicKey.from_public_bytes(ephemeral_pk)
            recipient_private_key = x25519.X25519PrivateKey.from_private_bytes(recipient_sk)
            
            # Perform ECDH to recover shared secret
            shared_secret = recipient_private_key.exchange(ephemeral_public_key)
            
            # Validate output length
            if len(shared_secret) != kem_params["shared_secret_length"]:
                raise CryptoError(f"Unexpected shared secret length: {len(shared_secret)}")
            
            logger.debug(f"Successfully performed {classical_kem_alg} decapsulation")
            return shared_secret
            
        except Exception as e:
            raise CryptoError(f"{classical_kem_alg} decapsulation failed: {e}") from e