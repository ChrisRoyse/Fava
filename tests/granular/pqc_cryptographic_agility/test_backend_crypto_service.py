import pytest
import logging
from typing import Dict, Any, List, Union, Callable

from fava.pqc.backend_crypto_service import (
    BackendCryptoService,
    HybridPqcCryptoHandler,
    HashingProvider,
    decrypt_data_at_rest_with_agility,
    parse_common_encrypted_bundle_header,
)
from fava.pqc.global_config import GlobalConfig
from fava.pqc.interfaces import (
    CryptoHandler,
    HybridEncryptedBundle,
    KeyMaterialForEncryption,
    KeyMaterialForDecryption,
    HasherInterface,
)
from fava.pqc.exceptions import (
    InvalidArgumentError,
    AlgorithmNotFoundError,
    ConfigurationError,
    CriticalConfigurationError,
    DecryptionError,
    EncryptionFailedError,
    AlgorithmUnavailableError,
    HashingOperationFailedError,
    BundleParsingError,
    CryptoError,
)

# Patching locations for helpers used by the UUT
KEM_LIB_PATH = "fava.pqc.backend_crypto_service.KEM_LIBRARY"
KDF_LIB_PATH = "fava.pqc.backend_crypto_service.KDF_LIBRARY"
SYM_CIPHER_LIB_PATH = "fava.pqc.backend_crypto_service.SYMMETRIC_CIPHER_LIBRARY"
UTIL_LIB_PATH = "fava.pqc.backend_crypto_service.UTILITY_LIBRARY"
GLOBAL_CONFIG_PATH = "fava.pqc.backend_crypto_service.GlobalConfig" # Used by BackendCryptoService methods
PARSE_BUNDLE_HEADER_PATH = "fava.pqc.backend_crypto_service.parse_common_encrypted_bundle_header"


