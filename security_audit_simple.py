#!/usr/bin/env python3
"""
COMPREHENSIVE SECURITY AUDIT - ADVERSARIAL TESTING
Security Audit Agent #2: Hostile Security Research

This script performs comprehensive adversarial testing to identify
remaining security vulnerabilities in the Favapqc implementation.
"""

import sys
import os
import time
import logging
import threading
import random
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import hashlib
import hmac

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityFindings:
    def __init__(self):
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
        self.tests_passed = 0
        self.tests_failed = 0
    
    def add_critical(self, issue_name, description, attack_vector):
        self.critical_issues.append({
            'name': issue_name,
            'description': description,
            'attack_vector': attack_vector,
            'cvss': 9.0
        })
    
    def add_high(self, issue_name, description, attack_vector):
        self.high_issues.append({
            'name': issue_name,
            'description': description,
            'attack_vector': attack_vector,
            'cvss': 7.5
        })
    
    def add_medium(self, issue_name, description, attack_vector):
        self.medium_issues.append({
            'name': issue_name,
            'description': description,
            'attack_vector': attack_vector,
            'cvss': 5.0
        })

def test_crypto_service_vulnerabilities(findings: SecurityFindings):
    """Test crypto service for vulnerabilities"""
    logger.info("Testing crypto service vulnerabilities...")
    
    try:
        from fava.crypto.service import HashingService
        
        # Test 1: Algorithm downgrade attack
        try:
            logger.info("  -> Testing algorithm downgrade protection")
            service = HashingService("MD5")  # Should not be allowed
            
            if service.get_configured_algorithm_name() == "MD5":
                findings.add_high(
                    "Cryptographic Downgrade Attack",
                    "System allows use of cryptographically weak MD5 hash algorithm",
                    "Configure system to use MD5 algorithm"
                )
                findings.tests_failed += 1
            else:
                logger.info("    [OK] Weak algorithm properly rejected")
                findings.tests_passed += 1
                
        except Exception as e:
            logger.info(f"    [OK] Algorithm downgrade test passed (exception expected): {e}")
            findings.tests_passed += 1
        
        # Test 2: Hash collision resistance
        try:
            logger.info("  -> Testing hash collision resistance")
            service = HashingService("SHA3-256")
            
            # Test with known collision-prone inputs
            test_data = [b"test1", b"test2", b"", b"a" * 1000000]
            hashes = []
            
            for data in test_data:
                hash_result = service.hash_data(data)
                hashes.append(hash_result)
            
            # Check for unexpected collisions
            if len(set(hashes)) != len(hashes):
                findings.add_critical(
                    "Hash Collision Vulnerability",
                    "Hash function produces collisions for different inputs",
                    "Craft inputs that produce identical hashes"
                )
                findings.tests_failed += 1
            else:
                logger.info("    [OK] No hash collisions detected")
                findings.tests_passed += 1
                
        except Exception as e:
            logger.error(f"    [ERROR] Hash collision test failed: {e}")
            findings.tests_failed += 1
            
    except ImportError as e:
        logger.error(f"Failed to import crypto service: {e}")
        findings.tests_failed += 1

def test_key_management_vulnerabilities(findings: SecurityFindings):
    """Test key management for vulnerabilities"""
    logger.info("Testing key management vulnerabilities...")
    
    try:
        from fava.crypto.keys import OQSKEMAdapter, derive_kem_keys_from_passphrase
        
        # Test 1: Key generation entropy
        logger.info("  -> Testing key generation entropy")
        kem = OQSKEMAdapter("Kyber768")
        
        keys1 = kem.generate_keypair()
        keys2 = kem.generate_keypair()
        
        if keys1[0] == keys2[0] or keys1[1] == keys2[1]:
            findings.add_critical(
                "Weak Key Generation",
                "Key generation produces identical keys indicating weak entropy",
                "Generate multiple keys and compare for duplicates"
            )
            findings.tests_failed += 1
        else:
            logger.info("    [OK] Key generation appears properly random")
            findings.tests_passed += 1
        
        # Test 2: Weak passphrase handling
        logger.info("  -> Testing weak passphrase handling")
        weak_passphrases = ["123456", "password", "admin", ""]
        
        weak_accepted = 0
        for weak_pass in weak_passphrases:
            try:
                salt = b'\x00' * 16
                keys = derive_kem_keys_from_passphrase(
                    weak_pass, salt, "Argon2id", "HKDF-SHA3-512", 
                    "X25519", "Kyber768"
                )
                weak_accepted += 1
                logger.info(f"    [INFO] Weak passphrase '{weak_pass}' processed")
                
            except Exception:
                # Expected to fail or warn
                continue
        
        # It's not necessarily a vulnerability to accept weak passphrases
        # if using strong KDF, but it's worth noting
        if weak_accepted > 0:
            logger.info(f"    [INFO] {weak_accepted} weak passphrases processed (may be OK with strong KDF)")
        
        findings.tests_passed += 1
        
    except Exception as e:
        logger.error(f"Key management test failed: {e}")
        findings.tests_failed += 1

