"""
Enterprise dependency management with graceful fallbacks.

This module provides robust optional dependency handling to ensure enterprise
features work gracefully when optional libraries are not installed.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from functools import wraps
import importlib
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class DependencyInfo:
    """Information about an optional dependency."""
    name: str
    module: str
    version_requirement: str
    install_command: str
    description: str
    fallback_available: bool = False
    enterprise_critical: bool = False


class DependencyError(Exception):
    """Raised when a required enterprise dependency is not available."""
    pass


class DependencyManager:
    """Manages optional dependencies with graceful fallbacks."""
    
    ENTERPRISE_DEPENDENCIES = {
        'vault': DependencyInfo(
            name='HashiCorp Vault',
            module='hvac',
            version_requirement='>=1.0.0',
            install_command='pip install hvac>=1.0.0',
            description='HashiCorp Vault integration for enterprise key management',
            fallback_available=True,
            enterprise_critical=True
        ),
        'hsm': DependencyInfo(
            name='PKCS#11 HSM',
            module='pkcs11',
            version_requirement='>=0.7.0',
            install_command='pip install python-pkcs11>=0.7.0',
            description='Hardware Security Module integration via PKCS#11',
            fallback_available=True,
            enterprise_critical=True
        ),
        'prometheus': DependencyInfo(
            name='Prometheus Metrics',
            module='prometheus_client',
            version_requirement='>=0.12.0',
            install_command='pip install prometheus-client>=0.12.0',
            description='Prometheus metrics collection for monitoring',
            fallback_available=True,
            enterprise_critical=False
        ),
        'ldap': DependencyInfo(
            name='LDAP/Active Directory',
            module='ldap3',
            version_requirement='>=2.9.0',
            install_command='pip install ldap3>=2.9.0',
            description='LDAP/Active Directory authentication integration',
            fallback_available=True,
            enterprise_critical=False
        ),
        'oauth': DependencyInfo(
            name='OAuth/OIDC',
            module='requests_oauthlib',
            version_requirement='>=1.3.0',
            install_command='pip install requests-oauthlib>=1.3.0',
            description='OAuth/OpenID Connect authentication integration',
            fallback_available=True,
            enterprise_critical=False
        ),
        'kerberos': DependencyInfo(
            name='Kerberos/GSSAPI',
            module='gssapi',
            version_requirement='>=1.6.0',
            install_command='pip install gssapi>=1.6.0',
            description='Kerberos/GSSAPI enterprise authentication',
            fallback_available=True,
            enterprise_critical=False
        ),
        'opentelemetry': DependencyInfo(
            name='OpenTelemetry',
            module='opentelemetry.api',
            version_requirement='>=1.15.0',
            install_command='pip install opentelemetry-api>=1.15.0',
            description='OpenTelemetry observability and tracing',
            fallback_available=True,
            enterprise_critical=False
        ),
        'statsd': DependencyInfo(
            name='StatsD Metrics',
            module='statsd',
            version_requirement='>=3.3.0',
            install_command='pip install statsd>=3.3.0',
            description='StatsD metrics collection',
            fallback_available=True,
            enterprise_critical=False
        )
    }
    
    _instance: Optional['DependencyManager'] = None
    _availability_cache: Dict[str, bool] = {}
    _module_cache: Dict[str, Any] = {}
    
    def __new__(cls) -> 'DependencyManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._scan_dependencies()
    
    def _scan_dependencies(self) -> None:
        """Scan for available enterprise dependencies."""
        logger.info("Scanning for enterprise dependencies...")
        
        for dep_key, dep_info in self.ENTERPRISE_DEPENDENCIES.items():
            available = self._check_module_availability(dep_info.module)
            self._availability_cache[dep_key] = available
            
            if available:
                logger.info(f"✓ {dep_info.name} available")
            else:
                level = logging.WARNING if dep_info.enterprise_critical else logging.INFO
                logger.log(level, f"✗ {dep_info.name} not available - {dep_info.install_command}")
    
    def _check_module_availability(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def is_available(self, dependency: str) -> bool:
        """Check if a dependency is available."""
        return self._availability_cache.get(dependency, False)
    
    def get_module(self, dependency: str) -> Optional[Any]:
        """Get an imported module if available."""
        if not self.is_available(dependency):
            return None
            
        if dependency not in self._module_cache:
            dep_info = self.ENTERPRISE_DEPENDENCIES[dependency]
            try:
                self._module_cache[dependency] = importlib.import_module(dep_info.module)
            except ImportError:
                logger.error(f"Failed to import {dep_info.module} despite availability check")
                return None
                
        return self._module_cache[dependency]
    
    def require_dependency(self, dependency: str, feature_name: str) -> Any:
        """Require a dependency for a feature, raising error if not available."""
        if not self.is_available(dependency):
            dep_info = self.ENTERPRISE_DEPENDENCIES[dependency]
            raise DependencyError(
                f"{feature_name} requires {dep_info.name}. "
                f"Install with: {dep_info.install_command}"
            )
        return self.get_module(dependency)
    
    def get_enterprise_readiness(self) -> Dict[str, Any]:
        """Calculate enterprise readiness score and status."""
        total_deps = len(self.ENTERPRISE_DEPENDENCIES)
        available_deps = sum(1 for available in self._availability_cache.values() if available)
        
        # Weight critical dependencies more heavily
        critical_deps = [dep for dep in self.ENTERPRISE_DEPENDENCIES.values() if dep.enterprise_critical]
        available_critical = sum(
            1 for key, dep in self.ENTERPRISE_DEPENDENCIES.items() 
            if dep.enterprise_critical and self._availability_cache.get(key, False)
        )
        
        # Base score from all dependencies
        base_score = (available_deps / total_deps) * 60
        
        # Bonus for critical dependencies
        critical_score = (available_critical / len(critical_deps)) * 40 if critical_deps else 40
        
        total_score = base_score + critical_score
        
        # Determine readiness level
        if total_score >= 90:
            readiness_level = "ENTERPRISE_READY"
        elif total_score >= 70:
            readiness_level = "PARTIAL_READINESS"
        elif total_score >= 50:
            readiness_level = "BASIC_FUNCTIONALITY"
        else:
            readiness_level = "DEVELOPMENT_ONLY"
        
        return {
            'score': round(total_score, 1),
            'level': readiness_level,
            'available_dependencies': available_deps,
            'total_dependencies': total_deps,
            'critical_available': available_critical,
            'critical_total': len(critical_deps),
            'missing_dependencies': [
                key for key, available in self._availability_cache.items() 
                if not available
            ],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on missing dependencies."""
        recommendations = []
        
        missing_critical = [
            key for key, dep in self.ENTERPRISE_DEPENDENCIES.items()
            if dep.enterprise_critical and not self._availability_cache.get(key, False)
        ]
        
        if missing_critical:
            recommendations.append(
                f"Install critical enterprise dependencies: "
                f"{', '.join(self.ENTERPRISE_DEPENDENCIES[key].install_command for key in missing_critical)}"
            )
        
        missing_monitoring = [
            key for key in ['prometheus', 'opentelemetry', 'statsd']
            if not self._availability_cache.get(key, False)
        ]
        
        if missing_monitoring:
            recommendations.append(
                "Install monitoring dependencies for operational visibility"
            )
        
        missing_auth = [
            key for key in ['ldap', 'oauth', 'kerberos']
            if not self._availability_cache.get(key, False)
        ]
        
        if missing_auth:
            recommendations.append(
                "Install authentication dependencies for enterprise identity integration"
            )
        
        return recommendations


