"""
Timing Attack Protection Module

This module provides constant-time cryptographic operations to prevent timing side-channel attacks.
Addresses VULN-001 and VULN-002 from Security Audit Agent #2.

Security Requirements:
- All crypto operations must have consistent timing (±2% variance max)
- Error handling must have uniform response times
- Memory access patterns must be normalized
- Side-channel resistance validated through measurement
"""

import secrets
import hmac
import time
import random
import os
import warnings
from typing import Union, List, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class SecureComparison:
    """Constant-time comparison utilities for cryptographic operations."""
    
    @staticmethod
    def compare_digest(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
        """
        Secure digest comparison using secrets.compare_digest.
        
        This is the primary function for comparing cryptographic hashes,
        signatures, and other sensitive byte sequences.
        
        Args:
            a: First value to compare
            b: Second value to compare
            
        Returns:
            True if values are equal, False otherwise
        """
        return secrets.compare_digest(a, b)
    
    @staticmethod
    def compare_strings(a: str, b: str) -> bool:
        """Secure string comparison for API keys, tokens, etc."""
        if not isinstance(a, str) or not isinstance(b, str):
            return False
        return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))
    
    @staticmethod
    def verify_hmac(message: bytes, key: bytes, expected_mac: bytes) -> bool:
        """Secure HMAC verification with constant-time comparison."""
        try:
            computed_mac = hmac.new(key, message, digestmod='sha256').digest()
            return secrets.compare_digest(computed_mac, expected_mac)
        except Exception:
            return False
    
    @staticmethod
    def constant_time_bytes_compare(a: bytes, b: bytes) -> bool:
        """
        Custom constant-time comparison for when secrets.compare_digest
        is not available or additional control is needed.
        """
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        return result == 0
    
    @staticmethod
    def compare_with_padding(a: bytes, b: bytes, target_length: int) -> bool:
        """
        Constant-time comparison with length padding to prevent
        length-based timing attacks.
        """
        # Pad both inputs to target length
        a_padded = a.ljust(target_length, b'\x00')
        b_padded = b.ljust(target_length, b'\x00')
        
        # Perform constant-time comparison
        result = 0
        for x, y in zip(a_padded, b_padded):
            result |= x ^ y
        
        # Also check original lengths in constant time
        length_match = len(a) ^ len(b)
        
        return (result == 0) and (length_match == 0)


