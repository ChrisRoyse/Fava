import pytest
from unittest import mock

# Import fixtures from the new location
from tests.granular.pqc_data_at_rest.fixtures import mock_crypto_libs, mock_fava_config
# Assuming CryptoServiceLocator might be needed for type hinting or direct use in fixtures
from fava.crypto.locator import CryptoServiceLocator


@pytest.mark.usefixtures("mock_fava_config", "mock_crypto_libs")
class TestFavaLedgerIntegration:
    """
    Tests for 5.5. FavaLedger Integration (fava.core.ledger.FavaLedger)
    """
    """
    Tests for 5.5. FavaLedger Integration (fava.core.ledger.FavaLedger)
    """
    @pytest.fixture
    def fava_ledger(self, mock_fava_config):
        from fava.core import FavaLedger
        ledger = FavaLedger(mock_fava_config)
        ledger.crypto_service_locator = mock.Mock(spec=CryptoServiceLocator)
        return ledger
    @pytest.mark.key_management
    @pytest.mark.critical_path
    @mock.patch('fava.core.ledger_main.PROMPT_USER_FOR_PASSPHRASE_SECURELY')
    @mock.patch('fava.core.ledger_main.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT')
    @mock.patch('fava.crypto.keys.load_keys_from_external_file')
    def test_tp_dar_fl_001_get_key_material_decrypt_passphrase(
        self,
        mock_load_keys_external_file, # Corresponds to fava.crypto.keys.load_keys_from_external_file
        mock_retrieve_salt,           # Corresponds to fava.core.ledger.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT
        mock_prompt_passphrase,       # Corresponds to fava.core.ledger.PROMPT_USER_FOR_PASSPHRASE_SECURELY
        fava_ledger,
        mock_fava_config
    ):
        file_path_context = "test_file.pqc"
        operation_type = "decrypt"
        
        # Scenario 1: PASSPHRASE_DERIVED
        mock_fava_config.pqc_key_management_mode = "PASSPHRASE_DERIVED"
        mock_prompt_passphrase.return_value = "test_passphrase" # Use the correctly named mock
        mock_retrieve_salt.return_value = b"a_salt_for_context_16b" # Use the correctly named mock
        # This test focuses on _get_key_material_for_operation.
        # The actual key derivation (fava.crypto.keys.derive_kem_keys_from_passphrase)
        # is mocked *within* _get_key_material_for_operation if mode is PASSPHRASE_DERIVED.
        # So, we don't mock derive_kem_keys at this test level directly for this part.
        # Instead, we ensure the mocks for PROMPT and RETRIEVE_SALT are hit,
        # and then we'd need to mock 'fava.crypto.keys.derive_kem_keys_from_passphrase'
        # if we were to trace the call deeper into _get_key_material_for_operation.
        # For now, let's assume the logic within _get_key_material_for_operation
        # correctly calls the *actual* derive_kem_keys_from_passphrase, which would then
        # use its own mocks if this were a more integrated test.
        # However, the original test structure implies derive_kem_keys IS mocked here.
        # Let's assume 'fava.core.ledger.fava_keys.derive_kem_keys_from_passphrase' is the target.
        # Re-checking the patches:
        # @mock.patch('fava.core.ledger.PROMPT_USER_FOR_PASSPHRASE_SECURELY') -> mock_prompt_passphrase
        # @mock.patch('fava.core.ledger.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT') -> mock_retrieve_salt
        # @mock.patch('fava.crypto.keys.load_keys_from_external_file') -> mock_load_keys_external_file
        # The mock for 'fava.crypto.keys.derive_kem_keys_from_passphrase' is NOT active at this level.
        # It is called INTERNALLY by _get_key_material_for_operation.
        # So the previous assertion on mock_derive_kem_keys was incorrect for *this* test's direct mocks.
        # We need to mock it where it's called if we want to control its output from here.
        # Let's patch it directly for the scope of this test method call on fava_ledger.

        with mock.patch('fava.core.ledger_main.fava_keys.derive_kem_keys_from_passphrase') as mock_internal_derive_keys:
            mock_classical_sk_bytes = b"mock_classical_sk_bytes_derived"
            mock_pqc_sk_bytes = b"mock_pqc_sk_bytes_derived"
            mock_internal_derive_keys.return_value = (
                (b"mock_classical_pk_derived", mock_classical_sk_bytes),
                (b"mock_pqc_pk_derived", mock_pqc_sk_bytes)
            )

            key_material = fava_ledger._get_key_material_for_operation(file_path_context, operation_type)
            
            mock_prompt_passphrase.assert_called_once_with(f"Enter passphrase for {file_path_context} ({operation_type}):")
            mock_retrieve_salt.assert_called_once_with(f"{file_path_context}_{operation_type}_salt")
            
            active_suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
            mock_internal_derive_keys.assert_called_once_with(
                passphrase="test_passphrase",
                salt=b"a_salt_for_context_16b",
                pbkdf_algorithm="Argon2id",
                kdf_algorithm_for_ikm="HKDF-SHA3-512",
                classical_kem_spec="X25519",
                pqc_kem_spec="Kyber768",
                argon2_params=None
            )
            assert key_material == {
                "classical_private_key": mock_classical_sk_bytes,
                "pqc_private_key": mock_pqc_sk_bytes
            }
            # The 'with' block for mock_internal_derive_keys correctly ends here due to dedent.
            mock_load_keys_external_file.assert_not_called()

        # Reset mocks for Scenario 2
        mock_prompt_passphrase.reset_mock()
        mock_retrieve_salt.reset_mock()
        # mock_derive_kem_keys was not a direct argument, mock_internal_derive_keys was used in a 'with' block
        mock_load_keys_external_file.reset_mock() # Reset this one too

        fava_ledger.fava_options.pqc_key_management_mode = "EXTERNAL_FILE"
        fava_ledger.fava_options.pqc_key_file_paths = {"classical_private": "c.key", "pqc_private": "p.key"}
        
        mock_classical_sk_ext_bytes = b"mock_classical_sk_bytes_external"
        mock_pqc_sk_ext_bytes = b"mock_pqc_sk_bytes_external"
        mock_load_keys_external_file.return_value = ( # Use the correctly named mock
            (b"mock_classical_pk_ext", mock_classical_sk_ext_bytes),
            (b"mock_pqc_pk_ext", mock_pqc_sk_ext_bytes)
        )

        key_material_ext = fava_ledger._get_key_material_for_operation(file_path_context, operation_type)
        mock_load_keys_external_file.assert_called_once_with(
            key_file_path_config=fava_ledger.fava_options.pqc_key_file_paths,
            pqc_kem_spec="Kyber768"
        )
        assert key_material_ext == {
            "classical_private_key": mock_classical_sk_ext_bytes,
            "pqc_private_key": mock_pqc_sk_ext_bytes
        }
        # mock_derive_kem_keys was not a direct argument.
        # mock_internal_derive_keys would not be called in "EXTERNAL_FILE" mode.
        # If we had mock_internal_derive_keys as a broader mock, we'd check its call_count == 1 (from first scenario)

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @mock.patch('fava.core.ledger_main.WRITE_BYTES_TO_FILE')
    @mock.patch('fava.core.ledger_main.READ_BYTES_FROM_FILE')
    @mock.patch('fava.core.ledger_main.parse_beancount_file_from_source')
    @mock.patch('fava.core.ledger_main.PROMPT_USER_FOR_PASSPHRASE_SECURELY')
    @mock.patch('fava.core.ledger_main.RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT')
    @mock.patch('fava.core.ledger_main.fava_keys.derive_kem_keys_from_passphrase')
    def test_tp_dar_fl_002_save_reload_pqc_encrypted_file(
        self, mock_derive_keys_for_get_material, mock_get_salt_for_get_material,
        mock_prompt_pass_for_get_material,
        mock_beancount_parser, mock_read_bytes, mock_write_bytes,
        fava_ledger, mock_fava_config
    ):
        plaintext_data_str = "ledger_content_to_encrypt_and_reload"
        file_path = "test_ledger.bc.pqc_fava"
        key_context = "test_ledger_context"

        fava_ledger.fava_options.pqc_data_at_rest_enabled = True
        fava_ledger.fava_options.pqc_key_management_mode = "PASSPHRASE_DERIVED"
        
        mock_classical_pk_bytes_save = b"classical_pk_for_save"
        mock_pqc_pk_bytes_save = b"pqc_pk_for_save_1184b" + b"A" * (1184 - len(b"pqc_pk_for_save_1184b"))
        mock_derive_keys_for_get_material.return_value = (
            (mock_classical_pk_bytes_save, b"classical_sk_for_save"),
            (mock_pqc_pk_bytes_save, b"pqc_sk_for_save")
        )
        mock_prompt_pass_for_get_material.return_value = "save_passphrase"
        mock_get_salt_for_get_material.return_value = b"salt_for_save_op"

        mock_encrypt_handler = mock.Mock()
        fava_ledger.crypto_service_locator.get_pqc_encrypt_handler.return_value = mock_encrypt_handler
        mock_encrypted_bundle_bytes = b"super_secret_encrypted_bundle_bytes"
        mock_encrypt_handler.encrypt_content.return_value = mock_encrypted_bundle_bytes
        
        fava_ledger.save_file_pqc(file_path, plaintext_data_str, key_context=key_context)

        mock_prompt_pass_for_get_material.assert_called_with(f"Enter passphrase for {key_context} (encrypt):")
        mock_get_salt_for_get_material.assert_called_with(f"{key_context}_encrypt_salt")
        
        expected_suite_config = {
            "id": "X25519_KYBER768_AES256GCM",
            "classical_kem_algorithm": "X25519",
            "pqc_kem_algorithm": "ML-KEM-768",
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512",
            "pbkdf_algorithm_for_passphrase": "Argon2id",
            "kdf_algorithm_for_ikm_from_pbkdf": "HKDF-SHA3-512"
        }
        fava_ledger.crypto_service_locator.get_pqc_encrypt_handler.assert_called_once_with(expected_suite_config, fava_ledger.fava_options)
        
        expected_key_material_encrypt = {
            "classical_public_key": mock_classical_pk_bytes_save,
            "pqc_public_key": mock_pqc_pk_bytes_save
        }
        # Correct indentation for the multi-line assert_called_once_with
        mock_encrypt_handler.encrypt_content.assert_called_once_with(
            plaintext_data_str,
            expected_suite_config,
            expected_key_material_encrypt,
            fava_ledger.fava_options
        )
        mock_write_bytes.assert_called_once_with(file_path, mock_encrypted_bundle_bytes)

        mock_read_bytes.return_value = mock_encrypted_bundle_bytes
        
        mock_classical_sk_bytes_load = b"classical_sk_for_load"
        mock_pqc_sk_bytes_load = b"pqc_sk_for_load_2400b" + b"S" * (2400 - len(b"pqc_sk_for_load_2400b"))
        mock_derive_keys_for_get_material.reset_mock()
        mock_derive_keys_for_get_material.return_value = (
            (b"classical_pk_for_load", mock_classical_sk_bytes_load),
            (b"pqc_pk_for_load", mock_pqc_sk_bytes_load)
        )
        mock_prompt_pass_for_get_material.reset_mock()
        mock_prompt_pass_for_get_material.return_value = "load_passphrase"
        mock_get_salt_for_get_material.reset_mock()
        mock_get_salt_for_get_material.return_value = b"salt_for_load_op"


        mock_decrypt_handler = mock.Mock()
        fava_ledger.crypto_service_locator.get_handler_for_file.return_value = mock_decrypt_handler
        mock_decrypt_handler.decrypt_content.return_value = plaintext_data_str

        mock_beancount_parser.return_value = ("parsed_ledger_entries", [], {})

        loaded_entries, _, _ = fava_ledger.load_file(file_path)

        mock_read_bytes.assert_called_once_with(file_path)
        
        # get_handler_for_file is called twice:
        # 1. In load_file with peek_bytes
        # 2. In _try_decrypt_content with full_bytes (which are the same in this test)
        expected_get_handler_call_args = (file_path, mock_encrypted_bundle_bytes[:128], mock_fava_config)
        
        # Check call count
        assert fava_ledger.crypto_service_locator.get_handler_for_file.call_count == 2
        
        # Check the arguments of the calls
        # Since the arguments are identical for both calls in this specific test case:
        fava_ledger.crypto_service_locator.get_handler_for_file.assert_any_call(*expected_get_handler_call_args)
        # To be more precise about two identical calls:
        fava_ledger.crypto_service_locator.get_handler_for_file.assert_has_calls([
            mock.call(*expected_get_handler_call_args),
            mock.call(*expected_get_handler_call_args)
        ], any_order=False) # Order matters, even if calls are identical here.

        mock_prompt_pass_for_get_material.assert_called_with(f"Enter passphrase for {file_path} (decrypt):")
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
        # The pytest.skip line was previously here and might have caused indentation issues.
        # It is correctly commented out or removed in the current version of the file.