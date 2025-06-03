import pytest
from unittest import mock
from fava.core.fava_options import FavaOptions # Import the real FavaOptions
from .mocks import (
    MockOQS_KeyEncapsulation,
    MockX25519PrivateKey,
    MockX25519PublicKey,
    MockAESGCM,
    MockArgon2id,
    MockHKDFExpand
)

@pytest.fixture
def mock_crypto_libs(monkeypatch):
    """Mocks core crypto libraries at a high level."""
    # Patch KeyEncapsulation where it's imported and used by HybridPqcHandler
    monkeypatch.setattr("fava.crypto.handlers.KeyEncapsulation", lambda name: MockOQS_KeyEncapsulation(name))
    monkeypatch.setattr("cryptography.hazmat.primitives.asymmetric.x25519.X25519PrivateKey", MockX25519PrivateKey)
    monkeypatch.setattr("cryptography.hazmat.primitives.asymmetric.x25519.X25519PublicKey", MockX25519PublicKey)
    # Patch AESGCM where it's imported and used by HybridPqcHandler
    monkeypatch.setattr("fava.crypto.handlers.AESGCM", MockAESGCM)
    # For specific classes like Argon2id, HKDFExpand, Cipher, algorithms, modes, hashes, backends:
    # These might need more granular mocking if used directly by UUT, e.g.,
    monkeypatch.setattr("cryptography.hazmat.primitives.kdf.argon2.Argon2id", MockArgon2id)
    monkeypatch.setattr("cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand", MockHKDFExpand)
    # monkeypatch.setattr("cryptography.hazmat.primitives.hashes.SHA512", mock.Mock) # if SHA512() is called
    # monkeypatch.setattr("cryptography.hazmat.backends.default_backend", mock.Mock) # if default_backend() is called
    # monkeypatch.setattr("cryptography.hazmat.primitives.ciphers.Cipher", mock.Mock) # if Cipher(...) is called
    # monkeypatch.setattr("cryptography.hazmat.primitives.ciphers.algorithms.AES", mock.Mock) # if AES(...) is called
    # monkeypatch.setattr("cryptography.hazmat.primitives.ciphers.modes.GCM", mock.Mock) # if GCM(...) is called
    # monkeypatch.setattr("os.urandom", mock.Mock(return_value=b"random_bytes_for_iv_salt"))


@pytest.fixture
def mock_fava_config():
    """Provides a mock FavaOptions object."""
    # Use spec to make the mock behave more like the real FavaOptions class
    config = mock.Mock(spec=FavaOptions)
    config.pqc_data_at_rest_enabled = True
    config.pqc_active_suite_id = "X25519_KYBER768_AES256GCM"
    config.pqc_key_management_mode = "PASSPHRASE_DERIVED" # or "EXTERNAL_FILE"
    config.pqc_suites = {
        "X25519_KYBER768_AES256GCM": {
            "id": "X25519_KYBER768_AES256GCM",
            "classical_kem_algorithm": "X25519",
            "pqc_kem_algorithm": "ML-KEM-768", # Matched to oqs.KeyEncapsulation
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512", # For HKDFExpand mock
            "pbkdf_algorithm_for_passphrase": "Argon2id", # For Argon2id mock
            "kdf_algorithm_for_ikm_from_pbkdf": "HKDF-SHA3-512"
        }
    }
    config.pqc_key_file_paths = {
        "classical_private": "path/to/classical.key",
        "pqc_private": "path/to/pqc.key"
    }
    config.pqc_fallback_to_classical_gpg = True
    config.gpg_options = "--some-gpg-option"
    config.input_files = ["mock_ledger.beancount"] # Add input_files for FavaLedger init
    return config