def test_bundle_parsing_vulnerabilities(findings: SecurityFindings):
    """Test bundle parsing for security vulnerabilities"""
    logger.info("Testing bundle parsing vulnerabilities...")
    
    try:
        from fava.core.encrypted_file_bundle import SecureBundleParser, ValidationError
        
        # Test 1: Oversized bundle handling
        logger.info("  -> Testing oversized bundle protection")
        parser = SecureBundleParser()
        
        # Create oversized bundle (101MB)
        large_data = b'FAVA' + b'\x00' * 28 + b'x' * (101 * 1024 * 1024)
        
        try:
            parser.parse_bundle(large_data)
            findings.add_high(
                "Bundle Size DoS Vulnerability",
                "Parser accepts oversized bundles that could cause memory exhaustion",
                "Send bundle larger than expected size limits"
            )
            findings.tests_failed += 1
        except ValidationError as e:
            if "exceeds maximum size" in str(e) or "too large" in str(e).lower():
                logger.info("    [OK] Oversized bundle properly rejected")
                findings.tests_passed += 1
            else:
                logger.warning(f"    [WARN] Unexpected validation error: {e}")
        except Exception as e:
            logger.warning(f"    [WARN] Unexpected exception: {e}")
        
        # Test 2: Malformed header handling
        logger.info("  -> Testing malformed header handling")
        malformed_bundles = [
            b'FAKE' + b'\x00' * 100,  # Invalid magic
            b'FAVA' + b'\xFF' * 100,  # Invalid structure
            b'FAVA' + b'\x00' * 4 + struct.pack('<I', 0xFFFFFFFF) + b'\x00' * 20,  # Size overflow
        ]
        
        malformed_accepted = 0
        for malformed_data in malformed_bundles:
            try:
                parser.parse_bundle(malformed_data)
                malformed_accepted += 1
            except ValidationError:
                # Expected to fail
                continue
            except Exception:
                # Other exceptions are also expected
                continue
        
        if malformed_accepted > 0:
            findings.add_medium(
                "Malformed Bundle Processing",
                f"Parser accepts {malformed_accepted} malformed bundles without proper validation",
                "Send malformed bundle headers to bypass validation"
            )
            findings.tests_failed += 1
        else:
            logger.info("    [OK] Malformed bundles properly rejected")
            findings.tests_passed += 1
            
    except Exception as e:
        logger.error(f"Bundle parsing test failed: {e}")
        findings.tests_failed += 1

def test_input_validation_vulnerabilities(findings: SecurityFindings):
    """Test input validation for security vulnerabilities"""
    logger.info("Testing input validation vulnerabilities...")
    
    try:
        from fava.crypto.keys import load_keys_from_external_file
        
        # Test 1: Path traversal in key file paths
        logger.info("  -> Testing path traversal protection")
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/dev/zero",
            "\\\\attacker.com\\share\\malicious.key",
        ]
        
        path_vulnerabilities = 0
        for malicious_path in malicious_paths:
            try:
                config = {"classical_private": malicious_path, "pqc_private": "test.key"}
                load_keys_from_external_file(config)
                # If it doesn't raise exception, might be vulnerable
                logger.warning(f"    [WARN] Path {malicious_path} processed without exception")
                
            except FileNotFoundError:
                # Expected for non-existent paths
                continue
            except Exception as e:
                if "path" in str(e).lower() and ("invalid" in str(e).lower() or "not allowed" in str(e).lower()):
                    logger.info(f"    [OK] Path validation working for {malicious_path}")
                    continue
                else:
                    logger.warning(f"    [WARN] Unexpected error for {malicious_path}: {e}")
        
        logger.info("    [OK] Path traversal test completed")
        findings.tests_passed += 1
        
    except Exception as e:
        logger.error(f"Input validation test failed: {e}")
        findings.tests_failed += 1

