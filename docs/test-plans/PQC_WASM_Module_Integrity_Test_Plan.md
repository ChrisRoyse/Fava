# Test Plan: PQC WASM Module Integrity

**Version:** 1.0
**Date:** 2025-06-03
**Feature:** PQC WASM Module Integrity

## 1. Introduction

This document outlines the granular test plan for the "PQC WASM Module Integrity" feature of the Fava application. The goal of this feature is to ensure that WebAssembly (WASM) modules, specifically `tree-sitter-beancount.wasm`, are authentic and have not been tampered with, using Dilithium3 PQC digital signatures.

This test plan is derived from:
*   **Primary Project Planning Document:** [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md) (v1.1)
*   **Specification:** [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md) (v1.1)
*   **Pseudocode:** [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](../../docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md) (v1.0)
*   **Architecture:** [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md) (v1.0)

The AI verifiable outcome of this document is its creation and existence at [`docs/test-plans/PQC_WASM_Module_Integrity_Test_Plan.md`](docs/test-plans/PQC_WASM_Module_Integrity_Test_Plan.md), containing all specified sections and AI verifiable criteria.

## 2. Test Scope

The primary scope of these granular tests is to verify the correct implementation of the PQC WASM Module Integrity feature as defined in its specification and pseudocode. Successful execution of these tests will directly contribute to satisfying the following AI Verifiable End Results (AVERs) from the [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md):

*   **AVER for Task 4.X.B (Feature Implementation & Iteration - PQC WASM Module Integrity):** "All granular tests defined in 4.X.A for the PQC WASM Module Integrity feature pass. Code is committed to a feature branch. Code review comments (initial pass) are addressed."
*   This also supports the overall AVERs for Phase 4 (Refinement) and Phase 5 (Completion) by ensuring this specific PQC feature is correctly implemented and robustly tested.

These tests cover the frontend logic responsible for fetching, verifying, and loading the `tree-sitter-beancount.wasm` module, including various success, failure, and edge case scenarios.

**AI Verifiable Criterion for Test Scope Definition:** This section accurately identifies the PQC Master Project Plan AVERs that the test cases herein are designed to validate for the PQC WASM Module Integrity feature.

## 3. Test Strategy

### 3.1. Approach: London School of TDD

This test plan adopts the **London School of Test-Driven Development (TDD)** principles.
*   **Interaction-Based Testing:** Tests will focus on verifying the behavior of a unit (e.g., `WasmLoaderService`) by observing its interactions with its collaborators (e.g., `PqcVerificationService`, `Fetch API`).
*   **Mocking/Stubbing Collaborators:** All external dependencies and collaborators of the Unit Under Test (UUT) will be mocked or stubbed. This isolates the UUT, allows precise control over the test environment, and ensures tests are fast and deterministic. For example, `liboqs-js` will be mocked to simulate PQC verification outcomes, and the `Fetch API` will be mocked to simulate network responses.
*   **Observable Outcomes:** Tests will assert on the observable outcomes of these interactions (e.g., a specific function on a mock was called with expected parameters, the UUT returned an expected value based on mocked collaborator behavior) rather than checking the internal state of the UUT.

### 3.2. Test Levels

The tests defined are primarily **unit tests** targeting the individual frontend services and components detailed in the [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md), such as the `WasmLoaderService` and `PqcVerificationService`.

### 3.3. Test Environment & Data

*   **Environment:** A JavaScript testing framework (e.g., Vitest, Jest) capable of running in a Node.js environment or a browser-like environment (via JSDOM if necessary for specific browser APIs not easily mocked).
*   **Test Data:**
    *   Mock `tree-sitter-beancount.wasm` data (as `ArrayBuffer`).
    *   Mock PQC Dilithium3 signatures (valid and invalid, as `ArrayBuffer`).
    *   Mock PQC Dilithium3 public keys (Base64 encoded strings).
    *   Mocked configuration objects (`PQC_WASM_CONFIG`).
*   **Mocked Collaborators:**
    *   `ConfigService`: To provide PQC configuration.
    *   Browser `Fetch API`: To simulate fetching WASM and signature files.
    *   `liboqs-js` (or its wrapper in `PqcVerificationService`): To simulate PQC verification results.
    *   Browser `WebAssembly API`: To simulate WASM instantiation.
    *   `NotificationService`: To verify UI notifications are triggered.
    *   Helper functions (e.g., `DECODE_BASE64_TO_BYTE_ARRAY`, `GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM`) if their direct testing is not covered by service-level tests.

