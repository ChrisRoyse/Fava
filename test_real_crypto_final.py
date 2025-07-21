#!/usr/bin/env python3
"""
Final comprehensive test of real cryptographic implementations.
This test validates that our real implementations work correctly and can replace placeholders.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_kem_library():
    """Test RealKEMLibraryHelper implementation."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from fava.pqc.real_implementations.kem_helper import RealKEMLibraryHelper
    
    logger.info("Testing RealKEMLibraryHelper...")
    
    # Test X25519 (Classical KEM)
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives import serialization
    
    # Generate recipient key pair
    recipient_private_key = x25519.X25519PrivateKey.generate()
    recipient_public_key_bytes = recipient_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    recipient_private_key_bytes = recipient_private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Test encapsulation
    encap_result = RealKEMLibraryHelper.hybrid_kem_classical_encapsulate(
        "X25519", recipient_public_key_bytes
    )
    assert "shared_secret" in encap_result
    assert "ephemeral_public_key" in encap_result
    
    # Test decapsulation
    shared_secret = RealKEMLibraryHelper.hybrid_kem_classical_decapsulate(
        "X25519", encap_result["ephemeral_public_key"], recipient_private_key_bytes
    )
    assert shared_secret == encap_result["shared_secret"]
    
    # Test Kyber768 (PQC KEM)
    try:
        import oqs
        
        with oqs.KeyEncapsulation("Kyber768") as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()
        
        # Test encapsulation
        pqc_encap_result = RealKEMLibraryHelper.pqc_kem_encapsulate("Kyber768", public_key)
        assert "shared_secret" in pqc_encap_result
        assert "encapsulated_key" in pqc_encap_result
        
        # Test decapsulation
        pqc_shared_secret = RealKEMLibraryHelper.pqc_kem_decapsulate(
            "Kyber768", pqc_encap_result["encapsulated_key"], private_key
        )
        assert pqc_shared_secret == pqc_encap_result["shared_secret"]
        
        logger.info("✓ RealKEMLibraryHelper working correctly")
        return True
        
    except Exception as e:
        logger.warning(f"⚠ Kyber768 test failed: {e}")
        return False


def test_real_kdf_library():
    """Test RealKDFLibraryHelper implementation."""
    from fava.pqc.real_implementations.kdf_helper import RealKDFLibraryHelper
    from fava.pqc.real_implementations.utility_helper import RealUtilityLibraryHelper
    
    logger.info("Testing RealKDFLibraryHelper...")
    
    # Test HKDF-SHA256
    input_material = b"test_input_key_material_for_hkdf_testing"
    salt = RealUtilityLibraryHelper.generate_random_bytes(16)
    
    derived_key = RealKDFLibraryHelper.derive(
        input_material, salt, "HKDF-SHA256", 32, "test_context"
    )
    assert len(derived_key) == 32
    
    # Test reproducibility
    derived_key2 = RealKDFLibraryHelper.derive(
        input_material, salt, "HKDF-SHA256", 32, "test_context"
    )
    assert derived_key == derived_key2
    
    # Test Argon2id
    password = b"test_password_for_argon2id_testing"
    derived_key3 = RealKDFLibraryHelper.derive(
        password, salt, "Argon2id", 64, "test_context"
    )
    assert len(derived_key3) == 64
    
    logger.info("✓ RealKDFLibraryHelper working correctly")
    return True


def test_real_symmetric_library():
    """Test RealSymmetricCipherLibraryHelper implementation."""
    from fava.pqc.real_implementations.symmetric_helper import RealSymmetricCipherLibraryHelper
    from fava.pqc.real_implementations.utility_helper import RealUtilityLibraryHelper
    
    logger.info("Testing RealSymmetricCipherLibraryHelper...")
    
    # Generate key and IV
    key = RealUtilityLibraryHelper.generate_random_bytes(32)
    iv = RealUtilityLibraryHelper.generate_random_bytes(12)
    
    # Test data
    plaintext = b"This is a comprehensive test message for AES-256-GCM encryption using our real implementation"
    
    # Test encryption
    result = RealSymmetricCipherLibraryHelper.encrypt_aead(
        "AES256GCM", key, iv, plaintext, None
    )
    assert "ciphertext" in result
    assert "authentication_tag" in result
    
    # Test decryption
    decrypted = RealSymmetricCipherLibraryHelper.decrypt_aead(
        "AES256GCM", key, iv, result["ciphertext"], result["authentication_tag"], None
    )
    assert decrypted == plaintext
    
    # Test authentication failure
    tampered_ciphertext = bytearray(result["ciphertext"])
    tampered_ciphertext[0] ^= 0x01  # Flip one bit
    
    decrypted_tampered = RealSymmetricCipherLibraryHelper.decrypt_aead(
        "AES256GCM", key, iv, bytes(tampered_ciphertext), result["authentication_tag"], None
    )
    assert decrypted_tampered is None  # Should fail authentication
    
    logger.info("✓ RealSymmetricCipherLibraryHelper working correctly")
    return True


