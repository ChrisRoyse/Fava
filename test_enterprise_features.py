#!/usr/bin/env python3
"""
Simple test script for enterprise features validation.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from fava.enterprise import (
        DependencyManager,
        get_metrics_collector,
        get_audit_logger,
        DeploymentValidator,
        PlatformChecker,
        ComplianceAssessor
    )
    
    print("SUCCESS: Enterprise modules imported successfully")
    
    # Test dependency manager
    print("\n--- Testing Dependency Manager ---")
    dep_manager = DependencyManager()
    readiness = dep_manager.get_enterprise_readiness()
    print(f"Enterprise readiness score: {readiness['score']}%")
    print(f"Readiness level: {readiness['level']}")
    print(f"Available dependencies: {readiness['available_dependencies']}/{readiness['total_dependencies']}")
    
    # Test platform checker
    print("\n--- Testing Platform Checker ---")
    platform_checker = PlatformChecker()
    platform_info = platform_checker.get_platform_info()
    compatible, issues = platform_checker.check_platform_compatibility()
    print(f"Platform: {platform_info.system} {platform_info.release}")
    print(f"Python: {platform_info.python_version}")
    print(f"Compatible: {compatible}")
    if issues:
        print(f"Issues: {issues}")
    
    # Test metrics collector
    print("\n--- Testing Metrics Collector ---")
    metrics = get_metrics_collector()
    metrics_summary = metrics.get_metrics_summary()
    print(f"Prometheus enabled: {metrics_summary['prometheus_enabled']}")
    print(f"Prometheus available: {metrics_summary['prometheus_available']}")
    print(f"Fallback mode: {metrics_summary['fallback_mode']}")
    print(f"Metrics count: {metrics_summary['metrics_count']}")
    
    # Test audit logger
    print("\n--- Testing Audit Logger ---")
    audit_logger = get_audit_logger({'enabled': True, 'destinations': ['file']})
    audit_logger.log_event('test', 'enterprise_test', 'validation', 'success')
    print("Audit event logged successfully")
    
    # Test compliance assessor
    print("\n--- Testing Compliance Assessor ---")
    assessor = ComplianceAssessor()
    nist_assessment = assessor.assess_framework('NIST-SP-800-208')
    print(f"NIST compliance score: {nist_assessment.overall_compliance_score}%")
    print(f"Requirements assessed: {nist_assessment.requirements_total}")
    
    # Overall success
    print("\n" + "="*50)
    print("ENTERPRISE FEATURES TEST SUMMARY")
    print("="*50)
    print(f"Enterprise Readiness: {readiness['score']}% ({readiness['level']})")
    print(f"Platform Compatible: {compatible}")
    print(f"Monitoring Available: {not metrics_summary['fallback_mode']}")
    print(f"Compliance Score: {nist_assessment.overall_compliance_score}%")
    
    if readiness['score'] >= 70:
        print("\nSTATUS: ENTERPRISE FEATURES VALIDATED SUCCESSFULLY")
        exit_code = 0
    else:
        print("\nSTATUS: ENTERPRISE FEATURES NEED IMPROVEMENT")
        exit_code = 1
    
    audit_logger.shutdown()
    sys.exit(exit_code)
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"TEST ERROR: {e}")
    sys.exit(1)