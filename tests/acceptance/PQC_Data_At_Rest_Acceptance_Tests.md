# High-Level Acceptance Tests: PQC Data at Rest

**Version:** 1.0
**Date:** 2025-06-02
**PQC Focus Area:** Data at Rest (Encrypted Beancount Files)

This document contains high-level end-to-end acceptance tests for verifying the Post-Quantum Cryptography (PQC) integration related to data at rest in Fava, primarily focusing on the encryption and decryption of Beancount files.

---

## Test Cases

### Test ID: PQC_DAR_001
*   **Test Title/Objective:** Verify successful decryption and loading of a Beancount file encrypted with a configured PQC hybrid scheme (Happy Path).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr21`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us42`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us42)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#51-use-case-load-pqc-encrypted-beancount-file-happy-path`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#51-use-case-load-pqc-encrypted-beancount-file-happy-path)
*   **Preconditions:**
    1.  Fava is configured to use `PQC_KEM_Algorithm_X` (e.g., CRYSTALS-Kyber768) and `Symmetric_Cipher_Y` (e.g., AES-256-GCM) for PQC hybrid decryption via `FavaOptions` and the `CryptoService`.
    2.  A valid Beancount file (`test_pqc_dar_001.bc.pqc`) exists, encrypted using `PQC_KEM_Algorithm_X` + `Symmetric_Cipher_Y`.
    3.  The correct PQC private key for `test_pqc_dar_001.bc.pqc` is available to Fava (e.g., via configured file path).
    4.  The unencrypted version of `test_pqc_dar_001.bc.pqc` (named `test_pqc_dar_001_plain.bc`) is available, and a known API query (e.g., `/api/balance_sheet/`) on this plain file produces a known JSON output (`expected_balance_sheet_001.json`).
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load the PQC-encrypted Beancount file `test_pqc_dar_001.bc.pqc`.
    3.  Once loaded, make an API request to a standard Fava endpoint that reflects the content of the Beancount file (e.g., `/api/balance_sheet/`).
*   **Expected Results:**
    1.  Fava successfully loads the Beancount file without errors.
    2.  The data presented by Fava (e.g., via API, UI) accurately reflects the content of the decrypted Beancount file.
    3.  Fava logs indicate successful PQC decryption.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_001",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_success_log_present": true, // check for "INFO: Successfully decrypted 'test_pqc_dar_001.bc.pqc' using PQC KEM: [Algorithm_X_Name]"
        "decryption_algorithm_logged": "CRYSTALS-Kyber768" // Example, actual name from config
      },
      "api_validation": {
        "endpoint_tested": "/api/balance_sheet/",
        "response_matches_expected": true // Compare API response with content of `expected_balance_sheet_001.json`
      },
      "error_messages_present": false // No unexpected error messages in Fava logs related to loading this file
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_002
*   **Test Title/Objective:** Verify Fava handles an attempt to load a PQC-encrypted file with an incorrect PQC key.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr27`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr27)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us43`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us43)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#52-use-case-attempt-to-load-pqc-encrypted-file-with-incorrect-key`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#52-use-case-attempt-to-load-pqc-encrypted-file-with-incorrect-key)
*   **Preconditions:**
    1.  Fava is configured as in PQC_DAR_001.
    2.  A valid PQC-encrypted Beancount file (`test_pqc_dar_001.bc.pqc`) exists.
    3.  An incorrect PQC private key (not matching the key used for encryption) is provided to Fava for `test_pqc_dar_001.bc.pqc`.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load `test_pqc_dar_001.bc.pqc`.
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure (e.g., "incorrect key" or "decryption error") is logged by Fava and potentially shown in the UI if a file loading status is displayed.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_002",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // check for "ERROR: Failed to decrypt 'test_pqc_dar_001.bc.pqc'. Decryption error with PQC KEM: [Algorithm_X_Name]. Incorrect key or corrupted file."
        "no_successful_load_log": true
      },
      "fava_state": {
        "file_loaded": false, // API check for loaded file status, or check if Fava reports no file loaded
        "application_operational": true // Fava responds to other status requests
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_003
*   **Test Title/Objective:** Verify backward compatibility: Fava successfully loads a classically GPG-encrypted Beancount file.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr22`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr22)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us45`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us45)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#53-use-case-load-classically-gpg-encrypted-beancount-file`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#53-use-case-load-classically-gpg-encrypted-beancount-file)
*   **Preconditions:**
    1.  Fava is configured to support PQC decryption, but also has classical GPG decryption enabled (either as a fallback or primary for non-PQC files).
    2.  A valid Beancount file (`test_gpg_dar_003.bc.gpg`) exists, encrypted using classical GPG.
    3.  The correct GPG key for `test_gpg_dar_003.bc.gpg` is available in the user's GPG agent/keyring, and Fava is configured to use it (e.g., `encryption_key` option in Beancount file or Fava config).
    4.  The unencrypted version of `test_gpg_dar_003.bc.gpg` (named `test_gpg_dar_003_plain.bc`) is available, and a known API query on this plain file produces `expected_balance_sheet_003.json`.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load the GPG-encrypted Beancount file `test_gpg_dar_003.bc.gpg`.
    3.  Once loaded, make an API request (e.g., `/api/balance_sheet/`).
