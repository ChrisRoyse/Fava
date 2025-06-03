import pytest
from unittest import mock
from typing import Tuple # Added for type hinting

# --- Placeholder for Application Modules (UUTs) ---
# These would normally be imported, e.g.:
# from fava.crypto import keys as key_management_module
# from fava.crypto.handlers import HybridPqcHandler, GpgHandler
# from fava.crypto.locator import CryptoServiceLocator
# from fava.core.ledger import FavaLedger
# from fava.core.encrypted_file_bundle import EncryptedFileBundle
# from fava.helpers import FavaOptions # or wherever FavaOptions is defined

# For TDD, we mock assuming these paths.

# --- Mock Objects for External Libraries (Simplified) ---
# These help in structuring tests if UUTs expect specific types.

class MockOQS_KeyEncapsulation:
    # Class-level mocks
    _mock_generate_keypair_class = mock.Mock(return_value=(b"mock_pqc_pk_class", b"mock_pqc_sk_class"))
    _mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class")) # (ciphertext, shared_secret)
    _correct_pqc_sk_for_mock_ct = b'S' * 2400 # Matches test_tp_dar_hph_003's PQC SK

    @staticmethod
    def _mock_decapsulate_side_effect(sk, ct):
        if ct == b"mock_kem_ct_class" and sk == MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct:
            return b"mock_kem_ss_class" # Correct SS for correct SK and CT
        # For any other SK with the "correct" CT, or any other CT, return a different SS
        return b"ss_for_oqs_WRONG_SK_OR_CT_" + (sk[:5] if sk else b"no_sk")

    _mock_decapsulate_class = mock.Mock(side_effect=_mock_decapsulate_side_effect)
    _mock_keypair_from_secret_class = mock.Mock(return_value=(b"mock_pqc_pk_from_secret_class", b"mock_pqc_sk_from_secret_class"))
    SUPPORTED_KEMS = {"ML-KEM-768", "Kyber-768", "ML-KEM-1024"} # Added to mock the real attribute

    def __init__(self, kem_name):
        self.kem_name = kem_name
        # Instance-specific mocks are not used when class is replaced with `new=` for these assertions.
        # For clarity, ensure class mocks are reset per test if state needs to be isolated.

    def generate_keypair(self):
        return MockOQS_KeyEncapsulation._mock_generate_keypair_class()

    def encapsulate(self, public_key):
        return MockOQS_KeyEncapsulation._mock_encapsulate_class(public_key)

    def decapsulate(self, secret_key, ciphertext):
        return MockOQS_KeyEncapsulation._mock_decapsulate_class(secret_key, ciphertext)

    def keypair_from_secret(self, secret_bytes):
        return MockOQS_KeyEncapsulation._mock_keypair_from_secret_class(secret_bytes)

    def encap_secret(self, public_key: bytes) -> Tuple[bytes, bytes]:
        # _mock_encapsulate_class default return_value is (b"mock_kem_ct_class", b"mock_kem_ss_class")
        # Let's assume this is (actual_ciphertext, actual_shared_secret)
        actual_ct, actual_ss = MockOQS_KeyEncapsulation._mock_encapsulate_class(public_key)
        # HybridPqcHandler expects (shared_secret, ciphertext)
        return actual_ss, actual_ct

    def decap_secret(self, sk_bytes: bytes, ciphertext: bytes) -> bytes:
        # _mock_decapsulate_class default return_value is b"mock_kem_ss_class"
        # It's a mock, so it will record the call with sk_bytes and ciphertext.
        return MockOQS_KeyEncapsulation._mock_decapsulate_class(sk_bytes, ciphertext)

class MockX25519PrivateKey:
    _generate_return_override = None # Tests can set this to an instance to override generate()
    _from_private_bytes_return_override = None # Similar for from_private_bytes

    def __init__(self, private_bytes=None):
        self._private_bytes = private_bytes if private_bytes is not None else b"default_mock_priv_key_bytes"
        # Each private key instance should have its own public key instance.
        # For mock commutativity in exchange, let public key "material" be same as private key "material".
        self.public_key_instance = MockX25519PublicKey(self._private_bytes)

    @staticmethod
    def generate():
        # If a test has specifically configured an override, use that.
        if MockX25519PrivateKey._generate_return_override is not None:
            instance_to_return = MockX25519PrivateKey._generate_return_override
            # Optional: Reset for next test if state needs to be isolated per call
            # MockX25519PrivateKey._generate_return_override = None
            return instance_to_return
        
        # Otherwise, for default behavior, create and return a fresh instance directly.
        return MockX25519PrivateKey(b"default_generated_private_key_direct_in_generate")

    def public_key(self):
        return self.public_key_instance

    def exchange(self, peer_public_key_instance):
        # peer_public_key_instance is expected to be an instance of MockX25519PublicKey
        if not isinstance(peer_public_key_instance, MockX25519PublicKey):
            raise TypeError(f"peer_public_key must be MockX25519PublicKey, not {type(peer_public_key_instance)}")
        # Make shared secret dependent on both keys for a more realistic (though still mock) exchange.
        # Use first 5 bytes of each key's material for simplicity.
        self_priv_prefix = self._private_bytes[:5] if self._private_bytes else b"noprv"
        peer_pub_prefix = peer_public_key_instance._public_bytes[:5] if peer_public_key_instance._public_bytes else b"nopub"
        # Ensure commutativity by sorting before combining, then hashing (or just concatenating for mock)
        parts = sorted([self_priv_prefix, peer_pub_prefix])
        return b"ss_x25519_" + parts[0] + b"_" + parts[1]
    @staticmethod
    def from_private_bytes(data):
        if MockX25519PrivateKey._from_private_bytes_return_override is not None:
            instance_to_return = MockX25519PrivateKey._from_private_bytes_return_override
            # Optional: Reset for next test
            # MockX25519PrivateKey._from_private_bytes_return_override = None
            return instance_to_return
        return MockX25519PrivateKey(data) # Default behavior

class MockX25519PublicKey:
    def __init__(self, public_bytes=None):
        self._public_bytes = public_bytes if public_bytes is not None else b"default_mock_public_key_bytes"

    @staticmethod
    def from_public_bytes(data):
        return MockX25519PublicKey(public_bytes=data)

    def public_bytes(self, encoding, format):
        # encoding and format are part of the real API (e.g., serialization.Encoding.Raw)
        return self._public_bytes


class MockAESGCMEncryptor:
    def __init__(self):
        self.update = mock.Mock(return_value=b"") # Can be chained if needed
        self.finalize = mock.Mock(return_value=b"mock_aes_ciphertext")
        self.tag = b"mock_aes_auth_tag"

class MockAESGCMDecryptor:
    def __init__(self):
        self.update = mock.Mock(return_value=b"")
        self.finalize = mock.Mock(return_value=b"mock_aes_plaintext")


class MockArgon2id:
    def __init__(self, time_cost=mock.ANY, memory_cost=mock.ANY, parallelism=mock.ANY, length=mock.ANY, salt_len=mock.ANY, backend=None):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.length = length
        self.salt_len = salt_len
        self.backend = backend
        self.derive_mock = mock.Mock(return_value=b"mock_argon2id_ikm_64_bytes_default")

    def derive(self, password, salt):
        return self.derive_mock(password, salt)


class MockAESGCM:
    _correct_key_for_test = None
    _stored_plaintext_for_mock_success = None
    _expected_mock_ciphertext_for_success = None
    _expected_mock_tag_for_success = None

    @classmethod
    def reset_correct_key_for_test(cls):
        cls._correct_key_for_test = None
        cls._stored_plaintext_for_mock_success = None
        cls._expected_mock_ciphertext_for_success = None
        cls._expected_mock_tag_for_success = None

    def __init__(self, key):
        self.key = key

    def encrypt(self, nonce, data, associated_data):
        MockAESGCM._correct_key_for_test = self.key
        MockAESGCM._stored_plaintext_for_mock_success = data
        
        MockAESGCM._expected_mock_ciphertext_for_success = b'c' * len(data)
        MockAESGCM._expected_mock_tag_for_success = b't' * 16
        
        return MockAESGCM._expected_mock_ciphertext_for_success + MockAESGCM._expected_mock_tag_for_success

    def decrypt(self, nonce, data, associated_data):
        if MockAESGCM._correct_key_for_test is not None and self.key != MockAESGCM._correct_key_for_test:
            raise ValueError("Simulated AESGCM InvalidTag: Decryption key does not match encryption key.")

        tag_length = 16
        if len(data) < tag_length:
            raise ValueError("Simulated AESGCM InvalidTag: Received data too short to contain tag.")
            
        received_ciphertext = data[:-tag_length]
        received_tag = data[-tag_length:]

        if (MockAESGCM._expected_mock_ciphertext_for_success is not None and
            received_ciphertext != MockAESGCM._expected_mock_ciphertext_for_success) or \
           (MockAESGCM._expected_mock_tag_for_success is not None and
            received_tag != MockAESGCM._expected_mock_tag_for_success):
            raise ValueError("Simulated AESGCM InvalidTag: Tampered ciphertext or tag.")

        if MockAESGCM._stored_plaintext_for_mock_success is not None:
            return MockAESGCM._stored_plaintext_for_mock_success
        
        raise RuntimeError("MockAESGCM: Decryption called without prior successful encryption state.")

