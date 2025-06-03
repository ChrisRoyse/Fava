# High-Level Test Strategy for PQC Integration in Fava

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document outlines the high-level acceptance test strategy for integrating Post-Quantum Cryptography (PQC) into the Fava application. The goal is to ensure that the PQC integration is robust, secure, and does not negatively impact existing Fava functionality. This strategy prioritizes the creation of tests with AI Verifiable End Results (AVERs), enabling automated validation of PQC-enhanced features.

This strategy is based on the project goals outlined in [`docs/Plan.MD`](../../docs/Plan.MD), initial research findings in [`docs/research/final_report/01_executive_summary_PART_1.md`](../../docs/research/final_report/01_executive_summary_PART_1.md), and established best practices for testing cryptographic systems.

## 2. Scope of Testing

### 2.1. In Scope

*   **End-to-End PQC Protection:** Verification of PQC mechanisms for:
    *   Data at Rest (encryption/decryption of Beancount files via the proposed `CryptoService` or PQC-aware GPG).
    *   Data in Transit (HTTPS/TLS security, assuming Fava operates behind a PQC-capable reverse proxy or with a PQC-enabled web server).
    *   Data Integrity (hashing mechanisms using PQC-resistant algorithms).
    *   WASM Module Integrity (verification of PQC digital signatures for `tree-sitter-beancount.wasm`).
*   **Cryptographic Agility:** Testing Fava's ability to switch between different cryptographic algorithms (classical, PQC, hybrid) as configured through the `CryptoService`.
*   **Functional Correctness:** Ensuring core Fava features (e.g., loading reports, displaying data, editing files) operate correctly when PQC mechanisms are active.
*   **Basic System Stability:** Confirming the system remains stable and responsive with PQC integrations.
*   **Adherence to Chosen Standards:** Verifying that PQC implementations use algorithms and parameters aligned with NIST recommendations (e.g., Kyber, Dilithium, SHA3).

### 2.2. Out of Scope (for High-Level Acceptance Tests)

*   **Granular Performance Benchmarking:** Detailed performance analysis of individual PQC algorithms or cryptographic operations (this is better suited for specialized performance tests or research phases). High-level tests will only capture gross performance regressions.
*   **In-depth Cryptanalysis:** Security analysis or cryptanalysis of the underlying PQC algorithms themselves.
*   **Unit/Integration Testing of PQC Libraries:** Testing the correctness of third-party PQC libraries (e.g., liboqs) at a unit level. These are prerequisites.
*   **Exhaustive Security Penetration Testing:** Comprehensive penetration testing beyond the defined PQC security scenarios.

## 3. Test Objectives

The primary objectives of the high-level acceptance testing for PQC integration are:

*   **Verify PQC Effectiveness:** Confirm that the implemented PQC solutions provide the intended security protections for data at rest, in transit, and for software module integrity.
*   **Ensure Functional Equivalence:** Validate that Fava's existing functionalities are not adversely affected by the PQC integration.
*   **Confirm Cryptographic Agility:** Demonstrate that Fava can be configured to use different PQC algorithms (and hybrid modes) and that the system behaves correctly with these configurations.
*   **Validate Adherence to Standards:** Ensure that the PQC algorithms and parameters used are consistent with the project's chosen standards (e.g., NIST PQC selections like Kyber, Dilithium).
*   **Establish Baseline Confidence:** Provide high confidence that the PQC-enhanced Fava application is ready for further, more specialized testing or deployment phases.
*   **Support AI Verification:** Design tests such that their outcomes can be programmatically verified, facilitating automated regression testing and continuous integration.

## 4. Test Types

A combination of test types will be employed:

*   **PQC Functional Tests:**
    *   Description: These tests verify the correct functioning of Fava features that directly utilize PQC algorithms.
    *   Examples: Successfully loading a Beancount file encrypted with a PQC KEM; successfully verifying a PQC-signed WASM module.
*   **Security-Focused Scenario Tests:**
    *   Description: These tests simulate specific security-related scenarios to ensure PQC mechanisms behave as expected under various conditions.
    *   Examples: Testing hybrid mode operations (classical + PQC); attempting to load data encrypted with a mismatched PQC key/algorithm; verifying behavior with known PQC test vectors where applicable at a high level.
*   **Cryptographic Agility Tests:**
    *   Description: These tests confirm Fava's ability to switch between different cryptographic algorithms or configurations.
    *   Examples: Configuring Fava to use PQC_Algorithm_A, performing an operation, reconfiguring to PQC_Algorithm_B, and successfully performing the same operation with data appropriate for Algorithm_B.
