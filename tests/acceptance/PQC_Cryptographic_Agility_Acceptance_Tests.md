# High-Level Acceptance Tests: PQC Cryptographic Agility

**Version:** 1.0
**Date:** 2025-06-02
**PQC Focus Area:** Cryptographic Agility

This document contains high-level end-to-end acceptance tests for verifying Fava's cryptographic agility. This involves ensuring Fava can switch between different cryptographic algorithms and configurations via its abstraction layers (`CryptoService` backend, crypto abstractions frontend).

---

## Test Cases

### Test ID: PQC_AGL_001
*   **Test Title/Objective:** Verify backend hashing algorithm can be switched via configuration, and the correct hash is produced for each configured algorithm.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr25`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr25)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#us41`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#us41)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#51-use-case-administrator-changes-default-hashing-algorithm`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#51-use-case-administrator-changes-default-hashing-algorithm)
*   **Preconditions:**
    1.  Fava's `CryptoService` supports at least two hashing algorithms: `Hash_Algo_A` (e.g., "SHA-256") and `Hash_Algo_B` (e.g., "SHA3-256").
    2.  A known data block (`test_data_block_agl_001.txt`) exists.
    3.  Expected hash of `test_data_block_agl_001.txt` using `Hash_Algo_A` is `expected_hash_A_001.txt`.
    4.  Expected hash of `test_data_block_agl_001.txt` using `Hash_Algo_B` is `expected_hash_B_001.txt`.
*   **Test Steps (User actions or system interactions):**
    1.  **Step Group 1 (Hash_Algo_A):**
        a.  Configure Fava (`FavaOptions`) to use `Hash_Algo_A` for hashing.
        b.  Restart Fava (if necessary for config to take effect) or ensure `CryptoService` re-initializes.
        c.  Trigger a backend hashing operation for `test_data_block_agl_001.txt` using the `HashingService`.
        d.  Capture `calculated_hash_A`.
    2.  **Step Group 2 (Hash_Algo_B):**
        a.  Configure Fava (`FavaOptions`) to use `Hash_Algo_B` for hashing.
        b.  Restart Fava or ensure `CryptoService` re-initializes.
        c.  Trigger a backend hashing operation for `test_data_block_agl_001.txt` using the `HashingService`.
        d.  Capture `calculated_hash_B`.
