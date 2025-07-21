"""
Enterprise deployment automation and validation tools.

This module provides comprehensive deployment automation for enterprise environments
including platform validation, dependency management, and deployment verification.
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
import time
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import tempfile

from .dependency_manager import DependencyManager, enterprise_feature

logger = logging.getLogger(__name__)


@dataclass
class PlatformInfo:
    """Information about the deployment platform."""
    system: str
    release: str
    version: str
    machine: str
    processor: str
    python_version: str
    python_executable: str
    architecture: str
    is_64bit: bool


@dataclass
class DeploymentConfig:
    """Configuration for enterprise deployment."""
    target_environment: str  # 'development', 'staging', 'production'
    install_optional_deps: bool = True
    enable_monitoring: bool = True
    enable_audit_logging: bool = True
    vault_config: Optional[Dict[str, str]] = None
    hsm_config: Optional[Dict[str, str]] = None
    monitoring_config: Optional[Dict[str, str]] = None
    performance_config: Optional[Dict[str, Any]] = None
    
    # Platform-specific settings
    windows_service: bool = False
    systemd_service: bool = False
    docker_deployment: bool = False


@dataclass
class DeploymentResult:
    """Result of deployment operation."""
    success: bool
    platform_info: PlatformInfo
    installed_dependencies: List[str] = field(default_factory=list)
    failed_dependencies: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    duration: float = 0.0


class PlatformChecker:
    """Cross-platform compatibility checker."""
    
    @staticmethod
    def get_platform_info() -> PlatformInfo:
        """Get comprehensive platform information."""
        system = platform.system()
        
        return PlatformInfo(
            system=system,
            release=platform.release(),
            version=platform.version(),
            machine=platform.machine(),
            processor=platform.processor() or "unknown",
            python_version=platform.python_version(),
            python_executable=sys.executable,
            architecture=platform.architecture()[0],
            is_64bit=sys.maxsize > 2**32
        )
    
    @staticmethod
    def check_platform_compatibility() -> Tuple[bool, List[str]]:
        """Check if platform is compatible with Fava PQC."""
        issues = []
        platform_info = PlatformChecker.get_platform_info()
        
        # Check Python version
        python_version = tuple(map(int, platform_info.python_version.split('.')))
        if python_version < (3, 10):
            issues.append(f"Python {platform_info.python_version} is not supported. Minimum: 3.10")
        
        # Check architecture
        if not platform_info.is_64bit:
            issues.append("32-bit systems are not supported")
        
        # Platform-specific checks
        if platform_info.system == "Windows":
            issues.extend(PlatformChecker._check_windows_compatibility())
        elif platform_info.system == "Linux":
            issues.extend(PlatformChecker._check_linux_compatibility())
        elif platform_info.system == "Darwin":  # macOS
            issues.extend(PlatformChecker._check_macos_compatibility())
        else:
            issues.append(f"Platform {platform_info.system} is not officially supported")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def _check_windows_compatibility() -> List[str]:
        """Check Windows-specific compatibility."""
        issues = []
        
        # Check Windows version
        version = platform.version()
        try:
            # Extract build number from version string
            build = int(version.split('.')[-1])
            if build < 10240:  # Windows 10 build 10240
                issues.append("Windows 10 or newer is required")
        except (ValueError, IndexError):
            issues.append("Unable to determine Windows version")
        
        return issues
    
    @staticmethod
    def _check_linux_compatibility() -> List[str]:
        """Check Linux-specific compatibility."""
        issues = []
        
        # Check for required system libraries
        required_libs = ['libc.so.6', 'libssl.so', 'libcrypto.so']
        for lib in required_libs:
            if not PlatformChecker._find_library(lib):
                issues.append(f"Required system library not found: {lib}")
        
        return issues
    
    @staticmethod
    def _check_macos_compatibility() -> List[str]:
        """Check macOS-specific compatibility."""
        issues = []
        
        # Check macOS version
        version = platform.mac_ver()[0]
        if version:
            try:
                major, minor = map(int, version.split('.')[:2])
                if (major, minor) < (10, 15):
                    issues.append("macOS 10.15 (Catalina) or newer is required")
            except (ValueError, IndexError):
                issues.append("Unable to determine macOS version")
        
        return issues
    
    @staticmethod
    def _find_library(lib_name: str) -> bool:
        """Check if a library exists on the system."""
        try:
            # Try common library paths
            lib_paths = [
                '/lib', '/lib64', '/usr/lib', '/usr/lib64',
                '/usr/local/lib', '/opt/lib'
            ]
            
            for path in lib_paths:
                lib_path = Path(path)
                if lib_path.exists():
                    for lib_file in lib_path.glob(f"{lib_name}*"):
                        return True
            
            # Try using ldconfig on Linux
            if platform.system() == "Linux":
                result = subprocess.run(['ldconfig', '-p'], 
                                      capture_output=True, text=True, timeout=10)
                return lib_name in result.stdout
        except Exception:
            pass
        
        return False


class DependencyInstaller:
    """Automated dependency installation for enterprise features."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
    
    def install_enterprise_dependencies(self, 
                                      config: DeploymentConfig) -> Tuple[List[str], List[str]]:
        """Install enterprise dependencies based on configuration."""
        installed = []
        failed = []
        
        if not config.install_optional_deps:
            logger.info("Skipping optional dependency installation per configuration")
            return installed, failed
        
        # Define dependency groups
        core_enterprise = ['vault', 'hsm']
        monitoring = ['prometheus', 'opentelemetry', 'statsd']
        authentication = ['ldap', 'oauth', 'kerberos']
        
        # Install based on configuration and environment
        deps_to_install = []
        
        if config.target_environment == 'production':
            deps_to_install.extend(core_enterprise)
            
        if config.enable_monitoring:
            deps_to_install.extend(monitoring)
            
        if config.target_environment in ['staging', 'production']:
            deps_to_install.extend(authentication)
        
        # Install dependencies
        for dep_key in deps_to_install:
            if self._install_dependency(dep_key):
                installed.append(dep_key)
            else:
                failed.append(dep_key)
        
        return installed, failed
    
    def _install_dependency(self, dep_key: str) -> bool:
        """Install a single dependency."""
        if self.dep_manager.is_available(dep_key):
            logger.info(f"Dependency {dep_key} already available")
            return True
        
        dep_info = self.dep_manager.ENTERPRISE_DEPENDENCIES.get(dep_key)
        if not dep_info:
            logger.error(f"Unknown dependency: {dep_key}")
            return False
        
        logger.info(f"Installing {dep_info.name}...")
        
        try:
            # Extract package name from install command
            install_cmd = dep_info.install_command
            if install_cmd.startswith('pip install '):
                package_spec = install_cmd[12:]  # Remove 'pip install '
                
                # Run pip install
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package_spec
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"Successfully installed {dep_info.name}")
                    return True
                else:
                    logger.error(f"Failed to install {dep_info.name}: {result.stderr}")
                    return False
            else:
                logger.warning(f"Non-pip install command for {dep_key}: {install_cmd}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Installation timeout for {dep_info.name}")
            return False
        except Exception as e:
            logger.error(f"Installation error for {dep_info.name}: {e}")
            return False
    
    def create_requirements_file(self, config: DeploymentConfig, 
                                file_path: Optional[str] = None) -> str:
        """Create requirements.txt file for enterprise deployment."""
        if not file_path:
            file_path = "requirements-enterprise.txt"
        
        requirements = []
        
        # Base requirements (already in pyproject.toml)
        base_requirements = [
            "fava",  # Will install base dependencies
        ]
        
        # Add enterprise dependencies based on config
        if config.install_optional_deps:
            for dep_key, dep_info in self.dep_manager.ENTERPRISE_DEPENDENCIES.items():
                if self._should_include_dependency(dep_key, config):
                    # Extract package and version from install command
                    install_cmd = dep_info.install_command
                    if install_cmd.startswith('pip install '):
                        package_spec = install_cmd[12:]
                        requirements.append(package_spec)
        
        # Write requirements file
        with open(file_path, 'w') as f:
            f.write("# Enterprise deployment requirements for Fava PQC\n")
            f.write(f"# Generated for {config.target_environment} environment\n\n")
            
            f.write("# Base requirements\n")
            for req in base_requirements:
                f.write(f"{req}\n")
            
            if requirements:
                f.write("\n# Enterprise optional dependencies\n")
                for req in requirements:
                    f.write(f"{req}\n")
        
        logger.info(f"Requirements file created: {file_path}")
        return file_path
    
    def _should_include_dependency(self, dep_key: str, config: DeploymentConfig) -> bool:
        """Determine if a dependency should be included based on config."""
        monitoring_deps = ['prometheus', 'opentelemetry', 'statsd']
        auth_deps = ['ldap', 'oauth', 'kerberos']
        
        if dep_key in ['vault', 'hsm'] and config.target_environment == 'production':
            return True
        elif dep_key in monitoring_deps and config.enable_monitoring:
            return True
        elif dep_key in auth_deps and config.target_environment in ['staging', 'production']:
            return True
        
        return False


