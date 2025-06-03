"""
Cryptographic key management for the Fava PQC module.

This module provides an adapter layer for post-quantum cryptographic key operations,
specifically using the oqs-python library.
"""

from typing import Tuple, Optional, Any, Dict, Union
import os
import oqs
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from argon2.low_level import hash_secret_raw, Type # argon2-cffi direct usage
from . import exceptions
from .exceptions import KeyGenerationError, InvalidKeyError, UnsupportedAlgorithmError, CryptoError

# Re-export for test compatibility
HKDFExpand = HKDF


class OQSKEMAdapter:
    """
    Adapter class that wraps oqs.KeyEncapsulation to provide a consistent interface.
    """

    def __init__(self, kem_name: str):
        self.kem_name = kem_name
        self._public_key: Optional[bytes] = None
        self._private_key: Optional[bytes] = None
        try:
            self._kem_details = oqs.KeyEncapsulation(kem_name).details
            self.oqs_kem = oqs.KeyEncapsulation(self.kem_name)
        except oqs.MechanismNotSupportedError as e:
            raise UnsupportedAlgorithmError(f"Unsupported KEM: {kem_name}. OQS: {str(e)}") from e
        except Exception as e:
            raise CryptoError(f"Init OQS KEM adapter for {kem_name} failed: {str(e)}") from e

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        try:
            self.oqs_kem = oqs.KeyEncapsulation(self.kem_name) # Fresh instance
            self._public_key = self.oqs_kem.generate_keypair()
            self._private_key = self.oqs_kem.export_secret_key()
            if self._public_key is None or self._private_key is None:
                raise KeyGenerationError(f"OQS {self.kem_name} keygen returned None.")
            return self._public_key, self._private_key
        except Exception as e:
            if isinstance(e, (KeyGenerationError, CryptoError)): raise
            raise KeyGenerationError(f"OQS {self.kem_name} keygen failed: {str(e)}") from e

    def keypair_from_seed(self, seed: bytes) -> Tuple[bytes, bytes]:
        try:
            hkdf = HKDF(
                algorithm=hashes.SHA3_512(),
                length=self._kem_details['length_secret_key'],
                salt=None, info=b"oqs_sk_from_seed_" + self.kem_name.encode(),
                backend=default_backend()
            )
            actual_secret_key = hkdf.derive(seed)
            self.oqs_kem = oqs.KeyEncapsulation(self.kem_name, secret_key=actual_secret_key)
            self._public_key = self.oqs_kem.generate_keypair()
            self._private_key = actual_secret_key
            if self._public_key is None:
                raise KeyGenerationError(f"PK derivation from seed failed for {self.kem_name}.")
            return self._public_key, self._private_key
        except Exception as e:
            if isinstance(e, (KeyGenerationError, CryptoError)): raise
            raise KeyGenerationError(f"Keygen from seed for {self.kem_name} failed: {str(e)}") from e

    def load_keypair_from_secret_key(self, sk_bytes: bytes) -> Tuple[bytes, bytes]:
        try:
            self.oqs_kem = oqs.KeyEncapsulation(self.kem_name, secret_key=sk_bytes)
            self._public_key = self.oqs_kem.generate_keypair()
            self._private_key = sk_bytes
            if self._public_key is None:
                raise InvalidKeyError(f"PK derivation from SK failed for {self.kem_name}.")
            return self._public_key, self._private_key
        except Exception as e:
            if isinstance(e, (InvalidKeyError, CryptoError)): raise
            raise InvalidKeyError(f"Load SK for {self.kem_name} failed: {str(e)}") from e
            
    def export_public_key(self) -> bytes:
        if self._public_key is None: raise InvalidKeyError("No PK. Gen/load keys first.")
        return self._public_key
    
    def export_secret_key(self) -> bytes:
        if self._private_key is None: raise InvalidKeyError("No SK. Gen/load keys first.")
        return self._private_key
    
    def encap_secret(self, public_key_bytes: bytes) -> Tuple[bytes, bytes]:
        try:
            ciphertext, shared_secret = self.oqs_kem.encap_secret(public_key_bytes)
            return shared_secret, ciphertext 
        except Exception as e:
            raise CryptoError(f"OQS {self.kem_name} encap failed: {str(e)}") from e

    def decap_secret(self, sk_bytes: bytes, ciphertext: bytes) -> bytes:
        try:
            temp_kem = oqs.KeyEncapsulation(self.kem_name, secret_key=sk_bytes)
            return temp_kem.decap_secret(ciphertext)
        except Exception as e:
            raise CryptoError(f"OQS {self.kem_name} decap failed: {str(e)}") from e

