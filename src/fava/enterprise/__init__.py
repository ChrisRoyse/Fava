"""
Enterprise integration module for Fava PQC.

This module provides enterprise-ready features including:
- Optional dependency management with graceful fallbacks
- Enterprise authentication systems
- Monitoring and observability
- Hardware Security Module (HSM) integration
- HashiCorp Vault integration
- Compliance and audit capabilities
"""

from .dependency_manager import DependencyManager, enterprise_feature
from .monitoring import MetricsCollector, AuditLogger, get_metrics_collector, get_audit_logger
from .deployment import DeploymentValidator, PlatformChecker, AutomatedDeployment, DeploymentConfig
from .compliance import ComplianceReporter, AuditTrailGenerator, ComplianceAssessor, ComplianceEvidenceCollector, run_comprehensive_compliance_assessment
from .integration_testing import EnterpriseIntegrationTestRunner, EnterpriseTestSuite, run_enterprise_integration_tests

__all__ = [
    'DependencyManager',
    'enterprise_feature',
    'MetricsCollector',
    'AuditLogger',
    'get_metrics_collector',
    'get_audit_logger',
    'DeploymentValidator',
    'PlatformChecker',
    'AutomatedDeployment',
    'DeploymentConfig',
    'ComplianceReporter',
    'AuditTrailGenerator',
    'ComplianceAssessor',
    'ComplianceEvidenceCollector',
    'run_comprehensive_compliance_assessment',
    'EnterpriseIntegrationTestRunner',
    'EnterpriseTestSuite',
    'run_enterprise_integration_tests',
]

__version__ = '1.0.0'