# High-Level Acceptance Tests: PQC Data in Transit

**Version:** 1.0
**Date:** 2025-06-02
**PQC Focus Area:** Data in Transit (HTTPS/TLS Communication)

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) integration related to data in transit for the Fava application. This primarily concerns Fava operating correctly behind a PQC-TLS enabled reverse proxy.

---

## Test Cases

### Test ID: PQC_DIT_001
*   **Test Title/Objective:** Verify Fava functions correctly when accessed via a reverse proxy configured for PQC hybrid KEM in TLS (Happy Path).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#fr21`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#us41`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#us41)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#51-use-case-secure-client-server-communication-via-pqc-tls-reverse-proxy-happy-path`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#51-use-case-secure-client-server-communication-via-pqc-tls-reverse-proxy-happy-path)
*   **Preconditions:**
    1.  A Fava instance is running.
    2.  A reverse proxy (e.g., Nginx compiled with OQS OpenSSL) is configured in front of Fava.
    3.  The reverse proxy is configured to use a PQC hybrid KEM for TLS 1.3 (e.g., `X25519Kyber768`).
    4.  The reverse proxy has a valid SSL certificate (classical cert is fine with hybrid KEMs).
    5.  A test client (e.g., `curl` built with PQC KEM support like `oqssl`, or a browser with experimental PQC enabled) is available.
    6.  A Beancount file (`test_dit_001.bc`) is loaded in Fava, and a known API query (e.g., `/api/all_activity/`) on this file produces `expected_all_activity_001.json`.
*   **Test Steps (User actions or system interactions):**
    1.  Using the PQC-capable test client, make an HTTPS GET request to a known Fava API endpoint (e.g., `/api/all_activity/`) through the reverse proxy, ensuring the client attempts to negotiate the configured PQC KEM.
*   **Expected Results:**
    1.  The TLS handshake between the client and reverse proxy successfully negotiates the PQC hybrid KEM.
    2.  The API request is successfully proxied to Fava.
    3.  Fava processes the request and returns the correct data.
    4.  The client receives a 200 OK response with the expected JSON payload.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_001",
      "status": "PASSED/FAILED",
      "client_request": {
        "pqc_kem_negotiated": true, // Verified by client-side tools (e.g. curl verbose output) or proxy logs
        "pqc_kem_used": "X25519Kyber768", // Example, actual from test setup
        "http_status_code": 200
      },
      "api_response_validation": {
        "payload_matches_expected": true // Compare response body with `expected_all_activity_001.json`
      },
      "proxy_log_evidence": { // Optional, if proxy logs are accessible and parseable
        "pqc_handshake_success_logged": true,
        "pqc_kem_in_log": "X25519Kyber768"
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DIT_002
*   **Test Title/Objective:** Verify Fava's functionality when client browser does not support the server's preferred PQC KEM, but a classical fallback is allowed and negotiated.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem) (Scenario A)
*   **Preconditions:**
    1.  Fava instance and reverse proxy are set up as in PQC_DIT_001.
    2.  The reverse proxy is configured to prefer a PQC KEM (e.g., `X25519Kyber768`) but also allows fallback to a classical KEM (e.g., `X25519` or `P-256`).
    3.  A test client (e.g., standard `curl` or browser *without* PQC KEM support for `X25519Kyber768` but with support for the classical fallback) is available.
    4.  Beancount file `test_dit_001.bc` loaded, expected API output `expected_all_activity_001.json`.
*   **Test Steps (User actions or system interactions):**
    1.  Using the classical-only test client, make an HTTPS GET request to `/api/all_activity/` through the reverse proxy.
*   **Expected Results:**
    1.  The TLS handshake falls back to and successfully negotiates a classical KEM.
    2.  The API request is successfully proxied to Fava.
    3.  Fava returns the correct data.
    4.  The client receives a 200 OK response with the expected JSON payload.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_002",
      "status": "PASSED/FAILED",
      "client_request": {
        "classical_kem_negotiated": true, // Verified by client-side tools or proxy logs
        "classical_kem_used": "X25519", // Example, actual from test setup/logs
        "http_status_code": 200
      },
      "api_response_validation": {
        "payload_matches_expected": true // Compare with `expected_all_activity_001.json`
      },
      "proxy_log_evidence": { // Optional
        "classical_handshake_success_logged": true,
        "negotiated_kem_in_log": "X25519" // Or other classical KEM
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DIT_003
*   **Test Title/Objective:** Verify connection failure if reverse proxy *requires* a PQC KEM not supported by the client, and no compatible fallback exists.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem) (Scenario B)
*   **Preconditions:**
    1.  Fava instance and reverse proxy are set up.
    2.  The reverse proxy is configured to *require* a specific PQC KEM (e.g., `X25519Kyber768`) and does *not* offer a classical KEM that the client supports as a fallback (or client supports no common KEMs).
    3.  A test client is used that does *not* support the required PQC KEM and any other KEMs the proxy might offer (if any).
*   **Test Steps (User actions or system interactions):**
    1.  Using the incompatible test client, attempt an HTTPS GET request to `/api/all_activity/` through the reverse proxy.
*   **Expected Results:**
    1.  The TLS handshake fails.
    2.  The client receives a connection error (e.g., `curl` error, browser "Cannot connect" page).
    3.  Fava does not receive the request.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_003",
      "status": "PASSED/FAILED",
      "client_request": {
        "connection_failed_as_expected": true, // Client reports handshake failure
        "client_error_message_contains": ["SSL_ERROR", "HANDSHAKE_FAILURE"] // Keywords from client error
      },
      "proxy_log_evidence": { // Optional
        "handshake_failure_logged": true,
        "reason_indicated": "no_common_cipher_suite_or_kem" // If log provides this detail
      },
      "fava_access_log": { // Check Fava's access logs
          "request_not_received": true // The specific request should not appear in Fava's logs
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DIT_004
*   **Test Title/Objective:** Verify basic Fava UI pages load correctly over a PQC-TLS enabled connection.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#fr21`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#fr21)
*   **Preconditions:**
    1.  Setup as in PQC_DIT_001 (PQC-TLS proxy, PQC-capable client/browser).
    2.  A simple Beancount file is loaded in Fava.
*   **Test Steps (User actions or system interactions):**
    1.  Using the PQC-capable client (browser), navigate to the Fava main page (e.g., `/`).
    2.  Navigate to a report page (e.g., Balance Sheet).
*   **Expected Results:**
    1.  Both pages load successfully without TLS errors.
    2.  Page content is rendered correctly.
    3.  Browser indicates a secure (HTTPS) connection using the PQC KEM (if browser devtools show this).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_004",
      "status": "PASSED/FAILED",
      "page_load_main": {
        "http_status_code": 200,
        "content_validation_keyword_present": true // Check for a keyword like "Fava" or "Balance Sheet" in HTML body
      },
      "page_load_report": {
        "http_status_code": 200,
        "content_validation_keyword_present": true // Check for a keyword specific to the report page
      },
      "client_security_indication": { // If automatable via browser testing tools
        "pqc_kem_negotiated": true,
        "secure_connection_icon_present": true
      }
    }
    ```
*   **Test Priority:** High