**AI Verifiable Criterion for Test Strategy Definition:** This section accurately describes the adoption of London School TDD, defines test levels, and outlines the necessary test environment, data, and collaborator mocking strategy.

## 4. Recursive Testing Strategy (Regression Testing)

### 4.1. Goal

To ensure the ongoing stability and correctness of the PQC WASM Module Integrity feature as the Fava application evolves, and to catch regressions early.

### 4.2. Triggers for Re-running Test Suites

The PQC WASM Integrity test suite (or relevant subsets) will be re-executed upon the following SDLC touchpoints:
1.  **Post-Commit/Pre-Merge (CI Pipeline):** All tests in this plan will run automatically on every commit to a feature branch related to PQC WASM integrity, and on every Pull Request targeting `main` or `develop` branches.
2.  **Dependency Updates:** If `liboqs-js` is updated, or if there are significant changes to browser APIs that `Fetch` or `WebAssembly` instantiation rely on.
3.  **Refactoring:** After any refactoring of the `WasmLoaderService`, `PqcVerificationService`, `ConfigService`, or related PQC components.
4.  **Build Process Changes:** If the process for signing the WASM module or generating/embedding the PQC public key in the frontend configuration changes.
5.  **Scheduled Runs:** As part of a nightly or regular full regression suite run for the entire Fava application.

### 4.3. Test Prioritization & Tagging

Tests will be tagged to allow for flexible execution:
*   `@critical_path`: Tests covering the main success scenarios and most common failure modes (e.g., valid signature, invalid signature).
*   `@error_handling`: Tests specifically for edge cases and error conditions (e.g., file not found, bad configuration).
*   `@config_related`: Tests verifying behavior based on different PQC configurations (e.g., verification enabled/disabled).
*   `@pqc_wasm_integrity`: A general tag for all tests in this plan.

### 4.4. Test Subset Selection for Regression

*   **CI Pipeline (Commit/PR):** Run all tests tagged `@pqc_wasm_integrity`.
*   **Targeted Regression:** If a change is localized (e.g., only in `PqcVerificationService`), developers can manually trigger tests for that service and its direct interactions.
*   **Smoke Tests:** A subset of `@critical_path` tests can be designated as smoke tests for very quick feedback loops during development or in a rapid CI stage.

### 4.5. AI Verifiable Criterion for Recursive Testing Strategy Implementation

A CI/CD pipeline configuration (e.g., GitHub Actions workflow file) exists and is verifiably active. This configuration explicitly includes a job or step that executes the test suite associated with the `@pqc_wasm_integrity` tag (or equivalent test runner command) based on the defined triggers (e.g., on push to specific branches, on pull request). Test execution reports from this CI job are generated, stored, and auditable.

## 5. Test Cases

The following test cases are derived primarily from the TDD anchors in [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](../../docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md) and requirements in [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md).

**Common Collaborators & Mocks (unless specified otherwise):**
*   `mockConfigService`: Provides `PQC_WASM_CONFIG`.
*   `mockFetch`: Simulates `fetch()` calls and responses.
*   `mockLibOqsJsVerify`: Simulates the `verify` method of the PQC library.
*   `mockWasmApiInstantiate`: Simulates `WebAssembly.instantiate()`.
*   `mockNotificationService`: Spy on `notifyUIDegradedFunctionality()`.
*   `mockDecodeBase64`: Simulates Base64 decoding.
*   `mockGetPqcVerifier`: Simulates obtaining a PQC verifier instance.

---

### 5.1. Tests for `PqcVerificationService.verifyPqcWasmSignature()`

**UUT:** `PqcVerificationService.verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName)`

