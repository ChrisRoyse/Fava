# High-Level Acceptance Tests: PQC Cryptographic Agility

**Version:** 1.1
**Date:** 2025-06-02
**PQC Focus Area:** Cryptographic Agility

**Revision History:**
*   **1.1 (2025-06-02):** Aligned with [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md) v1.1.
    *   Updated algorithm examples (Kyber-768/1024, SHA3-256, X25519).
    *   Refined tests to reflect detailed configuration (e.g., `active_encryption_suite_id`, `decryption_attempt_order`).
    *   Enhanced PQC_AGL_002 to better cover decryption of files with legacy vs. active suites.
*   **1.0 (2025-06-02):** Initial version.

This document contains high-level end-to-end acceptance tests for verifying Fava's cryptographic agility. This involves ensuring Fava can switch between different cryptographic algorithms and configurations via its abstraction layers.

---

## Test Cases

### Test ID: PQC_AGL_001
*   **Test Title/Objective:** Verify backend hashing algorithm can be switched via configuration (SHA3-256 vs. SHA-256), and the correct hash is produced.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#us41`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#us41)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr22`](../../../docs/specifications/PQC_Hashing_Spec.md#fr22) (SHA3-256 default)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr23`](../../../docs/specifications/PQC_Hashing_Spec.md#fr23) (SHA-256 option)
*   **Preconditions:**
    1.  Fava's `HashingService` supports "SHA3-256" and "SHA256".
    2.  A known data block (`test_data_block_agl_001.txt`).
    3.  Expected SHA3-256 hash: `expected_sha3_256_hash_agl_001.txt`.
    4.  Expected SHA-256 hash: `expected_sha256_hash_agl_001.txt`.
*   **Test Steps (User actions or system interactions):**
    1.  **Step Group 1 (SHA3-256):**
        a.  Configure Fava (`FavaOptions`) `hashing.default_algorithm = "SHA3-256"`. Restart/re-init.
        b.  Trigger backend hashing of `test_data_block_agl_001.txt`. Capture `calculated_hash_sha3_256`.
    2.  **Step Group 2 (SHA-256):**
        a.  Configure Fava `hashing.default_algorithm = "SHA256"`. Restart/re-init.
        b.  Trigger backend hashing of `test_data_block_agl_001.txt`. Capture `calculated_hash_sha256`.
*   **Expected Results:**
    1.  `calculated_hash_sha3_256` matches `expected_sha3_256_hash_agl_001.txt`.
    2.  `calculated_hash_sha256` matches `expected_sha256_hash_agl_001.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_001",
      "status": "PASSED/FAILED",
      "results_sha3_256": {
        "configured_algorithm": "SHA3-256",
        "calculated_hash": "actual_hex_digest_sha3_256",
        "expected_hash": "content_of_expected_sha3_256_hash_agl_001.txt",
        "hash_match": true
      },
      "results_sha256": {
        "configured_algorithm": "SHA256",
        "calculated_hash": "actual_hex_digest_sha256",
        "expected_hash": "content_of_expected_sha256_hash_agl_001.txt",
        "hash_match": true
      },
      "log_evidence": {
        "sha3_init_log_present": true, // Optional: log for service init with SHA3-256
        "sha256_init_log_present": true  // Optional: log for service init with SHA256
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_002
*   **Test Title/Objective:** Verify backend PQC KEM suite for data-at-rest can be switched for new encryptions, and Fava can decrypt files encrypted with different (active vs. legacy) supported suites.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr23)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr29`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr29) (Decrypting older formats)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr21`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#nfr37`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#nfr37)
*   **Preconditions:**
    1.  Fava's `CryptoService` supports two PQC hybrid suites:
        *   `Suite_A` = `HYBRID_X25519_MLKEM768_AES256GCM` (Kyber-768 based)
        *   `Suite_B` = `HYBRID_X25519_MLKEM1024_AES256GCM` (Kyber-1024 based, hypothetical distinct suite)
    2.  `file_A.bc.pqc_fava` encrypted with `Suite_A` and its key `key_A_material`.
    3.  `file_B.bc.pqc_fava` encrypted with `Suite_B` and its key `key_B_material`.
    4.  Plaintext versions and expected API outputs for both files are known.
*   **Test Steps (User actions or system interactions):**
    1.  **Config 1 (Suite_A active, Suite_B legacy):**
        a.  Configure Fava: `active_encryption_suite_id = "Suite_A"`, `decryption_attempt_order = ["Suite_A", "Suite_B", "CLASSICAL_GPG"]`.
        b.  Provide `key_A_material` and `key_B_material` (e.g., passphrases). Restart/re-init.
        c.  Attempt to load `file_A.bc.pqc_fava`. Verify success (uses Suite_A).
        d.  Attempt to load `file_B.bc.pqc_fava`. Verify success (uses Suite_B from legacy attempt order).
        e.  Encrypt a new file `new_file_config1.bc` to `new_file_config1.pqc_fava`. Verify it's encrypted with `Suite_A`.
    2.  **Config 2 (Suite_B active, Suite_A legacy):**
        a.  Configure Fava: `active_encryption_suite_id = "Suite_B"`, `decryption_attempt_order = ["Suite_B", "Suite_A", "CLASSICAL_GPG"]`.
        b.  Provide `key_A_material` and `key_B_material`. Restart/re-init.
        c.  Attempt to load `file_A.bc.pqc_fava`. Verify success (uses Suite_A from legacy).
        d.  Attempt to load `file_B.bc.pqc_fava`. Verify success (uses Suite_B).
        e.  Encrypt a new file `new_file_config2.bc` to `new_file_config2.pqc_fava`. Verify it's encrypted with `Suite_B`.