class MockHKDFExpand:
    def __init__(self, algorithm, length, info, backend=None): # Added backend=None to make it optional for other mocks
        self.algorithm = algorithm
        self.length = length
        self.info = info
        self.backend = backend
        self.derive_mock = mock.Mock(return_value=b"M" * self.length) # Consistent with MockHKDF

    def derive(self, ikm):
        return self.derive_mock(ikm)

class MockHKDF:
    def __init__(self, algorithm, length, salt, info, backend):
        self.algorithm = algorithm
        self.length = length
        self.salt = salt
        self.info = info
        self.backend = backend
        self.derive_mock = mock.Mock(return_value=b"M" * self.length)

    def derive(self, ikm):
        return self.derive_mock(ikm)

# --- Test Cases ---

@pytest.mark.usefixtures("mock_crypto_libs", "mock_fava_config")
class TestKeyManagementFunctions:
    """
    Tests for 5.1. Key Management Functions (fava.crypto.keys)
    """

    @pytest.mark.key_management
    @pytest.mark.key_management
    @pytest.mark.critical_path
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    @mock.patch('fava.crypto.keys.KeyEncapsulation')
    @mock.patch('fava.crypto.keys.X25519PrivateKey')
    def test_tp_dar_km_001_derive_kem_keys_from_passphrase(self, mock_x25519_priv_key_class, mock_oqs_kem_class, mock_hkdf_class, mock_argon2id_class, mock_fava_config):
        from fava.crypto import keys as key_management_module # Assuming UUT is here

        passphrase = "test_passphrase_123!"
        salt = b'test_argon_salt_16b'
        pbkdf_algorithm = "Argon2id" # This would select the class, already mocked
        kdf_algorithm_for_ikm = "HKDF-SHA3-512" # This would select the class, already mocked
        classical_kem_spec = "X25519"
        pqc_kem_spec = "ML-KEM-768"

        # Configure mocks
        mock_argon2id_class.return_value = MockArgon2id()
        mock_hkdf_class.return_value = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        mock_oqs_kem_class.return_value = MockOQS_KeyEncapsulation('ML-KEM-768')
        mock_x25519_priv_key_class.return_value = MockX25519PrivateKey()
        
        mock_argon2_instance = mock_argon2id_class.return_value
        mock_argon2_instance.derive_mock.return_value = b"mock_ikm_from_argon"

        mock_hkdf_instance = mock_hkdf_class.return_value
        mock_hkdf_instance.derive_mock.side_effect = [
            b"hkdf_output_for_classical",
            b"hkdf_output_for_pqc"
        ]

        mock_x25519_key_instance = mock_x25519_priv_key_class.return_value
        mock_oqs_kem_instance = mock_oqs_kem_class.return_value


        # Call UUT (assuming it exists and is imported)
        # For now, let's assume a direct call if the module was real
        # classical_keys, pqc_keys = key_management_module.derive_kem_keys_from_passphrase(
        #     passphrase, salt, pbkdf_algorithm, kdf_algorithm_for_ikm,
        #     classical_kem_spec, pqc_kem_spec
        # )
        # UUT function fava.crypto.keys.derive_kem_keys_from_passphrase is now implemented
        classical_keys, pqc_keys = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )

        # Assertions
        mock_argon2_instance.derive_mock.assert_called_once_with(passphrase, salt)
        assert mock_hkdf_instance.derive_mock.call_count == 2
        mock_hkdf_instance.derive_mock.assert_any_call(b"mock_ikm_from_argon")
        assert classical_keys is not None  # Should be mock objects
        assert pqc_keys is not None  # Should be mock objects


    @pytest.mark.key_management
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    def test_tp_dar_km_002_derive_kem_keys_uses_salt_correctly(self, mock_hkdf_class, mock_argon2id_class, mock_fava_config):
        # UUT: fava.crypto.keys.derive_kem_keys_from_passphrase
        from fava.crypto import keys as key_management_module

        passphrase = "test_passphrase_123!"
        salt1 = b'test_argon_salt_A_16b'
        salt2 = b'test_argon_salt_B_16b'
        mock_argon2id_class.return_value = MockArgon2id()
        mock_hkdf_class.return_value = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        
        mock_argon2_instance = mock_argon2id_class.return_value

        # Call 1
        mock_argon2_instance.derive_mock.return_value = b"ikm_for_salt1"
        key_management_module.derive_kem_keys_from_passphrase(passphrase, salt1, "Argon2id", "HKDF-SHA3-512", "X25519", "ML-KEM-768")
        call_args_salt1 = mock_argon2_instance.derive_mock.call_args

        # Call 2
        mock_argon2_instance.derive_mock.return_value = b"ikm_for_salt2"
        key_management_module.derive_kem_keys_from_passphrase(passphrase, salt2, "Argon2id", "HKDF-SHA3-512", "X25519", "ML-KEM-768")
        call_args_salt2 = mock_argon2_instance.derive_mock.call_args

        # Assertions (Example)
        assert call_args_salt1[0][1] == salt1
        assert call_args_salt2[0][1] == salt2
        assert mock_argon2_instance.derive_mock.call_args_list[0][0][1] == salt1 # ikm from salt1
        assert mock_argon2_instance.derive_mock.call_args_list[1][0][1] == salt2 # ikm from salt2


    @pytest.mark.key_management
    @pytest.mark.error_handling
    def test_tp_dar_km_003_key_derivation_fails_unsupported_spec(self, mock_fava_config):
        # UUT: fava.crypto.keys.derive_kem_keys_from_passphrase
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import UnsupportedAlgorithmError # Import the specific exception

        passphrase = "test_passphrase"
        salt = b'some_salt_value_16b'

        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "UNSUPPORTED_KDF", "X25519", "ML-KEM-768"
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "HKDF-SHA3-512", "X25519", "UNSUPPORTED_PQC_KEM"
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "UNSUPPORTED_PBKDF", "HKDF-SHA3-512", "X25519", "ML-KEM-768"
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "HKDF-SHA3-512", "UNSUPPORTED_CLASSICAL_KEM", "ML-KEM-768"
            )


    @pytest.mark.key_management
    @pytest.mark.key_management
    # Patches are applied from bottom up. Arguments in test signature match from left to right.
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    # Patch KeyEncapsulation directly as it's used in load_keys_from_external_file
    @mock.patch('fava.crypto.keys.KeyEncapsulation', new=MockOQS_KeyEncapsulation)
    @mock.patch('fava.crypto.keys.X25519PrivateKey', new=MockX25519PrivateKey)
    def test_tp_dar_km_004_load_keys_from_external_file(self, mock_open, mock_fava_config): # Signature updated
        # UUT: fava.crypto.keys.load_keys_from_external_file
        from fava.crypto import keys as key_management_module
        key_file_path_config = {"classical_private": "mock_classical.key", "pqc_private": "mock_pqc.key"}

        # Configure class-level override for from_private_bytes
        MockX25519PrivateKey._from_private_bytes_return_override = None # Reset before setting
        mock_classical_key_instance = MockX25519PrivateKey(private_bytes=b"classical_key_bytes_instance_data")
        MockX25519PrivateKey._from_private_bytes_return_override = mock_classical_key_instance

        MockOQS_KeyEncapsulation._mock_keypair_from_secret_class.reset_mock() # This mock still uses the old pattern
        mock_pqc_key_instance_pk, mock_pqc_key_instance_sk = (b"mock_pqc_pk_via_class_mock", b"mock_pqc_sk_via_class_mock")
        MockOQS_KeyEncapsulation._mock_keypair_from_secret_class.return_value = (mock_pqc_key_instance_pk, mock_pqc_key_instance_sk)

        mock_open.side_effect = [
            mock.mock_open(read_data=b"classical_key_bytes_from_file").return_value,
            mock.mock_open(read_data=b"pqc_key_bytes_from_file").return_value
        ]
        
        classical_keys_tuple, pqc_keys_tuple = key_management_module.load_keys_from_external_file(key_file_path_config)
        
        # Assertions
        mock_open.assert_any_call("mock_classical.key", "rb")
        mock_open.assert_any_call("mock_pqc.key", "rb")
        
        # Assert calls on the class-level mocks
        # We can't directly assert_called_once_with on _from_private_bytes_return_override.
        # If needed, MockX25519PrivateKey.from_private_bytes itself would need to be patched for this test.
        # For now, the critical check is that the correct instance is returned.
        MockOQS_KeyEncapsulation._mock_keypair_from_secret_class.assert_called_once_with(b"pqc_key_bytes_from_file")

        # Assert returned keys are what the mocks were configured to return
        # classical_keys_tuple is (public_key, private_key)
        assert classical_keys_tuple == (mock_classical_key_instance.public_key(), mock_classical_key_instance)
        assert pqc_keys_tuple == (mock_pqc_key_instance_pk, mock_pqc_key_instance_sk) # UUT returns the tuple from keypair_from_secret
    @pytest.mark.key_management
    @pytest.mark.error_handling
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('fava.crypto.keys.X25519PrivateKey.from_private_bytes', side_effect=ValueError("Invalid key format"))
    def test_tp_dar_km_005_load_keys_external_file_missing_or_invalid(self, mock_x25519_from_bytes, mock_open, mock_fava_config):
        # UUT: fava.crypto.keys.load_keys_from_external_file
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import KeyManagementError # Import specific exception

        # Scenario 1: File not found
        mock_open.side_effect = FileNotFoundError
        with pytest.raises(KeyManagementError):
           key_management_module.load_keys_from_external_file({"classical_private": "non_existent.key"})

        # Scenario 2: Invalid format
        # Reset side_effect for open to avoid interference from previous FileNotFoundError
        mock_open.side_effect = [mock.mock_open(read_data=b"bad_key_data").return_value]
        # mock_x25519_from_bytes is already set to raise ValueError("Invalid key format")
        with pytest.raises(KeyManagementError):
           key_management_module.load_keys_from_external_file({"classical_private": "bad_format.key"})


    @pytest.mark.key_management
    @pytest.mark.security_sensitive
    @mock.patch('fava.crypto.keys._retrieve_stored_or_derived_pqc_private_key')
    @mock.patch('fava.crypto.keys.secure_format_for_export') # Placeholder for actual formatting function
    def test_tp_dar_km_006_export_fava_managed_keys_secure_format(self, mock_secure_format, mock_retrieve_key, mock_fava_config):
        def test_tp_dar_km_006_export_fava_managed_keys_secure_format(self, mock_secure_format, mock_retrieve_key, mock_fava_config):
            # UUT: fava.crypto.keys.export_fava_managed_pqc_private_keys
            from fava.crypto import keys as key_management_module
            # from fava.crypto import exceptions # No longer needed here due to specific import below
    
            mock_retrieve_key.return_value = MockOQS_KeyEncapsulation("ML-KEM-768")._mock_keypair_from_secret()[1] # mock private key bytes
            mock_secure_format.return_value = b"securely_formatted_exported_key_bytes"
    
            exported_data = key_management_module.export_fava_managed_pqc_private_keys(
                "user_context_1", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "export_passphrase", config=mock_fava_config # Pass config
            )
            # Assertions
            mock_retrieve_key.assert_called_once_with("user_context_1", mock_fava_config, "export_passphrase")
            mock_secure_format.assert_called_once_with(mock_retrieve_key.return_value, "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "export_passphrase")
            assert exported_data == b"securely_formatted_exported_key_bytes"
    @pytest.mark.key_management
    @pytest.mark.error_handling
    @pytest.mark.security_sensitive
    @mock.patch('fava.crypto.keys._retrieve_stored_or_derived_pqc_private_key', return_value=None)
    def test_tp_dar_km_007_export_fava_managed_keys_not_found(self, mock_retrieve_key, mock_fava_config):
        # UUT: fava.crypto.keys.export_fava_managed_pqc_private_keys
        from fava.crypto import keys as key_management_module
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import KeyManagementError # Import specific exception

        with pytest.raises(KeyManagementError):
            key_management_module.export_fava_managed_pqc_private_keys(
                "non_existent_context", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "any_pass"
            )

@pytest.mark.usefixtures("mock_crypto_libs", "mock_fava_config")
class TestHybridPqcHandler:
    """
    Tests for 5.2. HybridPqcHandler (fava.crypto.handlers.HybridPqcHandler)
    """
    @pytest.fixture(autouse=True)
    def _reset_mock_aesgcm_state_fixture(self): # Added underscore to indicate it's a fixture for setup/teardown
        MockAESGCM.reset_correct_key_for_test()
        yield
        MockAESGCM.reset_correct_key_for_test()

    @pytest.fixture
    def hybrid_handler(self):
        from fava.crypto.handlers import HybridPqcHandler # Assuming UUT
        return HybridPqcHandler() # Instantiate the handler


    @pytest.mark.config_dependent
    def test_tp_dar_hph_001_can_handle_by_extension(self, hybrid_handler, mock_fava_config):
        assert hybrid_handler.can_handle("data.bc.pqc_hybrid_fava", None, mock_fava_config) is True
        assert hybrid_handler.can_handle("data.bc.gpg", None, mock_fava_config) is False
        assert hybrid_handler.can_handle("data.bc", None, mock_fava_config) is False
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.config_dependent
    @pytest.mark.bundle_format
    @mock.patch('fava.core.encrypted_file_bundle.EncryptedFileBundle.parse_header_only') # Assuming path
    def test_tp_dar_hph_002_can_handle_by_magic_bytes(self, mock_parse_header, hybrid_handler, mock_fava_config):
        mock_parse_header.return_value = {"format_identifier": "FAVA_PQC_HYBRID_V1"} # Valid
        assert hybrid_handler.can_handle("file.ext", b'FAVA_PQC_HYBRID_V1_HEADER_START...', mock_fava_config) is True # Use the example peek from EncryptedFileBundle
        
        mock_parse_header.return_value = None # Invalid or different format
        assert hybrid_handler.can_handle("file.ext", b'OTHER_FORMAT...', mock_fava_config) is False
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.critical_path
    @pytest.mark.performance_smoke
    # Extensive mocking needed here for oqs, cryptography, EncryptedFileBundle
    def test_tp_dar_hph_003_encrypt_decrypt_success(self, hybrid_handler, mock_fava_config):
        plaintext = "This is secret Beancount data."
        suite_config = { "id": "X25519_KYBER768_AES256GCM", "classical_kem_algorithm": "X25519",
                         "pqc_kem_algorithm": "ML-KEM-768", "symmetric_algorithm": "AES256GCM",
                         "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512" }
        
        # Mock key_material_encrypt (public keys) and key_material_decrypt (private keys)
        # These would typically come from FavaLedger or a similar key management component.
        # For this unit test, we can provide mock key objects directly.
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes")
        # ML-KEM-768 public key size is 1184 bytes
        mock_pqc_pk_bytes_correct_size = b'A' * 1184
        # The mock class needs to be updated or we provide raw bytes if the handler expects bytes.
        # The handler's pqc_kem.encap_secret(pqc_pk) expects bytes for public_key.
        # Let's adjust what MockOQS_KeyEncapsulation()._mock_generate_keypair_class()[0] returns for this test.
        # For simplicity, we'll directly use correctly sized bytes here.
        mock_pqc_pk = mock_pqc_pk_bytes_correct_size


        mock_classical_sk = MockX25519PrivateKey(b"mock_classical_sk_bytes")
        # ML-KEM-768 secret key size is 2400 bytes
        mock_pqc_sk_bytes_correct_size = b'S' * 2400
        mock_pqc_sk = mock_pqc_sk_bytes_correct_size

        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk
        }
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk,
            "pqc_private_key": mock_pqc_sk
        }

        # Configure all crypto mocks (oqs KEMs, X25519, HKDF, AESGCM) to behave correctly.
        # This will be handled by the UUT's interaction with the already mocked classes.
        # We need to ensure the UUT calls them correctly.
        
        encrypted_bundle = hybrid_handler.encrypt_content(plaintext, suite_config, key_material_encrypt, mock_fava_config)
        decrypted_content = hybrid_handler.decrypt_content(encrypted_bundle, suite_config, key_material_decrypt, mock_fava_config)
        assert decrypted_content == plaintext
        # pytest.skip("Test not implemented due to complex mocking setup.") # Unskipped

    @pytest.mark.config_dependent
    @mock.patch('fava.crypto.handlers.KeyEncapsulation') # Path to KeyEncapsulation in handler module
    def test_tp_dar_hph_004_encrypt_uses_suite_config(self, mock_key_encapsulation_class_in_handler, hybrid_handler, mock_fava_config): # Renamed mock arg
        # Mock key material (not strictly needed for this specific test's focus but good practice for handler calls)
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes")
        mock_pqc_pk_correct_size = b'B' * 1184 # ML-KEM-768 public key size
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk_correct_size
        }

        suite_config_kyber768 = { "id": "X25519_KYBER768_AES256GCM",
                                  "pqc_kem_algorithm": "ML-KEM-768",
                                  # other params...
                                }
        
        # Mock the instance's encap_secret to prevent actual crypto and allow assertion
        mock_kem_instance = mock_key_encapsulation_class_in_handler.return_value
        mock_kem_instance.encap_secret.return_value = (b"mock_ss", b"mock_ct")

        hybrid_handler.encrypt_content("plaintext", suite_config_kyber768, key_material_encrypt, mock_fava_config)
        
        # Assertion: KeyEncapsulation was initialized with the correct KEM name from suite_config
        mock_key_encapsulation_class_in_handler.assert_called_once_with("ML-KEM-768")
        # Also assert that encap_secret was called on the instance with the correct public key
        mock_kem_instance.encap_secret.assert_called_once_with(mock_pqc_pk_correct_size)
        mock_key_encapsulation_class_in_handler.reset_mock() # Reset for the next call

        suite_config_kyber1024 = { "id": "X25519_KYBER1024_AES256GCM", # Example, assuming 1024 is valid
                                   "pqc_kem_algorithm": "ML-KEM-1024",
                                   # other params...
                                 }
        hybrid_handler.encrypt_content("plaintext", suite_config_kyber1024, key_material_encrypt, mock_fava_config)
        mock_key_encapsulation_class_in_handler.assert_called_with("ML-KEM-1024")
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.KeyEncapsulation')
    def test_tp_dar_hph_005_pqc_kem_encapsulation(self, mock_key_encapsulation_class_in_handler, hybrid_handler, mock_fava_config):
        plaintext = "test data"
        pqc_pk_bytes = b"mock_pqc_public_key_for_encap_test"
        
        key_material_encrypt = {
            "classical_public_key": MockX25519PublicKey(b"mock_classical_pk_bytes"), # Needed for full call
            "pqc_public_key": pqc_pk_bytes
        }
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM",
            "pqc_kem_algorithm": "ML-KEM-768", # Must be a supported one
            "classical_kem_algorithm": "X25519",
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }

        # Configure the mock KeyEncapsulation instance that will be created inside encrypt_content
        mock_kem_instance = mock_key_encapsulation_class_in_handler.return_value
        # MLKEMBridge.encap_secret returns (shared_secret, ciphertext)
        mock_kem_instance.encap_secret.return_value = (b"mock_pqc_ss_from_encap", b"mock_pqc_ct_from_encap")

        hybrid_handler.encrypt_content(plaintext, suite_config, key_material_encrypt, mock_fava_config)

        # Assert that KeyEncapsulation was instantiated with the correct KEM name
        mock_key_encapsulation_class_in_handler.assert_called_with("ML-KEM-768")
        # Assert that encap_secret was called on the instance with the correct public key
        mock_kem_instance.encap_secret.assert_called_once_with(pqc_pk_bytes)
        
        # Further assertions could check if the returned values are used,
        # but that overlaps with test_tp_dar_hph_006 for KDF input.
        # For this test, focusing on the call to encapsulate_secret is key.
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.HKDFExpand') # Path to HKDF in handler module
    @mock.patch('fava.crypto.handlers.KeyEncapsulation') # Mock KeyEncapsulation used within encrypt_content
    def test_tp_dar_hph_006_hybrid_kem_symmetric_key_derivation(self, mock_key_encapsulation_class, mock_hkdf_class_in_handler, hybrid_handler, mock_fava_config):
        # Isolate KDF step. Assert mock_hkdf_class_in_handler.return_value.derive called with concatenated secrets.
        
        # Setup mock values
        mock_classical_ss = b"fixed_classical_ss_for_hkdf_test"
        mock_pqc_ss = b"fixed_pqc_ss_for_hkdf_test"
        expected_combined_secret = mock_classical_ss + mock_pqc_ss
        
        # Mock key material for encrypt_content
        # These need to be valid sizes if not fully mocked deeper
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes_for_hkdf")
        mock_pqc_pk_correct_size = b'C' * 1184
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk_correct_size
        }
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM",
            "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519", # Needed by handler
            "symmetric_algorithm": "AES256GCM", # Needed by handler
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512" # Important for HKDF mock
        }

        # Configure the KeyEncapsulation mock (for PQC KEM part)
        mock_pqc_kem_instance = mock_key_encapsulation_class.return_value
        mock_pqc_kem_instance.encap_secret.return_value = (mock_pqc_ss, b"mock_pqc_ct_for_hkdf")

        # Configure the HKDFExpand mock (the actual UUT interaction point for this test)
        mock_hkdf_instance = mock_hkdf_class_in_handler.return_value
        mock_hkdf_instance.derive.return_value = b"k" * 32 # Ensure a 32-byte key for AES256GCM

        # To make classical_shared_secret predictable in encrypt_content,
        # we might need to patch X25519PrivateKey.generate() and exchange() if they are called.
        # For now, encrypt_content uses a placeholder: classical_shared_secret = b"mock_classical_ss_placeholder"
        # Let's use that placeholder value from the handler for now, and refine if the handler changes.
        # If the handler's classical_shared_secret changes, this test will need to adapt.
        # With the new MockX25519PublicKey init:
        # Ephemeral SK (during encrypt): self._private_bytes = b"default_generated_private_key_direct_in_generate" (prefix b"defau")
        # Its public key (ephem_pk): ephem_pk._public_bytes also b"default_generated_private_key_direct_in_generate" (prefix b"defau")
        # Recipient PK (classical_pk for encrypt): _public_bytes = b"mock_classical_pk_bytes_for_hkdf" (prefix b"mock_")
        # Exchange uses ephemeral SK's private_bytes and recipient PK's public_bytes:
        # sorted([b"defau", b"mock_"]) -> parts are [b"defau", b"mock_"]
        actual_classical_ss_from_mock = b"ss_x25519_" + b"defau" + b"_" + b"mock_"
        expected_combined_secret_for_derive = actual_classical_ss_from_mock + mock_pqc_ss

        # Call the UUT method
        hybrid_handler.encrypt_content("test_plaintext_for_hkdf", suite_config, key_material_encrypt, mock_fava_config)

        # Assertions
        # Check that HKDFExpand was instantiated correctly.
        mock_hkdf_class_in_handler.assert_called_once()
        
        # Get the arguments passed to HKDFExpand constructor (optional check)
        # hkdf_constructor_args = mock_hkdf_class_in_handler.call_args
        
        # Assert that the derive method of the HKDF instance was called with the correct combined secret.
        mock_hkdf_instance.derive.assert_called_once_with(expected_combined_secret_for_derive)

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.AESGCM') # Path to AESGCM in handler module
    @mock.patch('fava.crypto.handlers.os.urandom') # Mock os.urandom for predictable IV
    @mock.patch('fava.crypto.handlers.KeyEncapsulation') # Mock for KEM steps
    @mock.patch('fava.crypto.handlers.HKDFExpand') # Mock for KDF step
    def test_tp_dar_hph_007_aes_gcm_encryption_produces_tag_iv(
        self, mock_hkdf_class, mock_key_encap_class, mock_os_urandom,
        mock_aesgcm_class_in_handler, hybrid_handler, mock_fava_config
    ):
        # Isolate AES step. Assert mock_aesgcm_class_in_handler.return_value.encryptor called.
        # Assert ciphertext, IV, tag are produced and used in the bundle.

        plaintext_str = "secret symmetric data"
        mock_derived_symmetric_key = b'k' * 32 # Expected input to AESGCM
        mock_iv = b'i' * 12
        mock_actual_ciphertext = b'c' * len(plaintext_str) # Ciphertext part
        mock_auth_tag = b't' * 16
        
        # Configure mocks that lead up to AESGCM
        # KEM part (to produce pqc_shared_secret)
        mock_pqc_kem_instance = mock_key_encap_class.return_value
        mock_pqc_kem_instance.encap_secret.return_value = (b"mock_pqc_ss_for_aes", b"mock_pqc_ct_for_aes")

        # KDF part (to produce symmetric_key)
        mock_hkdf_instance = mock_hkdf_class.return_value
        mock_hkdf_instance.derive.return_value = mock_derived_symmetric_key

        # os.urandom for IV
        mock_os_urandom.return_value = mock_iv

        # Configure AESGCM mock (the focus of this test)
        mock_aesgcm_instance = mock_aesgcm_class_in_handler.return_value
        # AESGCM object itself has the encrypt method.
        # It returns ciphertext_with_tag. The tag is not a separate attribute of the encryptor for this API.
        mock_aesgcm_instance.encrypt.return_value = mock_actual_ciphertext + mock_auth_tag


        # Prepare inputs for encrypt_content
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519", "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }
        key_material_encrypt = {
            "classical_public_key": MockX25519PublicKey(b"mock_classical_pk_for_aes"),
            "pqc_public_key": b'P' * 1184 # Correct size
        }

        # Patch EncryptedFileBundle to inspect its population
        with mock.patch('fava.crypto.handlers.EncryptedFileBundle', autospec=True) as mock_bundle_class:
            mock_bundle_instance = mock_bundle_class.return_value

            # Call the UUT method
            # Note: encrypt_content currently returns bundle.symmetric_ciphertext.
            # We are more interested in how the mock_bundle_instance is populated.
            _ = hybrid_handler.encrypt_content(plaintext_str, suite_config, key_material_encrypt, mock_fava_config)

            # Assertions
            # 1. AESGCM was instantiated with the derived symmetric key
            mock_aesgcm_class_in_handler.assert_called_once_with(mock_derived_symmetric_key)
            
            # 2. AESGCM's encrypt method was called directly on the instance
            mock_aesgcm_instance.encrypt.assert_called_once_with(mock_iv, plaintext_str.encode('utf-8'), associated_data=None)
            # The previous diff had mock_aesgcm_instance.encryptor.assert_called_once() which is incorrect.
            # The call to encrypt is directly on mock_aesgcm_instance.

            # 3. Assertions on the (mocked) EncryptedFileBundle instance
            # Check that the IV, ciphertext, and tag from AESGCM were assigned to the bundle
            assert mock_bundle_instance.symmetric_iv == mock_iv
            assert mock_bundle_instance.symmetric_ciphertext == mock_actual_ciphertext
            assert mock_bundle_instance.symmetric_auth_tag == mock_auth_tag
            
            # Check other bundle fields if necessary (e.g., KEM ciphertexts)
            assert mock_bundle_instance.pqc_kem_ciphertext == b"mock_pqc_ct_for_aes"
            # classical_kem_ciphertext_for_bundle is classical_ephemeral_sk.public_key().public_bytes(...)
            # classical_ephemeral_sk.public_key() is an instance of MockX25519PublicKey
            # initialized with classical_ephemeral_sk._private_bytes.
            # Default ephemeral SK has _private_bytes = b"default_generated_private_key_direct_in_generate".
            expected_classical_kem_ct = b"default_generated_private_key_direct_in_generate"
            assert mock_bundle_instance.classical_kem_ciphertext == expected_classical_kem_ct
            assert mock_bundle_instance.format_identifier == "FAVA_PQC_HYBRID_V1"
            assert mock_bundle_instance.suite_id == suite_config["id"]

    @pytest.mark.error_handling
    @pytest.mark.critical_path
    def test_tp_dar_hph_008_decrypt_fails_wrong_key(self, hybrid_handler, mock_fava_config):
        from fava.crypto.exceptions import DecryptionError # Import the specific exception

        plaintext = "secret data for wrong key test"
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519", "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }

        # Key Material A (for encryption)
        # For simplicity, we'll rely on the default mock behaviors for generating ephemeral keys
        # during encryption. The public keys provided here are for the recipient.
        key_material_encrypt_A = {
            "classical_public_key": MockX25519PublicKey(b"classical_pk_A_recipient"),
            "pqc_public_key": b'A_pqc_pk_recipient' * (1184 // len(b'A_pqc_pk_recipient')) # ML-KEM-768 size
        }
        
        # Encrypt content with Key Material A's public keys
        encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt_A, mock_fava_config
        )

        # Key Material B (for decryption - these are WRONG private keys for the bundle)
        # Ensure these private key bytes are different from what would correspond to key_material_encrypt_A
        # The enhanced mocks for exchange and decap_secret will use these differing bytes.
        key_material_decrypt_B = {
            "classical_private_key": MockX25519PrivateKey(b"classical_sk_B_DIFFERENT"),
            "pqc_private_key": b'B_pqc_sk_DIFFERENT' * (2400 // len(b'B_pqc_sk_DIFFERENT')) # ML-KEM-768 SK size
        }

        # Attempt to decrypt with Key Material B (wrong keys)
        with pytest.raises(DecryptionError) as excinfo:
            hybrid_handler.decrypt_content(
                encrypted_bundle_bytes, suite_config, key_material_decrypt_B, mock_fava_config
            )
        
        # Optional: Check the error message if needed, e.g., contains "Simulated AESGCM InvalidTag"
        # This depends on the exact error raised by MockAESGCM.decrypt
        assert "Simulated AESGCM InvalidTag" in str(excinfo.value) or \
               "Decryption failed due to value error" in str(excinfo.value) # Handler wraps it

    @pytest.mark.error_handling
    @pytest.mark.bundle_format
    def test_tp_dar_hph_009_decrypt_fails_tampered_ciphertext_tag(self, hybrid_handler, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle
        from fava.crypto.exceptions import DecryptionError

        plaintext = "data to test tampering"
        suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        
        # Use consistent mock keys for this test to ensure KEM/KDF parts are stable
        mock_classical_pk = MockX25519PublicKey(b"classical_pk_for_tamper_test")
        mock_pqc_pk = b'P' * 1184
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk
        }
        mock_classical_sk = MockX25519PrivateKey(b"classical_pk_for_tamper_test") # Same bytes as PK for mock commutativity
        mock_pqc_sk = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct # Use the "correct" mock SK
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk,
            "pqc_private_key": mock_pqc_sk
        }

        # 1. Encrypt normally to get a valid bundle
        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt, mock_fava_config
        )
        
        # Scenario 1: Tamper symmetric_ciphertext
        bundle_tamper_ct = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_ct.symmetric_ciphertext) > 0:
            original_byte = bundle_tamper_ct.symmetric_ciphertext[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_ct.symmetric_ciphertext = bytes([tampered_byte]) + bundle_tamper_ct.symmetric_ciphertext[1:]
        else: # Handle empty ciphertext case if it occurs, though unlikely for non-empty plaintext
            bundle_tamper_ct.symmetric_ciphertext = b"tampered"
        tampered_ct_bytes = bundle_tamper_ct.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_ct:
            hybrid_handler.decrypt_content(tampered_ct_bytes, suite_config, key_material_decrypt, mock_fava_config)
        # AESGCM decrypt should raise an error if ciphertext/tag don't match.
        # Our MockAESGCM raises ValueError("Simulated AESGCM InvalidTag: Decryption key does not match encryption key.")
        # if keys mismatch, but for actual data tampering, the real AESGCM would raise InvalidTag.
        # The handler wraps this in DecryptionError.
        assert "Decryption failed due to value error" in str(excinfo_ct.value) or "InvalidTag" in str(excinfo_ct.value)


        # Scenario 2: Tamper symmetric_auth_tag
        bundle_tamper_tag = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_tag.symmetric_auth_tag) > 0:
            original_byte = bundle_tamper_tag.symmetric_auth_tag[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_tag.symmetric_auth_tag = bytes([tampered_byte]) + bundle_tamper_tag.symmetric_auth_tag[1:]
        else: # Handle empty tag case
            bundle_tamper_tag.symmetric_auth_tag = b"tampered_tag1234"
        tampered_tag_bytes = bundle_tamper_tag.to_bytes()
        
        with pytest.raises(DecryptionError) as excinfo_tag:
            hybrid_handler.decrypt_content(tampered_tag_bytes, suite_config, key_material_decrypt, mock_fava_config)
        assert "Decryption failed due to value error" in str(excinfo_tag.value) or "InvalidTag" in str(excinfo_tag.value)

    @pytest.mark.error_handling
    @pytest.mark.bundle_format
    def test_tp_dar_hph_010_decrypt_fails_corrupted_kem_ciphertext(self, hybrid_handler, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle
        from fava.crypto.exceptions import DecryptionError

        plaintext = "data for KEM corruption test"
        suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        
        # Consistent keys for encryption and subsequent decryption attempt
        # Recipient's public keys for encryption
        mock_classical_pk_recipient = MockX25519PublicKey(b"classical_pk_recipient_for_kem_corruption")
        # Ensure PQC PK is of correct size for ML-KEM-768 (1184 bytes)
        mock_pqc_pk_recipient_bytes = b'P_rcp' * (1184 // len(b'P_rcp')) + b'P' * (1184 % len(b'P_rcp'))
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk_recipient,
            "pqc_public_key": mock_pqc_pk_recipient_bytes
        }

        # Recipient's private keys for decryption
        # For mock commutativity and predictability with current mocks:
        # Classical SK's private_bytes should match the PK's public_bytes it's supposed to pair with.
        # The ephemeral classical key generated during encrypt() uses "default_generated_private_key_direct_in_generate".
        # So, for successful classical decryption, the recipient SK should be able to "exchange" with that.
        # Here, the classical_kem_ciphertext in the bundle *is* the ephemeral public key.
        # The classical_private_key in key_material_decrypt is the recipient's SK.
        mock_classical_sk_recipient = MockX25519PrivateKey(b"classical_pk_recipient_for_kem_corruption") # Matches PK for mock
        
        # For PQC, MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct is used by the mock decapsulate.
        # And MockOQS_KeyEncapsulation._mock_encapsulate_class produces (b"mock_kem_ct_class", b"mock_kem_ss_class")
        # So, for successful PQC decapsulation, the SK should be _correct_pqc_sk_for_mock_ct
        # and the CT should be b"mock_kem_ct_class".
        mock_pqc_sk_recipient_bytes = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk_recipient,
            "pqc_private_key": mock_pqc_sk_recipient_bytes
        }

        # 1. Encrypt normally to get a valid bundle
        # Ensure the mock PQC KEM produces its standard "correct" ciphertext for this path
        original_encap_mock = MockOQS_KeyEncapsulation._mock_encapsulate_class
        MockOQS_KeyEncapsulation._mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class"))
        
        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt, mock_fava_config
        )
        MockOQS_KeyEncapsulation._mock_encapsulate_class = original_encap_mock # Restore

        # Scenario 1: Tamper classical_kem_ciphertext
        bundle_tamper_classical_kem = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_classical_kem.classical_kem_ciphertext) > 0:
            original_byte = bundle_tamper_classical_kem.classical_kem_ciphertext[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_classical_kem.classical_kem_ciphertext = bytes([tampered_byte]) + bundle_tamper_classical_kem.classical_kem_ciphertext[1:]
        else:
            bundle_tamper_classical_kem.classical_kem_ciphertext = b"tampered_classical_kem_ct"
        tampered_classical_kem_bytes = bundle_tamper_classical_kem.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_classical:
            hybrid_handler.decrypt_content(tampered_classical_kem_bytes, suite_config, key_material_decrypt, mock_fava_config)
        # This should fail because the tampered classical KEM CT (ephemeral PK) leads to a different X25519 shared secret,
        # then a different symmetric key, causing MockAESGCM to raise an error.
        assert "Decryption failed due to value error" in str(excinfo_classical.value) or "InvalidTag" in str(excinfo_classical.value)


        # Scenario 2: Tamper pqc_kem_ciphertext
        bundle_tamper_pqc_kem = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_pqc_kem.pqc_kem_ciphertext) > 0:
            original_byte = bundle_tamper_pqc_kem.pqc_kem_ciphertext[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_pqc_kem.pqc_kem_ciphertext = bytes([tampered_byte]) + bundle_tamper_pqc_kem.pqc_kem_ciphertext[1:]
        else:
            bundle_tamper_pqc_kem.pqc_kem_ciphertext = b"tampered_pqc_kem_ct"
        tampered_pqc_kem_bytes = bundle_tamper_pqc_kem.to_bytes()
        
        with pytest.raises(DecryptionError) as excinfo_pqc:
            hybrid_handler.decrypt_content(tampered_pqc_kem_bytes, suite_config, key_material_decrypt, mock_fava_config)
        # This should fail because the tampered PQC KEM CT leads to MockOQS_KeyEncapsulation.decap_secret
        # returning a "wrong" shared secret (due to its side_effect), then a different symmetric key,
        # causing MockAESGCM to raise an error.
        assert "Decryption failed due to value error" in str(excinfo_pqc.value) or "InvalidTag" in str(excinfo_pqc.value)

    @pytest.mark.bundle_format
    @pytest.mark.critical_path
    def test_tp_dar_hph_011_encrypted_bundle_parser(self, mock_fava_config): # mock_fava_config not strictly needed but good for consistency
        from fava.core.encrypted_file_bundle import EncryptedFileBundle

        # 1. Create an EncryptedFileBundle instance with known values
        original_bundle = EncryptedFileBundle()
        original_bundle.format_identifier = "FAVA_PQC_HYBRID_V1"
        original_bundle.suite_id = "X25519_KYBER768_AES256GCM_TEST" # Test-specific suite ID
        original_bundle.classical_kem_ciphertext = b"classical_ct_test_bytes"
        original_bundle.pqc_kem_ciphertext = b"pqc_ct_test_bytes_longer"
        original_bundle.symmetric_iv = b"iv_12_bytes123"
        original_bundle.symmetric_ciphertext = b"encrypted_symmetric_data_payload"
        original_bundle.symmetric_auth_tag = b"auth_tag_16bytes"
        # format_version is not part of current serialization, so not tested here.

        # 2. Serialize it to bytes
        serialized_bundle_bytes = original_bundle.to_bytes()

        # 3. Deserialize it back into an object
        parsed_bundle = EncryptedFileBundle.from_bytes(serialized_bundle_bytes)

        # 4. Assert all fields match the original values
        assert parsed_bundle.format_identifier == original_bundle.format_identifier
        assert parsed_bundle.suite_id == original_bundle.suite_id
        assert parsed_bundle.classical_kem_ciphertext == original_bundle.classical_kem_ciphertext
        assert parsed_bundle.pqc_kem_ciphertext == original_bundle.pqc_kem_ciphertext
        assert parsed_bundle.symmetric_iv == original_bundle.symmetric_iv
        assert parsed_bundle.symmetric_ciphertext == original_bundle.symmetric_ciphertext
        assert parsed_bundle.symmetric_auth_tag == original_bundle.symmetric_auth_tag

        # Test edge case: empty fields (except identifiers which usually have a value)
        empty_bundle = EncryptedFileBundle()
        empty_bundle.format_identifier = "EMPTY_TEST_V0" # Must not be empty string for encoding
        empty_bundle.suite_id = "EMPTY_SUITE_ID"   # Must not be empty string for encoding
        # Other fields are b"" by default

        serialized_empty_bundle = empty_bundle.to_bytes()
        parsed_empty_bundle = EncryptedFileBundle.from_bytes(serialized_empty_bundle)

        assert parsed_empty_bundle.format_identifier == empty_bundle.format_identifier
        assert parsed_empty_bundle.suite_id == empty_bundle.suite_id
        assert parsed_empty_bundle.classical_kem_ciphertext == b""
        assert parsed_empty_bundle.pqc_kem_ciphertext == b""
        assert parsed_empty_bundle.symmetric_iv == b""
        assert parsed_empty_bundle.symmetric_ciphertext == b""
        assert parsed_empty_bundle.symmetric_auth_tag == b""

        # Test error case: insufficient data for parsing
        with pytest.raises(ValueError, match="Data too short to read length prefix."):
            EncryptedFileBundle.from_bytes(b"\x01\x00\x00") # Too short for even one length

        with pytest.raises(ValueError, match="Data too short to read field content."):
            EncryptedFileBundle.from_bytes(b"\x05\x00\x00\x00abc") # Length 5, data 'abc' (len 3)

    @pytest.mark.error_handling
    @pytest.mark.bundle_format
    @pytest.mark.config_dependent
    def test_tp_dar_hph_012_decrypt_fails_mismatched_suite_format_id(self, hybrid_handler, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle
        from fava.crypto.exceptions import DecryptionError

        plaintext = "data for suite/format ID mismatch test"
        
        # Use the active suite config for encryption and as the 'expected' during decryption
        correct_suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        
        # Consistent keys for encryption
        mock_classical_pk_recipient = MockX25519PublicKey(b"classical_pk_recipient_for_mismatch_test")
        mock_pqc_pk_recipient_bytes = b'P_rcp_mm' * (1184 // len(b'P_rcp_mm')) + b'P' * (1184 % len(b'P_rcp_mm'))
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk_recipient,
            "pqc_public_key": mock_pqc_pk_recipient_bytes
        }
        # Decryption keys (needed for the handler to proceed past KEM decapsulation)
        mock_classical_sk_recipient = MockX25519PrivateKey(b"classical_pk_recipient_for_mismatch_test")
        mock_pqc_sk_recipient_bytes = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk_recipient,
            "pqc_private_key": mock_pqc_sk_recipient_bytes
        }

        # 1. Encrypt normally to get a valid bundle
        original_encap_mock = MockOQS_KeyEncapsulation._mock_encapsulate_class
        MockOQS_KeyEncapsulation._mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class"))
        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, correct_suite_config, key_material_encrypt, mock_fava_config
        )
        MockOQS_KeyEncapsulation._mock_encapsulate_class = original_encap_mock


        # Scenario 1: Mismatched suite_id
        bundle_mismatched_suite = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        bundle_mismatched_suite.suite_id = "DIFFERENT_SUITE_ID_XYZ"
        mismatched_suite_bytes = bundle_mismatched_suite.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_suite:
            hybrid_handler.decrypt_content(mismatched_suite_bytes, correct_suite_config, key_material_decrypt, mock_fava_config)
        assert f"Mismatched suite ID. Bundle: DIFFERENT_SUITE_ID_XYZ, Config: {correct_suite_config['id']}" in str(excinfo_suite.value)

        # Scenario 2: Mismatched format_identifier
        bundle_mismatched_format = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        bundle_mismatched_format.format_identifier = "FAVA_PQC_HYBRID_V0_OLD" # Different from handler.EXPECTED_FORMAT_IDENTIFIER
        mismatched_format_bytes = bundle_mismatched_format.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_format:
            hybrid_handler.decrypt_content(mismatched_format_bytes, correct_suite_config, key_material_decrypt, mock_fava_config)
        assert f"Unsupported bundle format: FAVA_PQC_HYBRID_V0_OLD" in str(excinfo_format.value)