| Test Case ID | Description | Inspired by TDD Anchor/Spec/Pseudo | Targeted AVER(s) | Preconditions/Test Data | Mocked Collaborator Behavior | Steps | Expected Observable Outcome | AI Verifiable Completion Criterion | Recursive Scope |
|---|---|---|---|---|---|---|---|---|---|
| PWMI_TC_PVS_001 | Valid Dilithium3 signature returns true | Pseudo: `test_verifyPqcWasmSignature_dilithium3_valid_signature_returns_true()` | 4.X.B | Valid `wasmBuffer`, `signatureBuffer`, `publicKeyBase64` for Dilithium3. `algorithmName` = "Dilithium3". | `mockGetPqcVerifier` returns a valid verifier. `mockLibOqsJsVerify` (called by verifier) returns `true`. `mockDecodeBase64` returns valid `publicKeyBytes`. | Call UUT. | Returns `true`. `mockLibOqsJsVerify` called with correct `messageBytes`, `signatureBytes`, `publicKeyBytes`. | UUT returns `true`, and `mockLibOqsJsVerify` confirms it was called with byte arrays derived from inputs and the decoded public key. | `CI-Commit`, `Full-Regression` |
| PWMI_TC_PVS_002 | Invalid Dilithium3 signature returns false | Pseudo: `test_verifyPqcWasmSignature_dilithium3_invalid_signature_returns_false()` | 4.X.B | Valid `wasmBuffer`, **invalid** `signatureBuffer`, `publicKeyBase64`. `algorithmName` = "Dilithium3". | `mockGetPqcVerifier` returns a valid verifier. `mockLibOqsJsVerify` returns `false`. `mockDecodeBase64` returns valid `publicKeyBytes`. | Call UUT. | Returns `false`. `mockLibOqsJsVerify` called. | UUT returns `false`, and `mockLibOqsJsVerify` confirms it was called. | `CI-Commit`, `Full-Regression` |
| PWMI_TC_PVS_003 | Tampered WASM (valid signature) returns false | Pseudo: `test_verifyPqcWasmSignature_dilithium3_tampered_wasm_returns_false()` | 4.X.B | **Tampered** `wasmBuffer`, original valid `signatureBuffer`, `publicKeyBase64`. `algorithmName` = "Dilithium3". | `mockGetPqcVerifier` returns valid verifier. `mockLibOqsJsVerify` returns `false`. `mockDecodeBase64` returns valid `publicKeyBytes`. | Call UUT. | Returns `false`. `mockLibOqsJsVerify` called. | UUT returns `false`, and `mockLibOqsJsVerify` confirms it was called with the tampered WASM data. | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_PVS_004 | Wrong public key returns false | Pseudo: `test_verifyPqcWasmSignature_dilithium3_wrong_public_key_returns_false()` | 4.X.B | Valid `wasmBuffer`, `signatureBuffer`, **incorrect** `publicKeyBase64`. `algorithmName` = "Dilithium3". | `mockGetPqcVerifier` returns valid verifier. `mockLibOqsJsVerify` returns `false`. `mockDecodeBase64` returns bytes for the incorrect key. | Call UUT. | Returns `false`. `mockLibOqsJsVerify` called. | UUT returns `false`, and `mockLibOqsJsVerify` confirms it was called with the incorrect public key bytes. | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_PVS_005 | Unsupported algorithm returns false and logs error | Pseudo: `test_verifyPqcWasmSignature_unsupported_algorithm_returns_false()` | 4.X.B | Any `wasmBuffer`, `signatureBuffer`, `publicKeyBase64`. `algorithmName` = "UnsupportedAlgo". | `console.error` (or logger) spy. | Call UUT. | Returns `false`. Error logged about unsupported algorithm. `mockGetPqcVerifier` / `mockLibOqsJsVerify` not called for verification. | UUT returns `false` and mocked logger confirms an "Unsupported PQC algorithm" error message was logged. | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_PVS_006 | Public key decoding failure returns false and logs error | Pseudo: `test_verifyPqcWasmSignature_public_key_decoding_failure_returns_false()` (EC6.2) | 4.X.B | Valid `wasmBuffer`, `signatureBuffer`. `publicKeyBase64` is invalid (e.g., "bad!"). `algorithmName` = "Dilithium3". | `mockDecodeBase64` returns `null` or throws. `console.error` spy. | Call UUT. | Returns `false`. Error logged about public key decoding. | UUT returns `false` and mocked logger confirms a "PQC public key decoding failed" error message. | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_PVS_007 | PQC library verifier initialization failure returns false | Pseudo: `GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM` failure (EC6.3) | 4.X.B | Valid inputs. `algorithmName` = "Dilithium3". | `mockGetPqcVerifier` returns `null` or throws. `console.error` spy. | Call UUT. | Returns `false`. Error logged about verifier init. | UUT returns `false` and mocked logger confirms "Failed to obtain/initialize PQC verifier" error. | `CI-Commit`, `Full-Regression`, `@error_handling` |

