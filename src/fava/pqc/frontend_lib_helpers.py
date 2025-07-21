# src/fava/pqc/frontend_lib_helpers.py
"""
Real frontend cryptographic helpers replacing placeholder implementations.
"""

import asyncio
import time
import hashlib
import base64
import oqs
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RealHTTPClientHelper:
    """Real HTTP client implementation."""
    
    @staticmethod
    async def http_get_json(url: str) -> Dict[str, Any]:
        """Real async HTTP GET request."""
        try:
            # For now, use a basic implementation that would work in browser context
            # In a real frontend, this would use fetch() API or similar
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except ImportError:
            # Fallback for environments without aiohttp
            import urllib.request
            import json
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except Exception as e:
            logger.error(f"HTTP GET failed for {url}: {e}")
            raise


class RealSystemTimeHelper:
    """Real system time implementation."""
    
    @staticmethod
    def get_system_time_ms() -> int:
        """Get current system time in milliseconds."""
        return int(time.time() * 1000)


class RealJSCryptoSHA256Helper:
    """Real SHA256 implementation."""
    
    @staticmethod
    def hash(data_bytes: bytes) -> bytes:
        """Real SHA256 hashing."""
        if not isinstance(data_bytes, bytes):
            raise ValueError("Input must be bytes")
        return hashlib.sha256(data_bytes).digest()


class RealJSCryptoSHA3_256Helper:
    """Real SHA3-256 implementation."""
    
    @staticmethod
    def hash(data_bytes: bytes) -> bytes:
        """Real SHA3-256 hashing."""
        if not isinstance(data_bytes, bytes):
            raise ValueError("Input must be bytes")
        return hashlib.sha3_256(data_bytes).digest()


class RealLibOQSJSHelper:
    """Real liboqs implementation for frontend operations."""
    
    @staticmethod
    def dilithium3_verify(message_buffer: bytes, signature_buffer: bytes, public_key_bytes: bytes) -> bool:
        """
        Real Dilithium3 signature verification.
        
        Args:
            message_buffer: Message that was signed
            signature_buffer: Dilithium3 signature (2420 bytes)
            public_key_bytes: Dilithium3 public key (1952 bytes)
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Validate input parameters
            if not isinstance(message_buffer, bytes):
                logger.warning("Message buffer is not bytes")
                return False
            if not isinstance(signature_buffer, bytes):
                logger.warning("Signature buffer is not bytes")
                return False
            if not isinstance(public_key_bytes, bytes):
                logger.warning("Public key bytes is not bytes")
                return False
                
            # Dilithium3 public key is 1952 bytes
            if len(public_key_bytes) != 1952:
                logger.warning(f"Invalid Dilithium3 public key length: {len(public_key_bytes)} (expected 1952)")
                return False
                
            # Dilithium3 signature length is variable (around 2420-3300 bytes depending on implementation)
            if len(signature_buffer) < 2000 or len(signature_buffer) > 4000:
                logger.warning(f"Invalid Dilithium3 signature length: {len(signature_buffer)} (expected 2000-4000)")
                return False
                
            with oqs.Signature("Dilithium3") as verifier:
                # Verify signature
                is_valid = verifier.verify(message_buffer, signature_buffer, public_key_bytes)
                logger.debug(f"Dilithium3 verification result: {is_valid}")
                return is_valid
                
        except oqs.MechanismNotSupportedError as e:
            logger.error(f"Dilithium3 not supported by liboqs: {e}")
            return False
        except Exception as e:
            # Log error but return False for security
            logger.error(f"Dilithium3 verification failed: {e}")
            return False


# UTILITIES - keep real implementations (these were already real)
class FrontendUtilitiesHelper:
    @staticmethod
    def utf8_encode(data_string: str) -> bytes:
        """UTF-8 encoding."""
        return data_string.encode('utf-8')

    @staticmethod
    def bytes_to_hex_string(data_bytes: bytes) -> str:
        """Converting bytes to a hex string."""
        return data_bytes.hex()

    @staticmethod
    def base64_decode(b64_string: str) -> bytes:
        """Base64 decoding."""
        import base64
        return base64.b64decode(b64_string)


# Replace placeholders with real implementations
HTTP_CLIENT = RealHTTPClientHelper
SYSTEM_TIME = RealSystemTimeHelper
JS_CRYPTO_SHA256 = RealJSCryptoSHA256Helper
JS_CRYPTO_SHA3_256 = RealJSCryptoSHA3_256Helper
LIBOQS_JS = RealLibOQSJSHelper
FRONTEND_UTILS = FrontendUtilitiesHelper  # Keep existing real implementation