*   **Expected Results:**
    1.  Fava successfully loads the Beancount file without errors using GPG.
    2.  The data presented by Fava accurately reflects the content of the decrypted GPG file.
    3.  Fava logs indicate successful GPG decryption.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_003",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "gpg_decryption_success_log_present": true, // check for "INFO: Successfully decrypted 'test_gpg_dar_003.bc.gpg' using classical GPG" or similar Beancount loader log
        "no_pqc_decryption_attempt_log_for_this_file": true // ensure PQC path wasn't incorrectly tried first if file is clearly GPG
      },
      "api_validation": {
        "endpoint_tested": "/api/balance_sheet/",
        "response_matches_expected": true // Compare API response with `expected_balance_sheet_003.json`
      },
      "error_messages_present": false
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_004
*   **Test Title/Objective:** Verify Fava handles a PQC-encrypted file that is corrupted.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#ec61`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#ec61)
*   **Preconditions:**
    1.  Fava is configured as in PQC_DAR_001.
    2.  A PQC-encrypted Beancount file (`test_pqc_dar_004_corrupted.bc.pqc`) exists, but its content (ciphertext part) has been intentionally corrupted (e.g., a few bytes flipped after encryption).
    3.  The correct PQC private key is available to Fava.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load `test_pqc_dar_004_corrupted.bc.pqc`.
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure due to corruption (e.g., "integrity check failed," "corrupted data," or similar error from the symmetric cipher like AES-GCM) is logged.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_004",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // e.g., "ERROR: Failed to decrypt 'test_pqc_dar_004_corrupted.bc.pqc'. Data integrity check failed."
        "corruption_error_indicated": true // Log message specifically points to corruption or integrity issue
      },
      "fava_state": {
        "file_loaded": false,
        "application_operational": true
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DAR_005
*   **Test Title/Objective:** Verify Fava handles an attempt to load a PQC-encrypted file when Fava is configured for a *different* PQC KEM algorithm.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#ec62`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#ec62)
*   **Preconditions:**
    1.  A valid Beancount file (`test_pqc_dar_001.bc.pqc`) exists, encrypted using `PQC_KEM_Algorithm_X` (e.g., CRYSTALS-Kyber768).
    2.  The correct PQC private key for `PQC_KEM_Algorithm_X` is available.
    3.  Fava is configured to use a *different* PQC KEM, `PQC_KEM_Algorithm_Z` (e.g., another NIST KEM, or a different Kyber variant like Kyber1024, assuming keys are incompatible), for PQC hybrid decryption.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application with configuration for `PQC_KEM_Algorithm_Z`.
    2.  Instruct Fava to load `test_pqc_dar_001.bc.pqc` (which was encrypted with `PQC_KEM_Algorithm_X`).
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure, possibly due to algorithm mismatch or inability to process the KEM ciphertext, is logged.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_005",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // e.g., "ERROR: Failed to decrypt 'test_pqc_dar_001.bc.pqc'. Configured KEM [Algorithm_Z_Name] may not match file's KEM [Algorithm_X_Name]."
        "algorithm_mismatch_indicated": true // Log message suggests algorithm incompatibility
      },
      "fava_state": {
        "file_loaded": false,
        "application_operational": true
      }
    }
    ```
*   **Test Priority:** Medium