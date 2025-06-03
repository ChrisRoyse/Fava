# src/fava/pqc/backend_crypto_service.py
"""
Backend Cryptographic Service for Fava PQC features.
Manages cryptographic handlers, provides hashing services, and orchestrates decryption.
"""
import logging
from typing import Any, Dict, List, Optional, Callable, Union
import json # Added for robust JSON parsing

from .global_config import GlobalConfig
from .interfaces import (
    CryptoHandler,
    HybridEncryptedBundle,
    KeyMaterialForEncryption,
    KeyMaterialForDecryption,
    HasherInterface
)
from .exceptions import (
    InvalidArgumentError,
    AlgorithmNotFoundError,
    ConfigurationError,
    CriticalConfigurationError,
    DecryptionError,
    EncryptionFailedError,
    HashingOperationFailedError,
    AlgorithmUnavailableError,
    BundleParsingError,
    CryptoError,
)
# Import placeholder crypto library helpers for HybridPqcCryptoHandler
from .crypto_lib_helpers import (
    KEM_LIBRARY,
    KDF_LIBRARY,
    SYMMETRIC_CIPHER_LIBRARY,
    UTILITY_LIBRARY
)


logger = logging.getLogger(__name__)

# Type alias for a factory that creates CryptoHandler instances
CryptoHandlerFactory = Callable[[str, Dict[str, Any]], CryptoHandler]


class BackendCryptoService:
    """
    Central service for backend cryptographic operations, managing handlers.
    Corresponds to pseudocode: MODULE BackendCryptoService
    """
    _handler_registry: Dict[str, Union[CryptoHandler, CryptoHandlerFactory]] = {}

    @classmethod
    def register_crypto_handler(
        cls, suite_id: str, handler_or_factory: Union[CryptoHandler, CryptoHandlerFactory]
    ) -> None:
        """
        Registers a CryptoHandler instance or factory for a given suite_id.
        Corresponds to pseudocode: FUNCTION RegisterCryptoHandler
        """
        if not suite_id or handler_or_factory is None:
            msg = "suite_id and handler_or_factory must be provided for registration."
            logger.error(f"Attempted to register crypto handler with invalid arguments: {msg}")
            raise InvalidArgumentError(msg)

        if suite_id in cls._handler_registry:
            logger.warning(f"Overwriting existing crypto handler for suite_id: {suite_id}")
        cls._handler_registry[suite_id] = handler_or_factory
        logger.info(f"Crypto handler registered for suite: {suite_id}")

    @classmethod
    def get_crypto_handler(cls, suite_id: str) -> CryptoHandler:
        """
        Retrieves a CryptoHandler instance for the given suite_id.
        If a factory was registered, it's used to create an instance.
        Corresponds to pseudocode: FUNCTION GetCryptoHandler
        """
        if suite_id not in cls._handler_registry:
            logger.error(f"No crypto handler registered for suite_id: {suite_id}")
            raise AlgorithmNotFoundError(f"Handler for suite '{suite_id}' not registered.")

        handler_entry = cls._handler_registry[suite_id]
        handler_entry = cls._handler_registry[suite_id]
        if callable(handler_entry) and not isinstance(handler_entry, CryptoHandler): # It's a factory
            try:
                app_config = GlobalConfig.get_crypto_settings()
                # Ensure structure for suites exists
                if not (app_config
                        and "data_at_rest" in app_config
                        and "suites" in app_config["data_at_rest"]
                        and suite_id in app_config["data_at_rest"]["suites"]):
                    raise ConfigurationError(f"Missing suite configuration for {suite_id} needed by factory.")

                suite_config = app_config["data_at_rest"]["suites"][suite_id]
                # Factory creates instance, then cache it
                instance = handler_entry(suite_id, suite_config)
                cls._handler_registry[suite_id] = instance # Cache the instance
                logger.debug(f"Instantiated and cached handler for suite: {suite_id}")
                return instance
            except Exception as e:
                logger.error(f"Factory for suite '{suite_id}' failed to create handler: {e}")
                raise AlgorithmUnavailableError(f"Factory for suite '{suite_id}' failed: {e}") from e
        elif isinstance(handler_entry, CryptoHandler):
            return handler_entry # It's already an instance (was cached or registered as instance)
        else: # Should not happen if registration is type-checked
            msg = f"Invalid entry in handler registry for suite '{suite_id}'."
            raise CriticalConfigurationError(msg)


    @classmethod
    def get_active_encryption_handler(cls) -> CryptoHandler:
        """
        Gets the active CryptoHandler for encryption based on global configuration.
        Corresponds to pseudocode: FUNCTION GetActiveEncryptionHandler
        """
        app_config = GlobalConfig.get_crypto_settings()
        active_suite_id = app_config.get("data_at_rest", {}).get("active_encryption_suite_id")

        if not active_suite_id:
            msg = "Active encryption suite ID ('active_encryption_suite_id') is not configured."
            logger.critical(msg)
            raise ConfigurationError(msg)
        try:
            return cls.get_crypto_handler(active_suite_id)
        except (AlgorithmNotFoundError, AlgorithmUnavailableError) as e:
            msg = (f"Configured active encryption handler '{active_suite_id}' "
                   f"is not registered or its library is unavailable: {e}")
            logger.critical(msg)
            raise CriticalConfigurationError(msg) from e

    @classmethod
    def get_configured_decryption_handlers(cls) -> List[CryptoHandler]:
        """
        Gets an ordered list of CryptoHandlers for decryption attempts.
        Corresponds to pseudocode: FUNCTION GetConfiguredDecryptionHandlers
        """
        app_config = GlobalConfig.get_crypto_settings()
        decryption_order_list = app_config.get("data_at_rest", {}).get("decryption_attempt_order", [])
        
        handlers_list: List[CryptoHandler] = []
        if not decryption_order_list:
            logger.warning("No 'decryption_attempt_order' configured.")
            return handlers_list

        for suite_id in decryption_order_list:
            try:
                handler = cls.get_crypto_handler(suite_id)
                handlers_list.append(handler)
            except (AlgorithmNotFoundError, AlgorithmUnavailableError):
                logger.warning(
                    f"Crypto handler for suite_id '{suite_id}' (listed in "
                    f"'decryption_attempt_order') not found/registered or unavailable. "
                    f"It will be skipped for decryption attempts."
                )
        return handlers_list
    
    @classmethod
    def reset_registry_for_testing(cls) -> None:
        """Helper to clear the registry, primarily for isolated testing."""
        cls._handler_registry.clear()


