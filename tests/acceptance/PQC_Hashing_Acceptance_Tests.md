# High-Level Acceptance Tests: PQC Hashing

**Version:** 1.0
**Date:** 2025-06-02
**PQC Focus Area:** Data Integrity (Hashing Mechanisms)

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) considerations in Fava's hashing mechanisms. This involves ensuring Fava can use PQC-resistant hash algorithms (e.g., SHA3-256) via its abstraction layers.

---

## Test Cases

### Test ID: PQC_HASH_001
*   **Test Title/Objective:** Verify backend file integrity check uses the configured PQC-resistant hash algorithm (Happy Path).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr24`](../../../docs/specifications/PQC_Hashing_Spec.md#fr24)
    *   [`docs/specifications/PQC_Hashing_Spec.md#us41`](../../../docs/specifications/PQC_Hashing_Spec.md#us41)
    *   [`docs/specifications/PQC_Hashing_Spec.md#51-use-case-backend-file-integrity-check-with-configured-pqc-resistant-hash`](../../../docs/specifications/PQC_Hashing_Spec.md#51-use-case-backend-file-integrity-check-with-configured-pqc-resistant-hash)
*   **Preconditions:**
    1.  Fava is configured to use `PQC_Hash_Algorithm_X` (e.g., "SHA3-256") as the default hashing algorithm via `FavaOptions`.
    2.  The backend `HashingService` is initialized with this configuration.
    3.  A known block of data (`test_data_block_001.txt`) exists.
    4.  The expected hash of `test_data_block_001.txt` using `PQC_Hash_Algorithm_X` is pre-calculated (`expected_hash_001.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  In a test script or Fava extension, trigger a backend operation that involves hashing the content of `test_data_block_001.txt` using the `HashingService` (simulating, for example, a file save integrity check).
    2.  Capture the calculated hash digest.
*   **Expected Results:**
    1.  The `HashingService` correctly uses the configured `PQC_Hash_Algorithm_X`.
    2.  The calculated hash digest matches the pre-calculated `expected_hash_001.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_001",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA3-256", // From FavaOptions
      "calculated_hash": "actual_hex_digest_from_service",
      "expected_hash": "content_of_expected_hash_001.txt",
      "hash_match": true, // true if calculated_hash == expected_hash
      "log_evidence": {
        "hashing_service_used_log_present": true // Optional: log indicating which hash service impl was used
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_HASH_002
*   **Test Title/Objective:** Verify frontend optimistic concurrency check uses the configured PQC-resistant hash algorithm consistently with the backend.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr25`](../../../docs/specifications/PQC_Hashing_Spec.md#fr25)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr26`](../../../docs/specifications/PQC_Hashing_Spec.md#fr26)
    *   [`docs/specifications/PQC_Hashing_Spec.md#us42`](../../../docs/specifications/PQC_Hashing_Spec.md#us42)
    *   [`docs/specifications/PQC_Hashing_Spec.md#52-use-case-frontend-optimistic-concurrency-check-with-configured-pqc-resistant-hash`](../../../docs/specifications/PQC_Hashing_Spec.md#52-use-case-frontend-optimistic-concurrency-check-with-configured-pqc-resistant-hash)
*   **Preconditions:**
    1.  Fava is configured to use `PQC_Hash_Algorithm_X` (e.g., "SHA3-256").
    2.  The frontend has fetched this configuration (e.g., Fava exposes `pqc_hashing_algorithm` option via an API).
    3.  Frontend crypto abstraction (`frontend/src/lib/crypto.ts`) supports `PQC_Hash_Algorithm_X`.
    4.  A known string of Beancount data (`test_slice_content_002`) is defined.
    5.  The expected hash of `test_slice_content_002` using `PQC_Hash_Algorithm_X` is pre-calculated (`expected_slice_hash_002.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  **Frontend Simulation:**
        a.  In a frontend test environment (e.g., using Jest/Vitest with Svelte component testing), simulate the `SliceEditor.svelte` component.
        b.  Provide `test_slice_content_002` as the editor content.
        c.  Trigger the logic that calculates the hash of the content using the frontend's `calculateHash(content, configured_algorithm)` function.
        d.  Capture the `frontend_calculated_hash`.
    2.  **Backend Simulation (or actual call if integrated test):**
        a.  Send `test_slice_content_002` and `frontend_calculated_hash` to a backend endpoint that simulates the optimistic concurrency check (e.g., a save operation).
        b.  The backend recalculates the hash of `test_slice_content_002` using its `HashingService`.
        c.  Capture the `backend_calculated_hash`.
        d.  The backend compares `frontend_calculated_hash` with `backend_calculated_hash`.
*   **Expected Results:**
    1.  The `frontend_calculated_hash` matches `expected_slice_hash_002.txt`.
    2.  The `backend_calculated_hash` matches `expected_slice_hash_002.txt`.
    3.  The backend comparison shows that `frontend_calculated_hash` equals `backend_calculated_hash`, so the (simulated) save operation would proceed.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_002",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA3-256",
      "frontend_validation": {
        "calculated_hash": "actual_frontend_hex_digest",
        "expected_hash": "content_of_expected_slice_hash_002.txt",
        "hash_match": true
      },
      "backend_validation": {
        "calculated_hash": "actual_backend_hex_digest",
        "expected_hash": "content_of_expected_slice_hash_002.txt",
        "hash_match": true
      },
      "consistency_check": {
        "frontend_hash_equals_backend_hash": true // Based on backend's comparison result
      },
      "simulated_save_outcome": "SUCCESS" // if consistency_check is true
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_HASH_003
*   **Test Title/Objective:** Verify hashing still works correctly if Fava is configured to use SHA-256 (backward compatibility/configurability).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr23`](../../../docs/specifications/PQC_Hashing_Spec.md#fr23)
*   **Preconditions:**
    1.  Fava is configured to use "SHA-256" as the hashing algorithm.
    2.  The backend `HashingService` and frontend crypto abstraction are initialized with this configuration.
    3.  A known data block (`test_data_block_001.txt`) exists.
    4.  The expected SHA-256 hash of `test_data_block_001.txt` is pre-calculated (`expected_sha256_hash_001.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  Trigger a backend hashing operation for `test_data_block_001.txt` (as in PQC_HASH_001, Step 1).
    2.  Capture the `backend_calculated_sha256_hash`.
    3.  Trigger a frontend hashing operation for `test_data_block_001.txt` (similar to PQC_HASH_002, Step 1a-d, using the same data).
    4.  Capture the `frontend_calculated_sha256_hash`.
*   **Expected Results:**
    1.  The `backend_calculated_sha256_hash` matches `expected_sha256_hash_001.txt`.
    2.  The `frontend_calculated_sha256_hash` matches `expected_sha256_hash_001.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_003",
      "status": "PASSED/FAILED",
      "configured_algorithm": "SHA-256",
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
    1.  Fava is configured to use an "UNSUPPORTED_HASH_ALGO" as the hashing algorithm.
*   **Test Steps (User actions or system interactions):**
    1.  Attempt to start the Fava application.
    2.  If Fava starts, attempt a backend hashing operation.
    3.  If Fava starts, attempt a frontend hashing operation (after frontend tries to get config).
*   **Expected Results:**
    1.  Fava backend `HashingService` fails to initialize or throws an error upon first use, logging a clear message about the unsupported algorithm. Fava might fail to start if hashing is critical at init.
    2.  Frontend, upon receiving the "UNSUPPORTED_HASH_ALGO" configuration, either fails its hashing operations with an error or gracefully disables features relying on it, logging a console error.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_HASH_004",
      "status": "PASSED/FAILED",
      "backend_behavior": {
        "initialization_failed_or_error_on_use": true,
        "error_log_present": true, // Log message like "ERROR: Unsupported hash algorithm configured: UNSUPPORTED_HASH_ALGO"
        "fava_startup_status": "FAILED_OR_DEGRADED" // Depending on how critical hashing init is
      },
      "frontend_behavior": {
        "error_on_hash_attempt_or_feature_disabled": true,
        "console_error_log_present": true // Console log like "Error: Unsupported hash algorithm configured by backend: UNSUPPORTED_HASH_ALGO"
      }
    }
    ```
*   **Test Priority:** Medium