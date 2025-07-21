#!/usr/bin/env python3
"""
PQC Key Management Validation Script

This script validates the key management implementation completed by Agent I1,
identifying security issues, functionality problems, and implementation gaps.

Security Requirements Checked:
- No hardcoded cryptographic material
- Secure key generation and storage
- Proper file permissions
- Audit logging functionality
- Error handling and validation

Usage:
    python validate_key_management.py
"""

import base64
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import List, Dict, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test results storage
test_results = []
security_issues = []
functionality_issues = []
recommendations = []

def log_result(test_name: str, passed: bool, message: str, severity: str = "INFO"):
    """Log a test result."""
    result = {
        "test": test_name,
        "passed": passed,
        "message": message,
        "severity": severity
    }
    test_results.append(result)
    
    if not passed:
        if severity in ["CRITICAL", "HIGH"]:
            security_issues.append(result)
        else:
            functionality_issues.append(result)
    
    status = "PASS" if passed else "FAIL"
    print(f"{status}: {test_name} - {message}")

def check_imports():
    """Test that all required modules can be imported."""
    print("\n=== Testing Module Imports ===")
    
    required_modules = [
        "fava.pqc.key_manager",
        "fava.pqc.global_config", 
        "fava.pqc.audit_logger",
        "fava.pqc.configuration_validator",
        "fava.pqc.exceptions"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            log_result(f"Import {module}", True, "Module imported successfully")
        except ImportError as e:
            log_result(f"Import {module}", False, f"Import failed: {e}", "HIGH")
    
    # Test OQS import
    try:
        import oqs
        log_result("Import OQS", True, "liboqs-python available")
    except ImportError:
        log_result("Import OQS", False, "liboqs-python not available", "CRITICAL")

def check_hardcoded_keys():
    """Check for any remaining hardcoded cryptographic material."""
    print("\n=== Checking for Hardcoded Keys ===")
    
    # Check configuration file
    config_file = Path("config/fava_crypto_settings.py")
    if config_file.exists():
        content = config_file.read_text()
        
        # Look for base64-like strings (potential keys)
        import re
        base64_pattern = r'[A-Za-z0-9+/]{50,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        if matches:
            log_result("Hardcoded keys check", False, 
                      f"Potential hardcoded keys found in config: {len(matches)} matches", "CRITICAL")
        else:
            log_result("Hardcoded keys check", True, "No hardcoded keys found in config")
        
        # Check for deprecated public_key_base64 field
        if "public_key_base64" in content:
            log_result("Deprecated key field", False, 
                      "Deprecated 'public_key_base64' field found in config", "CRITICAL")
        else:
            log_result("Deprecated key field", True, "No deprecated key fields found")
    else:
        log_result("Config file check", False, "Configuration file not found", "HIGH")

def test_key_generation():
    """Test key generation functionality."""
    print("\n=== Testing Key Generation ===")
    
    try:
        from fava.pqc.key_manager import PQCKeyManager
        from fava.pqc.global_config import GlobalConfig
        
        # Load configuration
        config = GlobalConfig.get_crypto_settings()
        log_result("Load configuration", True, "Configuration loaded successfully")
        
        # Override to use environment for testing
        config['wasm_module_integrity']['key_source'] = 'environment'
        
        # Initialize key manager
        key_manager = PQCKeyManager(config)
        log_result("Key manager init", True, "Key manager initialized")
        
        # Test key generation
        public_key, private_key = key_manager.generate_keypair()
        
        if public_key and private_key:
            log_result("Key generation", True, 
                      f"Keys generated: pub={len(public_key)} bytes, priv={len(private_key)} bytes")
        else:
            log_result("Key generation", False, "Key generation returned empty keys", "HIGH")
        
        # Test key validation
        is_valid = key_manager._validate_keypair(public_key, private_key)
        log_result("Key validation", is_valid, 
                  "Generated keys are valid" if is_valid else "Generated keys failed validation")
        
        return public_key, private_key
        
    except Exception as e:
        log_result("Key generation", False, f"Key generation failed: {e}", "HIGH")
        return None, None

def test_key_storage_and_loading():
    """Test key storage and loading functionality."""
    print("\n=== Testing Key Storage and Loading ===")
    
    try:
        from fava.pqc.key_manager import PQCKeyManager
        from fava.pqc.global_config import GlobalConfig
        
        # Create temporary directory for file-based keys
        with tempfile.TemporaryDirectory() as temp_dir:
            config = GlobalConfig.get_crypto_settings()
            config['wasm_module_integrity']['key_source'] = 'file'
            config['wasm_module_integrity']['key_file_path'] = temp_dir
            
            key_manager = PQCKeyManager(config)
            
            # Generate keys
            public_key, private_key = key_manager.generate_keypair()
            
            # Store keys
            key_manager.store_keypair(public_key, private_key)
            log_result("Key storage", True, "Keys stored successfully")
            
            # Load keys
            loaded_public = key_manager.load_public_key()
            loaded_private = key_manager.load_private_key()
            
            # Verify loaded keys match original
            if loaded_public == public_key and loaded_private == private_key:
                log_result("Key loading", True, "Loaded keys match original keys")
            else:
                log_result("Key loading", False, "Loaded keys don't match original", "HIGH")
            
            # Check file permissions
            algorithm = config['wasm_module_integrity']['signature_algorithm']
            private_file = Path(temp_dir) / f"private_key.{algorithm.lower()}"
            
            if private_file.exists():
                if os.name != 'nt':  # Unix-like systems
                    file_mode = private_file.stat().st_mode & 0o777
                    if file_mode == 0o600:
                        log_result("File permissions", True, "Private key has correct permissions (600)")
                    else:
                        log_result("File permissions", False, 
                                  f"Private key has wrong permissions: {oct(file_mode)}", "MEDIUM")
                else:
                    log_result("File permissions", True, "File permissions check skipped on Windows")
            
    except Exception as e:
        log_result("Key storage/loading", False, f"Storage/loading test failed: {e}", "HIGH")

def test_environment_variables():
    """Test environment variable key storage."""
    print("\n=== Testing Environment Variable Storage ===")
    
    try:
        from fava.pqc.key_manager import PQCKeyManager
        from fava.pqc.global_config import GlobalConfig
        
        config = GlobalConfig.get_crypto_settings()
        config['wasm_module_integrity']['key_source'] = 'environment'
        
        key_manager = PQCKeyManager(config)
        
        # Generate and store keys
        public_key, private_key = key_manager.generate_keypair()
        key_manager.store_keypair(public_key, private_key)
        
        # Check that environment variables are set
        wasm_config = config['wasm_module_integrity']
        public_env_var = wasm_config.get('public_key_env_var', 'FAVA_PQC_PUBLIC_KEY')
        private_env_var = wasm_config.get('private_key_env_var', 'FAVA_PQC_PRIVATE_KEY')
        
        if os.environ.get(public_env_var) and os.environ.get(private_env_var):
            log_result("Environment variables", True, "Keys stored in environment variables")
        else:
            log_result("Environment variables", False, "Environment variables not set", "MEDIUM")
            
        # Test loading from environment
        loaded_public = key_manager.load_public_key()
        loaded_private = key_manager.load_private_key()
        
        if loaded_public and loaded_private:
            log_result("Environment loading", True, "Keys loaded from environment")
        else:
            log_result("Environment loading", False, "Failed to load keys from environment", "HIGH")
            
    except Exception as e:
        log_result("Environment variables", False, f"Environment test failed: {e}", "HIGH")

def test_audit_logging():
    """Test audit logging functionality."""
    print("\n=== Testing Audit Logging ===")
    
    try:
        from fava.pqc.audit_logger import get_audit_logger, audit_key_generation, audit_security_event
        
        # Get audit logger
        audit_logger = get_audit_logger()
        log_result("Audit logger init", True, "Audit logger initialized")
        
        # Test audit functions
        audit_key_generation("Dilithium3", "test", "test_hash")
        log_result("Audit key generation", True, "Key generation audit logged")
        
        audit_security_event("test_event", {"test": "data"}, "INFO")
        log_result("Audit security event", True, "Security event audit logged")
        
        # Check if log file was created
        log_file = audit_logger.log_file
        if Path(log_file).exists():
            log_result("Audit log file", True, f"Audit log file created: {log_file}")
        else:
            log_result("Audit log file", False, "Audit log file not created", "MEDIUM")
            
    except Exception as e:
        log_result("Audit logging", False, f"Audit logging test failed: {e}", "MEDIUM")

def test_configuration_validation():
    """Test configuration validation."""
    print("\n=== Testing Configuration Validation ===")
    
    try:
        from fava.pqc.configuration_validator import validate_full_pqc_configuration, get_configuration_recommendations
        from fava.pqc.global_config import GlobalConfig
        
        config = GlobalConfig.get_crypto_settings()
        
        # Test validation
        errors = validate_full_pqc_configuration(config)
        if not errors:
            log_result("Config validation", True, "Configuration validation passed")
        else:
            log_result("Config validation", False, f"Validation errors: {errors}", "MEDIUM")
        
        # Test recommendations
        recommendations = get_configuration_recommendations(config)
        log_result("Config recommendations", True, f"Got {len(recommendations)} recommendations")
        
    except Exception as e:
        log_result("Configuration validation", False, f"Config validation test failed: {e}", "MEDIUM")

def test_cli_integration():
    """Test CLI command integration."""
    print("\n=== Testing CLI Integration ===")
    
    try:
        from fava.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test pqc command group
        result = runner.invoke(cli, ['pqc', '--help'])
        if result.exit_code == 0:
            log_result("CLI pqc group", True, "PQC command group accessible")
        else:
            log_result("CLI pqc group", False, f"PQC command failed: {result.output}", "MEDIUM")
        
        # Test info command
        result = runner.invoke(cli, ['pqc', 'info'])
        if result.exit_code == 0 or "PQC Key Information" in result.output:
            log_result("CLI info command", True, "PQC info command works")
        else:
            log_result("CLI info command", False, f"Info command failed: {result.output}", "LOW")
            
    except Exception as e:
        log_result("CLI integration", False, f"CLI test failed: {e}", "LOW")

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from fava.pqc.key_manager import PQCKeyManager, KeyNotFoundException
        from fava.pqc.global_config import GlobalConfig
        
        config = GlobalConfig.get_crypto_settings()
        
        # Test with invalid key source
        invalid_config = config.copy()
        invalid_config['wasm_module_integrity']['key_source'] = 'invalid_source'
        
        try:
            key_manager = PQCKeyManager(invalid_config)
            key_manager.load_public_key()
            log_result("Invalid key source", False, "Should have failed with invalid key source", "MEDIUM")
        except Exception:
            log_result("Invalid key source", True, "Correctly handled invalid key source")
        
        # Test with missing environment variables
        config['wasm_module_integrity']['key_source'] = 'environment'
        config['wasm_module_integrity']['public_key_env_var'] = 'NONEXISTENT_VAR'
        
        try:
            key_manager = PQCKeyManager(config)
            key_manager.load_public_key()
            log_result("Missing env var", False, "Should have failed with missing env var", "MEDIUM")
        except KeyNotFoundException:
            log_result("Missing env var", True, "Correctly handled missing environment variable")
        except Exception as e:
            log_result("Missing env var", True, f"Handled missing env var: {type(e).__name__}")
            
    except Exception as e:
        log_result("Error handling", False, f"Error handling test failed: {e}", "MEDIUM")

def generate_report():
    """Generate the final validation report."""
    print("\n" + "=" * 80)
    print("                    PQC KEY MANAGEMENT VALIDATION REPORT")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"\nSUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if security_issues:
        print(f"\nSECURITY ISSUES ({len(security_issues)}):")
        for issue in security_issues:
            print(f"  X [{issue['severity']}] {issue['test']}: {issue['message']}")
    
    if functionality_issues:
        print(f"\nFUNCTIONALITY ISSUES ({len(functionality_issues)}):")
        for issue in functionality_issues:
            print(f"  X [{issue['severity']}] {issue['test']}: {issue['message']}")
    
    # Categorize by severity
    critical_issues = [r for r in test_results if not r['passed'] and r['severity'] == 'CRITICAL']
    high_issues = [r for r in test_results if not r['passed'] and r['severity'] == 'HIGH']
    
    print(f"\nISSUE BREAKDOWN:")
    print(f"  Critical: {len(critical_issues)}")
    print(f"  High: {len(high_issues)}")
    print(f"  Medium: {len([r for r in test_results if not r['passed'] and r['severity'] == 'MEDIUM'])}")
    print(f"  Low: {len([r for r in test_results if not r['passed'] and r['severity'] == 'LOW'])}")
    
    # Production readiness assessment
    print(f"\nPRODUCTION READINESS ASSESSMENT:")
    if critical_issues:
        print("  X NOT READY FOR PRODUCTION - Critical security issues found")
    elif high_issues:
        print("  ! NOT RECOMMENDED FOR PRODUCTION - High priority issues found")
    elif failed_tests == 0:
        print("  + READY FOR PRODUCTION - All tests passed")
    else:
        print("  ! PRODUCTION READY WITH CAUTION - Minor issues found")
    
    # Recommendations
    print(f"\nVALIDATION RECOMMENDATIONS:")
    if critical_issues or high_issues:
        print("  1. Fix all critical and high priority security issues")
        print("  2. Re-run validation after fixes")
        print("  3. Perform additional security testing")
    
    print("  4. Test in staging environment before production deployment")
    print("  5. Set up monitoring for key management operations")
    print("  6. Establish key rotation procedures")
    print("  7. Create backup and recovery plans for keys")
    
    # Save detailed report
    report_data = {
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100
        },
        "security_issues": security_issues,
        "functionality_issues": functionality_issues,
        "all_results": test_results
    }
    
    report_file = "pqc_key_management_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")

def main():
    """Main validation function."""
    print("PQC Key Management Implementation Validation")
    print("Agent V1 - Security and Functionality Validation")
    print("=" * 80)
    
    try:
        # Run all validation tests
        check_imports()
        check_hardcoded_keys()
        test_key_generation()
        test_key_storage_and_loading()
        test_environment_variables()
        test_audit_logging()
        test_configuration_validation()
        test_cli_integration()
        test_error_handling()
        
        # Generate comprehensive report
        generate_report()
        
    except Exception as e:
        print(f"\nVALIDATION FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()