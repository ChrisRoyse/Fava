import unittest
from unittest import mock

from fava.pqc.proxy_awareness import (
    check_pqc_proxy_headers,
    get_pqc_status_from_config,
    determine_effective_pqc_status,
    PQC_CONFIRMED_VIA_HEADER, # Import constants too
    PQC_ABSENT_VIA_HEADER,
    PQC_UNKNOWN_VIA_HEADER,
    PQC_ASSUMED_ENABLED_VIA_CONFIG,
    PQC_ASSUMED_DISABLED_VIA_CONFIG,
    PQC_STATUS_UNCERTAIN,
)


class TestFavaPQCProxyAwareness(unittest.TestCase):
    """
    Test cases for the FavaPQCProxyAwareness module.
    Based on docs/test-plans/PQC_Data_In_Transit_Test_Plan.md
    """

    def test_TC_DIT_AWARE_001_known_pqc_kem_header_present_and_recognized(self):
        """
        TC-DIT-AWARE-001: `check_pqc_proxy_headers` - Known PQC KEM Header Present and Recognized
        AI Verifiable Outcome: The return value of the function call is strictly equal to "PQC_CONFIRMED_VIA_HEADER".
        """
        mock_request_headers = {"X-PQC-KEM": "X25519Kyber768"}
        result = check_pqc_proxy_headers(mock_request_headers)
        self.assertEqual(result, PQC_CONFIRMED_VIA_HEADER)

    def test_TC_DIT_AWARE_002_pqc_indicator_header_present_kem_not_recognized(self):
        """
        TC-DIT-AWARE-002: `check_pqc_proxy_headers` - PQC Indicator Header Present but KEM Not Recognized/Classical
        AI Verifiable Outcome: The return value is strictly equal to "PQC_ABSENT_VIA_HEADER".
        """
        mock_request_headers = {"X-PQC-KEM": "SomeOtherKEM"}
        result = check_pqc_proxy_headers(mock_request_headers)
        self.assertEqual(result, PQC_ABSENT_VIA_HEADER)

    def test_TC_DIT_AWARE_003_no_pqc_indicator_header_present(self):
        """
        TC-DIT-AWARE-003: `check_pqc_proxy_headers` - No PQC Indicator Header Present
        AI Verifiable Outcome: The return value is strictly equal to "PQC_UNKNOWN_VIA_HEADER".
        """
        mock_request_headers = {}
        result = check_pqc_proxy_headers(mock_request_headers)
        self.assertEqual(result, PQC_UNKNOWN_VIA_HEADER)

    def test_TC_DIT_AWARE_004_malformed_pqc_indicator_header_value(self):
        """
        TC-DIT-AWARE-004: `check_pqc_proxy_headers` - Malformed PQC Indicator Header Value
        AI Verifiable Outcome: The return value is strictly equal to "PQC_ABSENT_VIA_HEADER",
                               and the function call completes without raising an unhandled exception.
        """
        mock_request_headers = {"X-PQC-KEM": 123} # Non-string value
        try:
            result = check_pqc_proxy_headers(mock_request_headers)
            self.assertEqual(result, PQC_ABSENT_VIA_HEADER)
        except Exception as e:
            self.fail(f"Function raised an unexpected exception: {e}")

    def test_TC_DIT_AWARE_005_pqc_assumed_enabled_via_config(self):
        """
        TC-DIT-AWARE-005: `get_pqc_status_from_config` - PQC Assumed Enabled via Config
        AI Verifiable Outcome: The return value is strictly equal to "PQC_ASSUMED_ENABLED_VIA_CONFIG".
        """
        mock_fava_config = {"assume_pqc_tls_proxy_enabled": True}
        result = get_pqc_status_from_config(mock_fava_config)
        self.assertEqual(result, PQC_ASSUMED_ENABLED_VIA_CONFIG)

    def test_TC_DIT_AWARE_006_pqc_assumed_disabled_flag_false_or_absent(self):
        """
        TC-DIT-AWARE-006: `get_pqc_status_from_config` - PQC Assumed Disabled (Flag False or Absent)
        AI Verifiable Outcome: The return value is strictly equal to "PQC_ASSUMED_DISABLED_VIA_CONFIG" for both scenarios.
        """
        # Scenario 1: Flag False
        mock_fava_config_false = {"assume_pqc_tls_proxy_enabled": False}
        result_false = get_pqc_status_from_config(mock_fava_config_false)
        self.assertEqual(result_false, PQC_ASSUMED_DISABLED_VIA_CONFIG)

        # Scenario 2: Flag Absent
        mock_fava_config_absent = {}
        result_absent = get_pqc_status_from_config(mock_fava_config_absent)
        self.assertEqual(result_absent, PQC_ASSUMED_DISABLED_VIA_CONFIG)

    @mock.patch('fava.pqc.proxy_awareness.get_pqc_status_from_config')
    @mock.patch('fava.pqc.proxy_awareness.check_pqc_proxy_headers')
    def test_TC_DIT_AWARE_007_determine_effective_pqc_status_prioritizes_header(self, mock_check_headers, mock_get_config_status):
        """
        TC-DIT-AWARE-007: `determine_effective_pqc_status` - Prioritizes Confirmed Header Info
        AI Verifiable Outcome: The return value is strictly equal to "PQC_CONFIRMED_VIA_HEADER".
                               The mock for `get_pqc_status_from_config` confirms it was not called.
        """
        mock_check_headers.return_value = PQC_CONFIRMED_VIA_HEADER
        mock_request_headers = {"X-PQC-KEM": "X25519Kyber768"} # Example content
        mock_fava_config = {"assume_pqc_tls_proxy_enabled": False} # Config that would differ

        result = determine_effective_pqc_status(mock_request_headers, mock_fava_config)

        self.assertEqual(result, PQC_CONFIRMED_VIA_HEADER)
        mock_check_headers.assert_called_once_with(mock_request_headers)
        mock_get_config_status.assert_not_called()

    @mock.patch('fava.pqc.proxy_awareness.get_pqc_status_from_config')
    @mock.patch('fava.pqc.proxy_awareness.check_pqc_proxy_headers')
    def test_TC_DIT_AWARE_008_determine_effective_pqc_status_fallback_to_config(self, mock_check_headers, mock_get_config_status):
        """
        TC-DIT-AWARE-008: `determine_effective_pqc_status` - Falls Back to Config if Header Unknown
        AI Verifiable Outcome: The return value is strictly equal to "PQC_ASSUMED_ENABLED_VIA_CONFIG".
                               Mocks for internal calls confirm they were called.
        """
        mock_check_headers.return_value = PQC_UNKNOWN_VIA_HEADER
        mock_get_config_status.return_value = PQC_ASSUMED_ENABLED_VIA_CONFIG
        mock_request_headers = {}
        mock_fava_config = {"assume_pqc_tls_proxy_enabled": True}

        result = determine_effective_pqc_status(mock_request_headers, mock_fava_config)

        self.assertEqual(result, PQC_ASSUMED_ENABLED_VIA_CONFIG)
        mock_check_headers.assert_called_once_with(mock_request_headers)
        mock_get_config_status.assert_called_once_with(mock_fava_config)

    @mock.patch('fava.pqc.proxy_awareness.get_pqc_status_from_config')
    @mock.patch('fava.pqc.proxy_awareness.check_pqc_proxy_headers')
    def test_TC_DIT_AWARE_009_determine_effective_pqc_status_uncertain(self, mock_check_headers, mock_get_config_status):
        """
        TC-DIT-AWARE-009: `determine_effective_pqc_status` - Uncertain if Header Unknown and Config Disabled
        AI Verifiable Outcome: The return value is strictly equal to "PQC_STATUS_UNCERTAIN".
                               Mocks for internal calls confirm they were called.
        """
        mock_check_headers.return_value = PQC_UNKNOWN_VIA_HEADER
        mock_get_config_status.return_value = PQC_ASSUMED_DISABLED_VIA_CONFIG
        mock_request_headers = {}
        mock_fava_config = {"assume_pqc_tls_proxy_enabled": False}

        result = determine_effective_pqc_status(mock_request_headers, mock_fava_config)

        self.assertEqual(result, PQC_STATUS_UNCERTAIN)
        mock_check_headers.assert_called_once_with(mock_request_headers)
        mock_get_config_status.assert_called_once_with(mock_fava_config)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)