---

### 5.2. Tests for `WasmLoaderService.loadBeancountParserWithPQCVerification()`

**UUT:** `WasmLoaderService.loadBeancountParserWithPQCVerification()`

| Test Case ID | Description | Inspired by TDD Anchor/Spec/Pseudo | Targeted AVER(s) | Preconditions/Test Data | Mocked Collaborator Behavior | Steps | Expected Observable Outcome | AI Verifiable Completion Criterion | Recursive Scope |
|---|---|---|---|---|---|---|---|---|---|
| PWMI_TC_WLS_001 | Verification enabled, valid sig: loads WASM | Pseudo: `test_loadBeancountParser_verificationEnabled_validSig_succeeds()` (FR2.6) | 4.X.B | `mockConfigService` returns `{ pqcWasmVerificationEnabled: true, wasmModulePath: "valid.wasm", wasmSignaturePathSuffix: ".sig", pqcWasmPublicKeyDilithium3Base64: "validKey" }`. | `mockFetch` for "valid.wasm" & "valid.wasm.sig" return valid `ArrayBuffer`s. `PqcVerificationService.verifyPqcWasmSignature` (mocked or real if testing integration) returns `true`. `mockWasmApiInstantiate` returns a mock WASM instance. `console.info` spy. | Call UUT. | Returns mock WASM instance. `mockWasmApiInstantiate` called with correct `wasmBuffer`. Success logged. | UUT returns a non-null WASM instance. `mockWasmApiInstantiate` was called with the fetched WASM buffer. `console.info` logged "VERIFIED successfully". | `CI-Commit`, `Full-Regression`, `@critical_path` |
| PWMI_TC_WLS_002 | Verification enabled, invalid sig: fails, notifies UI | Pseudo: `test_loadBeancountParser_verificationEnabled_invalidSig_fails()` (FR2.7) | 4.X.B | Same as WLS_001. | `mockFetch` returns valid buffers. `PqcVerificationService.verifyPqcWasmSignature` returns `false`. `mockNotificationService.notifyUIDegradedFunctionality` spy. `console.error` spy. | Call UUT. | Returns `null`. `mockNotificationService` called. Error logged. `mockWasmApiInstantiate` NOT called. | UUT returns `null`. `mockNotificationService.notifyUIDegradedFunctionality` was called with an appropriate message. `console.error` logged "verification FAILED". | `CI-Commit`, `Full-Regression`, `@critical_path`, `@error_handling` |
| PWMI_TC_WLS_003 | Verification disabled: loads WASM, bypasses verification | Pseudo: `test_loadBeancountParser_verificationDisabled_succeeds_bypassing_verification()` (FR2.9) | 4.X.B | `mockConfigService` returns `{ pqcWasmVerificationEnabled: false, wasmModulePath: "valid.wasm" }`. | `mockFetch` for "valid.wasm" returns valid `ArrayBuffer`. `PqcVerificationService.verifyPqcWasmSignature` NOT called. `mockWasmApiInstantiate` returns mock instance. `console.warn` spy. | Call UUT. | Returns mock WASM instance. `PqcVerificationService.verifyPqcWasmSignature` not called. Warning logged. | UUT returns a non-null WASM instance. `PqcVerificationService.verifyPqcWasmSignature` mock confirms it was not called. `console.warn` logged "verification is DISABLED". | `CI-Commit`, `Full-Regression`, `@config_related` |
| PWMI_TC_WLS_004 | WASM file fetch fail: fails, notifies UI | Pseudo: `test_loadBeancountParser_wasmFetchFail_fails()` (EC6.4) | 4.X.B | `mockConfigService` returns `{ pqcWasmVerificationEnabled: true, ... }`. | `mockFetch` for WASM path returns `{ ok: false, status: 404 }`. `mockNotificationService` spy. `console.error` spy. | Call UUT. | Returns `null`. `mockNotificationService` called. Error logged. | UUT returns `null`. `mockNotificationService.notifyUIDegradedFunctionality` was called. `console.error` logged "Failed to fetch WASM module". | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_WLS_005 | Signature file fetch fail: fails, notifies UI | Pseudo: `test_loadBeancountParser_signatureFetchFail_fails()` (EC6.1, EC6.4) | 4.X.B | `mockConfigService` returns `{ pqcWasmVerificationEnabled: true, ... }`. | `mockFetch` for WASM succeeds. `mockFetch` for signature path returns `{ ok: false, status: 404 }`. `mockNotificationService` spy. `console.error` spy. | Call UUT. | Returns `null`. `mockNotificationService` called. Error logged. | UUT returns `null`. `mockNotificationService.notifyUIDegradedFunctionality` was called. `console.error` logged "Failed to fetch PQC signature". | `CI-Commit`, `Full-Regression`, `@error_handling` |
| PWMI_TC_WLS_006 | Missing public key config: fails, notifies UI | Pseudo: `test_loadBeancountParser_missingPublicKeyConfig_fails()` (EC6.2) | 4.X.B | `mockConfigService` returns `{ pqcWasmVerificationEnabled: true, pqcWasmPublicKeyDilithium3Base64: null }`. | `mockNotificationService` spy. `console.error` spy. | Call UUT. | Returns `null`. `mockNotificationService` called. Error logged. `mockFetch` not called. | UUT returns `null`. `mockNotificationService.notifyUIDegradedFunctionality` was called. `console.error` logged "PQC WASM public key is not configured". | `CI-Commit`, `Full-Regression`, `@error_handling`, `@config_related` |
| PWMI_TC_WLS_007 | PQC lib init fail (via PVS mock): fails, notifies UI | Pseudo: `test_loadBeancountParser_pqcLibraryInitFailure_fails()` (EC6.3) | 4.X.B | Same as WLS_001. | `mockFetch` returns valid buffers. `PqcVerificationService.verifyPqcWasmSignature` (mocked) throws an error simulating PQC lib init failure or returns false due to it. `mockNotificationService` spy. `console.error` spy. | Call UUT. | Returns `null`. `mockNotificationService` called. Error logged (from PVS or WLS). | UUT returns `null`. `mockNotificationService.notifyUIDegradedFunctionality` was called. `console.error` logged an error related to PQC verification failure. | `CI-Commit`, `Full-Regression`, `@error_handling` |