*   **Regression Tests:**
    *   Description: Re-running existing Fava high-level tests (or newly defined ones for core Fava features) with PQC enabled to detect any unintended side effects or regressions in non-PQC-related functionality.
*   **Basic Performance Indicator Tests:**
    *   Description: Measuring the time taken for key high-level operations (e.g., Beancount file load time, API response time for a standard query) with PQC enabled versus disabled (or with classical crypto) to identify significant performance degradations. These are not exhaustive benchmarks.
*   **Integrity Verification Tests:**
    *   Description: Specifically testing the PQC-enhanced hashing mechanisms and digital signature verifications.
    *   Examples: Verifying that the hash of a saved file matches a pre-calculated PQC-resistant hash; confirming a PQC signature on a WASM module is correctly validated.

## 5. Test Environment Requirements

*   **PQC Libraries:** A dedicated testing environment with the necessary PQC libraries (e.g., `liboqs` and its Python/JS wrappers) installed and correctly configured.
*   **Fava Configuration:** Ability to configure Fava to use specific PQC algorithms, keys, and operational modes (e.g., via `FavaOptions` and the `CryptoService`).
*   **PQC-Capable Tools:** Access to tools for generating PQC-encrypted test data and PQC-signed artifacts if not handled by Fava itself or test harness scripts (e.g., a PQC-enabled GPG version if testing GPG-based encryption).
*   **Reverse Proxy (for TLS):** If testing PQC in TLS, a PQC-capable reverse proxy (e.g., Nginx with PQC modules) will be needed.
*   **Test Data Injection:** Mechanisms to easily inject PQC-specific test data (encrypted files, signed modules, keys) into the test environment.
*   **Logging and Monitoring:** Adequate logging from Fava and potentially other components (like the reverse proxy) to aid in debugging and verifying test outcomes.

## 6. Test Data

High-quality test data is crucial for effective PQC testing:

*   **PQC Encrypted Beancount Files:**
    *   Sample Beancount files encrypted using selected PQC KEMs (e.g., CRYSTALS-Kyber at various security levels) and hybrid schemes (e.g., Kyber + AES).
    *   Corresponding PQC private keys for decryption.
    *   Files encrypted with incorrect keys or different PQC algorithms to test error handling.
*   **PQC Signed WASM Modules:**
    *   The `tree-sitter-beancount.wasm` module signed with selected PQC digital signature algorithms (e.g., CRYSTALS-Dilithium).
    *   Corresponding PQC public keys for verification.
    *   WASM modules with invalid signatures or signed with different keys to test failure scenarios.
*   **Hashing Test Data:**
    *   Sample data inputs (e.g., file contents) for which PQC-resistant hashes (e.g., SHA3-256, SHAKE256) have been pre-calculated.
*   **Configuration Data:**
    *   Fava configuration files specifying various PQC algorithms and parameters for testing cryptographic agility.
*   **Baseline Data:**
    *   "Clean" (unencrypted/unsigned) versions of test files for comparison and to ensure Fava's core logic processes data correctly after PQC operations.

Test data should be version-controlled and managed alongside test scripts.

## 7. Success Criteria & AI Verifiable End Results (AVERs)

Each high-level acceptance test case will define an action, an expected outcome, and an AI Verifiable End Result (AVER). The AVER must be a concrete, machine-parseable artifact or state that an AI orchestrator or automated test runner can use to determine pass/fail status.

### 7.1. General Principles for AVERs:

*   **Deterministic:** The AVER should be consistent for a given set of inputs and actions.
*   **Machine-Parseable:** Preferably JSON, plain text logs with specific markers, or simple string comparisons (e.g., hashes).
*   **Specific:** Clearly indicates success or failure of the specific aspect being tested.
*   **Minimal:** Contains only the necessary information for verification.

### 7.2. AVERs for PQC Focus Areas:

#### 7.2.1. Data at Rest (Beancount File Encryption/Decryption)

*   **User Story Concept (US1):** As a user, I want to load my Beancount file, which is encrypted using a configured PQC algorithm, so Fava can process my financial data.
*   **Action:** Fava attempts to load a Beancount file encrypted with `PQC_KEM_Algorithm_X`. Fava is configured to use `PQC_KEM_Algorithm_X`.
*   **Expected Outcome (Positive Test):** File loads successfully, data is decrypted correctly, and Fava can process queries on the data.
*   **AVER (Positive Test):**
    1.  A Fava log entry: `INFO: Successfully decrypted 'filename.beancount' using PQC KEM: [Algorithm_X_Name]`.
    2.  A JSON output from a predefined Fava API query (e.g., account balance) on the loaded data, matching a known-good JSON snapshot for that file.
