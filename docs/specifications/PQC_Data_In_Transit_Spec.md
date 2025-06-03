# PQC Integration Specification: Data in Transit

**Version:** 1.1
**Date:** 2025-06-02

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on new research findings and Devil's Advocate critique. Key changes include:
    *   Incorporated specific hybrid KEM recommendations for TLS (X25519Kyber768).
    *   Updated performance NFRs with more concrete targets based on benchmark research.
    *   Emphasized reliance on reverse proxy capabilities and updated documentation stubs accordingly.
    *   Reflected current status of PQC-TLS proxy/client tool maturity and contingencies.
    *   Removed "TBD" placeholders where possible.
*   **1.0 (2025-06-02):** Initial version.

## 1. Introduction

This document outlines the specifications for integrating Post-Quantum Cryptography (PQC) to protect Data in Transit for the Fava application. This primarily concerns the security of HTTPS/TLS connections between the Fava client (browser) and the Fava server (typically via a reverse proxy). It is based on the overall PQC integration plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)), comprehensive research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure that client-server communication is protected against eavesdropping and tampering by adversaries equipped with both classical and quantum computers, primarily by guiding administrators on configuring PQC-capable reverse proxies. This revision incorporates recent research on PQC KEMs for TLS, proxy tooling, and client support.

## 2. Functional Requirements

*   **FR2.1:** Fava, when deployed behind a PQC-capable reverse proxy (e.g., Nginx, Caddy compiled with PQC-OpenSSL), MUST function correctly. All client-server communication (API calls, data fetching, WebSocket connections if any) must operate seamlessly through the PQC-hybrid secured TLS tunnel established by the proxy.
*   **FR2.2:** Fava's documentation MUST provide clear, updated guidance on configuring recommended reverse proxies (e.g., Nginx, Caddy) to use PQC hybrid KEMs for TLS 1.3, specifically recommending `X25519Kyber768` as per current research (`pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md`, `pf_pqc_tls_proxies_clients_g4_2_PART_1.md`).
*   **FR2.3:** If Fava's embedded web server (e.g., Cheroot via Flask's development server) is used directly for HTTPS (not recommended for production), and if the underlying Python `ssl` module and server libraries gain PQC cipher suite support (currently not standard), Fava SHOULD allow configuration of these PQC cipher suites via Fava options. This is a future consideration contingent on Python ecosystem advancements.
*   **FR2.4:** The Fava frontend (JavaScript) MUST continue to use standard browser APIs (`fetch`, `WebSocket`) for communication. No PQC-specific changes are expected in the frontend transport logic itself, as PQC negotiation in TLS is handled by the browser and server/proxy.
*   **FR2.5:** Fava MUST NOT break or interfere with the TLS handshake process, whether classical or PQC-hybrid, handled by the browser and the server/proxy.
*   **FR2.6:** Fava documentation MUST include information on contingency plans if PQC-TLS reverse proxies are unstable or difficult to configure, such as recommending application-layer PQC for highly sensitive data over classical TLS, as outlined in research (`pf_tooling_contingency_PART_1.md`).

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC mechanisms used in TLS (by the proxy or server) MUST adhere to NIST standards (ML-KEM/Kyber in FIPS 203) and IETF recommendations for PQC hybrid cipher suites (e.g., `X25519Kyber768`).
*   **NFR3.2 (Performance):** The use of PQC in TLS SHOULD NOT introduce prohibitive latency.
    *   Target: TLS handshake latency with `X25519Kyber768` should ideally add no more than 50-150ms compared to a classical X25519 handshake on typical server/client hardware, based on available PQC KEM performance benchmarks (`pf_pqc_performance_benchmarks_g1_3_PART_1.md`).
    *   Overall application responsiveness for typical user interactions (e.g., loading a report, saving a transaction) should not be noticeably degraded (e.g., <10% increase in overall perceived page load or action completion time attributable to TLS).
