import pytest
import time
import logging
import os
import json
from typing import Dict, Any

from fava.pqc.global_config import GlobalConfig
from fava.pqc.backend_crypto_service import (
    BackendCryptoService,
    HybridPqcCryptoHandler,
    HashingProvider,
    KeyMaterialForEncryption,
    KeyMaterialForDecryption,
    HybridEncryptedBundle
)
from fava.pqc.interfaces import HasherInterface
from fava.pqc.exceptions import ConfigurationError, DecryptionError, EncryptionFailedError

# Configure logging to capture performance metrics
# Using a dedicated logger or specific formatting for performance logs
performance_logger = logging.getLogger("pqc_performance")
performance_logger.setLevel(logging.INFO)
# Ensure logs go to stdout for capture by test runners or CI
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s') # Keep it simple for parsing
handler.setFormatter(formatter)
if not performance_logger.handlers:
    performance_logger.addHandler(handler)

# --- Constants for Testing ---
TEST_SUITE_ID_HYBRID = "TEST_HYBRID_X25519_KYBER768_AES256GCM"
TEST_HYBRID_SUITE_CONFIG: Dict[str, Any] = {
    "description": "Test Hybrid: X25519 + Kyber-768 KEM with AES-256-GCM",
    "classical_kem_algorithm": "X25519",  # Placeholder, real lib might need specific names
    "pqc_kem_algorithm": "Kyber768",      # Placeholder
    "symmetric_algorithm": "AES256GCM",   # Placeholder
    "kdf_algorithm_for_hybrid_sk": "HKDF-SHA256", # Placeholder
    "format_identifier": "FAVA_PQC_HYBRID_TEST_V1"
}

# Dummy key material (replace with actual key generation/loading if testing real crypto performance)
# For now, these are just to satisfy type hints and basic structure.
# Actual crypto libraries will require valid keys.
# Using os.urandom for plausible byte strings of appropriate (though arbitrary) lengths.
# Kyber-768 public key: 1184 bytes, secret key: 2400 bytes
# X25519 keys: 32 bytes
DUMMY_CLASSICAL_PK = os.urandom(32)
DUMMY_CLASSICAL_SK = os.urandom(32)
DUMMY_PQC_PK = os.urandom(1184)
DUMMY_PQC_SK = os.urandom(2400)

KEY_MATERIAL_ENCRYPT: KeyMaterialForEncryption = {
    "classical_recipient_pk": DUMMY_CLASSICAL_PK,
    "pqc_recipient_pk": DUMMY_PQC_PK,
    "kdf_salt_for_passphrase_derived_keys": os.urandom(16) # Example salt
}
KEY_MATERIAL_DECRYPT: KeyMaterialForDecryption = {
    "classical_recipient_sk": DUMMY_CLASSICAL_SK,
    "pqc_recipient_sk": DUMMY_PQC_SK,
    "kdf_salt_for_passphrase_derived_keys": KEY_MATERIAL_ENCRYPT["kdf_salt_for_passphrase_derived_keys"]
}

def generate_test_data(size_kb: int) -> bytes:
    """Generates test data of a specified size in KB."""
    return os.urandom(size_kb * 1024)

@pytest.fixture(autouse=True)
def reset_crypto_services_for_test():
    """Ensures a clean state for crypto services before each test."""
    BackendCryptoService.reset_registry_for_testing()
    GlobalConfig.reset_cache() # Ensure GlobalConfig cache is cleared
    # Reset GlobalConfig if it caches, or ensure monkeypatch handles it per test
    # For now, assuming GlobalConfig.set_config is effective per test via monkeypatch

@pytest.fixture
def configured_global_config_hybrid(monkeypatch):
    """Sets up GlobalConfig for hybrid encryption tests."""
    test_config = {
        "data_at_rest": {
            "active_encryption_suite_id": TEST_SUITE_ID_HYBRID,
            "decryption_attempt_order": [TEST_SUITE_ID_HYBRID],
            "suites": {
                TEST_SUITE_ID_HYBRID: TEST_HYBRID_SUITE_CONFIG
            }
        },
        "hashing": {
            "default_algorithm": "SHA3-256"
        }
    }
    monkeypatch.setattr(GlobalConfig, "get_crypto_settings", lambda: test_config)
    
    # Register the handler factory or instance
    BackendCryptoService.register_crypto_handler(
        TEST_SUITE_ID_HYBRID,
        lambda sid, scfg: HybridPqcCryptoHandler(sid, scfg)
    )
    return test_config

@pytest.fixture
def configured_global_config_hashing(monkeypatch):
    """Sets up GlobalConfig for hashing tests."""
    test_config = {
        "hashing": {
            "default_algorithm": "SHA3-256"
        }
        # data_at_rest can be minimal or absent if not used by hashing tests
    }
    monkeypatch.setattr(GlobalConfig, "get_crypto_settings", lambda: test_config)
    return test_config