class TestBackendCryptoServiceRegistration:
    """
    Test suite for BackendCryptoService Handler Registration and Retrieval
    """
    def setup_method(self):
        BackendCryptoService.reset_registry_for_testing()
        GlobalConfig.reset_cache()

    @pytest.mark.critical_path
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_001_register_and_get_handler(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mock_handler_A = mocker.Mock(spec=CryptoHandler)
        mock_handler_A.get_suite_id.return_value = "SUITE_A"
        
        BackendCryptoService.register_crypto_handler("SUITE_A", mock_handler_A)
        assert "Crypto handler registered for suite: SUITE_A" in caplog.text
        
        retrieved_handler = BackendCryptoService.get_crypto_handler("SUITE_A")
        assert retrieved_handler is mock_handler_A

    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_002_register_handler_invalid_args(self, mocker, caplog):
        caplog.set_level(logging.ERROR)
        mock_handler = mocker.Mock(spec=CryptoHandler)

        with pytest.raises(InvalidArgumentError, match="suite_id and handler_or_factory must be provided"):
            BackendCryptoService.register_crypto_handler(None, mock_handler)
        assert "Attempted to register crypto handler with invalid arguments" in caplog.text
        caplog.clear()
        with pytest.raises(InvalidArgumentError, match="suite_id and handler_or_factory must be provided"):
            BackendCryptoService.register_crypto_handler("", mock_handler)
        assert "Attempted to register crypto handler with invalid arguments" in caplog.text
        caplog.clear()
        with pytest.raises(InvalidArgumentError, match="suite_id and handler_or_factory must be provided"):
            BackendCryptoService.register_crypto_handler("SUITE_X", None)
        assert "Attempted to register crypto handler with invalid arguments" in caplog.text


    @pytest.mark.critical_path
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_003_get_handler_unregistered_suite(self, mocker, caplog):
        caplog.set_level(logging.ERROR)
        with pytest.raises(AlgorithmNotFoundError, match="Handler for suite 'UNKNOWN_SUITE' not registered."):
            BackendCryptoService.get_crypto_handler("UNKNOWN_SUITE")
        assert "No crypto handler registered for suite_id: UNKNOWN_SUITE" in caplog.text

    @pytest.mark.backend
    def test_tc_agl_bcs_reg_004_get_handler_with_factory(self, mocker):
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_suite_config_f = {"config_key": "config_value_f", "type": "FAVA_HYBRID_PQC"}
        mock_global_config_get.return_value = {
            "data_at_rest": {"suites": {"SUITE_F": mock_suite_config_f}}
        }
        
        mock_handler_instance = mocker.Mock(spec=CryptoHandler)
        
        # Define a mock factory function
        factory_call_args_storage = {} # To store arguments passed to the factory
        def mock_factory(suite_id_arg, suite_config_arg):
            factory_call_args_storage['suite_id'] = suite_id_arg
            factory_call_args_storage['suite_config'] = suite_config_arg
            return mock_handler_instance

        BackendCryptoService.register_crypto_handler("SUITE_F", mock_factory)
        
        handler = BackendCryptoService.get_crypto_handler("SUITE_F")
        
        mock_global_config_get.assert_called_once()
        assert factory_call_args_storage.get('suite_id') == "SUITE_F"
        assert factory_call_args_storage.get('suite_config') == mock_suite_config_f
        assert handler is mock_handler_instance

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_005_get_active_encryption_handler(self, mocker):
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_global_config_get.return_value = {
            "data_at_rest": {"active_encryption_suite_id": "ACTIVE_SUITE", "suites": {"ACTIVE_SUITE": {"type": "MOCK"}}}
        }
        mock_active_handler = mocker.Mock(spec=CryptoHandler)
        BackendCryptoService.register_crypto_handler("ACTIVE_SUITE", mock_active_handler)
        
        handler = BackendCryptoService.get_active_encryption_handler()
        mock_global_config_get.assert_called_once()
        assert handler is mock_active_handler

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_006_get_active_encryption_handler_errors(self, mocker, caplog):
        caplog.set_level(logging.CRITICAL)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")

        mock_global_config_get.return_value = {"data_at_rest": {"active_encryption_suite_id": None}}
        with pytest.raises(ConfigurationError, match="Active encryption suite ID .* is not configured."):
            BackendCryptoService.get_active_encryption_handler()
        assert "Active encryption suite ID ('active_encryption_suite_id') is not configured." in caplog.text
        caplog.clear()

        mock_global_config_get.return_value = {"data_at_rest": {"active_encryption_suite_id": ""}}
        with pytest.raises(ConfigurationError, match="Active encryption suite ID .* is not configured."):
            BackendCryptoService.get_active_encryption_handler()
        assert "Active encryption suite ID ('active_encryption_suite_id') is not configured." in caplog.text
        caplog.clear()
        
        mock_global_config_get.return_value = {
            "data_at_rest": {"active_encryption_suite_id": "UNAVAILABLE_ACTIVE_SUITE"}
        }
        with pytest.raises(CriticalConfigurationError, match="Configured active encryption handler 'UNAVAILABLE_ACTIVE_SUITE' is not registered"):
            BackendCryptoService.get_active_encryption_handler()
        assert "Configured active encryption handler 'UNAVAILABLE_ACTIVE_SUITE' is not registered" in caplog.text


    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_007_get_configured_decryption_handlers_order(self, mocker):
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_global_config_get.return_value = {
            "data_at_rest": {"decryption_attempt_order": ["SUITE_B", "SUITE_A"], "suites": {"SUITE_A":{}, "SUITE_B":{}}}
        }
        mock_handler_A = mocker.Mock(spec=CryptoHandler)
        mock_handler_B = mocker.Mock(spec=CryptoHandler)
        
        BackendCryptoService.register_crypto_handler("SUITE_A", mock_handler_A)
        BackendCryptoService.register_crypto_handler("SUITE_B", mock_handler_B)
        
        handlers = BackendCryptoService.get_configured_decryption_handlers()
        mock_global_config_get.assert_called_once()
        assert handlers == [mock_handler_B, mock_handler_A]

    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_bcs_reg_008_get_configured_decryption_handlers_skip_unregistered(self, mocker, caplog):
        caplog.set_level(logging.WARNING)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_global_config_get.return_value = {
            "data_at_rest": {"decryption_attempt_order": ["REGISTERED_SUITE", "SKIPPED_SUITE"], "suites": {"REGISTERED_SUITE":{}}}
        }
        mock_handler_registered = mocker.Mock(spec=CryptoHandler)
        BackendCryptoService.register_crypto_handler("REGISTERED_SUITE", mock_handler_registered)
        
        handlers = BackendCryptoService.get_configured_decryption_handlers()
        assert handlers == [mock_handler_registered]
        assert "Crypto handler for suite_id 'SKIPPED_SUITE' (listed in 'decryption_attempt_order') not found/registered or unavailable." in caplog.text


class TestHybridPqcCryptoHandler:
    """ Test suite for HybridPqcCryptoHandler """
    suite_id = "HYBRID_K1_X25519_AES256GCM"
    valid_suite_config = {
        "classical_kem_algorithm": "X25519",
        "pqc_kem_algorithm": "ML-KEM-768",
        "symmetric_algorithm": "AES256GCM",
        "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512",
        "format_identifier": "FAVA_PQC_HYBRID_V1"
    }
    key_material_enc: KeyMaterialForEncryption = {
        "classical_recipient_pk": b"classical_pk_bytes",
        "pqc_recipient_pk": b"pqc_pk_bytes",
        "kdf_salt_for_passphrase_derived_keys": b"passphrase_salt_optional"
    }
    key_material_dec: KeyMaterialForDecryption = {
        "classical_recipient_sk": b"classical_sk_bytes",
        "pqc_recipient_sk": b"pqc_sk_bytes"
    }

    @pytest.mark.suite_specific_HYBRID_TEST # Note: pytest.mark.tags is not standard, using direct marker
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_hch_001_constructor(self, mocker):
        handler = HybridPqcCryptoHandler(self.suite_id, self.valid_suite_config)
        assert handler.get_suite_id() == self.suite_id
        assert handler.my_suite_config == self.valid_suite_config

        invalid_config = self.valid_suite_config.copy()
        del invalid_config["pqc_kem_algorithm"]
        with pytest.raises(ConfigurationError, match=r"requires .*pqc_kem_algorithm.*in suite configuration"):
            HybridPqcCryptoHandler(self.suite_id, invalid_config)

    @pytest.mark.suite_specific_HYBRID_TEST
    @pytest.mark.security_sensitive
    @pytest.mark.backend
    def test_tc_agl_hch_002_encrypt(self, mocker):
        mock_kem_lib = mocker.patch(KEM_LIB_PATH)
        mock_kdf_lib = mocker.patch(KDF_LIB_PATH)
        mock_sym_cipher_lib = mocker.patch(SYM_CIPHER_LIB_PATH)
        mock_util_lib = mocker.patch(UTIL_LIB_PATH)

        mock_kem_lib.hybrid_kem_classical_encapsulate.return_value = {"shared_secret": b"ss_classical", "ephemeral_public_key": b"epk_classical"}
        mock_kem_lib.pqc_kem_encapsulate.return_value = {"shared_secret": b"ss_pqc", "encapsulated_key": b"ek_pqc"}
        mock_util_lib.generate_random_bytes.side_effect = [b"kdf_salt_hybrid", b"iv_nonce_bytes"] # For KDF salt then IV
        mock_util_lib.get_symmetric_key_length.return_value = 32 # AES256
        mock_util_lib.get_iv_length.return_value = 12 # AES GCM IV
        mock_kdf_lib.derive.return_value = b"derived_symmetric_key_bytes_32"
        mock_sym_cipher_lib.encrypt_aead.return_value = {"ciphertext": b"ciphertext_final", "authentication_tag": b"auth_tag_final"}
        
        handler = HybridPqcCryptoHandler(self.suite_id, self.valid_suite_config)
        plaintext = b"super secret data"
        
        bundle = handler.encrypt(plaintext, self.key_material_enc)

        mock_kem_lib.hybrid_kem_classical_encapsulate.assert_called_once_with("X25519", b"classical_pk_bytes")
        mock_kem_lib.pqc_kem_encapsulate.assert_called_once_with("ML-KEM-768", b"pqc_pk_bytes")
        mock_util_lib.generate_random_bytes.assert_any_call(16) # kdf_salt_hybrid_sk
        mock_util_lib.generate_random_bytes.assert_any_call(12) # iv_nonce
        mock_kdf_lib.derive.assert_called_once_with(b"ss_classical" + b"ss_pqc", b"kdf_salt_hybrid", "HKDF-SHA3-512", 32, "FavaHybridSymmetricKey")
        mock_sym_cipher_lib.encrypt_aead.assert_called_once_with("AES256GCM", b"derived_symmetric_key_bytes_32", b"iv_nonce_bytes", plaintext, None)

        assert bundle["format_identifier"] == "FAVA_PQC_HYBRID_V1"
        assert bundle["suite_id_used"] == self.suite_id
        assert bundle["classical_kem_ephemeral_public_key"] == b"epk_classical"
        assert bundle["pqc_kem_encapsulated_key"] == b"ek_pqc"
        assert bundle["symmetric_cipher_iv_or_nonce"] == b"iv_nonce_bytes"
        assert bundle["encrypted_data_ciphertext"] == b"ciphertext_final"
        assert bundle["authentication_tag"] == b"auth_tag_final"
        assert bundle["kdf_salt_for_passphrase_derived_keys"] == b"passphrase_salt_optional"
        assert bundle["kdf_salt_for_hybrid_sk_derivation"] == b"kdf_salt_hybrid"


    @pytest.mark.suite_specific_HYBRID_TEST
    @pytest.mark.security_sensitive
    @pytest.mark.backend
    def test_tc_agl_hch_003_decrypt(self, mocker):
        mock_kem_lib = mocker.patch(KEM_LIB_PATH)
        mock_kdf_lib = mocker.patch(KDF_LIB_PATH)
        mock_sym_cipher_lib = mocker.patch(SYM_CIPHER_LIB_PATH)
        mock_util_lib = mocker.patch(UTIL_LIB_PATH) # For key length

        original_plaintext = b"super secret data"
        mock_kem_lib.hybrid_kem_classical_decapsulate.return_value = b"ss_classical"
        mock_kem_lib.pqc_kem_decapsulate.return_value = b"ss_pqc"
        mock_util_lib.get_symmetric_key_length.return_value = 32
        mock_kdf_lib.derive.return_value = b"derived_symmetric_key_bytes_32"
        mock_sym_cipher_lib.decrypt_aead.return_value = original_plaintext

        handler = HybridPqcCryptoHandler(self.suite_id, self.valid_suite_config)
        
        # Construct a bundle that would be passed to decrypt
        bundle_to_decrypt: HybridEncryptedBundle = {
            "format_identifier": "FAVA_PQC_HYBRID_V1",
            "suite_id_used": self.suite_id,
            "classical_kem_ephemeral_public_key": b"epk_classical",
            "pqc_kem_encapsulated_key": b"ek_pqc",
            "symmetric_cipher_iv_or_nonce": b"iv_nonce_bytes",
            "encrypted_data_ciphertext": b"ciphertext_final",
            "authentication_tag": b"auth_tag_final",
            "kdf_salt_for_passphrase_derived_keys": b"passphrase_salt_optional",
            "kdf_salt_for_hybrid_sk_derivation": b"kdf_salt_hybrid_from_bundle"
        }

        decrypted_text = handler.decrypt(bundle_to_decrypt, self.key_material_dec)

        mock_kem_lib.hybrid_kem_classical_decapsulate.assert_called_once_with("X25519", b"epk_classical", b"classical_sk_bytes")
        mock_kem_lib.pqc_kem_decapsulate.assert_called_once_with("ML-KEM-768", b"ek_pqc", b"pqc_sk_bytes")
        mock_kdf_lib.derive.assert_called_once_with(b"ss_classical" + b"ss_pqc", b"kdf_salt_hybrid_from_bundle", "HKDF-SHA3-512", 32, "FavaHybridSymmetricKey")
        mock_sym_cipher_lib.decrypt_aead.assert_called_once_with("AES256GCM", b"derived_symmetric_key_bytes_32", b"iv_nonce_bytes", b"ciphertext_final", b"auth_tag_final", None)
        assert decrypted_text == original_plaintext

    @pytest.mark.suite_specific_HYBRID_TEST
    @pytest.mark.error_handling
    @pytest.mark.security_sensitive
    @pytest.mark.backend
    def test_tc_agl_hch_004_decrypt_tampered_data(self, mocker):
        mock_kem_lib = mocker.patch(KEM_LIB_PATH)
        mock_kdf_lib = mocker.patch(KDF_LIB_PATH)
        mock_util_lib = mocker.patch(UTIL_LIB_PATH)
        mock_sym_cipher_lib = mocker.patch(SYM_CIPHER_LIB_PATH)
        
        mock_kem_lib.hybrid_kem_classical_decapsulate.return_value = b"ss_classical"
        mock_kem_lib.pqc_kem_decapsulate.return_value = b"ss_pqc"
        mock_util_lib.get_symmetric_key_length.return_value = 32
        mock_kdf_lib.derive.return_value = b"derived_symmetric_key_bytes_32"
        mock_sym_cipher_lib.decrypt_aead.return_value = None # Simulate AEAD failure

        handler = HybridPqcCryptoHandler(self.suite_id, self.valid_suite_config)
        bundle_to_decrypt: HybridEncryptedBundle = {
            "format_identifier": "FAVA_PQC_HYBRID_V1", "suite_id_used": self.suite_id,
            "classical_kem_ephemeral_public_key": b"epk", "pqc_kem_encapsulated_key": b"ek",
            "symmetric_cipher_iv_or_nonce": b"iv", "encrypted_data_ciphertext": b"ct",
            "authentication_tag": b"tag", "kdf_salt_for_passphrase_derived_keys": None,
            "kdf_salt_for_hybrid_sk_derivation": b"salt"
        }
        with pytest.raises(DecryptionError, match="Symmetric decryption failed: authentication tag mismatch or corrupted data."):
            handler.decrypt(bundle_to_decrypt, self.key_material_dec)
        mock_sym_cipher_lib.decrypt_aead.assert_called_once()


class TestHashingProvider:
    """ Test suite for HashingProvider """
    def setup_method(self):
        GlobalConfig.reset_cache()

    @pytest.mark.config_dependent
    @pytest.mark.backend
    @pytest.mark.parametrize("algo_name, expected_hasher_class_name", [
        ("SHA3-256", "SHA3_256HasherImpl"),
        ("SHA256", "SHA256HasherImpl"),
    ])
    def test_tc_agl_hp_001_get_configured_hasher(self, mocker, algo_name, expected_hasher_class_name):
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_global_config_get.return_value = {"hashing": {"default_algorithm": algo_name}}
        
        mock_hasher_instance = mocker.Mock(spec=HasherInterface)
        mock_internal_get_hasher = mocker.patch.object(HashingProvider, "_get_hasher_instance", return_value=mock_hasher_instance)

        hasher = HashingProvider.get_configured_hasher()

        mock_global_config_get.assert_called_once()
        mock_internal_get_hasher.assert_called_once_with(algo_name)
        assert hasher is mock_hasher_instance

    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_hp_002_get_configured_hasher_fallback(self, mocker, caplog):
        caplog.set_level(logging.WARNING)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        mock_global_config_get.return_value = {"hashing": {"default_algorithm": "UNAVAILABLE_HASH"}}
        mock_sha3_hasher = mocker.Mock(spec=HasherInterface)
        def get_hasher_side_effect(algo):
            if algo == "UNAVAILABLE_HASH":
                raise AlgorithmUnavailableError("Mocked unavailable")
            elif algo == "SHA3-256":
                return mock_sha3_hasher
            pytest.fail(f"Unexpected algo in _get_hasher_instance mock: {algo}")

        mock_internal_get_hasher = mocker.patch.object(HashingProvider, "_get_hasher_instance", side_effect=get_hasher_side_effect)
        
        hasher = HashingProvider.get_configured_hasher()

        assert mock_internal_get_hasher.call_count == 2
        mock_internal_get_hasher.assert_any_call("UNAVAILABLE_HASH")
        mock_internal_get_hasher.assert_any_call("SHA3-256")
        assert hasher is mock_sha3_hasher
        assert "Configured hash algorithm 'UNAVAILABLE_HASH' is unavailable" in caplog.text
        assert "Attempting fallback to SHA3-256." in caplog.text


class TestDecryptionOrchestration:
    """ Test suite for Decryption Orchestration """
    def setup_method(self):
        BackendCryptoService.reset_registry_for_testing()
        GlobalConfig.reset_cache()

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_do_001_decrypt_data_at_rest_agility(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mock_parse_header = mocker.patch(PARSE_BUNDLE_HEADER_PATH)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")
        
        raw_encrypted_bytes = b"encrypted_data_with_header"
        key_material_input = {"classical_recipient_sk": b"sk1", "pqc_recipient_sk": b"sk2"}
        
        # Header parsing identifies SUITE_FROM_HEADER
        mock_bundle_from_header: HybridEncryptedBundle = {
            "format_identifier": "V1", "suite_id_used": "SUITE_FROM_HEADER",
            "classical_kem_ephemeral_public_key": b"epk", "pqc_kem_encapsulated_key": b"ek",
            "symmetric_cipher_iv_or_nonce": b"iv", "encrypted_data_ciphertext": b"ct",
            "authentication_tag": b"tag", "kdf_salt_for_passphrase_derived_keys": None,
            "kdf_salt_for_hybrid_sk_derivation": b"salt"
        }
        mock_parse_header.return_value = {"was_successful": True, "suite_id": "SUITE_FROM_HEADER", "bundle_object": mock_bundle_from_header}
        
        # Config for decryption order and suite details
        mock_global_config_get.return_value = {
            "data_at_rest": {
                "decryption_attempt_order": ["LEGACY_SUITE_1", "SUITE_FROM_HEADER"], # SUITE_FROM_HEADER is also in list
                "suites": {
                    "SUITE_FROM_HEADER": {"type": "HYBRID", "param": "val_header"},
                    "LEGACY_SUITE_1": {"type": "LEGACY", "param": "val_legacy1"}
                }
            }
        }

        # Mock handlers
        mock_handler_from_header_target = mocker.Mock(spec=CryptoHandler)
        mock_handler_from_header_target.get_suite_id.return_value = "SUITE_FROM_HEADER"
        mock_handler_from_header_target.decrypt.side_effect = DecryptionError("Targeted SUITE_FROM_HEADER failed initially")

        mock_handler_legacy1 = mocker.Mock(spec=CryptoHandler)
        mock_handler_legacy1.get_suite_id.return_value = "LEGACY_SUITE_1"
        mock_handler_legacy1.decrypt.side_effect = DecryptionError("LEGACY_SUITE_1 failed")
        
        mock_handler_header_from_list = mocker.Mock(spec=CryptoHandler) # This one will succeed
        mock_handler_header_from_list.get_suite_id.return_value = "SUITE_FROM_HEADER"
        expected_plaintext = b"success_plaintext"
        mock_handler_header_from_list.decrypt.return_value = expected_plaintext

        # Setup BackendCryptoService registry for GetCryptoHandler and GetConfiguredDecryptionHandlers
        # GetCryptoHandler will be called for the targeted attempt
        mocker.patch.object(BackendCryptoService, 'get_crypto_handler', side_effect=lambda sid: {
            "SUITE_FROM_HEADER": mock_handler_from_header_target, # For targeted attempt
        }.get(sid, AlgorithmNotFoundError(f"No handler for {sid} in direct GetCryptoHandler mock")))
        
        # GetConfiguredDecryptionHandlers will return handlers for the iteration
        mocker.patch.object(BackendCryptoService, 'get_configured_decryption_handlers', return_value=[mock_handler_legacy1, mock_handler_header_from_list])

        plaintext = decrypt_data_at_rest_with_agility(raw_encrypted_bytes, key_material_input)

        mock_parse_header.assert_called_once_with(raw_encrypted_bytes)
        # Targeted attempt
        BackendCryptoService.get_crypto_handler.assert_any_call("SUITE_FROM_HEADER")
        mock_handler_from_header_target.decrypt.assert_called_once_with(mock_bundle_from_header, key_material_input, {"type": "HYBRID", "param": "val_header"})
        assert "Targeted decryption with handler 'SUITE_FROM_HEADER' failed" in caplog.text
        
        # Iteration attempts
        BackendCryptoService.get_configured_decryption_handlers.assert_called_once()
        mock_handler_legacy1.decrypt.assert_called_once_with(mock_bundle_from_header, key_material_input, {"type": "LEGACY", "param": "val_legacy1"})
        assert "Decryption with handler 'LEGACY_SUITE_1' failed" in caplog.text
        
        mock_handler_header_from_list.decrypt.assert_called_once_with(mock_bundle_from_header, key_material_input, {"type": "HYBRID", "param": "val_header"})
        assert plaintext == expected_plaintext


    @pytest.mark.error_handling
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_do_002_decrypt_data_at_rest_all_fail(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mock_parse_header = mocker.patch(PARSE_BUNDLE_HEADER_PATH)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_PATH}.get_crypto_settings")

        raw_bytes = b"some_data_all_fail"
        key_material = {"classical_recipient_sk": b"sk1", "pqc_recipient_sk": b"sk2"}
        
        mock_bundle_obj: HybridEncryptedBundle = {
            "format_identifier": "V1", "suite_id_used": "UNKNOWN_SUITE_IN_HEADER", # or parsing fails
            "classical_kem_ephemeral_public_key": b"epk", "pqc_kem_encapsulated_key": b"ek",
            "symmetric_cipher_iv_or_nonce": b"iv", "encrypted_data_ciphertext": b"ct",
            "authentication_tag": b"tag", "kdf_salt_for_passphrase_derived_keys": None,
            "kdf_salt_for_hybrid_sk_derivation": b"salt"
        }
        # Simulate header parsing failing or returning a suite not directly handled by targeted attempt
        mock_parse_header.return_value = {"was_successful": True, "suite_id": "UNKNOWN_SUITE_IN_HEADER", "bundle_object": mock_bundle_obj}

        mock_global_config_get.return_value = {
             "data_at_rest": {
                "decryption_attempt_order": ["FAIL_HANDLER_1", "FAIL_HANDLER_2"],
                "suites": {
                    "FAIL_HANDLER_1": {"type":"TYPE1"}, "FAIL_HANDLER_2": {"type":"TYPE2"}
                }
            }
        }

        mock_handler1 = mocker.Mock(spec=CryptoHandler)
        mock_handler1.get_suite_id.return_value = "FAIL_HANDLER_1"
        mock_handler1.decrypt.side_effect = DecryptionError("Handler1 failed")
        
        mock_handler2 = mocker.Mock(spec=CryptoHandler)
        mock_handler2.get_suite_id.return_value = "FAIL_HANDLER_2"
        mock_handler2.decrypt.side_effect = DecryptionError("Handler2 failed")

        # Targeted attempt for UNKNOWN_SUITE_IN_HEADER will fail due to AlgorithmNotFoundError
        mocker.patch.object(BackendCryptoService, 'get_crypto_handler', side_effect=AlgorithmNotFoundError)
        mocker.patch.object(BackendCryptoService, 'get_configured_decryption_handlers', return_value=[mock_handler1, mock_handler2])
        
        with pytest.raises(DecryptionError, match="Unable to decrypt data: No configured cryptographic suite succeeded."):
            decrypt_data_at_rest_with_agility(raw_bytes, key_material)
        
        mock_handler1.decrypt.assert_called_once()
        mock_handler2.decrypt.assert_called_once()
        assert "All configured decryption attempts failed for the provided data." in caplog.text