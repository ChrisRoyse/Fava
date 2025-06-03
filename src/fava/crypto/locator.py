"""
Crypto Service Locator for managing cryptographic handlers.

This module provides the CryptoServiceLocator class that manages
and selects appropriate cryptographic handlers based on file types
and content characteristics.
"""

from typing import List, Optional, Union
from .handlers import HybridPqcHandler, GpgHandler
from .exceptions import CryptoError


class CryptoServiceLocator:
    """
    Service locator for cryptographic handlers.
    
    Manages registration and selection of appropriate crypto handlers
    based on file extensions, magic bytes, and other criteria.
    """
    
    def __init__(self):
        """Initialize the crypto service locator with default handlers."""
        self._handlers = []
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register the default cryptographic handlers."""
        # Register handlers in priority order
        self._handlers.append(HybridPqcHandler())
        self._handlers.append(GpgHandler())
    
    def register_handler(self, handler):
        """
        Register a new cryptographic handler.
        
        Args:
            handler: Handler instance with can_handle, encrypt_content, 
                    decrypt_content methods and name attribute
        """
        if not hasattr(handler, 'can_handle'):
            raise CryptoError("Handler must implement can_handle method")
        if not hasattr(handler, 'name'):
            raise CryptoError("Handler must have name attribute")
        
        self._handlers.append(handler)
    
    def get_handler(self, file_path: str = None, content: bytes = None) -> Optional[object]:
        """
        Get the appropriate handler for the given file or content.
        
        Args:
            file_path: Path to the file (optional)
            content: File content bytes (optional)
            
        Returns:
            Handler instance that can handle the file/content, or None
        """
        for handler in self._handlers:
            if handler.can_handle(file_path=file_path, content=content):
                return handler
        return None
    
    def get_pqc_encrypt_handler(self) -> Optional[object]:
        """
        Get the PQC encryption handler specifically.
        
        Returns:
            HybridPqcHandler instance if available, None otherwise
        """
        for handler in self._handlers:
            if hasattr(handler, 'name') and 'Pqc' in handler.name:
                return handler
        return None
    
    def get_handlers_by_priority(self) -> List[object]:
        """
        Get all handlers in priority order.
        
        Returns:
            List of handler instances in registration order
        """
        return self._handlers.copy()