class HybridPqcCryptoHandler(CryptoHandler):
    """
    Example implementation of a CryptoHandler for Hybrid PQC schemes.
    Corresponds to pseudocode: CLASS HybridPqcCryptoHandler
    This is a simplified version focusing on the agility aspect and interaction points.
    Actual crypto operations are delegated to placeholder helpers.
    """
    def __init__(self, suite_id: str, suite_specific_config: Dict[str, Any]):
        self.my_suite_id = suite_id
        self.my_suite_config = suite_specific_config

        required_keys = [
            "classical_kem_algorithm", "pqc_kem_algorithm",
            "symmetric_algorithm", "kdf_algorithm_for_hybrid_sk" # As per pseudo
        ]
        if not all(key in suite_specific_config for key in required_keys):
            raise ConfigurationError(
                f"HybridPqcCryptoHandler for suite '{suite_id}' requires "
                f"{', '.join(required_keys)} in suite configuration."
            )
        logger.debug(f"HybridPqcCryptoHandler for suite '{self.my_suite_id}' initialized.")

    def get_suite_id(self) -> str:
        return self.my_suite_id

    def encrypt(
        self,
        plaintext: bytes,
        key_material: KeyMaterialForEncryption,
        suite_specific_config: Optional[Dict[str, Any]] = None # Allow override for testing
    ) -> HybridEncryptedBundle:
        current_config = suite_specific_config if suite_specific_config is not None else self.my_suite_config
        logger.info(f"Encrypting with Hybrid PQC suite: {self.my_suite_id}")

        if not key_material or not key_material.get("classical_recipient_pk") or not key_material.get("pqc_recipient_pk"):
            raise InvalidArgumentError("Missing recipient public keys in key_material for encryption.")

        classical_kem_alg = current_config["classical_kem_algorithm"]
        pqc_kem_alg = current_config["pqc_kem_algorithm"]
        symmetric_alg = current_config["symmetric_algorithm"]
        kdf_hybrid_alg = current_config["kdf_algorithm_for_hybrid_sk"]
        
        try:
            # 1. Classical KEM
            classical_res = KEM_LIBRARY.hybrid_kem_classical_encapsulate(
                classical_kem_alg, key_material["classical_recipient_pk"]
            )
            # 2. PQC KEM
            pqc_res = KEM_LIBRARY.pqc_kem_encapsulate(
                pqc_kem_alg, key_material["pqc_recipient_pk"]
            )
            # 3. Combine & KDF
            combined_secrets = classical_res["shared_secret"] + pqc_res["shared_secret"]
            # Pseudocode suggests optional salt for hybrid SK derivation, not explicitly in spec 8.1 bundle.
            # Assuming if needed, it's generated and stored in bundle.kdf_salt_for_hybrid_sk_derivation
            kdf_salt_hybrid_sk = UTILITY_LIBRARY.generate_random_bytes(16) # Example, length from config if needed
            
            sym_key_len = UTILITY_LIBRARY.get_symmetric_key_length(symmetric_alg)
            derived_sym_key = KDF_LIBRARY.derive(
                combined_secrets, kdf_salt_hybrid_sk, kdf_hybrid_alg, sym_key_len, "FavaHybridSymmetricKey"
            )
            # 4. Symmetric Encryption
            iv_len = UTILITY_LIBRARY.get_iv_length(symmetric_alg)
            iv_nonce = UTILITY_LIBRARY.generate_random_bytes(iv_len)
            sym_cipher_res = SYMMETRIC_CIPHER_LIBRARY.encrypt_aead(
                symmetric_alg, derived_sym_key, iv_nonce, plaintext, None
            )
            
            bundle: HybridEncryptedBundle = {
                "format_identifier": current_config.get("format_identifier", "FAVA_PQC_HYBRID_V1"),
                "suite_id_used": self.my_suite_id,
                "classical_kem_ephemeral_public_key": classical_res["ephemeral_public_key"],
                "pqc_kem_encapsulated_key": pqc_res["encapsulated_key"],
                "symmetric_cipher_iv_or_nonce": iv_nonce,
                "encrypted_data_ciphertext": sym_cipher_res["ciphertext"],
                "authentication_tag": sym_cipher_res["authentication_tag"],
                "kdf_salt_for_passphrase_derived_keys": key_material.get("kdf_salt_for_passphrase_derived_keys"),
                "kdf_salt_for_hybrid_sk_derivation": kdf_salt_hybrid_sk,
            }
            return bundle
        except Exception as e: # Catch underlying crypto lib errors
            logger.error(f"Hybrid encryption failed for suite {self.my_suite_id}: {e}")
            raise EncryptionFailedError(f"Underlying crypto op failed during hybrid encryption: {e}") from e


    def decrypt(
        self,
        bundle: HybridEncryptedBundle,
        key_material: KeyMaterialForDecryption,
        suite_specific_config: Optional[Dict[str, Any]] = None # Allow override
    ) -> bytes:
        current_config = suite_specific_config if suite_specific_config is not None else self.my_suite_config
        logger.info(f"Decrypting with Hybrid PQC suite: {self.my_suite_id} (bundle from {bundle['suite_id_used']})")

        if not key_material or not key_material.get("classical_recipient_sk") or not key_material.get("pqc_recipient_sk"):
            raise InvalidArgumentError("Missing recipient private keys in key_material for decryption.")
        
        if bundle["suite_id_used"] != self.my_suite_id and suite_specific_config is None:
             logger.warning(f"Bundle suite_id '{bundle['suite_id_used']}' mismatches handler '{self.my_suite_id}'.")
             # Potentially load config for bundle['suite_id_used'] if this handler is multi-suite aware
             # For now, assume current_config is for self.my_suite_id or explicitly passed for bundle's suite.

        classical_kem_alg = current_config["classical_kem_algorithm"]
        pqc_kem_alg = current_config["pqc_kem_algorithm"]
        symmetric_alg = current_config["symmetric_algorithm"]
        kdf_hybrid_alg = current_config["kdf_algorithm_for_hybrid_sk"]

        try:
            # 1. Classical KEM Decapsulation
            classical_secret = KEM_LIBRARY.hybrid_kem_classical_decapsulate(
                classical_kem_alg, bundle["classical_kem_ephemeral_public_key"], key_material["classical_recipient_sk"]
            )
            # 2. PQC KEM Decapsulation
            pqc_secret = KEM_LIBRARY.pqc_kem_decapsulate(
                pqc_kem_alg, bundle["pqc_kem_encapsulated_key"], key_material["pqc_recipient_sk"]
            )
            # 3. Combine & KDF
            combined_secrets = classical_secret + pqc_secret
            kdf_salt_hybrid_sk = bundle["kdf_salt_for_hybrid_sk_derivation"]
            
            sym_key_len = UTILITY_LIBRARY.get_symmetric_key_length(symmetric_alg)
            derived_sym_key = KDF_LIBRARY.derive(
                combined_secrets, kdf_salt_hybrid_sk, kdf_hybrid_alg, sym_key_len, "FavaHybridSymmetricKey"
            )
            # 4. Symmetric Decryption
            plaintext = SYMMETRIC_CIPHER_LIBRARY.decrypt_aead(
                symmetric_alg, derived_sym_key, bundle["symmetric_cipher_iv_or_nonce"],
                bundle["encrypted_data_ciphertext"], bundle["authentication_tag"], None
            )
            if plaintext is None: # AEAD verification failed
                raise DecryptionError("Symmetric decryption failed: authentication tag mismatch or corrupted data.")
            return plaintext
        except CryptoError as e: # Catch specific crypto errors from helpers
            logger.warning(f"Hybrid decryption op failed for suite {self.my_suite_id}: {e}")
            raise DecryptionError(f"Underlying crypto op failed during hybrid decryption: {e}") from e
        except Exception as e: # Catch other unexpected errors
            logger.error(f"Unexpected error during hybrid decryption for suite {self.my_suite_id}: {e}")
            raise DecryptionError(f"Unexpected error during hybrid decryption: {e}") from e


