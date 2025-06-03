# Test Plan: PQC Hashing Feature

**Version:** 1.0
**Date:** 2025-06-03
**Feature:** PQC Hashing

## 1. Introduction

This document outlines the granular test plan for the "PQC Hashing" feature integration into Fava. The primary goal of this feature is to enhance Fava's hashing mechanisms to be resistant to threats from quantum computers by adopting algorithms like SHA3-256, while maintaining support for SHA-256.

This test plan is derived from:
*   Specification Document: [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md) (Version 1.1)
*   Pseudocode Document: [`docs/pseudocode/PQC_Hashing_Pseudo.md`](docs/pseudocode/PQC_Hashing_Pseudo.md) (Version 1.0)
*   Primary Project Planning Document: [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md) (Version 1.1)

This plan focuses on verifying the functional and non-functional requirements of the PQC Hashing feature, emphasizing interaction-based testing (London School of TDD) and a robust recursive testing strategy.

**AI Verifiable Completion for this Document:** This Test Plan document is successfully created and saved at [`docs/test-plans/PQC_Hashing_Test_Plan.md`](docs/test-plans/PQC_Hashing_Test_Plan.md).

## 2. Test Scope

This test plan aims to verify the successful implementation of the PQC Hashing feature, ensuring it meets the requirements outlined in the specification and aligns with the AI Verifiable End Results (AVERs) from the [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md).

Specifically, these tests will contribute to verifying:
*   **AVER for Project Master Plan Task 2.3 (PQC Hashing Pseudocode - Implementation Verification):** That the implemented logic aligns with the pseudocode for selecting and applying hash functions (SHA3-256 default, SHA-256 fallback), configuration handling, and error management.
*   **AVERs for Project Master Plan Phase 4.X.B (Feature Implementation & Iteration for PQC Hashing):** All granular tests defined in this plan for the PQC Hashing feature pass.
*   **AVERs for Project Master Plan Phase 4.X.C (Module-Level Review & Refinement for PQC Hashing):** Granular tests continue to pass after reviews, and performance tests align with NFRs.
*   **AVERs for Project Master Plan Phase 5.1 (System Integration & Full Acceptance Testing):** Contribution to overall system stability and correctness, particularly regarding consistent hashing between frontend and backend, and performance NFRs.
*   **Functional Requirements (FR) from [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md):** FR2.1 - FR2.7.
*   **Non-Functional Requirements (NFR) from [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md):** NFR3.1 (Correctness), NFR3.2 (Performance), NFR3.3 (Usability - Config), NFR3.4 (Reliability), NFR3.5 (Maintainability), NFR3.6 (Agility), NFR3.7 (Bundle Size).

**AI Verifiable Completion for this Section:** The test scope is clearly defined, listing the targeted AVERs and requirements.

## 3. Test Strategy

### 3.1. London School of TDD Principles

The testing approach will strictly adhere to the London School of TDD:
*   **Behavior-Driven:** Tests will focus on the observable behavior of units (modules/classes/functions) rather than their internal state.
*   **Interaction-Based Testing:** Units will be tested in isolation. Collaborators (dependencies) will be mocked or stubbed to control their behavior and verify interactions.
*   **Observable Outcomes:** Assertions will be made against the return values of methods, the state changes of objects passed to methods (if applicable and observable), or the sequence and arguments of calls made to mocked collaborators.
*   **Outside-In Development:** While this plan details granular tests, they are designed to support an outside-in TDD flow where acceptance tests drive feature development, and these granular tests verify the individual components.

**AI Verifiable Completion for this Subsection:** The London School of TDD principles and their application to this test plan are explicitly described.

### 3.2. Recursive Testing (Regression Strategy)

A comprehensive recursive testing strategy will be employed to ensure ongoing stability and catch regressions early.

*   **Triggers for Re-running Test Suites (or subsets):**
    1.  **Code Changes:** Any modification within the PQC Hashing modules (backend `fava.crypto_service`, frontend `frontend/src/lib/crypto.ts`) or their direct, critical collaborators.
    2.  **Configuration Changes:** Modifications to Fava's options affecting `pqc_hashing_algorithm`.
    3.  **Dependency Updates:** Updates to underlying cryptographic libraries (e.g., Python's `hashlib`, `pysha3`, frontend's SHA3 library, Web Crypto API changes).
    4.  **Build Process:** As part of Continuous Integration (CI) builds on every commit/push to relevant branches.
    5.  **Pre-Merge:** Before merging feature branches related to hashing or core Fava systems into the main development branch.
    6.  **Release Candidate Builds:** Full regression suite execution before tagging a release.
    7.  **Nightly Builds:** Full regression suite execution.