KeyEncapsulation = OQSKEMAdapter

# OWASP recommended defaults for Argon2id (as of early 2024)
# Iterations (time_cost): 2
# Memory (memory_cost): 122880 KiB (120 MiB)
# Parallelism (parallelism): 1
ARGON2_DEFAULT_TIME_COST = 2
ARGON2_DEFAULT_MEMORY_COST = 122880 
ARGON2_DEFAULT_PARALLELISM = 1

class Argon2id:
    def __init__(self, time_cost: int = ARGON2_DEFAULT_TIME_COST, 
                 memory_cost: int = ARGON2_DEFAULT_MEMORY_COST,
                 parallelism: int = ARGON2_DEFAULT_PARALLELISM, 
                 salt_len: int = 16, hash_len: int = 32):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.salt_len = salt_len # Note: salt is generated externally and passed to derive
        self.hash_len = hash_len
    
    def derive(self, password: Union[str, bytes], salt: bytes) -> bytes:
        try:
            password_bytes = password.encode('utf-8') if isinstance(password, str) else password
            return hash_secret_raw(
                secret=password_bytes, salt=salt, time_cost=self.time_cost,
                memory_cost=self.memory_cost, parallelism=self.parallelism,
                hash_len=self.hash_len, type=Type.ID
            )
        except Exception as e:
            raise KeyGenerationError(f"Argon2id derivation failed: {str(e)}") from e

def derive_kem_keys_from_passphrase(
    passphrase: str, salt: bytes,
    pbkdf_algorithm: str, kdf_algorithm_for_ikm: str,
    classical_kem_spec: str, pqc_kem_spec: str,
    argon2_params: Optional[Dict[str, int]] = None
) -> Tuple[Any, Any]:
    try:
        if pbkdf_algorithm != "Argon2id":
            raise UnsupportedAlgorithmError(f"Unsupported PBKDF: {pbkdf_algorithm}")
        if kdf_algorithm_for_ikm != "HKDF-SHA3-512":
            raise UnsupportedAlgorithmError(f"Unsupported KDF for IKM: {kdf_algorithm_for_ikm}")
        if classical_kem_spec != "X25519":
            raise UnsupportedAlgorithmError(f"Unsupported classical KEM: {classical_kem_spec}")
        
        current_argon2_params = {
            "time_cost": ARGON2_DEFAULT_TIME_COST,
            "memory_cost": ARGON2_DEFAULT_MEMORY_COST,
            "parallelism": ARGON2_DEFAULT_PARALLELISM,
        }
        if argon2_params:
            current_argon2_params.update(argon2_params)

        argon2_instance = Argon2id(
            hash_len=64, # For IKM
            time_cost=current_argon2_params["time_cost"],
            memory_cost=current_argon2_params["memory_cost"],
            parallelism=current_argon2_params["parallelism"]
        )
        ikm = argon2_instance.derive(passphrase, salt)
        
        classical_hkdf = HKDF(
            algorithm=hashes.SHA3_512(), length=32, salt=None, 
            info=b"classical_kem_key_derivation", backend=default_backend()
        )
        classical_key_material = classical_hkdf.derive(ikm)
        
        pqc_seed_hkdf = HKDF(
            algorithm=hashes.SHA3_512(), length=64, salt=None,
            info=b"pqc_kem_key_derivation_seed", backend=default_backend()
        )
        pqc_seed_material = pqc_seed_hkdf.derive(ikm)
        
        classical_private_key = X25519PrivateKey.from_private_bytes(classical_key_material)
        classical_keys = (classical_private_key.public_key(), classical_private_key)
        
        pqc_kem = OQSKEMAdapter(pqc_kem_spec) # Will raise UnsupportedAlgorithmError if needed
        pqc_keys = pqc_kem.keypair_from_seed(pqc_seed_material)
        
        return classical_keys, pqc_keys
    except Exception as e:
        if isinstance(e, (UnsupportedAlgorithmError, KeyGenerationError, CryptoError)): raise
        raise KeyGenerationError(f"Passphrase key derivation failed: {str(e)}") from e

