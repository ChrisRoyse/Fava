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
# FAVA_CRYPTO_SETTINGS_PATH would typically be derived from Fava's main config system
# For now, a placeholder.
FAVA_CRYPTO_SETTINGS_PATH: str = "config/fava_crypto_settings.py" # Placeholder

# FAVA_CRYPTO_SETTINGS_ExpectedSchema would be a more complex structure.
# For now, a placeholder.
FAVA_CRYPTO_SETTINGS_ExpectedSchema: Dict[str, Any] = {"version": 1} # Placeholder

logger = logging.getLogger(__name__)

class GlobalConfig:
    """
    Manages loading, validation, and caching of FAVA_CRYPTO_SETTINGS.
    """
    _global_crypto_settings_cache: Optional[Dict[str, Any]] = None

    @staticmethod
    def load_crypto_settings() -> Dict[str, Any]:
        """
        Loads, parses, and validates the FAVA_CRYPTO_SETTINGS.
        Corresponds to pseudocode: FUNCTION LoadCryptoSettings()
        FR2.3: Fava's configuration (`FavaOptions`) MUST allow administrators
               to specify desired cryptographic algorithms.
        """
        try:
            raw_config_content = file_system.read_file_content(FAVA_CRYPTO_SETTINGS_PATH)
            # In a real scenario, parsing might involve ast.literal_eval if it's Python-like
            # or a dedicated config parser if it's another format (e.g. YAML, TOML).
            parsed_config = parser.parse_python_like_structure(raw_config_content)

            # Schema validation (FR2.3, Spec 8.1)
            # The actual schema would be complex, based on PQC_Cryptographic_Agility_Spec.md#81
            if not validator.validate_schema(parsed_config, FAVA_CRYPTO_SETTINGS_ExpectedSchema):
                # Assuming validator.validate_schema raises its own error or returns detailed errors
                # For simplicity, we'll treat a False return as a schema validation failure.
                logger.error("Crypto settings schema validation failed.")
                raise ConfigurationError("Crypto settings schema validation failed.")

            logger.info("Successfully loaded and validated crypto settings.")
            return parsed_config
        except FileNotFoundError as e:
            logger.error(f"Crypto settings file not found at {FAVA_CRYPTO_SETTINGS_PATH}: {e}")
            raise CriticalConfigurationError("Crypto settings file is missing.") from e
        except PQCInternalParsingError as e: # Using the aliased exception
            logger.error(f"Failed to parse crypto settings: {e}")
            raise CriticalConfigurationError("Crypto settings file is malformed.") from e
        except ConfigurationError as e: # Includes schema validation errors from our logic
            logger.error(f"Invalid crypto settings: {e}")
            # Re-raise as Critical if schema validation is considered critical
            raise CriticalConfigurationError(f"Crypto settings are invalid: {e}") from e
        except Exception as e: # Catch any other unexpected errors during loading
            logger.error(f"An unexpected error occurred while loading crypto settings: {e}")
            raise CriticalConfigurationError(f"Unexpected error loading crypto settings: {e}") from e


    @staticmethod
    def get_crypto_settings() -> Dict[str, Any]:
        """
        Retrieves the cached crypto settings, loading them if not already cached.
        Corresponds to pseudocode: FUNCTION GetCryptoSettings()
        """
        if GlobalConfig._global_crypto_settings_cache is None:
            GlobalConfig._global_crypto_settings_cache = GlobalConfig.load_crypto_settings()
        return GlobalConfig._global_crypto_settings_cache

    @staticmethod
    def reset_cache() -> None:
        """Utility method for testing to reset the cache."""
        GlobalConfig._global_crypto_settings_cache = None