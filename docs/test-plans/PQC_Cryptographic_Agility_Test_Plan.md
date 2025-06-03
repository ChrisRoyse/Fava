# Test Plan: PQC Cryptographic Agility

**Version:** 1.0
**Date:** 2025-06-03
**Feature:** PQC Cryptographic Agility
**Author:** AI Agent (Spec-To-TestPlan Converter)

## 1. Introduction

This document outlines the granular test plan for the **PQC Cryptographic Agility** feature of the Fava application. Cryptographic agility is a critical component of the Post-Quantum Cryptography (PQC) integration, enabling Fava to adapt to evolving cryptographic standards and algorithm choices primarily through configuration, with minimal code changes.

This test plan is derived from:
*   Specification Document: [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](../specifications/PQC_Cryptographic_Agility_Spec.md) (v1.1)
*   Pseudocode Document: [`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](../pseudocode/PQC_Cryptographic_Agility_Pseudo.md) (v1.1)
*   Architecture Document: [`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](../architecture/PQC_Cryptographic_Agility_Arch.md) (v1.0)
*   Primary Project Planning Document: [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md) (v1.1)

The purpose of this test plan is to define a comprehensive testing strategy to verify the correct implementation of cryptographic agility mechanisms, ensuring they are robust, secure, and meet the specified requirements. It emphasizes London School TDD principles and includes a recursive testing strategy for ongoing stability.

**AI Verifiable Completion Criterion for this Document:** This test plan document is successfully created and saved at [`docs/test-plans/PQC_Cryptographic_Agility_Test_Plan.md`](./PQC_Cryptographic_Agility_Test_Plan.md), and its content aligns with the requirements outlined in the initial prompt.

## 2. Test Scope

The scope of this test plan covers the granular testing of all components and functionalities related to cryptographic agility as defined in the aforementioned documents. The primary goal is to ensure that the implemented features correctly support the AI Verifiable End Results (AVERs) outlined in the [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md) for the PQC Cryptographic Agility feature, ultimately contributing to the success of the high-level acceptance tests:

*   **PQC_AGL_001:** Administrator can switch default backend hashing algorithm.
*   **PQC_AGL_002:** Administrator can switch active PQC KEM suite for new data-at-rest encryption and Fava can still decrypt data encrypted with a configured legacy PQC KEM suite.
*   **PQC_AGL_003:** Frontend hashing operations use the default algorithm specified in Fava's backend configuration.
*   **PQC_AGL_004:** Fava handles attempts to use unknown/unsupported cryptographic suites gracefully.

This test plan focuses on verifying:
*   **Configuration Management:** Loading, validation, and application of `FAVA_CRYPTO_SETTINGS`.
*   **Backend CryptoService:** Correct registration, retrieval, and operation of `CryptoHandler` instances for various suites (hybrid, classical), including encryption, decryption, and hashing.
*   **Frontend CryptoFacade:** Correct fetching of configuration from the backend API and application of configured algorithms for hashing and WASM signature verification.
*   **Algorithm Switching:** Seamless switching of algorithms for new operations based on configuration changes without requiring code modifications in consuming modules.
*   **Legacy Decryption:** Support for decrypting data encrypted with older, configured cryptographic suites.
*   **Error Handling:** Graceful and secure handling of misconfigurations, unavailable algorithms, or tampered data.

**Out of Scope:**
*   Performance testing (though interactions might highlight areas for later performance scrutiny).
*   Usability testing of the admin configuration interface.
*   The actual cryptographic strength of the algorithms (assumed to be sound as per library providers).
*   Testing of the underlying cryptographic libraries themselves (e.g., `oqs-python`, `liboqs-js`, `cryptography`), beyond their correct invocation by Fava's services.

**AI Verifiable Completion Criterion for this Section:** This Test Scope section is documented within the test plan, clearly defining what is and is not covered by these granular tests, and links to relevant AVERs and acceptance tests.

## 3. Test Strategy

### 3.1. London School of TDD Principles

This test plan adheres to the London School of Test-Driven Development (TDD), emphasizing interaction-based testing:

*   **Focus on Behavior, Not State:** Tests will verify the behavior of a unit (module/class/function) by observing its interactions with its collaborators. Internal state verification will be minimized.
*   **Mocking Collaborators:** External dependencies and collaborators of the Unit Under Test (UUT) will be mocked or stubbed. This allows for isolated testing of the UUT's logic and ensures tests are fast and reliable.
    *   Examples of collaborators to mock:
        *   File system access for configuration loading.
        *   Underlying cryptographic libraries (e.g., `oqs.KeyEncapsulation`, `cryptography.hazmat.primitives.ciphers.AESGCM`).
        *   Backend API endpoints (for frontend tests).
        *   `FavaOptions` or configuration access objects.
*   **Verifying Observable Outcomes:** Tests will assert that the UUT produces the correct observable outcomes, such as:
    *   Returning expected values.
    *   Calling methods on mocked collaborators with the correct arguments and in the expected sequence.
    *   Raising appropriate exceptions under error conditions.

### 3.2. Recursive Testing Strategy (Regression Testing)

A comprehensive recursive (frequent regression) testing strategy is crucial for maintaining stability as the PQC features are developed and integrated.

*   **Triggers for Re-execution:**
    *   **Code Changes:** Any modification to the UUT or its direct, non-mocked collaborators.
    *   **Configuration Schema Changes:** Any change to the structure or expected values within `FAVA_CRYPTO_SETTINGS`.
    *   **Crypto Library Updates:** Updates to `oqs-python`, `liboqs-js`, `cryptography`, or other core crypto dependencies.
    *   **Pre-Commit Hooks:** Execution of a tagged subset of fast-running, critical path tests before each commit.
    *   **Continuous Integration (CI):** Automated execution of the full granular test suite (or relevant tagged subsets) on every push to a development branch or pull request.
    *   **Nightly Builds:** Execution of the full test suite.
    *   **Pre-Release:** Execution of the full test suite and all acceptance tests.

*   **Test Prioritization and Tagging:**
    Tests will be tagged to allow for selective execution:
    *   `@critical_path`: Core functionalities essential for basic operation (e.g., config loading, active handler retrieval).
    *   `@config_dependent`: Tests highly sensitive to `FAVA_CRYPTO_SETTINGS` structure and values.
    *   `@suite_specific_<suite_id>`: Tests for a particular cryptographic suite handler (e.g., `@suite_specific_HYBRID_X25519_MLKEM768_AES256GCM`).
    *   `@error_handling`: Tests covering fallback mechanisms, misconfigurations, and error conditions.
    *   `@backend`: Tests for backend components.
    *   `@frontend`: Tests for frontend components.
    *   `@api_driven`: Frontend tests relying on backend API responses for configuration.
    *   `@security_sensitive`: Tests related to secure failure modes or correct application of cryptographic primitives.

*   **Subset Selection for Regression:**
    *   **Local Development (on save/pre-commit):** Run `@critical_path` tests and tests related to the specific modules being modified.
    *   **Configuration Schema Change:** Run all `@config_dependent` and `@critical_path` tests.
    *   **Crypto Library Update:** Run all relevant `@suite_specific_*` tests, `@critical_path`, and `@security_sensitive` tests.
    *   **CI/Pull Request:** Run all tests tagged `@backend` and `@frontend`, or a more targeted subset based on changed files if feasible. Full suite for merges to main/release branches.
    *   **Nightly/Pre-Release:** Full test suite.

