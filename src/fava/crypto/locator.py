"""
Cryptographic Service Locator for Fava.
"""
from typing import List, Optional, Any, Type, Dict
from fava.crypto.handlers import HybridPqcHandler, GpgHandler
from fava.crypto import exceptions

# Define a base handler type for type hinting if needed, or use Any
BaseCryptoHandler = Any # Could be a Protocol if handlers have a common interface

class CryptoServiceLocator:
    """
    Locates and provides appropriate cryptographic handlers.
    """
    def __init__(self, handlers: Optional[List[BaseCryptoHandler]] = None, app_config: Optional[Any] = None):
        """
        Initializes the CryptoServiceLocator.

        Args:
            handlers: A list of handler instances to be used. 
                      If None, default handlers (HybridPqcHandler, GpgHandler) are instantiated.
            app_config: The Fava application configuration (FavaOptions).
        """
        if handlers is None:
            self._handlers = [HybridPqcHandler(), GpgHandler()]
        else:
            self._handlers = handlers
        
        # Store app_config if needed by locator logic directly,
        # or expect it to be passed to methods like get_handler_for_file.
        self._app_config = app_config


    def get_handler_for_file(self, file_path: str, file_content_peek: Optional[bytes] = None, config: Optional[Any] = None) -> Optional[BaseCryptoHandler]:
        """
        Selects an appropriate handler for the given file.

        Handlers are checked in the order they are registered.
        The first handler that `can_handle` the file is returned.

        Args:
            file_path: The path to the file.
            file_content_peek: Optional first few bytes of the file content.
            config: Fava application configuration (FavaOptions).

        Returns:
            A crypto handler instance if a suitable one is found, otherwise None.
        """
        effective_config = config if config is not None else self._app_config
        if not effective_config:
            # This case should ideally be handled by the caller ensuring config is available.
            # Or, raise a ConfigurationError if config is essential for all handler selections.
            # For now, let handlers decide if they can operate without config.
            pass

        for handler in self._handlers:
            try:
                if hasattr(handler, 'can_handle') and callable(handler.can_handle):
                    if handler.can_handle(file_path, file_content_peek, effective_config):
                        return handler
            except Exception as e:
                # Optionally log this error, as a handler failing `can_handle` might be unexpected.
                # For now, just skip to the next handler.
                # print(f"Error checking handler {getattr(handler, 'name', type(handler).__name__)}: {e}")
                pass
        return None

    def get_pqc_encrypt_handler(self, suite_config: Dict[str, Any], config: Optional[Any] = None) -> Optional[BaseCryptoHandler]:
        """
        Gets a handler suitable for PQC encryption based on the suite configuration.
        Currently, this will always be the HybridPqcHandler if PQC is enabled.

        Args:
            suite_config: The PQC suite configuration.
            config: Fava application configuration (FavaOptions).

        Returns:
            A HybridPqcHandler instance if PQC is enabled, otherwise None.
        """
        effective_config = config if config is not None else self._app_config
        if not effective_config or not getattr(effective_config, 'pqc_data_at_rest_enabled', False):
            return None

        # For PQC encryption, we specifically want the HybridPqcHandler.
        # We could also check suite_config details if multiple PQC handlers existed.
        for handler in self._handlers:
            # Check by name attribute, as tests might pass mock instances
            if hasattr(handler, 'name') and handler.name == "HybridPqcHandler":
                return handler
            # Fallback to isinstance if name attribute is not present (for non-mocked scenarios)
            elif isinstance(handler, HybridPqcHandler):
                # Potentially, could also check if this handler supports the specific
                # algorithms in suite_config, but HybridPqcHandler is designed to be flexible.
                return handler
        
        # This case should ideally not be reached if HybridPqcHandler is always in self._handlers
        # and pqc_data_at_rest_enabled is True.
        # Consider raising an error or logging if no HybridPqcHandler is found when expected.
        # raise exceptions.ConfigurationError("HybridPqcHandler not found in locator, but PQC encryption requested.")
        return None