*   **NFR3.3 (Usability - Admin):** Configuration of the recommended reverse proxy for PQC-TLS MUST be clearly documented and as straightforward as possible, acknowledging the current experimental nature of some PQC proxy setups (`pf_pqc_tls_proxies_clients_g4_2_PART_1.md`).
*   **NFR3.4 (Reliability):** PQC-hybrid secured TLS connections MUST be as reliable as classical TLS connections, assuming stable proxy and client software. Connection drops or handshake failures due to PQC should be minimal and traceable via proxy/client logs.
*   **NFR3.5 (Interoperability):** Fava's PQC-TLS setup (via proxy) MUST be interoperable with modern browsers that support the chosen PQC KEMs (e.g., Chrome, Edge, Firefox with experimental `X25519Kyber768` support).
*   **NFR3.6 (Maintainability):** Fava's direct involvement in TLS PQC is minimal (mostly documentation or passthrough configuration for embedded server). The reverse proxy's maintainability and update cycle for PQC features are key.
*   **NFR3.7 (Cryptographic Agility):** The choice of PQC KEMs for TLS is primarily managed at the reverse proxy or web server level. Fava's documentation should reflect this and guide users on how to achieve agility at that layer, including updating to new recommended hybrid suites as they emerge. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))

## 4. User Stories

*   **US4.1:** As a Fava user, I want my connection to the Fava server to be secured with quantum-resistant cryptography (via PQC-hybrid in TLS) so that my financial data and interactions are protected from future quantum threats during transit.
*   **US4.2:** As a system administrator deploying Fava, I want to configure my reverse proxy (e.g., Nginx) to use a NIST-recommended PQC hybrid KEM (like X25519Kyber768) for TLS connections to Fava, following clear instructions provided by Fava's documentation.
*   **US4.3:** As a Fava user accessing Fava via a browser that supports PQC in TLS, I want my session to establish a PQC-hybrid secured connection automatically without any special actions on my part.
*   **US4.4:** As a developer using Fava's development server with HTTPS, if Python's SSL libraries and Cheroot support PQC, I want to be able to configure Fava to use a PQC cipher suite for testing purposes.

## 5. Use Cases

### 5.1. Use Case: Secure Client-Server Communication via PQC-TLS Reverse Proxy (Happy Path)

*   **Actor:** Fava User (browser), Fava Server, PQC-Capable Reverse Proxy
*   **Preconditions:**
    *   Reverse proxy (e.g., Nginx compiled with OQS-OpenSSL) is configured to terminate TLS using `X25519Kyber768`.
    *   Reverse proxy has valid classical certificates (PQC certificates are future; hybrid KEMs work with classical certs).
    *   User's browser supports `X25519Kyber768`.
    *   Fava server is running behind the reverse proxy.
*   **Main Flow:**
    1.  User's browser initiates an HTTPS connection to the Fava URL (served by the reverse proxy).
    2.  Browser and reverse proxy perform a TLS 1.3 handshake, negotiating the `X25519Kyber768` hybrid KEM cipher suite.
    3.  The hybrid KEM is used to establish a shared secret for the TLS session.
    4.  A secure PQC-hybrid protected TLS tunnel is established between the browser and the reverse proxy.
    5.  The reverse proxy forwards the decrypted HTTP request to the Fava server.
    6.  Fava server processes the request and sends the HTTP response back to the reverse proxy.
    7.  The reverse proxy encrypts the HTTP response using the PQC-hybrid protected TLS session keys and sends it to the browser.
    8.  Browser decrypts and renders the response.
*   **Postconditions:**
    *   All communication between browser and Fava (via proxy) is encrypted using `X25519Kyber768`.
    *   User can interact with Fava normally.
    *   (External Verification) Tools like PQC-aware `openssl s_client` or browser developer tools might indicate the KEM used.

### 5.2. Use Case: Client Browser Does Not Support Server's PQC KEM

*   **Actor:** Fava User (browser with no/mismatched PQC KEM support), PQC-Capable Reverse Proxy
*   **Preconditions:**
    *   Reverse proxy is configured to *prefer* or *require* `X25519Kyber768`, which is not supported by the user's browser.
    *   Reverse proxy also supports classical KEMs (e.g., X25519 alone) as fallback.
*   **Main Flow (Scenario A: Proxy allows fallback to classical KEM):**
    1.  Browser initiates HTTPS connection.
    2.  During TLS handshake, browser and proxy fail to negotiate `X25519Kyber768`.
    3.  Proxy and browser negotiate a classical KEM (e.g., X25519 or ECDHE) that both support.
    4.  A classical TLS tunnel is established.
    5.  Communication proceeds as in Use Case 5.1, but with classical TLS security.
*   **Main Flow (Scenario B: Proxy *requires* PQC KEM, no fallback or no common classical KEM):**
    1.  Browser initiates HTTPS connection.
    2.  During TLS handshake, browser and proxy fail to negotiate any common KEM.
    3.  TLS handshake fails.
    4.  Browser displays a connection error to the user.
