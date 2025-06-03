# Master Acceptance Test Plan for PQC Integration in Fava

**Version:** 1.1
**Date:** 2025-06-02
**Project:** Fava PQC Integration
**Prepared by:** AI Test Specialist (Roo)

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on updated v1.1 PQC specifications and Devil's Advocate critique ([`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](../../docs/devil/PQC_SPARC_Specification_Phase_Critique.md)). Key changes include:
    *   Alignment with revised functional requirements (e.g., Fava-driven PQC encryption for Data at Rest).
    *   Enhanced strategy for verifying updated, more concrete Performance NFRs using Basic Performance Indicator Tests.
    *   Significant expansion of the Test Data generation section (6.2) detailing processes, tools (`oqs-python`, `liboqs` CLI), and risk assessment for PQC-specific test artifacts.
    *   General updates to ensure clarity and robustness of the testing framework.
*   **1.0 (2025-06-02):** Initial version.

## Table of Contents
1.  [Introduction](#1-introduction)
    1.1. [Purpose](#11-purpose)
    1.2. [Project Overview](#12-project-overview)
2.  [Overall Testing Approach](#2-overall-testing-approach)
    2.1. [Guiding Principles](#21-guiding-principles)
    2.2. [Test Types](#22-test-types)
3.  [Scope of Acceptance Testing](#3-scope-of-acceptance-testing)
    3.1. [In Scope](#31-in-scope)
    3.2. [Out of Scope](#32-out-of-scope)
4.  [Roles and Responsibilities](#4-roles-and-responsibilities)
5.  [Test Schedule and Milestones (High-Level)](#5-test-schedule-and-milestones-high-level)
6.  [Test Environment and Data Requirements](#6-test-environment-and-data-requirements)
    6.1. [Test Environment](#61-test-environment)
    6.2. [Test Data Generation and Management](#62-test-data-generation-and-management)
7.  [Entry and Exit Criteria](#7-entry-and-exit-criteria)
    7.1. [Entry Criteria](#71-entry-criteria)
    7.2. [Exit Criteria](#72-exit-criteria)
8.  [Test Deliverables](#8-test-deliverables)
9.  [AI Verifiable End Results (AVERs) Implementation and Tracking](#9-ai-verifiable-end-results-avers-implementation-and-tracking)
    9.1. [Definition and Principles](#91-definition-and-principles)
    9.2. [Implementation in Test Cases](#92-implementation-in-test-cases)
    9.3. [Tracking and Verification](#93-tracking-and-verification)
10. [Reporting and Communication Plan](#10-reporting-and-communication-plan)
11. [Risks and Mitigation](#11-risks-and-mitigation)

---

## 1. Introduction

### 1.1. Purpose
This Master Acceptance Test Plan (MATP) outlines the strategy, scope, resources, and schedule for conducting high-level end-to-end acceptance testing for the Post-Quantum Cryptography (PQC) integration into the Fava application. The primary goal of this acceptance testing phase is to verify that the PQC-enhanced Fava application meets the specified requirements (Version 1.1 of PQC Specification Documents in [`docs/specifications/`](../../docs/specifications/)), functions as expected from a user and system integration perspective, and achieves the overall project goal of protecting data against quantum threats.

This plan has been revised to incorporate feedback from the Devil's Advocate critique ([`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](../../docs/devil/PQC_SPARC_Specification_Phase_Critique.md)) and to align with the updated PQC specifications (v1.1). It builds upon the findings and strategies outlined in the [`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md).

### 1.2. Project Overview
The project aims to integrate PQC into Fava, focusing on key areas as defined in the v1.1 specifications:
*   Data at Rest (Fava-driven PQC hybrid encryption/decryption of Beancount files, GPG backward compatibility)
*   Data in Transit (HTTPS/TLS communication via PQC-capable reverse proxy)
*   Data Integrity (hashing mechanisms using SHA3-256 by default)
*   WASM Module Integrity (PQC digital signatures like Dilithium3 for `tree-sitter-beancount.wasm`)
*   Cryptographic Agility (ability to switch algorithms and manage multiple decryption schemes)

The successful completion of acceptance testing, as defined by this plan, will signify that Fava's PQC integration meets the ultimate success criteria from a user's perspective.

## 2. Overall Testing Approach

### 2.1. Guiding Principles
The acceptance testing approach will adhere to the following principles:
*   **User-Centric:** Tests will simulate real-world user scenarios and system interactions.
*   **End-to-End:** Focus on complete workflows and system integration.
*   **AI Verifiability:** All test cases will include an AI Verifiable End Result (AVER) to enable automated or semi-automated validation.
*   **Risk-Based:** Prioritize testing based on the criticality and risk associated with PQC focus areas.
*   **Specification-Driven:** Test cases will be directly derived from the v1.1 PQC specification documents ([`docs/specifications/`](../../docs/specifications/)) and the [`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md).
*   **London School TDD Influence:** While these are high-level acceptance tests, the focus remains on behavior and outcomes, aligning with TDD principles.

### 2.2. Test Types
The following types of tests will be employed, as detailed in the [`docs/research/PQC_High_Level_Test_Strategy.md#4-test-types`](../../docs/research/PQC_High_Level_Test_Strategy.md#4-test-types):
*   PQC Functional Tests
*   Security-Focused Scenario Tests
*   Cryptographic Agility Tests
*   Regression Tests (for core Fava functionality with PQC enabled)
*   **Basic Performance Indicator Tests:** These tests will execute key operations under PQC load (e.g., decrypting a large PQC-encrypted file, hashing significant data with SHA3-256, PQC-verifying WASM). While not exhaustive benchmarks, they aim to capture timing information (e.g., via logged durations). The AI Verifiable End Result (AVER) for these tests will confirm the operation's success and the presence of logged performance data. This data will then be compared against the more concrete performance NFRs defined in the v1.1 specification documents (e.g., [`docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32`](../../docs/specifications/PQC_Data_At_Rest_Spec.md#nfr32)) to ensure performance is within acceptable ballpark ranges.
*   Integrity Verification Tests

## 3. Scope of Acceptance Testing

### 3.1. In Scope
As defined in [`docs/research/PQC_High_Level_Test_Strategy.md#21-in-scope`](../../docs/research/PQC_High_Level_Test_Strategy.md#21-in-scope) and updated for v1.1 specifications:
*   **End-to-End PQC Protection:**
    *   Data at Rest: Verification of Fava-driven encryption/decryption of Beancount files using the `CryptoService` (e.g., X25519+Kyber-768+AES-256-GCM hybrid). Verification of backward compatibility with classical GPG.
    *   Data in Transit: Verification of HTTPS/TLS security with Fava operating behind a PQC-capable reverse proxy (e.g., X25519Kyber768 for TLS KEM).
    *   Data Integrity: Verification of hashing mechanisms using PQC-resistant algorithms (e.g., SHA3-256).
    *   WASM Module Integrity: Verification of PQC digital signatures (e.g., Dilithium3) for `tree-sitter-beancount.wasm`.
*   **Cryptographic Agility:** Testing Fava's ability to switch between different cryptographic algorithms and to decrypt files encrypted with known legacy PQC schemes.
*   **Functional Correctness:** Ensuring core Fava features operate correctly when PQC mechanisms are active.
*   **Basic System Stability:** Confirming system stability with PQC integrations.
*   **Adherence to Chosen Standards:** Verifying PQC implementations use algorithms aligned with NIST recommendations (Kyber, Dilithium, SHA3).
*   **Verification of Performance NFRs (High-Level):** Confirming that basic performance indicators for key operations fall within the acceptable ranges defined in the v1.1 NFRs.

### 3.2. Out of Scope
As defined in [`docs/research/PQC_High_Level_Test_Strategy.md#22-out-of-scope-for-high-level-acceptance-tests`](../../docs/research/PQC_High_Level_Test_Strategy.md#22-out-of-scope-for-high-level-acceptance-tests):
*   Granular performance benchmarking of PQC algorithms (beyond the Basic Performance Indicator Tests).
*   In-depth cryptanalysis of PQC algorithms.
*   Unit/integration testing of third-party PQC libraries.
*   Exhaustive security penetration testing beyond defined PQC scenarios.

## 4. Roles and Responsibilities
*   **Test Lead / Orchestrator:** Responsible for overall test planning, coordination, execution oversight, and reporting. Ensures adherence to this plan.
*   **Test Engineers / AI Agent (acting as tester):** Responsible for designing, developing (if scriptable), executing acceptance tests, and documenting results. Verifies AVERs.
*   **Development Team:** Responsible for providing testable builds, fixing defects identified during testing, and providing technical support for test environment setup and PQC configurations.
*   **Product Owner / Stakeholders:** Responsible for reviewing and approving the MATP, test cases, and final acceptance report. Provides clarification on requirements.

## 5. Test Schedule and Milestones (High-Level)
The acceptance testing will be conducted in phases:

1.  **Phase 1: Test Planning & Design (Current Revision)**
    *   Deliverable: This Master Acceptance Test Plan (v1.1), High-Level Acceptance Test Cases (v1.1).
    *   Timeline: TBD (dependent on project start)
2.  **Phase 2: Test Environment Setup & Validation**
    *   Deliverable: Fully configured and validated test environment, including PQC libraries, tools, and generated test data.
    *   Timeline: TBD (following development milestones for PQC features)
3.  **Phase 3: Test Execution**
    *   Deliverable: Executed test cases, logged defects, interim status reports (including performance indicator data).
    *   Timeline: TBD (following environment setup)
4.  **Phase 4: Test Reporting & Closure**
    *   Deliverable: Final Acceptance Test Summary Report, sign-off.
    *   Timeline: TBD (following test execution and defect resolution)

Detailed timelines will be aligned with the overall project plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)).

## 6. Test Environment and Data Requirements

### 6.1. Test Environment
As outlined in [`docs/research/PQC_High_Level_Test_Strategy.md#5-test-environment-requirements`](../../docs/research/PQC_High_Level_Test_Strategy.md#5-test-environment-requirements) and updated:
*   Dedicated testing environment with necessary PQC libraries (e.g., `oqs-python` wrapping `liboqs`, `liboqs-js`) installed and configured.
*   Fava application builds with PQC features integrated.
*   Ability to configure Fava (`FavaOptions`, `CryptoService`) for various PQC algorithms (Kyber, Dilithium, SHA3) and modes.
*   Tools and scripts for generating PQC test data (see section 6.2).
*   PQC-capable reverse proxy (e.g., Nginx with OQS OpenSSL configured for X25519Kyber768) for Data in Transit testing.
*   Mechanisms for test data injection and configuration management.
*   Adequate logging (from Fava, test harness, proxy) and monitoring capabilities, including capturing performance indicators.

### 6.2. Test Data Generation and Management
This section addresses Critique 3.7 from [`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](../../docs/devil/PQC_SPARC_Specification_Phase_Critique.md) by detailing the strategy for generating PQC-specific test data.

**Overall Strategy:**
Test data generation will primarily leverage `oqs-python` (for backend-related data like encrypted files) and `liboqs` command-line interface (CLI) tools or `oqs-python` scripts (for signing WASM modules). Helper scripts will be developed to automate and standardize the creation of these artifacts. All test data and generation scripts will be version-controlled.

**Specific Test Data Artifacts and Generation Process:**

1.  **PQC-Hybrid Encrypted Beancount Files (Data at Rest):**
    *   **Purpose:** For testing Fava-driven PQC hybrid encryption/decryption (e.g., X25519 + Kyber-768 + AES-256-GCM).
    *   **Tooling:** Python scripts utilizing `oqs-python` for Kyber KEM operations and the `cryptography` library for X25519 and AES-256-GCM.
    *   **Process:**
        *   A script will take a plaintext Beancount file and a known key (or derive one from a passphrase) as input.
        *   It will perform the hybrid encryption:
            1.  Generate/load X25519 key pair.
            2.  Generate/load Kyber-768 key pair.
            3.  Generate a symmetric key (e.g., for AES-256-GCM).
            4.  Encapsulate the symmetric key using X25519 (classical KEM ciphertext).
            5.  Encapsulate the symmetric key using Kyber-768 (PQC KEM ciphertext).
            6.  Combine KEM ciphertexts and potentially other metadata (IV, algorithm identifiers).
            7.  Encrypt the Beancount file content using the symmetric key with AES-256-GCM, producing the final ciphertext and AEAD tag.
            8.  Store the combined KEM ciphertexts, IV, AEAD tag, and main ciphertext in a defined bundle format (as per [`docs/specifications/PQC_Data_At_Rest_Spec.md#82-encrypted-file-metadata-conceptual-for-fava-pqc-hybrid-encrypted-files`](../../docs/specifications/PQC_Data_At_Rest_Spec.md#82-encrypted-file-metadata-conceptual-for-fava-pqc-hybrid-encrypted-files)).
    *   **Variations:**
        *   **Corrupted Files:** After valid encryption, programmatically alter bytes in the KEM ciphertexts, symmetric ciphertext, or AEAD tag.
        *   **Mismatched Keys:** Use a different private key for decryption than was used for encryption (or derived from a different passphrase).
        *   **Different Algorithms:** Generate files encrypted with different (but supported) PQC KEMs or hybrid suite configurations for agility testing.

2.  **PQC Signed WASM Modules (WASM Integrity):**
    *   **Purpose:** For testing PQC signature verification of `tree-sitter-beancount.wasm` (e.g., using Dilithium3).
    *   **Tooling:** Python scripts using `oqs-python` for Dilithium3 signing, or `liboqs` CLI signing utilities (e.g., `oqs_sig_tool` if available and suitable, as mentioned in `pf_pqc_cli_signing_tools_g4_3_PART_1.md`).
    *   **Process:**
        1.  A script will take the `tree-sitter-beancount.wasm` file and a known Dilithium3 private key as input.
        2.  It will generate a PQC signature for the WASM file.
        3.  The signature will be saved to a separate file (e.g., `tree-sitter-beancount.wasm.dilithium3.sig`).
        4.  The corresponding Dilithium3 public key will be extracted and stored (e.g., Base64 encoded) for embedding in the frontend.
    *   **Variations:**
        *   **Invalid Signatures:** Sign with a different private key; tamper with the WASM file after signing; tamper with the signature file itself.

3.  **Hashing Test Data (Data Integrity):**
    *   **Purpose:** For testing PQC-resistant hashing (e.g., SHA3-256).
    *   **Tooling:** Python scripts using `hashlib` (for SHA3-256 if Python >= 3.6) or `pysha3`.
    *   **Process:**
        1.  Take sample data blocks (text, binary) as input.
        2.  Calculate their SHA3-256 (and SHA-256 for agility tests) hashes.
        3.  Store these pre-calculated hashes for comparison in tests.

4.  **Configuration Data:** Fava configuration files (`FavaOptions`) tailored for specific test scenarios (e.g., enabling specific PQC algorithms, setting key paths).

5.  **Baseline Data:** Unencrypted/unsigned versions of test files for comparison and ensuring core logic correctness.

**Test Data Management and Risks:**
*   **Version Control:** All test data generation scripts, generated test data artifacts (where feasible, or clear instructions for generation), and known keys will be stored in version control.
*   **Key Management:** A dedicated set of test keys (PQC KEM keys, PQC signature keys, GPG keys) will be generated and managed securely for testing purposes only. These keys should not be production keys.
*   **Risks & Mitigations for Test Data Generation:**
    *   **Tooling Immaturity/Bugs (`liboqs`, `oqs-python`):**
        *   *Risk:* Test data might be generated incorrectly due to bugs in underlying PQC libraries.
        *   *Mitigation:* Use latest stable library versions. Cross-verify generated artifacts with examples from library documentation if possible. Develop simple, focused generation scripts.
    *   **Complexity of Hybrid Schemes:**
        *   *Risk:* Incorrect implementation of the hybrid encryption logic in generation scripts.
        *   *Mitigation:* Follow documented hybrid scheme constructions (e.g., from IETF drafts or `liboqs` examples). Ensure KDF usage and secret concatenation are correct.
    *   **Consistency:**
        *   *Risk:* Subtle differences between test data generation and Fava's PQC implementation leading to false positives/negatives.
        *   *Mitigation:* Use the same PQC libraries (`oqs-python`) in both test data generation and Fava where possible. Thoroughly review and test generation scripts.
    *   **Resource Intensive:**
        *   *Risk:* Generating a large corpus of diverse test data can be time-consuming.
        *   *Mitigation:* Prioritize essential test data. Automate generation fully.

This detailed approach to test data generation aims to provide a robust foundation for acceptance testing, directly addressing the concerns raised in Critique 3.7.

## 7. Entry and Exit Criteria

### 7.1. Entry Criteria
Acceptance testing will commence when the following criteria are met:
1.  All PQC features, as defined in the v1.1 specification documents, are code-complete and unit/integration tested by the development team.
2.  A stable build of Fava with PQC integration is deployed to the designated test environment.
3.  The test environment is fully set up, configured, and validated as per section 6.1.
4.  All required test data (section 6.2) is generated, validated, and available.
5.  This Master Acceptance Test Plan (v1.1) and the detailed high-level acceptance test cases (v1.1) are reviewed and approved.
6.  Necessary PQC libraries and tools are installed and functional in the test environment.
7.  Key personnel (testers, developers for support) are available.

### 7.2. Exit Criteria
Acceptance testing will be considered complete when the following criteria are met:
1.  All defined high-level acceptance test cases have been executed.
2.  100% of High priority test cases have passed.
3.  At least 95% of Medium priority test cases have passed.
4.  No outstanding Critical or High severity defects related to PQC functionality.
5.  All Medium severity defects have a documented resolution plan or are accepted by stakeholders.
6.  Basic performance indicators for key operations are confirmed to be within the acceptable NFR ranges, or deviations are documented and accepted.
7.  The Final Acceptance Test Summary Report is completed, reviewed, and approved by stakeholders.
8.  All AVERs for passed tests have been successfully verified.

## 8. Test Deliverables
The following deliverables will be produced as part of the acceptance testing phase:
1.  **Master Acceptance Test Plan (this document, v1.1):** [`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](./PQC_Master_Acceptance_Test_Plan.md)
2.  **High-Level Acceptance Test Cases (v1.1):** Located in [`tests/acceptance/`](../../../tests/acceptance/), covering each PQC focus area.
    *   [`tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Hashing_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Hashing_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md`](../../../tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md)
3.  **Test Data and Generation Scripts:** Stored in a designated, version-controlled location.
4.  **Test Execution Logs:** Detailed logs of test execution, including AVER outputs and captured performance indicators.
5.  **Defect Reports:** Documented in a designated defect tracking system.
6.  **Interim Test Status Reports:** Provided as per the communication plan (section 10).
7.  **Final Acceptance Test Summary Report:** A comprehensive report summarizing test activities, results, defect status, performance NFR verification status, and overall assessment of PQC integration readiness.

## 9. AI Verifiable End Results (AVERs) Implementation and Tracking

### 9.1. Definition and Principles
An AI Verifiable End Result (AVER) is a concrete, machine-parseable artifact or system state that allows an AI orchestrator or automated test runner to determine the pass/fail status of a test case. AVERs will adhere to the principles outlined in [`docs/research/PQC_High_Level_Test_Strategy.md#71-general-principles-for-avers`](../../docs/research/PQC_High_Level_Test_Strategy.md#71-general-principles-for-avers):
*   **Deterministic:** Consistent for given inputs/actions.
*   **Machine-Parseable:** JSON, specific log patterns, simple string comparisons (e.g., hashes).
*   **Specific:** Clearly indicates success/failure of the tested aspect.
*   **Minimal:** Contains only necessary information for verification.

### 9.2. Implementation in Test Cases
Each high-level acceptance test case document (v1.1) within [`tests/acceptance/`](../../../tests/acceptance/) will explicitly define an "AI Verifiable End Result (AVER)" section. This section will describe the precise condition, output, or state to be checked. Examples include:
*   Specific log messages (e.g., `INFO: Successfully decrypted 'file.pqc_hybrid' using PQC Hybrid Suite: FAVA_HYBRID_X25519_MLKEM768_AES256GCM`).
*   JSON output from an API call matching a known-good snapshot or schema.
*   File content hash matching a pre-calculated value.
*   Presence of specific log messages containing performance data (e.g., `INFO: Operation X completed in YYYms`). The AI verifies the log's presence and format; a separate process compares YYY against NFRs.
*   Specific HTTP status codes and response body characteristics.

### 9.3. Tracking and Verification
*   During test execution, the actual outcomes corresponding to AVERs will be captured (e.g., log snippets, API responses, calculated hashes, performance indicator logs).
*   These captured outcomes will be compared against the defined AVERs.
*   An AI agent or test execution script can perform this comparison.
*   Test execution logs will record both the expected AVER and the actual outcome, along with the pass/fail status based on their comparison.

## 10. Reporting and Communication Plan
*   **Defect Tracking:** All defects found during acceptance testing will be logged in a designated defect tracking system with appropriate severity, priority, and steps to reproduce.
*   **Regular Status Updates:** The Test Lead will provide regular (e.g., daily or bi-weekly) status updates to stakeholders, including:
    *   Number of tests executed, passed, failed, blocked.
    *   New defects raised, defect resolution status.
    *   Status of performance indicator collection and comparison against NFRs.
    *   Any risks or issues impacting testing.
*   **Test Phase Completion Reports:** A summary report will be provided at the end of each major test execution cycle.
*   **Final Acceptance Test Summary Report:** Upon completion of all acceptance testing, a comprehensive report will be delivered, detailing the overall results, outstanding defects (if any), and a recommendation for go/no-go.

Communication channels will include regular meetings, email updates, and the defect tracking system.

## 11. Risks and Mitigation
Key risks and mitigation strategies are adapted from [`docs/research/PQC_High_Level_Test_Strategy.md#8-risks-and-mitigation`](../../docs/research/PQC_High_Level_Test_Strategy.md#8-risks-and-mitigation) and updated:

| Risk                                      | Mitigation Strategy                                                                                                                               |
| :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PQC Library Instability/Bugs**          | Use stable, well-tested versions (`oqs-python`, `liboqs-js`). Isolate crypto operations via `CryptoService`. Intensive unit/integration testing by dev team prior to UAT.        |
| **Performance Bottlenecks**               | Basic performance indicators in acceptance tests will be compared against NFR targets. Flag operations outside NFRs. Defer deep optimization but ensure usability and high-level NFR adherence.                             |
| **Immature PQC Tooling for Test Data**    | Develop robust helper scripts using `oqs-python` and `liboqs` CLI tools for test data generation (PQC encryption, PQC signatures). Allocate specific time for test data creation and validation. Document generation process thoroughly. Address via expanded Section 6.2. |
| **Complexity of Test Setup/Environment**  | Automate environment setup where possible. Detailed setup documentation. Containerization (e.g., Docker) for consistency.                           |
| **Evolving PQC Standards**                | Focus tests on `CryptoService` abstraction and agility. Prioritize currently NIST-recommended algorithms (Kyber, Dilithium, SHA3). Design tests to be adaptable.             |
| **Difficulty in Generating Test Vectors** | Leverage existing vectors from PQC libraries/NIST. Generate end-to-end test data using the chosen PQC libraries and defined processes in Section 6.2.                                      |
| **AI Verifiability Challenges**           | Keep AVERs simple, deterministic, and machine-parseable. Use structured log outputs or API responses. Develop parsing scripts for AVER verification. For performance, verify log presence/format, separate NFR comparison. |
| **Resource Unavailability**               | Identify backup resources. Clear scheduling and communication.                                                                                      |
| **Scope Creep**                           | Adhere strictly to the defined scope in this MATP (v1.1). Manage changes through a formal change request process.                                        |

This Master Acceptance Test Plan provides the framework for ensuring the PQC integration in Fava is thoroughly validated against user and system requirements (v1.1), ultimately confirming its readiness and effectiveness.