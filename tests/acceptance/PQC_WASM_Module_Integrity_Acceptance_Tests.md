# High-Level Acceptance Tests: PQC WASM Module Integrity

**Version:** 1.0
**Date:** 2025-06-02
**PQC Focus Area:** WASM Module Integrity (PQC Digital Signatures for `tree-sitter-beancount.wasm`)

This document contains high-level end-to-end acceptance tests for verifying Post-Quantum Cryptography (PQC) integration related to WASM module integrity in Fava. This involves ensuring the Fava frontend can verify a PQC digital signature for the `tree-sitter-beancount.wasm` module.

---

## Test Cases

### Test ID: PQC_WASM_001
*   **Test Title/Objective:** Verify successful PQC signature verification and loading of the WASM parser module (Happy Path).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr25`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr25)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr26`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr26)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us41`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us41)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#51-use-case-frontend-verifies-and-loads-pqc-signed-wasm-module-happy-path`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#51-use-case-frontend-verifies-and-loads-pqc-signed-wasm-module-happy-path)
*   **Preconditions:**
    1.  The `tree-sitter-beancount.wasm` module is available.
    2.  A valid PQC signature file (`tree-sitter-beancount.wasm.sig`) for the WASM module exists, signed with `PQC_Signature_Algorithm_Y` (e.g., CRYSTALS-Dilithium2).
    3.  The Fava frontend has the corresponding PQC public key embedded/configured.
    4.  A JS/WASM PQC signature verification library supporting `PQC_Signature_Algorithm_Y` is integrated into the frontend.
    5.  PQC WASM signature verification is enabled in Fava's frontend configuration.
    6.  A small, valid Beancount snippet (`test_beancount_snippet_001.beancount`) exists. Expected AST/parsed output from this snippet using the WASM parser is known (`expected_ast_001.json`).
*   **Test Steps (User actions or system interactions):**
    1.  Load the Fava frontend in a browser or test environment (e.g., Playwright, Puppeteer).
    2.  The frontend attempts to load the `tree-sitter-beancount.wasm` module, triggering the PQC signature verification process.
    3.  After the WASM module is expected to be loaded, use a frontend function (or simulate UI interaction) that utilizes the parser on `test_beancount_snippet_001.beancount` to generate an AST or perform a basic parsing task.
*   **Expected Results:**
    1.  The PQC signature of the WASM module is successfully verified.
    2.  The WASM module is loaded and initialized without errors.
    3.  The parser correctly processes the test snippet.
    4.  A success message regarding signature verification is logged in the browser console.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_001",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "signature_verified_log_present": true, // Check console for "INFO: WASM module 'tree-sitter-beancount.wasm' PQC signature verified successfully using [Algorithm_Y_Name]."
        "algorithm_logged": "CRYSTALS-Dilithium2" // Example
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": true, // Inferred from successful parsing
        "test_snippet_parsed_correctly": true, // Compare AST output with `expected_ast_001.json`
        "parsing_error_present": false
      },
      "error_messages_present": false // No unexpected console errors related to WASM loading/verification
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_WASM_002
*   **Test Title/Objective:** Verify WASM module is NOT loaded if PQC signature verification fails (e.g., tampered WASM file).
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr27`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr27)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us43`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#us43)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#52-use-case-frontend-fails-to-verify-pqc-signed-wasm-module-invalid-signature`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#52-use-case-frontend-fails-to-verify-pqc-signed-wasm-module-invalid-signature)
*   **Preconditions:**
    1.  The `tree-sitter-beancount.wasm` module has been intentionally tampered with (e.g., a byte modified) after signing.
    2.  The original, valid PQC signature file (`tree-sitter-beancount.wasm.sig`) is available.
    3.  Frontend setup is as in PQC_WASM_001 (correct public key, PQC lib, verification enabled).
*   **Test Steps (User actions or system interactions):**
    1.  Load the Fava frontend.
    2.  The frontend attempts to load the (tampered) `tree-sitter-beancount.wasm` module and its original signature.
*   **Expected Results:**
    1.  PQC signature verification fails.
    2.  The WASM module is not loaded.
    3.  An error message indicating signature verification failure is logged in the browser console.
    4.  Features dependent on the parser (e.g., syntax highlighting) are degraded or unavailable.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_002",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "signature_verification_failed_log_present": true, // Check console for "ERROR: WASM module 'tree-sitter-beancount.wasm' PQC signature verification FAILED. Module not loaded."
        "no_success_log_present": true
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": false, // Check a flag or try to use parser, expect failure
        "dependent_feature_degraded": true // e.g., check if syntax highlighting CSS classes are absent
      }
    }
    ```
*   **Test Priority:** High

### Test ID: PQC_WASM_003
*   **Test Title/Objective:** Verify WASM module is NOT loaded if its PQC signature file (`.sig`) is missing.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#ec61`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#ec61)
*   **Preconditions:**
    1.  The valid `tree-sitter-beancount.wasm` module is available.
    2.  The PQC signature file (`tree-sitter-beancount.wasm.sig`) is MISSING from the expected location.
    3.  Frontend setup is as in PQC_WASM_001.
*   **Test Steps (User actions or system interactions):**
    1.  Load the Fava frontend.
    2.  The frontend attempts to load the WASM module and fetch its signature.
*   **Expected Results:**
    1.  Fetching the signature file fails (e.g., 404 error).
    2.  PQC signature verification cannot proceed and is marked as failed.
    3.  The WASM module is not loaded.
    4.  An error message is logged in the browser console indicating the missing signature file or verification failure.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_003",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "missing_signature_file_or_verification_failed_log_present": true, // e.g., "ERROR: Failed to fetch WASM signature for 'tree-sitter-beancount.wasm'. Verification skipped/failed." or "ERROR: ... PQC signature verification FAILED ..."
        "http_error_for_sig_file": 404 // If fetch error is specifically logged or checkable
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": false
      }
    }
    ```
*   **Test Priority:** Medium

### Test ID: PQC_WASM_004
*   **Test Title/Objective:** Verify WASM module loads without PQC verification if the feature is disabled in configuration.
*   **Link to relevant Specification section(s):**
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr29`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#fr29)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md#53-use-case-pqc-wasm-verification-disabled`](../../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md#53-use-case-pqc-wasm-verification-disabled)
*   **Preconditions:**
    1.  The `tree-sitter-beancount.wasm` module is available.
    2.  PQC WASM signature verification is explicitly DISABLED in Fava's frontend configuration.
    3.  (Signature file may or may not be present, it shouldn't matter).
    4.  Setup for parsing test snippet as in PQC_WASM_001.
*   **Test Steps (User actions or system interactions):**
    1.  Load the Fava frontend.
    2.  The frontend attempts to load the WASM module.
    3.  Attempt to parse `test_beancount_snippet_001.beancount`.
*   **Expected Results:**
    1.  The PQC signature verification process is skipped.
    2.  The WASM module is loaded directly.
    3.  The parser correctly processes the test snippet.
    4.  A warning message about verification being disabled might be logged in the console.
*   **AI Verifiable End Result (AVER):**
    A JSON object:
    ```json
    {
      "test_id": "PQC_WASM_004",
      "status": "PASSED/FAILED",
      "verification_log_evidence": {
        "verification_disabled_log_present": true, // Check console for "WARN: PQC WASM signature verification is disabled."
        "no_verification_attempt_log_present": true // No logs about attempting or succeeding/failing verification
      },
      "parser_functionality": {
        "wasm_module_loaded_successfully": true,
        "test_snippet_parsed_correctly": true // Compare AST output with `expected_ast_001.json`
      }
    }
    ```
*   **Test Priority:** Medium