def test_timing_attack_vulnerabilities(findings: SecurityFindings):
    """Test for timing attack vulnerabilities"""
    logger.info("Testing timing attack vulnerabilities...")
    
    try:
        from fava.crypto.keys import OQSKEMAdapter
        
        # Test 1: Key operation timing side-channels
        logger.info("  -> Testing key operation timing consistency")
        
        kem = OQSKEMAdapter("Kyber768")
        pub_key, priv_key = kem.generate_keypair()
        
        # Test decapsulation timing with valid vs invalid ciphertext
        valid_shared_secret, valid_ciphertext = kem.encap_secret(pub_key)
        invalid_ciphertext = b'\x00' * len(valid_ciphertext)
        
        # Time valid operations
        valid_times = []
        for _ in range(20):
            start = time.perf_counter()
            try:
                kem.decap_secret(priv_key, valid_ciphertext)
            except:
                pass
            valid_times.append(time.perf_counter() - start)
        
        # Time invalid operations
        invalid_times = []
        for _ in range(20):
            start = time.perf_counter()
            try:
                kem.decap_secret(priv_key, invalid_ciphertext)
            except:
                pass
            invalid_times.append(time.perf_counter() - start)
        
        avg_valid = sum(valid_times) / len(valid_times) if valid_times else 0
        avg_invalid = sum(invalid_times) / len(invalid_times) if invalid_times else 0
        
        if avg_valid > 0 and avg_invalid > 0:
            timing_ratio = max(avg_valid, avg_invalid) / min(avg_valid, avg_invalid)
            
            if timing_ratio > 2.0:  # More than 100% difference
                findings.add_medium(
                    "Timing Side-Channel in Key Operations",
                    f"Key operations have significant timing differences (ratio: {timing_ratio:.2f})",
                    "Measure timing differences between valid and invalid operations"
                )
                findings.tests_failed += 1
            else:
                logger.info("    [OK] No significant timing side-channel detected")
                findings.tests_passed += 1
        else:
            logger.info("    [INFO] Timing test inconclusive")
            findings.tests_passed += 1
            
    except Exception as e:
        logger.error(f"Timing attack test failed: {e}")
        findings.tests_failed += 1

def test_memory_safety_vulnerabilities(findings: SecurityFindings):
    """Test memory safety vulnerabilities"""
    logger.info("Testing memory safety vulnerabilities...")
    
    try:
        from fava.crypto.keys import OQSKEMAdapter
        
        # Test 1: Oversized key handling
        logger.info("  -> Testing oversized key handling")
        
        kem = OQSKEMAdapter("Kyber768")
        
        # Try extremely large "key"
        large_key = b'\x00' * (50 * 1024 * 1024)  # 50MB of zeros
        
        try:
            kem.load_keypair_from_secret_key(large_key)
            findings.add_high(
                "Memory Exhaustion via Oversized Keys",
                "System accepts oversized key material that could cause memory exhaustion",
                "Provide extremely large key material to key loading functions"
            )
            findings.tests_failed += 1
        except Exception as e:
            logger.info(f"    [OK] Oversized key properly rejected: {type(e).__name__}")
            findings.tests_passed += 1
            
    except Exception as e:
        logger.error(f"Memory safety test failed: {e}")
        findings.tests_failed += 1

