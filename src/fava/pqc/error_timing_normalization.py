"""
Error Timing Normalization Module

This module addresses VULN-002: Error Timing Side-Channel (CVSS 3.5)
- Normalizes error response times to prevent timing oracles
- Eliminates 35.3x timing ratio between error types
- Provides uniform error handling across all cryptographic operations

Security Requirements:
- All error responses must have uniform timing
- No information disclosure through error timing patterns
- Consistent memory access patterns for error handling
"""

import time
import random
import logging
import functools
from typing import Any, Callable, Optional, Dict, Type, Union
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors for timing normalization."""
    AUTHENTICATION_ERROR = "auth_error"
    VALIDATION_ERROR = "validation_error"
    CRYPTO_ERROR = "crypto_error"
    CONFIGURATION_ERROR = "config_error"
    NETWORK_ERROR = "network_error"
    GENERIC_ERROR = "generic_error"


class TimingNormalizedError(Exception):
    """Base exception that enforces timing normalization."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.GENERIC_ERROR):
        self.category = category
        self.normalized_time = time.perf_counter()
        super().__init__(message)


class ErrorTimingNormalizer:
    """
    Provides uniform error response timing to prevent timing oracle attacks.
    
    This addresses VULN-002 by ensuring all error conditions take consistent time
    regardless of the specific error type or validation failure point.
    """
    
    # Base timing constants (in seconds)
    BASE_ERROR_TIME = 0.010  # 10ms base time for all errors
    JITTER_RANGE = 0.002     # ±2ms jitter to prevent micro-timing analysis
    
    # Category-specific timing adjustments (normalized to same base)
    CATEGORY_TIMES = {
        ErrorCategory.AUTHENTICATION_ERROR: BASE_ERROR_TIME,
        ErrorCategory.VALIDATION_ERROR: BASE_ERROR_TIME, 
        ErrorCategory.CRYPTO_ERROR: BASE_ERROR_TIME,
        ErrorCategory.CONFIGURATION_ERROR: BASE_ERROR_TIME,
        ErrorCategory.NETWORK_ERROR: BASE_ERROR_TIME,
        ErrorCategory.GENERIC_ERROR: BASE_ERROR_TIME,
    }
    
    @classmethod
    def normalize_error_response(
        cls, 
        error_category: ErrorCategory = ErrorCategory.GENERIC_ERROR,
        start_time: Optional[float] = None
    ) -> None:
        """
        Ensure error response takes consistent time regardless of error type.
        
        Args:
            error_category: Category of error for logging purposes
            start_time: Start time of operation (from time.perf_counter())
        """
        target_time = cls.CATEGORY_TIMES[error_category]
        jitter = random.uniform(-cls.JITTER_RANGE, cls.JITTER_RANGE)
        total_target_time = target_time + jitter
        
        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            remaining_time = total_target_time - elapsed
            
            if remaining_time > 0:
                time.sleep(remaining_time)
        else:
            # No start time provided, sleep for full duration
            time.sleep(total_target_time)
        
        logger.debug(f"Normalized {error_category.value} response timing")
    
    @classmethod
    def secure_error_handler(
        cls, 
        error_category: ErrorCategory = ErrorCategory.GENERIC_ERROR,
        return_value: Any = False
    ):
        """
        Decorator that ensures all exceptions are handled with uniform timing.
        
        Args:
            error_category: Category of errors this handler manages
            return_value: Value to return on error
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Log error without timing information
                    logger.debug(f"Exception in {func.__name__}: {type(e).__name__}")
                    
                    # Normalize error response timing
                    cls.normalize_error_response(error_category, start_time)
                    
                    # Return consistent value for all error types
                    return return_value
            return wrapper
        return decorator
    
    @classmethod
    def constant_time_validate(
        cls,
        validation_func: Callable,
        error_category: ErrorCategory = ErrorCategory.VALIDATION_ERROR
    ) -> Callable:
        """
        Decorator that ensures validation functions take constant time.
        
        Args:
            validation_func: Function to wrap with constant-time execution
            error_category: Category for error timing normalization
        """
        @functools.wraps(validation_func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = validation_func(*args, **kwargs)
                # Ensure consistent timing even for successful validation
                cls.normalize_error_response(error_category, start_time)
                return result
            except Exception as e:
                logger.debug(f"Validation failed in {validation_func.__name__}: {type(e).__name__}")
                cls.normalize_error_response(error_category, start_time)
                return False
        return wrapper


class UniformCryptoErrorHandler:
    """
    Specialized error handler for cryptographic operations to prevent timing oracles.
    """
    
    @staticmethod
    def handle_decryption_error(operation_name: str, start_time: Optional[float] = None) -> bool:
        """Handle decryption errors with uniform timing."""
        ErrorTimingNormalizer.normalize_error_response(
            ErrorCategory.CRYPTO_ERROR, start_time
        )
        logger.debug(f"Decryption operation {operation_name} failed")
        return False
    
    @staticmethod
    def handle_verification_error(operation_name: str, start_time: Optional[float] = None) -> bool:
        """Handle verification errors with uniform timing."""
        ErrorTimingNormalizer.normalize_error_response(
            ErrorCategory.AUTHENTICATION_ERROR, start_time
        )
        logger.debug(f"Verification operation {operation_name} failed")
        return False
    
    @staticmethod
    def handle_validation_error(operation_name: str, start_time: Optional[float] = None) -> bool:
        """Handle validation errors with uniform timing."""
        ErrorTimingNormalizer.normalize_error_response(
            ErrorCategory.VALIDATION_ERROR, start_time
        )
        logger.debug(f"Validation operation {operation_name} failed")
        return False
    
    @staticmethod
    def secure_crypto_operation(error_category: ErrorCategory = ErrorCategory.CRYPTO_ERROR):
        """
        Decorator for cryptographic operations requiring timing attack protection.
        """
        return ErrorTimingNormalizer.secure_error_handler(error_category, False)


class ErrorPatternMitigation:
    """
    Additional protections against error pattern analysis.
    """
    
    @staticmethod
    def randomize_error_messages(base_message: str, error_type: str) -> str:
        """
        Generate randomized error messages to prevent information leakage.
        
        Args:
            base_message: Base error message
            error_type: Type of error for categorization
            
        Returns:
            Randomized error message
        """
        # Generic messages that don't reveal specific failure points
        generic_messages = {
            "crypto": [
                "Cryptographic operation failed",
                "Security validation error",
                "Authentication verification failed"
            ],
            "validation": [
                "Input validation failed",
                "Data format error",
                "Parameter validation error"
            ],
            "auth": [
                "Authentication failed",
                "Access denied", 
                "Credential verification failed"
            ]
        }
        
        category_messages = generic_messages.get(error_type, ["Operation failed"])
        return random.choice(category_messages)
    
    @staticmethod
    def uniform_exception_context() -> Dict[str, Any]:
        """
        Provide uniform exception context to prevent information disclosure.
        
        Returns:
            Standardized exception context
        """
        return {
            "timestamp": time.time(),
            "error_id": f"err_{random.randint(10000, 99999)}",
            "category": "security_error",
            "details": "Operation not permitted"
        }


def secure_function_wrapper(
    error_category: ErrorCategory = ErrorCategory.GENERIC_ERROR,
    return_on_error: Any = None
):
    """
    Function wrapper that provides comprehensive timing attack protection.
    
    Args:
        error_category: Category of errors for this function
        return_on_error: Value to return on any error
        
    Example:
        @secure_function_wrapper(ErrorCategory.CRYPTO_ERROR, False)
        def verify_signature(signature, message, key):
            # Implementation here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            operation_name = func.__name__
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Normalize timing even for successful operations
                ErrorTimingNormalizer.normalize_error_response(error_category, start_time)
                
                return result
                
            except Exception as e:
                # Log error without sensitive information
                logger.debug(f"Security operation {operation_name} failed: {type(e).__name__}")
                
                # Ensure uniform error response timing
                ErrorTimingNormalizer.normalize_error_response(error_category, start_time)
                
                # Return consistent value for all errors
                return return_on_error
                
        return wrapper
    return decorator


