import pytest
from unittest import mock

# Import fixtures from the new location
from tests.granular.pqc_data_at_rest.fixtures import mock_fava_config


@pytest.mark.usefixtures("mock_fava_config")
class TestGpgHandler:
    """
    Tests for 5.3. GpgHandler (fava.crypto.handlers.GpgHandler)
    """
    @pytest.fixture
    def gpg_handler(self):
        from fava.crypto.handlers import GpgHandler
        return GpgHandler()
    
    @pytest.mark.gpg_compatibility
    @pytest.mark.config_dependent
    def test_tp_dar_gpgh_001_can_handle_gpg(self, gpg_handler, mock_fava_config):
        from fava.crypto.handlers import GpgHandler # For GPG_ARMORED_MAGIC_STRING etc.
        mock_fava_config.pqc_fallback_to_classical_gpg = True
        
        assert gpg_handler.can_handle("data.bc.gpg", None, mock_fava_config) is True
        assert gpg_handler.can_handle("data.bc.GPG", None, mock_fava_config) is True
        assert gpg_handler.can_handle("data.bc.pqc_hybrid_fava", None, mock_fava_config) is False
        assert gpg_handler.can_handle("data.txt", None, mock_fava_config) is False
    
        assert gpg_handler.can_handle("data.txt", b'\x85\x02_some_other_data', mock_fava_config) is True
        assert gpg_handler.can_handle("data.bin", b'\x99_compressed_data_follows', mock_fava_config) is True
        
        assert gpg_handler.can_handle("message.asc", GpgHandler.GPG_ARMORED_MAGIC_STRING + b" rest of message", mock_fava_config) is True
        
        mock_fava_config.pqc_fallback_to_classical_gpg = False
        assert gpg_handler.can_handle("data.bc.gpg", None, mock_fava_config) is False
        assert gpg_handler.can_handle("data.txt", b'\x85\x02...', mock_fava_config) is False
        
        mock_fava_config.pqc_fallback_to_classical_gpg = True
        assert gpg_handler.can_handle("data.txt", None, mock_fava_config) is False

    @pytest.mark.gpg_compatibility
    @pytest.mark.critical_path
    @mock.patch('subprocess.run')
    def test_tp_dar_gpgh_002_gpg_decrypt_success(self, mock_subprocess_run, gpg_handler, mock_fava_config):
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

    @pytest.mark.gpg_compatibility
    @pytest.mark.error_handling
    @mock.patch('subprocess.run')
    def test_tp_dar_gpgh_003_gpg_decrypt_failure(self, mock_subprocess_run, gpg_handler, mock_fava_config):
        from fava.crypto.exceptions import DecryptionError
        
        mock_subprocess_run.return_value = mock.Mock(stdout=b"Some output but failed.", returncode=2, stderr=b"gpg: decryption failed: No secret key")
        
        with pytest.raises(DecryptionError) as excinfo:
            gpg_handler.decrypt_content(b"bad_gpg_data_no_key", mock_fava_config, None)
        assert "GPG decryption failed (exit code 2)" in str(excinfo.value)
        assert "gpg: decryption failed: No secret key" in str(excinfo.value)
    
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = FileNotFoundError("gpg command not found test")
        with pytest.raises(FileNotFoundError) as fnf_excinfo:
            gpg_handler.decrypt_content(b"any_data", mock_fava_config, None)
        assert "The 'gpg' command-line tool was not found" in str(fnf_excinfo.value)
        
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = None
        mock_subprocess_run.return_value = mock.Mock(stdout=b'\xff\xfe', returncode=0, stderr=b"")
        with pytest.raises(DecryptionError) as decode_excinfo:
            gpg_handler.decrypt_content(b"data_producing_bad_output", mock_fava_config, None)
        assert "Failed to decode GPG output as UTF-8" in str(decode_excinfo.value)