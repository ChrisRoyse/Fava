"""
Timing Attack Protection Security Configuration

This configuration file centralizes all timing attack protection settings and provides
secure defaults that address VULN-001 and VULN-002 identified by Security Audit Agent #2.

Security Settings:
- All timing operations configured for <2% variance maximum
- Error handling normalized to prevent timing oracles
- Memory access patterns randomized
- Statistical pattern elimination enabled
- High-precision timing measurements configured
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class TimingAttackProtectionConfig:
    """
    Centralized configuration for timing attack protection settings.
    
    This class provides secure defaults and environment-based configuration
    for all timing attack protection mechanisms.
    """
    
    # Core timing protection settings
    ENABLE_TIMING_PROTECTION = True
    ENABLE_CONSTANT_TIME_COMPARISONS = True
    ENABLE_ERROR_TIMING_NORMALIZATION = True
    ENABLE_STATISTICAL_PATTERN_MITIGATION = True
    ENABLE_MEMORY_ACCESS_NORMALIZATION = True
    
    # Timing variance targets (addressing VULN-001)
    TARGET_TIMING_VARIANCE_PERCENT = 1.0  # Target: 1% CV (down from 11.3%)
    MAXIMUM_TIMING_VARIANCE_PERCENT = 2.0  # Maximum: 2% CV allowed
    VULNERABILITY_THRESHOLD_PERCENT = 5.0  # Above this = vulnerable
    
    # Error timing settings (addressing VULN-002)
    ERROR_TIMING_NORMALIZATION_ENABLED = True
    UNIFORM_ERROR_RESPONSE_TIME_MS = 10.0  # 10ms uniform error time
    ERROR_JITTER_RANGE_MS = 2.0  # ±2ms jitter for error responses
    MAXIMUM_ERROR_TIMING_RATIO = 1.1  # Max 10% difference (down from 35.3x)
    
    # Statistical pattern elimination
    ADAPTIVE_JITTER_ENABLED = True
    BASE_JITTER_MS = 1.0  # 1ms base jitter
    ADAPTIVE_JITTER_MAX_MS = 10.0  # Maximum 10ms adaptive jitter
    TIMING_POOL_SIZE = 1000  # Pre-computed timing pool size
    PATTERN_DETECTION_THRESHOLD = 0.02  # 2% threshold for pattern detection
    
    # Memory access protection
    CACHE_LINE_POLLUTION_ENABLED = True
    CACHE_LINE_SIZE_BYTES = 64  # Standard x86/x64 cache line size
    MEMORY_POOL_COUNT = 16  # Number of memory pools for cache pollution
    MEMORY_ACCESS_RANDOMIZATION_ENABLED = True
    
    # Cryptographic operation settings
    CRYPTO_OPERATION_BASE_TIME_MS = 5.0  # 5ms base time for crypto ops
    SIGNATURE_VERIFICATION_TIME_MS = 5.0  # 5ms for signature verification
    KEY_VERIFICATION_TIME_MS = 2.0  # 2ms for key verification
    HASH_COMPARISON_TIME_MS = 1.0  # 1ms for hash comparisons
    
    # Testing and validation settings
    ENABLE_TIMING_MEASUREMENTS = False  # Disable in production
    TIMING_TEST_ITERATIONS = 10000  # Number of test iterations
    HIGH_PRECISION_TIMING_ENABLED = True
    STATISTICAL_ANALYSIS_ENABLED = True
    
    # Security hardening levels
    SECURITY_LEVEL_STANDARD = "standard"      # Basic protection
    SECURITY_LEVEL_HIGH = "high"             # Enhanced protection  
    SECURITY_LEVEL_DEFENSE = "defense"       # Maximum protection
    
    # Default security level
    DEFAULT_SECURITY_LEVEL = SECURITY_LEVEL_HIGH
    
    @classmethod
    def load_from_environment(cls) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary of configuration settings
        """
        config = {}
        
        # Core protection settings
        config['enable_timing_protection'] = cls._get_bool_env(
            'FAVA_ENABLE_TIMING_PROTECTION', cls.ENABLE_TIMING_PROTECTION
        )
        
        config['enable_constant_time'] = cls._get_bool_env(
            'FAVA_ENABLE_CONSTANT_TIME', cls.ENABLE_CONSTANT_TIME_COMPARISONS
        )
        
        config['enable_error_normalization'] = cls._get_bool_env(
            'FAVA_ENABLE_ERROR_NORMALIZATION', cls.ENABLE_ERROR_TIMING_NORMALIZATION
        )
        
        config['enable_pattern_mitigation'] = cls._get_bool_env(
            'FAVA_ENABLE_PATTERN_MITIGATION', cls.ENABLE_STATISTICAL_PATTERN_MITIGATION
        )
        
        config['enable_memory_protection'] = cls._get_bool_env(
            'FAVA_ENABLE_MEMORY_PROTECTION', cls.ENABLE_MEMORY_ACCESS_NORMALIZATION
        )
        
        # Timing variance settings
        config['target_variance_percent'] = cls._get_float_env(
            'FAVA_TARGET_VARIANCE_PERCENT', cls.TARGET_TIMING_VARIANCE_PERCENT
        )
        
        config['max_variance_percent'] = cls._get_float_env(
            'FAVA_MAX_VARIANCE_PERCENT', cls.MAXIMUM_TIMING_VARIANCE_PERCENT
        )
        
        # Error timing settings
        config['error_response_time_ms'] = cls._get_float_env(
            'FAVA_ERROR_RESPONSE_TIME_MS', cls.UNIFORM_ERROR_RESPONSE_TIME_MS
        )
        
        config['error_jitter_ms'] = cls._get_float_env(
            'FAVA_ERROR_JITTER_MS', cls.ERROR_JITTER_RANGE_MS
        )
        
        # Security level
        config['security_level'] = os.getenv(
            'FAVA_SECURITY_LEVEL', cls.DEFAULT_SECURITY_LEVEL
        ).lower()
        
        # Apply security level adjustments
        config = cls._apply_security_level_settings(config, config['security_level'])
        
        return config
    
    @classmethod
    def _get_bool_env(cls, env_var: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(env_var, str(default)).lower()
        return value in ('true', '1', 'yes', 'on', 'enabled')
    
    @classmethod
    def _get_float_env(cls, env_var: str, default: float) -> float:
        """Get float value from environment variable."""
        try:
            return float(os.getenv(env_var, str(default)))
        except ValueError:
            return default
    
    @classmethod
    def _apply_security_level_settings(cls, config: Dict[str, Any], security_level: str) -> Dict[str, Any]:
        """
        Apply security level specific settings.
        
        Args:
            config: Base configuration
            security_level: Security level to apply
            
        Returns:
            Updated configuration with security level settings
        """
        if security_level == cls.SECURITY_LEVEL_STANDARD:
            # Standard security - basic protection
            config['target_variance_percent'] = 2.0  # 2% target
            config['error_response_time_ms'] = 5.0   # 5ms error time
            config['adaptive_jitter_max_ms'] = 5.0   # 5ms max jitter
            
        elif security_level == cls.SECURITY_LEVEL_HIGH:
            # High security - enhanced protection
            config['target_variance_percent'] = 1.0  # 1% target
            config['error_response_time_ms'] = 10.0  # 10ms error time
            config['adaptive_jitter_max_ms'] = 10.0  # 10ms max jitter
            config['memory_pool_count'] = 16         # More memory pools
            
        elif security_level == cls.SECURITY_LEVEL_DEFENSE:
            # Defense level - maximum protection
            config['target_variance_percent'] = 0.5  # 0.5% target
            config['error_response_time_ms'] = 15.0  # 15ms error time
            config['adaptive_jitter_max_ms'] = 15.0  # 15ms max jitter
            config['memory_pool_count'] = 32         # Maximum memory pools
            config['timing_pool_size'] = 2000        # Larger timing pools
            
        else:
            # Default to high security
            config['target_variance_percent'] = cls.TARGET_TIMING_VARIANCE_PERCENT
            config['error_response_time_ms'] = cls.UNIFORM_ERROR_RESPONSE_TIME_MS
        
        return config
    
    @classmethod
    def get_crypto_operation_config(cls, security_level: Optional[str] = None) -> Dict[str, float]:
        """
        Get timing configuration for cryptographic operations.
        
        Args:
            security_level: Security level (optional)
            
        Returns:
            Dictionary of crypto operation timing settings
        """
        if security_level is None:
            security_level = cls.DEFAULT_SECURITY_LEVEL
        
        base_times = {
            'signature_verification': cls.SIGNATURE_VERIFICATION_TIME_MS / 1000.0,
            'key_verification': cls.KEY_VERIFICATION_TIME_MS / 1000.0,
            'hash_comparison': cls.HASH_COMPARISON_TIME_MS / 1000.0,
            'crypto_operation': cls.CRYPTO_OPERATION_BASE_TIME_MS / 1000.0,
            'error_handling': cls.UNIFORM_ERROR_RESPONSE_TIME_MS / 1000.0,
        }
        
        # Adjust for security level
        if security_level == cls.SECURITY_LEVEL_DEFENSE:
            # Increase all times for maximum security
            for key in base_times:
                base_times[key] *= 1.5
        elif security_level == cls.SECURITY_LEVEL_STANDARD:
            # Reduce times for better performance
            for key in base_times:
                base_times[key] *= 0.7
        
        return base_times
    
    @classmethod
    def validate_configuration(cls, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration settings and return warnings.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check if timing protection is enabled
        if not config.get('enable_timing_protection', True):
            warnings.append("CRITICAL: Timing attack protection is disabled!")
        
        # Check variance targets
        target_variance = config.get('target_variance_percent', 1.0)
        if target_variance > 2.0:
            warnings.append(f"WARNING: Target variance {target_variance}% may allow timing attacks")
        
        # Check error timing settings
        if not config.get('enable_error_normalization', True):
            warnings.append("HIGH: Error timing normalization disabled - VULN-002 risk")
        
        # Check if constant-time comparisons are enabled
        if not config.get('enable_constant_time', True):
            warnings.append("CRITICAL: Constant-time comparisons disabled - VULN-001 risk")
        
        # Check security level
        security_level = config.get('security_level', 'high')
        if security_level not in [cls.SECURITY_LEVEL_STANDARD, cls.SECURITY_LEVEL_HIGH, cls.SECURITY_LEVEL_DEFENSE]:
            warnings.append(f"WARNING: Unknown security level '{security_level}'")
        
        return warnings
    
    @classmethod
    def export_config_template(cls, filename: str = "timing_protection_config.json") -> None:
        """
        Export a configuration template file.
        
        Args:
            filename: Name of the template file to create
        """
        import json
        
        template = {
            "_description": "Timing Attack Protection Configuration Template",
            "_security_levels": [
                cls.SECURITY_LEVEL_STANDARD,
                cls.SECURITY_LEVEL_HIGH, 
                cls.SECURITY_LEVEL_DEFENSE
            ],
            "timing_protection": {
                "enabled": cls.ENABLE_TIMING_PROTECTION,
                "security_level": cls.DEFAULT_SECURITY_LEVEL,
                "target_variance_percent": cls.TARGET_TIMING_VARIANCE_PERCENT,
                "max_variance_percent": cls.MAXIMUM_TIMING_VARIANCE_PERCENT
            },
            "constant_time_operations": {
                "enabled": cls.ENABLE_CONSTANT_TIME_COMPARISONS,
                "crypto_base_time_ms": cls.CRYPTO_OPERATION_BASE_TIME_MS,
                "signature_verification_ms": cls.SIGNATURE_VERIFICATION_TIME_MS,
                "key_verification_ms": cls.KEY_VERIFICATION_TIME_MS
            },
            "error_timing_normalization": {
                "enabled": cls.ENABLE_ERROR_TIMING_NORMALIZATION,
                "uniform_response_time_ms": cls.UNIFORM_ERROR_RESPONSE_TIME_MS,
                "jitter_range_ms": cls.ERROR_JITTER_RANGE_MS,
                "max_timing_ratio": cls.MAXIMUM_ERROR_TIMING_RATIO
            },
            "statistical_pattern_mitigation": {
                "enabled": cls.ENABLE_STATISTICAL_PATTERN_MITIGATION,
                "adaptive_jitter_enabled": cls.ADAPTIVE_JITTER_ENABLED,
                "base_jitter_ms": cls.BASE_JITTER_MS,
                "max_jitter_ms": cls.ADAPTIVE_JITTER_MAX_MS,
                "timing_pool_size": cls.TIMING_POOL_SIZE
            },
            "memory_access_protection": {
                "enabled": cls.ENABLE_MEMORY_ACCESS_NORMALIZATION,
                "cache_pollution_enabled": cls.CACHE_LINE_POLLUTION_ENABLED,
                "cache_line_size": cls.CACHE_LINE_SIZE_BYTES,
                "memory_pool_count": cls.MEMORY_POOL_COUNT
            },
            "testing_validation": {
                "enable_measurements": cls.ENABLE_TIMING_MEASUREMENTS,
                "test_iterations": cls.TIMING_TEST_ITERATIONS,
                "high_precision_timing": cls.HIGH_PRECISION_TIMING_ENABLED
            },
            "environment_variables": {
                "FAVA_ENABLE_TIMING_PROTECTION": "Enable/disable timing attack protection",
                "FAVA_SECURITY_LEVEL": "Security level: standard|high|defense",
                "FAVA_TARGET_VARIANCE_PERCENT": "Target timing variance percentage",
                "FAVA_ENABLE_CONSTANT_TIME": "Enable constant-time comparisons",
                "FAVA_ENABLE_ERROR_NORMALIZATION": "Enable error timing normalization",
                "FAVA_ERROR_RESPONSE_TIME_MS": "Uniform error response time in ms"
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Configuration template exported to: {filename}")


# Global configuration instance
_global_config = None

def get_timing_protection_config() -> Dict[str, Any]:
    """
    Get the global timing protection configuration.
    
    Returns:
        Dictionary of timing protection settings
    """
    global _global_config
    
    if _global_config is None:
        _global_config = TimingAttackProtectionConfig.load_from_environment()
        
        # Validate configuration
        warnings = TimingAttackProtectionConfig.validate_configuration(_global_config)
        if warnings:
            import logging
            logger = logging.getLogger(__name__)
            for warning in warnings:
                logger.warning(f"Configuration warning: {warning}")
    
    return _global_config


def initialize_timing_protection():
    """
    Initialize timing attack protection with current configuration.
    This should be called at application startup.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    config = get_timing_protection_config()
    
    logger.info("Initializing timing attack protection...")
    logger.info(f"Security level: {config.get('security_level', 'unknown')}")
    logger.info(f"Target timing variance: {config.get('target_variance_percent', 0):.1f}%")
    logger.info(f"Constant-time operations: {'enabled' if config.get('enable_constant_time') else 'disabled'}")
    logger.info(f"Error timing normalization: {'enabled' if config.get('enable_error_normalization') else 'disabled'}")
    logger.info(f"Pattern mitigation: {'enabled' if config.get('enable_pattern_mitigation') else 'disabled'}")
    logger.info(f"Memory protection: {'enabled' if config.get('enable_memory_protection') else 'disabled'}")
    
    if not config.get('enable_timing_protection'):
        logger.critical("SECURITY WARNING: Timing attack protection is DISABLED!")
        
    logger.info("Timing attack protection initialization complete")


# Initialize on import if needed
if os.getenv('FAVA_AUTO_INIT_TIMING_PROTECTION', 'false').lower() == 'true':
    initialize_timing_protection()


# Export main configuration class and functions
__all__ = [
    'TimingAttackProtectionConfig',
    'get_timing_protection_config', 
    'initialize_timing_protection'
]