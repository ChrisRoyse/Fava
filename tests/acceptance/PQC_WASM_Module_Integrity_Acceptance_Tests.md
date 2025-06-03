# High-Level Acceptance Tests: PQC WASM Module Integrity

**Version:** 1.1
**Date:** 2025-06-02
**PQC Focus Area:** WASM Module Integrity (PQC Digital Signatures for `tree-sitter-beancount.wasm`)

**Revision History:**
*   **1.1 (2025-06-02):** Aligned with [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md) v1.1.
    *   Default PQC signature algorithm specified as Dilithium3.
    *   Updated tests to reflect Dilithium3 and `liboqs-js` reliance.
    *   Incorporated performance NFR considerations (logged verification time in AVERs).
*   **1.0 (2025-06-02):** Initial version.

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) integration related to WASM module integrity in Fava. This involves ensuring the Fava frontend can verify a Dilithium3 PQC digital signature for the `tree-sitter-beancount.wasm` module.

---

## Test Cases

### Test ID: PQC_WASM_001
*   **Test Title/Objective:** Verify successful Dilithium3 PQC signature verification and loading of the WASM parser module.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr25`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr25)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us41`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us41)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#51-use-case-frontend-verifies-and-loads-pqc-signed-wasm-module-happy-path`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#51-use-case-frontend-verifies-and-loads-pqc-signed-wasm-module-happy-path)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#nfr32`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#nfr32) (Performance)
*   **Preconditions:**
    1.  `tree-sitter-beancount.wasm` is available.
    2.  A valid Dilithium3 signature file (`tree-sitter-beancount.wasm.dilithium3.sig`) exists.
    3.  Fava frontend has the corresponding Dilithium3 public key embedded/configured.
    4.  `liboqs-js` (for Dilithium3 verification) is integrated into the frontend.
    5.  PQC WASM signature verification is enabled.
    6.  A Beancount snippet (`test_beancount_snippet_001.beancount`) and its expected AST (`expected_ast_001.json`) are available.
*   **Test Steps (User actions or system interactions):**
    1.  Load Fava frontend in a browser/test environment.
    2.  Frontend attempts to load `tree-sitter-beancount.wasm`, triggering Dilithium3 signature verification.
    3.  After expected load, use parser on `test_beancount_snippet_001.beancount`.
*   **Expected Results:**
    1.  Dilithium3 signature is successfully verified.
    2.  WASM module loads and initializes without errors.
    3.  Parser correctly processes the snippet. Verification time within NFR3.2 (< 50ms).
    4.  Success message (including verification time) logged in console.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_001",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "signature_verified_log_present": true, // Check console for "INFO: WASM module 'tree-sitter-beancount.wasm' Dilithium3 signature verified successfully in XXms."
        "algorithm_logged": "Dilithium3",
        "verification_time_logged_ms": "<captured_time_ms>"
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": true,
        "test_snippet_parsed_correctly": true, // Compare AST with `expected_ast_001.json`
        "parsing_error_present": false
      },
      "error_messages_present": false
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_WASM_002
*   **Test Title/Objective:** Verify WASM module is NOT loaded if Dilithium3 signature verification fails (e.g., tampered WASM file).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr27`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr27)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us43`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us43)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#52-use-case-frontend-fails-to-verify-pqc-signed-wasm-module-invalid-signature`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#52-use-case-frontend-fails-to-verify-pqc-signed-wasm-module-invalid-signature)
*   **Preconditions:**
    1.  `tree-sitter-beancount.wasm` is tampered. Original valid `.dilithium3.sig` is available.
    2.  Frontend setup as in PQC_WASM_001.
*   **Test Steps (User actions or system interactions):**
    1.  Load Fava frontend.
    2.  Frontend attempts to load tampered WASM and its original signature.
*   **Expected Results:**
    1.  Dilithium3 signature verification fails. WASM module not loaded.
    2.  Error message logged. Parser-dependent features degraded.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_002",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "signature_verification_failed_log_present": true, // Check console for "ERROR: WASM module 'tree-sitter-beancount.wasm' Dilithium3 signature verification FAILED. Module not loaded."
        "no_success_log_present": true
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": false,
        "dependent_feature_degraded": true
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_WASM_003
*   **Test Title/Objective:** Verify WASM module is NOT loaded if its Dilithium3 signature file (`.sig`) is missing.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#ec61`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#ec61)
*   **Preconditions:**
    1.  Valid `tree-sitter-beancount.wasm` available. `.dilithium3.sig` file is MISSING.
    2.  Frontend setup as in PQC_WASM_001.
*   **Test Steps (User actions or system interactions):**
    1.  Load Fava frontend.
    2.  Frontend attempts to load WASM and fetch its signature.
*   **Expected Results:**
    1.  Fetching signature file fails (404). Verification cannot proceed/fails.
    2.  WASM module not loaded. Error message logged.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_003",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "missing_signature_file_or_verification_failed_log_present": true, // e.g., "ERROR: Failed to fetch WASM signature for 'tree-sitter-beancount.wasm'. Verification skipped/failed." or "ERROR: ... Dilithium3 signature verification FAILED ..."
        "http_error_for_sig_file": 404 // If fetch error is checkable
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": false
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_WASM_004
*   **Test Title/Objective:** Verify WASM module loads without PQC verification if the feature is disabled.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr29`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr29)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#53-use-case-pqc-wasm-verification-disabled`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#53-use-case-pqc-wasm-verification-disabled)
*   **Preconditions:**
    1.  `tree-sitter-beancount.wasm` available.
    2.  PQC WASM signature verification is DISABLED in frontend configuration.
    3.  Test snippet setup as in PQC_WASM_001.
*   **Test Steps (User actions or system interactions):**
    1.  Load Fava frontend.
    2.  Frontend attempts to load WASM.
    3.  Attempt to parse `test_beancount_snippet_001.beancount`.
*   **Expected Results:**
    1.  PQC signature verification skipped. WASM module loaded directly.
    2.  Parser processes snippet correctly. Warning about disabled verification logged.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_004",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "verification_disabled_log_present": true, // Check console for "WARN: PQC WASM signature verification is disabled."
        "no_verification_attempt_log_present": true
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": true,
        "test_snippet_parsed_correctly": true // Compare AST with `expected_ast_001.json`
      }
    }
    ```
*   **Test Priority:** Medium