*   **Software Development Life Cycle (SDLC) Touchpoints:**
    *   **Development:** Developers are responsible for writing and running tests for new/modified code.
    *   **Code Review:** Test coverage and quality are part_of_the_code_review_process.
    *   **Continuous Integration:** Automated test execution provides rapid feedback.
    *   **Quality Assurance (QA):** QA processes may involve targeted regression testing based on risk assessment.
    *   **Release Management:** Successful completion of all relevant regression suites is a prerequisite for release.

**AI Verifiable Completion Criterion for this Section:** This Test Strategy section is documented, detailing the adoption of London School TDD and a comprehensive recursive testing strategy with triggers, tagging, subset selection, and SDLC integration points.

## 4. Test Environment & Setup

*   **Testing Frameworks:**
    *   Backend (Python): `pytest` with `pytest-mock`.
    *   Frontend (TypeScript/JavaScript): `Vitest` or `Jest` with appropriate mocking capabilities.
*   **Mocking:**
    *   All external dependencies (crypto libraries, file system, API calls) will be mocked.
    *   Mock configurations for `FAVA_CRYPTO_SETTINGS` will be created to simulate various scenarios (e.g., different active suites, decryption orders, algorithm choices).
*   **Test Data:**
    *   Sample plaintext data for encryption/decryption tests.
    *   Pre-computed (or mock-generated) ciphertext, KEM outputs, signatures for specific test cases where the focus is not on the crypto primitive itself but on the service's handling of it.
    *   Malformed or tampered data bundles to test error handling.
    *   Various `FAVA_CRYPTO_SETTINGS` configurations (valid, invalid, missing sections).
*   **Build/CI Environment:**
    *   Ensure CI environment has access to necessary Python and Node.js versions and can install test dependencies.

**AI Verifiable Completion Criterion for this Section:** This Test Environment & Setup section is documented, outlining necessary frameworks, mocking strategies, and test data requirements.

## 5. Test Cases

Each test case below includes:
*   **Test Case ID:** Unique identifier.
*   **Target Component(s):** The primary module/class/function under test.
*   **Related Requirement(s):** Links to Functional Requirements (FR), Edge Cases (EC), Constraints (C) from the Spec, or Pseudocode sections.
*   **TDD Anchor(s):** Links to relevant TDD anchors from the Pseudocode.
*   **Description:** What the test aims to verify.
*   **Test Steps (Interaction-focused):**
    1.  Setup: Initialize UUT, configure mocks.
    2.  Action: Call the method/function on UUT.
    3.  Assert: Verify interactions with mocks and observable outcomes.
*   **Mocked Collaborators & Expected Interactions:**
*   **Expected Observable Outcome:**
*   **Recursive Testing Tags:** Tags for regression suite selection.
*   **AI Verifiable Completion Criterion:** For the test case itself.

---

### 5.1. Global Configuration Management (`GlobalConfig` Module - Backend)

**Test Case ID:** `TC_AGL_GC_001`
**Target Component(s):** `GlobalConfig.LoadCryptoSettings`
**Related Requirement(s):** FR2.3, Spec 8.1, Pseudo 1 (`LoadCryptoSettings`)
**TDD Anchor(s):** `test_load_crypto_settings_loads_valid_config_from_path()`
**Description:** Verify that `LoadCryptoSettings` correctly loads and parses a valid crypto configuration file.
**Test Steps:**
    1.  Setup:
        *   Mock file system `READ_FILE_CONTENT` to return a valid `FAVA_CRYPTO_SETTINGS` string (as per Spec 8.1).
        *   Mock `PARSE_PYTHON_LIKE_STRUCTURE` to correctly parse this string into a dictionary.
        *   Mock `VALIDATE_SCHEMA` to return success.
    2.  Action: Call `GlobalConfig.LoadCryptoSettings()`.
    3.  Assert:
        *   `READ_FILE_CONTENT` called once with the correct config path.
        *   `PARSE_PYTHON_LIKE_STRUCTURE` called once with the content from `READ_FILE_CONTENT`.
        *   `VALIDATE_SCHEMA` called once with the parsed config and expected schema.
**Mocked Collaborators & Expected Interactions:**
    *   `file_system.READ_FILE_CONTENT(FAVA_CRYPTO_SETTINGS_PATH)`: Called once.
    *   `parser.PARSE_PYTHON_LIKE_STRUCTURE(valid_config_string)`: Called once.
    *   `validator.VALIDATE_SCHEMA(parsed_config, expected_schema)`: Called once, returns success.
**Expected Observable Outcome:** Returns the parsed and validated configuration object. No exceptions thrown. Log message "Successfully loaded and validated crypto settings."
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_GC_001` is implemented in the test suite, passes consistently, and its successful execution is logged/reported by the test runner.

**Test Case ID:** `TC_AGL_GC_002`
**Target Component(s):** `GlobalConfig.LoadCryptoSettings`
**Related Requirement(s):** FR2.7, Pseudo 1 (`LoadCryptoSettings` - FileNotFoundError)
**TDD Anchor(s):** `test_load_crypto_settings_handles_missing_file_gracefully_returns_defaults_or_throws_critical()`
**Description:** Verify that `LoadCryptoSettings` handles a missing configuration file by throwing a critical error.
**Test Steps:**
    1.  Setup: Mock `READ_FILE_CONTENT` to raise `FileNotFoundError`.
    2.  Action: Call `GlobalConfig.LoadCryptoSettings()`.
    3.  Assert: `READ_FILE_CONTENT` was called.
**Mocked Collaborators & Expected Interactions:**
    *   `file_system.READ_FILE_CONTENT(FAVA_CRYPTO_SETTINGS_PATH)`: Called once, raises `FileNotFoundError`.
**Expected Observable Outcome:** `CriticalConfigurationError` ("Crypto settings file is missing.") is raised. Log message "Crypto settings file not found..."
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_GC_002` is implemented, passes, and its successful execution (including expected error) is logged/reported.

**Test Case ID:** `TC_AGL_GC_003`
**Target Component(s):** `GlobalConfig.LoadCryptoSettings`
**Related Requirement(s):** FR2.7, Pseudo 1 (`LoadCryptoSettings` - ParsingError)
**TDD Anchor(s):** (Implicit from `test_load_crypto_settings_handles_missing_file_gracefully_returns_defaults_or_throws_critical()`)
**Description:** Verify that `LoadCryptoSettings` handles a malformed configuration file by throwing a critical error.
**Test Steps:**
    1.  Setup:
        *   Mock `READ_FILE_CONTENT` to return a malformed config string.
        *   Mock `PARSE_PYTHON_LIKE_STRUCTURE` to raise `ParsingError`.
    2.  Action: Call `GlobalConfig.LoadCryptoSettings()`.
    3.  Assert: `PARSE_PYTHON_LIKE_STRUCTURE` was called.