def enterprise_feature(dependency: str, fallback_value: Any = None, 
                      feature_name: Optional[str] = None):
    """
    Decorator to mark functions that require enterprise dependencies.
    
    Args:
        dependency: The dependency key from ENTERPRISE_DEPENDENCIES
        fallback_value: Value to return if dependency is not available
        feature_name: Human-readable feature name for error messages
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            dep_manager = DependencyManager()
            func_name = feature_name or func.__name__
            
            if not dep_manager.is_available(dependency):
                dep_info = dep_manager.ENTERPRISE_DEPENDENCIES.get(dependency)
                if dep_info:
                    logger.warning(
                        f"{func_name} requires {dep_info.name}. "
                        f"Install with: {dep_info.install_command}. "
                        f"Using fallback behavior."
                    )
                else:
                    logger.warning(f"{func_name} requires unknown dependency: {dependency}")
                
                if callable(fallback_value):
                    return fallback_value(*args, **kwargs)
                return fallback_value
            
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                logger.error(f"{func_name} failed due to import error: {e}")
                if callable(fallback_value):
                    return fallback_value(*args, **kwargs)
                return fallback_value
        
        # Mark function as enterprise feature
        wrapper._enterprise_feature = True
        wrapper._dependency = dependency
        wrapper._fallback_value = fallback_value
        
        return wrapper
    return decorator


class MockClient:
    """Mock client for unavailable enterprise services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._logged_warning = False
    
    def __getattr__(self, name: str) -> Callable:
        def mock_method(*args, **kwargs):
            if not self._logged_warning:
                logger.warning(
                    f"{self.service_name} operation '{name}' called but service is not available. "
                    f"This is a mock response."
                )
                self._logged_warning = True
            return None
        return mock_method


def get_dependency_manager() -> DependencyManager:
    """Get the singleton dependency manager instance."""
    return DependencyManager()