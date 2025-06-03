import pytest
import logging
from fava.pqc.app_startup import initialize_backend_crypto_service
from fava.pqc.global_config import GlobalConfig
from fava.pqc.backend_crypto_service import BackendCryptoService, HybridPqcCryptoHandler
from fava.pqc.exceptions import ApplicationStartupError, CriticalConfigurationError, ConfigurationError
from fava.pqc.interfaces import CryptoHandler


# Paths for patching
GLOBAL_CONFIG_APP_STARTUP_PATH = "fava.pqc.app_startup.GlobalConfig"
BACKEND_SERVICE_APP_STARTUP_PATH = "fava.pqc.app_startup.BackendCryptoService"

class TestInitializationAndRegistrationFlow:
    """
    Test suite for Initialization and Registration Flow (Backend - Integration Style)
    """
    def setup_method(self):
        GlobalConfig.reset_cache()
        BackendCryptoService.reset_registry_for_testing()


    @pytest.mark.critical_path
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_init_001_app_startup_registers_valid_handlers(self, mocker, caplog):
        """
        TC_AGL_INIT_001: Verify app startup registers all valid crypto handlers from config.
        Covers TDD Anchor: test_app_startup_registers_all_valid_handlers_from_config_suites()
        """
        caplog.set_level(logging.INFO)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_APP_STARTUP_PATH}.get_crypto_settings")
        # We spy on the class method directly
        spy_register_handler = mocker.spy(BackendCryptoService, "register_crypto_handler")
        
        mock_active_handler_instance = mocker.Mock(spec=CryptoHandler)
        mock_active_handler_instance.get_suite_id.return_value = "SUITE_HYBRID_ACTIVE"

        # Mock GetActiveEncryptionHandler to return a mock, assuming SUITE_HYBRID_ACTIVE is valid
        mock_get_active = mocker.patch.object(BackendCryptoService, "get_active_encryption_handler")
        mock_get_active.return_value = mock_active_handler_instance

        mock_global_config_get.return_value = {
            "data_at_rest": {
                "suites": {
                    "SUITE_HYBRID_ACTIVE": {"type": "FAVA_HYBRID_PQC", "param": "val1"},
                    "SUITE_OTHER_HYBRID": {"type": "FAVA_HYBRID_PQC", "param": "val2"},
                    "SUITE_UNKNOWN_TYPE": {"type": "UNKNOWN", "param": "val3"}
                },
                "active_encryption_suite_id": "SUITE_HYBRID_ACTIVE",
                "decryption_attempt_order": ["SUITE_HYBRID_ACTIVE"] # Minimal valid order
            }
        }
        
        initialize_backend_crypto_service()

        mock_global_config_get.assert_called_once()
        
        # Check calls to RegisterCryptoHandler
        # Expected calls: (suite_id, factory_class)
        # The factory_class for FAVA_HYBRID_PQC is HybridPqcCryptoHandler
        
        # Check that SUITE_HYBRID_ACTIVE was registered with HybridPqcCryptoHandler factory
        call_args_active = next(
            call for call in spy_register_handler.call_args_list
            if call[0][0] == "SUITE_HYBRID_ACTIVE"
        )
        assert call_args_active[0][1] is HybridPqcCryptoHandler
        assert "Registered HybridPqcCryptoHandler factory for suite: SUITE_HYBRID_ACTIVE" in caplog.text

        # Check that SUITE_OTHER_HYBRID was registered
        call_args_other = next(
            call for call in spy_register_handler.call_args_list
            if call[0][0] == "SUITE_OTHER_HYBRID"
        )
        assert call_args_other[0][1] is HybridPqcCryptoHandler
        assert "Registered HybridPqcCryptoHandler factory for suite: SUITE_OTHER_HYBRID" in caplog.text

        # Check warning for unknown type
        assert "Unknown crypto suite type 'UNKNOWN' for suite_id 'SUITE_UNKNOWN_TYPE'" in caplog.text
        
        # Check active handler loading success
        mock_get_active.assert_called_once()
        assert "Active encryption handler 'SUITE_HYBRID_ACTIVE' successfully loaded." in caplog.text
        assert "PQC Backend Crypto Service initialized successfully." in caplog.text


    @pytest.mark.critical_path
    @pytest.mark.error_handling
    @pytest.mark.config_dependent
    @pytest.mark.backend
    def test_tc_agl_init_002_app_startup_fails_if_active_handler_load_fails(self, mocker, caplog):
        """
        TC_AGL_INIT_002: Verify app startup fails if active encryption handler cannot be loaded.
        Covers TDD Anchor: test_app_startup_throws_critical_error_if_active_encryption_handler_cannot_be_loaded_after_registration()
        """
        caplog.set_level(logging.CRITICAL)
        mock_global_config_get = mocker.patch(f"{GLOBAL_CONFIG_APP_STARTUP_PATH}.get_crypto_settings")
        
        # Mock GetActiveEncryptionHandler to simulate failure
        mock_get_active_handler = mocker.patch.object(BackendCryptoService, "get_active_encryption_handler")
        mock_get_active_handler.side_effect = CriticalConfigurationError("Mocked: Active handler load failed from GetActive")

        mock_global_config_get.return_value = {
            "data_at_rest": {
                "suites": {}, # No specific handlers needed for this test, focus on active handler failure
                "active_encryption_suite_id": "ACTIVE_BUT_WILL_FAIL_LOAD"
            }
        }

        with pytest.raises(ApplicationStartupError, match="Critical failure: Active PQC encryption handler unavailable: Mocked: Active handler load failed from GetActive"):
            initialize_backend_crypto_service()

        mock_get_active_handler.assert_called_once()
        assert "Failed to load active PQC encryption handler post-registration: Mocked: Active handler load failed from GetActive" in caplog.text