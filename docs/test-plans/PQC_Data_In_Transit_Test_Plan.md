# Test Plan: PQC Data in Transit

**Version:** 1.0
**Date:** 2025-06-03
**Feature:** PQC Data in Transit
**Derived From:**
*   Specification: [`docs/specifications/PQC_Data_In_Transit_Spec.md`](../../docs/specifications/PQC_Data_In_Transit_Spec.md) (v1.1)
*   Pseudocode: [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md) (v1.0)
*   Architecture: [`docs/architecture/PQC_Data_In_Transit_Arch.md`](../../docs/architecture/PQC_Data_In_Transit_Arch.md) (v1.0)
*   Project Master Plan: [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md) (v1.1)

## 1. Introduction

### 1.1. Purpose
This document outlines the granular test plan for the "PQC Data in Transit" feature of the Fava application. The primary architectural decision for this feature, as detailed in [`docs/architecture/PQC_Data_In_Transit_Arch.md`](../../docs/architecture/PQC_Data_In_Transit_Arch.md), is that Fava itself **does not perform PQC TLS cryptographic operations**. Instead, it relies on a PQC-capable reverse proxy to handle PQC TLS termination.

This test plan focuses on verifying:
1.  Fava's internal logic related to awareness of PQC protection (e.g., via proxy-set headers or configuration), as outlined in `FavaPQCProxyAwareness` module in the pseudocode.
2.  The correctness and completeness of Fava's generated documentation for configuring reverse proxies (e.g., Nginx, Caddy) to use PQC hybrid KEMs for TLS 1.3 (specifically `X25519Kyber768`), as per the `FavaDocumentationGenerator` module.
3.  (Future Consideration) Validation logic for Fava's configuration options related to direct PQC KEM specification if its embedded web server gains such capabilities, as per the `FavaConfigurationValidator` module.
4.  Fava's general operational correctness and logging behavior when requests are received that notionally pass through a PQC-secured channel.

### 1.2. Scope
The scope of this test plan includes granular unit and integration tests for the Fava components responsible for the aspects listed in section 1.1. It does **not** cover:
*   Testing the PQC cryptographic implementations within external reverse proxies or client browsers.
*   Full end-to-end PQC TLS handshake testing (which is covered by acceptance tests like `PQC_DIT_001` from [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](../../tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md) and the TDD anchor `test_fava_api_accessible_via_x25519kyber768_tls_proxy` from the specification). However, these granular tests ensure Fava behaves correctly as a component within such a scenario.

The tests defined herein aim to verify the AI Verifiable End Results (AVERs) associated with the implementation of the PQC Data in Transit feature, as outlined in the [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md), specifically contributing to:
*   Successful completion of Task 4.X.B (Feature Implementation & Iteration) for PQC Data in Transit, by ensuring all granular tests pass.
*   Supporting the successful execution of relevant High-Level Acceptance Tests by ensuring Fava's components function as expected.

### 1.3. AI Verifiable Completion Criterion for this Test Plan
The Test Plan document for 'PQC Data in Transit' is created, reviewed for completeness against this section's requirements, and saved at [`docs/test-plans/PQC_Data_In_Transit_Test_Plan.md`](docs/test-plans/PQC_Data_In_Transit_Test_Plan.md). The content of the document fulfills all requirements set forth in the initial task description for its creation, including adherence to London School TDD principles, definition of a recursive testing strategy, and ensuring all its own components are AI verifiable.
    *   **AI Verifiable Check:** File `docs/test-plans/PQC_Data_In_Transit_Test_Plan.md` exists and its content aligns with the directives for this mode.

## 2. Test Strategy

### 2.1. Overall Approach: London School of TDD
This test plan adopts the **London School of Test-Driven Development (TDD)**. Tests will focus on the **observable behavior** of Fava's software units through their interactions with collaborators. Internal state verification will be avoided; instead, tests will verify that units send the correct messages (method calls with correct arguments) to their collaborators and produce the correct, observable outcomes (return values, state changes in collaborators if applicable, side effects like logging or file generation).

### 2.2. Mocking and Interaction Testing
*   **Collaborators:** Dependencies of the Unit Under Test (UUT) will be treated as collaborators.
*   **Mocking:** Collaborators will be replaced with mock objects during testing. These mocks will be configured to:
    *   Expect specific interactions (method calls with specific arguments).
    *   Return predefined values or simulate specific behaviors/exceptions.
*   **Interaction Verification:** Tests will assert that the UUT interacts with its mocked collaborators as expected.

### 2.3. Unit Under Test (UUT) Definition
For this feature, UUTs will typically be:
*   Python functions or methods within the `FavaPQCProxyAwareness`, `FavaDocumentationGenerator`, and `FavaConfigurationValidator` conceptual modules (as defined in [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md)).
*   Fava's request handling pipeline components or initialization routines, verifying their response to specific (mocked) PQC-related inputs or configurations.

