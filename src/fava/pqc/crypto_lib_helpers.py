# src/fava/pqc/crypto_lib_helpers.py
"""
Placeholder helper modules for underlying cryptographic libraries,
intended for mocking in tests of CryptoHandlers.
"""
from typing import Any, Dict, Tuple, Optional
from .interfaces import HybridEncryptedBundle # For type hinting if needed by mocks

# KEM_LIBRARY Placeholder
class KEMLibraryHelper:
    @staticmethod
    def hybrid_kem_classical_encapsulate(
        classical_kem_alg: str, classical_recipient_pk: bytes
    ) -> Dict[str, bytes]:
        raise NotImplementedError("KEMLibraryHelper.hybrid_kem_classical_encapsulate should be mocked.")

    @staticmethod
    def pqc_kem_encapsulate(
        pqc_kem_alg: str, pqc_recipient_pk: bytes
    ) -> Dict[str, bytes]:
        raise NotImplementedError("KEMLibraryHelper.pqc_kem_encapsulate should be mocked.")

    @staticmethod
    def hybrid_kem_classical_decapsulate(
        classical_kem_alg: str, ephemeral_pk: bytes, recipient_sk: bytes
    ) -> bytes:
        raise NotImplementedError("KEMLibraryHelper.hybrid_kem_classical_decapsulate should be mocked.")

    @staticmethod
    def pqc_kem_decapsulate(
        pqc_kem_alg: str, encapsulated_key: bytes, recipient_sk: bytes
    ) -> bytes:
        raise NotImplementedError("KEMLibraryHelper.pqc_kem_decapsulate should be mocked.")

# KDF_LIBRARY Placeholder
class KDFLibraryHelper:
    @staticmethod
    def derive(
        input_key_material: bytes,
        salt: Optional[bytes],
        kdf_alg: str,
        output_length: int,
        context: str
    ) -> bytes:
        raise NotImplementedError("KDFLibraryHelper.derive should be mocked.")

# SYMMETRIC_CIPHER_LIBRARY Placeholder
class SymmetricCipherLibraryHelper:
    @staticmethod
    def encrypt_aead(
        symmetric_alg: str, key: bytes, iv: bytes, plaintext: bytes, aad: Optional[bytes]
    ) -> Dict[str, bytes]:
        raise NotImplementedError("SymmetricCipherLibraryHelper.encrypt_aead should be mocked.")

    @staticmethod
    def decrypt_aead(
        symmetric_alg: str, key: bytes, iv: bytes, ciphertext: bytes, tag: bytes, aad: Optional[bytes]
    ) -> Optional[bytes]: # Returns None on auth failure
        raise NotImplementedError("SymmetricCipherLibraryHelper.decrypt_aead should be mocked.")

# UTILITY_LIBRARY Placeholder (for random bytes, key lengths etc.)
class UtilityLibraryHelper:
    @staticmethod
    def generate_random_bytes(length: int) -> bytes:
        raise NotImplementedError("UtilityLibraryHelper.generate_random_bytes should be mocked.")

    @staticmethod
    def get_symmetric_key_length(symmetric_alg: str) -> int:
        raise NotImplementedError("UtilityLibraryHelper.get_symmetric_key_length should be mocked.")

    @staticmethod
    def get_iv_length(symmetric_alg: str) -> int:
        raise NotImplementedError("UtilityLibraryHelper.get_iv_length should be mocked.")

# Expose for easy patching
KEM_LIBRARY = KEMLibraryHelper
KDF_LIBRARY = KDFLibraryHelper
SYMMETRIC_CIPHER_LIBRARY = SymmetricCipherLibraryHelper
UTILITY_LIBRARY = UtilityLibraryHelper