**Mocked Collaborators & Expected Interactions:**
    *   `file_system.READ_FILE_CONTENT`: Called once.
    *   `parser.PARSE_PYTHON_LIKE_STRUCTURE`: Called once, raises `ParsingError`.
**Expected Observable Outcome:** `CriticalConfigurationError` ("Crypto settings file is malformed.") is raised. Log message "Failed to parse crypto settings..."
**Recursive Testing Tags:** `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_GC_003` is implemented, passes, and its successful execution (including expected error) is logged/reported.

**Test Case ID:** `TC_AGL_GC_004`
**Target Component(s):** `GlobalConfig.LoadCryptoSettings`
**Related Requirement(s):** FR2.7, Pseudo 1 (`LoadCryptoSettings` - SchemaValidationError)
**TDD Anchor(s):** `test_load_crypto_settings_validates_schema_against_spec_8_1_FAVA_CRYPTO_SETTINGS()`
**Description:** Verify that `LoadCryptoSettings` handles a configuration file that fails schema validation by throwing a critical error.
**Test Steps:**
    1.  Setup:
        *   Mock `READ_FILE_CONTENT` to return a config string that will fail schema validation.
        *   Mock `PARSE_PYTHON_LIKE_STRUCTURE` to return a parsed dictionary.
        *   Mock `VALIDATE_SCHEMA` to raise `ConfigurationError` (or return a failure indicator that causes the UUT to throw).
    2.  Action: Call `GlobalConfig.LoadCryptoSettings()`.
    3.  Assert: `VALIDATE_SCHEMA` was called.
**Mocked Collaborators & Expected Interactions:**
    *   `file_system.READ_FILE_CONTENT`: Called once.
    *   `parser.PARSE_PYTHON_LIKE_STRUCTURE`: Called once.
    *   `validator.VALIDATE_SCHEMA`: Called once, indicates failure / raises `ConfigurationError`.
**Expected Observable Outcome:** `CriticalConfigurationError` ("Crypto settings are invalid.") is raised. Log message "Invalid crypto settings..."
**Recursive Testing Tags:** `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_GC_004` is implemented, passes, and its successful execution (including expected error) is logged/reported.

**Test Case ID:** `TC_AGL_GC_005`
**Target Component(s):** `GlobalConfig.GetCryptoSettings`
**Related Requirement(s):** Pseudo 1 (`GetCryptoSettings`)
**TDD Anchor(s):** `test_get_crypto_settings_returns_cached_settings_after_first_load()`, `test_get_crypto_settings_calls_load_crypto_settings_if_cache_is_empty()`
**Description:** Verify that `GetCryptoSettings` uses cached settings after the first load and calls `LoadCryptoSettings` only if the cache is empty.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.LoadCryptoSettings` to return a specific config object.
        *   Ensure internal cache `GlobalCryptoSettingsCache` is initially NULL.
    2.  Action: Call `GlobalConfig.GetCryptoSettings()` first time.
    3.  Assert: `GlobalConfig.LoadCryptoSettings` was called once. The returned object matches the mock.
    4.  Action: Call `GlobalConfig.GetCryptoSettings()` second time.
    5.  Assert: `GlobalConfig.LoadCryptoSettings` was NOT called again. The returned object matches the mock (from cache).
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.LoadCryptoSettings`: Called only on the first call to `GetCryptoSettings`.
**Expected Observable Outcome:** Correct configuration object returned on both calls.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_GC_005` is implemented, passes, and its successful execution is logged/reported.

---

### 5.2. Backend `CryptoService` (`BackendCryptoService` Module)

#### 5.2.1. Handler Registration and Retrieval

**Test Case ID:** `TC_AGL_BCS_REG_001`
**Target Component(s):** `BackendCryptoService.RegisterCryptoHandler`, `BackendCryptoService.GetCryptoHandler`
**Related Requirement(s):** FR2.4, Pseudo 2 (`RegisterCryptoHandler`, `GetCryptoHandler`)
**TDD Anchor(s):** `test_register_crypto_handler_successfully_adds_new_handler_to_registry()`, `test_get_crypto_handler_returns_correctly_registered_handler_instance()`
**Description:** Verify successful registration of a handler instance and its retrieval.
**Test Steps:**
    1.  Setup:
        *   Create a mock `CryptoHandler` instance (`mock_handler_A`) with `get_suite_id()` returning "SUITE_A".
        *   Initialize `BackendCryptoService` (ensure `_HANDLER_REGISTRY` is empty).
    2.  Action: Call `BackendCryptoService.RegisterCryptoHandler("SUITE_A", mock_handler_A)`.
    3.  Assert: No exceptions. Log message "Crypto handler registered for suite: SUITE_A".
    4.  Action: Call `BackendCryptoService.GetCryptoHandler("SUITE_A")`.
    5.  Assert: The returned handler is `mock_handler_A`.
**Mocked Collaborators & Expected Interactions:** None (testing internal registry).
**Expected Observable Outcome:** `mock_handler_A` is returned by `GetCryptoHandler`.
**Recursive Testing Tags:** `@critical_path`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_002`
**Target Component(s):** `BackendCryptoService.RegisterCryptoHandler`
**Related Requirement(s):** Pseudo 2 (`RegisterCryptoHandler`)
**TDD Anchor(s):** `test_register_crypto_handler_throws_error_if_suite_id_is_null_or_empty()`
**Description:** Verify `RegisterCryptoHandler` throws an error for null/empty suite_id or null handler.
**Test Steps:**
    1.  Setup: Initialize `BackendCryptoService`. Create a `mock_handler`.
    2.  Action & Assert:
        *   Call `BackendCryptoService.RegisterCryptoHandler(None, mock_handler)` -> Expect `InvalidArgumentError`.
        *   Call `BackendCryptoService.RegisterCryptoHandler("", mock_handler)` -> Expect `InvalidArgumentError`.
        *   Call `BackendCryptoService.RegisterCryptoHandler("SUITE_X", None)` -> Expect `InvalidArgumentError`.