*   **Postconditions:**
    *   (Scenario A): Communication is secured with classical TLS. User might not be aware of the fallback.
    *   (Scenario B): User cannot connect to Fava.
*   **Fava's Role:** Fava itself is not directly involved. Documentation should cover proxy configuration for fallback strategies.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Misconfiguration of PQC cipher suites or KEMs on the reverse proxy: Leads to TLS handshake failures. Error is at proxy/browser level.
*   **EC6.2:** Expired/invalid SSL certificate on the reverse proxy: Standard browser certificate warnings/errors.
*   **EC6.3:** Performance degradation due to PQC KEMs causing timeouts for Fava API calls: Fava might log request timeouts. Proxy logs might show slow TLS handshakes. Ensure NFR3.2 is met.
*   **EC6.4:** PQC KEM library bugs in the reverse proxy's SSL/TLS stack (e.g., OQS-OpenSSL): May lead to handshake failures or security vulnerabilities (outside Fava's direct control). Mitigation: Use latest stable patched versions.
*   **EC6.5:** Client browser has experimental PQC support that is buggy or incompatible: May lead to handshake failures. Mitigation: Rely on proxy fallback mechanisms.
*   **EC6.6:** Network intermediaries (firewalls, IDS/IPS) not understanding PQC TLS extensions: Could block or interfere with PQC handshakes. Mitigation: Standard network troubleshooting; PQC TLS aims to be compatible.

## 7. Constraints

*   **C7.1:** Fava's PQC for Data in Transit capability is primarily dependent on the PQC capabilities of the reverse proxy (e.g., Nginx, Caddy) or the underlying Python SSL libraries and web server (e.g., Cheroot) if used directly. Fava itself will not implement TLS PQC logic.
*   **C7.2:** Browser support for PQC KEMs in TLS is still experimental and evolving. Interoperability may vary. (Current research `pf_pqc_tls_proxies_clients_g4_2_PART_1.md` indicates improving support for X25519Kyber768).
*   **C7.3:** Availability and stability of PQC modules/support in common reverse proxies (e.g., requiring custom builds with OQS-OpenSSL).
*   **C7.4:** PQC CA certificate issuance and widespread trust store support are not yet available. Hybrid KEMs with classical certificates are the current approach.
*   **C7.5:** Performance overhead of PQC KEMs in TLS handshakes is a known factor (addressed in NFR3.2).

## 8. Data Models (if applicable)

*   Not directly applicable to Fava for Data in Transit if TLS is handled by a reverse proxy.
*   Fava's configuration might include new options if direct PQC cipher suite specification for its embedded server becomes feasible:
    *   `pqc_tls_embedded_server_kems`: list of strings (e.g., `["X25519Kyber768", "X25519"]`) - highly speculative and future-dependent.

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (User-facing):** No direct UI/UX changes in Fava. Users see standard browser padlock. Browser error pages for TLS failures.
*   **UI9.2 (Admin-facing - Documentation):** Fava's deployment documentation will need a new section on configuring PQC-TLS with recommended reverse proxies (Nginx, Caddy) and the `X25519Kyber768` hybrid KEM. Example configurations should be provided.

## 10. Initial TDD Anchors or Pseudocode Stubs

Testing PQC in TLS for Fava primarily involves end-to-end tests verifying Fava's functionality *through* a PQC-TLS channel.

### 10.1. Test Case: Fava Operates Correctly with PQC-TLS Proxy

*   **TEST:** `test_fava_api_accessible_via_x25519kyber768_tls_proxy()`
*   **SETUP:**
    1.  Configure a reverse proxy (e.g., Nginx with OQS-OpenSSL) with `X25519Kyber768` KEM and a classical certificate, proxying to a running Fava instance.
    2.  Ensure a test client environment (e.g., Docker with PQC-enabled `openssl s_client` or `curl`) capable of PQC TLS.
*   **ACTION:**
    1.  From the test client, execute a command (e.g., `openssl s_client -connect fava.pqc.test:443 -groups X25519Kyber768 -ign_eof <<<'GET /api/all-events/ HTTP/1.1\r\nHost: fava.pqc.test\r\n\r\n'`) to a known Fava API endpoint.
*   **ASSERT:**
    1.  Client command exits successfully.
    2.  TLS handshake completes using `X25519Kyber768` (verified via client tool output or proxy logs).
    3.  HTTP response status code is 200.
    4.  HTTP response body is valid JSON and matches expected output.
