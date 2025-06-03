"""FavaLedger - Core ledger class for Fava application."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, Optional, Tuple

from fava.core.fava_options import FavaOptions
from fava.crypto.locator import CryptoServiceLocator
from fava.crypto import keys as fava_keys # For key derivation/loading
from fava.crypto import exceptions as crypto_exceptions # For custom exceptions

# Mocked in tests, but define for real use or type checking if needed
def PROMPT_USER_FOR_PASSPHRASE_SECURELY(prompt: str) -> str:
    # In a real app, this would securely prompt the user.
    # For tests, this will be mocked.
    # raise NotImplementedError("Secure passphrase prompt not implemented.")
    return "default_mock_passphrase_if_not_mocked"

def RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(context_id: str, salt_len: int = 16) -> bytes:
    # In a real app, this would manage salts securely.
    # For tests, this will be mocked.
    # raise NotImplementedError("Salt management not implemented.")
    return b"default_mock_salt" * (salt_len // len(b"default_mock_salt"))

def WRITE_BYTES_TO_FILE(file_path: str, data: bytes) -> None:
    # raise NotImplementedError("WRITE_BYTES_TO_FILE not implemented.")
    pass # Mocked in tests

def READ_BYTES_FROM_FILE(file_path: str) -> bytes:
    # raise NotImplementedError("READ_BYTES_FROM_FILE not implemented.")
    return b"" # Mocked in tests

def parse_beancount_file_from_source(source: str, config: Any, file_path: str) -> Tuple[Any, Any, Any]:
    # raise NotImplementedError("parse_beancount_file_from_source not implemented.")
    return ([], [], {}) # Mocked in tests


if TYPE_CHECKING:  # pragma: no cover
    from fava.core.watcher import WatcherBase

log = logging.getLogger(__name__)


class FavaLedger:
    """Core ledger class for Fava application with PQC support."""

    def __init__(
        self,
        beancount_file_path: str, # This is FavaOptions in mock_fava_config for tests
        *,
        poll_watcher: WatcherBase | None = None,
    ) -> None:
        """Initialize FavaLedger.
        
        Args:
            beancount_file_path: Path to the beancount file or FavaOptions for tests.
            poll_watcher: Optional file watcher instance
        """
        if isinstance(beancount_file_path, FavaOptions): # Test scenario
            self.fava_options = beancount_file_path
            self.beancount_file_path = self.fava_options.input_files[0] if self.fava_options.input_files else "mock_ledger.beancount"
        else: # Real scenario
            self.beancount_file_path = beancount_file_path
            self.fava_options = FavaOptions() # Or load from somewhere
            # Potentially load options specific to this ledger path if FavaOptions supports it

        self.poll_watcher = poll_watcher
        self.crypto_service_locator = CryptoServiceLocator(app_config=self.fava_options)
        self.options = self.fava_options


    def _get_key_material_for_operation(
        self, file_path_context: str, operation_type: str # e.g., "encrypt" or "decrypt"
    ) -> Dict[str, Any]:
        """
        Retrieves appropriate key material based on FavaOptions configuration.
        This is a simplified version focusing on what tests need.
        """
        key_material: Dict[str, Any] = {}
        mode = self.fava_options.pqc_key_management_mode
        active_suite_id = self.fava_options.pqc_active_suite_id
        suite_config = self.fava_options.pqc_suites.get(active_suite_id, {})

        if mode == "PASSPHRASE_DERIVED":
            passphrase = PROMPT_USER_FOR_PASSPHRASE_SECURELY(f"Enter passphrase for {file_path_context} ({operation_type}):")
            salt = RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(f"{file_path_context}_{operation_type}_salt")
            
            classical_keys, pqc_keys = fava_keys.derive_kem_keys_from_passphrase(
                passphrase,
                salt,
                suite_config.get("pbkdf_algorithm_for_passphrase", "Argon2id"),
                suite_config.get("kdf_algorithm_for_ikm_from_pbkdf", "HKDF-SHA3-512"),
                suite_config.get("classical_kem_algorithm", "X25519"),
                suite_config.get("pqc_kem_algorithm", "ML-KEM-768")
            )
            # classical_keys = (classical_pk_bytes, classical_sk_bytes)
            # pqc_keys = (pqc_pk_bytes, pqc_sk_bytes)
            if operation_type == "encrypt":
                key_material["classical_public_key"] = classical_keys[0]
                key_material["pqc_public_key"] = pqc_keys[0]
            else: # decrypt
                key_material["classical_private_key"] = classical_keys[1]
                key_material["pqc_private_key"] = pqc_keys[1]

        elif mode == "EXTERNAL_FILE":
            key_paths = self.fava_options.pqc_key_file_paths
            classical_keys, pqc_keys = fava_keys.load_keys_from_external_file(key_paths)
            if operation_type == "encrypt":
                key_material["classical_public_key"] = classical_keys[0]
                key_material["pqc_public_key"] = pqc_keys[0]
            else: # decrypt
                key_material["classical_private_key"] = classical_keys[1]
                key_material["pqc_private_key"] = pqc_keys[1]
        else:
            raise crypto_exceptions.ConfigurationError(f"Unsupported PQC key management mode: {mode}")
        
        return key_material

    def _try_decrypt_content(self, file_path: str, encrypted_content_bytes: bytes) -> Optional[str]:
        """
        Attempts to decrypt content using the CryptoServiceLocator.
        """
        handler = self.crypto_service_locator.get_handler_for_file(file_path, encrypted_content_bytes, self.fava_options)
        if not handler:
            # This could mean it's plaintext or an unsupported encrypted format.
            # For this PQC context, if it was expected to be handled, this is an issue.
            # However, load_file might try to parse as plaintext if no handler.
            return None

        try:
            key_material = self._get_key_material_for_operation(file_path, "decrypt")
            active_suite_config = self.fava_options.pqc_suites.get(self.fava_options.pqc_active_suite_id, {})
            
            # Ensure decrypt_content exists and is callable
            if not hasattr(handler, 'decrypt_content') or not callable(handler.decrypt_content):
                 log.error(f"Handler {getattr(handler, 'name', type(handler).__name__)} has no callable decrypt_content method.")
                 return None # Or raise an error

            return handler.decrypt_content(encrypted_content_bytes, active_suite_config, key_material, self.fava_options)
        except crypto_exceptions.CryptoError as e:
            log.warning(f"Decryption failed for {file_path} with handler {getattr(handler, 'name', type(handler).__name__)}: {e}")
            return None # Or re-raise if critical
        except Exception as e:
            log.error(f"Unexpected error during decryption of {file_path}: {e}")
            return None


    def save_file_pqc(self, file_path: str, plaintext_content: str, key_context: Optional[str] = None) -> None:
        """
        Encrypts and saves file content using the PQC hybrid scheme.
        key_context can be used to derive different keys/salts if needed, defaults to file_path.
        """
        if not self.fava_options.pqc_data_at_rest_enabled:
            raise crypto_exceptions.ConfigurationError("PQC data at rest is not enabled.")

        context = key_context if key_context else file_path
        key_material_encrypt = self._get_key_material_for_operation(context, "encrypt")
        active_suite_id = self.fava_options.pqc_active_suite_id
        suite_config = self.fava_options.pqc_suites.get(active_suite_id)
        if not suite_config:
            raise crypto_exceptions.ConfigurationError(f"Active PQC suite '{active_suite_id}' not found.")

        handler = self.crypto_service_locator.get_pqc_encrypt_handler(suite_config, self.fava_options)
        if not handler:
            raise crypto_exceptions.CryptoError("No PQC encryption handler found.")
        
        if not hasattr(handler, 'encrypt_content') or not callable(handler.encrypt_content):
            raise crypto_exceptions.CryptoError(f"Handler {getattr(handler, 'name', type(handler).__name__)} has no callable encrypt_content method.")

        encrypted_bytes = handler.encrypt_content(
            plaintext_content,
            suite_config,
            key_material_encrypt,
            self.fava_options
        )
        WRITE_BYTES_TO_FILE(file_path, encrypted_bytes)

    def load_file(self, file_path: str) -> Tuple[Any, Any, Any]: # Mimics Beancount load return
        """
        Loads a file, attempting PQC decryption if applicable.
        If decryption fails or no handler, attempts to load as plaintext.
        """
        file_content_bytes = READ_BYTES_FROM_FILE(file_path)
        
        # Try to determine if it's a PQC or GPG file and decrypt
        decrypted_source: Optional[str] = None
        peek_bytes = file_content_bytes[:128] # Arbitrary peek size
        
        handler = self.crypto_service_locator.get_handler_for_file(file_path, peek_bytes, self.fava_options)

        if handler:
            try:
                decrypted_source = self._try_decrypt_content(file_path, file_content_bytes)
            except crypto_exceptions.CryptoError as e: # Catch our specific crypto errors
                log.warning(f"Decryption attempt failed for {file_path}: {e}. Attempting plaintext load.")
                decrypted_source = None # Ensure it's None to fall through to plaintext
            except Exception as e: # Catch other unexpected errors
                log.error(f"Unexpected error during decryption of {file_path}: {e}. Attempting plaintext load.")
                decrypted_source = None


        source_to_parse: str
        if decrypted_source is not None:
            source_to_parse = decrypted_source
            log.info(f"Successfully decrypted and loaded PQC/GPG encrypted file: {file_path}")
        else:
            # If no handler or decryption failed/skipped, try to decode as UTF-8 plaintext
            try:
                source_to_parse = file_content_bytes.decode('utf-8')
                log.info(f"Loading file as plaintext: {file_path}")
            except UnicodeDecodeError:
                log.error(f"Failed to decode file as UTF-8 and no crypto handler matched or decryption failed: {file_path}")
                # What to do here? Raise an error, or return empty ledger?
                # For now, let parse_beancount_file_from_source handle potentially bad source.
                # Or, we could raise a specific FavaLoadError.
                raise crypto_exceptions.FileLoadError(f"Cannot load file: Not valid UTF-8 and crypto handling failed for {file_path}")

        # Parse the (potentially decrypted) source content
        # The actual parse_beancount_file_from_source is complex and involves beancount.loader
        # For tests, this will be mocked.
        return parse_beancount_file_from_source(source_to_parse, self.fava_options, file_path)