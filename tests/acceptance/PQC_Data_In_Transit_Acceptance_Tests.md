# High-Level Acceptance Tests: PQC Data in Transit

**Version:** 1.1
**Date:** 2025-06-02
**PQC Focus Area:** Data in Transit (HTTPS/TLS Communication)

**Revision History:**
*   **1.1 (2025-06-02):** Aligned with [`docs/specifications/PQC_Data_In_Transit_Spec.md`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md) v1.1.
    *   Updated recommended PQC hybrid KEM for TLS to `X25519Kyber768`.
    *   Revised test cases to reflect this specific KEM and updated NFRs.
    *   Ensured AVERs are precise and focus on Fava's functional correctness through the PQC-TLS channel.
*   **1.0 (2025-06-02):** Initial version.

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) integration related to data in transit for the Fava application. This primarily concerns Fava operating correctly behind a PQC-TLS enabled reverse proxy using `X25519Kyber768`.

---

## Test Cases

### Test ID: PQC_DIT_001
*   **Test Title/Objective:** Verify Fava functions correctly when accessed via a reverse proxy configured for PQC hybrid KEM `X25519Kyber768` in TLS.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#fr21`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#us41`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#us41)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#51-use-case-secure-client-server-communication-via-pqc-tls-reverse-proxy-happy-path`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#51-use-case-secure-client-server-communication-via-pqc-tls-reverse-proxy-happy-path)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#nfr32`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  A Fava instance is running.
    2.  A reverse proxy (e.g., Nginx with OQS OpenSSL) is configured for `X25519Kyber768` in TLS 1.3.
    3.  The proxy has a valid classical SSL certificate.
    4.  A test client (e.g., `curl` with `X25519Kyber768` support, or PQC-enabled browser) is available.
    5.  A Beancount file (`test_dit_001.bc`) is loaded in Fava, producing `expected_all_activity_001.json` for `/api/all_activity/`.
*   **Test Steps (User actions or system interactions):**
    1.  Using the PQC-capable client, make an HTTPS GET request to `/api/all_activity/` through the proxy, negotiating `X25519Kyber768`.
*   **Expected Results:**
    1.  TLS handshake successfully negotiates `X25519Kyber768`.
    2.  API request is proxied to Fava. Fava processes and returns correct data.
    3.  Client receives 200 OK with `expected_all_activity_001.json`.
    4.  Overall request-response time is within acceptable limits (NFR3.2).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_001",
      "status": "PASSED/FAILED",
      "client_request": {
        "pqc_kem_negotiated": true, // Verified by client tool output (e.g. curl verbose) or proxy logs
        "pqc_kem_used": "X25519Kyber768",
        "http_status_code": 200
      },
      "api_response_validation": {
        "payload_matches_expected": true // Compare response with `expected_all_activity_001.json`
      },
      "proxy_log_evidence": { // Optional, if accessible
        "pqc_handshake_success_logged": true,
        "pqc_kem_in_log": "X25519Kyber768"
      },
      "performance_indicator": { // For NFR3.2
        "request_duration_ms": "<captured_duration_ms>" // Logged by client or test harness
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DIT_002
*   **Test Title/Objective:** Verify Fava's functionality when client does not support `X25519Kyber768`, but a classical fallback (e.g., X25519) is allowed and negotiated.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem) (Scenario A)
*   **Preconditions:**
    1.  Fava and proxy setup as in PQC_DIT_001, but proxy also allows fallback to classical KEMs (e.g., X25519).
    2.  A test client (e.g., standard `curl` or browser *without* `X25519Kyber768` support but with X25519 support).
    3.  `test_dit_001.bc` loaded, expected API output `expected_all_activity_001.json`.
*   **Test Steps (User actions or system interactions):**
    1.  Using the classical-only client, make an HTTPS GET request to `/api/all_activity/` through the proxy.
*   **Expected Results:**
    1.  TLS handshake falls back to and successfully negotiates a classical KEM (e.g., X25519).
    2.  API request is proxied to Fava. Fava returns correct data.
    3.  Client receives 200 OK with `expected_all_activity_001.json`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_002",
      "status": "PASSED/FAILED",
      "client_request": {
        "classical_kem_negotiated": true, // Verified by client tools or proxy logs
        "classical_kem_used": "X25519", // Example
        "http_status_code": 200
      },
      "api_response_validation": {
        "payload_matches_expected": true // Compare with `expected_all_activity_001.json`
      },
      "proxy_log_evidence": { // Optional
        "classical_handshake_success_logged": true,
        "negotiated_kem_in_log": "X25519"
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DIT_003
*   **Test Title/Objective:** Verify connection failure if proxy *requires* `X25519Kyber768` not supported by client, and no compatible fallback exists.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#52-use-case-client-browser-does-not-support-servers-pqc-kem) (Scenario B)
*   **Preconditions:**
    1.  Fava and proxy setup. Proxy configured to *require* `X25519Kyber768` and offers no classical KEMs the client supports.
    2.  Test client does *not* support `X25519Kyber768` or other offered KEMs.
*   **Test Steps (User actions or system interactions):**
    1.  Using the incompatible client, attempt HTTPS GET to `/api/all_activity/` through the proxy.
*   **Expected Results:**
    1.  TLS handshake fails. Client receives connection error. Fava does not receive the request.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_003",
      "status": "PASSED/FAILED",
      "client_request": {
        "connection_failed_as_expected": true, // Client reports handshake failure
        "client_error_message_contains": ["SSL_ERROR", "HANDSHAKE_FAILURE"]
      },
      "proxy_log_evidence": { // Optional
        "handshake_failure_logged": true,
        "reason_indicated": "no_common_cipher_suite_or_kem"
      },
      "fava_access_log": {
        "request_not_received": true // Request should not appear in Fava's logs
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DIT_004
*   **Test Title/Objective:** Verify basic Fava UI pages load correctly over an `X25519Kyber768`-TLS enabled connection.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#fr21`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md#nfr32`](../../../docs/specifications/PQC_Data_In_Transit_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  Setup as in PQC_DIT_001 (PQC-TLS proxy with `X25519Kyber768`, PQC-capable client/browser).
    2.  A simple Beancount file is loaded in Fava.
*   **Test Steps (User actions or system interactions):**
    1.  Using PQC-capable client (browser), navigate to Fava main page (`/`).
    2.  Navigate to a report page (e.g., Balance Sheet).
*   **Expected Results:**
    1.  Both pages load successfully without TLS errors. Content rendered correctly.
    2.  Browser indicates secure HTTPS connection using `X25519Kyber768` (if devtools show this).
    3.  Page load times are within acceptable limits (NFR3.2).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DIT_004",
      "status": "PASSED/FAILED",
      "page_load_main": {
        "http_status_code": 200,
        "content_validation_keyword_present": true, // Check for "Fava" or "Balance Sheet" in HTML
        "page_load_time_ms": "<captured_load_time_main_ms>" // From browser devtools or test harness
      },
      "page_load_report": {
        "http_status_code": 200,
        "content_validation_keyword_present": true, // Check for report-specific keyword
        "page_load_time_ms": "<captured_load_time_report_ms>"
      },
      "client_security_indication": { // If automatable
        "pqc_kem_negotiated": true,
        "secure_connection_icon_present": true
      }
    }
    ```
*   **Test Priority:** High