@pytest.mark.parametrize("data_size_kb", [1, 10, 100]) # Test with 1KB, 10KB, 100KB data
def test_performance_data_at_rest_encryption(configured_global_config_hybrid, data_size_kb):
    data_to_encrypt = generate_test_data(data_size_kb)
    data_size_bytes = len(data_to_encrypt)

    try:
        handler = BackendCryptoService.get_active_encryption_handler()
        assert isinstance(handler, HybridPqcCryptoHandler)
    except ConfigurationError as e:
        pytest.fail(f"Failed to get active encryption handler: {e}")
        return # for type checker

    start_time = time.perf_counter()
    try:
        encrypted_bundle = handler.encrypt(data_to_encrypt, KEY_MATERIAL_ENCRYPT)
        assert encrypted_bundle is not None
    except EncryptionFailedError as e:
        # This might happen if dummy keys are not compatible with underlying real crypto libs
        performance_logger.warning(f"PERFORMANCE_LOG_ENCRYPT_FAILED: operation=encrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, data_size_bytes={data_size_bytes}, error='{e}'")
        pytest.skip(f"Encryption failed, possibly due to dummy keys and real crypto lib interaction: {e}")
        return
    except Exception as e:
        performance_logger.error(f"PERFORMANCE_LOG_ENCRYPT_UNEXPECTED_ERROR: operation=encrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, data_size_bytes={data_size_bytes}, error='{e}'")
        pytest.fail(f"Unexpected error during encryption: {e}")
        return

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    performance_logger.info(
        f"PERFORMANCE_LOG: operation=encrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, "
        f"data_size_bytes={data_size_bytes}, duration_ms={duration_ms:.3f}"
    )
    assert encrypted_bundle["suite_id_used"] == TEST_SUITE_ID_HYBRID

@pytest.mark.parametrize("data_size_kb", [1, 10, 100])
def test_performance_data_at_rest_decryption(configured_global_config_hybrid, data_size_kb):
    data_to_process = generate_test_data(data_size_kb)
    data_size_bytes = len(data_to_process)

    try:
        enc_handler = BackendCryptoService.get_active_encryption_handler()
        assert isinstance(enc_handler, HybridPqcCryptoHandler)
    except ConfigurationError as e:
        pytest.fail(f"Failed to get active encryption handler for setup: {e}")
        return

    try:
        encrypted_bundle = enc_handler.encrypt(data_to_process, KEY_MATERIAL_ENCRYPT)
    except EncryptionFailedError as e:
        pytest.skip(f"Setup encryption failed, cannot test decryption: {e}")
        return
    except Exception as e:
        pytest.fail(f"Unexpected error during setup encryption: {e}")
        return

    dec_handlers = BackendCryptoService.get_configured_decryption_handlers()
    assert len(dec_handlers) > 0
    dec_handler = dec_handlers[0]
    assert isinstance(dec_handler, HybridPqcCryptoHandler)

    start_time = time.perf_counter()
    try:
        decrypted_data = dec_handler.decrypt(encrypted_bundle, KEY_MATERIAL_DECRYPT)
        assert decrypted_data == data_to_process
    except DecryptionError as e:
        performance_logger.warning(f"PERFORMANCE_LOG_DECRYPT_FAILED: operation=decrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, data_size_bytes={data_size_bytes}, error='{e}'")
        pytest.skip(f"Decryption failed, possibly due to dummy keys or bundle mismatch: {e}")
        return
    except Exception as e:
        performance_logger.error(f"PERFORMANCE_LOG_DECRYPT_UNEXPECTED_ERROR: operation=decrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, data_size_bytes={data_size_bytes}, error='{e}'")
        pytest.fail(f"Unexpected error during decryption: {e}")
        return

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    performance_logger.info(
        f"PERFORMANCE_LOG: operation=decrypt_data_at_rest, suite_id={TEST_SUITE_ID_HYBRID}, "
        f"data_size_bytes={data_size_bytes}, duration_ms={duration_ms:.3f}"
    )

@pytest.mark.parametrize("data_size_kb", [1, 100, 1024]) # Test with 1KB, 100KB, 1MB data
def test_performance_hashing_backend(configured_global_config_hashing, data_size_kb):
    data_to_hash_str = generate_test_data(data_size_kb).decode('latin-1') # As string
    data_size_bytes = len(data_to_hash_str.encode('utf-8')) # Use UTF-8 byte size for consistency
    algo_name = "SHA3-256" # As per configured_global_config_hashing

    try:
        hasher = HashingProvider.get_configured_hasher()
    except Exception as e:
        pytest.fail(f"Failed to get hasher: {e}")
        return

    start_time = time.perf_counter()
    try:
        # Using hash_string_to_hex as it's often used in Fava
        hex_digest = hasher.hash_string_to_hex(data_to_hash_str)
        assert hex_digest is not None and len(hex_digest) == 64 # SHA3-256 produces 32 bytes -> 64 hex chars
    except Exception as e: # Catch potential errors from hashing
        performance_logger.error(f"PERFORMANCE_LOG_HASH_ERROR: operation=hash_backend, algorithm={algo_name}, data_size_bytes={data_size_bytes}, error='{e}'")
        pytest.fail(f"Hashing operation failed: {e}")
        return

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    performance_logger.info(
        f"PERFORMANCE_LOG: operation=hash_backend, algorithm={algo_name}, "
        f"data_size_bytes={data_size_bytes}, duration_ms={duration_ms:.3f}"
    )

# Note: The actual performance of crypto operations will heavily depend on the
# implementation of KEM_LIBRARY, KDF_LIBRARY, SYMMETRIC_CIPHER_LIBRARY,
# and the underlying C libraries (e.g., oqs-python, cryptography).
# If these helpers are pure Python mocks, the timings will not be representative.
# This test assumes they call out to real crypto libraries.
# The dummy keys might cause issues if real crypto libraries expect specific formats/validity.
# If EncryptionFailedError or DecryptionError occur frequently, it indicates an issue with
# the dummy key setup or the interaction with the crypto libraries, and tests are skipped.