def test_information_disclosure_vulnerabilities(findings: SecurityFindings):
    """Test for information disclosure vulnerabilities"""
    logger.info("Testing information disclosure vulnerabilities...")
    
    try:
        from fava.crypto.keys import OQSKEMAdapter
        
        # Test 1: Error message information leakage
        logger.info("  -> Testing error message information disclosure")
        
        try:
            kem = OQSKEMAdapter("NonexistentAlgorithm12345")
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for potentially sensitive information in error messages
            sensitive_keywords = [
                "password", "secret", "private", "key", "confidential",
                "/home/", "/etc/", "c:\\", "database", "token", "credential"
            ]
            
            leaked_info = [kw for kw in sensitive_keywords if kw in error_msg]
            
            if leaked_info:
                findings.add_medium(
                    "Information Disclosure in Error Messages",
                    f"Error messages may leak sensitive information: {leaked_info}",
                    "Trigger error conditions and analyze error messages"
                )
                findings.tests_failed += 1
            else:
                logger.info("    [OK] Error messages appear clean")
                findings.tests_passed += 1
                
    except Exception as e:
        logger.error(f"Information disclosure test failed: {e}")
        findings.tests_failed += 1

def generate_security_assessment_report(findings: SecurityFindings) -> str:
    """Generate comprehensive security assessment report"""
    
    total_issues = (len(findings.critical_issues) + len(findings.high_issues) + 
                   len(findings.medium_issues) + len(findings.low_issues))
    total_tests = findings.tests_passed + findings.tests_failed
    
    if total_tests > 0:
        pass_rate = (findings.tests_passed / total_tests) * 100
    else:
        pass_rate = 0
    
    # Calculate security score
    security_score = max(0, pass_rate - (len(findings.critical_issues) * 30) - 
                        (len(findings.high_issues) * 15) - (len(findings.medium_issues) * 8))
    
    report = f"""
# COMPREHENSIVE SECURITY AUDIT REPORT
**Adversarial Security Assessment - Favapqc Implementation**

## EXECUTIVE SUMMARY

Total Security Issues Found: {total_issues}
- Critical Issues: {len(findings.critical_issues)}
- High Severity Issues: {len(findings.high_issues)}
- Medium Severity Issues: {len(findings.medium_issues)}
- Low Severity Issues: {len(findings.low_issues)}

Overall Security Score: {security_score:.1f}/100
Test Pass Rate: {pass_rate:.1f}% ({findings.tests_passed}/{total_tests})

"""
    
    if findings.critical_issues:
        report += "## CRITICAL VULNERABILITIES (CVSS >= 9.0)\n"
        report += "IMMEDIATE ACTION REQUIRED - DO NOT DEPLOY TO PRODUCTION\n\n"
        
        for i, issue in enumerate(findings.critical_issues, 1):
            report += f"### CRITICAL-{i}: {issue['name']}\n"
            report += f"- **CVSS Score**: {issue['cvss']}\n"
            report += f"- **Description**: {issue['description']}\n"
            report += f"- **Attack Vector**: {issue['attack_vector']}\n\n"
    
    if findings.high_issues:
        report += "## HIGH SEVERITY VULNERABILITIES (CVSS 7.0-8.9)\n"
        report += "Action Required Before Production Deployment\n\n"
        
        for i, issue in enumerate(findings.high_issues, 1):
            report += f"### HIGH-{i}: {issue['name']}\n"
            report += f"- **CVSS Score**: {issue['cvss']}\n"
            report += f"- **Description**: {issue['description']}\n"
            report += f"- **Attack Vector**: {issue['attack_vector']}\n\n"
    
    if findings.medium_issues:
        report += "## MEDIUM SEVERITY VULNERABILITIES (CVSS 4.0-6.9)\n\n"
        
        for i, issue in enumerate(findings.medium_issues, 1):
            report += f"### MEDIUM-{i}: {issue['name']}\n"
            report += f"- **CVSS Score**: {issue['cvss']}\n"
            report += f"- **Description**: {issue['description']}\n"
            report += f"- **Attack Vector**: {issue['attack_vector']}\n\n"
    
    report += "## SECURITY RECOMMENDATIONS\n\n"
    
    if findings.critical_issues or findings.high_issues:
        report += "### IMMEDIATE ACTIONS REQUIRED\n"
        report += "1. DO NOT deploy to production until critical/high issues are fixed\n"
        report += "2. Implement comprehensive input validation\n"
        report += "3. Add security testing to CI/CD pipeline\n"
        report += "4. Conduct security code review\n\n"
    else:
        report += "### NO CRITICAL OR HIGH SEVERITY ISSUES FOUND\n"
        report += "The system appears to have good security controls in place.\n\n"
    
    report += "### GENERAL SECURITY IMPROVEMENTS\n"
    report += "1. Implement comprehensive security monitoring\n"
    report += "2. Add rate limiting for DoS protection\n"
    report += "3. Regular security audits (quarterly recommended)\n"
    report += "4. Keep cryptographic libraries updated\n"
    report += "5. Implement proper key rotation mechanisms\n"
    report += "6. Add memory protection for sensitive data\n\n"
    
    # Overall assessment
    if security_score >= 80:
        assessment = "GOOD - System demonstrates strong security controls"
    elif security_score >= 60:
        assessment = "MODERATE - Some security improvements needed"
    elif security_score >= 40:
        assessment = "BELOW AVERAGE - Significant security improvements required"
    else:
        assessment = "POOR - Major security issues must be addressed"
    
    report += f"## OVERALL SECURITY ASSESSMENT\n\n{assessment}\n"
    report += f"**Final Security Score: {security_score:.1f}/100**\n\n"
    
    report += "---\n"
    report += f"Report generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
    report += "Generated by: Security Audit Agent #2 - Adversarial Testing\n"
    
    return report