**Mocked Collaborators & Expected Interactions:** None.
**Expected Observable Outcome:** `InvalidArgumentError` raised for each invalid call. Log message "Attempted to register crypto handler with invalid arguments."
**Recursive Testing Tags:** `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_002` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_003`
**Target Component(s):** `BackendCryptoService.GetCryptoHandler`
**Related Requirement(s):** FR2.7, EC6.1, Pseudo 2 (`GetCryptoHandler`)
**TDD Anchor(s):** `test_get_crypto_handler_throws_algorithm_not_found_error_for_unregistered_suite_id()`
**Description:** Verify `GetCryptoHandler` throws `AlgorithmNotFoundError` for an unregistered suite_id.
**Test Steps:**
    1.  Setup: Initialize `BackendCryptoService` (ensure `_HANDLER_REGISTRY` is empty or does not contain "UNKNOWN_SUITE").
    2.  Action: Call `BackendCryptoService.GetCryptoHandler("UNKNOWN_SUITE")`.
    3.  Assert: `AlgorithmNotFoundError` is raised.
**Mocked Collaborators & Expected Interactions:** None.
**Expected Observable Outcome:** `AlgorithmNotFoundError` ("Handler for suite 'UNKNOWN_SUITE' not registered.") raised. Log message "No crypto handler registered for suite_id: UNKNOWN_SUITE".
**Recursive Testing Tags:** `@critical_path`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_003` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_004`
**Target Component(s):** `BackendCryptoService.GetCryptoHandler` (with factory)
**Related Requirement(s):** FR2.4, Pseudo 2 (`GetCryptoHandler`)
**TDD Anchor(s):** `test_get_crypto_handler_correctly_uses_factory_to_create_handler_instance()`
**Description:** Verify `GetCryptoHandler` correctly uses a registered factory to create and return a handler instance.
**Test Steps:**
    1.  Setup:
        *   Create a mock factory (`mock_factory`) with a `CREATE_INSTANCE(suite_config)` method that returns a `mock_handler_instance`.
        *   Mock `GlobalConfig.GetCryptoSettings()` to return a config object containing `data_at_rest.suites["SUITE_F"] = mock_suite_config_f`.
        *   Initialize `BackendCryptoService` and register `mock_factory` for "SUITE_F".
    2.  Action: Call `BackendCryptoService.GetCryptoHandler("SUITE_F")`.
    3.  Assert:
        *   `GlobalConfig.GetCryptoSettings()` was called.
        *   `mock_factory.CREATE_INSTANCE` was called with `mock_suite_config_f`.
        *   The returned handler is `mock_handler_instance`.
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
    *   `mock_factory.CREATE_INSTANCE(mock_suite_config_f)`: Called once.
**Expected Observable Outcome:** `mock_handler_instance` returned.
**Recursive Testing Tags:** `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_004` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_005`
**Target Component(s):** `BackendCryptoService.GetActiveEncryptionHandler`
**Related Requirement(s):** FR2.5, Spec 10.1, Pseudo 2 (`GetActiveEncryptionHandler`)
**TDD Anchor(s):** `test_crypto_service_locator_returns_active_encryption_handler()`, `test_get_active_encryption_handler_retrieves_handler_matching_active_suite_id_in_config()`
**Description:** Verify `GetActiveEncryptionHandler` returns the handler corresponding to `active_encryption_suite_id` in config.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` to return config where `data_at_rest.active_encryption_suite_id = "ACTIVE_SUITE"`.
        *   Create `mock_active_handler` and register it for "ACTIVE_SUITE" in `BackendCryptoService`.
    2.  Action: Call `BackendCryptoService.GetActiveEncryptionHandler()`.
    3.  Assert: `GlobalConfig.GetCryptoSettings()` was called. The returned handler is `mock_active_handler`.
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
    *   (Internal) `BackendCryptoService.GetCryptoHandler("ACTIVE_SUITE")`: Called.
**Expected Observable Outcome:** `mock_active_handler` returned.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_005` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_006`
**Target Component(s):** `BackendCryptoService.GetActiveEncryptionHandler`
**Related Requirement(s):** FR2.7, EC6.1, EC6.2, Pseudo 2 (`GetActiveEncryptionHandler` - error cases)
**TDD Anchor(s):** (Implicit from error handling in `GetActiveEncryptionHandler` pseudocode)
**Description:** Verify `GetActiveEncryptionHandler` throws error if active suite ID is missing or its handler is not registered/unavailable.
**Test Steps & Assertions:**
    1.  Setup: Mock `GlobalConfig.GetCryptoSettings()` to return config where `active_encryption_suite_id` is null or empty.
        Action: Call `GetActiveEncryptionHandler()`. Expect `ConfigurationError`. Log "Active encryption suite ID...is not configured."
    2.  Setup: Mock `GlobalConfig.GetCryptoSettings()` for `active_encryption_suite_id = "UNAVAILABLE_ACTIVE_SUITE"`. Do NOT register a handler for "UNAVAILABLE_ACTIVE_SUITE".
        Action: Call `GetActiveEncryptionHandler()`. Expect `CriticalConfigurationError`. Log "Configured active encryption handler...is not registered..."
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
**Expected Observable Outcome:** Appropriate errors raised and logs generated.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_006` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_007`
**Target Component(s):** `BackendCryptoService.GetConfiguredDecryptionHandlers`
**Related Requirement(s):** FR2.9, Spec 10.1, Pseudo 2 (`GetConfiguredDecryptionHandlers`)
**TDD Anchor(s):** `test_crypto_service_locator_returns_decryption_handlers_in_order()`, `test_get_configured_decryption_handlers_returns_list_of_handlers_matching_order_in_config()`
**Description:** Verify `GetConfiguredDecryptionHandlers` returns a list of handlers in the order specified by `decryption_attempt_order`.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` to return config with `data_at_rest.decryption_attempt_order = ["SUITE_B", "SUITE_A"]`.
        *   Create `mock_handler_A` (for "SUITE_A") and `mock_handler_B` (for "SUITE_B").
        *   Register both handlers in `BackendCryptoService`.
    2.  Action: Call `BackendCryptoService.GetConfiguredDecryptionHandlers()`.
    3.  Assert: `GlobalConfig.GetCryptoSettings()` was called. The returned list is `[mock_handler_B, mock_handler_A]`.
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
**Expected Observable Outcome:** List of handlers `[mock_handler_B, mock_handler_A]` returned.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_007` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_BCS_REG_008`
**Target Component(s):** `BackendCryptoService.GetConfiguredDecryptionHandlers`
**Related Requirement(s):** FR2.7, Pseudo 2 (`GetConfiguredDecryptionHandlers` - skip unregistered)
**TDD Anchor(s):** `test_get_configured_decryption_handlers_skips_unregistered_suite_ids_and_logs_warning()`
**Description:** Verify `GetConfiguredDecryptionHandlers` skips unregistered suite IDs from `decryption_attempt_order` and logs a warning.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` for `decryption_attempt_order = ["REGISTERED_SUITE", "SKIPPED_SUITE"]`.
        *   Create and register `mock_handler_registered` for "REGISTERED_SUITE". Do NOT register "SKIPPED_SUITE".
    2.  Action: Call `BackendCryptoService.GetConfiguredDecryptionHandlers()`.
    3.  Assert: The returned list is `[mock_handler_registered]`. A warning is logged for "SKIPPED_SUITE".
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
**Expected Observable Outcome:** List `[mock_handler_registered]` returned. Log "Crypto handler for suite_id 'SKIPPED_SUITE'...not found..."
**Recursive Testing Tags:** `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_BCS_REG_008` is implemented, passes, and its successful execution is logged/reported.

---
#### 5.2.2. `HybridPqcCryptoHandler` (Example Implementation)

(Assuming `HybridPqcCryptoHandler` as UUT, mocking `KEM_LIBRARY`, `KDF_LIBRARY`, `SYMMETRIC_CIPHER_LIBRARY`)

**Test Case ID:** `TC_AGL_HCH_001`
**Target Component(s):** `HybridPqcCryptoHandler.constructor`
**Related Requirement(s):** Pseudo 2 (HybridPqcCryptoHandler constructor)
**TDD Anchor(s):** `test_hybrid_handler_constructor_sets_id_and_config()`, `test_hybrid_handler_constructor_throws_if_essential_algos_missing_in_config(...)`
**Description:** Verify constructor sets ID/config and throws if essential algorithms are missing in suite config.
**Test Steps:**
    1.  Setup: `mock_suite_id = "HYBRID_TEST"`. `valid_suite_config` with all required algorithms. `invalid_suite_config` missing `pqc_kem_algorithm`.
    2.  Action & Assert (Success): `handler = HybridPqcCryptoHandler(mock_suite_id, valid_suite_config)`. Handler's internal ID and config match.
    3.  Action & Assert (Failure): `HybridPqcCryptoHandler(mock_suite_id, invalid_suite_config)` -> Expect `ConfigurationError`.
**Mocked Collaborators & Expected Interactions:** None.
**Expected Observable Outcome:** Successful instantiation or `ConfigurationError`.
**Recursive Testing Tags:** `@suite_specific_HYBRID_TEST`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HCH_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_HCH_002`
**Target Component(s):** `HybridPqcCryptoHandler.encrypt`
**Related Requirement(s):** FR2.6, Pseudo 2 (`HybridPqcCryptoHandler.encrypt`)
**TDD Anchor(s):** `test_hybrid_encrypt_generates_valid_bundle_with_all_fields()`, `test_hybrid_encrypt_classical_kem_interface_returns_secret_and_ephemeral_pk()`, etc.
**Description:** Verify `encrypt` correctly interacts with KEM, KDF, and Symmetric Cipher libraries and produces a valid `HybridEncryptedBundle`.
**Test Steps:**
    1.  Setup:
        *   Instantiate `HybridPqcCryptoHandler` with a valid `suite_config` (e.g., X25519, ML-KEM-768, AES256GCM, HKDF-SHA3-512).
        *   `plaintext_bytes`, `key_material_for_encryption` (with mock classical and PQC recipient PKs).
        *   Mock `KEM_LIBRARY.hybrid_kem_classical_encapsulate` to return `{ shared_secret_classical, ephemeral_public_key }`.
        *   Mock `KEM_LIBRARY.pqc_kem_encapsulate` to return `{ shared_secret_pqc, encapsulated_key_pqc }`.
        *   Mock `KDF_LIBRARY.derive` to return `derived_symmetric_key`.
        *   Mock `SYMMETRIC_CIPHER_LIBRARY.encrypt_aead` to return `{ ciphertext, authentication_tag }`.
        *   Mock `GENERATE_RANDOM_BYTES` for IV.
    2.  Action: Call `handler.encrypt(plaintext_bytes, key_material_for_encryption)`.
    3.  Assert:
        *   `KEM_LIBRARY.hybrid_kem_classical_encapsulate` called with correct algo and PK.
        *   `KEM_LIBRARY.pqc_kem_encapsulate` called with correct algo and PK.
        *   `KDF_LIBRARY.derive` called with concatenated secrets, correct KDF algo, key length, context.
        *   `SYMMETRIC_CIPHER_LIBRARY.encrypt_aead` called with correct symmetric algo, derived key, IV, plaintext.
        *   Returned `HybridEncryptedBundle` contains all expected fields populated from mock return values (suite_id, ephemeral_pk, encapsulated_key, iv, ciphertext, tag).