*   **Expected Results:**
    1.  `calculated_hash_A` matches `expected_hash_A_001.txt`.
    2.  `calculated_hash_B` matches `expected_hash_B_001.txt`.
    3.  Fava operates correctly under both configurations.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_001",
      "status": "PASSED/FAILED",
      "results_algo_A": {
        "configured_algorithm": "SHA-256", // Example for Hash_Algo_A
        "calculated_hash": "actual_hex_digest_A",
        "expected_hash": "content_of_expected_hash_A_001.txt",
        "hash_match": true
      },
      "results_algo_B": {
        "configured_algorithm": "SHA3-256", // Example for Hash_Algo_B
        "calculated_hash": "actual_hex_digest_B",
        "expected_hash": "content_of_expected_hash_B_001.txt",
        "hash_match": true
      },
      "log_evidence": { // Optional: check logs for service initialization with correct algo
        "algo_A_init_log_present": true,
        "algo_B_init_log_present": true
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_002
*   **Test Title/Objective:** Verify backend PQC KEM for data-at-rest decryption can be switched via configuration.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr21`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#nfr37`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#nfr37)
*   **Preconditions:**
    1.  Fava's `CryptoService` supports two PQC KEMs for hybrid decryption: `PQC_KEM_Suite_X` (e.g., Kyber768 + AES256GCM) and `PQC_KEM_Suite_Y` (e.g., Kyber1024 + AES256GCM, or a different KEM like FrodoKEM + AES256GCM if supported).
    2.  `file_X.bc.pqc` encrypted with `PQC_KEM_Suite_X` and its corresponding private key `key_X`.
    3.  `file_Y.bc.pqc` encrypted with `PQC_KEM_Suite_Y` and its corresponding private key `key_Y`.
    4.  Plaintext versions and expected API outputs for both files are known (e.g., `expected_output_X.json`, `expected_output_Y.json`).
*   **Test Steps (User actions or system interactions):**
    1.  **Step Group 1 (PQC_KEM_Suite_X):**
        a.  Configure Fava (`FavaOptions`) for `PQC_KEM_Suite_X`, providing `key_X`.
        b.  Restart Fava / re-initialize `CryptoService`.
        c.  Attempt to load `file_X.bc.pqc`. Verify successful load and API output matches `expected_output_X.json`.
        d.  Attempt to load `file_Y.bc.pqc`. Verify it fails to load (due to KEM/key mismatch).
    2.  **Step Group 2 (PQC_KEM_Suite_Y):**
        a.  Configure Fava (`FavaOptions`) for `PQC_KEM_Suite_Y`, providing `key_Y`.
        b.  Restart Fava / re-initialize `CryptoService`.
        c.  Attempt to load `file_Y.bc.pqc`. Verify successful load and API output matches `expected_output_Y.json`.
        d.  Attempt to load `file_X.bc.pqc`. Verify it fails to load.
*   **Expected Results:**
    1.  `file_X.bc.pqc` loads successfully only when Fava is configured for `PQC_KEM_Suite_X`.
    2.  `file_Y.bc.pqc` loads successfully only when Fava is configured for `PQC_KEM_Suite_Y`.
    3.  Decryption failures occur as expected when configurations don't match the file's encryption.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_002",
      "status": "PASSED/FAILED",
      "config_X_results": {
        "suite_configured": "PQC_KEM_Suite_X_Name",
        "load_file_X_status": "SUCCESS", // API output matches expected_output_X.json
        "load_file_X_log": "INFO: Successfully decrypted 'file_X.bc.pqc' using PQC KEM: [Suite_X_KEM_Name]",
        "load_file_Y_status": "FAILURE", // API indicates file not loaded or error
        "load_file_Y_log": "ERROR: Failed to decrypt 'file_Y.bc.pqc'. Mismatch or key error."
      },
      "config_Y_results": {
        "suite_configured": "PQC_KEM_Suite_Y_Name",
        "load_file_Y_status": "SUCCESS", // API output matches expected_output_Y.json
        "load_file_Y_log": "INFO: Successfully decrypted 'file_Y.bc.pqc' using PQC KEM: [Suite_Y_KEM_Name]",
        "load_file_X_status": "FAILURE",
        "load_file_X_log": "ERROR: Failed to decrypt 'file_X.bc.pqc'. Mismatch or key error."
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_003
*   **Test Title/Objective:** Verify frontend hashing uses the algorithm specified by backend configuration, demonstrating agility in frontend-backend crypto consistency.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr22`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr22)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr26`](../../../docs/specifications/PQC_Hashing_Spec.md#fr26)
*   **Preconditions:**
    1.  Fava backend supports `Hash_Algo_A` ("SHA-256") and `Hash_Algo_B` ("SHA3-256").
    2.  Fava frontend's crypto abstraction supports both algorithms.
    3.  Fava backend exposes the currently configured hashing algorithm via an API endpoint (e.g., `/api/fava_options/`).
    4.  A known data string (`test_string_agl_003`).
    5.  Expected hash for `test_string_agl_003` with `Hash_Algo_A` (`expected_frontend_hash_A_003.txt`).
    6.  Expected hash for `test_string_agl_003` with `Hash_Algo_B` (`expected_frontend_hash_B_003.txt`).
*   **Test Steps (User actions or system interactions):**
    1.  **Step Group 1 (Hash_Algo_A):**
        a.  Configure Fava backend for `Hash_Algo_A`. Restart Fava.
        b.  In a frontend test environment, load Fava.
        c.  Frontend fetches the configured hash algorithm ("SHA-256") from the backend API.
        d.  Frontend calculates hash of `test_string_agl_003` using its `calculateHash` function, explicitly passing the fetched algorithm name.
        e.  Capture `frontend_calculated_hash_A`.
    2.  **Step Group 2 (Hash_Algo_B):**
        a.  Configure Fava backend for `Hash_Algo_B`. Restart Fava.
        b.  In frontend test environment, reload Fava / re-fetch config.
        c.  Frontend fetches the new configured hash algorithm ("SHA3-256").
        d.  Frontend calculates hash of `test_string_agl_003` using `calculateHash` with the new algorithm.
        e.  Capture `frontend_calculated_hash_B`.
*   **Expected Results:**
    1.  Frontend correctly fetches and uses `Hash_Algo_A` in Step Group 1. `frontend_calculated_hash_A` matches `expected_frontend_hash_A_003.txt`.
    2.  Frontend correctly fetches and uses `Hash_Algo_B` in Step Group 2. `frontend_calculated_hash_B` matches `expected_frontend_hash_B_003.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_003",
      "status": "PASSED/FAILED",
      "results_algo_A": {
        "backend_config_for_hashing": "SHA-256",
        "frontend_fetched_config": "SHA-256", // From mocked API call in test
        "calculated_hash": "actual_frontend_hex_digest_A",
        "expected_hash": "content_of_expected_frontend_hash_A_003.txt",
        "hash_match": true
      },
      "results_algo_B": {
        "backend_config_for_hashing": "SHA3-256",
        "frontend_fetched_config": "SHA3-256",
        "calculated_hash": "actual_frontend_hex_digest_B",
        "expected_hash": "content_of_expected_frontend_hash_B_003.txt",
        "hash_match": true
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_004
*   **Test Title/Objective:** Verify graceful error handling if backend `CryptoService` is configured with an unknown/unsupported algorithm for a critical operation (e.g., data-at-rest decryption).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr27`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr27)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#ec61`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#ec61)
*   **Preconditions:**
    1.  Fava is configured (`FavaOptions`) to use an "UNKNOWN_KEM_SUITE" for data-at-rest decryption, which is not registered in the `CryptoService` factory.
    2.  A PQC-encrypted file `test_file.bc.pqc` exists.
*   **Test Steps (User actions or system interactions):**
    1.  Start Fava with the problematic configuration.
    2.  Attempt to load `test_file.bc.pqc`.
*   **Expected Results:**
    1.  Fava's `CryptoService` fails to initialize the decryption service for "UNKNOWN_KEM_SUITE".
    2.  A critical error is logged indicating the unsupported algorithm configuration.
    3.  Fava either fails to load the file with a specific error or, if the crypto context is essential for startup with an encrypted file, Fava might fail to fully start or operate in a clearly degraded mode for that file.
    4.  Fava application itself (if started) should remain stable and not crash.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_004",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "unsupported_algorithm_error_logged": true, // e.g., "CRITICAL: CryptoService: Unknown or unsupported KEM suite configured: UNKNOWN_KEM_SUITE"
        "service_initialization_failure_indicated": true
      },
      "fava_behavior": {
        "file_load_status": "FAILURE", // Or Fava fails to start if this is the primary ledger
        "application_stability": "STABLE" // Fava (the process) does not crash
      }
    }
    ```
*   **Test Priority:** Medium