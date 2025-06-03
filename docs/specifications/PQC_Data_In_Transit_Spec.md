# PQC Integration Specification: Data in Transit

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document outlines the specifications for integrating Post-Quantum Cryptography (PQC) to protect Data in Transit for the Fava application. This primarily concerns the security of HTTPS/TLS connections between the Fava client (browser) and the Fava server (or a reverse proxy). It is based on the overall PQC integration plan ([`docs/Plan.MD`](../../docs/Plan.MD)), research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure that client-server communication is protected against eavesdropping and tampering by adversaries equipped with both classical and quantum computers.

## 2. Functional Requirements

*   **FR2.1:** Fava, when deployed behind a PQC-capable reverse proxy (e.g., Nginx, Apache), MUST function correctly. All client-server communication (API calls, data fetching, WebSocket connections if any) must operate seamlessly through the PQC-secured TLS tunnel established by the proxy.
*   **FR2.2:** Fava's documentation MUST provide clear guidance on configuring recommended reverse proxies (e.g., Nginx) to use PQC KEMs for TLS 1.3 (e.g., hybrid schemes like X25519Kyber768).
*   **FR2.3:** If Fava's embedded web server (e.g., Cheroot via Flask's development server) is used directly for HTTPS (not recommended for production but possible for development/testing), and if the underlying Python `ssl` module and server libraries gain PQC cipher suite support, Fava SHOULD allow configuration of these PQC cipher suites.
*   **FR2.4:** The Fava frontend (JavaScript) MUST continue to use standard browser APIs (`fetch`, `WebSocket`) for communication. No PQC-specific changes are expected in the frontend transport logic itself, as PQC negotiation in TLS is handled by the browser and server/proxy.
*   **FR2.5:** Fava MUST NOT break or interfere with the TLS handshake process, whether classical or PQC-hybrid, handled by the browser and the server/proxy.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC mechanisms used in TLS (by the proxy or server) MUST adhere to NIST standards or IETF recommendations for PQC cipher suites (e.g., Kyber-based KEMs in TLS 1.3).
*   **NFR3.2 (Performance):** The use of PQC in TLS SHOULD NOT introduce prohibitive latency in client-server communication. Target: TLS handshake latency with PQC KEMs should be within Y% of classical ECDH handshakes (Y to be determined, e.g., 50-150% increase initially, acknowledging PQC KEMs can be slower). Overall application responsiveness should not be noticeably degraded for typical user interactions.
*   **NFR3.3 (Usability - Admin):** Configuration of Fava or the recommended reverse proxy for PQC-TLS MUST be clearly documented and as straightforward as possible for system administrators.
*   **NFR3.4 (Reliability):** PQC-secured TLS connections MUST be as reliable as classical TLS connections. Connection drops or handshake failures due to PQC should be minimal and traceable.
*   **NFR3.5 (Interoperability):** Fava's PQC-TLS setup (via proxy) MUST be interoperable with modern browsers that support the chosen PQC KEMs (e.g., Chrome, Edge with experimental Kyber support).
*   **NFR3.6 (Maintainability):** Fava's direct involvement in TLS PQC is minimal (mostly documentation or passthrough configuration). The reverse proxy's maintainability is key.
*   **NFR3.7 (Cryptographic Agility):** The choice of PQC KEMs for TLS is primarily managed at the reverse proxy or web server level. Fava's documentation should reflect this and guide users on how to achieve agility at that layer. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))

## 4. User Stories

*   **US4.1:** As a Fava user, I want my connection to the Fava server to be secured with quantum-resistant cryptography (via PQC in TLS) so that my financial data and interactions are protected from future quantum threats during transit.
*   **US4.2:** As a system administrator deploying Fava, I want to configure my reverse proxy (e.g., Nginx) to use a NIST-recommended PQC KEM for TLS connections to Fava, following clear instructions provided by Fava's documentation.
*   **US4.3:** As a Fava user accessing Fava via a browser that supports PQC in TLS, I want my session to establish a PQC-secured connection automatically without any special actions on my part.
*   **US4.4:** As a developer using Fava's development server with HTTPS, if Python's SSL libraries support PQC, I want to be able to configure Fava to use a PQC cipher suite for testing purposes.

## 5. Use Cases

### 5.1. Use Case: Secure Client-Server Communication via PQC-TLS Reverse Proxy (Happy Path)

*   **Actor:** Fava User (browser), Fava Server, PQC-Capable Reverse Proxy
*   **Preconditions:**
    *   Reverse proxy (e.g., Nginx) is configured to terminate TLS using a PQC hybrid KEM (e.g., X25519Kyber768).
    *   Reverse proxy has valid PQC-capable or classical certificates (PQC certificates are future, hybrid KEMs work with classical certs).
    *   User's browser supports the configured PQC KEM.
    *   Fava server is running behind the reverse proxy.