*   **AVER (AI Verifiable End Result):**
    *   JSON: `{"test_name": "test_fava_api_accessible_via_x25519kyber768_tls_proxy", "client_exit_code": 0, "kem_negotiated": "X25519Kyber768", "http_status": 200, "response_body_checksum_match": true}`

### 10.2. Fava Documentation Stub (for PQC-TLS Configuration) - Updated

```markdown
# In docs/deployment.rst (conceptual addition)

## Securing Fava with Post-Quantum TLS (Experimental)

To protect Fava's data in transit against future quantum threats, configure your reverse proxy to use Post-Quantum Cryptography (PQC) hybrid Key Encapsulation Mechanisms (KEMs) for TLS 1.3. The recommended hybrid KEM is `X25519Kyber768`. This setup relies on experimental features in browsers and server software.

### Example: Nginx with OpenSSL (OQS Provider or PQC-enabled build)

This example assumes Nginx compiled with an OpenSSL version (e.g., 3.2+ with OQS provider, or custom build) that supports `X25519Kyber768`.

1.  **Install/Compile PQC-enabled Nginx and OpenSSL.** (Refer to OQS project and Nginx documentation for custom builds).
2.  **Configure Nginx:**
    In your Nginx server block for Fava:

    ```nginx
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name fava.example.com;

        # Enable PQC KEMs (example: X25519Kyber768)
        # For OpenSSL 3.x with OQS provider, this might be automatic if KEMs are enabled in OpenSSL config,
        # or specific directives might be needed.
        # Consult your OpenSSL/Nginx-OQS version documentation.
        # Example using ssl_ecdh_curve (might need specific OpenSSL patches for PQC KEMs)
        # or via ssl_conf_command for TLS 1.3 groups if supported:
        # ssl_conf_command Groups X25519Kyber768:X25519:secp256r1; # Prioritize PQC hybrid

        ssl_protocols TLSv1.3;
        ssl_prefer_server_ciphers off; # For TLS 1.3, client and server negotiate from shared list
        # Modern TLS 1.3 cipher suites are typically AEADs like AES-GCM or CHACHA20-POLY1305
        ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';

        ssl_certificate /path/to/your/fullchain.pem; # Standard ECC/RSA certificate
        ssl_certificate_key /path/to/your/privkey.pem;

        location / {
            proxy_pass http://localhost:5000; # Assuming Fava runs on port 5000
            proxy_set_header Host $host;
            # ... other proxy headers
        }
    }
    ```
3.  **Test:** Use a browser with experimental PQC support (e.g., Chrome/Edge/Firefox with `X25519Kyber768` enabled) or `openssl s_client -groups X25519Kyber768 ...`.

**Note:** The PQC landscape and software support are rapidly evolving. Always consult the latest documentation for Nginx, OpenSSL, the OQS project, and your chosen browser. Ensure your OpenSSL configuration (`openssl.cnf`) enables PQC providers/algorithms if using a modular setup.
```

*   **TEST (Manual/Doc Review):** `test_pqc_tls_documentation_is_clear_accurate_and_actionable()`
*   **ACTION:** Review the PQC-TLS setup documentation for clarity, accuracy (matching current OQS/Nginx/OpenSSL recommendations for `X25519Kyber768`), and completeness.
*   **ASSERT:** Documentation enables a knowledgeable admin to attempt PQC-TLS setup. Key steps, potential pitfalls, and current tooling status are covered.

## 11. Dependencies

*   **External Software (Server-Side):**
    *   PQC-capable reverse proxy (e.g., Nginx compiled with OQS-OpenSSL).
    *   PQC-capable TLS library (e.g., OQS fork of OpenSSL, or OpenSSL 3.2+ with OQS provider).
    *   If direct HTTPS from Fava: Python `ssl` module and web server (Cheroot) would need PQC support (future).
*   **External Software (Client-Side):**
    *   Modern web browser with experimental support for `X25519Kyber768` in TLS.
    *   PQC-enabled `openssl s_client` or `curl` for testing.
*   **Internal Fava Modules:**
    *   No direct code dependencies for PQC in TLS if handled by a proxy.
    *   Documentation files will need updates.

## 12. Integration Points

*   **IP12.1 (Reverse Proxy Integration):** Fava runs behind the proxy, which handles PQC TLS.
*   **IP12.2 (Documentation):** Fava's deployment guides integrate instructions for PQC-TLS setup.
*   **IP12.3 (Fava Development Server - Future):** If Cheroot/Python `ssl` support PQC, Fava's CLI might pass new configuration options for PQC KEMs.