*   **Expected Outcome (Negative Test - Mismatched Algo):** File fails to load, specific error indicating decryption failure.
*   **AVER (Negative Test - Mismatched Algo):**
    1.  A Fava log entry: `ERROR: Failed to decrypt 'filename.beancount'. Configured PQC KEM: [Algorithm_X_Name], file may use different encryption or key.`.

#### 7.2.2. Data in Transit (HTTPS/TLS with PQC)

*   **User Story Concept (US3):** As a Fava user, I want my communication with the Fava server (behind a PQC-TLS proxy) to be secure.
*   **Action:** A test client (e.g., `curl` built with PQC KEM support) makes an API request to the Fava instance operating behind a PQC-TLS enabled reverse proxy.
*   **Expected Outcome:** API call succeeds, data is received correctly.
*   **AVER:**
    1.  HTTP status code `200 OK` from the client.
    2.  The body of the HTTP response matches an expected JSON payload.
    3.  (Optional, if proxy logs are accessible and parseable) Reverse proxy log entry indicating a successful TLS handshake using a specific PQC KEM cipher suite.
    *Note: Direct verification of PQC cipher suite by Fava itself is out of scope if TLS is terminated by a proxy. The test verifies Fava's functionality through such a setup.*

#### 7.2.3. Data Integrity (Hashing)

*   **User Story Concept (US4 - Backend Hashing):** As a Fava system, I want to use a configured PQC-resistant hash (e.g., SHA3-256) for file integrity.
*   **Action:** Fava backend (e.g., during a file save operation or integrity check) calculates a hash of a known data block using the configured PQC-resistant hash algorithm.
*   **Expected Outcome:** The calculated hash matches a pre-computed known-good hash.
*   **AVER:** A JSON object: `{"calculated_hash": "actual_hex_digest", "expected_hash": "precomputed_hex_digest", "algorithm": "SHA3-256", "status": "match/mismatch"}`. The overall test passes if status is "match".
*   **User Story Concept (US5 - Frontend Hashing):** As a Fava user, I want the frontend to use a configured PQC-resistant hash for optimistic concurrency.
*   **Action:** Fava frontend calculates a hash of a known data block (e.g., editor content) using the configured PQC-resistant hash algorithm (via WASM/JS PQC lib).
*   **Expected Outcome:** The calculated hash matches a pre-computed known-good hash.
*   **AVER:** Similar to backend hashing: `{"calculated_hash": "actual_hex_digest", "expected_hash": "precomputed_hex_digest", "algorithm": "SHA3-256", "status": "match/mismatch"}`.

#### 7.2.4. WASM Module Integrity (PQC Digital Signatures)

*   **User Story Concept (US6):** As a Fava user, I want the Fava frontend to verify the PQC signature of the WASM parser before loading.
*   **Action (Positive Test):** Fava frontend attempts to load `tree-sitter-beancount.wasm` which has a valid PQC signature (`PQC_Sig_Algorithm_Y`). Frontend is configured with the correct public key.
*   **Expected Outcome (Positive Test):** WASM module is verified, loaded, and a basic parsing function succeeds.
*   **AVER (Positive Test):**
    1.  A frontend console log message: `INFO: WASM module 'tree-sitter-beancount.wasm' PQC signature verified successfully using [Algorithm_Y_Name].`.
    2.  Output of a simple, predefined parsing task using the loaded WASM, matching an expected output string/structure.
*   **Action (Negative Test - Invalid Signature):** Frontend attempts to load a WASM module with an invalid PQC signature.
*   **Expected Outcome (Negative Test):** WASM module verification fails, module is not loaded, error is reported.
*   **AVER (Negative Test):**
    1.  A frontend console log message: `ERROR: WASM module 'tree-sitter-beancount.wasm' PQC signature verification failed. Module not loaded.`.

#### 7.2.5. Cryptographic Agility

*   **User Story Concept (US7 - Hashing Agility):** As an admin, I want to switch Fava's hashing algorithm, and have it take effect.
*   **Action:**
    1.  Configure Fava to use `PQC_Hash_Algorithm_1` (e.g., SHA3-256). Perform a hashing operation (see 7.2.3).
    2.  Reconfigure Fava to use `PQC_Hash_Algorithm_2` (e.g., SHAKE256 if supported). Perform the same hashing operation on the same data.
