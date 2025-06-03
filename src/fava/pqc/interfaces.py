# src/fava/pqc/interfaces.py
"""
Interfaces and data structures for PQC cryptographic agility.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypedDict # Using TypedDict for HybridEncryptedBundle as per pseudocode

class HybridEncryptedBundle(TypedDict):
    """
    Structure for hybrid encrypted data bundle.
    Based on pseudocode: STRUCTURE HybridEncryptedBundle
    """
    format_identifier: str
    suite_id_used: str
    classical_kem_ephemeral_public_key: bytes
    pqc_kem_encapsulated_key: bytes
    symmetric_cipher_iv_or_nonce: bytes
    encrypted_data_ciphertext: bytes
    authentication_tag: bytes
    kdf_salt_for_passphrase_derived_keys: Optional[bytes]
    kdf_salt_for_hybrid_sk_derivation: Optional[bytes]

class KeyMaterialForEncryption(TypedDict):
    """
    Key material required for hybrid encryption.
    Based on pseudocode: STRUCTURE KeyMaterialForEncryption
    """
    classical_recipient_pk: bytes
    pqc_recipient_pk: bytes
    kdf_salt_for_passphrase_derived_keys: Optional[bytes]

class KeyMaterialForDecryption(TypedDict):
    """
    Key material required for hybrid decryption.
    Based on pseudocode: STRUCTURE KeyMaterialForDecryption
    """
    classical_recipient_sk: bytes
    pqc_recipient_sk: bytes

class CryptoHandler(ABC):
    """
    Abstract Base Class for cryptographic handlers.
    Based on pseudocode: INTERFACE CryptoHandler
    """

    @abstractmethod
    def get_suite_id(self) -> str:
        """Returns the unique identifier of the suite this handler implements."""
        pass

    @abstractmethod
    def encrypt(
        self,
        plaintext: bytes,
        key_material: KeyMaterialForEncryption, # Updated type hint
        suite_specific_config: Dict[str, Any]
    ) -> HybridEncryptedBundle:
        """
        Encrypts the given plaintext.
        Returns a HybridEncryptedBundle.
        """
        pass

    @abstractmethod
    def decrypt(
        self,
        bundle: HybridEncryptedBundle,
        key_material: KeyMaterialForDecryption, # Updated type hint
        suite_specific_config: Dict[str, Any]
    ) -> bytes:
        """
        Decrypts the given HybridEncryptedBundle.
        Returns the original plaintext.
        """
        pass

class HasherInterface(ABC):
    """
    Abstract Base Class for hashing implementations.
    """
    @abstractmethod
    def hash(self, data: bytes) -> bytes:
        """Computes the hash of the given data."""
        pass