"""
Provides a centralized hashing service for Fava, supporting PQC-compliant
algorithms like SHA3-256 and standard algorithms like SHA256.
"""
import hashlib
import logging
from typing import Optional, List

# Assuming fava.config will provide a way to get FavaConfigurationProvider
# For now, we'll define a placeholder or expect it to be passed.
# from fava.config import FavaConfigurationProvider # Placeholder

from fava.crypto.exceptions import (
    HashingAlgorithmUnavailableError,
    InternalHashingError,
)

# Global constants from pseudocode
DEFAULT_ALGORITHM_BACKEND = "SHA3-256"
SUPPORTED_ALGORITHMS_BACKEND: List[str] = ["SHA3-256", "SHA256"]

logger = logging.getLogger(__name__)

# Placeholder for a real configuration provider interface
class FavaConfigurationProvider:
    """Placeholder for Fava's configuration provider."""
    def get_string_option(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Gets a string option from the configuration."""
        # In a real scenario, this would access Fava's actual config.
        # For this module, it's used by get_hashing_service.
        # To make get_hashing_service testable without full Fava,
        # this might be mocked or a simple dict-based provider used in tests.
        if key == "pqc_hashing_algorithm":
            return getattr(self, "_mock_pqc_hashing_algorithm", default)
        return default

class HashingService:
    """
    A service to provide hashing capabilities using configured algorithms.
    """
    _algorithm_name_internal: str
    _native_sha3_available: bool = False # Initialize to False
    _pysha3_checked_and_functional: Optional[bool] = None # None: unchecked, True: functional, False: not functional

    def __init__(self, configured_algorithm_name: Optional[str] = None) -> None:
        """
        Initializes the HashingService.

        Args:
            configured_algorithm_name: The algorithm name from Fava's config.
                                       Defaults to SHA3-256 if None or empty.
        """
        if not configured_algorithm_name:
            self._algorithm_name_internal = DEFAULT_ALGORITHM_BACKEND
            logger.info(
                "HashingService: No algorithm configured, defaulting to %s",
                DEFAULT_ALGORITHM_BACKEND,
            )
        else:
            normalized_algo = configured_algorithm_name.upper()
            if normalized_algo == "SHA-256": # Normalize from potential WebCrypto name
                normalized_algo = "SHA256"

            if normalized_algo in SUPPORTED_ALGORITHMS_BACKEND:
                self._algorithm_name_internal = normalized_algo
            else:
                logger.warning(
                    "HashingService: Unsupported hash algorithm '%s'. Defaulting to '%s'.",
                    configured_algorithm_name,
                    DEFAULT_ALGORITHM_BACKEND,
                )
                self._algorithm_name_internal = DEFAULT_ALGORITHM_BACKEND
        
        # Determine native SHA3 availability once during initialization
        try:
            hashlib.sha3_256(b"initial_test") # Test call
            self._native_sha3_available = True
        except AttributeError:
            self._native_sha3_available = False
            logger.info(
                "HashingService: Native hashlib.sha3_256 is not available. "
                "Will check for pysha3 if SHA3-256 is the configured algorithm."
            )
            # If native SHA3 is not available AND SHA3-256 is the chosen algorithm,
            # check pysha3 status immediately.
            if self._algorithm_name_internal == "SHA3-256":
                self._initialize_pysha3_status()

    def _initialize_pysha3_status(self) -> None:
        """
        Checks pysha3 availability and functionality once and stores the result.
        This is called from __init__ if native SHA3 is unavailable and SHA3-256 is chosen.
        """
        if self._pysha3_checked_and_functional is None: # Ensure it's checked only once
            try:
                # pylint: disable=import-outside-toplevel
                import pysha3 # pyright: ignore[reportMissingImports]
                pysha3.sha3_256(b"pysha3_init_test").hexdigest() # Test call
                self._pysha3_checked_and_functional = True
                logger.info("HashingService: pysha3 fallback is available and functional.")
            except (ImportError, AttributeError, Exception) as e_pysha3: # pylint: disable=broad-except
                self._pysha3_checked_and_functional = False
                logger.warning(
                    "HashingService: pysha3 fallback is NOT available or functional: %s", e_pysha3
                )

    def hash_data(self, data: bytes) -> str:
        """
        Hashes the provided data using the configured algorithm.

        Args:
            data: The bytes to hash.

        Returns:
            A hexadecimal string representation of the hash digest.

        Raises:
            HashingAlgorithmUnavailableError: If the configured algorithm
                                              cannot be used.
            InternalHashingError: For other unexpected errors.
        """
        try:
            if self._algorithm_name_internal == "SHA3-256":
                if self._native_sha3_available:
                    return hashlib.sha3_256(data).hexdigest()
                
                # Native SHA3 not available. Check pysha3 status.
                # If _pysha3_checked_and_functional is still None here, it means SHA3-256
                # wasn't the initial algorithm, but is now being requested.
                # This scenario is less common if config is stable, but we should check.
                if self._pysha3_checked_and_functional is None:
                    self._initialize_pysha3_status()

                if self._pysha3_checked_and_functional: # True means checked and functional
                    try:
                        # pylint: disable=import-outside-toplevel
                        import pysha3 # pyright: ignore[reportMissingImports]
                        return pysha3.sha3_256(data).hexdigest()
                    except Exception as e_fallback: # pylint: disable=broad-except
                        logger.error(
                            "HashingService: pysha3 fallback execution for SHA3-256 failed: %s", e_fallback
                        )
                        raise HashingAlgorithmUnavailableError(
                            "SHA3-256 fallback library (pysha3) failed during use."
                        ) from e_fallback
                else: # _pysha3_checked_and_functional is False
                    logger.error(
                        "HashingService: SHA3-256 is configured, native hashlib.sha3_256 is unavailable, "
                        "and pysha3 fallback is not functional or not found."
                    )
                    raise HashingAlgorithmUnavailableError(
                        "SHA3-256 implementation not available (native or fallback)."
                    )
            elif self._algorithm_name_internal == "SHA256":
                try:
                    return hashlib.sha256(data).hexdigest()
                except AttributeError: # Should not happen for sha256 with hashlib
                    # This is a critical failure if hashlib.sha256 is missing.
                    logger.critical(
                        "HashingService: hashlib.sha256 (standard library) not available. "
                        "This indicates a severely broken Python environment."
                    )
                    raise HashingAlgorithmUnavailableError(
                        "SHA256 implementation (hashlib.sha256) not available."
                    ) # Removed "from None" as it's not standard for raising new exceptions
            else:
                # This case should ideally be prevented by the constructor's validation.
                logger.error(
                    "HashingService: Internal error - hash_data called with "
                    "unsupported algorithm: %s", self._algorithm_name_internal
                )
                raise InternalHashingError(
                    "Unsupported hash algorithm encountered post-initialization."
                )
        except HashingAlgorithmUnavailableError: # Specific exception, re-raise
            raise
        except Exception as e: # Catch any other unexpected exceptions during hashing
            logger.exception( # Use logger.exception to include stack trace
                "HashingService: Unexpected error during hashing for algorithm %s.",
                 self._algorithm_name_internal
            )
            raise InternalHashingError(
                f"Unexpected error during hashing: {e}"
            ) from e

    def get_configured_algorithm_name(self) -> str:
        """Returns the name of the algorithm the service is configured to use."""
        return self._algorithm_name_internal


def get_hashing_service(
    fava_config_provider: FavaConfigurationProvider,
) -> HashingService:
    """
    Factory function to get an instance of the HashingService.

    Args:
        fava_config_provider: An instance that can provide Fava's configuration.

    Returns:
        An initialized HashingService instance.
    """
    configured_algo_name = fava_config_provider.get_string_option(
        "pqc_hashing_algorithm", DEFAULT_ALGORITHM_BACKEND
    )
    return HashingService(configured_algo_name)