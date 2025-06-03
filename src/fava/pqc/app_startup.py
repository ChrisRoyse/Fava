# src/fava/pqc/app_startup.py
"""
Handles the initialization of PQC cryptographic services during Fava application startup.
"""
import logging
from typing import Dict, Any, Optional

from .global_config import GlobalConfig
from .backend_crypto_service import BackendCryptoService, HybridPqcCryptoHandler
from .gpg_handler import GpgCryptoHandler # Assuming GpgHandler is in this module
from .exceptions import ApplicationStartupError, CriticalConfigurationError, ConfigurationError

logger = logging.getLogger(__name__)

def initialize_backend_crypto_service(crypto_settings_file: Optional[str] = None) -> None:
    """
    Initializes the BackendCryptoService by loading configuration and registering handlers.
    Corresponds to pseudocode: PROCEDURE InitializeBackendCryptoService

    Args:
        crypto_settings_file: Optional path to the PQC crypto settings file.
                              If None, GlobalConfig will use its default.
    """
    logger.info("Initializing PQC Backend Crypto Service...")
    try:
        # Ensure GlobalConfig cache is fresh for startup, or load if not already.
        # load_crypto_settings will raise if critical issues are found.
        GlobalConfig.reset_cache() # Ensure fresh load on startup
        app_config = GlobalConfig.get_crypto_settings(file_path=crypto_settings_file)
    except CriticalConfigurationError as e:
        logger.critical(f"Failed to load critical PQC crypto settings during startup (path: {crypto_settings_file}): {e}")
        raise ApplicationStartupError(f"PQC crypto settings load failure: {e}") from e

    # Register handlers based on configuration
    # This part assumes specific handler classes for given suite types.
    # In a more dynamic system, this might involve plugin discovery or more generic factory registration.
    
    suites_config = app_config.get("data_at_rest", {}).get("suites", {})
    if not isinstance(suites_config, dict):
        logger.warning("PQC 'data_at_rest.suites' configuration is missing or not a dictionary. No handlers will be registered.")
        suites_config = {}

    for suite_id, suite_conf in suites_config.items():
        if not isinstance(suite_conf, dict):
            logger.warning(f"Configuration for suite '{suite_id}' is not a dictionary. Skipping registration.")
            continue
        
        suite_type = suite_conf.get("type")
        try:
            if suite_type == "FAVA_HYBRID_PQC":
                # For FAVA_HYBRID_PQC, we directly instantiate HybridPqcCryptoHandler
                # In a real system, we might register a factory:
                # BackendCryptoService.register_crypto_handler(suite_id, HybridPqcCryptoHandler)
                # And GetCryptoHandler would call it: HybridPqcCryptoHandler(suite_id, suite_conf)
                # For simplicity matching test plan, let's assume direct registration of instance for now,
                # or a factory that takes suite_id and suite_conf.
                # The test plan implies a factory is called by GetCryptoHandler.
                # So, we register the class itself as a factory.
                BackendCryptoService.register_crypto_handler(suite_id, HybridPqcCryptoHandler)
                logger.info(f"Registered HybridPqcCryptoHandler factory for suite: {suite_id}")
            elif suite_type == "CLASSICAL_GPG":
                # Ensure GpgCryptoHandler is a factory or can be registered directly
                # If GpgCryptoHandler's __init__ matches the factory signature (suite_id, suite_config),
                # it can be registered directly. Otherwise, a lambda or wrapper factory is needed.
                # For now, assuming it can be registered as a factory like HybridPqcCryptoHandler.
                BackendCryptoService.register_crypto_handler(suite_id, GpgCryptoHandler)
                logger.info(f"Registered GpgCryptoHandler factory for suite: {suite_id}")
            else:
                logger.warning(f"Unknown crypto suite type '{suite_type}' for suite_id '{suite_id}'. Cannot register handler.")
        except Exception as e: # Catch any error during handler registration setup
            logger.error(f"Failed to prepare or register handler for suite '{suite_id}': {e}")
            # Depending on policy, this could be a critical failure if the suite is essential.

    # Verify active encryption handler can be loaded
    try:
        # This call will use the factories registered above if the active suite_id matches.
        active_handler = BackendCryptoService.get_active_encryption_handler()
        logger.info(f"Active encryption handler '{active_handler.get_suite_id()}' successfully loaded.")
    except (ConfigurationError, CriticalConfigurationError) as e: # Catch errors from get_active_encryption_handler
        logger.critical(f"Failed to load active PQC encryption handler post-registration: {e}")
        raise ApplicationStartupError(f"Critical failure: Active PQC encryption handler unavailable: {e}") from e
    
    logger.info("PQC Backend Crypto Service initialized successfully.")