**Mocked Collaborators & Expected Interactions:** As listed in Test Steps.
**Expected Observable Outcome:** A `HybridEncryptedBundle` object with all fields correctly populated.
**Recursive Testing Tags:** `@suite_specific_HYBRID_TEST`, `@security_sensitive`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HCH_002` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_HCH_003`
**Target Component(s):** `HybridPqcCryptoHandler.decrypt`
**Related Requirement(s):** FR2.6, Pseudo 2 (`HybridPqcCryptoHandler.decrypt`)
**TDD Anchor(s):** `test_hybrid_decrypt_reverses_encrypt_successfully_with_valid_keys_and_bundle()`, `test_hybrid_decrypt_aead_verifies_tag_and_returns_original_plaintext()`, etc.
**Description:** Verify `decrypt` correctly reconstructs plaintext from a valid bundle and key material, interacting with crypto libraries.
**Test Steps:**
    1.  Setup:
        *   Instantiate `HybridPqcCryptoHandler` with `suite_config`.
        *   `key_material_for_decryption` (with mock classical and PQC recipient SKs).
        *   A valid `mock_bundle` (as if produced by `encrypt`).
        *   Mock `KEM_LIBRARY.hybrid_kem_classical_decapsulate` to return `shared_secret_classical`.
        *   Mock `KEM_LIBRARY.pqc_kem_decapsulate` to return `shared_secret_pqc`.
        *   Mock `KDF_LIBRARY.derive` to return `derived_symmetric_key` (same as encryption).
        *   Mock `SYMMETRIC_CIPHER_LIBRARY.decrypt_aead` to return `original_plaintext_bytes`.
    2.  Action: Call `handler.decrypt(mock_bundle, key_material_for_decryption)`.
    3.  Assert:
        *   `KEM_LIBRARY.hybrid_kem_classical_decapsulate` called with correct algo, ephemeral PK from bundle, and SK.
        *   `KEM_LIBRARY.pqc_kem_decapsulate` called with correct algo, encapsulated key from bundle, and SK.
        *   `KDF_LIBRARY.derive` called correctly.
        *   `SYMMETRIC_CIPHER_LIBRARY.decrypt_aead` called with correct symmetric algo, derived key, IV from bundle, ciphertext from bundle, tag from bundle.
        *   Returned value is `original_plaintext_bytes`.
**Mocked Collaborators & Expected Interactions:** As listed in Test Steps.
**Expected Observable Outcome:** `original_plaintext_bytes` returned.
**Recursive Testing Tags:** `@suite_specific_HYBRID_TEST`, `@security_sensitive`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HCH_003` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_HCH_004`
**Target Component(s):** `HybridPqcCryptoHandler.decrypt`
**Related Requirement(s):** EC6.4, Pseudo 2 (`HybridPqcCryptoHandler.decrypt` - error cases)
**TDD Anchor(s):** `test_hybrid_decrypt_fails_on_tampered_ciphertext_auth_tag_mismatch()`
**Description:** Verify `decrypt` fails (e.g., raises `DecryptionError`) if AEAD decryption/verification fails (e.g., tampered data, wrong key).
**Test Steps:**
    1.  Setup: Similar to `TC_AGL_HCH_003`, but mock `SYMMETRIC_CIPHER_LIBRARY.decrypt_aead` to return `NULL` or raise a specific crypto error indicating tag mismatch/decryption failure.
    2.  Action: Call `handler.decrypt(mock_bundle, key_material_for_decryption)`.
    3.  Assert: `SYMMETRIC_CIPHER_LIBRARY.decrypt_aead` was called.