*   **Test Prioritization and Tagging:** Tests will be tagged to allow for selective execution:
    *   `@pqc_hash_critical_path`: Core functionality, default configurations (SHA3-256).
    *   `@pqc_hash_config`: Tests dependent on specific algorithm configurations (SHA-256).
    *   `@pqc_hash_backend`: Backend `HashingService` specific tests.
    *   `@pqc_hash_frontend`: Frontend `calculateHash` specific tests.
    *   `@pqc_hash_api`: Configuration API endpoint tests.
    *   `@pqc_hash_edge_case`: Error handling, empty inputs, invalid configurations.
    *   `@pqc_hash_performance`: Performance-related test stubs (actual execution may involve specialized tools).
    *   `@pqc_hash_consistency`: Tests verifying hash consistency between frontend and backend.

*   **Selecting Test Subsets for Regression:**
    1.  **Local Development (on file save/pre-commit hook):** Run tests tagged `@pqc_hash_critical_path` and any tests directly related to the changed files/modules.
    2.  **CI on Pull Requests:** Run all tests tagged with `@pqc_hash_critical_path`, `@pqc_hash_config`, `@pqc_hash_backend`, `@pqc_hash_frontend`, `@pqc_hash_api`, `@pqc_hash_edge_case`, `@pqc_hash_consistency`.
    3.  **Nightly/Release Builds:** Run all PQC Hashing tests, including `@pqc_hash_performance` if integrated into automated suite.

**AI Verifiable Completion for this Subsection:** The recursive testing strategy, including triggers, tagging schema, and test subset selection rules, is comprehensively defined.

## 4. Test Environment and Setup

### 4.1. Backend (`fava.crypto_service`)
*   **Environment:** Python (version compatible with Fava and `hashlib` SHA3 support, e.g., >=3.6).
*   **Libraries:** `hashlib`. `pysha3` (if testing fallback scenarios).
*   **Framework:** `unittest` (or `pytest`). Mocking library: `unittest.mock`.
*   **Setup:**
    *   Ability to instantiate `HashingService` with specific algorithm configurations.
    *   Ability to mock `FavaConfigurationProvider` to simulate different Fava options.
    *   Mock implementations for `NATIVE_CRYPTO_LIBRARY` (e.g., `hashlib`) and `FALLBACK_SHA3_LIBRARY` (e.g., `pysha3`) to simulate availability/unavailability and errors.
    *   Mock logger instance.

### 4.2. Frontend (`frontend/src/lib/crypto.ts`)
*   **Environment:** Node.js-based test runner (e.g., Vitest, Jest) or browser environment.
*   **Libraries:** JavaScript SHA3 library (e.g., `js-sha3`).
*   **Framework:** Testing framework compatible with the chosen runner.
*   **Setup:**
    *   Mock for the `SHA3_JS_LIBRARY` to control its behavior and simulate errors.
    *   Mock for `window.crypto.subtle.digest` for SHA-256 testing.
    *   Mock for `TextEncoder`.
    *   Mock for API calls that fetch the `hashing_algorithm` configuration from the backend.
    *   Mock logger instance (e.g., `console.warn`, `console.error`).

**AI Verifiable Completion for this Section:** The test environment and setup requirements for both backend and frontend components are clearly detailed.

## 5. Test Cases

Each test case will follow a standard structure. The "AI Verifiable Completion for Test Case" is that its definition is complete with all sub-fields and is ready for implementation by a testing agent.

---
**Test Case ID Format:** `PQC_HASH_TC_<Domain>_<SeqNum>`
(Domain: BHS=BackendHashingService, BGHS=BackendGetHashingService, FCH=FrontendCalculateHash, CAPI=ConfigAPI, CFE=ConfigFrontend, E2E=EndToEndConsistency, PERF=Performance)
---

### 5.1. Backend `HashingService` Tests (`fava.crypto_service`)

**PQC_HASH_TC_BHS_001**
*   **Description:** Verify `HashingService.constructor` initializes with SHA3-256 by default when no algorithm is provided.
*   **Target AVER(s):** Task 2.3 (Implementation of default config), FR2.2.
*   **Inspired by TDD Anchor(s):** Spec 10.1 (Implicit), Pseudo `HashingService.constructor_initializes_with_sha3_256_by_default()`.
*   **UUT:** `HashingService.__init__`
*   **Collaborators to Mock:** Logger (e.g., `fava.crypto_service.logger.info`).
*   **Input Data:** `configured_algorithm_name = None` or `""`.
*   **Steps:**
    1. Instantiate `HashingService()` without arguments or with an empty/null algorithm name.
    2. Check the internal algorithm used by the service.
