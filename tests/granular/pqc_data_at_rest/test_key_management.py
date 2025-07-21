import pytest
from unittest import mock

# Import mocks from the new location
from tests.granular.pqc_data_at_rest.mocks import (
    MockOQS_KeyEncapsulation,
    MockX25519PrivateKey,
    MockArgon2id,
    MockHKDF
)
# Import fixtures from the new location
from tests.granular.pqc_data_at_rest.fixtures import mock_crypto_libs, mock_fava_config

class TestKeyManagementFunctions:
    """
    Tests for 5.1. Key Management Functions (fava.crypto.keys)
    """

    @pytest.mark.key_management
    @pytest.mark.critical_path
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    @mock.patch('fava.crypto.keys.OQSKEMAdapter') # Patches OQSKEMAdapter directly
    @mock.patch('fava.crypto.keys.X25519PrivateKey')
    def test_tp_dar_km_001_derive_kem_keys_from_passphrase(self, mock_x25519_priv_key_class, mock_oqskem_adapter_class, mock_hkdf_class, mock_argon2id_class, mock_fava_config):
        from fava.crypto import keys as key_management_module

        passphrase = "test_passphrase_123!"
        salt = b'test_argon_salt_16b'
        pbkdf_algorithm = "Argon2id"
        kdf_algorithm_for_ikm = "HKDF-SHA3-512"
        classical_kem_spec = "X25519"
        pqc_kem_spec = "Kyber768"

        mock_argon2id_class.return_value = MockArgon2id()
        mock_hkdf_class.return_value = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        
        mock_adapter_instance = mock.MagicMock() # Removed spec
        mock_adapter_instance.keypair_from_seed.return_value = (b"mock_pqc_pk", b"mock_pqc_sk")
        mock_oqskem_adapter_class.return_value = mock_adapter_instance
        
        mock_x25519_priv_key_class.from_private_bytes.return_value = MockX25519PrivateKey()
        
        mock_argon2_instance = mock_argon2id_class.return_value
        mock_argon2_instance.derive_mock.return_value = b"mock_ikm_from_argon"

        mock_hkdf_instance = mock_hkdf_class.return_value
        mock_hkdf_instance.derive_mock.side_effect = [
            b"C_classical" * (32 // 11) + b"C" * (32 % 11),
            b"P_pqc_seed_" * (64 // 12) + b"P" * (64 % 12),
        ]

        classical_keys, pqc_keys = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )

        mock_argon2_instance.derive_mock.assert_called_once_with(passphrase, salt)
        assert mock_hkdf_instance.derive_mock.call_count == 2 
        mock_hkdf_instance.derive_mock.assert_any_call(b"mock_ikm_from_argon")
        
        mock_oqskem_adapter_class.assert_called_once_with(pqc_kem_spec)
        mock_adapter_instance.keypair_from_seed.assert_called_once_with(b"P_pqc_seed_" * (64 // 12) + b"P" * (64 % 12))

        assert classical_keys is not None
        assert pqc_keys == (b"mock_pqc_pk", b"mock_pqc_sk")


    @pytest.mark.key_management
    @mock.patch('fava.crypto.keys.Argon2id')
    @mock.patch('fava.crypto.keys.HKDF')
    @mock.patch('fava.crypto.keys.OQSKEMAdapter') # Patch OQSKEMAdapter directly
    @mock.patch('fava.crypto.keys.X25519PrivateKey')
    def test_salt_derivation_variant(self, mock_x25519_priv_key_class, mock_oqskem_adapter_class, mock_hkdf_class, mock_argon2id_class, mock_fava_config):
        from fava.crypto import keys as key_management_module

        passphrase = "test_passphrase_salt_variant"
        salt1 = b'salt_for_test_v1' 
        salt2 = b'salt_for_test_v2' 
        assert salt1 != salt2
        assert len(salt1) == 16 and len(salt2) == 16

        pbkdf_algorithm = "Argon2id"
        kdf_algorithm_for_ikm = "HKDF-SHA3-512"
        classical_kem_spec = "X25519"
        pqc_kem_spec = "Kyber768"

        mock_argon2_instance = MockArgon2id() 
        mock_argon2id_class.return_value = mock_argon2_instance

        mock_hkdf_instance = MockHKDF(algorithm=None, length=32, salt=None, info=b'', backend=None)
        mock_hkdf_class.return_value = mock_hkdf_instance
        
        ikm1 = b"ikm_for_salt1_unique_and_long_enough_for_hkdf_input"
        ikm2 = b"ikm_for_salt2_unique_and_long_enough_for_hkdf_input"
        assert ikm1 != ikm2

        def argon2_derive_side_effect(p, s):
            if p == passphrase and s == salt1: return ikm1
            if p == passphrase and s == salt2: return ikm2
            raise AssertionError(f"MockArgon2id.derive called with unexpected salt: {s} or passphrase: {p}")
        mock_argon2_instance.derive_mock.side_effect = argon2_derive_side_effect

        classical_key_material1 = b"ClassyKeyMat_S1_32bytes_exactlyX" 
        classical_key_material2 = b"ClassyKeyMat_S2_32bytes_exactlyY" 
        
        def mock_static_from_private_bytes_side_effect(data):
            if data == classical_key_material1:
                return MockX25519PrivateKey(private_bytes=classical_key_material1)
            elif data == classical_key_material2:
                return MockX25519PrivateKey(private_bytes=classical_key_material2)
            raise ValueError(f"Unexpected data for X25519PrivateKey.from_private_bytes: {data}")
        mock_x25519_priv_key_class.from_private_bytes.side_effect = mock_static_from_private_bytes_side_effect
        MockX25519PrivateKey._from_private_bytes_return_override = None

        pqc_seed1 = b"PQC_Seed_Material_S1_64bytes_exactly_xxxxxxxxxxxxxxxxxxxxxxxxxxA" 
        pqc_seed2 = b"PQC_Seed_Material_S2_64bytes_exactly_yyyyyyyyyyyyyyyyyyyyyyyyyyB" 
        pqc_keys_s1_tuple = (b"pqc_pk_s1_test_diff", b"pqc_sk_s1_test_diff_from_seed1")
        pqc_keys_s2_tuple = (b"pqc_pk_s2_test_diff", b"pqc_sk_s2_test_diff_from_seed2")

        mock_adapter_instance1 = mock.MagicMock() # Removed spec
        mock_adapter_instance1.keypair_from_seed.return_value = pqc_keys_s1_tuple
        
        mock_adapter_instance2 = mock.MagicMock() # Removed spec
        mock_adapter_instance2.keypair_from_seed.return_value = pqc_keys_s2_tuple
        
        mock_oqskem_adapter_class.side_effect = [mock_adapter_instance1, mock_adapter_instance2]
        
        mock_hkdf_instance.derive_mock.side_effect = [
            classical_key_material1, 
            pqc_seed1,               
            classical_key_material2, 
            pqc_seed2
        ]
        
        keys1_classical, keys1_pqc = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt1, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )
        keys2_classical, keys2_pqc = key_management_module.derive_kem_keys_from_passphrase(
            passphrase, salt2, pbkdf_algorithm, kdf_algorithm_for_ikm,
            classical_kem_spec, pqc_kem_spec
        )

        mock_argon2_instance.derive_mock.assert_any_call(passphrase, salt1)
        mock_argon2_instance.derive_mock.assert_any_call(passphrase, salt2)
        assert mock_argon2_instance.derive_mock.call_count == 2

        hkdf_calls = mock_hkdf_instance.derive_mock.call_args_list
        assert len(hkdf_calls) == 4
        
        inputs_to_hkdf_derive = [call[0][0] for call in hkdf_calls]
        
        assert inputs_to_hkdf_derive[0] == ikm1
        assert inputs_to_hkdf_derive[1] == ikm1 
        assert inputs_to_hkdf_derive[2] == ikm2
        assert inputs_to_hkdf_derive[3] == ikm2 
        
        mock_oqskem_adapter_class.assert_any_call(pqc_kem_spec)
        assert mock_oqskem_adapter_class.call_count == 2
        
        mock_adapter_instance1.keypair_from_seed.assert_called_once_with(pqc_seed1)
        mock_adapter_instance2.keypair_from_seed.assert_called_once_with(pqc_seed2)

        assert keys1_pqc == pqc_keys_s1_tuple
        assert keys2_pqc == pqc_keys_s2_tuple
        
        assert keys1_classical != keys2_classical or keys1_pqc != keys2_pqc, \
            "Keys derived with different salts should be different"

    @pytest.mark.key_management
    @pytest.mark.error_handling
    def test_tp_dar_km_003_key_derivation_fails_unsupported_spec(self): 
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import UnsupportedAlgorithmError

        passphrase = "test_passphrase"
        salt = b'some_salt_value_16b'

        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "UNSUPPORTED_KDF", "X25519", "Kyber768" 
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "HKDF-SHA3-512", "X25519", "UNSUPPORTED_PQC_KEM"
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "UNSUPPORTED_PBKDF", "HKDF-SHA3-512", "X25519", "Kyber768" 
            )
        with pytest.raises(UnsupportedAlgorithmError):
            key_management_module.derive_kem_keys_from_passphrase(
                passphrase, salt, "Argon2id", "HKDF-SHA3-512", "UNSUPPORTED_CLASSICAL_KEM", "Kyber768" 
            )

    @pytest.mark.key_management
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('fava.crypto.keys.OQSKEMAdapter') # Patch OQSKEMAdapter directly
    @mock.patch('fava.crypto.keys.X25519PrivateKey', new=MockX25519PrivateKey)
    def test_tp_dar_km_004_load_keys_from_external_file(self, mock_oqskem_adapter_class, mock_open): 
        from fava.crypto import keys as key_management_module
        key_file_path_config = {"classical_private": "mock_classical.key", "pqc_private": "mock_pqc.key"}

        mock_classical_key_instance = MockX25519PrivateKey(private_bytes=b"classical_key_bytes_instance_data")
        MockX25519PrivateKey._from_private_bytes_return_override = mock_classical_key_instance
        
        mock_adapter_instance = mock.MagicMock() # Removed spec
        mock_oqskem_adapter_class.return_value = mock_adapter_instance

        expected_pqc_pk_loaded = b"mock_pqc_pk_loaded_from_file"
        expected_pqc_sk_loaded = b"pqc_key_bytes_from_file" 
        mock_adapter_instance.load_keypair_from_secret_key.return_value = (expected_pqc_pk_loaded, expected_pqc_sk_loaded)      

        mock_open.side_effect = [
            mock.mock_open(read_data=b"classical_key_bytes_from_file").return_value,
            mock.mock_open(read_data=b"pqc_key_bytes_from_file").return_value
        ]
            
        classical_keys_tuple, pqc_keys_tuple = key_management_module.load_keys_from_external_file(
            key_file_path_config, pqc_kem_spec="Kyber768"
        )
        
        mock_open.assert_any_call("mock_classical.key", "rb")
        mock_open.assert_any_call("mock_pqc.key", "rb")

        mock_oqskem_adapter_class.assert_called_once_with("Kyber768")
        mock_adapter_instance.load_keypair_from_secret_key.assert_called_once_with(b"pqc_key_bytes_from_file")
        
        assert classical_keys_tuple[1] is mock_classical_key_instance 
        assert classical_keys_tuple[0] is mock_classical_key_instance.public_key() 
        
        assert pqc_keys_tuple[0] == expected_pqc_pk_loaded
        assert pqc_keys_tuple[1] == expected_pqc_sk_loaded


    @pytest.mark.error_handling
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('fava.crypto.keys.X25519PrivateKey.from_private_bytes', side_effect=ValueError("Invalid key format"))
    def test_tp_dar_km_005_load_keys_external_file_missing_or_invalid(self, mock_x25519_from_bytes, mock_open):
        from fava.crypto import keys as key_management_module
        from fava.crypto.exceptions import KeyManagementError

        mock_open.side_effect = FileNotFoundError
        with pytest.raises(KeyManagementError):
           key_management_module.load_keys_from_external_file({"classical_private": "non_existent.key"})

        mock_open.reset_mock() 
        mock_open.side_effect = [mock.mock_open(read_data=b"bad_key_data").return_value]
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
        mock_secure_format.assert_called_once_with(b"mock_pqc_sk_for_export", "ENCRYPTED_PKCS8_AES256GCM_PBKDF2", "export_passphrase", None)
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