@pytest.mark.usefixtures("mock_fava_config")
class TestGpgHandler:
    """
    Tests for 5.3. GpgHandler (fava.crypto.handlers.GpgHandler)
    """
    @pytest.fixture
    def gpg_handler(self):
        def gpg_handler(self):
            from fava.crypto.handlers import GpgHandler # Assuming UUT
            return GpgHandler()
            # pytest.skip("GpgHandler not implemented yet for instantiation.") # Unskipped
            # return None # Unskipped
    
        @pytest.mark.gpg_compatibility
        @pytest.mark.config_dependent
        def test_tp_dar_gpgh_001_can_handle_gpg(self, gpg_handler, mock_fava_config):
            from fava.crypto.handlers import GpgHandler # For GPG_ARMORED_MAGIC_STRING etc.
            mock_fava_config.pqc_fallback_to_classical_gpg = True
            
            # Test by extension
            assert gpg_handler.can_handle("data.bc.gpg", None, mock_fava_config) is True
            assert gpg_handler.can_handle("data.bc.GPG", None, mock_fava_config) is True # Case-insensitive check in handler
            assert gpg_handler.can_handle("data.bc.pqc_hybrid_fava", None, mock_fava_config) is False
            assert gpg_handler.can_handle("data.txt", None, mock_fava_config) is False
    
            # Test by binary magic bytes
            assert gpg_handler.can_handle("data.txt", b'\x85\x02_some_other_data', mock_fava_config) is True
            assert gpg_handler.can_handle("data.bin", b'\x99_compressed_data_follows', mock_fava_config) is True
            
            # Test by armored magic string
            assert gpg_handler.can_handle("message.asc", GpgHandler.GPG_ARMORED_MAGIC_STRING + b" rest of message", mock_fava_config) is True
            
            # Test fallback disabled
            mock_fava_config.pqc_fallback_to_classical_gpg = False
            assert gpg_handler.can_handle("data.bc.gpg", None, mock_fava_config) is False
            assert gpg_handler.can_handle("data.txt", b'\x85\x02...', mock_fava_config) is False
            
            # Test no content peek and wrong extension
            mock_fava_config.pqc_fallback_to_classical_gpg = True
            assert gpg_handler.can_handle("data.txt", None, mock_fava_config) is False
            # pytest.skip("Test not implemented.") # Unskipped
    
        @pytest.mark.gpg_compatibility
        @pytest.mark.critical_path
        @mock.patch('subprocess.run')
        def test_tp_dar_gpgh_002_gpg_decrypt_success(self, mock_subprocess_run, gpg_handler, mock_fava_config):
            from fava.crypto import exceptions # For DecryptionError
            mock_fava_config.gpg_options = "--custom-option --another"
            expected_gpg_cmd = ['gpg', '--decrypt', '--batch', '--yes', '--quiet', '--no-tty', '--custom-option', '--another']
            
            mock_subprocess_run.return_value = mock.Mock(stdout=b"GPG decrypted data successfully!", returncode=0, stderr=b"")
            
            encrypted_data = b"gpg_encrypted_binary_bytes"
            decrypted = gpg_handler.decrypt_content(encrypted_data, mock_fava_config, None)
            
            assert decrypted == "GPG decrypted data successfully!"
            mock_subprocess_run.assert_called_once_with(
                expected_gpg_cmd,
                input=encrypted_data,
                capture_output=True,
                check=False
            )
            # pytest.skip("Test not implemented.") # Unskipped
    
        @pytest.mark.gpg_compatibility
        @pytest.mark.error_handling
        @mock.patch('subprocess.run')
        def test_tp_dar_gpgh_003_gpg_decrypt_failure(self, mock_subprocess_run, gpg_handler, mock_fava_config):
            from fava.crypto.exceptions import DecryptionError # Import specific exception
            
            # Scenario 1: GPG command returns error
            mock_subprocess_run.return_value = mock.Mock(stdout=b"Some output but failed.", returncode=2, stderr=b"gpg: decryption failed: No secret key")
            
            with pytest.raises(DecryptionError) as excinfo:
                gpg_handler.decrypt_content(b"bad_gpg_data_no_key", mock_fava_config, None)
            assert "GPG decryption failed (exit code 2)" in str(excinfo.value)
            assert "gpg: decryption failed: No secret key" in str(excinfo.value)
    
            # Scenario 2: GPG command not found
            mock_subprocess_run.reset_mock() # Reset for the next scenario
            mock_subprocess_run.side_effect = FileNotFoundError("gpg command not found test")
            with pytest.raises(FileNotFoundError) as fnf_excinfo: # Catch FileNotFoundError directly
                gpg_handler.decrypt_content(b"any_data", mock_fava_config, None)
            assert "The 'gpg' command-line tool was not found" in str(fnf_excinfo.value)
            
            # Scenario 3: GPG output cannot be decoded
            mock_subprocess_run.reset_mock()
            mock_subprocess_run.side_effect = None # Clear side_effect
            mock_subprocess_run.return_value = mock.Mock(stdout=b'\xff\xfe', returncode=0, stderr=b"") # Invalid UTF-8 sequence
            with pytest.raises(DecryptionError) as decode_excinfo:
                gpg_handler.decrypt_content(b"data_producing_bad_output", mock_fava_config, None)
            assert "Failed to decode GPG output as UTF-8" in str(decode_excinfo.value)
            # pytest.skip("Test not implemented.") # Unskipped

