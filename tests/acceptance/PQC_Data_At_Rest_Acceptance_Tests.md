# High-Level Acceptance Tests: PQC Data at Rest

**Version:** 1.1
**Date:** 2025-06-02
**PQC Focus Area:** Data at Rest (Encrypted Beancount Files)

**Revision History:**
*   **1.1 (2025-06-02):** Aligned with [`docs/specifications/PQC_Data_At_Rest_Spec.md`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md) v1.1.
    *   Updated PQC hybrid suite to `FAVA_HYBRID_X25519_MLKEM768_AES256GCM` (X25519 + Kyber-768 + AES-256-GCM).
    *   Added new test cases (PQC_DAR_006, PQC_DAR_007) for Fava-driven PQC encryption.
    *   Revised existing tests for algorithm name changes, log messages, and performance NFR considerations (e.g., file sizes, logged timings in AVERs).
    *   Ensured AVERs are precise and machine-verifiable.
*   **1.0 (2025-06-02):** Initial version.

This document contains high-level end-to-end acceptance tests for verifying the Post-Quantum Cryptography (PQC) integration related to data at rest in Fava, primarily focusing on the encryption and decryption of Beancount files.

---

## Test Cases

### Test ID: PQC_DAR_001
*   **Test Title/Objective:** Verify successful decryption and loading of a Beancount file encrypted with the configured PQC hybrid suite (`FAVA_HYBRID_X25519_MLKEM768_AES256GCM`).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr21`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr21)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us42`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us42)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#51-use-case-load-pqc-hybrid-encrypted-beancount-file-happy-path`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#51-use-case-load-pqc-hybrid-encrypted-beancount-file-happy-path)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  Fava is configured to use the `FAVA_HYBRID_X25519_MLKEM768_AES256GCM` suite for PQC hybrid decryption via `FavaOptions` and the `CryptoService`.
    2.  A valid Beancount file (`test_pqc_dar_001.bc.pqc_hybrid_fava`, approx. 1MB) exists, encrypted using this suite.
    3.  The correct PQC decryption key material (e.g., passphrase for Fava-managed key, or path to private key file) for `test_pqc_dar_001.bc.pqc_hybrid_fava` is available to Fava.
    4.  The unencrypted version of the file (`test_pqc_dar_001_plain.bc`) is available, and a known API query (e.g., `/api/balance_sheet/`) on this plain file produces `expected_balance_sheet_001.json`.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load the PQC-hybrid-encrypted Beancount file `test_pqc_dar_001.bc.pqc_hybrid_fava`.
    3.  Once loaded, make an API request to `/api/balance_sheet/`.
*   **Expected Results:**
    1.  Fava successfully loads the Beancount file without errors.
    2.  The data presented by Fava accurately reflects the content of the decrypted Beancount file.
    3.  Fava logs indicate successful PQC decryption using the configured suite.
    4.  Fava logs the decryption time, which should be within the NFR3.2 target (e.g., 200-500ms for 1MB file).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_001",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_success_log_present": true, // check for "INFO: Successfully decrypted 'test_pqc_dar_001.bc.pqc_hybrid_fava' using PQC Hybrid Suite: FAVA_HYBRID_X25519_MLKEM768_AES256GCM"
        "decryption_algorithm_logged": "FAVA_HYBRID_X25519_MLKEM768_AES256GCM",
        "decryption_time_logged_ms": "<captured_time_ms>" // e.g., "INFO: Decryption of 'test_pqc_dar_001.bc.pqc_hybrid_fava' completed in XXXms"
      },
      "api_validation": {
        "endpoint_tested": "/api/balance_sheet/",
        "response_matches_expected": true // Compare API response with `expected_balance_sheet_001.json`
      },
      "error_messages_present": false
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_002
*   **Test Title/Objective:** Verify Fava handles an attempt to load a PQC-hybrid-encrypted file with an incorrect PQC key/passphrase.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr27`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr27)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us43`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us43)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#53-use-case-attempt-to-load-pqc-hybrid-encrypted-file-with-incorrect-keypassphrase`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#53-use-case-attempt-to-load-pqc-hybrid-encrypted-file-with-incorrect-keypassphrase)
*   **Preconditions:**
    1.  Fava is configured as in PQC_DAR_001.
    2.  A valid PQC-hybrid-encrypted Beancount file (`test_pqc_dar_001.bc.pqc_hybrid_fava`) exists.
    3.  Incorrect PQC decryption key material (wrong passphrase or path to wrong key file) is provided to Fava.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load `test_pqc_dar_001.bc.pqc_hybrid_fava`.
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure (e.g., "incorrect key/passphrase" or "decryption error") is logged.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_002",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // check for "ERROR: Failed to decrypt 'test_pqc_dar_001.bc.pqc_hybrid_fava'. Decryption error with PQC Hybrid Suite: FAVA_HYBRID_X25519_MLKEM768_AES256GCM. Incorrect key/passphrase or corrupted file."
        "no_successful_load_log": true
      },
      "fava_state": {
        "file_loaded": false,
        "application_operational": true
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_003
*   **Test Title/Objective:** Verify backward compatibility: Fava successfully loads a classically GPG-encrypted Beancount file.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr22`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr22)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us45`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us45)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#54-use-case-load-classically-gpg-encrypted-beancount-file-backward-compatibility`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#54-use-case-load-classically-gpg-encrypted-beancount-file-backward-compatibility)
*   **Preconditions:**
    1.  Fava is configured to support PQC decryption, and classical GPG decryption is enabled (e.g., as part of `decryption_attempt_order`).
    2.  A valid Beancount file (`test_gpg_dar_003.bc.gpg`) exists, encrypted using classical GPG.
    3.  The correct GPG key for `test_gpg_dar_003.bc.gpg` is available in the user's GPG agent/keyring, and Fava is configured to use it.
    4.  The unencrypted version of `test_gpg_dar_003.bc.gpg` (`test_gpg_dar_003_plain.bc`) produces `expected_balance_sheet_003.json` via API.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load `test_gpg_dar_003.bc.gpg`.
    3.  Once loaded, make an API request (e.g., `/api/balance_sheet/`).
