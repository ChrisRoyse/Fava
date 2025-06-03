import unittest
from unittest import mock

from fava.pqc.documentation_generator import (
    generate_pqc_tls_reverse_proxy_config_guide,
    generate_pqc_tls_contingency_guide,
    generate_pqc_tls_future_embedded_server_guide,
)


class TestFavaDocumentationGenerator(unittest.TestCase):
    """
    Test cases for the FavaDocumentationGenerator module.
    Based on docs/test-plans/PQC_Data_In_Transit_Test_Plan.md
    """

    def test_TC_DIT_DOCS_001_nginx_x25519kyber768(self):
        """
        TC-DIT-DOCS-001: `generate_pqc_tls_reverse_proxy_config_guide` - Nginx with X25519Kyber768
        AI Verifiable Outcome: The returned string contains all specified substrings.
        """
        result = generate_pqc_tls_reverse_proxy_config_guide(
            proxy_type="Nginx",
            kem_recommendation="X25519Kyber768",
            relevant_research_docs=["pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md"]
        )
        self.assertIn("Nginx", result)
        self.assertIn("`X25519Kyber768`", result)
        self.assertIn("experimental", result)
        self.assertIn("OQS project", result)
        self.assertIn("classical certificates", result)
        self.assertIn("ssl_conf_command Groups X25519Kyber768", result)
        self.assertIn("pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md", result)
        self.assertIn("[`pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md`](../../docs/research/pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md)", result)

    def test_TC_DIT_DOCS_002_caddy_x25519kyber768(self):
        """
        TC-DIT-DOCS-002: `generate_pqc_tls_reverse_proxy_config_guide` - Caddy with X25519Kyber768
        AI Verifiable Outcome: The returned string contains all specified substrings/patterns.
        """
        result = generate_pqc_tls_reverse_proxy_config_guide(
            proxy_type="Caddy",
            kem_recommendation="X25519Kyber768",
            relevant_research_docs=[]
        )
        self.assertIn("Caddy", result)
        self.assertIn("`X25519Kyber768`", result)
        self.assertIn("key_exchange_algorithms X25519Kyber768", result) # or similar

    def test_TC_DIT_DOCS_003_contingency_guide_content(self):
        """
        TC-DIT-DOCS-003: `generate_pqc_tls_contingency_guide` - Content Verification
        AI Verifiable Outcome: The returned string contains all specified substrings.
        """
        result = generate_pqc_tls_contingency_guide(
            contingency_research_doc="pf_tooling_contingency_PART_1.md"
        )
        self.assertIn("Contingency Planning", result)
        self.assertIn("application-layer PQC", result)
        self.assertIn("pf_tooling_contingency_PART_1.md", result)
        self.assertIn("[`pf_tooling_contingency_PART_1.md`](../../docs/research/pf_tooling_contingency_PART_1.md)", result)

    def test_TC_DIT_DOCS_004_future_embedded_guide_content_kems_supported(self):
        """
        TC-DIT-DOCS-004: `generate_pqc_tls_future_embedded_server_guide` - Content Verification (When KEMs Supported)
        AI Verifiable Outcome: The returned string is not empty and contains all specified substrings/patterns.
        """
        supported_kems = ["X25519Kyber768", "Kyber768"]
        result = generate_pqc_tls_future_embedded_server_guide(
            supported_kems_by_fava_embedded=supported_kems
        )
        self.assertTrue(result) # Not empty
        self.assertIn("Future", result)
        self.assertIn("Embedded Web Server", result)
        self.assertIn("Python `ssl` module", result)
        self.assertIn("Cheroot", result)
        self.assertIn('PQC_TLS_EMBEDDED_SERVER_KEMS = ["X25519Kyber768", "Kyber768"]', result)

    def test_TC_DIT_DOCS_005_future_embedded_guide_empty_no_kems_supported(self):
        """
        TC-DIT-DOCS-005: `generate_pqc_tls_future_embedded_server_guide` - Empty Output (When No KEMs Supported)
        AI Verifiable Outcome: The returned string is strictly equal to "".
        """
        result = generate_pqc_tls_future_embedded_server_guide(
            supported_kems_by_fava_embedded=[]
        )
        self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)