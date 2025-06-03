import pytest
import logging
from fava.pqc.frontend_crypto_facade import FrontendCryptoFacade
from fava.pqc.exceptions import (
    ConfigurationError,
    HashingOperationFailedError,
    AlgorithmUnavailableError,
    CryptoError
)

# Paths for patching helpers used by FrontendCryptoFacade
HTTP_CLIENT_PATH = "fava.pqc.frontend_crypto_facade.HTTP_CLIENT"
SYSTEM_TIME_PATH = "fava.pqc.frontend_crypto_facade.SYSTEM_TIME"
JS_SHA256_PATH = "fava.pqc.frontend_crypto_facade.JS_CRYPTO_SHA256"
JS_SHA3_256_PATH = "fava.pqc.frontend_crypto_facade.JS_CRYPTO_SHA3_256"
LIBOQS_JS_PATH = "fava.pqc.frontend_crypto_facade.LIBOQS_JS"
FRONTEND_UTILS_PATH = "fava.pqc.frontend_crypto_facade.FRONTEND_UTILS"


@pytest.mark.asyncio # For async test methods
class TestFrontendCryptoFacade:
    """
    Test suite for FrontendCryptoFacade
    """
    def setup_method(self):
        FrontendCryptoFacade.reset_cache_for_testing()

    @pytest.mark.critical_path
    @pytest.mark.frontend
    @pytest.mark.api_driven
    async def test_tc_agl_fcf_api_001_get_fava_runtime_crypto_options_caching(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mock_http_get = mocker.patch(f"{HTTP_CLIENT_PATH}.http_get_json")
        mock_get_time = mocker.patch(f"{SYSTEM_TIME_PATH}.get_system_time_ms")
        
        mock_api_response = {"crypto_settings": {"hashing": {"default_algorithm": "SHA3-256"}}}
        # Make http_get_json an async mock
        async_mock_http_get = mocker.AsyncMock(return_value=mock_api_response)
        mock_http_get.side_effect = async_mock_http_get # Assign the async mock to the side_effect
        
        FrontendCryptoFacade.CONFIG_CACHE_TTL_MS = 1000

        # Cache Empty
        mock_get_time.return_value = 0
        config1 = await FrontendCryptoFacade._get_fava_runtime_crypto_options()
        async_mock_http_get.assert_called_once_with("/api/fava-crypto-configuration")
        assert config1 == mock_api_response["crypto_settings"]
        assert FrontendCryptoFacade._config_cache_timestamp == 0
        assert FrontendCryptoFacade._fava_config_cache == mock_api_response["crypto_settings"]
        assert "Frontend fetched and cached Fava crypto configuration." in caplog.text
        caplog.clear()

        # Cache Fresh
        mock_get_time.return_value = 500
        config2 = await FrontendCryptoFacade._get_fava_runtime_crypto_options()
        async_mock_http_get.assert_called_once() # Still once
        assert config2 == mock_api_response["crypto_settings"]
        assert not caplog.text # No new fetch log

        # Cache Stale
        mock_get_time.return_value = 1500
        config3 = await FrontendCryptoFacade._get_fava_runtime_crypto_options()
        assert async_mock_http_get.call_count == 2 # Called again
        assert config3 == mock_api_response["crypto_settings"]
        assert "Frontend fetched and cached Fava crypto configuration." in caplog.text

    @pytest.mark.config_dependent
    @pytest.mark.frontend
    @pytest.mark.api_driven
    @pytest.mark.parametrize("algo_name, mock_hash_result_hex, js_lib_path_to_mock, expected_js_lib_call", [
        ("SHA3-256", "hex_digest_sha3", JS_SHA3_256_PATH, True),
        ("SHA256", "hex_digest_sha256", JS_SHA256_PATH, True),
    ])
    async def test_tc_agl_fcf_hash_001_calculate_configured_hash(self, mocker, algo_name, mock_hash_result_hex, js_lib_path_to_mock, expected_js_lib_call):
        mock_get_options = mocker.patch.object(FrontendCryptoFacade, '_get_fava_runtime_crypto_options')
        # Make it an async mock
        async_mock_get_options = mocker.AsyncMock(return_value={"hashing": {"default_algorithm": algo_name}})
        mock_get_options.side_effect = async_mock_get_options
        
        mock_js_lib_hash = mocker.patch(f"{js_lib_path_to_mock}.hash")
        mock_js_lib_hash.return_value = b"hashed_bytes_from_lib"
        
        mock_bytes_to_hex = mocker.patch(f"{FRONTEND_UTILS_PATH}.bytes_to_hex_string", return_value=mock_hash_result_hex)
        mock_utf8_encode = mocker.patch(f"{FRONTEND_UTILS_PATH}.utf8_encode", return_value=b"test_data_bytes")

        test_data_str = "test_data_string"
        result = await FrontendCryptoFacade.calculate_configured_hash(test_data_str)

        async_mock_get_options.assert_called_once()
        mock_utf8_encode.assert_called_once_with(test_data_str)
        if expected_js_lib_call:
            mock_js_lib_hash.assert_called_once_with(b"test_data_bytes")
        mock_bytes_to_hex.assert_called_once_with(b"hashed_bytes_from_lib")
        assert result == mock_hash_result_hex

    @pytest.mark.error_handling
    @pytest.mark.frontend
    @pytest.mark.api_driven
    async def test_tc_agl_fcf_hash_002_calculate_configured_hash_fallback(self, mocker, caplog):
        caplog.set_level(logging.WARNING)
        mock_get_options = mocker.patch.object(FrontendCryptoFacade, '_get_fava_runtime_crypto_options')
        async_mock_get_options = mocker.AsyncMock(return_value={"hashing": {"default_algorithm": "FAILING_ALGO"}})
        mock_get_options.side_effect = async_mock_get_options

        mock_js_sha256_hash = mocker.patch(f"{JS_SHA256_PATH}.hash") # Will be used by _internal_calculate_hash
        mock_js_sha3_256_hash = mocker.patch(f"{JS_SHA3_256_PATH}.hash")

        mock_bytes_to_hex = mocker.patch(f"{FRONTEND_UTILS_PATH}.bytes_to_hex_string")
        mock_utf8_encode = mocker.patch(f"{FRONTEND_UTILS_PATH}.utf8_encode", return_value=b"test_data_bytes")
        
        expected_fallback_digest_hex = "fallback_sha3_digest_hex"

        def internal_hash_side_effect(data_bytes, algo):
            if algo == "FAILING_ALGO":
                raise AlgorithmUnavailableError("Mocked: FAILING_ALGO unavailable")
            elif algo == "SHA3-256":
                return b"fallback_hashed_bytes"
            pytest.fail(f"Unexpected algo in _internal_calculate_hash mock: {algo}")
        
        mocker.patch.object(FrontendCryptoFacade, '_internal_calculate_hash', side_effect=internal_hash_side_effect)
        mock_bytes_to_hex.return_value = expected_fallback_digest_hex # For the fallback SHA3-256 result

        test_data_str = "test_data_string"
        result = await FrontendCryptoFacade.calculate_configured_hash(test_data_str)

        assert FrontendCryptoFacade._internal_calculate_hash.call_count == 2
        FrontendCryptoFacade._internal_calculate_hash.assert_any_call(b"test_data_bytes", "FAILING_ALGO")
        FrontendCryptoFacade._internal_calculate_hash.assert_any_call(b"test_data_bytes", "SHA3-256")
        
        mock_bytes_to_hex.assert_called_once_with(b"fallback_hashed_bytes")
        assert result == expected_fallback_digest_hex
        assert "CalculateConfiguredHash failed with primary algorithm" in caplog.text
        assert "Used fallback SHA3-256 for hashing." in caplog.text


    @pytest.mark.config_dependent
    @pytest.mark.frontend
    @pytest.mark.api_driven
    @pytest.mark.security_sensitive
    async def test_tc_agl_fcf_wasm_001_verify_wasm_signature_enabled(self, mocker):
        mock_get_options = mocker.patch.object(FrontendCryptoFacade, '_get_fava_runtime_crypto_options')
        async_mock_get_options = mocker.AsyncMock(return_value={
            "wasm_integrity": {
                "verification_enabled": True,
                "public_key_dilithium3_base64": "MOCK_DIL_PK_B64_STRING",
                "signature_algorithm": "Dilithium3"
            }
        })
        mock_get_options.side_effect = async_mock_get_options
        
        mock_internal_verify = mocker.patch.object(FrontendCryptoFacade, '_internal_verify_signature', return_value=True)
        mock_b64_decode = mocker.patch(f"{FRONTEND_UTILS_PATH}.base64_decode", return_value=b"decoded_pk_bytes")

        wasm_module_buffer = b"wasm_bytes_content"
        signature_buffer = b"sig_bytes_content"
        result = await FrontendCryptoFacade.verify_wasm_signature_with_config(wasm_module_buffer, signature_buffer)

        async_mock_get_options.assert_called_once()
        mock_internal_verify.assert_called_once_with(
            wasm_module_buffer, signature_buffer, "MOCK_DIL_PK_B64_STRING", "Dilithium3"
        )
        assert result is True

    @pytest.mark.config_dependent
    @pytest.mark.frontend
    @pytest.mark.api_driven
    async def test_tc_agl_fcf_wasm_002_verify_wasm_signature_disabled(self, mocker, caplog):
        caplog.set_level(logging.INFO)
        mock_get_options = mocker.patch.object(FrontendCryptoFacade, '_get_fava_runtime_crypto_options')
        async_mock_get_options = mocker.AsyncMock(return_value= {"wasm_integrity": {"verification_enabled": False}} )
        mock_get_options.side_effect = async_mock_get_options
        
        mock_internal_verify = mocker.spy(FrontendCryptoFacade, '_internal_verify_signature')

        result = await FrontendCryptoFacade.verify_wasm_signature_with_config(b"wasm", b"sig")

        async_mock_get_options.assert_called_once()
        mock_internal_verify.assert_not_called()
        assert result is True
        assert "WASM signature verification is disabled in configuration." in caplog.text