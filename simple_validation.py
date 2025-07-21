#!/usr/bin/env python3
"""
Simple PQC Key Management Validation

Tests core key management functionality without full dependency chain.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test basic imports without full dependency chain."""
    print("=== Testing Basic Imports ===")
    
    try:
        # Test OQS import first
        import oqs
        print("PASS: OQS library available")
        
        # Test if Dilithium3 is available
        if oqs.is_sig_enabled("Dilithium3"):
            print("PASS: Dilithium3 algorithm available")
        else:
            print("FAIL: Dilithium3 algorithm not available")
            
    except ImportError as e:
        print(f"FAIL: OQS import failed: {e}")
        return False
    
    try:
        # Test direct key manager import
        from fava.pqc.key_manager import PQCKeyManager, KeyManagementError
        print("PASS: PQCKeyManager imported successfully")
    except ImportError as e:
        print(f"FAIL: PQCKeyManager import failed: {e}")
        return False
    
    try:
        # Test configuration helpers
        from fava.pqc.global_config_helpers import file_system, parser, validator
        print("PASS: Configuration helpers imported")
    except ImportError as e:
        print(f"FAIL: Configuration helpers import failed: {e}")
        return False
    
    try:
        # Test exceptions
        from fava.pqc.exceptions import ConfigurationError, KeyManagementError
        print("PASS: PQC exceptions imported")
    except ImportError as e:
        print(f"FAIL: PQC exceptions import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading."""
    print("\n=== Testing Configuration Loading ===")
    
    try:
        from fava.pqc.global_config_helpers import file_system, parser
        
        # Test config file reading
        config_path = "config/fava_crypto_settings.py"
        if Path(config_path).exists():
            content = file_system.read_file_content(config_path)
            print("PASS: Configuration file read successfully")
            
            # Test parsing
            config = parser.parse_python_like_structure(content)
            print("PASS: Configuration parsed successfully")
            
            # Check for hardcoded keys
            import re
            if "public_key_base64" in content:
                print("FAIL: Hardcoded public_key_base64 found in config - SECURITY ISSUE")
                return False
            
            # Look for long base64-like strings
            base64_pattern = r'[A-Za-z0-9+/]{100,}={0,2}'
            matches = re.findall(base64_pattern, content)
            if matches:
                print(f"FAIL: Potential hardcoded keys found: {len(matches)} base64 strings")
                return False
            else:
                print("PASS: No hardcoded keys detected")
                
            return True
        else:
            print(f"FAIL: Configuration file not found: {config_path}")
            return False
            
    except Exception as e:
        print(f"FAIL: Configuration loading failed: {e}")
        return False

def test_key_generation():
    """Test key generation in isolation."""
    print("\n=== Testing Key Generation ===")
    
    try:
        import oqs
        
        # Test direct OQS key generation
        with oqs.Signature("Dilithium3") as signer:
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            
            if public_key and private_key:
                print(f"PASS: Keys generated directly - pub: {len(public_key)} bytes, priv: {len(private_key)} bytes")
                
                # Test signing and verification
                test_message = b"Test message for validation"
                signature = signer.sign(test_message)
                is_valid = signer.verify(test_message, signature, public_key)
                
                if is_valid:
                    print("PASS: Key validation successful (sign/verify test)")
                    return True
                else:
                    print("FAIL: Key validation failed")
                    return False
            else:
                print("FAIL: Key generation returned empty keys")
                return False
                
    except Exception as e:
        print(f"FAIL: Key generation test failed: {e}")
        return False

def test_key_manager_basic():
    """Test basic key manager functionality."""
    print("\n=== Testing Key Manager ===")
    
    try:
        from fava.pqc.key_manager import PQCKeyManager
        
        # Create minimal config
        config = {
            "wasm_module_integrity": {
                "signature_algorithm": "Dilithium3",
                "key_source": "environment",
                "public_key_env_var": "TEST_PQC_PUBLIC_KEY",
                "private_key_env_var": "TEST_PQC_PRIVATE_KEY",
                "key_rotation_enabled": True,
                "key_rotation_interval_days": 90
            }
        }
        
        # Initialize key manager
        key_manager = PQCKeyManager(config)
        print("PASS: Key manager initialized")
        
        # Test key generation
        public_key, private_key = key_manager.generate_keypair()
        if public_key and private_key:
            print("PASS: Key manager generated keypair")
            
            # Test validation
            is_valid = key_manager._validate_keypair(public_key, private_key)
            if is_valid:
                print("PASS: Generated keypair is valid")
                return True
            else:
                print("FAIL: Generated keypair validation failed")
                return False
        else:
            print("FAIL: Key manager failed to generate keys")
            return False
            
    except Exception as e:
        print(f"FAIL: Key manager test failed: {e}")
        return False

def test_audit_logger():
    """Test audit logger functionality."""
    print("\n=== Testing Audit Logger ===")
    
    try:
        from fava.pqc.audit_logger import PQCAuditLogger, audit_key_generation
        
        # Create audit logger
        audit_logger = PQCAuditLogger()
        print("PASS: Audit logger created")
        
        # Test logging
        audit_key_generation("Dilithium3", "test", "test_hash")
        print("PASS: Audit logging successful")
        
        # Check if log file exists
        if Path(audit_logger.log_file).exists():
            print(f"PASS: Audit log file created: {audit_logger.log_file}")
            return True
        else:
            print("FAIL: Audit log file not created")
            return False
            
    except Exception as e:
        print(f"FAIL: Audit logger test failed: {e}")
        return False

def test_file_permissions():
    """Test file permission handling."""
    print("\n=== Testing File Permissions ===")
    
    try:
        import tempfile
        from fava.pqc.key_manager import PQCKeyManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "wasm_module_integrity": {
                    "signature_algorithm": "Dilithium3",
                    "key_source": "file",
                    "key_file_path": temp_dir,
                    "key_rotation_enabled": True,
                    "key_rotation_interval_days": 90
                }
            }
            
            key_manager = PQCKeyManager(config)
            public_key, private_key = key_manager.generate_keypair()
            key_manager.store_keypair(public_key, private_key)
            
            # Check file permissions
            private_file = Path(temp_dir) / "private_key.dilithium3"
            if private_file.exists():
                if os.name != 'nt':  # Unix-like systems
                    file_mode = private_file.stat().st_mode & 0o777
                    if file_mode == 0o600:
                        print("PASS: Private key file has correct permissions (600)")
                    else:
                        print(f"FAIL: Private key has wrong permissions: {oct(file_mode)}")
                        return False
                else:
                    print("PASS: File permissions check skipped on Windows")
                
                print("PASS: File-based key storage works")
                return True
            else:
                print("FAIL: Private key file not created")
                return False
                
    except Exception as e:
        print(f"FAIL: File permissions test failed: {e}")
        return False

def main():
    """Run simplified validation."""
    print("PQC Key Management Simple Validation")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_config_loading,
        test_key_generation,
        test_key_manager_basic,
        test_audit_logger,
        test_file_permissions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: Test {test.__name__} crashed: {e}")
    
    print(f"\n{'='*50}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("RESULT: All tests passed - Implementation looks good")
    elif passed >= total * 0.8:
        print("RESULT: Most tests passed - Minor issues detected")
    else:
        print("RESULT: Multiple tests failed - Major issues detected")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)