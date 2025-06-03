import pytest
from unittest import mock

# Import fixtures from the new location
from .fixtures import mock_fava_config


@pytest.mark.usefixtures("mock_fava_config")
class TestCryptoServiceLocator:
    """
    Tests for 5.4. CryptoServiceLocator (fava.crypto.locator.CryptoServiceLocator)
    """
    @pytest.fixture
    def mock_hybrid_handler_instance(self):
        handler = mock.Mock(spec_set=['can_handle', 'encrypt_content', 'decrypt_content', 'name'])
        handler.name = "HybridPqcHandler"
        return handler

    @pytest.fixture
    def mock_gpg_handler_instance(self):
        handler = mock.Mock(spec_set=['can_handle', 'decrypt_content', 'name'])
        handler.name = "GpgHandler"
        return handler

    @pytest.fixture
    def crypto_locator(self, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        from fava.crypto.locator import CryptoServiceLocator
        return CryptoServiceLocator(handlers=[mock_hybrid_handler_instance, mock_gpg_handler_instance], app_config=mock_fava_config)


    @pytest.mark.config_dependent
    @pytest.mark.critical_path
    def test_tp_dar_csl_001_selects_pqc_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = True
        mock_gpg_handler_instance.can_handle.return_value = False
        mock_fava_config.pqc_data_at_rest_enabled = True

        handler = crypto_locator.get_handler_for_file("file.pqc_hybrid_fava", b"FAVA_PQC_HYBRID_V1_PEEK", mock_fava_config)
        assert handler is mock_hybrid_handler_instance
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("file.pqc_hybrid_fava", b"FAVA_PQC_HYBRID_V1_PEEK", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_not_called()

    @pytest.mark.config_dependent
    @pytest.mark.gpg_compatibility
    def test_tp_dar_csl_002_selects_gpg_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = False
        mock_gpg_handler_instance.can_handle.return_value = True
        mock_fava_config.pqc_fallback_to_classical_gpg = True

        handler = crypto_locator.get_handler_for_file("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)
        assert handler is mock_gpg_handler_instance
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_called_once_with("file.gpg", b"GPG_MAGIC_BYTES_PEEK", mock_fava_config)

    @pytest.mark.config_dependent
    def test_tp_dar_csl_003_handler_prioritization(self, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        from fava.crypto.locator import CryptoServiceLocator
        
        mock_hybrid_handler_instance.can_handle.return_value = True
        mock_gpg_handler_instance.can_handle.return_value = True
        mock_fava_config.pqc_data_at_rest_enabled = True
        mock_fava_config.pqc_fallback_to_classical_gpg = True

        locator = CryptoServiceLocator(handlers=[mock_hybrid_handler_instance, mock_gpg_handler_instance], app_config=mock_fava_config)
        
        handler = locator.get_handler_for_file("some_file.any_ext", b"some_peek_data", mock_fava_config)
        assert handler is mock_hybrid_handler_instance
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("some_file.any_ext", b"some_peek_data", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_not_called()

    @pytest.mark.error_handling
    def test_tp_dar_csl_004_no_handler_matches(self, crypto_locator, mock_hybrid_handler_instance, mock_gpg_handler_instance, mock_fava_config):
        mock_hybrid_handler_instance.can_handle.return_value = False
        mock_gpg_handler_instance.can_handle.return_value = False

        result = crypto_locator.get_handler_for_file("unknown.file", b"unknown_peek_data", mock_fava_config)
        assert result is None
        mock_hybrid_handler_instance.can_handle.assert_called_once_with("unknown.file", b"unknown_peek_data", mock_fava_config)
        mock_gpg_handler_instance.can_handle.assert_called_once_with("unknown.file", b"unknown_peek_data", mock_fava_config)

    @pytest.mark.config_dependent
    def test_tp_dar_csl_005_get_pqc_encrypt_handler(self, crypto_locator, mock_hybrid_handler_instance, mock_fava_config):
        suite_config = { "id": "X25519_KYBER768_AES256GCM", "pqc_kem_algorithm": "ML-KEM-768" }
        
        mock_fava_config.pqc_data_at_rest_enabled = True
        handler = crypto_locator.get_pqc_encrypt_handler(suite_config, mock_fava_config)
        assert handler is mock_hybrid_handler_instance

        mock_fava_config.pqc_data_at_rest_enabled = False
        handler_disabled = crypto_locator.get_pqc_encrypt_handler(suite_config, mock_fava_config)
        assert handler_disabled is None