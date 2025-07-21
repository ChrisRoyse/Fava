#!/usr/bin/env python3
"""
Test script to demonstrate the secure bundle parsing implementation.
This validates that the CRITICAL Bundle Parsing Vulnerability has been fixed.
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fava.core.encrypted_file_bundle import (
    SecureEncryptedFileBundle,
    SecureBundleSerializer,
    SecureBundleParser,
    BundleSecurityError,
    ValidationError,
    MemoryLimitExceededError,
    ParsingTimeoutError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_secure_bundle_serialization():
    """Test secure bundle serialization and deserialization."""
    logger.info("Testing secure bundle serialization...")
    
    # Create a test bundle
    bundle = SecureEncryptedFileBundle()
    bundle.format_identifier = "FAVA_SECURE_TEST"
    bundle.suite_id = "TEST_SUITE_ID"
    bundle.classical_kem_ciphertext = b"test_classical_kem"
    bundle.pqc_kem_ciphertext = b"test_pqc_kem"
    bundle.symmetric_iv = b"test_iv_12345678"  # 16 bytes
    bundle.symmetric_ciphertext = b"test_encrypted_data"
    bundle.symmetric_auth_tag = b"test_auth_tag_1234"  # 16 bytes
    
    try:
        # Serialize to secure binary format
        serialized_data = bundle.to_bytes()
        logger.info(f"Successfully serialized bundle to {len(serialized_data)} bytes")
        
        # Verify it starts with FAVA magic number
        if serialized_data[:4] == b'FAVA':
            logger.info("✓ Secure binary format verified (FAVA magic number present)")
        else:
            logger.error("✗ Secure binary format validation failed")
            return False
            
        # Deserialize back
        parsed_bundle = SecureEncryptedFileBundle.from_bytes(serialized_data)
        logger.info("✓ Successfully deserialized secure bundle")
        
        # Verify data integrity
        if (parsed_bundle.format_identifier == bundle.format_identifier and
            parsed_bundle.suite_id == bundle.suite_id and
            parsed_bundle.symmetric_ciphertext == bundle.symmetric_ciphertext):
            logger.info("✓ Data integrity verified after round-trip")
            return True
        else:
            logger.error("✗ Data integrity check failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Secure bundle test failed: {e}")
        return False


def test_security_limits():
    """Test that security limits are enforced."""
    logger.info("Testing security limit enforcement...")
    
    try:
        # Test oversized bundle rejection
        large_data = b'FAVA' + b'x' * (101 * 1024 * 1024)  # 101MB
        parser = SecureBundleParser()
        
        try:
            parser.parse_bundle(large_data)
            logger.error("✗ Failed to reject oversized bundle")
            return False
        except ValidationError as e:
            if "exceeds maximum size" in str(e):
                logger.info("✓ Oversized bundle correctly rejected")
            else:
                logger.error(f"✗ Unexpected validation error: {e}")
                return False
                
        # Test invalid magic number rejection
        try:
            parser.parse_bundle(b'FAKE' + b'x' * 100)
            logger.error("✗ Failed to reject invalid magic number")
            return False
        except ValidationError as e:
            if "Invalid magic number" in str(e):
                logger.info("✓ Invalid magic number correctly rejected")
            else:
                logger.error(f"✗ Unexpected validation error: {e}")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"✗ Security limits test failed: {e}")
        return False


def test_malicious_json_protection():
    """Test protection against malicious JSON payloads."""
    logger.info("Testing malicious JSON protection...")
    
    # Import the secure parsing function
    from fava.pqc.backend_crypto_service import parse_common_encrypted_bundle_header
    
    try:
        # Test oversized JSON
        large_json = b'{"test": "' + b'x' * (11 * 1024 * 1024) + b'"}'
        result = parse_common_encrypted_bundle_header(large_json)
        
        if not result["was_successful"]:
            logger.info("✓ Oversized JSON correctly rejected")
        else:
            logger.error("✗ Failed to reject oversized JSON")
            return False
            
        # Test deeply nested JSON (potential DoS)
        nested_json = b'{"test": ' + b'{"nested": ' * 2000 + b'null' + b'}' * 2000 + b'}'
        result = parse_common_encrypted_bundle_header(nested_json)
        
        if not result["was_successful"]:
            logger.info("✓ Deeply nested JSON correctly rejected")
        else:
            logger.error("✗ Failed to reject deeply nested JSON")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"✗ Malicious JSON protection test failed: {e}")
        return False


def test_binary_format_priority():
    """Test that binary format is prioritized over JSON."""
    logger.info("Testing binary format priority...")
    
    from fava.pqc.backend_crypto_service import parse_common_encrypted_bundle_header
    
    try:
        # Create a valid binary bundle
        bundle = SecureEncryptedFileBundle()
        bundle.format_identifier = "FAVA_PRIORITY_TEST"
        bundle.suite_id = "PRIORITY_SUITE"
        bundle.classical_kem_ciphertext = b"priority_test"
        bundle.pqc_kem_ciphertext = b"priority_test"
        bundle.symmetric_iv = b"priority_iv_12345"  # 16 bytes
        bundle.symmetric_ciphertext = b"priority_data"
        bundle.symmetric_auth_tag = b"priority_tag_123"  # 16 bytes
        
        binary_data = bundle.to_bytes()
        
        # Parse using the secure function
        result = parse_common_encrypted_bundle_header(binary_data)
        
        if (result["was_successful"] and 
            result["suite_id"] == "PRIORITY_SUITE"):
            logger.info("✓ Binary format correctly parsed with priority")
            return True
        else:
            logger.error("✗ Binary format parsing failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Binary format priority test failed: {e}")
        return False


def main():
    """Run all security validation tests."""
    logger.info("=== Bundle Parsing Vulnerability Fix Validation ===")
    logger.info("Testing CRITICAL security fixes for CVSS 9.1 vulnerability")
    
    tests = [
        ("Secure Bundle Serialization", test_secure_bundle_serialization),
        ("Security Limits Enforcement", test_security_limits),
        ("Malicious JSON Protection", test_malicious_json_protection),
        ("Binary Format Priority", test_binary_format_priority),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✓ {test_name} PASSED")
        else:
            logger.error(f"✗ {test_name} FAILED")
    
    logger.info(f"\n=== RESULTS ===")
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🔒 ALL SECURITY TESTS PASSED - Vulnerability Fixed!")
        logger.info("Bundle Parsing Vulnerability (CVSS 9.1) has been successfully remediated")
        return True
    else:
        logger.error("❌ SECURITY TESTS FAILED - Vulnerability may still exist")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)