*   **Main Flow:**
    1.  User's browser initiates an HTTPS connection to the Fava URL (served by the reverse proxy).
    2.  Browser and reverse proxy perform a TLS 1.3 handshake, negotiating a PQC hybrid KEM cipher suite.
    3.  The PQC KEM is used to establish a shared secret for the TLS session.
    4.  A secure PQC-protected TLS tunnel is established between the browser and the reverse proxy.
    5.  The reverse proxy forwards the decrypted HTTP request to the Fava server.
    6.  Fava server processes the request and sends the HTTP response back to the reverse proxy.
    7.  The reverse proxy encrypts the HTTP response using the PQC-protected TLS session keys and sends it to the browser.
    8.  Browser decrypts and renders the response.
*   **Postconditions:**
    *   All communication between browser and Fava (via proxy) is encrypted using a PQC-hybrid scheme.
    *   User can interact with Fava normally.
    *   (External Verification) Tools like `testssl.sh` (if PQC-aware) or browser developer tools might indicate the PQC KEM used.

### 5.2. Use Case: Client Browser Does Not Support Server's PQC KEM

*   **Actor:** Fava User (browser with no/mismatched PQC KEM support), PQC-Capable Reverse Proxy
*   **Preconditions:**
    *   Reverse proxy is configured to *prefer* or *require* a PQC KEM not supported by the user's browser.
    *   Reverse proxy might also support classical KEMs as fallback.
*   **Main Flow (Scenario A: Proxy allows fallback to classical KEM):**
    1.  Browser initiates HTTPS connection.
    2.  During TLS handshake, browser and proxy fail to negotiate the preferred PQC KEM.
    3.  Proxy and browser negotiate a classical KEM (e.g., ECDHE) that both support.
    4.  A classical TLS tunnel is established.
    5.  Communication proceeds as in Use Case 5.1, but with classical TLS security.
*   **Main Flow (Scenario B: Proxy *requires* PQC KEM, no fallback or no common classical KEM):**
    1.  Browser initiates HTTPS connection.
    2.  During TLS handshake, browser and proxy fail to negotiate any common KEM.
    3.  TLS handshake fails.
    4.  Browser displays a connection error to the user.
*   **Postconditions:**
    *   (Scenario A): Communication is secured with classical TLS. User might not be aware of the fallback unless server/proxy logs it.
    *   (Scenario B): User cannot connect to Fava.
*   **Fava's Role:** Fava itself is not directly involved in this negotiation but relies on the proxy's configuration. Documentation should cover fallback strategies.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Misconfiguration of PQC cipher suites on the reverse proxy: Leads to TLS handshake failures. Fava logs might show no incoming requests. Error is at proxy/browser level.
*   **EC6.2:** Expired/invalid SSL certificate on the reverse proxy (classical or future PQC cert): Standard browser certificate warnings/errors.
*   **EC6.3:** Performance degradation due to PQC KEMs causing timeouts for Fava API calls: Fava might log request timeouts. Proxy logs might show slow TLS handshakes.
*   **EC6.4:** PQC KEM library bugs in the reverse proxy's SSL/TLS stack (e.g., OpenSSL with PQC patches): May lead to handshake failures or, in worst case, security vulnerabilities (outside Fava's direct control).
*   **EC6.5:** Client browser has experimental PQC support that is buggy: May lead to handshake failures.
*   **EC6.6:** Network intermediaries (firewalls, IDS/IPS) not understanding PQC TLS extensions: Could block or interfere with PQC handshakes.

## 7. Constraints

*   **C7.1:** Fava's PQC for Data in Transit capability is primarily dependent on the PQC capabilities of the reverse proxy (e.g., Nginx, Apache) or the underlying Python SSL libraries and web server (e.g., Cheroot) if used directly. Fava itself will not implement TLS PQC logic.
*   **C7.2:** Browser support for PQC KEMs in TLS is still experimental and evolving. Interoperability may vary.
*   **C7.3:** Availability and stability of PQC modules/support in common reverse proxies and web servers.
*   **C7.4:** PQC CA certificate issuance and browser/OS trust store support for PQC certificates are not yet widespread (expected 2026+). Hybrid KEMs with classical certificates are the current approach.
*   **C7.5:** Performance overhead of PQC KEMs in TLS handshakes is a known factor.

## 8. Data Models (if applicable)

*   Not directly applicable to Fava for Data in Transit, as TLS PQC configuration and state are managed by the reverse proxy or web server stack.
*   Fava's configuration might include new options if direct PQC cipher suite specification for its embedded server becomes feasible:
    *   `pqc_tls_cipher_suites_embedded_server`: list of strings (e.g., `["X25519Kyber768", "TLS_AES_256_GCM_SHA384"]`) - highly speculative.

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (User-facing):** No direct UI/UX changes in Fava are anticipated for PQC in transit. Users will see the standard browser padlock icon. If connection fails due to TLS issues, standard browser error pages will be shown.
*   **UI9.2 (Admin-facing - Documentation):** Fava's deployment documentation will need a new section on configuring PQC-TLS with recommended reverse proxies, including example configurations.

## 10. Initial TDD Anchors or Pseudocode Stubs

Testing PQC in TLS for Fava primarily involves end-to-end tests verifying Fava's functionality *through* a PQC-TLS channel, rather than Fava testing the TLS channel itself.

### 10.1. Test Case: Fava Operates Correctly with PQC-TLS Proxy