*   **Expected Results:**
    1.  `file_A` and `file_B` load successfully under both configurations due to `decryption_attempt_order`.
    2.  New files are encrypted with the currently `active_encryption_suite_id`.
    3.  Logs indicate which suite was used for decryption.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_002",
      "status": "PASSED/FAILED",
      "config1_results": {
        "active_suite": "HYBRID_X25519_MLKEM768_AES256GCM",
        "load_file_A_status": "SUCCESS", "load_file_A_decryption_suite_logged": "HYBRID_X25519_MLKEM768_AES256GCM",
        "load_file_B_status": "SUCCESS", "load_file_B_decryption_suite_logged": "HYBRID_X25519_MLKEM1024_AES256GCM",
        "encrypt_new_file_suite_logged": "HYBRID_X25519_MLKEM768_AES256GCM"
      },
      "config2_results": {
        "active_suite": "HYBRID_X25519_MLKEM1024_AES256GCM",
        "load_file_A_status": "SUCCESS", "load_file_A_decryption_suite_logged": "HYBRID_X25519_MLKEM768_AES256GCM",
        "load_file_B_status": "SUCCESS", "load_file_B_decryption_suite_logged": "HYBRID_X25519_MLKEM1024_AES256GCM",
        "encrypt_new_file_suite_logged": "HYBRID_X25519_MLKEM1024_AES256GCM"
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_003
*   **Test Title/Objective:** Verify frontend hashing uses the algorithm specified by backend configuration (SHA3-256 vs. SHA-256).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr22`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr22)
    *   [`docs/specifications/PQC_Hashing_Spec.md#fr26`](../../../docs/specifications/PQC_Hashing_Spec.md#fr26)
*   **Preconditions:**
    1.  Fava backend supports "SHA3-256" and "SHA256". Frontend crypto abstraction supports both.
    2.  Backend exposes configured hashing algorithm via API.
    3.  Known data string (`test_string_agl_003`).
    4.  Expected SHA3-256 hash: `expected_frontend_sha3_256_agl_003.txt`.
    5.  Expected SHA-256 hash: `expected_frontend_sha256_agl_003.txt`.
*   **Test Steps (User actions or system interactions):**
    1.  **Step Group 1 (SHA3-256):**
        a.  Configure backend for "SHA3-256". Restart.
        b.  Frontend test env: Load Fava, fetch config ("SHA3-256").
        c.  Frontend calculates hash of `test_string_agl_003` using fetched algo. Capture `frontend_calculated_hash_sha3_256`.
    2.  **Step Group 2 (SHA-256):**
        a.  Configure backend for "SHA256". Restart.
        b.  Frontend test env: Reload Fava, fetch config ("SHA256").
        c.  Frontend calculates hash of `test_string_agl_003` using fetched algo. Capture `frontend_calculated_hash_sha256`.
*   **Expected Results:**
    1.  `frontend_calculated_hash_sha3_256` matches `expected_frontend_sha3_256_agl_003.txt`.
    2.  `frontend_calculated_hash_sha256` matches `expected_frontend_sha256_agl_003.txt`.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_003",
      "status": "PASSED/FAILED",
      "results_sha3_256": {
        "backend_config_for_hashing": "SHA3-256",
        "frontend_fetched_config": "SHA3-256",
        "calculated_hash": "actual_frontend_hex_digest_sha3_256",
        "expected_hash": "content_of_expected_frontend_sha3_256_agl_003.txt",
        "hash_match": true
      },
      "results_sha256": {
        "backend_config_for_hashing": "SHA256",
        "frontend_fetched_config": "SHA256",
        "calculated_hash": "actual_frontend_hex_digest_sha256",
        "expected_hash": "content_of_expected_frontend_sha256_agl_003.txt",
        "hash_match": true
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_AGL_004
*   **Test Title/Objective:** Verify graceful error handling if backend `CryptoService` is configured with an unknown/unsupported algorithm suite for data-at-rest.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr27`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#fr27)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#ec61`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#ec61)
*   **Preconditions:**
    1.  Fava is configured (`FavaOptions`) with `active_encryption_suite_id = "UNKNOWN_SUITE"`, which is not defined in `suites`.
    2.  A PQC-encrypted file `test_file.bc.pqc_fava` exists.
*   **Test Steps (User actions or system interactions):**
    1.  Start Fava with the problematic configuration.
    2.  Attempt to load `test_file.bc.pqc_fava` or encrypt a new file.
*   **Expected Results:**
    1.  `CryptoService` fails to initialize/find handler for "UNKNOWN_SUITE".
    2.  Critical error logged. File operations requiring the active suite fail.
    3.  Fava application (process) remains stable.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_AGL_004",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "unsupported_suite_error_logged": true, // e.g., "CRITICAL: CryptoService: Unknown or unsupported active_encryption_suite_id configured: UNKNOWN_SUITE"
        "service_initialization_failure_indicated": true
      },
      "fava_behavior": {
        "file_operation_status": "FAILURE", // e.g., load or encrypt fails
        "application_stability": "STABLE"
      }
    }
    ```
*   **Test Priority:** Medium