**Mocked Collaborators & Expected Interactions:** `SYMMETRIC_CIPHER_LIBRARY.decrypt_aead` is called and indicates failure.
**Expected Observable Outcome:** `DecryptionError` ("Symmetric decryption failed...") is raised.
**Recursive Testing Tags:** `@suite_specific_HYBRID_TEST`, `@error_handling`, `@security_sensitive`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HCH_004` is implemented, passes, and its successful execution is logged/reported.

---
#### 5.2.3. Hashing Provider

**Test Case ID:** `TC_AGL_HP_001`
**Target Component(s):** `BackendCryptoService.HashingProvider.GetConfiguredHasher`
**Related Requirement(s):** FR2.1, FR2.3, Pseudo 2 (`HashingProvider`)
**TDD Anchor(s):** `test_hashing_provider_returns_sha3_256_hasher_if_configured()`, `test_hashing_provider_returns_sha256_hasher_if_configured()`
**Description:** Verify `GetConfiguredHasher` returns the hasher instance corresponding to `hashing.default_algorithm` in config.
**Test Steps (Parametrized for SHA3-256 and SHA256):**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` to return config with `hashing.default_algorithm = <ALGO_NAME>` (e.g., "SHA3-256").
        *   Mock `GET_HASHER_INSTANCE(<ALGO_NAME>)` to return `mock_hasher_instance_algo`.
    2.  Action: Call `HashingProvider.GetConfiguredHasher()`.
    3.  Assert: `GlobalConfig.GetCryptoSettings()` called. `GET_HASHER_INSTANCE` called with `<ALGO_NAME>`. Returned object is `mock_hasher_instance_algo`.
**Mocked Collaborators & Expected Interactions:**
    *   `GlobalConfig.GetCryptoSettings()`: Called.
    *   `GET_HASHER_INSTANCE(<ALGO_NAME>)`: Called.
**Expected Observable Outcome:** Correct mock hasher instance returned.
**Recursive Testing Tags:** `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HP_001` is implemented (for SHA3-256 and SHA256), passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_HP_002`
**Target Component(s):** `BackendCryptoService.HashingProvider.GetConfiguredHasher`
**Related Requirement(s):** FR2.7, Pseudo 2 (`HashingProvider` - fallback)
**TDD Anchor(s):** `test_hashing_provider_falls_back_to_sha3_256_and_logs_warning_if_configured_algo_unavailable()`
**Description:** Verify `GetConfiguredHasher` falls back to SHA3-256 if the configured algorithm is unavailable.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` for `hashing.default_algorithm = "UNAVAILABLE_HASH"`.
        *   Mock `GET_HASHER_INSTANCE("UNAVAILABLE_HASH")` to raise `AlgorithmUnavailableError`.
        *   Mock `GET_HASHER_INSTANCE("SHA3-256")` to return `mock_sha3_hasher_instance`.
    2.  Action: Call `HashingProvider.GetConfiguredHasher()`.
    3.  Assert:
        *   `GET_HASHER_INSTANCE("UNAVAILABLE_HASH")` called first.
        *   `GET_HASHER_INSTANCE("SHA3-256")` called after the error.
        *   Returned object is `mock_sha3_hasher_instance`.
        *   Warning logged: "Configured hash algorithm 'UNAVAILABLE_HASH' is unavailable... Attempting fallback..."
**Mocked Collaborators & Expected Interactions:** As in steps.
**Expected Observable Outcome:** `mock_sha3_hasher_instance` returned, warning logged.
**Recursive Testing Tags:** `@config_dependent`, `@error_handling`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_HP_002` is implemented, passes, and its successful execution is logged/reported.

---
#### 5.2.4. Decryption Orchestration

**Test Case ID:** `TC_AGL_DO_001`
**Target Component(s):** `BackendCryptoService.DecryptDataAtRestWithAgility`
**Related Requirement(s):** FR2.9, C7.5, Pseudo 2 (`DecryptDataAtRestWithAgility`)
**TDD Anchor(s):** `test_decrypt_data_at_rest_tries_handlers_from_decryption_attempt_order()`, `test_decrypt_data_at_rest_parses_bundle_header_to_get_suite_id_for_targeted_first_attempt()`
**Description:** Verify `DecryptDataAtRestWithAgility` first attempts decryption with handler identified from bundle header, then tries handlers from `decryption_attempt_order`.
**Test Steps:**
    1.  Setup:
        *   `raw_encrypted_bytes`. `key_material_input`.
        *   Mock `PARSE_COMMON_ENCRYPTED_BUNDLE_HEADER(raw_encrypted_bytes)` to return `{ was_successful: True, suite_id: "SUITE_FROM_HEADER", bundle_object: mock_bundle_header }`.
        *   Mock `GlobalConfig.GetCryptoSettings()` for `decryption_attempt_order = ["LEGACY_SUITE_1", "SUITE_FROM_HEADER"]` and suite configs.
        *   Mock `BackendCryptoService.GetConfiguredDecryptionHandlers()` to return `[mock_handler_legacy1, mock_handler_header_from_list]`.
        *   `mock_handler_from_header` (for "SUITE_FROM_HEADER", distinct instance if needed for targeted attempt) whose `decrypt` method initially fails.
        *   `mock_handler_legacy1` whose `decrypt` method fails.
        *   `mock_handler_header_from_list` (for "SUITE_FROM_HEADER") whose `decrypt` method succeeds and returns `expected_plaintext`.
        *   (Conceptual) `BackendCryptoService.GetCryptoHandler("SUITE_FROM_HEADER")` would be involved in the targeted attempt.
    2.  Action: Call `BackendCryptoService.DecryptDataAtRestWithAgility(raw_encrypted_bytes, key_material_input)`.
    3.  Assert:
        *   `PARSE_COMMON_ENCRYPTED_BUNDLE_HEADER` was called.
        *   `mock_handler_from_header.decrypt` (or equivalent via `GetCryptoHandler("SUITE_FROM_HEADER")`) was called with `mock_bundle_header` and failed.
        *   `BackendCryptoService.GetConfiguredDecryptionHandlers()` was called.
        *   `mock_handler_legacy1.decrypt` was called and failed.
        *   `mock_handler_header_from_list.decrypt` was called and succeeded.
        *   The returned value is `expected_plaintext`.
**Mocked Collaborators & Expected Interactions:** As in steps.
**Expected Observable Outcome:** `expected_plaintext` returned. Correct sequence of decryption attempts logged.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_DO_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_DO_002`
**Target Component(s):** `BackendCryptoService.DecryptDataAtRestWithAgility`
**Related Requirement(s):** EC6.4, Pseudo 2 (`DecryptDataAtRestWithAgility` - all fail)
**TDD Anchor(s):** `test_decrypt_data_at_rest_fails_with_decryption_failed_error_if_all_handlers_fail()`
**Description:** Verify `DecryptDataAtRestWithAgility` throws `DecryptionFailedError` if all attempted handlers fail.
**Test Steps:**
    1.  Setup:
        *   Mock `PARSE_COMMON_ENCRYPTED_BUNDLE_HEADER` to indicate failure or a suite not in the list.
        *   Mock `BackendCryptoService.GetConfiguredDecryptionHandlers()` to return a list of mock handlers (`handler1`, `handler2`).
        *   Both `handler1.decrypt` and `handler2.decrypt` are mocked to raise `DecryptionError`.
    2.  Action: Call `BackendCryptoService.DecryptDataAtRestWithAgility(raw_bytes, key_material)`.
    3.  Assert: `handler1.decrypt` and `handler2.decrypt` were called.