*   **Expected Outcome:** Both hashing operations succeed, producing the correct hash for the respectively configured algorithm.
*   **AVER:** Two AVERs from 7.2.3, one for each configured algorithm, both showing "match" status, and confirming the algorithm used in the `algorithm` field.
*   **User Story Concept (US8 - KEM Agility):** As an admin, I want to switch Fava's PQC KEM for file decryption.
*   **Action:**
    1.  Prepare `file_A.beancount` encrypted with `PQC_KEM_1` and `file_B.beancount` encrypted with `PQC_KEM_2`.
    2.  Configure Fava for `PQC_KEM_1`. Attempt to load `file_A` (expected success) and `file_B` (expected failure).
    3.  Reconfigure Fava for `PQC_KEM_2`. Attempt to load `file_B` (expected success) and `file_A` (expected failure).
*   **Expected Outcome:** Decryption succeeds only when the configured KEM matches the file's encryption KEM.
*   **AVER:** A series of AVERs from 7.2.1:
    *   For `PQC_KEM_1` config: Positive AVER for `file_A`, Negative AVER for `file_B`.
    *   For `PQC_KEM_2` config: Positive AVER for `file_B`, Negative AVER for `file_A`.

## 8. Risks and Mitigation

| Risk                                      | Mitigation Strategy                                                                                                                               |
| :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PQC Library Instability/Bugs**          | Use stable, well-tested versions of PQC libraries. Isolate cryptographic operations within the `CryptoService` abstraction to limit impact.        |
| **Performance Bottlenecks**               | Include basic performance indicators in high-level tests. Defer deep optimization but flag gross regressions for further investigation.             |
| **Immature PQC Tooling**                  | Develop helper scripts/tools for test data generation if needed. Rely on core libraries like `liboqs` for generating PQC artifacts.                   |
| **Complexity of Test Setup**              | Automate test environment setup as much as possible. Provide clear documentation for manual steps. Use containerization if feasible.                |
| **Evolving PQC Standards**                | Design tests to primarily validate the `CryptoService` abstraction and its agility. Focus on currently NIST-recommended algorithms.                 |
| **Difficulty in Generating Test Vectors** | Leverage existing test vectors from PQC library providers or NIST. For end-to-end tests, generate data using the chosen PQC libraries themselves. |
| **AI Verifiability Challenges**           | Keep AVERs simple and deterministic. If complex state verification is needed, output a simplified, summary status that is easily parseable.         |

## 9. Relationship to Lower-Level Tests

This high-level acceptance test strategy complements, and relies upon, lower-level testing activities:

*   **Unit Tests:** Will focus on individual components, such as specific methods within `CryptoService` implementations (e.g., `KyberKEMService.encrypt_key()`, `DilithiumSignatureService.sign_data()`), ensuring they work correctly in isolation with known test vectors.
*   **Integration Tests:** Will verify the interactions between Fava's core logic and the `CryptoService` (e.g., ensuring `FavaLedger` correctly calls the decryption methods of the configured service) and interactions between frontend and backend PQC components.

High-level acceptance tests assume that the core PQC primitives and their direct integrations (covered by unit/integration tests) are functioning correctly. These acceptance tests then verify that the complete, end-to-end user-facing scenarios involving PQC are successful and meet business requirements.

## 10. Adherence to Principles of Good High-Level Testing

This strategy aims to embody the following principles:

*   **User-Centric:** Tests are designed around user stories and Fava's core functionalities as experienced by a user.
*   **End-to-End:** Tests cover complete operational flows involving PQC.
*   **Independent & Repeatable:** Test cases should be designed to be runnable independently and produce consistent results.
*   **Understandable:** Test objectives, actions, and expected outcomes (including AVERs) are clearly defined.
*   **Maintainable:** By focusing on stable interfaces (Fava's features, `CryptoService` API) and using well-defined test data.
*   **Reliable:** AVERs provide clear, unambiguous pass/fail conditions.
*   **AI-Verifiable:** AVERs are structured for machine parsing and automated validation.
*   **Real Data/Scenarios:** Tests will use realistic (though potentially simplified for testing) Beancount files and simulate common user interactions.
*   **Launch Readiness:** A successful pass of this test suite will provide high confidence in the PQC integration's readiness.
*   **Comprehensive Coverage:** Addresses all key PQC focus areas identified in [`docs/Plan.MD`](../../docs/Plan.MD).

This strategy will guide the `tester-acceptance-plan-writer` in creating a detailed master acceptance test plan and the specific high-level test cases.