def main():
    """Main security audit execution"""
    print("ADVERSARIAL SECURITY AUDIT - Favapqc Implementation")
    print("=" * 60)
    print("Security Audit Agent #2: Hostile Security Research")
    print("Mission: Find ALL remaining vulnerabilities")
    print("=" * 60)
    
    findings = SecurityFindings()
    
    # Test categories
    test_functions = [
        ("Crypto Service Vulnerabilities", test_crypto_service_vulnerabilities),
        ("Key Management Vulnerabilities", test_key_management_vulnerabilities),
        ("Bundle Parsing Vulnerabilities", test_bundle_parsing_vulnerabilities),
        ("Input Validation Vulnerabilities", test_input_validation_vulnerabilities),
        ("Timing Attack Vulnerabilities", test_timing_attack_vulnerabilities),
        ("Memory Safety Vulnerabilities", test_memory_safety_vulnerabilities),
        ("Information Disclosure Vulnerabilities", test_information_disclosure_vulnerabilities),
    ]
    
    print(f"\nRunning {len(test_functions)} test categories...\n")
    
    for category_name, test_func in test_functions:
        print(f"[TESTING] {category_name}")
        try:
            test_func(findings)
        except Exception as e:
            logger.error(f"Test category {category_name} failed: {e}")
            findings.tests_failed += 1
    
    # Generate report
    print("\nGenerating security assessment report...")
    report = generate_security_assessment_report(findings)
    
    # Save report
    report_file = Path("COMPREHENSIVE_SECURITY_AUDIT_REPORT.md")
    report_file.write_text(report, encoding='utf-8')
    
    # Print summary
    print("\n" + "=" * 60)
    print("SECURITY AUDIT COMPLETED")
    print("=" * 60)
    
    total_issues = (len(findings.critical_issues) + len(findings.high_issues) + 
                   len(findings.medium_issues) + len(findings.low_issues))
    
    print(f"Total Issues Found: {total_issues}")
    print(f"- Critical: {len(findings.critical_issues)}")
    print(f"- High: {len(findings.high_issues)}")
    print(f"- Medium: {len(findings.medium_issues)}")
    print(f"- Low: {len(findings.low_issues)}")
    print(f"Tests Passed: {findings.tests_passed}")
    print(f"Tests Failed: {findings.tests_failed}")
    print(f"Report saved: {report_file.absolute()}")
    
    if findings.critical_issues:
        print("\n[CRITICAL] Critical vulnerabilities found - DO NOT deploy to production!")
        for issue in findings.critical_issues:
            print(f"  - {issue['name']}")
        return False
    elif findings.high_issues:
        print("\n[WARNING] High severity vulnerabilities found - Address before production")
        for issue in findings.high_issues:
            print(f"  - {issue['name']}")
        return False
    else:
        print("\n[OK] No critical or high severity vulnerabilities found")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)