**Mocked Collaborators & Expected Interactions:** As in steps.
**Expected Observable Outcome:** `DecryptionFailedError` ("Unable to decrypt data...") is raised. Log "All configured decryption attempts failed..."
**Recursive Testing Tags:** `@error_handling`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_DO_002` is implemented, passes, and its successful execution is logged/reported.

---
### 5.3. Frontend `CryptoFacade` (`FrontendCryptoFacade` Module)

**Test Case ID:** `TC_AGL_FCF_API_001`
**Target Component(s):** `FrontendCryptoFacade._getFavaRuntimeCryptoOptions`
**Related Requirement(s):** IP12.4, Pseudo 3 (`_getFavaRuntimeCryptoOptions`)
**TDD Anchor(s):** `test_fe_get_runtime_options_fetches_from_api_if_cache_empty_or_stale()`, `test_fe_get_runtime_options_returns_cached_data_if_fresh()`
**Description:** Verify `_getFavaRuntimeCryptoOptions` fetches from API if cache is empty/stale, and uses cache if fresh.
**Test Steps:**
    1.  Setup:
        *   Mock `HTTP_GET_JSON("/api/fava-crypto-configuration")` to return `mock_api_response_config`.
        *   Mock `GET_SYSTEM_TIME_MS()` to control cache expiry.
        *   Ensure internal cache `_favaConfigCache` is initially NULL.
    2.  Action (Cache Empty): Call `_getFavaRuntimeCryptoOptions()`.
    3.  Assert: `HTTP_GET_JSON` was called. Returned config matches `mock_api_response_config.crypto_settings`. Cache is populated.
    4.  Action (Cache Fresh): Call `_getFavaRuntimeCryptoOptions()` again (ensure time hasn't expired cache).
    5.  Assert: `HTTP_GET_JSON` was NOT called. Returned config from cache.
    6.  Action (Cache Stale): Advance mock time beyond `CONFIG_CACHE_TTL_MS`. Call `_getFavaRuntimeCryptoOptions()`.
    7.  Assert: `HTTP_GET_JSON` was called again.
**Mocked Collaborators & Expected Interactions:** `HTTP_GET_JSON`, `GET_SYSTEM_TIME_MS`.
**Expected Observable Outcome:** Correct config object returned, API called/not called as expected.
**Recursive Testing Tags:** `@critical_path`, `@frontend`, `@api_driven`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_FCF_API_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_FCF_HASH_001`
**Target Component(s):** `FrontendCryptoFacade.CalculateConfiguredHash`
**Related Requirement(s):** FR2.2, Spec 10.2, Pseudo 3 (`CalculateConfiguredHash`)
**TDD Anchor(s):** `test_calculateConfiguredHash_uses_sha3_by_default_from_mock_api()`, `test_fe_calculate_hash_uses_algorithm_from_api_config_sha256()`
**Description:** Verify `CalculateConfiguredHash` uses the hashing algorithm specified in the (mocked) API config.
**Test Steps (Parametrized for "SHA3-256" and "SHA256"):**
    1.  Setup:
        *   Mock `_getFavaRuntimeCryptoOptions` to return `{ hashing: { default_algorithm: <ALGO_NAME> } }`.
        *   Mock `_internalCalculateHash(data_bytes, <ALGO_NAME>)` to return `mock_hashed_bytes_algo`.
        *   Mock `BYTES_TO_HEX_STRING` to return `expected_hex_digest`.
    2.  Action: Call `FrontendCryptoFacade.CalculateConfiguredHash("test_data")`.
    3.  Assert:
        *   `_getFavaRuntimeCryptoOptions` was called.
        *   `_internalCalculateHash` was called with `UTF8_ENCODE("test_data")` and `<ALGO_NAME>`.
        *   `BYTES_TO_HEX_STRING` was called with `mock_hashed_bytes_algo`.
        *   Returned value is `expected_hex_digest`.
**Mocked Collaborators & Expected Interactions:** `_getFavaRuntimeCryptoOptions`, `_internalCalculateHash`, `BYTES_TO_HEX_STRING`.
**Expected Observable Outcome:** `expected_hex_digest` returned.
**Recursive Testing Tags:** `@config_dependent`, `@frontend`, `@api_driven`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_FCF_HASH_001` is implemented (for SHA3-256 and SHA256), passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_FCF_HASH_002`
**Target Component(s):** `FrontendCryptoFacade.CalculateConfiguredHash` (fallback)
**Related Requirement(s):** FR2.7, Pseudo 3 (`CalculateConfiguredHash` - fallback)
**TDD Anchor(s):** `test_fe_calculate_hash_falls_back_to_sha3_256_if_api_config_algo_unavailable_logs_warning()`
**Description:** Verify `CalculateConfiguredHash` falls back to SHA3-256 if the API-configured algo causes an error.
**Test Steps:**
    1.  Setup:
        *   Mock `_getFavaRuntimeCryptoOptions` for `hashing.default_algorithm = "FAILING_ALGO"`.
        *   Mock `_internalCalculateHash(data, "FAILING_ALGO")` to throw an error.
        *   Mock `_internalCalculateHash(data, "SHA3-256")` to return `mock_hashed_bytes_sha3`.
        *   Mock `BYTES_TO_HEX_STRING` for the SHA3 result.
    2.  Action: Call `FrontendCryptoFacade.CalculateConfiguredHash("test_data")`.
    3.  Assert:
        *   `_internalCalculateHash` called first with "FAILING_ALGO".
        *   `_internalCalculateHash` called second with "SHA3-256".
        *   Warning logged: "CalculateConfiguredHash failed... Attempting fallback." and "Used fallback SHA3-256..."
        *   Returns hex digest of `mock_hashed_bytes_sha3`.
**Mocked Collaborators & Expected Interactions:** As in steps.
**Expected Observable Outcome:** Fallback hash digest returned, warnings logged.
**Recursive Testing Tags:** `@error_handling`, `@frontend`, `@api_driven`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_FCF_HASH_002` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_FCF_WASM_001`
**Target Component(s):** `FrontendCryptoFacade.VerifyWasmSignatureWithConfig`
**Related Requirement(s):** FR2.2, Spec 10.2, Pseudo 3 (`VerifyWasmSignatureWithConfig`)
**TDD Anchor(s):** `test_verifyWasmSignatureWithConfig_uses_dilithium3_from_mock_api()`, `test_fe_verify_wasm_sig_calls_internal_verify_with_params_from_api_config()`
**Description:** Verify `VerifyWasmSignatureWithConfig` uses Dilithium3 parameters from API config when verification is enabled.
**Test Steps:**
    1.  Setup:
        *   `wasm_module_buffer`, `signature_buffer`.
        *   Mock `_getFavaRuntimeCryptoOptions` to return `{ wasm_integrity: { verification_enabled: true, public_key_dilithium3_base64: "MOCK_DIL_PK_B64", signature_algorithm: "Dilithium3" } }`.
        *   Mock `_internalVerifySignature(wasm_module_buffer, signature_buffer, "MOCK_DIL_PK_B64", "Dilithium3")` to return `true`.
    2.  Action: Call `FrontendCryptoFacade.VerifyWasmSignatureWithConfig(wasm_module_buffer, signature_buffer)`.
    3.  Assert:
        *   `_getFavaRuntimeCryptoOptions` was called.
        *   `_internalVerifySignature` was called with the correct parameters from mock config.
        *   Returned value is `true`.
