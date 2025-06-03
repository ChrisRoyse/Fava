"""
Cryptographic handlers for Fava.
"""
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization # For KDFs and key serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.backends import default_backend # For HKDF
from fava.crypto.keys import KeyEncapsulation # Alias for MLKEMBridge
from fava.core.encrypted_file_bundle import EncryptedFileBundle
from fava.crypto import exceptions # For custom exceptions
import os # For os.urandom
import subprocess
import shlex
from typing import Dict, Tuple, Any, Optional


class HybridPqcHandler:
    """
    Handles hybrid PQC encryption and decryption.
    """
    EXPECTED_FORMAT_IDENTIFIER = "FAVA_PQC_HYBRID_V1" # Added class attribute

    def __init__(self):
        """
        Initializes the HybridPqcHandler.
        """
        pass # Placeholder for now

    def can_handle(self, file_path: str, file_content_peek: Optional[bytes] = None, config: Optional[Any] = None) -> bool:
        """
        Determines if this handler can process the given file.
        Checks based on file extension or magic bytes if content is provided.

        Args:
            file_path: The path to the file.
            file_content_peek: Optional first few bytes of the file content.
            config: Fava application configuration (FavaOptions).

        Returns:
            True if the handler can process the file, False otherwise.
        """
        if file_path and file_path.endswith(".pqc_hybrid_fava"):
            return True
        
        if file_content_peek:
            header_info = EncryptedFileBundle.parse_header_only(file_content_peek)
            if header_info and header_info.get("format_identifier") == "FAVA_PQC_HYBRID_V1":
                # Further checks could be done on suite_id if needed, based on config
                return True
        return False

    def encrypt_content(self, plaintext: str, suite_config: Dict,
                        key_material_encrypt: Dict, app_config: Any) -> bytes:
        """
        Encrypts plaintext content using the hybrid PQC scheme.

        Args:
            plaintext: The string data to encrypt.
            suite_config: Configuration for the crypto suite to use.
            key_material_encrypt: Dictionary containing public keys for encryption.
                                  e.g., {"classical_public_key": ..., "pqc_public_key": ...}
            app_config: Fava application configuration (FavaOptions).

        Returns:
            The encrypted content as a serialized EncryptedFileBundle in bytes.
        """
        # Placeholder implementation
        
        # Extract PQC KEM algorithm from suite_config
        pqc_kem_algo = suite_config.get("pqc_kem_algorithm")
        if not pqc_kem_algo:
            raise exceptions.ConfigurationError("PQC KEM algorithm not specified in suite_config.")

        # Instantiate KeyEncapsulation (MLKEMBridge) with the specified algorithm
        # The test will assert that this was called with the correct algorithm name.
        pqc_kem = KeyEncapsulation(pqc_kem_algo)
        
        # --- Further placeholder logic for encryption steps ---
        # (This will be built out as subsequent tests are unskipped)

        # Get classical and PQC public keys
        classical_pk = key_material_encrypt.get("classical_public_key")
        pqc_pk = key_material_encrypt.get("pqc_public_key")

        if not classical_pk or not pqc_pk:
            raise exceptions.KeyManagementError("Missing public keys for encryption.")

        # 2. Classical KEM (X25519)
        try:
            # Ensure classical_pk is an X25519PublicKey instance
            if not isinstance(classical_pk, x25519.X25519PublicKey):
                 # Attempt to load if it's bytes, otherwise raise error
                if isinstance(classical_pk, bytes):
                    classical_pk = x25519.X25519PublicKey.from_public_bytes(classical_pk)
                else:
                    raise exceptions.KeyManagementError(
                        "Classical public key is not in a recognized format (X25519PublicKey or bytes)."
                    )

            classical_ephemeral_sk = x25519.X25519PrivateKey.generate()
            classical_ephemeral_pk_bytes = classical_ephemeral_sk.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            classical_shared_secret = classical_ephemeral_sk.exchange(classical_pk)
            classical_kem_ciphertext_for_bundle = classical_ephemeral_pk_bytes # This is sent to the recipient
        except Exception as e:
            raise exceptions.EncryptionError(f"Classical KEM (X25519) failed during encryption: {str(e)}") from e

        # 3. PQC KEM (ML-KEM)
        if pqc_pk is None: # Should be caught by earlier check, but defensive
            raise exceptions.KeyManagementError("PQC public key is missing for KEM encapsulation.")
        
        try:
            # MLKEMBridge uses encap_secret, which internally calls mlkem's encaps
            pqc_shared_secret, pqc_kem_ciphertext = pqc_kem.encap_secret(pqc_pk)
        except Exception as e: # Catch potential errors from the KEM library
            raise exceptions.EncryptionError(f"PQC KEM encapsulation failed: {str(e)}") from e
        
        # 4. Combine secrets
        combined_secret = classical_shared_secret + pqc_shared_secret # Order: classical_ss || pqc_ss

        # 5. KDF (HKDF) to derive symmetric key
        kdf_algo_name = suite_config.get("kdf_algorithm_for_hybrid_sk", "HKDF-SHA3-512")
        
        if kdf_algo_name == "HKDF-SHA3-512":
            hash_algorithm_for_kdf = hashes.SHA3_512()
        elif kdf_algo_name == "HKDF-SHA256":
            hash_algorithm_for_kdf = hashes.SHA256()
        else:
            raise exceptions.ConfigurationError(f"Unsupported KDF algorithm for symmetric key: {kdf_algo_name}")

        symmetric_algo_name = suite_config.get("symmetric_algorithm", "AES256GCM")
        if symmetric_algo_name == "AES256GCM":
            symmetric_key_length = 32  # 256 bits
        elif symmetric_algo_name == "AES128GCM":
            symmetric_key_length = 16  # 128 bits
        else:
            raise exceptions.ConfigurationError(f"Unsupported symmetric algorithm for key length: {symmetric_algo_name}")

        try:
            symmetric_kdf = HKDFExpand(
                algorithm=hash_algorithm_for_kdf,
                length=symmetric_key_length,
                info=b"fava_hybrid_pqc_symmetric_key_v1", # Standardized context string
                backend=default_backend()
            )
            symmetric_key = symmetric_kdf.derive(combined_secret)
        except Exception as e:
            raise exceptions.EncryptionError(f"Symmetric key derivation failed: {str(e)}") from e
        
        # Store symmetric_key for next steps (AES encryption)
        # self._derived_symmetric_key_for_test = symmetric_key # For debugging if needed

        # 6. Symmetric Encryption (AES-GCM)
        try:
            aesgcm = AESGCM(symmetric_key)
            # AES-GCM standard IV size is 12 bytes (96 bits).
            # It should be unpredictable and unique for each encryption with the same key.
            iv = os.urandom(12)
            
            # Encrypt plaintext. AESGCM().encrypt() returns ciphertext || tag
            ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode('utf-8'), associated_data=None)
            
            # AES-GCM tag is typically 16 bytes (128 bits), but can vary.
            # The cryptography library appends it. Standard tag size is 16 bytes.
            tag_length = 16
            if len(ciphertext_with_tag) < tag_length:
                # This case should ideally not happen with standard AES-GCM usage if plaintext is not empty.
                raise exceptions.EncryptionError("Ciphertext too short to contain authentication tag.")
            
            actual_ciphertext = ciphertext_with_tag[:-tag_length]
            auth_tag = ciphertext_with_tag[-tag_length:]
            
        except Exception as e:
            # Catch specific crypto errors if possible, or general Exception.
            raise exceptions.EncryptionError(f"AES-GCM encryption failed: {str(e)}") from e
        
        # 7. Bundle
        bundle = EncryptedFileBundle()
        bundle.format_identifier = "FAVA_PQC_HYBRID_V1"
        bundle.suite_id = suite_config.get("id", "UNKNOWN_SUITE")
        bundle.classical_kem_ciphertext = classical_kem_ciphertext_for_bundle # Store ephemeral classical part
        bundle.pqc_kem_ciphertext = pqc_kem_ciphertext
        bundle.symmetric_iv = iv
        bundle.symmetric_ciphertext = actual_ciphertext
        bundle.symmetric_auth_tag = auth_tag
        
        # For this test (004), the primary concern is that KeyEncapsulation was called correctly.
        # The placeholder return for encrypt/decrypt in test 003 made it pass.
        # Now, to make test 003 *still* pass with this more structured (but still placeholder) encrypt,
        # Now, to make test 003 *still* pass with this more structured (but still placeholder) encrypt,
        # decrypt_content needs to be able to reverse this.
        return bundle.to_bytes()

    def decrypt_content(self, encrypted_bundle_bytes: bytes, suite_config: Dict,
                        key_material_decrypt: Dict, app_config: Any) -> str:
        """
        Decrypts content from an EncryptedFileBundle.
        """
        try:
            # 1. Parse encrypted_bundle_bytes into EncryptedFileBundle object
            bundle = EncryptedFileBundle.from_bytes(encrypted_bundle_bytes)

            # 2. Validate format_identifier, suite_id (basic checks)
            if bundle.format_identifier != "FAVA_PQC_HYBRID_V1":
                raise exceptions.DecryptionError(f"Unsupported bundle format: {bundle.format_identifier}")
            if bundle.suite_id != suite_config.get("id"):
                raise exceptions.DecryptionError(
                    f"Mismatched suite ID. Bundle: {bundle.suite_id}, Config: {suite_config.get('id')}"
                )

            # 3. Get classical and PQC private keys
            classical_sk_material = key_material_decrypt.get("classical_private_key")
            pqc_sk_material = key_material_decrypt.get("pqc_private_key")

            if not classical_sk_material or not pqc_sk_material:
                raise exceptions.KeyManagementError("Missing private keys for decryption.")

            # Ensure classical_sk is an X25519PrivateKey instance
            if isinstance(classical_sk_material, bytes):
                classical_sk = x25519.X25519PrivateKey.from_private_bytes(classical_sk_material)
            elif isinstance(classical_sk_material, x25519.X25519PrivateKey):
                classical_sk = classical_sk_material
            else:
                 raise exceptions.KeyManagementError("Classical private key is not in a recognized format.")


            # 4. Classical KEM (X25519) - Decapsulation
            # The bundle.classical_kem_ciphertext contains the sender's ephemeral public key bytes
            classical_ephemeral_pk = x25519.X25519PublicKey.from_public_bytes(bundle.classical_kem_ciphertext)
            classical_shared_secret = classical_sk.exchange(classical_ephemeral_pk)

            # 5. PQC KEM (ML-KEM) - Decapsulation
            pqc_kem_algo = suite_config.get("pqc_kem_algorithm")
            if not pqc_kem_algo:
                raise exceptions.ConfigurationError("PQC KEM algorithm not specified in suite_config for decryption.")
            
            pqc_kem = KeyEncapsulation(pqc_kem_algo)
            # pqc_sk_material should be the raw secret key bytes for MLKEMBridge.decap_secret
            pqc_shared_secret = pqc_kem.decap_secret(pqc_sk_material, bundle.pqc_kem_ciphertext)

            # 6. Combine secrets
            combined_secret = classical_shared_secret + pqc_shared_secret

            # 7. KDF (HKDF) to derive symmetric key
            kdf_algo_name = suite_config.get("kdf_algorithm_for_hybrid_sk", "HKDF-SHA3-512")
            if kdf_algo_name == "HKDF-SHA3-512": hash_algo_for_kdf = hashes.SHA3_512()
            elif kdf_algo_name == "HKDF-SHA256": hash_algo_for_kdf = hashes.SHA256()
            else: raise exceptions.ConfigurationError(f"Unsupported KDF for symmetric key: {kdf_algo_name}")

            symmetric_algo_name = suite_config.get("symmetric_algorithm", "AES256GCM")
            if symmetric_algo_name == "AES256GCM": symmetric_key_length = 32
            elif symmetric_algo_name == "AES128GCM": symmetric_key_length = 16
            else: raise exceptions.ConfigurationError(f"Unsupported symmetric algo for key length: {symmetric_algo_name}")
            
            symmetric_kdf = HKDFExpand(
                algorithm=hash_algo_for_kdf, length=symmetric_key_length,
                info=b"fava_hybrid_pqc_symmetric_key_v1", backend=default_backend()
            )
            symmetric_key = symmetric_kdf.derive(combined_secret)

            # 8. Symmetric Decryption (AES-GCM)
            aesgcm = AESGCM(symmetric_key)
            # Concatenate ciphertext and tag for decryption as per cryptography library's API for AESGCM
            ciphertext_with_tag_for_decrypt = bundle.symmetric_ciphertext + bundle.symmetric_auth_tag
            
            decrypted_plaintext_bytes = aesgcm.decrypt(
                bundle.symmetric_iv,
                ciphertext_with_tag_for_decrypt, # cryptography's AESGCM decrypt expects ciphertext || tag
                associated_data=None
            )
            return decrypted_plaintext_bytes.decode('utf-8')

        except ValueError as ve: # Catches issues from int.from_bytes, .decode, AESGCM key size etc.
            raise exceptions.DecryptionError(f"Decryption failed due to value error: {str(ve)}") from ve
        except exceptions.CryptoError: # Re-raise our own specific crypto errors (base class)
            raise
        except Exception as e: # Catch other unexpected errors during decryption
            raise exceptions.DecryptionError(f"An unexpected error occurred during decryption: {str(e)}") from e