class HashingProvider:
    """
    Provides configured hashing capabilities.
    Corresponds to pseudocode: MODULE HashingProvider
    """
    @staticmethod
    def get_configured_hasher() -> HasherInterface:
        """Gets a HasherInterface instance based on global configuration."""
        app_config = GlobalConfig.get_crypto_settings()
        configured_algo_name = app_config.get("hashing", {}).get("default_algorithm")

        if not configured_algo_name:
            logger.warning("No default hashing algorithm configured. Defaulting to SHA3-256.")
            configured_algo_name = "SHA3-256" # Default fallback

        try:
            return HashingProvider._get_hasher_instance(configured_algo_name)
        except AlgorithmUnavailableError as e:
            logger.warning(
                f"Configured hash algorithm '{configured_algo_name}' is unavailable: {e}. "
                f"Attempting fallback to SHA3-256."
            )
            try:
                return HashingProvider._get_hasher_instance("SHA3-256")
            except AlgorithmUnavailableError as fe:
                logger.critical(f"Fallback hash algorithm SHA3-256 is also unavailable: {fe}")
                raise HashingOperationFailedError("No hashing service available.") from fe

    @staticmethod
    def _get_hasher_instance(algorithm_name: str) -> HasherInterface:
        """Internal factory for hasher instances."""
        # This would map algorithm_name to actual hasher implementations.
        # For now, placeholder.
        if algorithm_name == "SHA3-256":
            # return SHA3_256HasherImpl() # Placeholder
            raise AlgorithmUnavailableError(f"Hasher for {algorithm_name} not implemented yet.")
        elif algorithm_name == "SHA256":
            # return SHA256HasherImpl() # Placeholder
            raise AlgorithmUnavailableError(f"Hasher for {algorithm_name} not implemented yet.")
        else:
            raise AlgorithmUnavailableError(f"Unsupported hash algorithm: {algorithm_name}")


