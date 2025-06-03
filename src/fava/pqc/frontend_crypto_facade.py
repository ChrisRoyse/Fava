# src/fava/pqc/frontend_crypto_facade.py
"""
Frontend Cryptographic Abstraction Layer for Fava PQC features.
Python representation for conceptual frontend logic.
"""
import logging
from typing import Any, Dict, Optional, Tuple

from .exceptions import (
    ConfigurationError,
    HashingOperationFailedError,
    AlgorithmUnavailableError, # Changed from AlgorithmNotSupportedError for consistency
    CryptoError, # For liboqs-js like errors
)
from .frontend_lib_helpers import (
    HTTP_CLIENT,
    SYSTEM_TIME,
    JS_CRYPTO_SHA256,
    JS_CRYPTO_SHA3_256,
    LIBOQS_JS,
    FRONTEND_UTILS,
)

logger = logging.getLogger(__name__)

# Corresponds to pseudocode: MODULE FrontendCryptoFacade
class FrontendCryptoFacade:
    """
    Provides cryptographic abstractions for the frontend, fetching configuration
    from the backend API.
    """
    _fava_config_cache: Optional[Dict[str, Any]] = None
    _config_cache_timestamp: int = 0
    CONFIG_CACHE_TTL_MS: int = 60000  # 1 minute

    @classmethod
    async def _get_fava_runtime_crypto_options(cls) -> Dict[str, Any]:
        """
        Fetches relevant crypto settings from Fava backend API, with caching.
        Corresponds to pseudocode: ASYNC FUNCTION _getFavaRuntimeCryptoOptions()
        """
        current_time = SYSTEM_TIME.get_system_time_ms()
        if (cls._fava_config_cache is None or
                (current_time - cls._config_cache_timestamp > cls.CONFIG_CACHE_TTL_MS)):
            try:
                # IP12.4: API exposes relevant parts of FAVA_CRYPTO_SETTINGS
                api_response = await HTTP_CLIENT.http_get_json("/api/fava-crypto-configuration")
                # Assuming API returns a dict with a "crypto_settings" key
                # containing sections like "hashing", "wasm_integrity"
                if "crypto_settings" not in api_response:
                    raise ConfigurationError("API response missing 'crypto_settings' key.")
                
                cls._fava_config_cache = api_response["crypto_settings"]
                cls._config_cache_timestamp = current_time
                logger.info("Frontend fetched and cached Fava crypto configuration.")
            except Exception as e: # Catch network errors, parsing errors from http_get_json
                logger.error(f"Frontend failed to fetch Fava crypto configuration from API: {e}")
                if cls._fava_config_cache is not None:
                    logger.warning("Returning stale frontend crypto config due to API error.")
                    return cls._fava_config_cache
                else:
                    raise ConfigurationError("Unable to fetch crypto configuration for frontend operations.") from e
        return cls._fava_config_cache

    @classmethod
    async def calculate_configured_hash(cls, data_string: str) -> str: # HexString
        """
        Calculates hash using the backend-configured default algorithm.
        Corresponds to pseudocode: ASYNC FUNCTION CalculateConfiguredHash
        """
        try:
            crypto_config = await cls._get_fava_runtime_crypto_options()
            hashing_settings = crypto_config.get("hashing", {})
            configured_algo = hashing_settings.get("default_algorithm")

            if not configured_algo:
                logger.warning("No default hashing algorithm in frontend config. Defaulting to SHA3-256.")
                configured_algo = "SHA3-256"

            data_bytes = FRONTEND_UTILS.utf8_encode(data_string)
            hashed_bytes = cls._internal_calculate_hash(data_bytes, configured_algo)
            return FRONTEND_UTILS.bytes_to_hex_string(hashed_bytes)
        except Exception as e: # Covers config fetch errors, internal hash errors
            logger.error(f"CalculateConfiguredHash failed with primary algorithm: {e}. Attempting fallback.")
            # FR2.7: Fallback for less critical ops
            try:
                data_bytes = FRONTEND_UTILS.utf8_encode(data_string)
                hashed_bytes = cls._internal_calculate_hash(data_bytes, "SHA3-256") # Default fallback
                logger.warning("Used fallback SHA3-256 for hashing.")
                return FRONTEND_UTILS.bytes_to_hex_string(hashed_bytes)
            except Exception as fe: # Catch errors from fallback attempt
                logger.critical(f"Frontend hashing failed completely, even with fallback SHA3-256: {fe}")
                raise HashingOperationFailedError("All hashing attempts failed.") from fe

    @classmethod
    def _internal_calculate_hash(cls, data_bytes: bytes, algorithm_name: str) -> bytes:
        """
        Internal helper to dispatch to specific hash implementations.
        Corresponds to pseudocode: FUNCTION _internalCalculateHash
        """
        if algorithm_name == "SHA256":
            return JS_CRYPTO_SHA256.hash(data_bytes)
        elif algorithm_name == "SHA3-256":
            return JS_CRYPTO_SHA3_256.hash(data_bytes)
        else:
            raise AlgorithmUnavailableError(f"Unsupported frontend hash algorithm: {algorithm_name}")

    @classmethod
    async def verify_wasm_signature_with_config(
        cls, wasm_module_buffer: bytes, signature_buffer: bytes # Changed to bytes for consistency
    ) -> bool:
        """
        Verifies WASM module signature based on backend-configured settings.
        Corresponds to pseudocode: ASYNC FUNCTION VerifyWasmSignatureWithConfig
        """
        try:
            crypto_config = await cls._get_fava_runtime_crypto_options()
            wasm_integrity_settings = crypto_config.get("wasm_integrity", {})

            if not wasm_integrity_settings.get("verification_enabled", False):
                logger.info("WASM signature verification is disabled in configuration.")
                return True # Verification not required or disabled

            public_key_b64 = wasm_integrity_settings.get("public_key_dilithium3_base64")
            signature_algo_name = wasm_integrity_settings.get("signature_algorithm")

            if not public_key_b64 or not signature_algo_name:
                logger.error("WASM integrity verification enabled, but public key or algorithm name is missing.")
                return False # Fail securely: cannot verify

            return cls._internal_verify_signature(
                wasm_module_buffer, signature_buffer, public_key_b64, signature_algo_name
            )
        except Exception as e: # Covers config fetch errors, internal verify errors
            logger.error(f"VerifyWasmSignatureWithConfig encountered an error: {e}. Failing securely.")
            return False # Fail securely

    @classmethod
    def _internal_verify_signature(
        cls, message_buffer: bytes, signature_buffer: bytes,
        public_key_b64: str, algorithm_name: str
    ) -> bool:
        """
        Internal helper for signature verification.
        Corresponds to pseudocode: FUNCTION _internalVerifySignature
        """
        public_key_bytes = FRONTEND_UTILS.base64_decode(public_key_b64)
        if algorithm_name == "Dilithium3": # C7.1: Bounded by liboqs-js capabilities
            try:
                logger.debug("Performing conceptual Dilithium3 verification using LIBOQS_JS.")
                return LIBOQS_JS.dilithium3_verify(message_buffer, signature_buffer, public_key_bytes)
            except Exception as oqse: # Catch errors from the mock/actual lib
                logger.error(f"LIBOQS_JS verification failed for Dilithium3: {oqse}")
                # Re-raise as a specific type if the mock lib defines one, or use a generic CryptoError
                raise CryptoError(f"Dilithium3 verification failed: {oqse}") from oqse
        else:
            raise AlgorithmUnavailableError(f"Unsupported frontend signature algorithm for WASM: {algorithm_name}")

    @classmethod
    def reset_cache_for_testing(cls) -> None:
        """Utility method for testing to reset the cache."""
        cls._fava_config_cache = None
        cls._config_cache_timestamp = 0