*   **Expected Observable Outcome:** `hashing_service.get_configured_algorithm_name()` returns "SHA3-256". Logger's `info` method called with message about defaulting.
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_002**
*   **Description:** Verify `HashingService.constructor` initializes correctly with "SHA3-256" (case-insensitive).
*   **Target AVER(s):** Task 2.3 (Config handling), FR2.2.
*   **Inspired by TDD Anchor(s):** Pseudo `HashingService.constructor_initializes_with_provided_sha3_256_correctly()`.
*   **UUT:** `HashingService.__init__`
*   **Input Data:** `configured_algorithm_name = "sHa3-256"`.
*   **Steps:** Instantiate `HashingService("sHa3-256")`.
*   **Expected Observable Outcome:** `hashing_service.get_configured_algorithm_name()` returns "SHA3-256".
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_003**
*   **Description:** Verify `HashingService.constructor` initializes correctly with "SHA256" (case-insensitive, handles "SHA-256").
*   **Target AVER(s):** Task 2.3 (Config handling), FR2.3.
*   **Inspired by TDD Anchor(s):** Pseudo `HashingService.constructor_initializes_with_provided_sha256_correctly()`.
*   **UUT:** `HashingService.__init__`
*   **Input Data:** `configured_algorithm_name = "sha256"` (or `configured_algorithm_name = "SHA-256"`).
*   **Steps:** Instantiate `HashingService("sha256")`.
*   **Expected Observable Outcome:** `hashing_service.get_configured_algorithm_name()` returns "SHA256".
*   **Recursive Testing Scope Tags:** `@pqc_hash_config`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_004**
*   **Description:** Verify `HashingService.constructor` defaults to SHA3-256 and logs a warning for an unsupported algorithm.
*   **Target AVER(s):** Task 2.3 (Error handling), EC6.1, EC6.5.
*   **Inspired by TDD Anchor(s):** Spec `test_hashing_service_defaults_to_sha3_on_invalid_algo()`, Pseudo `HashingService.constructor_defaults_to_sha3_256_and_logs_warning_for_unsupported_algorithm()`.
*   **UUT:** `HashingService.__init__`
*   **Collaborators to Mock:** Logger (e.g., `fava.crypto_service.logger.warn`).
*   **Input Data:** `configured_algorithm_name = "MD5_INVALID"`.
*   **Steps:** Instantiate `HashingService("MD5_INVALID")`.
*   **Expected Observable Outcome:** `hashing_service.get_configured_algorithm_name()` returns "SHA3-256". Logger's `warn` method called with a message about the invalid algorithm and defaulting.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_005**
*   **Description:** Verify `HashingService.hash_data` with SHA3-256 produces the correct hex digest for known data.
*   **Target AVER(s):** Task 2.3 (Correct hashing), FR2.7, NFR3.1, NFR3.4.
*   **Inspired by TDD Anchor(s):** Spec `test_hashing_service_sha3_256_correct_hash()`, Pseudo `HashingService.hash_data_sha3_256_produces_correct_hex_digest()`.
*   **UUT:** `HashingService.hash_data`
*   **Collaborators to Mock:** `NATIVE_CRYPTO_LIBRARY.sha3_256` (if direct mocking is preferred over using actual `hashlib`).
*   **Input Data:** `service = HashingService("SHA3-256")`, `known_data_bytes`, `known_sha3_256_hex_digest`.
*   **Steps:** Call `service.hash_data(known_data_bytes)`.
*   **Expected Observable Outcome:** Returned value equals `known_sha3_256_hex_digest`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_006**
*   **Description:** Verify `HashingService.hash_data` with SHA256 produces the correct hex digest for known data.
*   **Target AVER(s):** Task 2.3 (Correct hashing), FR2.7, NFR3.4.
*   **Inspired by TDD Anchor(s):** Spec `test_hashing_service_sha256_correct_hash()`, Pseudo `HashingService.hash_data_sha256_produces_correct_hex_digest()`.
*   **UUT:** `HashingService.hash_data`
*   **Input Data:** `service = HashingService("SHA256")`, `known_data_bytes`, `known_sha256_hex_digest`.
*   **Steps:** Call `service.hash_data(known_data_bytes)`.
*   **Expected Observable Outcome:** Returned value equals `known_sha256_hex_digest`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_config`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_007**
*   **Description:** Verify `HashingService.hash_data` handles empty input correctly for SHA3-256.
*   **Target AVER(s):** Task 2.3 (Edge case), EC6.2.
*   **Inspired by TDD Anchor(s):** Pseudo `HashingService.hash_data_handles_empty_input_correctly_for_sha3_256()`.
*   **UUT:** `HashingService.hash_data`
*   **Input Data:** `service = HashingService("SHA3-256")`, `empty_byte_array`, `known_sha3_256_hex_digest_of_empty`.
*   **Steps:** Call `service.hash_data(empty_byte_array)`.
*   **Expected Observable Outcome:** Returned value equals `known_sha3_256_hex_digest_of_empty`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_008**
*   **Description:** Verify `HashingService.hash_data` (SHA3-256) uses fallback if primary is unavailable and logs info (assuming fallback is implemented).
*   **Target AVER(s):** Task 2.3 (Fallback logic), C7.1.
*   **Inspired by TDD Anchor(s):** Pseudo `HashingService.hash_data_sha3_256_uses_fallback_if_primary_unavailable_and_logs_info()`.
*   **UUT:** `HashingService.hash_data`
*   **Collaborators to Mock:**
    *   `NATIVE_CRYPTO_LIBRARY.sha3_256`: Mock to raise `AttributeError` or a custom "NotAvailableError".
    *   `FALLBACK_SHA3_LIBRARY.sha3_256`: Mock to return a known hash digest.
    *   Logger: Mock `logger.info`.
*   **Input Data:** `service = HashingService("SHA3-256")`, `known_data_bytes`, `known_sha3_256_hex_digest`.
*   **Steps:** Call `service.hash_data(known_data_bytes)`.
*   **Expected Observable Outcome:** Returned value equals `known_sha3_256_hex_digest`. Logger's `info` method called indicating fallback usage.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_009**
*   **Description:** Verify `HashingService.hash_data` (SHA3-256) raises `HashingAlgorithmUnavailableError` if no implementation (native or fallback) is available.
*   **Target AVER(s):** Task 2.3 (Error handling), EC6.1.
*   **Inspired by TDD Anchor(s):** Pseudo `HashingService.hash_data_raises_error_if_sha3_256_unavailable_and_no_fallback()`.
*   **UUT:** `HashingService.hash_data`
*   **Collaborators to Mock:**
    *   `NATIVE_CRYPTO_LIBRARY.sha3_256`: Mock to raise `AttributeError` or "NotAvailableError".
    *   `FALLBACK_SHA3_LIBRARY_IS_AVAILABLE`: Mock to return `False` (or `FALLBACK_SHA3_LIBRARY.sha3_256` to also raise an error).
    *   Logger: Mock `logger.error`.
*   **Input Data:** `service = HashingService("SHA3-256")`, `known_data_bytes`.
*   **Steps:** Attempt to call `service.hash_data(known_data_bytes)`.
*   **Expected Observable Outcome:** `HashingAlgorithmUnavailableError` is raised. Logger's `error` method called.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_BHS_010**
*   **Description:** `HashingService.get_configured_algorithm_name` returns the correct algorithm name.
*   **Target AVER(s):** Task 2.3 (Helper function).
*   **UUT:** `HashingService.get_configured_algorithm_name`
*   **Input Data:** `service = HashingService("SHA256")`.
*   **Steps:** Call `service.get_configured_algorithm_name()`.
*   **Expected Observable Outcome:** Returns "SHA256".
*   **Recursive Testing Scope Tags:** `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

