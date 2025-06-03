import pytest
from unittest import mock

# Import mocks from the new location
from .mocks import (
    MockOQS_KeyEncapsulation,
    MockX25519PrivateKey,
    MockX25519PublicKey,
    MockAESGCM
)
# Import fixtures from the new location
from .fixtures import mock_crypto_libs, mock_fava_config


@pytest.mark.usefixtures("mock_crypto_libs", "mock_fava_config")
class TestHybridPqcHandler:
    """
    Tests for 5.2. HybridPqcHandler (fava.crypto.handlers.HybridPqcHandler)
    """
    @pytest.fixture(autouse=True)
    def _reset_mock_aesgcm_state_fixture(self):
        MockAESGCM.reset_correct_key_for_test()
        yield
        MockAESGCM.reset_correct_key_for_test()

    @pytest.fixture
    def hybrid_handler(self):
        from fava.crypto.handlers import HybridPqcHandler
        return HybridPqcHandler()


    @pytest.mark.config_dependent
    def test_tp_dar_hph_001_can_handle_by_extension(self, hybrid_handler, mock_fava_config):
        assert hybrid_handler.can_handle("data.bc.pqc_hybrid_fava", None, mock_fava_config) is True
        assert hybrid_handler.can_handle("data.bc.gpg", None, mock_fava_config) is False
        assert hybrid_handler.can_handle("data.bc", None, mock_fava_config) is False

    @pytest.mark.config_dependent
    @pytest.mark.bundle_format
    @mock.patch('fava.core.encrypted_file_bundle.EncryptedFileBundle.parse_header_only')
    def test_tp_dar_hph_002_can_handle_by_magic_bytes(self, mock_parse_header, hybrid_handler, mock_fava_config):
        mock_parse_header.return_value = {"format_identifier": "FAVA_PQC_HYBRID_V1"}
        assert hybrid_handler.can_handle("file.ext", b'FAVA_PQC_HYBRID_V1_HEADER_START...', mock_fava_config) is True
        
        mock_parse_header.return_value = None
        assert hybrid_handler.can_handle("file.ext", b'OTHER_FORMAT...', mock_fava_config) is False

    @pytest.mark.critical_path
    @pytest.mark.performance_smoke
    def test_tp_dar_hph_003_encrypt_decrypt_success(self, hybrid_handler, mock_fava_config):
        plaintext = "This is secret Beancount data."
        suite_config = { "id": "X25519_KYBER768_AES256GCM", "classical_kem_algorithm": "X25519",
                         "pqc_kem_algorithm": "ML-KEM-768", "symmetric_algorithm": "AES256GCM",
                         "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512" }
        
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes")
        mock_pqc_pk_bytes_correct_size = b'A' * 1184
        mock_pqc_pk = mock_pqc_pk_bytes_correct_size

        mock_classical_sk = MockX25519PrivateKey(b"mock_classical_sk_bytes")
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
        
        encrypted_bundle = hybrid_handler.encrypt_content(plaintext, suite_config, key_material_encrypt, mock_fava_config)
        decrypted_content = hybrid_handler.decrypt_content(encrypted_bundle, suite_config, key_material_decrypt, mock_fava_config)
        assert decrypted_content == plaintext

    @pytest.mark.config_dependent
    @mock.patch('fava.crypto.handlers.KeyEncapsulation')
    def test_tp_dar_hph_004_encrypt_uses_suite_config(self, mock_key_encapsulation_class_in_handler, hybrid_handler, mock_fava_config):
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes")
        mock_pqc_pk_correct_size = b'B' * 1184
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk_correct_size
        }

        suite_config_kyber768 = { "id": "X25519_KYBER768_AES256GCM",
                                  "pqc_kem_algorithm": "ML-KEM-768",
                                }
        
        mock_kem_instance = mock_key_encapsulation_class_in_handler.return_value
        mock_kem_instance.encap_secret.return_value = (b"mock_ss", b"mock_ct")

        hybrid_handler.encrypt_content("plaintext", suite_config_kyber768, key_material_encrypt, mock_fava_config)
        
        mock_key_encapsulation_class_in_handler.assert_called_once_with("ML-KEM-768")
        mock_kem_instance.encap_secret.assert_called_once_with(mock_pqc_pk_correct_size)
        mock_key_encapsulation_class_in_handler.reset_mock()

        suite_config_kyber1024 = { "id": "X25519_KYBER1024_AES256GCM",
                                   "pqc_kem_algorithm": "ML-KEM-1024",
                                 }
        hybrid_handler.encrypt_content("plaintext", suite_config_kyber1024, key_material_encrypt, mock_fava_config)
        mock_key_encapsulation_class_in_handler.assert_called_with("ML-KEM-1024")

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.KeyEncapsulation')
    def test_tp_dar_hph_005_pqc_kem_encapsulation(self, mock_key_encapsulation_class_in_handler, hybrid_handler, mock_fava_config):
        plaintext = "test data"
        pqc_pk_bytes = b"mock_pqc_public_key_for_encap_test"
        
        key_material_encrypt = {
            "classical_public_key": MockX25519PublicKey(b"mock_classical_pk_bytes"),
            "pqc_public_key": pqc_pk_bytes
        }
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM",
            "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519",
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }
        mock_kem_instance = mock_key_encapsulation_class_in_handler.return_value
        mock_kem_instance.encap_secret.return_value = (b"mock_pqc_ss_from_encap", b"mock_pqc_ct_from_encap")

        hybrid_handler.encrypt_content(plaintext, suite_config, key_material_encrypt, mock_fava_config)

        mock_key_encapsulation_class_in_handler.assert_called_with("ML-KEM-768")
        mock_kem_instance.encap_secret.assert_called_once_with(pqc_pk_bytes)

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.HKDFExpand')
    @mock.patch('fava.crypto.handlers.KeyEncapsulation')
    def test_tp_dar_hph_006_hybrid_kem_symmetric_key_derivation(self, mock_key_encapsulation_class, mock_hkdf_class_in_handler, hybrid_handler, mock_fava_config):
        mock_pqc_ss = b"fixed_pqc_ss_for_hkdf_test"
        
        mock_classical_pk = MockX25519PublicKey(b"mock_classical_pk_bytes_for_hkdf")
        mock_pqc_pk_correct_size = b'C' * 1184
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk_correct_size
        }
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM",
            "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519",
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }

        mock_pqc_kem_instance = mock_key_encapsulation_class.return_value
        mock_pqc_kem_instance.encap_secret.return_value = (mock_pqc_ss, b"mock_pqc_ct_for_hkdf")

        mock_hkdf_instance = mock_hkdf_class_in_handler.return_value
        mock_hkdf_instance.derive.return_value = b"k" * 32
        
        actual_classical_ss_from_mock = b"ss_x25519_" + b"defau" + b"_" + b"mock_"
        expected_combined_secret_for_derive = actual_classical_ss_from_mock + mock_pqc_ss

        hybrid_handler.encrypt_content("test_plaintext_for_hkdf", suite_config, key_material_encrypt, mock_fava_config)

        mock_hkdf_class_in_handler.assert_called_once()
        mock_hkdf_instance.derive.assert_called_once_with(expected_combined_secret_for_derive)

    @pytest.mark.critical_path
    @mock.patch('fava.crypto.handlers.AESGCM')
    @mock.patch('fava.crypto.handlers.os.urandom')
    @mock.patch('fava.crypto.handlers.KeyEncapsulation')
    @mock.patch('fava.crypto.handlers.HKDFExpand')
    def test_tp_dar_hph_007_aes_gcm_encryption_produces_tag_iv(
        self, mock_hkdf_class, mock_key_encap_class, mock_os_urandom,
        mock_aesgcm_class_in_handler, hybrid_handler, mock_fava_config
    ):
        plaintext_str = "secret symmetric data"
        mock_derived_symmetric_key = b'k' * 32
        mock_iv = b'i' * 12
        mock_actual_ciphertext = b'c' * len(plaintext_str)
        mock_auth_tag = b't' * 16
        
        mock_pqc_kem_instance = mock_key_encap_class.return_value
        mock_pqc_kem_instance.encap_secret.return_value = (b"mock_pqc_ss_for_aes", b"mock_pqc_ct_for_aes")

        mock_hkdf_instance = mock_hkdf_class.return_value
        mock_hkdf_instance.derive.return_value = mock_derived_symmetric_key

        mock_os_urandom.return_value = mock_iv

        mock_aesgcm_instance = mock_aesgcm_class_in_handler.return_value
        mock_aesgcm_instance.encrypt.return_value = mock_actual_ciphertext + mock_auth_tag

        suite_config = {
            "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519", "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }
        key_material_encrypt = {
            "classical_public_key": MockX25519PublicKey(b"mock_classical_pk_for_aes"),
            "pqc_public_key": b'P' * 1184
        }

        with mock.patch('fava.crypto.handlers.EncryptedFileBundle', autospec=True) as mock_bundle_class:
            mock_bundle_instance = mock_bundle_class.return_value
            _ = hybrid_handler.encrypt_content(plaintext_str, suite_config, key_material_encrypt, mock_fava_config)

            mock_aesgcm_class_in_handler.assert_called_once_with(mock_derived_symmetric_key)
            mock_aesgcm_instance.encrypt.assert_called_once_with(mock_iv, plaintext_str.encode('utf-8'), associated_data=None)
            
            assert mock_bundle_instance.symmetric_iv == mock_iv
            assert mock_bundle_instance.symmetric_ciphertext == mock_actual_ciphertext
            assert mock_bundle_instance.symmetric_auth_tag == mock_auth_tag
            assert mock_bundle_instance.pqc_kem_ciphertext == b"mock_pqc_ct_for_aes"
            expected_classical_kem_ct = b"default_generated_private_key_direct_in_generate"
            assert mock_bundle_instance.classical_kem_ciphertext == expected_classical_kem_ct
            assert mock_bundle_instance.format_identifier == "FAVA_PQC_HYBRID_V1"
            assert mock_bundle_instance.suite_id == suite_config["id"]

    @pytest.mark.error_handling
    @pytest.mark.critical_path
    def test_tp_dar_hph_008_decrypt_fails_wrong_key(self, hybrid_handler, mock_fava_config):
        from fava.crypto.exceptions import DecryptionError

        plaintext = "secret data for wrong key test"
        suite_config = {
            "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768",
            "classical_kem_algorithm": "X25519", "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512"
        }

        key_material_encrypt_A = {
            "classical_public_key": MockX25519PublicKey(b"classical_pk_A_recipient"),
            "pqc_public_key": b'A_pqc_pk_recipient' * (1184 // len(b'A_pqc_pk_recipient'))
        }
        
        encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt_A, mock_fava_config
        )

        key_material_decrypt_B = {
            "classical_private_key": MockX25519PrivateKey(b"classical_sk_B_DIFFERENT"),
            "pqc_private_key": b'B_pqc_sk_DIFFERENT' * (2400 // len(b'B_pqc_sk_DIFFERENT'))
        }

        with pytest.raises(DecryptionError) as excinfo:
            hybrid_handler.decrypt_content(
                encrypted_bundle_bytes, suite_config, key_material_decrypt_B, mock_fava_config
            )
        
        assert "Simulated AESGCM InvalidTag" in str(excinfo.value) or \
               "Decryption failed due to value error" in str(excinfo.value)

    @pytest.mark.error_handling
    @pytest.mark.bundle_format
    def test_tp_dar_hph_009_decrypt_fails_tampered_ciphertext_tag(self, hybrid_handler, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle
        from fava.crypto.exceptions import DecryptionError

        plaintext = "data to test tampering"
        suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        
        mock_classical_pk = MockX25519PublicKey(b"classical_pk_for_tamper_test")
        mock_pqc_pk = b'P' * 1184
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk,
            "pqc_public_key": mock_pqc_pk
        }
        mock_classical_sk = MockX25519PrivateKey(b"classical_pk_for_tamper_test")
        mock_pqc_sk = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk,
            "pqc_private_key": mock_pqc_sk
        }

        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt, mock_fava_config
        )
        
        bundle_tamper_ct = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_ct.symmetric_ciphertext) > 0:
            original_byte = bundle_tamper_ct.symmetric_ciphertext[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_ct.symmetric_ciphertext = bytes([tampered_byte]) + bundle_tamper_ct.symmetric_ciphertext[1:]
        else:
            bundle_tamper_ct.symmetric_ciphertext = b"tampered"
        tampered_ct_bytes = bundle_tamper_ct.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_ct:
            hybrid_handler.decrypt_content(tampered_ct_bytes, suite_config, key_material_decrypt, mock_fava_config)
        assert "Decryption failed due to value error" in str(excinfo_ct.value) or "InvalidTag" in str(excinfo_ct.value)


        bundle_tamper_tag = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        if len(bundle_tamper_tag.symmetric_auth_tag) > 0:
            original_byte = bundle_tamper_tag.symmetric_auth_tag[0]
            tampered_byte = (original_byte + 1) % 256
            bundle_tamper_tag.symmetric_auth_tag = bytes([tampered_byte]) + bundle_tamper_tag.symmetric_auth_tag[1:]
        else:
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
        
        mock_classical_pk_recipient = MockX25519PublicKey(b"classical_pk_recipient_for_kem_corruption")
        mock_pqc_pk_recipient_bytes = b'P_rcp' * (1184 // len(b'P_rcp')) + b'P' * (1184 % len(b'P_rcp'))
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk_recipient,
            "pqc_public_key": mock_pqc_pk_recipient_bytes
        }

        mock_classical_sk_recipient = MockX25519PrivateKey(b"classical_pk_recipient_for_kem_corruption")
        mock_pqc_sk_recipient_bytes = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct
        key_material_decrypt = {
            "classical_private_key": mock_classical_sk_recipient,
            "pqc_private_key": mock_pqc_sk_recipient_bytes
        }

        original_encap_mock = MockOQS_KeyEncapsulation._mock_encapsulate_class
        MockOQS_KeyEncapsulation._mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class"))
        
        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, suite_config, key_material_encrypt, mock_fava_config
        )
        MockOQS_KeyEncapsulation._mock_encapsulate_class = original_encap_mock

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
        assert "Decryption failed due to value error" in str(excinfo_classical.value) or "InvalidTag" in str(excinfo_classical.value)


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
        assert "Decryption failed due to value error" in str(excinfo_pqc.value) or "InvalidTag" in str(excinfo_pqc.value)

    @pytest.mark.bundle_format
    @pytest.mark.critical_path
    def test_tp_dar_hph_011_encrypted_bundle_parser(self, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle

        original_bundle = EncryptedFileBundle()
        original_bundle.format_identifier = "FAVA_PQC_HYBRID_V1"
        original_bundle.suite_id = "X25519_KYBER768_AES256GCM_TEST"
        original_bundle.classical_kem_ciphertext = b"classical_ct_test_bytes"
        original_bundle.pqc_kem_ciphertext = b"pqc_ct_test_bytes_longer"
        original_bundle.symmetric_iv = b"iv_12_bytes123"
        original_bundle.symmetric_ciphertext = b"encrypted_symmetric_data_payload"
        original_bundle.symmetric_auth_tag = b"auth_tag_16bytes"

        serialized_bundle_bytes = original_bundle.to_bytes()
        parsed_bundle = EncryptedFileBundle.from_bytes(serialized_bundle_bytes)

        assert parsed_bundle.format_identifier == original_bundle.format_identifier
        assert parsed_bundle.suite_id == original_bundle.suite_id
        assert parsed_bundle.classical_kem_ciphertext == original_bundle.classical_kem_ciphertext
        assert parsed_bundle.pqc_kem_ciphertext == original_bundle.pqc_kem_ciphertext
        assert parsed_bundle.symmetric_iv == original_bundle.symmetric_iv
        assert parsed_bundle.symmetric_ciphertext == original_bundle.symmetric_ciphertext
        assert parsed_bundle.symmetric_auth_tag == original_bundle.symmetric_auth_tag

        empty_bundle = EncryptedFileBundle()
        empty_bundle.format_identifier = "EMPTY_TEST_V0"
        empty_bundle.suite_id = "EMPTY_SUITE_ID"

        serialized_empty_bundle = empty_bundle.to_bytes()
        parsed_empty_bundle = EncryptedFileBundle.from_bytes(serialized_empty_bundle)

        assert parsed_empty_bundle.format_identifier == empty_bundle.format_identifier
        assert parsed_empty_bundle.suite_id == empty_bundle.suite_id
        assert parsed_empty_bundle.classical_kem_ciphertext == b""
        assert parsed_empty_bundle.pqc_kem_ciphertext == b""
        assert parsed_empty_bundle.symmetric_iv == b""
        assert parsed_empty_bundle.symmetric_ciphertext == b""
        assert parsed_empty_bundle.symmetric_auth_tag == b""

        with pytest.raises(ValueError, match="Data too short to read length prefix."):
            EncryptedFileBundle.from_bytes(b"\x01\x00\x00")

        with pytest.raises(ValueError, match="Data too short to read field content."):
            EncryptedFileBundle.from_bytes(b"\x05\x00\x00\x00abc")

    @pytest.mark.error_handling
    @pytest.mark.bundle_format
    @pytest.mark.config_dependent
    def test_tp_dar_hph_012_decrypt_fails_mismatched_suite_format_id(self, hybrid_handler, mock_fava_config):
        from fava.core.encrypted_file_bundle import EncryptedFileBundle
        from fava.crypto.exceptions import DecryptionError

        plaintext = "data for suite/format ID mismatch test"
        
        correct_suite_config = mock_fava_config.pqc_suites[mock_fava_config.pqc_active_suite_id]
        
        mock_classical_pk_recipient = MockX25519PublicKey(b"classical_pk_recipient_for_mismatch_test")
        mock_pqc_pk_recipient_bytes = b'P_rcp_mm' * (1184 // len(b'P_rcp_mm')) + b'P' * (1184 % len(b'P_rcp_mm'))
        key_material_encrypt = {
            "classical_public_key": mock_classical_pk_recipient,
            "pqc_public_key": mock_pqc_pk_recipient_bytes
        }
        mock_classical_sk_recipient = MockX25519PrivateKey(b"classical_pk_recipient_for_mismatch_test")
        mock_pqc_sk_recipient_bytes = MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct
        key_material_decrypt = { # Corrected indentation for the dictionary
            "classical_private_key": mock_classical_sk_recipient,
            "pqc_private_key": mock_pqc_sk_recipient_bytes
        } # Ensure this closing brace is correctly placed and indented with the `key_material_decrypt` dict.
        original_encap_mock = MockOQS_KeyEncapsulation._mock_encapsulate_class
        MockOQS_KeyEncapsulation._mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class"))
        valid_encrypted_bundle_bytes = hybrid_handler.encrypt_content(
            plaintext, correct_suite_config, key_material_encrypt, mock_fava_config
        )
        MockOQS_KeyEncapsulation._mock_encapsulate_class = original_encap_mock


        bundle_mismatched_suite = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        bundle_mismatched_suite.suite_id = "DIFFERENT_SUITE_ID_XYZ"
        mismatched_suite_bytes = bundle_mismatched_suite.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_suite:
            hybrid_handler.decrypt_content(mismatched_suite_bytes, correct_suite_config, key_material_decrypt, mock_fava_config)
        assert f"Mismatched suite ID. Bundle: DIFFERENT_SUITE_ID_XYZ, Config: {correct_suite_config['id']}" in str(excinfo_suite.value)

        bundle_mismatched_format = EncryptedFileBundle.from_bytes(valid_encrypted_bundle_bytes)
        bundle_mismatched_format.format_identifier = "FAVA_PQC_HYBRID_V0_OLD"
        mismatched_format_bytes = bundle_mismatched_format.to_bytes()

        with pytest.raises(DecryptionError) as excinfo_format:
            hybrid_handler.decrypt_content(mismatched_format_bytes, correct_suite_config, key_material_decrypt, mock_fava_config)
        assert f"Unsupported bundle format: FAVA_PQC_HYBRID_V0_OLD" in str(excinfo_format.value)