class DeploymentValidator:
    """Validates enterprise deployment configuration and environment."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.platform_checker = PlatformChecker()
    
    def validate_deployment(self, config: DeploymentConfig) -> DeploymentResult:
        """Comprehensive deployment validation."""
        start_time = time.time()
        platform_info = self.platform_checker.get_platform_info()
        result = DeploymentResult(success=False, platform_info=platform_info)
        
        logger.info("Starting enterprise deployment validation...")
        
        try:
            # Check platform compatibility
            compatible, platform_issues = self.platform_checker.check_platform_compatibility()
            if not compatible:
                result.errors.extend(platform_issues)
                return result
            
            # Validate Python environment
            self._validate_python_environment(result)
            
            # Check dependencies
            self._check_dependencies(config, result)
            
            # Validate configuration
            self._validate_configuration(config, result)
            
            # Check system resources
            self._check_system_resources(result)
            
            # Generate recommendations
            self._generate_recommendations(config, result)
            
            # Overall success determination
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(f"Deployment validation failed: {str(e)}")
        
        result.duration = time.time() - start_time
        logger.info(f"Deployment validation completed in {result.duration:.2f}s")
        
        return result
    
    def _validate_python_environment(self, result: DeploymentResult) -> None:
        """Validate Python environment setup."""
        # Check pip availability
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError):
            result.errors.append("pip is not available or not working")
        
        # Check virtual environment (recommended)
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            result.warnings.append("Not running in a virtual environment (recommended for production)")
    
    def _check_dependencies(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Check dependency availability and requirements."""
        enterprise_readiness = self.dep_manager.get_enterprise_readiness()
        
        # Check for critical missing dependencies
        critical_missing = [
            dep for dep, dep_info in self.dep_manager.ENTERPRISE_DEPENDENCIES.items()
            if dep_info.enterprise_critical and not self.dep_manager.is_available(dep)
        ]
        
        if critical_missing and config.target_environment == 'production':
            result.errors.extend([
                f"Critical enterprise dependency missing: {dep}"
                for dep in critical_missing
            ])
        
        # Record available dependencies
        result.installed_dependencies = [
            dep for dep in self.dep_manager.ENTERPRISE_DEPENDENCIES.keys()
            if self.dep_manager.is_available(dep)
        ]
        
        result.failed_dependencies = [
            dep for dep in self.dep_manager.ENTERPRISE_DEPENDENCIES.keys()
            if not self.dep_manager.is_available(dep)
        ]
    
    def _validate_configuration(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Validate deployment configuration."""
        # Validate Vault configuration
        if config.vault_config:
            vault_url = config.vault_config.get('url')
            if vault_url and not vault_url.startswith(('http://', 'https://')):
                result.errors.append("Invalid Vault URL format")
        
        # Validate HSM configuration
        if config.hsm_config:
            library_path = config.hsm_config.get('library_path')
            if library_path and not Path(library_path).exists():
                result.warnings.append(f"HSM library path does not exist: {library_path}")
        
        # Validate environment-specific requirements
        if config.target_environment == 'production':
            if not config.enable_audit_logging:
                result.errors.append("Audit logging must be enabled for production")
            
            if not config.enable_monitoring:
                result.warnings.append("Monitoring is recommended for production")
    
    def _check_system_resources(self, result: DeploymentResult) -> None:
        """Check system resources and requirements."""
        try:
            # Check disk space
            disk_usage = shutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 1:  # Less than 1GB free
                result.warnings.append(f"Low disk space: {free_gb:.1f}GB free")
            
            # Check memory (approximate)
            try:
                import psutil
                memory = psutil.virtual_memory()
                if memory.total < 2 * 1024**3:  # Less than 2GB RAM
                    result.warnings.append(f"Low system memory: {memory.total / (1024**3):.1f}GB")
            except ImportError:
                result.warnings.append("Cannot check system memory (psutil not available)")
            
        except Exception as e:
            result.warnings.append(f"Could not check system resources: {e}")
    
    def _generate_recommendations(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Generate deployment recommendations."""
        recommendations = []
        
        # Dependency recommendations
        if result.failed_dependencies:
            recommendations.append(
                f"Install missing dependencies: pip install {' '.join(result.failed_dependencies)}"
            )
        
        # Environment-specific recommendations
        if config.target_environment == 'production':
            if not config.vault_config:
                recommendations.append("Configure HashiCorp Vault for production key management")
            
            if not config.hsm_config:
                recommendations.append("Consider HSM integration for enhanced security")
            
            if result.platform_info.system == 'Linux' and not config.systemd_service:
                recommendations.append("Consider creating systemd service for production deployment")
        
        # Platform-specific recommendations
        if result.platform_info.system == 'Windows' and config.target_environment == 'production':
            if not config.windows_service:
                recommendations.append("Consider Windows service installation for production")
        
        result.recommendations.extend(recommendations)


class AutomatedDeployment:
    """Automated enterprise deployment orchestrator."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.validator = DeploymentValidator()
        self.installer = DependencyInstaller()
    
    def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Execute automated enterprise deployment."""
        start_time = time.time()
        logger.info(f"Starting automated deployment for {config.target_environment} environment")
        
        # Validate deployment
        result = self.validator.validate_deployment(config)
        
        if not result.success:
            logger.error("Deployment validation failed")
            return result
        
        try:
            # Install dependencies
            if config.install_optional_deps:
                installed, failed = self.installer.install_enterprise_dependencies(config)
                result.installed_dependencies.extend(installed)
                result.failed_dependencies.extend(failed)
                
                if failed:
                    result.warnings.append(f"Failed to install some dependencies: {failed}")
            
            # Create configuration files
            self._create_configuration_files(config, result)
            
            # Setup monitoring
            if config.enable_monitoring:
                self._setup_monitoring(config, result)
            
            # Setup audit logging
            if config.enable_audit_logging:
                self._setup_audit_logging(config, result)
            
            # Platform-specific deployment
            self._platform_specific_deployment(config, result)
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(f"Deployment failed: {str(e)}")
            result.success = False
        
        result.duration = time.time() - start_time
        
        status = "✓ SUCCESS" if result.success else "✗ FAILED"
        logger.info(f"Deployment completed: {status} ({result.duration:.2f}s)")
        
        return result
    
    def _create_configuration_files(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Create necessary configuration files."""
        try:
            # Create requirements file
            req_file = self.installer.create_requirements_file(config)
            result.recommendations.append(f"Requirements file created: {req_file}")
            
            # Create environment-specific config
            env_config = {
                'environment': config.target_environment,
                'monitoring_enabled': config.enable_monitoring,
                'audit_logging_enabled': config.enable_audit_logging,
                'vault_config': config.vault_config,
                'hsm_config': config.hsm_config,
                'generated_at': time.time()
            }
            
            config_file = f"fava-pqc-{config.target_environment}.json"
            with open(config_file, 'w') as f:
                json.dump(env_config, f, indent=2)
            
            result.recommendations.append(f"Configuration file created: {config_file}")
            
        except Exception as e:
            result.errors.append(f"Failed to create configuration files: {e}")
    
    def _setup_monitoring(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Setup monitoring infrastructure."""
        if not self.dep_manager.is_available('prometheus'):
            result.warnings.append("Prometheus not available for monitoring setup")
            return
        
        try:
            # Create basic monitoring configuration
            monitoring_config = {
                'prometheus': {
                    'enabled': True,
                    'port': config.monitoring_config.get('port', 9090) if config.monitoring_config else 9090,
                    'metrics': [
                        'fava_pqc_key_operations_total',
                        'fava_pqc_key_rotation_duration_seconds',
                        'fava_pqc_vault_connection_status'
                    ]
                }
            }
            
            with open('monitoring-config.json', 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            result.recommendations.append("Monitoring configuration created: monitoring-config.json")
            
        except Exception as e:
            result.warnings.append(f"Failed to setup monitoring: {e}")
    
    def _setup_audit_logging(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Setup audit logging configuration."""
        try:
            audit_config = {
                'audit_logging': {
                    'enabled': True,
                    'destinations': ['file', 'syslog'],
                    'log_level': 'INFO',
                    'retention_days': 2555,  # 7 years
                    'log_file': 'fava-pqc-audit.log',
                    'include_events': [
                        'key_generation',
                        'key_rotation',
                        'key_access',
                        'authentication',
                        'configuration_change'
                    ]
                }
            }
            
            with open('audit-config.json', 'w') as f:
                json.dump(audit_config, f, indent=2)
            
            result.recommendations.append("Audit logging configuration created: audit-config.json")
            
        except Exception as e:
            result.warnings.append(f"Failed to setup audit logging: {e}")
    
    def _platform_specific_deployment(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Handle platform-specific deployment tasks."""
        platform_info = result.platform_info
        
        try:
            if platform_info.system == 'Linux':
                self._linux_specific_deployment(config, result)
            elif platform_info.system == 'Windows':
                self._windows_specific_deployment(config, result)
            elif platform_info.system == 'Darwin':
                self._macos_specific_deployment(config, result)
            
        except Exception as e:
            result.warnings.append(f"Platform-specific deployment issues: {e}")
    
    def _linux_specific_deployment(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Linux-specific deployment tasks."""
        if config.systemd_service and config.target_environment == 'production':
            # Create systemd service file template
            service_content = f"""[Unit]
Description=Fava PQC Enterprise Service
After=network.target

[Service]
Type=simple
User=fava-pqc
Group=fava-pqc
WorkingDirectory=/opt/fava-pqc
Environment=FAVA_PQC_ENV={config.target_environment}
ExecStart={sys.executable} -m fava
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            with open('fava-pqc.service', 'w') as f:
                f.write(service_content)
            
            result.recommendations.append(
                "Systemd service file created: fava-pqc.service. "
                "Copy to /etc/systemd/system/ and run 'systemctl enable fava-pqc'"
            )
    
    def _windows_specific_deployment(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """Windows-specific deployment tasks."""
        if config.windows_service and config.target_environment == 'production':
            result.recommendations.append(
                "For Windows service installation, consider using NSSM or similar tool"
            )
    
    def _macos_specific_deployment(self, config: DeploymentConfig, result: DeploymentResult) -> None:
        """macOS-specific deployment tasks."""
        if config.target_environment == 'production':
            result.recommendations.append(
                "For macOS production deployment, consider using launchd for service management"
            )


# Convenience functions
def create_enterprise_deployment(target_environment: str = 'production',
                               install_deps: bool = True,
                               enable_monitoring: bool = True) -> DeploymentResult:
    """Create enterprise deployment with default settings."""
    config = DeploymentConfig(
        target_environment=target_environment,
        install_optional_deps=install_deps,
        enable_monitoring=enable_monitoring,
        enable_audit_logging=target_environment == 'production'
    )
    
    deployment = AutomatedDeployment()
    return deployment.deploy(config)


def validate_platform_compatibility() -> Tuple[bool, List[str]]:
    """Quick platform compatibility check."""
    return PlatformChecker.check_platform_compatibility()