*   **TEST:** `test_fava_api_accessible_via_pqc_tls_proxy()`
*   **SETUP:**
    1.  Configure a reverse proxy (e.g., Nginx with `nginx-oqssl`) with a PQC hybrid KEM (e.g., `X25519Kyber768`) and a classical certificate, proxying to a running Fava instance.
    2.  Ensure a test client environment (e.g., Docker container with `curl` built against `liboqs` / `oqssl`) capable of PQC TLS.
*   **ACTION:**
    1.  From the test client, execute a `curl` command to a known Fava API endpoint (e.g., `/api/all-events/`) through the PQC-TLS proxy, explicitly requesting the PQC KEM.
        ```bash
        # Conceptual curl command, actual flags depend on oqssl curl version
        # curl --curves X25519Kyber768 https://fava.pqc.test/api/all-events/
        ```
*   **ASSERT:**
    1.  `curl` command exits with status 0.
    2.  HTTP response status code is 200.
    3.  HTTP response body is valid JSON and matches the expected output for `/api/all-events/`.
    4.  (Optional, if proxy logs are verifiable): Proxy log shows a TLS handshake completed with the specified PQC KEM.
*   **AVER (AI Verifiable End Result):**
    *   JSON: `{"test_name": "test_fava_api_accessible_via_pqc_tls_proxy", "curl_exit_code": 0, "http_status": 200, "response_body_checksum_match": true, "pqc_kem_negotiated_in_log": "X25519Kyber768" | "unknown" | "failed_to_parse_log"}`

### 10.2. Fava Documentation Stub (for PQC-TLS Configuration)

```markdown
# In docs/deployment.rst (conceptual addition)

## Securing Fava with Post-Quantum TLS (Experimental)

To protect Fava's data in transit against future quantum threats, you can configure your reverse proxy to use Post-Quantum Cryptography (PQC) hybrid Key Encapsulation Mechanisms (KEMs) for TLS 1.3. This is an advanced setup and relies on experimental features in browsers and server software.

### Example: Nginx with OpenQuantumSafe (OQS) OpenSSL

This example assumes you have Nginx compiled with an OQS-enabled OpenSSL version.

1.  **Install OQS OpenSSL and Nginx with OQS support.** (Refer to OQS project documentation)
2.  **Configure Nginx:**
    In your Nginx server block for Fava:

    ```nginx
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name fava.example.com;

        # Enable PQC KEMs (example: Kyber768 with X25519)
        # The exact directive may vary based on your OpenSSL/Nginx-OQS version
        ssl_ecdh_curve X25519Kyber768:X25519; # Example, consult OQS docs for current syntax
        # Or via ssl_conf_command if supported:
        # ssl_conf_command Curves X25519Kyber768:secp384r1;

        ssl_protocols TLSv1.2 TLSv1.3; # TLSv1.3 is required for most PQC KEMs
        ssl_prefer_server_ciphers on;
        ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'; # Modern ciphers

        ssl_certificate /path/to/your/fullchain.pem; # Standard ECC/RSA cert
        ssl_certificate_key /path/to/your/privkey.pem;

        location / {
            proxy_pass http://localhost:5000; # Assuming Fava runs on port 5000
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```
3.  **Test:** Use a browser with experimental PQC support (e.g., Chrome with relevant flags enabled for Kyber) or a PQC-capable `curl` to connect.

**Note:** The PQC landscape and software support are rapidly evolving. Always consult the latest documentation for your chosen proxy server and the OpenQuantumSafe project.
```

*   **TEST (Manual/Doc Review):** `test_pqc_tls_documentation_is_clear_and_accurate()`
*   **ACTION:** Review the PQC-TLS setup documentation for clarity, accuracy (matching current OQS/Nginx recommendations), and completeness.
*   **ASSERT:** Documentation enables a knowledgeable admin to attempt PQC-TLS setup. Key steps and potential pitfalls are covered.

## 11. Dependencies

*   **External Software (Server-Side):**
    *   PQC-capable reverse proxy (e.g., Nginx compiled with OQS OpenSSL).
    *   PQC-capable TLS library (e.g., OQS fork of OpenSSL).
    *   If direct HTTPS from Fava: Python `ssl` module and web server (Cheroot) would need PQC support (future).
*   **External Software (Client-Side):**
    *   Modern web browser with experimental support for the chosen PQC KEMs in TLS.
*   **Internal Fava Modules:**
    *   No direct code dependencies for PQC in TLS if handled by a proxy.
    *   Documentation files will need updates.

## 12. Integration Points

*   **IP12.1 (Reverse Proxy Integration):** This is the primary "integration." Fava runs behind the proxy, which handles all PQC TLS aspects. Fava must be compatible with being proxied (which it already is).
*   **IP12.2 (Documentation):** Fava's deployment guides need to integrate instructions for PQC-TLS setup.
*   **IP12.3 (Fava Development Server - Future):** If Cheroot/Python `ssl` support PQC, Fava's CLI (`src/fava/cli.py`) might need to pass new configuration options for PQC cipher suites to the `WSGIServer`. This is a future consideration.