---

### 5.3. Tests for Helper/Utility Functions (Conceptual)

If helper functions like `GET_PQC_WASM_CONFIG_VALUES()`, `DECODE_BASE64_TO_BYTE_ARRAY()`, `NOTIFY_UI_DEGRADED_FUNCTIONALITY()` have complex logic not adequately covered by the service tests, they should have their own unit tests. For this plan, we assume their core functionality is verified via the service-level tests (e.g., `mockConfigService` behavior implies `GET_PQC_WASM_CONFIG_VALUES` works; `mockNotificationService` spy verifies `NOTIFY_UI_DEGRADED_FUNCTIONALITY` is called).

**AI Verifiable Criterion for Test Case Definition:** Each test case from PWMI_TC_PVS_001 to PWMI_TC_WLS_007 is defined with all specified fields (ID, Description, Inspired by, Targeted AVER(s), UUT, Preconditions, Mocked Behavior, Steps, Expected Outcome, AI Verifiable Completion Criterion, Recursive Scope), ensuring clarity for implementation and verification.

## 6. AI Verifiable Completion Criteria for this Test Plan

1.  **Document Existence and Completeness:** This document, [`docs/test-plans/PQC_WASM_Module_Integrity_Test_Plan.md`](docs/test-plans/PQC_WASM_Module_Integrity_Test_Plan.md), exists in the specified path and includes all sections (1 through 6) as outlined.
2.  **AI Verifiable Test Cases:** Each test case defined in Section 5 includes a specific "AI Verifiable Completion Criterion" describing the precise observable outcome that signifies a pass.
3.  **AI Verifiable Strategies:** The Test Strategy (Section 3) and Recursive Testing Strategy (Section 4) include AI verifiable criteria for their definition and implementation respectively.
4.  **Alignment with Inputs:** The test plan demonstrably aligns with the inputs: [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md), [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md), [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](../../docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md), and [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md).