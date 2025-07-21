import pytest
import logging
from fava.pqc.global_config import GlobalConfig, FAVA_CRYPTO_SETTINGS_PATH, FAVA_CRYPTO_SETTINGS_ExpectedSchema
from fava.pqc.exceptions import (
    CriticalConfigurationError,
    ConfigurationError,
    ParsingError as PQCInternalParsingError
)

# Note: The paths for patching helpers like `file_system.READ_FILE_CONTENT`
# should be where they are *used*, which is `fava.pqc.global_config`.

class TestGlobalConfig:
    """
    Test suite for Global Configuration Management (GlobalConfig Module - Backend)
    as per docs/test-plans/PQC_Cryptographic_Agility_Test_Plan.md
    """

    def setup_method(self):
        """Reset cache before each test method."""
        GlobalConfig.reset_cache()

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_gc_001_load_crypto_settings_valid_file(self, mocker, caplog):
        """
        TC_AGL_GC_001: Verify LoadCryptoSettings correctly loads a valid crypto config file.
        Covers TDD Anchor: test_load_crypto_settings_loads_valid_config_from_path()
        """
        caplog.set_level(logging.INFO)
        mock_read_file = mocker.patch("fava.pqc.global_config.file_system.read_file_content")
        mock_parse_structure = mocker.patch("fava.pqc.global_config.parser.parse_python_like_structure")
        mock_validate_schema = mocker.patch("fava.pqc.global_config.validator.validate_schema")

        expected_config = {"valid": "config", "version": 1} # Ensure schema match for placeholder
        mock_read_file.return_value = str(expected_config) # Simulate reading a string representation
        mock_parse_structure.return_value = expected_config
        mock_validate_schema.return_value = True

        config = GlobalConfig.load_crypto_settings()

        mock_read_file.assert_called_once_with(FAVA_CRYPTO_SETTINGS_PATH)
        mock_parse_structure.assert_called_once_with(str(expected_config))
        mock_validate_schema.assert_called_once_with(expected_config, FAVA_CRYPTO_SETTINGS_ExpectedSchema)
        assert config == expected_config
        assert "Successfully loaded and validated crypto settings from" in caplog.text

    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_gc_002_load_crypto_settings_missing_file(self, mocker, caplog):
        """
        TC_AGL_GC_002: Verify LoadCryptoSettings handles missing config file by raising CriticalConfigurationError.
        Covers TDD Anchor: test_load_crypto_settings_handles_missing_file_gracefully_returns_defaults_or_throws_critical()
        """
        caplog.set_level(logging.ERROR)
        mock_read_file = mocker.patch("fava.pqc.global_config.file_system.read_file_content")
        mock_read_file.side_effect = FileNotFoundError("Mocked FileNotFoundError")

        with pytest.raises(CriticalConfigurationError, match="Crypto settings file .* is missing."):
            GlobalConfig.load_crypto_settings()
        
        mock_read_file.assert_called_once_with(FAVA_CRYPTO_SETTINGS_PATH)
        assert f"Crypto settings file not found at {FAVA_CRYPTO_SETTINGS_PATH}" in caplog.text
        assert "Mocked FileNotFoundError" in caplog.text


    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_gc_003_load_crypto_settings_malformed_file(self, mocker, caplog):
        """
        TC_AGL_GC_003: Verify LoadCryptoSettings handles malformed config file by raising CriticalConfigurationError.
        """
        caplog.set_level(logging.ERROR)
        mock_read_file = mocker.patch("fava.pqc.global_config.file_system.read_file_content")
        mock_parse_structure = mocker.patch("fava.pqc.global_config.parser.parse_python_like_structure")
        
        malformed_string = "this is not a dict"
        mock_read_file.return_value = malformed_string
        mock_parse_structure.side_effect = PQCInternalParsingError("Mocked parsing error")

        with pytest.raises(CriticalConfigurationError, match="Crypto settings file .* is malformed."):
            GlobalConfig.load_crypto_settings()
        
        mock_parse_structure.assert_called_once_with(malformed_string)
        assert "Failed to parse crypto settings from" in caplog.text
        assert "Mocked parsing error" in caplog.text

    @pytest.mark.config_dependent
    @pytest.mark.error_handling
    @pytest.mark.backend
    def test_tc_agl_gc_004_load_crypto_settings_schema_validation_failure(self, mocker, caplog):
        """
        TC_AGL_GC_004: Verify LoadCryptoSettings handles config file failing schema validation by raising CriticalConfigurationError.
        Covers TDD Anchor: test_load_crypto_settings_validates_schema_against_spec_8_1_FAVA_CRYPTO_SETTINGS()
        """
        caplog.set_level(logging.ERROR)
        mock_read_file = mocker.patch("fava.pqc.global_config.file_system.read_file_content")
        mock_parse_structure = mocker.patch("fava.pqc.global_config.parser.parse_python_like_structure")
        mock_validate_schema = mocker.patch("fava.pqc.global_config.validator.validate_schema")

        invalid_schema_config = {"some_unexpected_key": "value"} # Does not match placeholder schema
        mock_read_file.return_value = str(invalid_schema_config)
        mock_parse_structure.return_value = invalid_schema_config
        mock_validate_schema.return_value = False # Simulate schema validation failure

        with pytest.raises(CriticalConfigurationError, match="Crypto settings in .* are invalid: Crypto settings schema validation failed"):
            GlobalConfig.load_crypto_settings()
        
        mock_validate_schema.assert_called_once_with(invalid_schema_config, FAVA_CRYPTO_SETTINGS_ExpectedSchema)
        assert "Crypto settings schema validation failed for" in caplog.text
        assert "Invalid crypto settings in" in caplog.text


    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_gc_005_get_crypto_settings_caching_behavior(self, mocker):
        """
        TC_AGL_GC_005: Verify GetCryptoSettings uses cached settings after first load.
        Covers TDD Anchors: test_get_crypto_settings_returns_cached_settings_after_first_load(),
                           test_get_crypto_settings_calls_load_crypto_settings_if_cache_is_empty()
        """
        mock_load_settings = mocker.patch.object(GlobalConfig, "load_crypto_settings")
        cached_settings_val = {"cached": "settings", "version": 1}
        mock_load_settings.return_value = cached_settings_val
        
        # First call - should load
        settings1 = GlobalConfig.get_crypto_settings()
        mock_load_settings.assert_called_once()
        assert settings1 == cached_settings_val

        # Second call - should use cache
        settings2 = GlobalConfig.get_crypto_settings()
        mock_load_settings.assert_called_once() # Still once
        assert settings2 == cached_settings_val