class GpgHandler:
    """
    Handles GPG encryption and decryption (placeholder).
    Handles GPG encryption and decryption using the GPG command-line tool.
    """
    GPG_BINARY_MAGIC_BYTES = [
        b'\x85\x02',  # Old GPG packet (RFC 4880 Section 4.2)
        b'\x99',      # Compressed Data Packet tag (RFC 4880 Section 5.6) - often follows header
        # Other common first bytes of OpenPGP packets (less specific than full magic)
        # b'\x84', # New packet format header byte (tag value 2)
        # b'\x88', # Symmetrically Encrypted Data Packet (tag value 3)
        # b'\x8c', # Marker Packet (tag value 10)
    ]
    GPG_ARMORED_MAGIC_STRING = b"-----BEGIN PGP MESSAGE-----"


    def __init__(self):
        """
        Initializes the GpgHandler.
        """
        pass

    def can_handle(self, file_path: str, file_content_peek: Optional[bytes] = None, config: Optional[Any] = None) -> bool:
        """
        Determines if this handler can process the given GPG file.

        Args:
            file_path: The path to the file.
            file_content_peek: Optional first few bytes of the file content.
            config: Fava application configuration (FavaOptions).

        Returns:
            True if the handler can process the file, False otherwise.
        """
        if not config or not getattr(config, 'pqc_fallback_to_classical_gpg', False):
            return False

        if file_path and file_path.lower().endswith(".gpg"):
            return True
        
        if file_content_peek:
            if file_content_peek.startswith(self.GPG_ARMORED_MAGIC_STRING):
                return True
            for magic in self.GPG_BINARY_MAGIC_BYTES:
                if file_content_peek.startswith(magic):
                    return True
        return False

    def decrypt_content(self, encrypted_content: bytes, config: Optional[Any] = None, key_material: Optional[Any] = None) -> str:
        """
        Decrypts GPG encrypted content using the gpg command-line tool.

        Args:
            encrypted_content: The GPG encrypted data as bytes.
            config: Fava application configuration (FavaOptions).
            key_material: Not used by this handler (relies on GPG agent/keyring).

        Returns:
            The decrypted plaintext as a string.

        Raises:
            DecryptionError: If GPG decryption fails.
            FileNotFoundError: If the 'gpg' command is not found.
        """
        cmd = ['gpg', '--decrypt', '--batch', '--yes', '--quiet', '--no-tty']
        
        gpg_options_str = getattr(config, 'gpg_options', None)
        if gpg_options_str and isinstance(gpg_options_str, str):
            try:
                additional_options = shlex.split(gpg_options_str)
                cmd.extend(additional_options)
            except ValueError as e:
                # Handle cases where shlex.split might fail, though unlikely for simple options
                raise exceptions.ConfigurationError(f"Invalid GPG options string: {gpg_options_str}. Error: {e}")


        try:
            process = subprocess.run(
                cmd,
                input=encrypted_content,
                capture_output=True,
                check=False  # We handle the return code manually
            )
        except FileNotFoundError:
            # This occurs if the 'gpg' command is not found in PATH
            raise FileNotFoundError("The 'gpg' command-line tool was not found. Please ensure GPG is installed and in your system's PATH.")
        except Exception as e: # Catch other potential subprocess errors
             raise exceptions.DecryptionError(f"Subprocess execution failed for GPG decryption: {str(e)}")


        if process.returncode != 0:
            stderr_output = process.stderr.decode('utf-8', errors='replace').strip() if process.stderr else "No stderr output."
            error_message = f"GPG decryption failed (exit code {process.returncode}). Error: {stderr_output}"
            raise exceptions.DecryptionError(error_message)

        try:
            decrypted_data = process.stdout.decode('utf-8')
        except UnicodeDecodeError as ude:
            raise exceptions.DecryptionError(f"Failed to decode GPG output as UTF-8: {str(ude)}")

        return decrypted_data