def test_real_utility_library():
    """Test RealUtilityLibraryHelper implementation."""
    from fava.pqc.real_implementations.utility_helper import RealUtilityLibraryHelper
    
    logger.info("Testing RealUtilityLibraryHelper...")
    
    # Test random byte generation
    random_bytes1 = RealUtilityLibraryHelper.generate_random_bytes(32)
    random_bytes2 = RealUtilityLibraryHelper.generate_random_bytes(32)
    assert len(random_bytes1) == 32
    assert len(random_bytes2) == 32
    assert random_bytes1 != random_bytes2  # Should be different
    
    # Test algorithm parameter lookup
    assert RealUtilityLibraryHelper.get_symmetric_key_length("AES256GCM") == 32
    assert RealUtilityLibraryHelper.get_symmetric_key_length("AES128GCM") == 16
    assert RealUtilityLibraryHelper.get_iv_length("AES256GCM") == 12
    
    # Test secure comparison
    data1 = b"test_data_for_comparison"
    data2 = b"test_data_for_comparison"
    data3 = b"different_test_data"
    
    assert RealUtilityLibraryHelper.secure_compare(data1, data2) == True
    assert RealUtilityLibraryHelper.secure_compare(data1, data3) == False
    
    logger.info("✓ RealUtilityLibraryHelper working correctly")
    return True


def test_real_frontend_helpers():
    """Test real frontend helper implementations."""
    from fava.pqc.frontend_lib_helpers import (
        RealSystemTimeHelper, RealJSCryptoSHA256Helper, RealJSCryptoSHA3_256Helper, RealLibOQSJSHelper
    )
    
    logger.info("Testing real frontend helpers...")
    
    # Test system time
    timestamp = RealSystemTimeHelper.get_system_time_ms()
    assert isinstance(timestamp, int)
    assert timestamp > 0
    
    # Test hashing
    test_data = b"test data for hashing functions"
    
    sha256_hash = RealJSCryptoSHA256Helper.hash(test_data)
    assert len(sha256_hash) == 32
    
    sha3_256_hash = RealJSCryptoSHA3_256Helper.hash(test_data)
    assert len(sha3_256_hash) == 32
    assert sha256_hash != sha3_256_hash  # Different algorithms should produce different hashes
    
    # Test Dilithium3 verification
    try:
        import oqs
        
        with oqs.Signature("Dilithium3") as signer:
            public_key = signer.generate_keypair()
            message = b"Test message for Dilithium3 signature verification"
            signature = signer.sign(message)
            
            # Test with our real implementation
            is_valid = RealLibOQSJSHelper.dilithium3_verify(message, signature, public_key)
            assert is_valid == True
            
            # Test with wrong message
            wrong_message = b"Wrong message"
            is_invalid = RealLibOQSJSHelper.dilithium3_verify(wrong_message, signature, public_key)
            assert is_invalid == False
        
        logger.info("✓ Real frontend helpers working correctly")
        return True
        
    except Exception as e:
        logger.warning(f"⚠ Dilithium3 frontend test failed: {e}")
        return False


def test_integration_with_placeholders_replaced():
    """Test that our real implementations work when placeholders are replaced."""
    # This tests the actual replacement we made in crypto_lib_helpers.py
    from fava.pqc.crypto_lib_helpers import (
        KEM_LIBRARY, KDF_LIBRARY, SYMMETRIC_CIPHER_LIBRARY, UTILITY_LIBRARY
    )
    from fava.pqc.real_implementations.kem_helper import RealKEMLibraryHelper
    from fava.pqc.real_implementations.kdf_helper import RealKDFLibraryHelper
    from fava.pqc.real_implementations.symmetric_helper import RealSymmetricCipherLibraryHelper
    from fava.pqc.real_implementations.utility_helper import RealUtilityLibraryHelper
    
    logger.info("Testing placeholder replacement integration...")
    
    # Verify that placeholders have been replaced with real implementations
    assert KEM_LIBRARY == RealKEMLibraryHelper
    assert KDF_LIBRARY == RealKDFLibraryHelper
    assert SYMMETRIC_CIPHER_LIBRARY == RealSymmetricCipherLibraryHelper
    assert UTILITY_LIBRARY == RealUtilityLibraryHelper
    
    # Test that we can use the libraries through the old interface
    random_data = UTILITY_LIBRARY.generate_random_bytes(16)
    assert len(random_data) == 16
    
    key_length = UTILITY_LIBRARY.get_symmetric_key_length("AES256GCM")
    assert key_length == 32
    
    logger.info("✓ Placeholder replacement integration working correctly")
    return True


def main():
    """Run all comprehensive tests."""
    logger.info("Starting comprehensive real crypto implementation tests...")
    
    tests = [
        test_real_kem_library,
        test_real_kdf_library,
        test_real_symmetric_library,
        test_real_utility_library,
        test_real_frontend_helpers,
        test_integration_with_placeholders_replaced
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"❌ Test {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Real crypto implementations are working correctly.")
        logger.info("✅ Placeholder cryptographic implementations have been successfully replaced with real, production-grade implementations.")
        logger.info("🔒 The system now provides actual cryptographic security using:")
        logger.info("   • Kyber768 for post-quantum key encapsulation")
        logger.info("   • X25519 for classical key agreement") 
        logger.info("   • AES-256-GCM for authenticated symmetric encryption")
        logger.info("   • HKDF and Argon2id for key derivation")
        logger.info("   • Dilithium3 for post-quantum digital signatures")
        logger.info("   • SHA-256 and SHA3-256 for hashing")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Some implementations may need attention.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)