**Mocked Collaborators & Expected Interactions:** `_getFavaRuntimeCryptoOptions`, `_internalVerifySignature`.
**Expected Observable Outcome:** `true` returned.
**Recursive Testing Tags:** `@config_dependent`, `@frontend`, `@api_driven`, `@security_sensitive`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_FCF_WASM_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_FCF_WASM_002`
**Target Component(s):** `FrontendCryptoFacade.VerifyWasmSignatureWithConfig`
**Related Requirement(s):** Pseudo 3 (`VerifyWasmSignatureWithConfig` - disabled)
**TDD Anchor(s):** `test_fe_verify_wasm_sig_returns_true_if_verification_disabled_in_api_config()`
**Description:** Verify `VerifyWasmSignatureWithConfig` returns `true` if verification is disabled in API config, without calling internal verification.
**Test Steps:**
    1.  Setup: Mock `_getFavaRuntimeCryptoOptions` for `wasm_integrity.verification_enabled: false`. Spy on `_internalVerifySignature`.
    2.  Action: Call `FrontendCryptoFacade.VerifyWasmSignatureWithConfig(...)`.
    3.  Assert: `_internalVerifySignature` was NOT called. Returned value is `true`. Log "WASM signature verification is disabled..."
**Mocked Collaborators & Expected Interactions:** `_getFavaRuntimeCryptoOptions`. `_internalVerifySignature` (spied, not called).
**Expected Observable Outcome:** `true` returned.
**Recursive Testing Tags:** `@config_dependent`, `@frontend`, `@api_driven`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_FCF_WASM_002` is implemented, passes, and its successful execution is logged/reported.

---
### 5.4. Initialization and Registration Flow (Backend - Integration Style)

**Test Case ID:** `TC_AGL_INIT_001`
**Target Component(s):** Application Startup Logic (Conceptual: `InitializeBackendCryptoService`)
**Related Requirement(s):** Pseudo 4
**TDD Anchor(s):** `test_app_startup_registers_all_valid_handlers_from_config_suites()`
**Description:** Verify that on app startup, all valid crypto handlers defined in `FAVA_CRYPTO_SETTINGS.data_at_rest.suites` are registered with `BackendCryptoService`.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` to return a config with multiple valid suites (e.g., "SUITE_HYBRID", "SUITE_GPG_MOCK").
        *   Spy on `BackendCryptoService.RegisterCryptoHandler`.
        *   Provide mock handler classes/factories for "SUITE_HYBRID" and "SUITE_GPG_MOCK".
    2.  Action: Execute the conceptual `InitializeBackendCryptoService()` procedure.
    3.  Assert:
        *   `GlobalConfig.GetCryptoSettings()` was called.
        *   `BackendCryptoService.RegisterCryptoHandler` was called for "SUITE_HYBRID" with a corresponding handler/factory.
        *   `BackendCryptoService.RegisterCryptoHandler` was called for "SUITE_GPG_MOCK" with a corresponding handler/factory.
**Mocked Collaborators & Expected Interactions:** `GlobalConfig.GetCryptoSettings`, `BackendCryptoService.RegisterCryptoHandler` (spied).
**Expected Observable Outcome:** All valid handlers from config are registered.
**Recursive Testing Tags:** `@critical_path`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_INIT_001` is implemented, passes, and its successful execution is logged/reported.

**Test Case ID:** `TC_AGL_INIT_002`
**Target Component(s):** Application Startup Logic
**Related Requirement(s):** Pseudo 4
**TDD Anchor(s):** `test_app_startup_throws_critical_error_if_active_encryption_handler_cannot_be_loaded_after_registration()`
**Description:** Verify app startup fails critically if the configured `active_encryption_suite_id` handler cannot be loaded after registration phase.
**Test Steps:**
    1.  Setup:
        *   Mock `GlobalConfig.GetCryptoSettings()` to return config with `active_encryption_suite_id = "ACTIVE_BUT_FAIL_LOAD"`.
        *   During the conceptual registration loop, ensure no handler (or a faulty one) is registered for "ACTIVE_BUT_FAIL_LOAD".
        *   Mock `BackendCryptoService.GetActiveEncryptionHandler` (when called after registration loop) to throw `CriticalConfigurationError`.
    2.  Action: Execute `InitializeBackendCryptoService()`.
    3.  Assert: `BackendCryptoService.GetActiveEncryptionHandler` was called.
**Mocked Collaborators & Expected Interactions:** `GlobalConfig.GetCryptoSettings`, `BackendCryptoService.RegisterCryptoHandler` (may be called for other suites), `BackendCryptoService.GetActiveEncryptionHandler`.
**Expected Observable Outcome:** `ApplicationStartupError` (or similar critical error) is raised. Log "Failed to load active encryption handler..."
**Recursive Testing Tags:** `@critical_path`, `@error_handling`, `@config_dependent`, `@backend`
**AI Verifiable Completion Criterion:** Test case `TC_AGL_INIT_002` is implemented, passes, and its successful execution is logged/reported.

---

## 6. AI Verifiable Completion Criteria for this Test Plan

*   **Criterion 1:** This Test Plan document ([`docs/test-plans/PQC_Cryptographic_Agility_Test_Plan.md`](./PQC_Cryptographic_Agility_Test_Plan.md)) is created and contains all sections as outlined (Introduction, Test Scope, Test Strategy, Test Environment & Setup, Test Cases, AI Verifiable Completion Criteria).
    *   **Verification:** Existence of the file with the specified structure and content.
*   **Criterion 2:** The Test Scope section correctly identifies the features to be tested and maps them to the relevant AVERs from the [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md) and high-level acceptance tests.
    *   **Verification:** Manual review of Section 2 against source documents.
*   **Criterion 3:** The Test Strategy section details the adoption of London School TDD principles and a comprehensive recursive testing strategy.
    *   **Verification:** Manual review of Section 3 for adherence to principles and completeness of regression strategy.
*   **Criterion 4:** Each defined Test Case (Section 5) includes a unique ID, target component, related requirements/TDD anchors, description, interaction-focused test steps, mocked collaborators, expected observable outcome, recursive testing tags, and its own AI verifiable completion criterion.
    *   **Verification:** Manual review of each test case in Section 5 for completeness of these elements.
*   **Criterion 5:** The test cases collectively provide adequate coverage for the functional requirements, edge cases, and error handling conditions specified in [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](../specifications/PQC_Cryptographic_Agility_Spec.md) and [`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](../pseudocode/PQC_Cryptographic_Agility_Pseudo.md).
    *   **Verification:** Traceability matrix or manual review mapping test cases back to specification/pseudocode elements.
*   **Criterion 6:** The overall Test Plan is clear, comprehensive, and actionable for human programmers and subsequent AI testing agents.
    *   **Verification:** Review by a human programmer or another AI agent for clarity and actionability.

This Test Plan is now ready for review and to guide the implementation of granular tests for the PQC Cryptographic Agility feature.