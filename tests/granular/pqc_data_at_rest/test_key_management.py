import pytest
from unittest import mock

# Import mocks from the new location
from .mocks import (
    MockOQS_KeyEncapsulation,
    MockX25519PrivateKey,
    MockArgon2id,
    MockHKDF
)
# Import fixtures from the new location
from .fixtures import mock_crypto_libs, mock_fava_config

# Removed @pytest.mark.usefixtures("mock_crypto_libs", "mock_fava_config")
class TestKeyManagementFunctions:
    """
    Tests for 5.1. Key Management Functions (fava.crypto.keys)
    """

    @pytest.mark.key_management
    @pytest.mark.critical_path
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    @mock.patch('fava.crypto.keys.KeyEncapsulation')
    @mock.patch('fava.crypto.keys.X25519PrivateKey')
    def test_tp_dar_km_001_derive_kem_keys_from_passphrase(self, mock_x25519_priv_key_class, mock_oqs_kem_class, mock_hkdf_class, mock_argon2id_class, mock_fava_config): # mock_fava_config still needed here
        from fava.crypto import keys as key_management_module

        passphrase = "test_passphrase_123!"
        salt = b'test_argon_salt_16b'
        pbkdf_algorithm = "Argon2id"
        kdf_algorithm_for_ikm = "HKDF-SHA3-512"
        classical_kem_spec = "X25519"
        pqc_kem_spec = "ML-KEM-768"

        mock_argon2id_class.return_value = MockArgon2id()
        mock_hkdf_class.return_value = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        mock_oqs_kem_class.return_value = MockOQS_KeyEncapsulation('ML-KEM-768')
        mock_x25519_priv_key_class.return_value = MockX25519PrivateKey()
        
        mock_argon2_instance = mock_argon2id_class.return_value
        mock_argon2_instance.derive_mock.return_value = b"mock_ikm_from_argon"

        mock_hkdf_instance = mock_hkdf_class.return_value
        # Ensure side_effect provides correctly sized byte strings
        # Classical HKDF length is 32, PQC HKDF length is 64
        mock_hkdf_instance.derive_mock.side_effect = [
            b"C" * 32,  # Classical key material (32 bytes)
            b"P" * 64   # PQC seed material (64 bytes)
        ]

        classical_keys, pqc_keys = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )

        mock_argon2_instance.derive_mock.assert_called_once_with(passphrase, salt)
        assert mock_hkdf_instance.derive_mock.call_count == 2
        mock_hkdf_instance.derive_mock.assert_any_call(b"mock_ikm_from_argon")
        assert classical_keys is not None
        assert pqc_keys is not None

    @pytest.mark.key_management
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    @mock.patch('fava.crypto.keys.KeyEncapsulation')
    @mock.patch('fava.crypto.keys.X25519PrivateKey')
    def test_salt_derivation_variant(self, mock_x25519_priv_key_class, mock_oqs_kem_class, mock_hkdf_class, mock_argon2id_class, mock_fava_config):
        from fava.crypto import keys as key_management_module

        passphrase = "test_passphrase_salt_variant"
        # Ensure salts are 16 bytes as per typical Argon2id usage
        salt1 = b'salt_for_test_v1' # 16 bytes
        salt2 = b'salt_for_test_v2' # 16 bytes
        assert salt1 != salt2, "Salts must be different for this test"
        assert len(salt1) == 16 and len(salt2) == 16, "Salts must be 16 bytes"

        pbkdf_algorithm = "Argon2id"
        kdf_algorithm_for_ikm = "HKDF-SHA3-512"
        classical_kem_spec = "X25519"
        pqc_kem_spec = "ML-KEM-768"

        # Configure mock instances
        mock_argon2_instance = MockArgon2id() # Uses default mock.Mock for derive_mock
        mock_argon2id_class.return_value = mock_argon2_instance

        # HKDF mock needs to be configured for specific lengths if derive_kem_keys_from_passphrase uses them
        # The HKDF mock in mocks.py uses the length passed to its __init__ to determine output size.
        # Here, we will control HKDF's output via side_effect, so initial length is less critical for this assertion.
        mock_hkdf_instance = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        mock_hkdf_class.return_value = mock_hkdf_instance
        # These mocks are needed for the function to run.
        # Their specific return values will be controlled to ensure different keys are produced.
        # mock_x25519_priv_key_class is the replacement for the X25519PrivateKey class itself.
        # mock_oqs_kem_class is the replacement for the KeyEncapsulation class.
        # We need to configure the behavior of their methods.
        
        # Set up side_effect for Argon2id to return different IKMs based on salt
        ikm1 = b"ikm_for_salt1_unique_and_long_enough_for_hkdf_input"
        ikm2 = b"ikm_for_salt2_unique_and_long_enough_for_hkdf_input"
        assert ikm1 != ikm2

        def argon2_derive_side_effect(p, s):
            if p == passphrase and s == salt1: return ikm1
            if p == passphrase and s == salt2: return ikm2
            raise AssertionError(f"MockArgon2id.derive called with unexpected salt: {s} or passphrase: {p}")
        mock_argon2_instance.derive_mock.side_effect = argon2_derive_side_effect

        # Setup for classical key derivation
        classical_key_material1 = b"ClassyKeyMat_S1_32bytes_exactlyX" # 32 bytes
        classical_key_material2 = b"ClassyKeyMat_S2_32bytes_exactlyY" # 32 bytes
        assert len(classical_key_material1) == 32 and len(classical_key_material2) == 32
        
        # mock_x25519_priv_key_class is the MagicMock replacing fava.crypto.keys.X25519PrivateKey
        # Its static method from_private_bytes needs to return different MockX25519PrivateKey instances
        def mock_static_from_private_bytes_side_effect(data):
            if data == classical_key_material1:
                return MockX25519PrivateKey(private_bytes=classical_key_material1)
            elif data == classical_key_material2:
                return MockX25519PrivateKey(private_bytes=classical_key_material2)
            raise ValueError(f"Unexpected data for X25519PrivateKey.from_private_bytes: {data}")
        mock_x25519_priv_key_class.from_private_bytes.side_effect = mock_static_from_private_bytes_side_effect
        # Ensure _from_private_bytes_return_override on the actual MockX25519PrivateKey class is clear
        MockX25519PrivateKey._from_private_bytes_return_override = None


        # Setup for PQC key derivation from seed
        pqc_seed1 = b"PQC_Seed_Material_S1_64bytes_exactly_xxxxxxxxxxxxxxxxxxxxxxxxxxA" # 64 bytes
        pqc_seed2 = b"PQC_Seed_Material_S2_64bytes_exactly_yyyyyyyyyyyyyyyyyyyyyyyyyyB" # 64 bytes
        assert len(pqc_seed1) == 64 and len(pqc_seed2) == 64
        pqc_keys_s1_tuple = (b"pqc_pk_s1_test_diff", b"pqc_sk_s1_test_diff")
        pqc_keys_s2_tuple = (b"pqc_pk_s2_test_diff", b"pqc_sk_s2_test_diff")

        # The SUT calls KeyEncapsulation(kem_spec).keypair_from_seed(seed)
        # KeyEncapsulation is replaced by mock_oqs_kem_class.
        # So, mock_oqs_kem_class(kem_spec) is called, returning an instance (mock_oqs_kem_class.return_value).
        # Then, .keypair_from_seed(seed) is called on that instance.
        # We need this instance's method to behave differently.
        # The MockOQS_KeyEncapsulation.keypair_from_seed uses a class-level mock:
        # _mock_keypair_from_seed_class. We can set its side_effect.
        def oqs_class_keypair_from_seed_side_effect(seed_param):
            if seed_param == pqc_seed1:
                return pqc_keys_s1_tuple
            elif seed_param == pqc_seed2:
                return pqc_keys_s2_tuple
            raise ValueError(f"MockOQS_KeyEncapsulation._mock_keypair_from_seed_class called with unexpected seed {seed_param}")
        MockOQS_KeyEncapsulation._mock_keypair_from_seed_class.side_effect = oqs_class_keypair_from_seed_side_effect
        # Ensure the mock_oqs_kem_class returns a standard MockOQS_KeyEncapsulation instance
        mock_oqs_kem_class.return_value = MockOQS_KeyEncapsulation('ML-KEM-768')


        # HKDF mock must output these exact materials
        mock_hkdf_instance.derive_mock.side_effect = [
            classical_key_material1,
            pqc_seed1,
            classical_key_material2,
            pqc_seed2
        ]

        # Call 1 with salt1
        # Call 1 with salt1
        keys1_classical, keys1_pqc = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt1, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )
        # Call 2 with salt2
        keys2_classical, keys2_pqc = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt2, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )

        # Assert Argon2id was called with both salts and the correct passphrase
        mock_argon2_instance.derive_mock.assert_any_call(passphrase, salt1)
        mock_argon2_instance.derive_mock.assert_any_call(passphrase, salt2)
        assert mock_argon2_instance.derive_mock.call_count == 2

        # Assert HKDF was called with the different IKMs produced by Argon2id
        hkdf_calls = mock_hkdf_instance.derive_mock.call_args_list
        assert len(hkdf_calls) == 4, "HKDF should be called 4 times (2 per main call)"
        
        # Check that the IKMs passed to HKDF are correct
        # The IKM is the first argument to HKDF's derive method.
        ikms_passed_to_hkdf = [call[0][0] for call in hkdf_calls]
        
        assert ikms_passed_to_hkdf[0] == ikm1, "First HKDF call (classical) for salt1 should use ikm1"
        assert ikms_passed_to_hkdf[1] == ikm1, "Second HKDF call (PQC) for salt1 should use ikm1"
        assert ikms_passed_to_hkdf[2] == ikm2, "First HKDF call (classical) for salt2 should use ikm2"
        assert ikms_passed_to_hkdf[3] == ikm2, "Second HKDF call (PQC) for salt2 should use ikm2"

        # Optional: Assert that the final keys are different. This is an indirect check but good for completeness.
        # This depends on the deterministic behavior of the downstream mock key generation from seeds/materials.
        # MockX25519PrivateKey.generate() and MockOQS_KeyEncapsulation.keypair_from_seed() would need to be deterministic
        # or their return values controlled based on the input seed/material from HKDF.
        # For simplicity, the primary assertion is on the IKMs passed to HKDF.
        # If HKDF's output (seeds) are different, and keygen from seed is deterministic, keys will differ.
        # The current HKDF mock returns fixed strings, so keys derived from these *will* be different if the strings differ.
        assert keys1_classical != keys2_classical or keys1_pqc != keys2_pqc, \
            "Keys derived with different salts should be different"

    @pytest.mark.key_management
    @pytest.mark.error_handling
    def test_tp_dar_km_003_key_derivation_fails_unsupported_spec(self): # mock_fava_config not used here
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import UnsupportedAlgorithmError

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
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('fava.crypto.keys.KeyEncapsulation', new=MockOQS_KeyEncapsulation)
    @mock.patch('fava.crypto.keys.X25519PrivateKey', new=MockX25519PrivateKey)
    def test_tp_dar_km_004_load_keys_from_external_file(self, mock_open): # mock_fava_config not used here
        from fava.crypto import keys as key_management_module
        key_file_path_config = {"classical_private": "mock_classical.key", "pqc_private": "mock_pqc.key"}

        # Configure class-level mock behavior for from_private_bytes
        # This ensures X25519PrivateKey.from_private_bytes(data) returns a specific mock instance
        mock_classical_key_instance = MockX25519PrivateKey(private_bytes=b"classical_key_bytes_instance_data")
        MockX25519PrivateKey._from_private_bytes_return_override = mock_classical_key_instance
        
        # Configure the mock method on the MockOQS_KeyEncapsulation class or its instances if necessary.
        # The `new=MockOQS_KeyEncapsulation` means KeyEncapsulation() will be MockOQS_KeyEncapsulation().
        # We need the instance of MockOQS_KeyEncapsulation to have its `load_keypair_from_secret_key_mock` configured.
        # This is typically done by configuring the mock object that `MockOQS_KeyEncapsulation` itself returns if it's a factory,
        # or by ensuring its instances have correctly configured mock methods.
        # For this test, we will rely on the MockOQS_KeyEncapsulation's instance methods being mock objects themselves.
        
        # Resetting a class attribute used for tracking calls in the mock, if that's the pattern.
        if hasattr(MockOQS_KeyEncapsulation, '_mock_load_keypair_from_secret_key_class_calls'):
             MockOQS_KeyEncapsulation._mock_load_keypair_from_secret_key_class_calls = []


        mock_open.side_effect = [
            mock.mock_open(read_data=b"classical_key_bytes_from_file").return_value,
            mock.mock_open(read_data=b"pqc_key_bytes_from_file").return_value
        ]
        
        classical_keys_tuple, pqc_keys_tuple = key_management_module.load_keys_from_external_file(key_file_path_config, pqc_kem_spec="Kyber-768")
        
        mock_open.assert_any_call("mock_classical.key", "rb")
        mock_open.assert_any_call("mock_pqc.key", "rb")

        # To assert calls on instance methods when using `new=`, it's often easier to patch the class
        # and make its return_value a mock instance you can then inspect.
        # However, if MockOQS_KeyEncapsulation is designed such that its instances' methods
        # are pre-configured mocks (e.g. self.load_keypair_from_secret_key_mock = mock.Mock()),
        # then we would need a way to access that specific instance.
        # The previous assertion `MockOQS_KeyEncapsulation._mock_load_keypair_from_secret_key_class.assert_called_once_with(...)`
        # relied on a custom static/class mock attribute. Let's assume this pattern is intended for the mock.
        MockOQS_KeyEncapsulation._mock_load_keypair_from_secret_key_class.assert_called_once_with(b"pqc_key_bytes_from_file")

        assert classical_keys_tuple[1] is mock_classical_key_instance # Check private key instance
        assert classical_keys_tuple[0] is mock_classical_key_instance.public_key() # Check public key mock
        
        # The pqc_keys_tuple should contain what load_keypair_from_secret_key_mock returns on the instance
        # This part depends on how MockOQS_KeyEncapsulation is set up by the `new=` patch.
        # If MockOQS_KeyEncapsulation's __init__ sets up load_keypair_from_secret_key_mock with a return value:
        assert pqc_keys_tuple == MockOQS_KeyEncapsulation._mock_load_keypair_from_secret_key_class.return_value


    @pytest.mark.error_handling
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('fava.crypto.keys.X25519PrivateKey.from_private_bytes', side_effect=ValueError("Invalid key format"))
    def test_tp_dar_km_005_load_keys_external_file_missing_or_invalid(self, mock_x25519_from_bytes, mock_open):
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import KeyManagementError

        mock_open.side_effect = FileNotFoundError
        with pytest.raises(KeyManagementError):
           key_management_module.load_keys_from_external_file({"classical_private": "non_existent.key"})

        mock_open.reset_mock() # Reset mock_open for the next scenario
        mock_open.side_effect = [mock.mock_open(read_data=b"bad_key_data").return_value]
        # Ensure the side_effect for from_private_bytes is active for this part of the test
        mock_x25519_from_bytes.side_effect = ValueError("Invalid key format")
        with pytest.raises(KeyManagementError, match="Invalid key format"):
           key_management_module.load_keys_from_external_file({"classical_private": "bad_format.key"})


    @pytest.mark.security_sensitive
    @mock.patch('fava.crypto.keys._retrieve_stored_or_derived_pqc_private_key')
    @mock.patch('fava.crypto.keys.secure_format_for_export')
    def test_tp_dar_km_006_export_fava_managed_keys_secure_format(self, mock_secure_format, mock_retrieve_key, mock_fava_config):
        from fava.crypto import keys as key_management_module
    
        mock_retrieve_key.return_value = b"mock_pqc_sk_for_export"
        mock_secure_format.return_value = b"securely_formatted_exported_key_bytes"
    
        exported_data = key_management_module.export_fava_managed_pqc_private_keys(
            "user_context_1", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "export_passphrase", config=mock_fava_config
        )
        mock_retrieve_key.assert_called_once_with(
            "user_context_1",
            config=mock_fava_config,
            passphrase="export_passphrase"
        )
        mock_secure_format.assert_called_once_with(b"mock_pqc_sk_for_export", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "export_passphrase")
        assert exported_data == b"securely_formatted_exported_key_bytes"

    @pytest.mark.key_management
    @pytest.mark.error_handling
    @pytest.mark.security_sensitive
    @mock.patch('fava.crypto.keys._retrieve_stored_or_derived_pqc_private_key', return_value=None)
    def test_tp_dar_km_007_export_fava_managed_keys_not_found(self, mock_retrieve_key):
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import KeyManagementError

        with pytest.raises(KeyManagementError):
            key_management_module.export_fava_managed_pqc_private_keys(
                "non_existent_context", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "any_pass"
            )