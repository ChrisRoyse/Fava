# src/fava/pqc/global_config.py
"""
Global Configuration Management for PQC features in Fava.
"""
import logging
from typing import Any, Dict, Optional

# Assuming these helpers are in a sibling file or adjust import path
from .global_config_helpers import file_system, parser, validator
from .exceptions import (
    CriticalConfigurationError,
    ConfigurationError,
    ParsingError as PQCInternalParsingError # Alias to avoid clash with built-in
)

# As per pseudocode: MODULE GlobalConfig
DEFAULT_FAVA_CRYPTO_SETTINGS_PATH: str = "config/fava_crypto_settings.py"

# FAVA_CRYPTO_SETTINGS_ExpectedSchema would be a more complex structure.
# For now, a placeholder.
FAVA_CRYPTO_SETTINGS_ExpectedSchema: Dict[str, Any] = {"version": 1} # Placeholder

logger = logging.getLogger(__name__)

class GlobalConfig:
    """
    Manages loading, validation, and caching of FAVA_CRYPTO_SETTINGS.
    """
    _global_crypto_settings_cache: Optional[Dict[str, Any]] = None
    _current_settings_path: Optional[str] = None

    @staticmethod
    def load_crypto_settings(file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads, parses, and validates the FAVA_CRYPTO_SETTINGS from the given file_path
        or a default path if file_path is None.
        Corresponds to pseudocode: FUNCTION LoadCryptoSettings()
        FR2.3: Fava's configuration (`FavaOptions`) MUST allow administrators
               to specify desired cryptographic algorithms.
        """
        actual_path = file_path or DEFAULT_FAVA_CRYPTO_SETTINGS_PATH
        logger.info(f"Attempting to load crypto settings from: {actual_path}")

        try:
            raw_config_content = file_system.read_file_content(actual_path)
            # In a real scenario, parsing might involve ast.literal_eval if it's Python-like
            # or a dedicated config parser if it's another format (e.g. YAML, TOML).
            parsed_config = parser.parse_python_like_structure(raw_config_content)

            # Schema validation (FR2.3, Spec 8.1)
            # The actual schema would be complex, based on PQC_Cryptographic_Agility_Spec.md#81
            if not validator.validate_schema(parsed_config, FAVA_CRYPTO_SETTINGS_ExpectedSchema):
                # Assuming validator.validate_schema raises its own error or returns detailed errors
                # For simplicity, we'll treat a False return as a schema validation failure.
                logger.error(f"Crypto settings schema validation failed for {actual_path}.")
                raise ConfigurationError(f"Crypto settings schema validation failed for {actual_path}.")

            logger.info(f"Successfully loaded and validated crypto settings from {actual_path}.")
            return parsed_config
        except FileNotFoundError as e:
            logger.error(f"Crypto settings file not found at {actual_path}: {e}")
            raise CriticalConfigurationError(f"Crypto settings file '{actual_path}' is missing.") from e
        except PQCInternalParsingError as e: # Using the aliased exception
            logger.error(f"Failed to parse crypto settings from {actual_path}: {e}")
            raise CriticalConfigurationError(f"Crypto settings file '{actual_path}' is malformed.") from e
        except ConfigurationError as e: # Includes schema validation errors from our logic
            logger.error(f"Invalid crypto settings in {actual_path}: {e}")
            # Re-raise as Critical if schema validation is considered critical
            raise CriticalConfigurationError(f"Crypto settings in '{actual_path}' are invalid: {e}") from e
        except Exception as e: # Catch any other unexpected errors during loading
            logger.error(f"An unexpected error occurred while loading crypto settings from {actual_path}: {e}")
            raise CriticalConfigurationError(f"Unexpected error loading crypto settings from '{actual_path}': {e}") from e


    @staticmethod
    def get_crypto_settings(file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves the cached crypto settings. If the cache is empty or the requested
        file_path differs from the cached one, it reloads the settings.
        Uses a default path if file_path is None.
        Corresponds to pseudocode: FUNCTION GetCryptoSettings()
        """
        actual_path_to_load = file_path or DEFAULT_FAVA_CRYPTO_SETTINGS_PATH

        if (
            GlobalConfig._global_crypto_settings_cache is None or
            GlobalConfig._current_settings_path != actual_path_to_load
        ):
            logger.info(
                f"Cache miss or path change for crypto settings. Old path: {GlobalConfig._current_settings_path}, New path: {actual_path_to_load}. Reloading."
            )
            GlobalConfig._global_crypto_settings_cache = GlobalConfig.load_crypto_settings(actual_path_to_load)
            GlobalConfig._current_settings_path = actual_path_to_load
        else:
            logger.debug(f"Using cached crypto settings from: {GlobalConfig._current_settings_path}")
        
        # Ensure cache is not None after attempt to load, defensive return
        if GlobalConfig._global_crypto_settings_cache is None:
             # This case should ideally be prevented by load_crypto_settings raising an error
            raise CriticalConfigurationError("Crypto settings cache is None after attempting to load.")
        return GlobalConfig._global_crypto_settings_cache

    @staticmethod
    def reset_cache() -> None:
        """Utility method for testing to reset the cache."""
        logger.debug("Resetting GlobalConfig crypto settings cache.")
        GlobalConfig._global_crypto_settings_cache = None
        GlobalConfig._current_settings_path = None