# High-Level Acceptance Tests: PQC Hashing

**Version:** 1.1
**Date:** 2025-06-02
**PQC Focus Area:** Data Integrity (Hashing Mechanisms)

**Revision History:**
*   **1.1 (2025-06-02):** Aligned with [`docs/specifications/PQC_Hashing_Spec.md`](../../../docs/specifications/PQC_Hashing_Spec.md) v1.1.
    *   Default hashing algorithm changed to SHA3-256.
    *   Updated tests to reflect SHA3-256 as default and SHA-256 as alternative.
    *   Incorporated performance NFR considerations (logged timings in AVERs).
    *   Acknowledged frontend JS/WASM SHA-3 library dependency.
*   **1.0 (2025-06-02):** Initial version.

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) considerations in Fava's hashing mechanisms. This involves ensuring Fava uses SHA3-256 by default and can be configured for SHA-256 via its abstraction layers.

---

## Test Cases

### Test ID: PQC_HASH_001
*   **Test Title/Objective:** Verify backend file integrity check uses the configured PQC-resistant hash algorithm (SHA3-256 by default).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr24`](../../../docs/specifications/PQC_Hashing_Spec.md#fr24)
    *   [`docs/specifications/PQC_Hashing_Spec.md#us41`](../../../docs/specifications/PQC_Hashing_Spec.md#us41)
    *   [`docs/specifications/PQC_Hashing_Spec.md#51-use-case-backend-file-integrity-check-with-configured-sha3-256-hash`](../../../docs/specifications/PQC_Hashing_Spec.md#51-use-case-backend-file-integrity-check-with-configured-pqc-resistant-hash) (Adjusted for SHA3-256)
    *   [`docs/specifications/PQC_Hashing_Spec.md#nfr32`](../../../docs/specifications/PQC_Hashing_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  Fava is configured to use "SHA3-256" (default) as the hashing algorithm via `FavaOptions`.
    2.  The backend `HashingService` is initialized with this configuration.
    3.  A known block of data (`test_data_block_001.txt`, e.g., 1MB) exists.
    4.  The expected SHA3-256 hash of `test_data_block_001.txt` is pre-calculated (`expected_sha3_256_hash_001.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  Trigger a backend operation (e.g., via test script) that hashes `test_data_block_001.txt` using the `HashingService`.
    2.  Capture the calculated hash digest and logged hashing time.
*   **Expected Results:**
    1.  The `HashingService` uses SHA3-256.
    2.  The calculated hash digest matches `expected_sha3_256_hash_001.txt`.
    3.  Hashing time is within NFR3.2 target (e.g., 50-100ms for 1MB).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_001",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA3-256",
      "calculated_hash": "actual_hex_digest_from_service",
      "expected_hash": "content_of_expected_sha3_256_hash_001.txt",
      "hash_match": true,
      "log_evidence": {
        "hashing_service_used_log_present": true, // Optional: log indicating HashingService use
        "hashing_time_logged_ms": "<captured_time_ms>" // e.g., "INFO: Hashing data (1MB) with SHA3-256 completed in XXms"
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_HASH_002
*   **Test Title/Objective:** Verify frontend optimistic concurrency check uses the configured SHA3-256 hash algorithm consistently with the backend.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr25`](../../../docs/specifications/PQC_Hashing_Spec.md#fr25)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr26`](../../../docs/specifications/PQC_Hashing_Spec.md#fr26)
    *   [`docs/specifications/PQC_Hashing_Spec.md#us42`](../../../docs/specifications/PQC_Hashing_Spec.md#us42)
    *   [`docs/specifications/PQC_Hashing_Spec.md#52-use-case-frontend-optimistic-concurrency-check-with-configured-sha3-256-hash`](../../../docs/specifications/PQC_Hashing_Spec.md#52-use-case-frontend-optimistic-concurrency-check-with-configured-pqc-resistant-hash) (Adjusted for SHA3-256)
    *   [`docs/specifications/PQC_Hashing_Spec.md#nfr32`](../../../docs/specifications/PQC_Hashing_Spec.md#nfr32) (Performance - Frontend)
    *   [`docs/specifications/PQC_Hashing_Spec.md#nfr37`](../../../docs/specifications/PQC_Hashing_Spec.md#nfr37) (Frontend Bundle Size)
*   **Preconditions:**
    1.  Fava is configured to use "SHA3-256".
    2.  Frontend has fetched this configuration ("SHA3-256") from the backend.
    3.  Frontend crypto abstraction (`frontend/src/lib/crypto.ts`) supports SHA3-256 (e.g., via `js-sha3` or WASM lib).
    4.  A known string of Beancount data (`test_slice_content_002`, e.g., 50KB) is defined.
    5.  The expected SHA3-256 hash of `test_slice_content_002` is pre-calculated (`expected_slice_sha3_256_hash_002.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  **Frontend Simulation:**
        a.  In a frontend test environment, simulate `SliceEditor.svelte`.
        b.  Provide `test_slice_content_002` as editor content.
        c.  Trigger logic to calculate hash using `calculateHash(content, "SHA3-256")`. Capture `frontend_calculated_hash` and hashing time.
    2.  **Backend Simulation:**
        a.  Send `test_slice_content_002` and `frontend_calculated_hash` to a backend endpoint simulating save.
        b.  Backend recalculates hash using `HashingService` (SHA3-256). Capture `backend_calculated_hash`.
        c.  Backend compares hashes.
*   **Expected Results:**
    1.  `frontend_calculated_hash` matches `expected_slice_sha3_256_hash_002.txt`. Frontend hashing time within NFR3.2 (e.g., 20-50ms for 50KB).
    2.  `backend_calculated_hash` matches `expected_slice_sha3_256_hash_002.txt`.
    3.  Backend comparison shows hashes match.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_002",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA3-256",
      "frontend_validation": {
        "calculated_hash": "actual_frontend_hex_digest",
        "expected_hash": "content_of_expected_slice_sha3_256_hash_002.txt",
        "hash_match": true,
        "hashing_time_ms": "<captured_frontend_time_ms>" // Logged by test harness
      },
      "backend_validation": {
        "calculated_hash": "actual_backend_hex_digest",
        "expected_hash": "content_of_expected_slice_sha3_256_hash_002.txt",
        "hash_match": true
      },
      "consistency_check": {
        "frontend_hash_equals_backend_hash": true
      },
      "simulated_save_outcome": "SUCCESS"
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_HASH_003
*   **Test Title/Objective:** Verify hashing works correctly if Fava is configured to use SHA-256 (backward compatibility/configurability).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr23`](../../../docs/specifications/PQC_Hashing_Spec.md#fr23)
*   **Preconditions:**
    1.  Fava is configured to use "SHA256" as the hashing algorithm.
    2.  Backend `HashingService` and frontend crypto abstraction are initialized/informed of this.
    3.  A known data block (`test_data_block_001.txt`) exists.
    4.  Expected SHA-256 hash of `test_data_block_001.txt` is pre-calculated (`expected_sha256_hash_001.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  Trigger backend hashing for `test_data_block_001.txt`. Capture `backend_calculated_sha256_hash`.
    2.  Trigger frontend hashing for `test_data_block_001.txt` (configured for SHA-256). Capture `frontend_calculated_sha256_hash`.
*   **Expected Results:**
    1.  `backend_calculated_sha256_hash` matches `expected_sha256_hash_001.txt`.
    2.  `frontend_calculated_sha256_hash` matches `expected_sha256_hash_001.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_003",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA256",
      "backend_hash_validation": {
        "calculated_hash": "actual_backend_sha256_digest",
        "expected_hash": "content_of_expected_sha256_hash_001.txt",
        "hash_match": true
      },
      "frontend_hash_validation": {
        "calculated_hash": "actual_frontend_sha256_digest",
        "expected_hash": "content_of_expected_sha256_hash_001.txt",
        "hash_match": true
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_HASH_004
*   **Test Title/Objective:** Verify error handling if an unsupported hash algorithm is configured.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#ec61`](../../../docs/specifications/PQC_Hashing_Spec.md#ec61)
*   **Preconditions:**
    1.  Fava is configured to use "UNSUPPORTED_HASH_ALGO" for hashing.
*   **Test Steps (User actions or system interactions):**
    1.  Attempt to start Fava / initialize `HashingService`.
    2.  If started, attempt a backend hashing operation.
    3.  If frontend gets this config, attempt a frontend hashing operation.
*   **Expected Results:**
    1.  Backend `HashingService` logs error and defaults to SHA3-256 (or fails init if critical).
    2.  Frontend logs console error and defaults to SHA-256 (or fails hashing).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_004",
      "status": "PASSED/FAILED",
      "backend_behavior": {
        "defaulted_or_error_on_use": true, // HashingService should default to SHA3-256
        "error_log_present_for_unsupported": true, // Log like "Warning: Unsupported hash algorithm 'UNSUPPORTED_HASH_ALGO'. Defaulting to 'sha3-256'."
        "actual_hash_matches_default_algo_hash": true // If it defaults and hashes, check against SHA3-256 of a known input
      },
      "frontend_behavior": {
        "defaulted_or_error_on_use": true, // Frontend should default to SHA-256
        "console_error_log_present": true, // Console log like "WARN: Unsupported hash algorithm 'UNSUPPORTED_HASH_ALGO'. Defaulting to SHA-256."
        "actual_hash_matches_default_algo_hash": true // If it defaults and hashes, check against SHA-256 of a known input
      }
    }
    ```
*   **Test Priority:** Medium