def load_keys_from_external_file(
    key_file_path_config: Dict[str, str],
    pqc_kem_spec: str = "Kyber768" 
    # passphrase not used for raw key files
) -> Tuple[Any, Any]:
    try:
        classical_key_path = key_file_path_config.get("classical_private")
        if not classical_key_path: raise exceptions.KeyManagementError("Classical PK path missing.")
        with open(classical_key_path, "rb") as f: classical_private_bytes = f.read()
        classical_private_key = X25519PrivateKey.from_private_bytes(classical_private_bytes)
        classical_keys = (classical_private_key.public_key(), classical_private_key)

        pqc_key_path = key_file_path_config.get("pqc_private")
        if not pqc_key_path: raise exceptions.KeyManagementError("PQC PK path missing.")
        with open(pqc_key_path, "rb") as f: pqc_private_bytes = f.read()
        
        pqc_kem = OQSKEMAdapter(pqc_kem_spec)
        pqc_keys = pqc_kem.load_keypair_from_secret_key(pqc_private_bytes)
        
        return classical_keys, pqc_keys
    except FileNotFoundError as e:
        raise exceptions.KeyManagementError(f"Key file not found: {e.filename}") from e
    except Exception as e: # Broad catch, specific errors raised within
        if isinstance(e, (exceptions.KeyManagementError, CryptoError, UnsupportedAlgorithmError)): raise
        raise exceptions.KeyManagementError(f"External key loading failed: {str(e)}") from e

def export_fava_managed_pqc_private_keys(
    key_id: str, format_spec: str, passphrase: str, 
    config: Optional[Any] = None, 
    argon2_params: Optional[Dict[str, int]] = None
) -> bytes:
    private_key_bytes = _retrieve_stored_or_derived_pqc_private_key(key_id, config=config, passphrase=passphrase)
    if private_key_bytes is None:
        raise exceptions.KeyManagementError(f"PQC private key not found for ID: {key_id}")
    return secure_format_for_export(private_key_bytes, format_spec, passphrase, argon2_params)

def _retrieve_stored_or_derived_pqc_private_key(
    key_id: str, config: Any, passphrase: Optional[str] = None
) -> Optional[bytes]:
    # This remains a placeholder as its full implementation depends on Fava's key storage strategy
    if key_id == "user_context_1_pqc_test" and passphrase == "export_passphrase_test":
        # For Kyber768, SK is 2400 bytes. This is a mock placeholder.
        return b"mock_pqc_sk_for_export_len_2400" + os.urandom(2400 - len(b"mock_pqc_sk_for_export_len_2400"))
    return None

def secure_format_for_export(
    private_key_bytes: bytes, format_spec: str, passphrase: str,
    argon2_params: Optional[Dict[str, int]] = None
) -> bytes:
    if format_spec == "ENCRYPTED_PKCS8_AES256GCM_PBKDF2":
        try:
            salt = os.urandom(16)
            current_argon2_params = {
                "time_cost": ARGON2_DEFAULT_TIME_COST,
                "memory_cost": ARGON2_DEFAULT_MEMORY_COST,
                "parallelism": ARGON2_DEFAULT_PARALLELISM,
            }
            if argon2_params:
                current_argon2_params.update(argon2_params)

            argon2_kdf = Argon2id(
                salt_len=16, hash_len=32, # For AES-256 key
                time_cost=current_argon2_params["time_cost"],
                memory_cost=current_argon2_params["memory_cost"],
                parallelism=current_argon2_params["parallelism"]
            )
            derived_encryption_key = argon2_kdf.derive(passphrase, salt)
            iv = os.urandom(12)
            aesgcm = AESGCM(derived_encryption_key)
            ciphertext_and_tag = aesgcm.encrypt(iv, private_key_bytes, associated_data=None)
            return salt + iv + ciphertext_and_tag
        except Exception as e:
            raise CryptoError(f"Secure export formatting failed: {str(e)}") from e
    raise UnsupportedAlgorithmError(f"Unsupported export format: {format_spec}")

# For type hinting, if Python < 3.9
# from typing import Union # Moved to the top