### 2.4. AI Verifiable Criterion for Test Strategy Adherence
Test code implementing the cases in this plan will demonstrate the use of mocking frameworks (e.g., Python's `unittest.mock`) and assertions focused on interactions and observable outcomes rather than internal state. Code reviews of the test implementations will confirm this adherence.
    *   **AI Verifiable Check:** Test implementation files (e.g., in `tests/granular/pqc_data_in_transit/`) utilize mocking for collaborators and assert on interactions or return values.

## 3. Recursive Testing (Regression Strategy)

A comprehensive recursive testing strategy is crucial to ensure ongoing stability and catch regressions early as Fava evolves.

### 3.1. Triggers for Re-running Tests
Test suites, or relevant subsets, will be re-executed upon the following triggers (SDLC touchpoints):
1.  **Code Changes:**
    *   Any modification to Fava modules directly related to PQC Data in Transit (e.g., documentation generation logic, configuration parsing for PQC, request header inspection).
    *   Changes to core Fava request handling, configuration loading, or logging mechanisms that might indirectly affect PQC-related behavior.
2.  **Dependency Updates:** Changes in how Fava interacts with its web server framework (e.g., Flask, Cheroot) if relevant to PQC configuration or header processing.
3.  **Documentation Content Updates:** Changes to the source templates or logic for generating PQC-TLS setup guides.
4.  **PQC Landscape Evolution:** Significant updates to recommended PQC KEMs (e.g., `X25519Kyber768`), proxy configuration best practices, or browser PQC support that necessitate updates to Fava's documentation or awareness logic.
5.  **Build Process Changes:** Modifications to how Fava's documentation is built or packaged.
6.  **Scheduled Runs:** Full regression suites run periodically (e.g., nightly builds via CI) and always before a release.

### 3.2. Test Prioritization and Tagging
Tests will be tagged to allow for targeted execution:
*   `pqc_transit_awareness`: Tests for the `FavaPQCProxyAwareness` module.
*   `pqc_transit_docs`: Tests for the `FavaDocumentationGenerator` module.
*   `pqc_transit_config_validation`: Tests for the `FavaConfigurationValidator` module (future embedded server PQC).
*   `pqc_transit_logging`: Tests for PQC-related logging.
*   `smoke`: A small subset of critical path tests from each category.
*   `regression_critical`: Key tests covering primary functionalities.
*   `regression_full`: All tests for the PQC Data in Transit feature.

Priority will be given based on the criticality of the functionality (e.g., documentation accuracy is high) and the likelihood of regression.

### 3.3. Test Subset Selection for Regression
*   **On Minor Code Change (specific module):** Run tests tagged for that module (e.g., `pqc_transit_docs` if doc generation changed) and `smoke` tests.
*   **On Core Fava Change (e.g., request handling, config):** Run `pqc_transit_awareness`, `pqc_transit_logging`, `regression_critical`, and `smoke` tests.
*   **On PQC Landscape Change (affecting docs):** Run `pqc_transit_docs` and `regression_critical`.
*   **Pre-Commit Hook (Developer):** Run relevant tagged tests for changed files, plus `smoke` tests.
*   **CI Pipeline (Pull Request):** Run `regression_critical` for the PQC Data in Transit feature, plus any specifically tagged tests related to changed modules.
*   **CI Pipeline (Nightly/Pre-Release):** Run `regression_full`.

### 3.4. AI Verifiable Criterion for Regression Strategy Implementation
The CI/CD pipeline configuration (e.g., GitHub Actions workflow files, `tox.ini`, or `Makefile`) and test runner scripts are updated to support tagged test execution based on the defined triggers and subsets. A report or log is available from the CI system demonstrating that tagged tests are executed according to this strategy for PQC Data in Transit tests.
    *   **AI Verifiable Check:** CI configuration files show rules for running tagged tests (e.g., `pytest -m pqc_transit_smoke`).

## 4. Test Environment

### 4.1. General Setup
*   Tests will be executed in a Python environment with Fava's dependencies installed.
*   No actual PQC-capable reverse proxy or PQC-enabled browser is required for these granular unit/integration tests, as their behavior will be mocked or simulated.

### 4.2. Key Mocked Components
*   **HTTP Request Object:** Mocked (e.g., using Flask's test client or `unittest.mock.MagicMock`) to simulate incoming requests with/without specific PQC-related headers (e.g., `X-PQC-KEM`).
*   **Fava Configuration Object:** Mocked to provide different PQC-related configuration settings.
*   **File System / Output Streams:** Mocked (e.g., `io.StringIO`, `unittest.mock.patch` for file operations) for tests involving documentation generation to capture and verify the generated content.
*   **Logging System:** Mocked (e.g., using Python's `logging.handlers.BufferingHandler` or `unittest.mock.patch` on logger methods) to verify correct logging messages are produced.
*   **Python Environment (for future PQC support):** Mocked to simulate presence or absence of PQC KEM support in Python's SSL/server libraries for `validate_pqc_tls_embedded_server_options` tests.

### 4.3. AI Verifiable Criterion for Test Environment Setup
Test helper utilities and fixtures (e.g., in `tests/conftest.py` or specific test modules) are created that allow for easy mocking of HTTP requests, Fava configuration, file system interactions, and logging, as required by the test cases. These are available and used by the test implementations for PQC Data in Transit.
    *   **AI Verifiable Check:** Test code for PQC Data in Transit demonstrates usage of such helper utilities or direct mocking for the components listed.

## 5. Test Cases

The following test cases are derived from the pseudocode TDD anchors ([`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md)) and specification requirements ([`docs/specifications/PQC_Data_In_Transit_Spec.md`](../../docs/specifications/PQC_Data_In_Transit_Spec.md)). Each test case aims to verify a specific interaction or observable outcome.

---
**Module: `FavaPQCProxyAwareness`** (from [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md#1-module-favapqcproxyawareness))
---

### TC-DIT-AWARE-001: `check_pqc_proxy_headers` - Known PQC KEM Header Present and Recognized
*   **Target AVER(s):** Contributes to Phase 4.X.B (Feature Implementation) for PQC Data in Transit by verifying core logic. Supports FR2.1 from spec.
*   **Related TDD Anchor(s):** `TEST check_pqc_proxy_headers correctly identifies known PQC indicator header`, `TEST check_pqc_proxy_headers correctly identifies X25519Kyber768 from header`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.check_pqc_proxy_headers` function.
*   **Collaborators & Mocks:**
    *   `request_headers`: Mock dictionary.
*   **Preconditions:**
    *   The `check_pqc_proxy_headers` function is implemented.
    *   Known PQC indicator header name is defined within the UUT (e.g., "X-PQC-KEM").
    *   Recognized PQC KEMs list within the UUT includes "X25519Kyber768".
*   **Test Steps:**
    1.  Create a mock `request_headers` dictionary: `{"X-PQC-KEM": "X25519Kyber768"}`.
    2.  Call `check_pqc_proxy_headers(mock_request_headers)`.
*   **Expected Interactions & Observable Outcome:**
    *   The function reads the "X-PQC-KEM" key from `mock_request_headers`.
    *   The function returns the string `"PQC_CONFIRMED_VIA_HEADER"`.
    *   **AI Verifiable Outcome:** The return value of the function call is strictly equal to `"PQC_CONFIRMED_VIA_HEADER"`.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`, `smoke`

### TC-DIT-AWARE-002: `check_pqc_proxy_headers` - PQC Indicator Header Present but KEM Not Recognized/Classical
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST check_pqc_proxy_headers returns PQC_ABSENT_VIA_HEADER if header value indicates classical KEM` (adapted for unrecognized PQC)
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.check_pqc_proxy_headers` function.
*   **Collaborators & Mocks:**
    *   `request_headers`: Mock dictionary.
*   **Preconditions:**
    *   `check_pqc_proxy_headers` function implemented.
    *   Recognized PQC KEMs list within the UUT does *not* include "SomeOtherKEM".
*   **Test Steps:**
    1.  Create mock `request_headers` with `{"X-PQC-KEM": "SomeOtherKEM"}`.
    2.  Call `check_pqc_proxy_headers(mock_request_headers)`.
*   **Expected Interactions & Observable Outcome:**
    *   Function reads "X-PQC-KEM" from `mock_request_headers`.
    *   Returns `"PQC_ABSENT_VIA_HEADER"`.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_ABSENT_VIA_HEADER"`.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-003: `check_pqc_proxy_headers` - No PQC Indicator Header Present
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST check_pqc_proxy_headers returns UNKNOWN if no PQC indicator header is present`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.check_pqc_proxy_headers` function.
*   **Collaborators & Mocks:**
    *   `request_headers`: Mock dictionary.
*   **Preconditions:**
    *   `check_pqc_proxy_headers` function implemented.
*   **Test Steps:**
    1.  Create an empty mock `request_headers` dictionary `{}`.
    2.  Call `check_pqc_proxy_headers(mock_request_headers)`.
*   **Expected Interactions & Observable Outcome:**
    *   Function attempts to access the PQC indicator header key but finds it absent.
    *   Returns `"PQC_UNKNOWN_VIA_HEADER"`.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_UNKNOWN_VIA_HEADER"`.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-004: `check_pqc_proxy_headers` - Malformed PQC Indicator Header Value
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST check_pqc_proxy_headers handles malformed PQC indicator header gracefully (returns UNKNOWN)`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.check_pqc_proxy_headers` function.
*   **Collaborators & Mocks:**
    *   `request_headers`: Mock dictionary.
*   **Preconditions:**
    *   `check_pqc_proxy_headers` function implemented to handle non-string values gracefully.
*   **Test Steps:**
    1.  Create mock `request_headers` with `{"X-PQC-KEM": 123}` (an integer, not a string).
    2.  Call `check_pqc_proxy_headers(mock_request_headers)`.
*   **Expected Interactions & Observable Outcome:**
    *   Function reads "X-PQC-KEM", encounters a non-string value.
    *   Returns `"PQC_ABSENT_VIA_HEADER"` (as per pseudocode logic: if not in recognized KEMs, which a non-string won't be).
    *   No exceptions (e.g., `TypeError`) are raised.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_ABSENT_VIA_HEADER"`, and the function call completes without raising an unhandled exception.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`

### TC-DIT-AWARE-005: `get_pqc_status_from_config` - PQC Assumed Enabled via Config
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST get_pqc_status_from_config returns PQC_ASSUMED_ENABLED if config flag is true`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.get_pqc_status_from_config` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock Fava configuration object/dictionary.
*   **Preconditions:**
    *   `get_pqc_status_from_config` function implemented.
    *   PQC config flag name (e.g., `assume_pqc_tls_proxy_enabled`) is defined within the UUT.
*   **Test Steps:**
    1.  Create a mock `fava_config` with `{"assume_pqc_tls_proxy_enabled": True}`.
    2.  Call `get_pqc_status_from_config(mock_fava_config)`.
*   **Expected Interactions & Observable Outcome:**
    *   Function reads `assume_pqc_tls_proxy_enabled` from `mock_fava_config`.
    *   Returns `"PQC_ASSUMED_ENABLED_VIA_CONFIG"`.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_ASSUMED_ENABLED_VIA_CONFIG"`.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-006: `get_pqc_status_from_config` - PQC Assumed Disabled (Flag False or Absent)
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST get_pqc_status_from_config returns PQC_ASSUMED_DISABLED if config flag is false or absent`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.get_pqc_status_from_config` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock Fava configuration object/dictionary.
*   **Preconditions:**
    *   `get_pqc_status_from_config` function implemented.
*   **Test Steps (Scenario 1: Flag False):**
    1.  Create mock `fava_config` with `{"assume_pqc_tls_proxy_enabled": False}`.
    2.  Call `get_pqc_status_from_config(mock_fava_config)`.
    3.  Verify return is `"PQC_ASSUMED_DISABLED_VIA_CONFIG"`.
*   **Test Steps (Scenario 2: Flag Absent):**
    1.  Create an empty mock `fava_config` `{}`.
    2.  Call `get_pqc_status_from_config(mock_fava_config)`.
    3.  Verify return is `"PQC_ASSUMED_DISABLED_VIA_CONFIG"`.
*   **Expected Interactions & Observable Outcome:**
    *   Function interacts with `mock_fava_config` as expected.
    *   Returns `"PQC_ASSUMED_DISABLED_VIA_CONFIG"` in both scenarios.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_ASSUMED_DISABLED_VIA_CONFIG"` for both test scenarios.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-007: `determine_effective_pqc_status` - Prioritizes Confirmed Header Info
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST determine_effective_pqc_status prioritizes header information over config`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.determine_effective_pqc_status` function.
*   **Collaborators & Mocks:**
    *   `request_headers`: Mock dictionary.
    *   `fava_config`: Mock Fava configuration object/dictionary.
    *   `check_pqc_proxy_headers` (internal call): Mocked to control its return value.
    *   `get_pqc_status_from_config` (internal call): Mocked to verify it's not called or to control its return if it were.
*   **Preconditions:**
    *   `determine_effective_pqc_status` function implemented.
*   **Test Steps:**
    1.  Use `unittest.mock.patch` to mock `check_pqc_proxy_headers` to return `"PQC_CONFIRMED_VIA_HEADER"`.
    2.  Use `unittest.mock.patch` to mock `get_pqc_status_from_config` (e.g., to raise an error if called, or to track calls).
    3.  Create mock `request_headers` (content can be minimal if `check_pqc_proxy_headers` is fully mocked).
    4.  Create mock `fava_config` (content can be minimal if `get_pqc_status_from_config` is fully mocked or not expected to be called).
    5.  Call `determine_effective_pqc_status(mock_request_headers, mock_fava_config)`.
*   **Expected Interactions & Observable Outcome:**
    *   The mocked `check_pqc_proxy_headers` is called with `mock_request_headers`.
    *   The mocked `get_pqc_status_from_config` is NOT called.
    *   The function returns `"PQC_CONFIRMED_VIA_HEADER"`.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_CONFIRMED_VIA_HEADER"`. The mock for `get_pqc_status_from_config` confirms it was not called (e.g., `mock_get_config_status.assert_not_called()`).
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-008: `determine_effective_pqc_status` - Falls Back to Config if Header Unknown
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST determine_effective_pqc_status falls back to config if header is UNKNOWN`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.determine_effective_pqc_status` function.
*   **Collaborators & Mocks:**
    *   `request_headers`, `fava_config`: Mocked.
    *   `check_pqc_proxy_headers`: Mocked.
    *   `get_pqc_status_from_config`: Mocked.
*   **Preconditions:**
    *   `determine_effective_pqc_status` function implemented.
*   **Test Steps:**
    1.  Mock `check_pqc_proxy_headers` to return `"PQC_UNKNOWN_VIA_HEADER"`.
    2.  Mock `get_pqc_status_from_config` to return `"PQC_ASSUMED_ENABLED_VIA_CONFIG"`.
    3.  Call `determine_effective_pqc_status(mock_request_headers, mock_fava_config)`.
*   **Expected Interactions & Observable Outcome:**
    *   Mocked `check_pqc_proxy_headers` is called.
    *   Mocked `get_pqc_status_from_config` is called.
    *   Returns `"PQC_ASSUMED_ENABLED_VIA_CONFIG"`.
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_ASSUMED_ENABLED_VIA_CONFIG"`. Mocks for internal calls confirm they were called.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`, `regression_critical`

### TC-DIT-AWARE-009: `determine_effective_pqc_status` - Uncertain if Header Unknown and Config Disabled
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.1.
*   **Related TDD Anchor(s):** `TEST determine_effective_pqc_status returns PQC_STATUS_UNCERTAIN if both header and config are non-conclusive`
*   **Unit Under Test (UUT):** `FavaPQCProxyAwareness.determine_effective_pqc_status` function.
*   **Collaborators & Mocks:**
    *   `request_headers`, `fava_config`: Mocked.
    *   `check_pqc_proxy_headers`: Mocked.
    *   `get_pqc_status_from_config`: Mocked.
*   **Preconditions:**
    *   `determine_effective_pqc_status` function implemented.
*   **Test Steps:**
    1.  Mock `check_pqc_proxy_headers` to return `"PQC_UNKNOWN_VIA_HEADER"`.
    2.  Mock `get_pqc_status_from_config` to return `"PQC_ASSUMED_DISABLED_VIA_CONFIG"`.
    3.  Call `determine_effective_pqc_status(mock_request_headers, mock_fava_config)`.
*   **Expected Interactions & Observable Outcome:**
    *   Mocked `check_pqc_proxy_headers` called.
    *   Mocked `get_pqc_status_from_config` called.
    *   Returns `"PQC_STATUS_UNCERTAIN"` (as per pseudocode line 79 preference for this explicit status).
    *   **AI Verifiable Outcome:** The return value is strictly equal to `"PQC_STATUS_UNCERTAIN"`. Mocks for internal calls confirm they were called.
*   **Recursive Testing Scope Tags:** `pqc_transit_awareness`

---
**Module: `FavaDocumentationGenerator`** (from [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md#2-module-favadocumentationgenerator))
---

### TC-DIT-DOCS-001: `generate_pqc_tls_reverse_proxy_config_guide` - Nginx with X25519Kyber768
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.2, NFR3.3 from spec.
*   **Related TDD Anchor(s):** `TEST generate_pqc_tls_reverse_proxy_config_guide for Nginx includes X25519Kyber768`, `TEST generate_pqc_tls_reverse_proxy_config_guide includes disclaimer about experimental nature`, `TEST generate_pqc_tls_reverse_proxy_config_guide includes link to OQS project or relevant resources`, `TEST generate_pqc_tls_reverse_proxy_config_guide mentions classical certificates with hybrid KEMs`
*   **Unit Under Test (UUT):** `FavaDocumentationGenerator.generate_pqc_tls_reverse_proxy_config_guide` function.
*   **Collaborators & Mocks:** None (input parameters are direct values).
*   **Preconditions:**
    *   `generate_pqc_tls_reverse_proxy_config_guide` function implemented.
*   **Test Steps:**
    1.  Call `generate_pqc_tls_reverse_proxy_config_guide(proxy_type="Nginx", kem_recommendation="X25519Kyber768", relevant_research_docs=["pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md"])`.
*   **Expected Interactions & Observable Outcome:**
    *   The function returns a Markdown string.
    *   The string contains the following substrings (case-sensitive where appropriate):
        *   "Nginx"
        *   "`X25519Kyber768`"
        *   "experimental"
        *   "OQS project"
        *   "classical certificates"
        *   "ssl_conf_command Groups X25519Kyber768" (or the current Nginx directive for this)
        *   "pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md"
    *   **AI Verifiable Outcome:** The returned string contains all specified substrings. This can be verified by multiple string `in` checks or regex matches.
*   **Recursive Testing Scope Tags:** `pqc_transit_docs`, `regression_critical`, `smoke`

### TC-DIT-DOCS-002: `generate_pqc_tls_reverse_proxy_config_guide` - Caddy with X25519Kyber768
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.2, NFR3.3.
*   **Related TDD Anchor(s):** `TEST generate_pqc_tls_reverse_proxy_config_guide for Caddy includes X25519Kyber768`, `TEST generate_pqc_tls_reverse_proxy_config_guide provides Caddy specific example if proxy_type is Caddy`
*   **Unit Under Test (UUT):** `FavaDocumentationGenerator.generate_pqc_tls_reverse_proxy_config_guide` function.
*   **Collaborators & Mocks:** None.
*   **Preconditions:**
    *   `generate_pqc_tls_reverse_proxy_config_guide` function implemented.
*   **Test Steps:**
    1.  Call `generate_pqc_tls_reverse_proxy_config_guide(proxy_type="Caddy", kem_recommendation="X25519Kyber768", relevant_research_docs=[])`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a Markdown string.
    *   Contains "Caddy", "`X25519Kyber768`".
    *   Contains a conceptual Caddyfile example snippet mentioning `key_exchange_algorithms X25519Kyber768` or similar.
    *   **AI Verifiable Outcome:** The returned string contains all specified substrings/patterns.
*   **Recursive Testing Scope Tags:** `pqc_transit_docs`, `regression_critical`

### TC-DIT-DOCS-003: `generate_pqc_tls_contingency_guide` - Content Verification
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.6.
*   **Related TDD Anchor(s):** `TEST generate_pqc_tls_contingency_guide includes recommending application-layer PQC as a contingency`, `TEST generate_pqc_tls_contingency_guide references relevant research doc pf_tooling_contingency_PART_1.md`
*   **Unit Under Test (UUT):** `FavaDocumentationGenerator.generate_pqc_tls_contingency_guide` function.
*   **Collaborators & Mocks:** None.
*   **Preconditions:**
    *   `generate_pqc_tls_contingency_guide` function implemented.
*   **Test Steps:**
    1.  Call `generate_pqc_tls_contingency_guide(contingency_research_doc="pf_tooling_contingency_PART_1.md")`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a Markdown string.
    *   Contains "Contingency Planning", "application-layer PQC", "pf_tooling_contingency_PART_1.md".
    *   **AI Verifiable Outcome:** The returned string contains all specified substrings.
*   **Recursive Testing Scope Tags:** `pqc_transit_docs`, `regression_critical`

### TC-DIT-DOCS-004: `generate_pqc_tls_future_embedded_server_guide` - Content Verification (When KEMs Supported)
*   **Target AVER(s):** Contributes to Phase 4.X.B. Supports FR2.3 (future).
*   **Related TDD Anchor(s):** `TEST generate_pqc_tls_future_embedded_server_guide is generated if supported_kems is not empty`, `TEST generate_pqc_tls_future_embedded_server_guide mentions dependency on Python SSL/Cheroot PQC support`, `TEST generate_pqc_tls_future_embedded_server_guide shows example config option pqc_tls_embedded_server_kems`
*   **Unit Under Test (UUT):** `FavaDocumentationGenerator.generate_pqc_tls_future_embedded_server_guide` function.
*   **Collaborators & Mocks:** None.
*   **Preconditions:**
    *   `generate_pqc_tls_future_embedded_server_guide` function implemented.
*   **Test Steps:**
    1.  Call `generate_pqc_tls_future_embedded_server_guide(supported_kems_by_fava_embedded=["X25519Kyber768", "Kyber768"])`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a Markdown string (not empty).
    *   Contains "Future", "Embedded Web Server", "Python `ssl` module", "Cheroot", "PQC_TLS_EMBEDDED_SERVER_KEMS = [\"X25519Kyber768\", \"Kyber768\"]".
    *   **AI Verifiable Outcome:** The returned string is not empty and contains all specified substrings/patterns.
*   **Recursive Testing Scope Tags:** `pqc_transit_docs`

### TC-DIT-DOCS-005: `generate_pqc_tls_future_embedded_server_guide` - Empty Output (When No KEMs Supported)
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** (Implicit from pseudocode logic: `IF supported_kems_by_fava_embedded IS EMPTY RETURN ""`)
*   **Unit Under Test (UUT):** `FavaDocumentationGenerator.generate_pqc_tls_future_embedded_server_guide` function.
*   **Collaborators & Mocks:** None.
*   **Preconditions:**
    *   `generate_pqc_tls_future_embedded_server_guide` function implemented.
*   **Test Steps:**
    1.  Call `generate_pqc_tls_future_embedded_server_guide(supported_kems_by_fava_embedded=[])`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns an empty string.
    *   **AI Verifiable Outcome:** The returned string is strictly equal to `""`.
*   **Recursive Testing Scope Tags:** `pqc_transit_docs`

---
**Module: `FavaConfigurationValidator` (Future PQC for Embedded Server)** (from [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md#3-module-favaconfigurationvalidator))
---

### TC-DIT-CONFVAL-001: `validate_pqc_tls_embedded_server_options` - Valid KEM List
*   **Target AVER(s):** Contributes to Phase 4.X.B (for future functionality). Supports FR2.3.
*   **Related TDD Anchor(s):** `TEST validate_pqc_tls_embedded_server_options accepts valid KEM list (e.g., ["X25519Kyber768"])`
*   **Unit Under Test (UUT):** `FavaConfigurationValidator.validate_pqc_tls_embedded_server_options` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock dictionary.
    *   `known_supported_pqc_kems_by_python_env`: Mock list.
*   **Preconditions:**
    *   `validate_pqc_tls_embedded_server_options` function implemented.
*   **Test Steps:**
    1.  Create mock `fava_config = {"pqc_tls_embedded_server_kems": ["X25519Kyber768"]}`.
    2.  Create `known_kems = ["X25519Kyber768", "Kyber512"]`.
    3.  Call `validate_pqc_tls_embedded_server_options(fava_config, known_kems)`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns an empty list (no errors).
    *   **AI Verifiable Outcome:** The returned list is empty.
*   **Recursive Testing Scope Tags:** `pqc_transit_config_validation`

### TC-DIT-CONFVAL-002: `validate_pqc_tls_embedded_server_options` - KEM List with Unknown KEM
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** `TEST validate_pqc_tls_embedded_server_options rejects KEM list with unknown/unsupported KEMs`
*   **Unit Under Test (UUT):** `FavaConfigurationValidator.validate_pqc_tls_embedded_server_options` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock dictionary.
    *   `known_supported_pqc_kems_by_python_env`: Mock list.
*   **Preconditions:**
    *   `validate_pqc_tls_embedded_server_options` function implemented.
*   **Test Steps:**
    1.  Create mock `fava_config = {"pqc_tls_embedded_server_kems": ["UnknownKEM", "X25519Kyber768"]}`.
    2.  Create `known_kems = ["X25519Kyber768"]`.
    3.  Call `validate_pqc_tls_embedded_server_options(fava_config, known_kems)`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a list containing one error message indicating "UnknownKEM" is not supported and lists "X25519Kyber768" as supported.
    *   **AI Verifiable Outcome:** The returned list has length 1, and the error string in it contains "UnknownKEM" and "not supported" and "Supported: X25519Kyber768".
*   **Recursive Testing Scope Tags:** `pqc_transit_config_validation`

### TC-DIT-CONFVAL-003: `validate_pqc_tls_embedded_server_options` - Empty KEM List when Option Set
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** `TEST validate_pqc_tls_embedded_server_options rejects empty KEM list if PQC enabled for embedded`
*   **Unit Under Test (UUT):** `FavaConfigurationValidator.validate_pqc_tls_embedded_server_options` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock dictionary.
    *   `known_supported_pqc_kems_by_python_env`: Mock list.
*   **Preconditions:**
    *   `validate_pqc_tls_embedded_server_options` function implemented.
*   **Test Steps:**
    1.  Create mock `fava_config = {"pqc_tls_embedded_server_kems": []}`.
    2.  Create `known_kems = ["X25519Kyber768"]`.
    3.  Call `validate_pqc_tls_embedded_server_options(fava_config, known_kems)`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a list containing an error message indicating the KEM list is empty.
    *   **AI Verifiable Outcome:** The returned list has length 1, and the error string contains "contains no KEMs".
*   **Recursive Testing Scope Tags:** `pqc_transit_config_validation`

### TC-DIT-CONFVAL-004: `validate_pqc_tls_embedded_server_options` - Option Set but Python Env Lacks Support
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** (Implicit from pseudocode logic: `IF known_supported_pqc_kems_by_python_env IS EMPTY ... APPEND "current Fava/Python environment does not support PQC KEMs"`)
*   **Unit Under Test (UUT):** `FavaConfigurationValidator.validate_pqc_tls_embedded_server_options` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock dictionary.
    *   `known_supported_pqc_kems_by_python_env`: Mock list (empty).
*   **Preconditions:**
    *   `validate_pqc_tls_embedded_server_options` function implemented.
*   **Test Steps:**
    1.  Create mock `fava_config = {"pqc_tls_embedded_server_kems": ["X25519Kyber768"]}`.
    2.  Create `known_kems = []` (simulating no Python env support).
    3.  Call `validate_pqc_tls_embedded_server_options(fava_config, known_kems)`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns a list containing an error message indicating the Python environment lacks PQC KEM support.
    *   **AI Verifiable Outcome:** The returned list has length 1, and the error string contains "current Fava/Python environment does not support PQC KEMs".
*   **Recursive Testing Scope Tags:** `pqc_transit_config_validation`

### TC-DIT-CONFVAL-005: `validate_pqc_tls_embedded_server_options` - Option Not Present
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** `TEST validate_pqc_tls_embedded_server_options passes if pqc_tls_embedded_server_kems is not present`
*   **Unit Under Test (UUT):** `FavaConfigurationValidator.validate_pqc_tls_embedded_server_options` function.
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock dictionary (empty).
    *   `known_supported_pqc_kems_by_python_env`: Mock list.
*   **Preconditions:**
    *   `validate_pqc_tls_embedded_server_options` function implemented.
*   **Test Steps:**
    1.  Create mock `fava_config = {}`.
    2.  Create `known_kems = ["X25519Kyber768"]`.
    3.  Call `validate_pqc_tls_embedded_server_options(fava_config, known_kems)`.
*   **Expected Interactions & Observable Outcome:**
    *   Returns an empty list (no errors).
    *   **AI Verifiable Outcome:** The returned list is empty.
*   **Recursive Testing Scope Tags:** `pqc_transit_config_validation`

---
**Main Application Logic Integration Points** (Conceptual Tests - verifying logging or initialization behavior from [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md#4-main-application-logic-conceptual-integration-points))
---

### TC-DIT-MAIN-001: Fava Initialization Logs Assumed PQC Status from Config
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** `TEST Fava logs assumed PQC status from config during initialization if assume_pqc_tls_proxy_enabled is true`
*   **Unit Under Test (UUT):** Fava's application initialization sequence (`initialize_fava_application` conceptual block).
*   **Collaborators & Mocks:**
    *   `fava_config`: Mock Fava configuration object.
    *   `LoggingSystem`: Mocked logger (e.g., using `unittest.mock.patch` on the relevant logger instance and its methods like `info` or `debug`).
    *   `get_pqc_status_from_config` (internal call): Can be the real function if `fava_config` is well-mocked, or this can be mocked to return a specific string.
*   **Preconditions:**
    *   Fava's initialization logic that calls `get_pqc_status_from_config` and logs its result is implemented.
    *   Logging is configured to be capturable.
*   **Test Steps:**
    1.  Configure mock `fava_config` with `assume_pqc_tls_proxy_enabled = True`.
    2.  (If not mocking `get_pqc_status_from_config` directly) Ensure `get_pqc_status_from_config` would return `"PQC_ASSUMED_ENABLED_VIA_CONFIG"` with this mock config.
    3.  Set up the mocked `LoggingSystem` to capture log messages.
    4.  Trigger the relevant part of Fava's initialization sequence.
*   **Expected Interactions & Observable Outcome:**
    *   `get_pqc_status_from_config` is called with `fava_config`.
    *   The mock `LoggingSystem` captures a log message containing "Initial PQC assumption based on config: PQC_ASSUMED_ENABLED_VIA_CONFIG".
    *   **AI Verifiable Outcome:** A log record is captured by the mock logger that matches the expected level (e.g., INFO) and message pattern.
*   **Recursive Testing Scope Tags:** `pqc_transit_logging`, `pqc_transit_awareness`, `regression_critical`

### TC-DIT-MAIN-002: Fava Request Handling Logs Effective PQC Status (Verbose Logging Enabled)
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** `TEST Effective PQC status is logged for an incoming request if verbose logging is enabled`
*   **Unit Under Test (UUT):** Fava's request handling sequence (`handle_incoming_request` conceptual block).
*   **Collaborators & Mocks:**
    *   `request`: Mock request object (e.g., Flask request context) with mock headers.
    *   `fava_config`: Mock Fava configuration (with `verbose_logging = True`).
    *   `LoggingSystem`: Mocked logger.
    *   `determine_effective_pqc_status` (internal call): Mocked to return a known status (e.g., `"PQC_CONFIRMED_VIA_HEADER"`).
*   **Preconditions:**
    *   Fava's request handling logic that calls `determine_effective_pqc_status` and logs its result (if verbose) is implemented.
*   **Test Steps:**
    1.  Configure mock `fava_config` with `verbose_logging = True`.
    2.  Create a mock `request` object (e.g., with `path="/some/api/endpoint"` and mock headers).
    3.  Mock `determine_effective_pqc_status` to return `"PQC_CONFIRMED_VIA_HEADER"`.
    4.  Set up the mocked `LoggingSystem` to capture log messages.
    5.  Simulate an incoming request to trigger the relevant Fava request handling logic.
*   **Expected Interactions & Observable Outcome:**
    *   `determine_effective_pqc_status` is called with the mock request's headers and the mock config.
    *   The mock `LoggingSystem` captures a log message similar to "Effective PQC status for request to /some/api/endpoint: PQC_CONFIRMED_VIA_HEADER".
    *   **AI Verifiable Outcome:** A log record is captured by the mock logger matching the expected level and message pattern.
*   **Recursive Testing Scope Tags:** `pqc_transit_logging`, `pqc_transit_awareness`

### TC-DIT-MAIN-003: Fava Request Handling Does NOT Log Effective PQC Status (Verbose Logging Disabled)
*   **Target AVER(s):** Contributes to Phase 4.X.B.
*   **Related TDD Anchor(s):** (Implicit: logging only occurs if verbose_logging is true)
*   **Unit Under Test (UUT):** Fava's request handling sequence.
*   **Collaborators & Mocks:**
    *   `request`: Mock request object.
    *   `fava_config`: Mock Fava configuration (with `verbose_logging = False`).
    *   `LoggingSystem`: Mocked logger.
    *   `determine_effective_pqc_status`: Mocked.
*   **Preconditions:**
    *   Fava's request handling logic implemented.
*   **Test Steps:**
    1.  Configure mock `fava_config` with `verbose_logging = False`.
    2.  Create mock `request`.
    3.  Mock `determine_effective_pqc_status` to return any valid status.
    4.  Set up mock `LoggingSystem` to capture log messages.
    5.  Simulate an incoming request.
*   **Expected Interactions & Observable Outcome:**
    *   `determine_effective_pqc_status` IS called (as it might be used for other things, or its result is needed for the conditional log).
    *   The mock `LoggingSystem` does NOT capture the "Effective PQC status..." log message. (Other logs might be present, but not this specific one).
    *   **AI Verifiable Outcome:** The mock logger's records do not contain a message matching the "Effective PQC status..." pattern. The `determine_effective_pqc_status` mock confirms it was called.
*   **Recursive Testing Scope Tags:** `pqc_transit_logging`, `pqc_transit_awareness`

---
This set of test cases covers the primary logic outlined in the pseudocode for PQC Data in Transit. Each test case is designed to be granular, focused on interactions and observable outcomes, and includes AI verifiable completion criteria.