### 5.2. Backend `get_hashing_service` Factory Function Tests

**PQC_HASH_TC_BGHS_001**
*   **Description:** Verify `get_hashing_service` creates a `HashingService` instance configured with the algorithm from `FavaConfigurationProvider`.
*   **Target AVER(s):** Task 2.3 (Factory logic), FR2.1.
*   **Inspired by TDD Anchor(s):** Pseudo `get_hashing_service_creates_service_with_algorithm_from_config()`.
*   **UUT:** `get_hashing_service`
*   **Collaborators to Mock:**
    *   `FavaConfigurationProvider.get_string_option`: Mock to return "SHA256".
*   **Input Data:** Mocked `fava_config_provider`.
*   **Steps:** Call `get_hashing_service(mock_fava_config_provider)`.
*   **Expected Observable Outcome:** Returned `HashingService` instance has its internal algorithm set to "SHA256". `FavaConfigurationProvider.get_string_option` called with "pqc_hashing_algorithm" and default.
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

### 5.3. Frontend `calculateHash` Tests (`frontend/src/lib/crypto.ts`)

**PQC_HASH_TC_FCH_001**
*   **Description:** Verify `calculateHash` with "SHA3-256" produces the correct hex digest for a known string using the JS SHA3 library.
*   **Target AVER(s):** Task 2.3 (Frontend hashing), FR2.5, FR2.7, NFR3.1, NFR3.4.
*   **Inspired by TDD Anchor(s):** Spec `test_calculate_hash_frontend_sha3_256_correct()`, Pseudo `calculateHash_sha3_256_produces_correct_hex_digest_for_known_string()`.
*   **UUT:** `calculateHash`
*   **Collaborators to Mock:**
    *   `SHA3_JS_LIBRARY.calculate_digest_as_hex` (or equivalent method): Mock to return `known_sha3_256_hex_digest_of_utf8_encoded_string`.
    *   `SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING`: Mock to return `True`.
    *   `TextEncoder.encode`: Can spy to ensure it's used.