def parse_common_encrypted_bundle_header(raw_encrypted_bytes: Union[bytes, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses a common bundle header to extract suite_id and the bundle object.
    Assumes the raw_encrypted_bytes might be a UTF-8 encoded JSON string
    representing the HybridEncryptedBundle, or a pre-parsed dictionary (for testing).
    VULN-PQC-AGL-002: This function needs robust parsing.
    """
    try:
        if isinstance(raw_encrypted_bytes, dict):
            # If it's already a dictionary, assume it's a pre-parsed bundle (e.g., from tests)
            bundle_data = raw_encrypted_bytes
        elif isinstance(raw_encrypted_bytes, bytes):
            try:
                # Attempt to decode as UTF-8 and parse as JSON
                bundle_str = raw_encrypted_bytes.decode('utf-8')
                bundle_data = json.loads(bundle_str)
                if not isinstance(bundle_data, dict):
                    raise BundleParsingError("Parsed JSON bundle is not a dictionary.")
            except UnicodeDecodeError as ude:
                logger.error(f"Bundle header decode error: {ude}")
                raise BundleParsingError(f"Bundle header is not valid UTF-8: {ude}") from ude
            except json.JSONDecodeError as jde:
                logger.error(f"Bundle header JSON parsing error: {jde}")
                raise BundleParsingError(f"Bundle header is not valid JSON: {jde}") from jde
        else:
            raise BundleParsingError(f"Unsupported type for bundle header: {type(raw_encrypted_bytes)}")

        # Validate essential fields
        suite_id = bundle_data.get("suite_id_used")
        format_id = bundle_data.get("format_identifier") # Example: FAVA_PQC_HYBRID_V1

        if not suite_id or not isinstance(suite_id, str):
            raise BundleParsingError("Missing or invalid 'suite_id_used' in bundle header.")
        if not format_id or not isinstance(format_id, str): # Basic check for format identifier
            logger.warning("Missing or invalid 'format_identifier' in bundle header.")
            # Depending on strictness, this could also be an error.
            # For now, we prioritize suite_id for handler selection.

        return {
            "was_successful": True,
            "suite_id": suite_id,
            "bundle_object": bundle_data # Return the full parsed dictionary
        }
    except BundleParsingError as bpe: # Catch our specific parsing errors
        logger.error(f"Bundle parsing error: {bpe}")
        return {"was_successful": False, "suite_id": None, "bundle_object": None, "error": str(bpe)}
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error during bundle header parsing: {e}")
        return {"was_successful": False, "suite_id": None, "bundle_object": None, "error": str(e)}


def decrypt_data_at_rest_with_agility(
    raw_encrypted_bytes: bytes, key_material_input: Any
) -> bytes:
    """
    Orchestrates decryption of data at rest using configured handlers.
    Corresponds to pseudocode: FUNCTION DecryptDataAtRestWithAgility
    """
    parsed_bundle_attempt = parse_common_encrypted_bundle_header(raw_encrypted_bytes)
    
    app_config = GlobalConfig.get_crypto_settings()
    
    # Attempt with handler from bundle header if successfully parsed
    if parsed_bundle_attempt["was_successful"] and parsed_bundle_attempt["suite_id"]:
        suite_id_from_header = parsed_bundle_attempt["suite_id"]
        bundle_object_from_header = parsed_bundle_attempt["bundle_object"]
        try:
            handler = BackendCryptoService.get_crypto_handler(suite_id_from_header)
            suite_specific_config = app_config.get("data_at_rest", {}).get("suites", {}).get(suite_id_from_header)
            if not suite_specific_config:
                raise ConfigurationError(f"Missing suite config for {suite_id_from_header}")

            logger.info(f"Attempting decryption with handler '{suite_id_from_header}' identified from bundle header.")
            return handler.decrypt(bundle_object_from_header, key_material_input, suite_specific_config)
        except (DecryptionError, ConfigurationError, AlgorithmNotFoundError, AlgorithmUnavailableError) as e:
            logger.info(f"Targeted decryption with handler '{suite_id_from_header}' failed: {e}")
        except Exception as ex: # Catch any other unexpected error from this attempt
            logger.error(f"Unexpected error with targeted handler '{suite_id_from_header}': {ex}")

    # Iterate through configured decryption handlers if targeted attempt failed or wasn't possible
    decryption_handlers = BackendCryptoService.get_configured_decryption_handlers()
    if not decryption_handlers:
        logger.error("No decryption handlers configured or available after targeted attempt.")
        raise DecryptionError("Unable to decrypt data: No decryption handlers available.")

    for handler in decryption_handlers:
        suite_id = handler.get_suite_id()
        logger.info(f"Attempting decryption with handler from configured order: {suite_id}")
        try:
            # Each handler might need to re-parse or expect a specific bundle format.
            # For HybridPqcCryptoHandler, it expects HybridEncryptedBundle.
            # If raw_encrypted_bytes was not parseable by common header parser,
            # we might need a handler-specific parser here, or assume bundle_object_from_header
            # is the only format for now if the common parser worked.
            # This part is tricky without a concrete bundle format for raw_bytes.
            # For now, assume if parse_common_encrypted_bundle_header worked, we use its bundle_object.
            # If not, this loop cannot proceed with raw_bytes unless handlers parse raw bytes themselves.
            # This is a simplification for now.
            if not parsed_bundle_attempt["was_successful"] or not parsed_bundle_attempt["bundle_object"]:
                 logger.warning(f"Cannot attempt decryption with handler {suite_id} as initial bundle parsing failed.")
                 continue # Or raise, or handler must parse raw_encrypted_bytes

            current_bundle_to_try = parsed_bundle_attempt["bundle_object"]
            
            suite_specific_config = app_config.get("data_at_rest", {}).get("suites", {}).get(suite_id)
            if not suite_specific_config:
                 logger.warning(f"Missing suite config for handler {suite_id} in decryption_attempt_order. Skipping.")
                 continue

            return handler.decrypt(current_bundle_to_try, key_material_input, suite_specific_config)
        except (DecryptionError, BundleParsingError, ConfigurationError) as e:
            logger.info(f"Decryption with handler '{suite_id}' failed: {e}. Trying next.")
        except Exception as ex:
            logger.error(f"Unexpected error with handler '{suite_id}' during decryption attempt: {ex}. Trying next.")
            
    logger.error("All configured decryption attempts failed for the provided data.")
    raise DecryptionError("Unable to decrypt data: No configured cryptographic suite succeeded.")