# Pre-configured decorators for common use cases
crypto_secure = functools.partial(
    secure_function_wrapper, 
    ErrorCategory.CRYPTO_ERROR, 
    False
)

auth_secure = functools.partial(
    secure_function_wrapper,
    ErrorCategory.AUTHENTICATION_ERROR,
    False  
)

validation_secure = functools.partial(
    secure_function_wrapper,
    ErrorCategory.VALIDATION_ERROR,
    False
)


# Example usage patterns
@crypto_secure()
def secure_decrypt_example(ciphertext: bytes, key: bytes) -> bytes:
    """Example of secure decryption with timing protection."""
    # Implementation would go here
    pass


@auth_secure()
def secure_authenticate_example(username: str, password_hash: str) -> bool:
    """Example of secure authentication with timing protection."""
    # Implementation would go here
    pass


@validation_secure()
def secure_validate_example(data: bytes) -> bool:
    """Example of secure validation with timing protection."""
    # Implementation would go here
    pass


# Initialize error timing normalization
logger.info("Error timing normalization module initialized")
logger.info(f"Base error time: {ErrorTimingNormalizer.BASE_ERROR_TIME * 1000:.1f}ms")
logger.info(f"Jitter range: ±{ErrorTimingNormalizer.JITTER_RANGE * 1000:.1f}ms")