*   **Input Data:** `known_input_string`, `algorithm_name_from_config = "SHA3-256"`.
*   **Steps:** `await calculateHash(known_input_string, "SHA3-256")`.
*   **Expected Observable Outcome:** Returns `known_sha3_256_hex_digest_of_utf8_encoded_string`. `SHA3_JS_LIBRARY.calculate_digest_as_hex` called with UTF-8 encoded `known_input_string`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_FCH_002**
*   **Description:** Verify `calculateHash` with "SHA-256" (or "SHA256" from config) produces correct hex digest using `window.crypto.subtle`.
*   **Target AVER(s):** Task 2.3 (Frontend hashing), FR2.5, FR2.7, NFR3.4.
*   **Inspired by TDD Anchor(s):** Spec `test_calculate_hash_frontend_sha256_correct()`, Pseudo `calculateHash_sha256_produces_correct_hex_digest_for_known_string_using_webcrypto()`.
*   **UUT:** `calculateHash`
*   **Collaborators to Mock:**
    *   `window.crypto.subtle.digest`: Mock to return an ArrayBuffer corresponding to `known_sha256_hex_digest_of_utf8_encoded_string`.
*   **Input Data:** `known_input_string`, `algorithm_name_from_config = "SHA-256"` (or "SHA256").
*   **Steps:** `await calculateHash(known_input_string, "SHA-256")`.
*   **Expected Observable Outcome:** Returns `known_sha256_hex_digest_of_utf8_encoded_string`. `window.crypto.subtle.digest` called with "SHA-256" and UTF-8 encoded `known_input_string`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_config`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_FCH_003**
*   **Description:** Verify `calculateHash` defaults to SHA-256 and logs a warning if an unsupported algorithm is provided AND the SHA3 library is unavailable.
*   **Target AVER(s):** Task 2.3 (Frontend error handling), EC6.1, EC6.3.
*   **Inspired by TDD Anchor(s):** Pseudo `calculateHash_defaults_to_sha256_and_logs_warning_if_unsupported_algorithm_and_sha3_unavailable()`.
*   **UUT:** `calculateHash`
*   **Collaborators to Mock:**
    *   `SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING`: Mock to return `False`.
    *   Logger (e.g., `console.warn`): Mock to verify warning.
    *   `window.crypto.subtle.digest`: Mock to return a known SHA-256 hash.
*   **Input Data:** `input_string`, `algorithm_name_from_config = "INVALID_ALGO_XYZ"`.
*   **Steps:** `await calculateHash(input_string, "INVALID_ALGO_XYZ")`.
*   **Expected Observable Outcome:** Returns the SHA-256 hash of `input_string`. Logger's `warn` method called about invalid algo and SHA3 unavailability.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_FCH_004**
*   **Description:** Verify `calculateHash` throws `FrontendHashingError` if the SHA3 JS library fails when "SHA3-256" is requested.
*   **Target AVER(s):** Task 2.3 (Frontend error handling), EC6.3.
*   **Inspired by TDD Anchor(s):** Pseudo `calculateHash_throws_error_if_sha3_js_library_fails_when_sha3_256_is_requested()`.
*   **UUT:** `calculateHash`
*   **Collaborators to Mock:**
    *   `SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING`: Mock to return `True`.
    *   `SHA3_JS_LIBRARY.calculate_digest_as_hex`: Mock to throw an error.
    *   Logger (e.g., `console.error`): Mock to verify error logging.
*   **Input Data:** `input_string`, `algorithm_name_from_config = "SHA3-256"`.
*   **Steps:** Attempt `await calculateHash(input_string, "SHA3-256")`.
*   **Expected Observable Outcome:** `FrontendHashingError` is thrown. Logger's `error` method called.
*   **Recursive Testing Scope Tags:** `@pqc_hash_edge_case`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_FCH_005**
*   **Description:** Verify `calculateHash` uses UTF-8 encoding for the input string.
*   **Target AVER(s):** Task 2.3 (Correct encoding), EC6.4.
*   **Inspired by TDD Anchor(s):** Pseudo `calculateHash_uses_utf8_encoding_for_input_string()`.
*   **UUT:** `calculateHash`
*   **Collaborators to Mock/Spy:**
    *   `TextEncoder.prototype.encode`: Spy to verify it's called with the input string.
    *   `window.crypto.subtle.digest` (or `SHA3_JS_LIBRARY` method): Mock to allow test to complete.
*   **Input Data:** `string_with_multibyte_chars = "你好世界"`, `algorithm_name_from_config = "SHA-256"`.
*   **Steps:** `await calculateHash(string_with_multibyte_chars, "SHA-256")`.
*   **Expected Observable Outcome:** `TextEncoder.prototype.encode` was called with `string_with_multibyte_chars`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_critical_path`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

