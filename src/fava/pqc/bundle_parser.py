"""
Bundle parser module that provides secure bundle parsing without circular dependencies.

This module handles the parsing of encrypted bundles in a way that avoids
circular imports between backend_crypto_service and core modules.
"""

import json
import logging
import re
import time
from typing import Dict, Any, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def parse_bundle_secure(raw_encrypted_bytes: Union[bytes, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Securely parses a bundle using dynamic imports to avoid circular dependencies.
    
    Args:
        raw_encrypted_bytes: Raw encrypted bytes or pre-parsed dictionary
        
    Returns:
        Dictionary with parsing results including:
        - was_successful: bool
        - suite_id: str or None
        - bundle_object: dict or None
        - error_message: str or None
    """
    try:
        # Handle pre-parsed dictionary (for testing)
        if isinstance(raw_encrypted_bytes, dict):
            return {
                "was_successful": True,
                "suite_id": raw_encrypted_bytes.get("suite_id_used", ""),
                "bundle_object": raw_encrypted_bytes,
                "error_message": None
            }
            
        if not isinstance(raw_encrypted_bytes, bytes):
            from .exceptions import BundleParsingError
            raise BundleParsingError(f"Unsupported bundle data type: {type(raw_encrypted_bytes)}")
            
        # Try secure binary format first
        try:
            # Import here to avoid circular dependency
            from ..core.encrypted_file_bundle import (
                SecureBundleParser, 
                FieldType,
                ValidationError,
                IntegrityError,
                MemoryLimitExceededError,
                ParsingTimeoutError
            )
            
            parser = SecureBundleParser()
            secure_bundle = parser.parse_bundle(raw_encrypted_bytes)
            
            # Convert to dictionary format for compatibility
            bundle_dict = {
                "format_identifier": secure_bundle.get_string_field(FieldType.FORMAT_IDENTIFIER) or "",
                "suite_id_used": secure_bundle.get_string_field(FieldType.SUITE_ID) or "",
                "classical_kem_ephemeral_public_key": secure_bundle.get_field(FieldType.CLASSICAL_KEM_CT) or b"",
                "pqc_kem_encapsulated_key": secure_bundle.get_field(FieldType.PQC_KEM_CT) or b"",
                "symmetric_cipher_iv_or_nonce": secure_bundle.get_field(FieldType.SYMMETRIC_IV) or b"",
                "encrypted_data_ciphertext": secure_bundle.get_field(FieldType.ENCRYPTED_DATA) or b"",
                "authentication_tag": secure_bundle.get_field(FieldType.AUTH_TAG) or b"",
                "kdf_salt_for_passphrase_derived_keys": secure_bundle.get_field(FieldType.KDF_SALT_PASS),
                "kdf_salt_for_hybrid_sk_derivation": secure_bundle.get_field(FieldType.KDF_SALT_HYBRID),
            }
            
            logger.info("Successfully parsed bundle using secure binary format")
            return {
                "was_successful": True,
                "suite_id": bundle_dict.get("suite_id_used", ""),
                "bundle_object": bundle_dict,
                "error_message": None
            }
            
        except ValidationError as validation_error:
            # Check if this is a format mismatch (allow fallback) vs security violation (block fallback)
            error_msg = str(validation_error)
            if ("Invalid magic number" in error_msg or 
                "Bundle too small" in error_msg or
                "Unsupported format version" in error_msg):
                # Format mismatch - allow fallback to legacy parsing
                logger.info("Binary format not detected, attempting legacy JSON parsing")
                return _parse_legacy_json_bundle(raw_encrypted_bytes)
            else:
                # Security violation - do not fall back
                logger.error(f"Bundle security violation detected: {validation_error}")
                return {
                    "was_successful": False,
                    "suite_id": None,
                    "bundle_object": None,
                    "error_message": f"Security violation: {validation_error}"
                }
            
        except (IntegrityError, MemoryLimitExceededError, ParsingTimeoutError) as security_error:
            # Definite security violations - do not fall back to legacy parsing
            logger.error(f"Bundle security violation detected: {security_error}")
            return {
                "was_successful": False,
                "suite_id": None,
                "bundle_object": None,
                "error_message": f"Security violation: {security_error}"
            }
            
        except Exception:
            # Other parsing errors - allow fallback to legacy JSON parsing
            logger.warning("Binary format parsing failed, attempting legacy JSON parsing")
            return _parse_legacy_json_bundle(raw_encrypted_bytes)
            
    except Exception as e:
        logger.error(f"Bundle parsing failed: {e}")
        return {
            "was_successful": False,
            "suite_id": None,
            "bundle_object": None,
            "error_message": str(e)
        }


def _parse_legacy_json_bundle(raw_encrypted_bytes: bytes) -> Dict[str, Any]:
    """
    Legacy JSON bundle parsing with enhanced security controls.
    Used only for backward compatibility during migration.
    
    SECURITY CONTROLS:
    - Size limit for legacy bundles (10MB max)
    - Timeout control (30 seconds)
    - Structural validation to detect DoS attempts
    - Essential field validation
    """
    from .exceptions import BundleParsingError
    
    # Size limit for legacy bundles
    if len(raw_encrypted_bytes) > 10 * 1024 * 1024:  # 10MB limit for JSON
        raise BundleParsingError("Legacy JSON bundle exceeds size limit")
        
    try:
        # Timeout control
        with timeout(30):  # 30 second timeout
            bundle_str = raw_encrypted_bytes.decode('utf-8')
            
            # Additional validation before JSON parsing
            if len(bundle_str) > 10 * 1024 * 1024:
                raise BundleParsingError("JSON string too large")
                
            # Count braces to detect potential DoS
            open_braces = bundle_str.count('{')
            close_braces = bundle_str.count('}')
            if open_braces > 1000 or abs(open_braces - close_braces) > 0:
                raise BundleParsingError("Suspicious JSON structure detected")
                
            # Parse JSON with limits
            bundle_data = json.loads(bundle_str)
            
            if not isinstance(bundle_data, dict):
                raise BundleParsingError("Parsed JSON bundle is not a dictionary")
                
            # Validate essential fields and detect malicious content
            suite_id = bundle_data.get("suite_id_used")
            if not suite_id or not isinstance(suite_id, str) or len(suite_id) > 64:
                raise BundleParsingError("Invalid suite_id_used in legacy bundle")
                
            # Security validation for suite_id - reject potentially malicious content
            if not re.match(r'^[a-zA-Z0-9_-]+$', suite_id):
                raise BundleParsingError("suite_id contains invalid characters")
                
            # Check for code injection patterns in all string fields
            dangerous_patterns = [
                r'__import__',
                r'eval\s*\(',
                r'exec\s*\(',
                r'os\.',
                r'subprocess',
                r'system\s*\(',
                r'<script',
                r'javascript:',
                r'DROP\s+TABLE',
                r'\.\./\.\.',
                r'\\x[0-9a-f]{2}',  # hex escapes
                r'\\u[0-9a-f]{4}',  # unicode escapes
            ]
            
            # Check all string values in the bundle
            for key, value in bundle_data.items():
                if isinstance(value, str):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, value, re.IGNORECASE):
                            raise BundleParsingError(f"Potentially malicious content detected in field {key}")
                            
            # Additional field validations
            format_id = bundle_data.get("format_identifier")
            if format_id and (not isinstance(format_id, str) or len(format_id) > 64):
                raise BundleParsingError("Invalid format_identifier in legacy bundle")
                
            logger.warning("Successfully parsed legacy JSON bundle - consider migrating to secure binary format")
            return {
                "was_successful": True,
                "suite_id": suite_id,
                "bundle_object": bundle_data,
                "error_message": None
            }
            
    except UnicodeDecodeError as e:
        raise BundleParsingError(f"Invalid UTF-8 encoding: {e}")
    except json.JSONDecodeError as e:
        raise BundleParsingError(f"Invalid JSON format: {e}")
    except TimeoutError:
        raise BundleParsingError("JSON parsing timeout exceeded")


@contextmanager
def timeout(seconds):
    """Context manager for operation timeout."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out")
        
    # Only use signal-based timeout on Unix-like systems
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    except (AttributeError, ValueError):
        # Windows or other systems without SIGALRM - use basic timeout
        start_time = time.time()
        try:
            yield
            if time.time() - start_time > seconds:
                raise TimeoutError("Operation timed out")
        except:
            raise