class TimingJitter:
    """Adds timing randomization to eliminate statistical timing patterns."""
    
    @staticmethod
    def add_random_delay(base_operation_time: float = 0.001, 
                        jitter_percentage: float = 0.1) -> None:
        """
        Add random timing jitter to normalize operation duration.
        
        Args:
            base_operation_time: Base time for the operation in seconds
            jitter_percentage: Percentage of base time to add as random jitter
        """
        jitter = random.uniform(0, base_operation_time * jitter_percentage)
        time.sleep(jitter)
    
    @staticmethod
    def normalize_operation_time(target_time: float, 
                               actual_start_time: float) -> None:
        """
        Ensure operation takes exactly target_time by adding delay if needed.
        
        Args:
            target_time: Target total operation time in seconds
            actual_start_time: Time when operation started (from time.perf_counter())
        """
        elapsed = time.perf_counter() - actual_start_time
        if elapsed < target_time:
            time.sleep(target_time - elapsed)
    
    @staticmethod
    def with_constant_timing(target_time: float):
        """
        Decorator to ensure a function always takes a constant amount of time.
        
        Args:
            target_time: Target execution time in seconds
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    TimingJitter.normalize_operation_time(target_time, start_time)
            return wrapper
        return decorator


class SecureErrorHandling:
    """Provides uniform error handling to prevent timing oracle attacks."""
    
    @staticmethod
    def uniform_error_response(error_type: str = "generic", 
                             base_delay: float = 0.01) -> bool:
        """
        Generate uniform error response with consistent timing.
        
        Args:
            error_type: Type of error (for logging purposes)
            base_delay: Base delay time for error response
            
        Returns:
            Always returns False for error conditions
        """
        # Add small random jitter to prevent micro-timing analysis
        jitter = random.uniform(0.8, 1.2) * base_delay
        time.sleep(jitter)
        
        logger.debug(f"Uniform error response for {error_type}")
        return False
    
    @staticmethod
    def secure_exception_handler(func: Callable) -> Callable:
        """
        Decorator that ensures all exceptions are handled with uniform timing.
        """
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Ensure error handling takes consistent time
                elapsed = time.perf_counter() - start_time
                if elapsed < 0.01:  # Minimum 10ms for error handling
                    time.sleep(0.01 - elapsed)
                
                logger.debug(f"Exception handled with uniform timing: {type(e).__name__}")
                return False
        return wrapper


class MemorySecureOperations:
    """Operations that maintain consistent memory access patterns."""
    
    @staticmethod
    def constant_time_select(condition: bool, true_value: bytes, 
                           false_value: bytes) -> bytes:
        """
        Select between two values without revealing the condition
        through memory access patterns.
        """
        # Convert condition to mask (0x00 or 0xFF)
        mask = (0 - int(condition)) & 0xFF
        
        max_len = max(len(true_value), len(false_value))
        result = bytearray(max_len)
        
        for i in range(max_len):
            true_byte = true_value[i] if i < len(true_value) else 0
            false_byte = false_value[i] if i < len(false_value) else 0
            
            # Constant-time selection
            result[i] = (mask & true_byte) | ((~mask) & false_byte)
        
        return bytes(result)
    
    @staticmethod
    def constant_time_memcmp(a: bytes, b: bytes, length: int) -> int:
        """
        Memory comparison with consistent access patterns.
        Always accesses exactly 'length' bytes.
        """
        result = 0
        for i in range(length):
            a_byte = a[i] if i < len(a) else 0
            b_byte = b[i] if i < len(b) else 0
            result |= a_byte ^ b_byte
        
        return result


class SecureSignatureVerification:
    """Constant-time signature verification protocols."""
    
    @staticmethod
    @TimingJitter.with_constant_timing(0.005)  # 5ms constant time
    def verify_signature_secure(signature: bytes, expected: bytes) -> bool:
        """
        Secure signature verification with constant-time comparison.
        
        Args:
            signature: Provided signature
            expected: Expected signature value
            
        Returns:
            True if signatures match, False otherwise
        """
        start_time = time.perf_counter()
        
        if not signature or not expected:
            # Use error timing normalization
            from .error_timing_normalization import UniformCryptoErrorHandler
            return UniformCryptoErrorHandler.handle_verification_error("invalid_signature_input", start_time)
        
        try:
            result = SecureComparison.compare_digest(signature, expected)
            return result
        except Exception:
            from .error_timing_normalization import UniformCryptoErrorHandler
            return UniformCryptoErrorHandler.handle_verification_error("signature_comparison_error", start_time)
    
    @staticmethod
    @SecureErrorHandling.secure_exception_handler
    def verify_hash_signature_secure(data: bytes, signature: bytes, 
                                   expected_hash: bytes) -> bool:
        """Verify a hash-based signature with constant-time comparison."""
        import hashlib
        
        # Compute hash of provided data
        computed_hash = hashlib.sha256(data).digest()
        
        # Constant-time comparison of hashes
        return SecureComparison.compare_digest(computed_hash, expected_hash)


class SecureKeyVerification:
    """Constant-time key material verification."""
    
    @staticmethod
    @TimingJitter.with_constant_timing(0.002)  # 2ms constant time
    def verify_api_key_secure(provided_key: str, stored_key_hash: str) -> bool:
        """
        Verify API key against stored hash with constant-time comparison.
        """
        if not provided_key or not stored_key_hash:
            return SecureErrorHandling.uniform_error_response("missing_key")
        
        try:
            import hashlib
            # Hash the provided key
            provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
            
            # Constant-time comparison
            return SecureComparison.compare_strings(provided_hash, stored_key_hash)
            
        except Exception:
            return SecureErrorHandling.uniform_error_response("hash_error")
    
    @staticmethod
    def verify_symmetric_key_secure(key1: bytes, key2: bytes) -> bool:
        """Verify symmetric key equality with constant-time comparison."""
        return SecureComparison.compare_digest(key1, key2)
    
    @staticmethod
    @SecureErrorHandling.secure_exception_handler
    def verify_password_hash_secure(password: str, stored_hash: str) -> bool:
        """
        Verify password using secure hash verification.
        
        Note: This should use proper password hashing functions like
        bcrypt, scrypt, or Argon2 which have built-in constant-time comparison.
        """
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except ImportError:
            # Fallback if bcrypt not available
            import hashlib
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            return SecureComparison.compare_strings(computed_hash, stored_hash)


class TimingProtectionConfig:
    """Configuration for timing attack protection."""
    
    def __init__(self):
        self.enable_constant_time = True
        self.enable_timing_jitter = True
        self.enable_memory_protection = True
        self.base_operation_time = 0.001  # 1ms base time
        self.jitter_percentage = 0.1  # 10% jitter
        self.error_response_time = 0.01  # 10ms uniform error time
        
    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        config.enable_constant_time = os.getenv(
            'FAVA_ENABLE_CONSTANT_TIME', 'true'
        ).lower() == 'true'
        
        config.enable_timing_jitter = os.getenv(
            'FAVA_ENABLE_TIMING_JITTER', 'true'
        ).lower() == 'true'
        
        config.enable_memory_protection = os.getenv(
            'FAVA_ENABLE_MEMORY_PROTECTION', 'true'
        ).lower() == 'true'
        
        try:
            config.base_operation_time = float(os.getenv(
                'FAVA_BASE_OPERATION_TIME', '0.001'
            ))
            config.jitter_percentage = float(os.getenv(
                'FAVA_JITTER_PERCENTAGE', '0.1'
            ))
            config.error_response_time = float(os.getenv(
                'FAVA_ERROR_RESPONSE_TIME', '0.01'
            ))
        except ValueError:
            logger.warning("Invalid timing configuration values, using defaults")
        
        return config
    
    def validate_security_settings(self) -> List[str]:
        """Validate that security settings are appropriate."""
        warnings = []
        
        if not self.enable_constant_time:
            warnings.append("Constant-time comparison is disabled - HIGH SECURITY RISK!")
        
        if not self.enable_timing_jitter:
            warnings.append("Timing jitter is disabled - may allow statistical timing analysis")
        
        if self.base_operation_time < 0.0001:  # Less than 0.1ms
            warnings.append("Base operation time is very low - may not provide sufficient protection")
        
        if self.jitter_percentage < 0.05:  # Less than 5%
            warnings.append("Jitter percentage is low - may allow timing pattern detection")
        
        return warnings


# Initialize default configuration
_default_config = TimingProtectionConfig.from_environment()

# Validate configuration on import
config_warnings = _default_config.validate_security_settings()
for warning in config_warnings:
    warnings.warn(warning, UserWarning)
    logger.warning(warning)

# Export configuration for other modules
timing_config = _default_config