### 5.4. Configuration Flow Tests

**PQC_HASH_TC_CAPI_001**
*   **Description:** Verify the API endpoint for crypto config returns the correct `hashing_algorithm` from Fava options (e.g., "SHA256").
*   **Target AVER(s):** Task 2.3 (API config), FR2.6, IP12.4.
*   **Inspired by TDD Anchor(s):** Pseudo `API_get_crypto_config_returns_correct_hashing_algorithm()`.
*   **UUT:** Backend API handler function for crypto configuration.
*   **Collaborators to Mock:**
    *   `FavaConfigurationProvider.get_string_option`: Mock to return "SHA256".
*   **Input Data:** HTTP request to the config API endpoint.
*   **Steps:** Simulate an API call to the endpoint.
*   **Expected Observable Outcome:** API response is successful (e.g., HTTP 200) and JSON payload contains `{"hashing_algorithm": "SHA256"}`. `FavaConfigurationProvider.get_string_option` called correctly.
*   **Recursive Testing Scope Tags:** `@pqc_hash_api`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_CFE_001**
*   **Description:** Verify frontend fetches and uses the hashing algorithm from the API when calling `calculateHash`.
*   **Target AVER(s):** Task 2.3 (Frontend config usage), FR2.6.
*   **Inspired by TDD Anchor(s):** Pseudo `Frontend_fetches_and_uses_hashing_algorithm_from_API()`.
*   **UUT:** Frontend component/service responsible for fetching config and initiating hashing (e.g., part of `SliceEditor` logic).
*   **Collaborators to Mock/Spy:**
    *   API client method (e.g., `fetch` or a dedicated service method): Mock to return `{"hashing_algorithm": "SHA3-256"}`.
    *   `PQC_Hashing_Frontend.calculateHash`: Spy to check the `algorithm_name_from_config` argument.
*   **Input Data:** `sample_content_string`.
*   **Steps:**
    1. Trigger frontend logic that fetches configuration.
    2. Trigger frontend logic that calculates a hash for `sample_content_string`.
*   **Expected Observable Outcome:** `PQC_Hashing_Frontend.calculateHash` is called with `algorithm_name_from_config` equal to "SHA3-256".
*   **Recursive Testing Scope Tags:** `@pqc_hash_api`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined.

### 5.5. End-to-End Hashing Consistency Test

**PQC_HASH_TC_E2E_001**
*   **Description:** Verify that the backend `HashingService` and frontend `calculateHash` produce identical SHA3-256 hash digests for the same string input data when Fava is configured for SHA3-256.
*   **Target AVER(s):** FR2.6, NFR3.4, EC6.4 (Mitigation).
*   **Inspired by TDD Anchor(s):** Implicit from consistency requirement.
*   **UUT:** Interaction between backend `HashingService` and frontend `calculateHash`.
*   **Input Data:** `sample_string = "Test for PQC Hashing Consistency!"`. Fava configured for "SHA3-256".
*   **Steps:**
    1.  Obtain backend hash: `backend_hash = HashingService("SHA3-256").hash_data(sample_string.encode('utf-8'))`.
    2.  Obtain frontend hash: `frontend_hash = await calculateHash(sample_string, "SHA3-256")`. (Ensure frontend mock for SHA3 lib uses a real, consistent implementation for this test).