@pytest.mark.usefixtures("mock_fava_config")
class TestCryptoServiceLocator:
    """
    Tests for 5.4. CryptoServiceLocator (fava.crypto.locator.CryptoServiceLocator)
    """
    @pytest.fixture
    def mock_hybrid_handler_instance(self):
        handler = mock.Mock(spec_set=['can_handle', 'encrypt_content', 'decrypt_content', 'name']) # Add methods as needed
        handler.name = "HybridPqcHandler" # For identification
        return handler

    @pytest.fixture
    def mock_gpg_handler_instance(self):
        handler = mock.Mock(spec_set=['can_handle', 'decrypt_content', 'name'])
        handler.name = "GpgHandler"
        return handler

    @pytest.fixture
    def crypto_locator(self, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config): # Added mock_fava_config
        from fava.crypto.locator import CryptoServiceLocator # Assuming UUT
        # Initialize with specific mock handlers for testing order and selection
        return CryptoServiceLocator(handlers=[mock_hybrid_handler_instance, mock_gpg_handler_instance], app_config=mock_fava_config)
        # pytest.skip("CryptoServiceLocator not implemented yet for instantiation.") # Unskipped
        # return None # Unskipped


    @pytest.mark.config_dependent
    @pytest.mark.critical_path
    def test_tp_dar_csl_001_selects_pqc_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = True
        mock_gpg_handler_instance.can_handle.return_value = False # Ensure GPG handler says no
        mock_fava_config.pqc_data_at_rest_enabled = True # Ensure PQC is generally enabled

        handler = crypto_locator.get_handler_for_file("file.pqc_hybrid_fava", b"FAVA_PQC_HYBRID_V1_PEEK", mock_fava_config)
        assert handler is mock_hybrid_handler_instance
        # Assert can_handle was called on the PQC handler with correct args
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("file.pqc_hybrid_fava", b"FAVA_PQC_HYBRID_V1_PEEK", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_not_called() # Should not be called if PQC handler matches first
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.config_dependent
    @pytest.mark.gpg_compatibility
    def test_tp_dar_csl_002_selects_gpg_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = False # PQC handler says no
        mock_gpg_handler_instance.can_handle.return_value = True   # GPG handler says yes
        mock_fava_config.pqc_fallback_to_classical_gpg = True    # GPG fallback enabled

        handler = crypto_locator.get_handler_for_file("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)
        assert handler is mock_gpg_handler_instance
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_called_once_with("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.config_dependent
    def test_tp_dar_csl_003_handler_prioritization(self, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config): # Added mock_hybrid_handler_instance, mock_gpg_handler_instance
        from fava.crypto.locator import CryptoServiceLocator
        # Test that HybridPqcHandler is checked before GpgHandler if both can handle.
        
        mock_hybrid_handler_instance.can_handle.return_value = True
        mock_gpg_handler_instance.can_handle.return_value = True # Both can handle
        mock_fava_config.pqc_data_at_rest_enabled = True
        mock_fava_config.pqc_fallback_to_classical_gpg = True

        # Locator is initialized with [mock_hybrid_handler_instance, mock_gpg_handler_instance]
        # So, mock_hybrid_handler_instance should be selected first.
        locator = CryptoServiceLocator(handlers=[mock_hybrid_handler_instance, mock_gpg_handler_instance], app_config=mock_fava_config)
        
        handler = locator.get_handler_for_file("some_file.any_ext", b"some_peek_data", mock_fava_config)
        assert handler is mock_hybrid_handler_instance
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("some_file.any_ext", b"some_peek_data", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_not_called() # GPG should not be called due to prioritization
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.error_handling
    def test_tp_dar_csl_004_no_handler_matches(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = False # PQC handler says no
        mock_gpg_handler_instance.can_handle.return_value = False   # GPG handler says no
        # Config for pqc_fallback_to_classical_gpg doesn't matter if GPG can_handle is False.
        # pqc_data_at_rest_enabled also doesn't matter if PQC can_handle is False.

        result = crypto_locator.get_handler_for_file("unknown.file", b"unknown_peek_data", mock_fava_config)
        assert result is None
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("unknown.file", b"unknown_peek_data", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_called_once_with("unknown.file", b"unknown_peek_data", mock_fava_config)
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.config_dependent
    def test_tp_dar_csl_005_get_pqc_encrypt_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_fava_config):
        suite_config = { "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768" } # Added id to suite_config
        
        # Scenario 1: PQC enabled
        mock_fava_config.pqc_data_at_rest_enabled = True
        handler = crypto_locator.get_pqc_encrypt_handler(suite_config, mock_fava_config)
        assert handler is mock_hybrid_handler_instance # Should return the PQC handler instance

        # Scenario 2: PQC disabled
        mock_fava_config.pqc_data_at_rest_enabled = False
        handler_disabled = crypto_locator.get_pqc_encrypt_handler(suite_config, mock_fava_config)
        assert handler_disabled is None
        # pytest.skip("Test not implemented.") # Unskipped


@pytest.mark.usefixtures("mock_fava_config", "mock_crypto_libs")
class TestFavaLedgerIntegration:
    """
    Tests for 5.5. FavaLedger Integration (fava.core.ledger.FavaLedger)
    @pytest.fixture
    def fava_ledger(self, mock_fava_config):
        from fava.core.ledger import FavaLedger
        # The FavaLedger __init__ now accepts FavaOptions directly for beancount_file_path for testing.
        ledger = FavaLedger(mock_fava_config)
        ledger.crypto_service_locator = mock.Mock(spec=CryptoServiceLocator) # Mock the locator after instantiation
        return ledger
        # pytest.skip("FavaLedger not implemented yet for instantiation.") # Unskipped
        # return None # Unskipped

    @pytest.mark.key_management
    @pytest.mark.critical_path
    @mock.patch('fava.core.ledger.PROMPT_USER_FOR_PASSPHRASE_SECURELY')
    @mock.patch('fava.core.ledger.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT')
    @mock.patch('fava.crypto.keys.derive_kem_keys_from_passphrase') # Patched at source
    @mock.patch('fava.crypto.keys.load_keys_from_external_file') # Patched at source
    def test_tp_dar_fl_001_get_key_material_decrypt_passphrase(
        self, mock_load_keys, mock_derive_keys, mock_get_salt,
        mock_prompt_pass, fava_ledger, mock_fava_config
    ):
        file_path_context = "test_file.pqc"
        operation_type = "decrypt"
        
        # Scenario 1: PASSPHRASE_DERIVED
        mock_fava_config.pqc_key_management_mode = "PASSPHRASE_DERIVED"
        mock_prompt_pass.return_value = "test_passphrase"
        mock_get_salt.return_value = b"a_salt_for_context_16b"
        
        # Mock return for derive_kem_keys_from_passphrase: ( (classical_pk, classical_sk), (pqc_pk, pqc_sk) )
        # For decryption, we need the private keys (index 1 of each tuple)
        mock_classical_sk_bytes = b"mock_classical_sk_bytes_derived"
        mock_pqc_sk_bytes = b"mock_pqc_sk_bytes_derived"
        mock_derive_keys.return_value = (
            (b"mock_classical_pk_derived", mock_classical_sk_bytes),
            (b"mock_pqc_pk_derived", mock_pqc_sk_bytes)
        )

        key_material = fava_ledger._get_key_material_for_operation(file_path_context, operation_type)
        
        mock_prompt_pass.assert_called_once_with(f"Enter passphrase for {file_path_context} ({operation_type}):")
        mock_get_salt.assert_called_once_with(f"{file_path_context}_{operation_type}_salt")
        
        active_suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        mock_derive_keys.assert_called_once_with(
            "test_passphrase",
            b"a_salt_for_context_16b",
            active_suite_config.get("pbkdf_algorithm_for_passphrase"),
            active_suite_config.get("kdf_algorithm_for_ikm_from_pbkdf"),
            active_suite_config.get("classical_kem_algorithm"),
            active_suite_config.get("pqc_kem_algorithm")
        )
        assert key_material == {
            "classical_private_key": mock_classical_sk_bytes,
            "pqc_private_key": mock_pqc_sk_bytes
        }
        mock_load_keys.assert_not_called() # Ensure external file loading wasn't called

        # Reset mocks for Scenario 2
        mock_prompt_pass.reset_mock()
        mock_get_salt.reset_mock()
        mock_derive_keys.reset_mock()

        # Scenario 2: EXTERNAL_FILE
        mock_fava_config.pqc_key_management_mode = "EXTERNAL_FILE"
        mock_fava_config.pqc_key_file_paths = {"classical_private": "c.key", "pqc_private": "p.key"}
        
        mock_classical_sk_ext_bytes = b"mock_classical_sk_bytes_external"
        mock_pqc_sk_ext_bytes = b"mock_pqc_sk_bytes_external"
        mock_load_keys.return_value = (
            (b"mock_classical_pk_ext", mock_classical_sk_ext_bytes),
            (b"mock_pqc_pk_ext", mock_pqc_sk_ext_bytes)
        )

        key_material_ext = fava_ledger._get_key_material_for_operation(file_path_context, operation_type)
        mock_load_keys.assert_called_once_with(mock_fava_config.pqc_key_file_paths)
        assert key_material_ext == {
            "classical_private_key": mock_classical_sk_ext_bytes,
            "pqc_private_key": mock_pqc_sk_ext_bytes
        }
        mock_derive_keys.assert_not_called() # Ensure passphrase derivation wasn't called
        # pytest.skip("Test not implemented.") # Unskipped

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @mock.patch('fava.core.ledger.WRITE_BYTES_TO_FILE')
    @mock.patch('fava.core.ledger.READ_BYTES_FROM_FILE')
    @mock.patch('fava.core.ledger.parse_beancount_file_from_source')
    @mock.patch('fava.core.ledger.PROMPT_USER_FOR_PASSPHRASE_SECURELY') # For _get_key_material
    @mock.patch('fava.core.ledger.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT') # For _get_key_material
    @mock.patch('fava.crypto.keys.derive_kem_keys_from_passphrase') # For _get_key_material
    def test_tp_dar_fl_002_save_reload_pqc_encrypted_file(
        self, mock_derive_keys_for_get_material, mock_get_salt_for_get_material,
        mock_prompt_pass_for_get_material,
        mock_beancount_parser, mock_read_bytes, mock_write_bytes,
        fava_ledger, mock_fava_config, mock_crypto_libs # mock_crypto_libs for handlers
    ):
        plaintext_data_str = "ledger_content_to_encrypt_and_reload"
        file_path = "test_ledger.bc.pqc_fava"
        key_context = "test_ledger_context" # For _get_key_material

        # --- Setup for save_file_pqc ---
        mock_fava_config.pqc_data_at_rest_enabled = True
        mock_fava_config.pqc_key_management_mode = "PASSPHRASE_DERIVED" # Consistent mode
        
        # Mock key material derivation for encryption
        mock_classical_pk_bytes_save = b"classical_pk_for_save"
        mock_pqc_pk_bytes_save = b"pqc_pk_for_save_1184b" + b"A" * (1184 - len(b"pqc_pk_for_save_1184b"))
        mock_derive_keys_for_get_material.return_value = (
            (mock_classical_pk_bytes_save, b"classical_sk_for_save"),
            (mock_pqc_pk_bytes_save, b"pqc_sk_for_save")
        )
        mock_prompt_pass_for_get_material.return_value = "save_passphrase"
        mock_get_salt_for_get_material.return_value = b"salt_for_save_op"

        # Mock the PQC encrypt handler on the locator
        mock_encrypt_handler = mock.Mock()
        fava_ledger.crypto_service_locator.get_pqc_encrypt_handler.return_value = mock_encrypt_handler
        mock_encrypted_bundle_bytes = b"super_secret_encrypted_bundle_bytes"
        mock_encrypt_handler.encrypt_content.return_value = mock_encrypted_bundle_bytes
        
        # Action: Save
        fava_ledger.save_file_pqc(file_path, plaintext_data_str, key_context=key_context)

        # Assertions for save
        mock_prompt_pass_for_get_material.assert_called_with(f"Enter passphrase for {key_context} (encrypt):")
        mock_get_salt_for_get_material.assert_called_with(f"{key_context}_encrypt_salt")
        
        active_suite_config_save = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        fava_ledger.crypto_service_locator.get_pqc_encrypt_handler.assert_called_once_with(active_suite_config_save, mock_fava_config)
        
        expected_key_material_encrypt = {
            "classical_public_key": mock_classical_pk_bytes_save,
            "pqc_public_key": mock_pqc_pk_bytes_save
        }
        mock_encrypt_handler.encrypt_content.assert_called_once_with(
            plaintext_data_str,
            active_suite_config_save,
            expected_key_material_encrypt,
            mock_fava_config
        )
        mock_write_bytes.assert_called_once_with(file_path, mock_encrypted_bundle_bytes)

        # --- Setup for load_file ---
        mock_read_bytes.return_value = mock_encrypted_bundle_bytes # What load_file will read
        
        # Mock key material derivation for decryption (can be different if salt/context changes, but keep simple for now)
        mock_classical_sk_bytes_load = b"classical_sk_for_load"
        mock_pqc_sk_bytes_load = b"pqc_sk_for_load_2400b" + b"S" * (2400 - len(b"pqc_sk_for_load_2400b"))
        # Reset and reconfigure derive_keys for the "decrypt" operation
        mock_derive_keys_for_get_material.reset_mock()
        mock_derive_keys_for_get_material.return_value = (
            (b"classical_pk_for_load", mock_classical_sk_bytes_load),
            (b"pqc_pk_for_load", mock_pqc_sk_bytes_load)
        )
        mock_prompt_pass_for_get_material.reset_mock()
        mock_prompt_pass_for_get_material.return_value = "load_passphrase" # Could be same or different
        mock_get_salt_for_get_material.reset_mock()
        mock_get_salt_for_get_material.return_value = b"salt_for_load_op"


        # Mock the handler returned by locator for decryption
        mock_decrypt_handler = mock.Mock()
        fava_ledger.crypto_service_locator.get_handler_for_file.return_value = mock_decrypt_handler
        mock_decrypt_handler.decrypt_content.return_value = plaintext_data_str # Simulate successful decryption

        mock_beancount_parser.return_value = ("parsed_ledger_entries", [], {}) # Mock Beancount parsing

        # Action: Load
        loaded_entries, _, _ = fava_ledger.load_file(file_path)

        # Assertions for load
        mock_read_bytes.assert_called_once_with(file_path)
        fava_ledger.crypto_service_locator.get_handler_for_file.assert_called_once_with(file_path, mock_encrypted_bundle_bytes[:128], mock_fava_config)
        
        mock_prompt_pass_for_get_material.assert_called_with(f"Enter passphrase for {file_path} (decrypt):") # Uses file_path as context for decrypt
        mock_get_salt_for_get_material.assert_called_with(f"{file_path}_decrypt_salt")

        expected_key_material_decrypt = {
            "classical_private_key": mock_classical_sk_bytes_load,
            "pqc_private_key": mock_pqc_sk_bytes_load
        }
        active_suite_config_load = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        mock_decrypt_handler.decrypt_content.assert_called_once_with(
            mock_encrypted_bundle_bytes,
            active_suite_config_load,
            expected_key_material_decrypt,
            mock_fava_config
        )
        mock_beancount_parser.assert_called_once_with(plaintext_data_str, mock_fava_config, file_path)
        assert loaded_entries == "parsed_ledger_entries"
        # pytest.skip("Test not implemented due to complex FavaLedger setup.") # Unskipped
        pytest.skip("Test not implemented due to complex FavaLedger setup.")


# --- Fixtures ---
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
    config = mock.Mock()
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
    return config