*   **Expected Results:**
    1.  Fava successfully loads the Beancount file using GPG.
    2.  The data presented by Fava accurately reflects the decrypted GPG file.
    3.  Fava logs indicate successful GPG decryption.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_003",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "gpg_decryption_success_log_present": true, // check for "INFO: Successfully decrypted 'test_gpg_dar_003.bc.gpg' using CLASSICAL_GPG" or similar Beancount loader log
        "no_pqc_decryption_attempt_log_for_this_file": true // ensure PQC path wasn't incorrectly tried first if file is clearly GPG and GPG is earlier in attempt order or identified by extension
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
*   **Test Title/Objective:** Verify Fava handles a PQC-hybrid-encrypted file that is corrupted (e.g., AEAD tag mismatch).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#ec61`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#ec61)
*   **Preconditions:**
    1.  Fava is configured as in PQC_DAR_001.
    2.  A PQC-hybrid-encrypted file (`test_pqc_dar_004_corrupted.bc.pqc_hybrid_fava`) exists, but its content (ciphertext or AEAD tag) has been intentionally corrupted.
    3.  The correct PQC decryption key material is available.
*   **Test Steps (User actions or system interactions):**
    1.  Start the Fava application.
    2.  Instruct Fava to load `test_pqc_dar_004_corrupted.bc.pqc_hybrid_fava`.
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure due to corruption (e.g., "integrity check failed," "corrupted data," or AES-GCM error) is logged.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_004",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // e.g., "ERROR: Failed to decrypt 'test_pqc_dar_004_corrupted.bc.pqc_hybrid_fava'. Data integrity check failed for suite FAVA_HYBRID_X25519_MLKEM768_AES256GCM."
        "corruption_error_indicated": true
      },
      "fava_state": {
        "file_loaded": false,
        "application_operational": true
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DAR_005
*   **Test Title/Objective:** Verify Fava handles an attempt to load a PQC-hybrid-encrypted file when Fava is configured for a *different* PQC KEM suite (or the file's metadata indicates a different suite).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#ec62`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#ec62)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md#53-use-case-fava-decrypts-file-encrypted-with-a-previous-pqc-suite`](../../../docs/specifications/PQC_Cryptographic_Agility_Spec.md#53-use-case-fava-decrypts-file-encrypted-with-a-previous-pqc-suite) (failure aspect)
*   **Preconditions:**
    1.  A Beancount file (`test_pqc_dar_001.bc.pqc_hybrid_fava`) exists, encrypted using `FAVA_HYBRID_X25519_MLKEM768_AES256GCM`.
    2.  The correct decryption key material for this suite is available.
    3.  Fava is configured with `active_encryption_suite_id` set to `FAVA_HYBRID_X25519_MLKEM1024_AES256GCM` (a different, hypothetical suite), and `FAVA_HYBRID_X25519_MLKEM768_AES256GCM` is NOT in its `decryption_attempt_order` or the file metadata explicitly points to the original suite which is not the active one for decryption attempt.
*   **Test Steps (User actions or system interactions):**
    1.  Start Fava with the mismatched active suite configuration.
    2.  Instruct Fava to load `test_pqc_dar_001.bc.pqc_hybrid_fava`.
*   **Expected Results:**
    1.  Fava fails to load the Beancount file.
    2.  A clear error message indicating decryption failure due to algorithm/suite mismatch is logged.
    3.  Fava remains operational.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_005",
      "status": "PASSED/FAILED",
      "log_evidence": {
        "decryption_failure_log_present": true, // e.g., "ERROR: Failed to decrypt 'test_pqc_dar_001.bc.pqc_hybrid_fava'. No configured decryption handler succeeded. Active suite: FAVA_HYBRID_X25519_MLKEM1024_AES256GCM. File may use FAVA_HYBRID_X25519_MLKEM768_AES256GCM."
        "algorithm_mismatch_indicated": true
      },
      "fava_state": {
        "file_loaded": false,
        "application_operational": true
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_DAR_006
*   **Test Title/Objective:** Verify successful Fava-driven PQC hybrid encryption of a new Beancount file using the configured suite (`FAVA_HYBRID_X25519_MLKEM768_AES256GCM`).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr25`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr25)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#us41`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#us41)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#52-use-case-encrypt-new-beancount-file-with-pqc-hybrid-using-fava`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#52-use-case-encrypt-new-beancount-file-with-pqc-hybrid-using-fava)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  Fava is configured with `active_encryption_suite_id` as `FAVA_HYBRID_X25519_MLKEM768_AES256GCM` and `pqc_encryption_enabled` as true.
    2.  Fava's `key_management_mode` is set (e.g., `PASSPHRASE_DERIVED`).
    3.  A plaintext Beancount file (`test_pqc_dar_006_plain.bc`, approx. 1MB) exists.
    4.  A known passphrase for encryption is available.
*   **Test Steps (User actions or system interactions):**
    1.  Start Fava.
    2.  Through Fava's UI or a test script simulating its API, initiate PQC encryption for `test_pqc_dar_006_plain.bc` to `test_pqc_dar_006_encrypted.bc.pqc_hybrid_fava`, providing the passphrase.
    3.  After encryption, instruct Fava to load the newly encrypted file `test_pqc_dar_006_encrypted.bc.pqc_hybrid_fava` (using the same passphrase for decryption).
    4.  Make an API request (e.g., `/api/balance_sheet/`) on the loaded encrypted file.
*   **Expected Results:**
    1.  Fava successfully encrypts the file.
    2.  The encrypted file `test_pqc_dar_006_encrypted.bc.pqc_hybrid_fava` is created.
    3.  Fava logs indicate successful PQC encryption using the configured suite and the encryption time.
    4.  Fava successfully decrypts and loads the newly encrypted file.
    5.  API response matches the expected output for the original plaintext file.
    6.  Encryption time logged should be within NFR3.2 target (e.g., 200-600ms for 1MB file).
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_006",
      "status": "PASSED/FAILED",
      "encryption_log_evidence": {
        "encryption_success_log_present": true, // "INFO: Successfully encrypted 'test_pqc_dar_006_plain.bc' to 'test_pqc_dar_006_encrypted.bc.pqc_hybrid_fava' using PQC Hybrid Suite: FAVA_HYBRID_X25519_MLKEM768_AES256GCM"
        "encryption_algorithm_logged": "FAVA_HYBRID_X25519_MLKEM768_AES256GCM",
        "encryption_time_logged_ms": "<captured_encryption_time_ms>"
      },
      "decryption_log_evidence": {
        "decryption_success_log_present": true, // For the re-load
        "decryption_algorithm_logged": "FAVA_HYBRID_X25519_MLKEM768_AES256GCM"
      },
      "file_system_check": {
        "encrypted_file_created": true // Check if 'test_pqc_dar_006_encrypted.bc.pqc_hybrid_fava' exists
      },
      "api_validation_on_reload": {
        "endpoint_tested": "/api/balance_sheet/",
        "response_matches_expected_for_plain_file": true
      },
      "error_messages_present": false
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_DAR_007
*   **Test Title/Objective:** Verify Fava-driven PQC encryption handles key generation/derivation correctly based on passphrase.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md#fr28`](../../../docs/specifications/PQC_Data_At_Rest_Spec.md#fr28)
*   **Preconditions:**
    1.  Fava configured as in PQC_DAR_006 (`PASSPHRASE_DERIVED` mode).
    2.  Plaintext file `test_pqc_dar_007_plain.bc`.
    3.  Passphrase A: "correct_horse_battery_staple_PQC1"
    4.  Passphrase B: "incorrect_horse_battery_staple_PQC2"
*   **Test Steps (User actions or system interactions):**
    1.  Encrypt `test_pqc_dar_007_plain.bc` to `file_A.pqc` using Fava with Passphrase A.
    2.  Attempt to decrypt `file_A.pqc` using Fava with Passphrase B. (Expect Failure)
    3.  Attempt to decrypt `file_A.pqc` using Fava with Passphrase A. (Expect Success)
*   **Expected Results:**
    1.  Encryption with Passphrase A succeeds.
    2.  Decryption with Passphrase B fails with an "incorrect key/passphrase" error.
    3.  Decryption with Passphrase A succeeds.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_DAR_007",
      "status": "PASSED/FAILED",
      "encryption_A_status": "SUCCESS", // Log check for successful encryption
      "decryption_B_status": "FAILURE", // Log check for decryption failure with wrong passphrase
      "decryption_A_status": "SUCCESS", // Log check for successful decryption with correct passphrase
      "error_messages_present_for_B": true,
      "no_error_messages_for_A_encryption_decryption": true
    }
    ```
*   **Test Priority:** High