*   **Expected Observable Outcome:** `backend_hash` equals `frontend_hash`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_consistency`, `@pqc_hash_critical_path`
*   **AI Verifiable Completion for Test Case:** Defined.

**PQC_HASH_TC_E2E_002**
*   **Description:** Verify that the backend `HashingService` and frontend `calculateHash` produce identical SHA256 hash digests for the same string input data when Fava is configured for SHA256.
*   **Target AVER(s):** FR2.6, NFR3.4, EC6.4 (Mitigation).
*   **UUT:** Interaction between backend `HashingService` and frontend `calculateHash`.
*   **Input Data:** `sample_string = "Test for PQC Hashing Consistency!"`. Fava configured for "SHA256".
*   **Steps:**
    1.  Obtain backend hash: `backend_hash = HashingService("SHA256").hash_data(sample_string.encode('utf-8'))`.
    2.  Obtain frontend hash: `frontend_hash = await calculateHash(sample_string, "SHA256")`.
*   **Expected Observable Outcome:** `backend_hash` equals `frontend_hash`.
*   **Recursive Testing Scope Tags:** `@pqc_hash_consistency`, `@pqc_hash_config`
*   **AI Verifiable Completion for Test Case:** Defined.

### 5.6. Performance Test Stubs

**PQC_HASH_TC_PERF_001**
*   **Description:** Stub for verifying backend SHA3-256 hashing of a 1MB file meets NFR3.2 (target: 50-100ms).
*   **Target AVER(s):** NFR3.2 (Backend).
*   **UUT:** `HashingService.hash_data` with SHA3-256.
*   **Recursive Testing Scope Tags:** `@pqc_hash_performance`, `@pqc_hash_backend`
*   **AI Verifiable Completion for Test Case:** Defined as a stub, actual measurement via performance tools.

**PQC_HASH_TC_PERF_002**
*   **Description:** Stub for verifying frontend SHA3-256 hashing of a 50KB slice meets NFR3.2 (target: 20-50ms).
*   **Target AVER(s):** NFR3.2 (Frontend).
*   **UUT:** `calculateHash` with SHA3-256.
*   **Recursive Testing Scope Tags:** `@pqc_hash_performance`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined as a stub, actual measurement via browser performance tools.

**PQC_HASH_TC_PERF_003**
*   **Description:** Stub for verifying frontend SHA3 library bundle size impact meets NFR3.7 (target: < 50KB gzipped).
*   **Target AVER(s):** NFR3.7.
*   **UUT:** Frontend build artifact.
*   **Recursive Testing Scope Tags:** `@pqc_hash_performance`, `@pqc_hash_frontend`
*   **AI Verifiable Completion for Test Case:** Defined as a stub, verification via build analysis.

## 6. Test Data Requirements

*   **Strings:**
    *   Empty string: `""`
    *   Short ASCII string: `"test"`
    *   Longer ASCII string: `"This is a longer test string for hashing."`
    *   String with multi-byte UTF-8 characters: `"你好世界 PQC"`
*   **Known Hashes:** Pre-calculated SHA3-256 and SHA-256 hex digests for all above strings (UTF-8 encoded).
    *   Example (Illustrative - actual values needed):
        *   SHA3-256("") = `a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a`
*   **Files (for performance):**
    *   1MB text file.
*   **Editor Content (for performance):**
    *   50KB Beancount slice text.

**AI Verifiable Completion for this Section:** The types of test data required are listed, with examples.

## 7. Traceability

| Test Case ID        | Requirement(s) (Spec)                                  | AVER(s) (Master Plan)                                                                                                | TDD Anchor(s) (Spec/Pseudo)                                                                                                                                                                                                                                                                                       |
|---------------------|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PQC_HASH_TC_BHS_001 | FR2.2                                                  | Task 2.3 (Default config)                                                                                            | Pseudo: `HashingService.constructor_initializes_with_sha3_256_by_default()`                                                                                                                                                                                                                                                       |
| PQC_HASH_TC_BHS_002 | FR2.2                                                  | Task 2.3 (Config handling)                                                                                           | Pseudo: `HashingService.constructor_initializes_with_provided_sha3_256_correctly()`                                                                                                                                                                                                                                               |
| PQC_HASH_TC_BHS_003 | FR2.3                                                  | Task 2.3 (Config handling)                                                                                           | Pseudo: `HashingService.constructor_initializes_with_provided_sha256_correctly()`                                                                                                                                                                                                                                                 |
| PQC_HASH_TC_BHS_004 | EC6.1, EC6.5                                           | Task 2.3 (Error handling)                                                                                            | Spec: `test_hashing_service_defaults_to_sha3_on_invalid_algo()`, Pseudo: `HashingService.constructor_defaults_to_sha3_256_and_logs_warning_for_unsupported_algorithm()`                                                                                                                                                             |
| PQC_HASH_TC_BHS_005 | FR2.7, NFR3.1, NFR3.4                                  | Task 2.3 (Correct hashing)                                                                                           | Spec: `test_hashing_service_sha3_256_correct_hash()`, Pseudo: `HashingService.hash_data_sha3_256_produces_correct_hex_digest()`                                                                                                                                                                                                        |
| PQC_HASH_TC_BHS_006 | FR2.7, NFR3.4                                          | Task 2.3 (Correct hashing)                                                                                           | Spec: `test_hashing_service_sha256_correct_hash()`, Pseudo: `HashingService.hash_data_sha256_produces_correct_hex_digest()`                                                                                                                                                                                                          |
| PQC_HASH_TC_BHS_007 | EC6.2                                                  | Task 2.3 (Edge case)                                                                                                 | Pseudo: `HashingService.hash_data_handles_empty_input_correctly_for_sha3_256()`                                                                                                                                                                                                                                                   |
| PQC_HASH_TC_BHS_008 | C7.1                                                   | Task 2.3 (Fallback logic)                                                                                            | Pseudo: `HashingService.hash_data_sha3_256_uses_fallback_if_primary_unavailable_and_logs_info()`                                                                                                                                                                                                                                  |
| PQC_HASH_TC_BHS_009 | EC6.1                                                  | Task 2.3 (Error handling)                                                                                            | Pseudo: `HashingService.hash_data_raises_error_if_sha3_256_unavailable_and_no_fallback()`                                                                                                                                                                                                                                         |
| PQC_HASH_TC_BHS_010 | N/A                                                    | Task 2.3 (Helper function)                                                                                           | N/A                                                                                                                                                                                                                                                                                                                               |
| PQC_HASH_TC_BGHS_001| FR2.1                                                  | Task 2.3 (Factory logic)                                                                                             | Pseudo: `get_hashing_service_creates_service_with_algorithm_from_config()`                                                                                                                                                                                                                                                      |
| PQC_HASH_TC_FCH_001 | FR2.5, FR2.7, NFR3.1, NFR3.4                           | Task 2.3 (Frontend hashing)                                                                                          | Spec: `test_calculate_hash_frontend_sha3_256_correct()`, Pseudo: `calculateHash_sha3_256_produces_correct_hex_digest_for_known_string()`                                                                                                                                                                                             |
| PQC_HASH_TC_FCH_002 | FR2.5, FR2.7, NFR3.4                                   | Task 2.3 (Frontend hashing)                                                                                          | Spec: `test_calculate_hash_frontend_sha256_correct()`, Pseudo: `calculateHash_sha256_produces_correct_hex_digest_for_known_string_using_webcrypto()`                                                                                                                                                                                |
| PQC_HASH_TC_FCH_003 | EC6.1, EC6.3                                           | Task 2.3 (Frontend error handling)                                                                                   | Pseudo: `calculateHash_defaults_to_sha256_and_logs_warning_if_unsupported_algorithm_and_sha3_unavailable()`                                                                                                                                                                                                                       |
| PQC_HASH_TC_FCH_004 | EC6.3                                                  | Task 2.3 (Frontend error handling)                                                                                   | Pseudo: `calculateHash_throws_error_if_sha3_js_library_fails_when_sha3_256_is_requested()`                                                                                                                                                                                                                                      |
| PQC_HASH_TC_FCH_005 | EC6.4                                                  | Task 2.3 (Correct encoding)                                                                                          | Pseudo: `calculateHash_uses_utf8_encoding_for_input_string()`                                                                                                                                                                                                                                                                     |
| PQC_HASH_TC_CAPI_001| FR2.6, IP12.4                                          | Task 2.3 (API config)                                                                                                | Pseudo: `API_get_crypto_config_returns_correct_hashing_algorithm()`                                                                                                                                                                                                                                                           |
| PQC_HASH_TC_CFE_001 | FR2.6                                                  | Task 2.3 (Frontend config usage)                                                                                     | Pseudo: `Frontend_fetches_and_uses_hashing_algorithm_from_API()`                                                                                                                                                                                                                                                              |
| PQC_HASH_TC_E2E_001 | FR2.6, NFR3.4, EC6.4 (Mitigation)                        | Phase 5.1 (System Integration)                                                                                       | N/A                                                                                                                                                                                                                                                                                                                               |
| PQC_HASH_TC_E2E_002 | FR2.6, NFR3.4, EC6.4 (Mitigation)                        | Phase 5.1 (System Integration)                                                                                       | N/A                                                                                                                                                                                                                                                                                                                               |
| PQC_HASH_TC_PERF_001| NFR3.2 (Backend)                                       | Phase 4.X.C, Phase 5.1 (Performance NFRs)                                                                            | N/A                                                                                                                                                                                                                                                                                                                               |
| PQC_HASH_TC_PERF_002| NFR3.2 (Frontend)                                      | Phase 4.X.C, Phase 5.1 (Performance NFRs)                                                                            | N/A                                                                                                                                                                                                                                                                                                                               |
| PQC_HASH_TC_PERF_003| NFR3.7                                                 | Phase 4.X.C (Bundle Size NFR)                                                                                        | N/A                                                                                                                                                                                                                                                                                                                               |

**AI Verifiable Completion for this Section:** The traceability matrix is present and maps test cases to requirements, AVERs, and TDD anchors.

## 8. Document Approval and Revision History

*   **Approved By:** (To be filled upon review)
*   **Date Approved:** (To be filled upon review)

| Version | Date       | Author      | Changes                                     |
|---------|------------|-------------|---------------------------------------------|
| 1.0     | 2025-06-03 | AI Agent    | Initial draft of the PQC Hashing Test Plan. |

**AI Verifiable Completion for this Section:** The approval and revision history section is present.