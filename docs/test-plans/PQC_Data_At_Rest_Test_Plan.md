# Granular Test Plan: PQC Data at Rest

**Version:** 1.0
**Date:** 2025-06-02
**Feature:** PQC Data at Rest
**Based on:**
*   Specification: [`docs/specifications/PQC_Data_At_Rest_Spec.md`](../specifications/PQC_Data_At_Rest_Spec.md) (v1.1)
*   Pseudocode: [`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](../pseudocode/PQC_Data_At_Rest_Pseudo.md) (v1.0)
*   Architecture: [`docs/architecture/PQC_Data_At_Rest_Arch.md`](../architecture/PQC_Data_At_Rest_Arch.md) (v1.0)
*   Project Master Plan: [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md) (v1.1)

## 1. Introduction

This document outlines the granular test plan for the "PQC Data at Rest" feature in Fava. The primary goal of this feature is to enable quantum-resistant encryption and decryption of Beancount files, while maintaining backward compatibility with existing GPG-encrypted files.

This test plan adheres to London School of TDD principles, emphasizing interaction-based testing and mocking of collaborators to verify observable outcomes. It also defines a recursive testing strategy to ensure ongoing stability and catch regressions. All tasks and criteria within this plan are designed to be AI verifiable.

**AI Verifiable Completion Criterion for this Document:** This test plan document ([`docs/test-plans/PQC_Data_At_Rest_Test_Plan.md`](docs/test-plans/PQC_Data_At_Rest_Test_Plan.md)) is created, reviewed, and its content aligns with the requirements outlined in the "Spec-To-TestPlan Converter" mode's objective.

## 2. Test Scope

This test plan covers the granular testing of components and interactions related to the "PQC Data at Rest" feature. The scope is to verify the successful implementation of logic detailed in the pseudocode and architecture, ensuring it meets the functional and non-functional requirements from the specification.

Specifically, these tests aim to provide evidence for the following AI Verifiable End Results (AVERs) from the [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md):

*   **Phase 2, Task 2.1 (Pseudocode for PQC Data at Rest):** Verification that the implemented code correctly reflects the logic for:
    *   Fava-driven PQC hybrid encryption/decryption (X25519+Kyber-768 KEMs with AES-256-GCM).
    *   Key handling (passphrase derivation with Argon2id + HKDF, external key file loading, key export security as per ADR-005 in architecture).
    *   Interaction with classical GPG for backward compatibility.
    *   Error conditions and reporting.
    *   `EncryptedFileBundle` data format handling.
*   **Phase 4, Task 4.X.A (Granular Test Specification & Generation for Data at Rest):** The creation of this test plan and the subsequent generation of test code based on it.
    *   AVER: "Granular test plan document exists. Test code file exists, containing stubs for tests covering key functionalities, edge cases, and error conditions derived from pseudocode/spec. Tests are runnable and initially failing or skipped (TDD)."
*   **Phase 4, Task 4.X.B (Feature Implementation & Iteration (TDD) for Data at Rest):** Ensuring all granular tests defined herein pass upon feature implementation.
    *   AVER: "All granular tests defined in 4.X.A for the specific feature/sub-feature pass."
*   **Phase 4, Task 4.X.C (Module-Level Review & Refinement for Data at Rest):** Ensuring all granular tests continue to pass after reviews and refinements. Some tests will act as basic performance indicators.
    *   AVER: "...All granular tests for the feature still pass. Basic Performance Indicator Tests for the module align with NFRs in v1.1 specs."

**Out of Scope for this Granular Test Plan:**
*   Full end-to-end UI testing (covered by acceptance tests).
*   Exhaustive PQC algorithm cryptographic validation (relies on underlying libraries).
*   Full performance benchmark testing (covered in Phase 5, though basic checks are included).

**AI Verifiable Completion Criterion for Test Scope:** This section accurately lists the targeted AVERs and defines clear boundaries for the granular tests.

## 3. Test Strategy

### 3.1. London School of TDD

This test plan adopts the London School of Test-Driven Development. Our tests will focus on the *behavior* of software units (modules/classes) by verifying the *interactions* they have with their collaborators. Collaborators will be mocked or stubbed to isolate the unit under test and ensure deterministic test outcomes.

*   **Focus on Observable Outcomes:** Tests will assert the observable outcomes of a unit's operation, such as return values, exceptions raised, or calls made to its collaborators. Internal state verification will be minimized.
*   **Mocking Collaborators:** Dependencies like cryptographic libraries (`oqs-python`, `cryptography`), file system operations, or other Fava services (`FavaOptions`) will be replaced with mocks during testing. This allows us to:
    *   Define expected interactions (e.g., `mock_kyber_encapsulate` was called with specific public key).
    *   Simulate various scenarios, including error conditions from collaborators.
    *   Avoid reliance on external systems or complex setup.
*   **Test-Driven Development:** Test cases defined in this plan will be implemented *before* the feature code, guiding the development process.

**AI Verifiable Completion Criterion for London School TDD Strategy:** This subsection clearly explains the principles of interaction-based testing and mocking as they will be applied.

### 3.2. Recursive Testing (Regression Strategy)

A comprehensive recursive (regression) testing strategy is crucial for maintaining stability as the "PQC Data at Rest" feature is developed and integrated, and as Fava evolves.

*   **Triggers for Re-running Test Subsets:**
    1.  **Code Changes:** Any modification within the `fava.crypto_service` (or equivalent module for PQC Data at Rest), `FavaLedger` related to file encryption/decryption, or key management logic.
    2.  **Configuration Changes:** Modifications to Fava's PQC configuration options structure or default values.
    3.  **Dependency Updates:** Updates to core cryptographic libraries (`oqs-python`, `cryptography`) or GPG versions.
    4.  **Pre-Commit Hooks:** A subset of fast-running, critical path tests executed locally before committing code.
    5.  **Pull Request (PR) Builds:** Full granular test suite for "PQC Data at Rest" executed in CI upon PR creation/update.
    6.  **Nightly/Scheduled Builds:** Full granular test suite executed regularly on the main development branch.
    7.  **Pre-Release:** Full granular test suite executed as part of the release process.

*   **Test Prioritization and Tagging:** Tests will be tagged to allow for selective execution:
    *   `@critical_path`: Core successful encryption and decryption flows (PQC Hybrid & GPG).
    *   `@error_handling`: Failure scenarios (e.g., incorrect key, corrupted data, missing dependencies).
    *   `@config_dependent`: Tests verifying behavior with different PQC suite configurations, key management modes.
    *   `@key_management`: Specific tests for key derivation (passphrase, external file), salt handling, and secure key export.
    *   `@bundle_format`: Tests for `EncryptedFileBundle` parsing and construction.
    *   `@gpg_compatibility`: Tests specifically for GPG decryption fallback.
    *   `@performance_smoke`: Quick checks to ensure PQC operations are not excessively slow (not full benchmarks).
    *   `@security_sensitive`: Tests related to particularly sensitive operations like key export.

*   **Test Subset Selection for Regression:**
    1.  **Local Development (Pre-commit):** Run `@critical_path` tests and tests related to the specific modules/files being changed by the developer.
        *   *AI Verifiable Criterion:* Pre-commit hook configuration exists and references the specified test tags/paths.
    2.  **CI on Pull Requests:** Run all tests tagged for "PQC Data at Rest" (all tags listed above except potentially very slow performance ones if separated).
        *   *AI Verifiable Criterion:* CI pipeline configuration (e.g., GitHub Actions workflow file) exists and specifies the execution of the full PQC Data at Rest granular test suite.
    3.  **Nightly/Scheduled Builds:** Run the complete "PQC Data at Rest" granular test suite.
        *   *AI Verifiable Criterion:* Scheduled CI job configuration exists for running the full suite.
    4.  **Pre-Release Builds:** Run the complete "PQC Data at Rest" granular test suite, potentially across multiple Python versions or OS environments if deemed necessary.
        *   *AI Verifiable Criterion:* Release checklist or SOP includes a step for executing these tests, and evidence of execution is recorded.

**AI Verifiable Completion Criterion for Recursive Testing Strategy:** This subsection details specific triggers, tagging conventions, and subset selection rules for regression testing, with each rule having a verifiable basis (e.g., CI configuration).

## 4. Test Environment & Setup

*   **Programming Language:** Python (version as per Fava's requirements).
*   **Testing Framework:** `pytest` (or Fava's standard testing framework).
*   **Mocking Library:** Python's `unittest.mock`.
*   **Required Libraries (for UUT, to be mocked in tests):**
    *   `oqs-python` (for Kyber KEM, Dilithium if used indirectly).
    *   `cryptography` (for X25519, AES-256-GCM, HKDF, SHA3, Argon2id).
*   **External Tools (for UUT, to be mocked or have controlled test instances):**
    *   GPG (command-line tool or library interface).
*   **Fava Configuration:**
    *   Tests will require setting up mock `FavaOptions` to simulate different PQC configurations (e.g., `pqc_data_at_rest_enabled`, `pqc_active_suite_id`, `pqc_key_management_mode`).
*   **Test Data:**
    *   Sample plaintext Beancount data.
    *   Pre-defined passphrases for testing key derivation.
    *   Mock key files (content structure for testing parsing, not actual cryptographic keys).
    *   Sample `EncryptedFileBundle` byte streams (both valid and intentionally corrupted for error testing).

**AI Verifiable Completion Criterion for Test Environment & Setup:** This section clearly lists all necessary tools, libraries, and configuration aspects, enabling a testing agent or human programmer to set up the environment required to execute the defined tests.

## 5. Test Cases

Each test case will verify specific interactions and observable outcomes, contributing to the AVERs outlined in Section 2.

---

### 5.1. Key Management Functions (`KeyManagementFunctions` / `fava.crypto.keys`)

#### Test Case ID: TP_DAR_KM_001
*   **Description:** Verify successful derivation of classical (X25519) and PQC (Kyber-768) KEM key pairs from a passphrase using Argon2id and HKDF-SHA3-512.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_key_derivation_from_passphrase_produces_valid_key_pairs_for_specified_algorithms()`
    *   Spec: FR2.8 (Sound Key Derivation)
    *   Architecture: ADR-003, Section 7.5 (Key Management Functions with Argon2id + HKDF)
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - key handling logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `derive_kem_keys_from_passphrase` function.
*   **Preconditions & Test Data:**
    *   `passphrase = "test_passphrase_123!"`
    *   `salt` (for Argon2id): `b'test_argon_salt_16b'` (16 bytes)
    *   `pbkdf_algorithm = "Argon2id"`
    *   `kdf_algorithm_for_ikm = "HKDF-SHA3-512"`
    *   `classical_kem_spec = "X25519"`
    *   `pqc_kem_spec = "ML-KEM-768"`
*   **Collaborators to Mock:**
    *   `cryptography.hazmat.primitives.kdf.argon2.Argon2id().derive()`
    *   `cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand(algorithm=hashes.SHA512(), length=N, info=b"...", backend=...)`
    *   `oqs.KeyEncapsulation(pqc_kem_spec).generate_keypair()` (or equivalent for deriving from HKDF output)
    *   `cryptography.hazmat.primitives.asymmetric.x25519.X25519PrivateKey.generate()` (or equivalent for deriving from HKDF output)
*   **Mocked Interactions & Expected Calls:**
    *   `Argon2id().derive(passphrase.encode(), salt)`: Called once, returns mock IKM (e.g., 64 bytes).
    *   `HKDFExpand(...).derive(mock_ikm)`: Called twice (once for classical key material, once for PQC key material, or once for combined material to be split), with appropriate lengths and info contexts. Returns mock keying material.
    *   Mocked key generation/derivation functions for X25519 and Kyber-768 are called with their respective portions of HKDF output.
*   **Test Steps:**
    1.  Configure mocks for `Argon2id().derive()`, `HKDFExpand().derive()`, and KEM key generation from derived material.
    2.  Call `UUT(passphrase, salt, pbkdf_algorithm, kdf_algorithm_for_ikm, classical_kem_spec, pqc_kem_spec)`.
*   **Observable Outcome & Assertions:**
    *   The function returns a tuple containing a mock classical key pair and a mock PQC key pair.
    *   Assert that `Argon2id().derive()` was called correctly.
    *   Assert that `HKDFExpand().derive()` was called correctly for both key types (or combined).
    *   Assert that the KEM key generation/derivation functions were called with the output from HKDF.
*   **Recursive Testing Tags:** `@key_management`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions are verified as specified.

#### Test Case ID: TP_DAR_KM_002
*   **Description:** Verify that `derive_kem_keys_from_passphrase` uses the provided Argon2id salt correctly (different salts produce different IKM).
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_key_derivation_from_passphrase_uses_salt_correctly()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - key handling logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `derive_kem_keys_from_passphrase` function.
*   **Preconditions & Test Data:**
    *   `passphrase = "test_passphrase_123!"`
    *   `salt1 = b'test_argon_salt_A'`
    *   `salt2 = b'test_argon_salt_B'`
    *   Other params same as TP_DAR_KM_001.
*   **Collaborators to Mock:** `cryptography.hazmat.primitives.kdf.argon2.Argon2id().derive()` (and downstream mocks as in KM_001).
*   **Mocked Interactions & Expected Calls:**
    *   `Argon2id().derive(passphrase.encode(), salt1)` returns `mock_ikm1`.
    *   `Argon2id().derive(passphrase.encode(), salt2)` returns `mock_ikm2`.
    *   Ensure `mock_ikm1` is not equal to `mock_ikm2`.
*   **Test Steps:**
    1.  Call UUT with `salt1`.
    2.  Record the IKM passed to HKDF (or observe calls to `Argon2id().derive()`).
    3.  Call UUT with `salt2`.
    4.  Record the IKM passed to HKDF.
*   **Observable Outcome & Assertions:**
    *   `Argon2id().derive()` is called with `salt1` in the first call and `salt2` in the second.
    *   The IKM produced by Argon2id (and subsequently used by HKDF) differs between the two calls.
*   **Recursive Testing Tags:** `@key_management`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions related to salt usage are verified.

#### Test Case ID: TP_DAR_KM_003
*   **Description:** Verify graceful failure of `derive_kem_keys_from_passphrase` for unsupported KDF or KEM specifications.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_key_derivation_fails_gracefully_for_unsupported_kdf_or_kem_spec()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `derive_kem_keys_from_passphrase` function.
*   **Preconditions & Test Data:**
    *   `passphrase = "test_passphrase"`
    *   `salt = b'some_salt_value'`
    *   Scenario 1: `kdf_algorithm_for_ikm = "UNSUPPORTED_KDF"`
    *   Scenario 2: `pqc_kem_spec = "UNSUPPORTED_PQC_KEM"`
*   **Collaborators to Mock:** Underlying crypto libraries (if they raise specific errors for unsupported algos).
*   **Mocked Interactions & Expected Calls:** N/A (testing UUT's error handling).
*   **Test Steps:**
    1.  Call UUT with an unsupported KDF algorithm.
    2.  Call UUT with an unsupported PQC KEM specification.
*   **Observable Outcome & Assertions:**
    *   A `KeyManagementError` (or specific `ConfigurationError`/`ValueError`) is raised in both scenarios.
    *   The error message indicates the unsupported algorithm.
*   **Recursive Testing Tags:** `@key_management`, `@error_handling`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies that the specified exception is raised with an appropriate message.

#### Test Case ID: TP_DAR_KM_004
*   **Description:** Verify successful loading of KEM key pairs from an (mocked) external key file.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_external_key_file_loading_parses_keys_correctly_for_supported_formats()`
    *   Spec: C7.3 (allowing users to provide paths to externally managed raw PQC key files)
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - key handling logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `load_keys_from_external_file` function.
*   **Preconditions & Test Data:**
    *   `key_file_path_config = {"classical_private": "mock_classical.key", "pqc_private": "mock_pqc.key"}` (or a single file format)
    *   Mock file content representing key data for X25519 and Kyber-768.
*   **Collaborators to Mock:**
    *   Built-in `open()` function (to simulate reading from files).
    *   Key parsing functions within `oqs` and `cryptography` libraries (e.g., `X25519PrivateKey.from_private_bytes()`, `oqs.KeyEncapsulation().keypair_from_secret()`).
*   **Mocked Interactions & Expected Calls:**
    *   `open()` called with specified file paths.
    *   Mocked file `read()` returns predefined byte strings for keys.
    *   Key parsing functions are called with the mock byte strings.
*   **Test Steps:**
    1.  Set up mock file system using `unittest.mock.patch('builtins.open', new_callable=mock_open, read_data=...)`.
    2.  Configure mocks for key parsing functions to return mock key pair objects.
    3.  Call `UUT(key_file_path_config)`.
*   **Observable Outcome & Assertions:**
    *   Returns a tuple containing mock classical and PQC key pairs.
    *   Assert `open()` was called for the correct file paths.
    *   Assert key parsing functions were called with the correct mock data.
*   **Recursive Testing Tags:** `@key_management`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions for file reading and key parsing are verified.

#### Test Case ID: TP_DAR_KM_005
*   **Description:** Verify graceful failure of `load_keys_from_external_file` if key file is missing or has invalid format.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_external_key_file_loading_fails_if_key_file_missing_or_invalid_format()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `load_keys_from_external_file` function.
*   **Preconditions & Test Data:**
    *   Scenario 1: `key_file_path_config` points to a non-existent file.
    *   Scenario 2: `key_file_path_config` points to a file with malformed key data.
*   **Collaborators to Mock:**
    *   `builtins.open()` (to raise `FileNotFoundError` or return bad data).
    *   Key parsing functions (to raise exceptions on malformed data).
*   **Mocked Interactions & Expected Calls:** N/A (testing UUT's error handling).
*   **Test Steps:**
    1.  Scenario 1: Configure `mock_open` to raise `FileNotFoundError`. Call UUT.
    2.  Scenario 2: Configure `mock_open` to return malformed data and key parsing mocks to raise an error (e.g., `ValueError`). Call UUT.
*   **Observable Outcome & Assertions:**
    *   A `KeyManagementError` is raised in both scenarios.
    *   Error message indicates file missing or invalid format.
*   **Recursive Testing Tags:** `@key_management`, `@error_handling`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies that the specified exception is raised.

#### Test Case ID: TP_DAR_KM_006 (Key Export - Secure Format)
*   **Description:** Verify `export_fava_managed_pqc_private_keys` retrieves (mocked) keys and formats them into a (mocked) secure, documented export format (e.g., encrypted PKCS#8).
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_key_export_retrieves_correct_fava_managed_keys_for_context()`, `test_key_export_formats_keys_correctly_for_documented_export_format()`
    *   Spec: FR2.9 (Key Export)
    *   Architecture: ADR-005 (Security of PQC Private Key Export)
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - key handling logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `export_fava_managed_pqc_private_keys` function.
*   **Preconditions & Test Data:**
    *   `key_context` (e.g., user ID, file ID for which key was derived/stored).
    *   `export_format = "ENCRYPTED_PKCS8_AES256GCM_PBKDF2"` (conceptual).
    *   User-provided export passphrase: `export_passphrase = "secure_export_password"`
    *   Mock PQC private key object.
*   **Collaborators to Mock:**
    *   Internal function to retrieve/re-derive the PQC private key for `key_context` (e.g., `_retrieve_stored_or_derived_pqc_private_key`).
    *   Functions for formatting the key into the specified secure format (e.g., `cryptography` library calls for PKCS#8 serialization and encryption with PBKDF2 and AES-GCM).
*   **Mocked Interactions & Expected Calls:**
    *   `_retrieve_stored_or_derived_pqc_private_key(key_context)` called once, returns mock PQC private key.
    *   Mocked secure formatting/encryption functions are called with the mock private key and `export_passphrase`.
*   **Test Steps:**
    1.  Configure mock for `_retrieve_stored_or_derived_pqc_private_key` to return a mock key.
    2.  Configure mocks for secure formatting/encryption to return a predefined byte string.
    3.  Call `UUT(key_context, export_format, export_passphrase)`.
*   **Observable Outcome & Assertions:**
    *   Returns the predefined byte string representing the securely formatted key.
    *   Assert `_retrieve_stored_or_derived_pqc_private_key` was called correctly.
    *   Assert secure formatting/encryption functions were called with the correct key and passphrase.
*   **Recursive Testing Tags:** `@key_management`, `@security_sensitive`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions for key retrieval and secure formatting are verified.

#### Test Case ID: TP_DAR_KM_007 (Key Export - Failure)
*   **Description:** Verify `export_fava_managed_pqc_private_keys` fails gracefully if keys are not found for the given context.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_key_export_fails_if_keys_not_found_for_context()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `export_fava_managed_pqc_private_keys` function.
*   **Preconditions & Test Data:**
    *   `key_context = "non_existent_context"`
    *   `export_format = "ENCRYPTED_PKCS8_AES256GCM_PBKDF2"`
*   **Collaborators to Mock:**
    *   `_retrieve_stored_or_derived_pqc_private_key`.
*   **Mocked Interactions & Expected Calls:**
    *   `_retrieve_stored_or_derived_pqc_private_key(key_context)` called once, returns `None` or raises a specific "not found" exception.
*   **Test Steps:**
    1.  Configure mock for `_retrieve_stored_or_derived_pqc_private_key` to indicate key not found.
    2.  Call `UUT(key_context, export_format, "any_passphrase")`.
*   **Observable Outcome & Assertions:**
    *   Raises `KeyManagementError`.
    *   Error message indicates key not found for export.
*   **Recursive Testing Tags:** `@key_management`, `@error_handling`, `@security_sensitive`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies that the specified exception is raised.

---

### 5.2. `HybridPqcHandler`

#### Test Case ID: TP_DAR_HPH_001
*   **Description:** Verify `HybridPqcHandler.can_handle()` correctly identifies files by extension (e.g., `.pqc_hybrid_fava`).
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_pqc_handler_can_handle_by_extension()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.can_handle` method.
*   **Preconditions & Test Data:**
    *   `file_path1 = "data.bc.pqc_hybrid_fava"`
    *   `file_path2 = "data.bc.gpg"`
    *   `file_path3 = "data.bc"`
    *   `content_bytes_peek = None`
    *   `config = {}` (or mock FavaOptions)
*   **Collaborators to Mock:** None.
*   **Test Steps:**
    1.  Instantiate `HybridPqcHandler`.
    2.  Call `UUT(file_path1, content_bytes_peek, config)`.
    3.  Call `UUT(file_path2, content_bytes_peek, config)`.
    4.  Call `UUT(file_path3, content_bytes_peek, config)`.
*   **Observable Outcome & Assertions:**
    *   Returns `True` for `file_path1`.
    *   Returns `False` for `file_path2`.
    *   Returns `False` for `file_path3`.
*   **Recursive Testing Tags:** `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies the expected boolean outcomes.

#### Test Case ID: TP_DAR_HPH_002
*   **Description:** Verify `HybridPqcHandler.can_handle()` correctly identifies files by magic bytes/format identifier in `content_bytes_peek`.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_pqc_handler_can_handle_by_magic_bytes()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.can_handle` method.
*   **Preconditions & Test Data:**
    *   `file_path = "some_file.unknown_ext"`
    *   `content_bytes_peek_pqc = b'FAVA_PQC_HYBRID_V1...'` (serialized start of a bundle)
    *   `content_bytes_peek_other = b'OTHER_FORMAT...'`
    *   `config = {}`
*   **Collaborators to Mock:** Mocked `EncryptedFileBundle.PARSE_HEADER_ONLY(content_bytes_peek_pqc)` that returns a valid format identifier.
*   **Test Steps:**
    1.  Instantiate `HybridPqcHandler`.
    2.  Call `UUT(file_path, content_bytes_peek_pqc, config)`.
    3.  Call `UUT(file_path, content_bytes_peek_other, config)`.
*   **Observable Outcome & Assertions:**
    *   Returns `True` for `content_bytes_peek_pqc`.
    *   Returns `False` for `content_bytes_peek_other`.
*   **Recursive Testing Tags:** `@config_dependent`, `@bundle_format`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies the expected boolean outcomes based on content peeking.

#### Test Case ID: TP_DAR_HPH_003 (Encrypt-Decrypt Success)
*   **Description:** Verify successful end-to-end encryption and decryption of plaintext content using `HybridPqcHandler` with X25519+Kyber768+AES256GCM.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_hybrid_pqc_handler_encrypts_decrypts_successfully()`
    *   Spec: FR2.1, FR2.5, TDD Anchor `test_hybrid_pqc_handler_encrypts_decrypts_successfully()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - hybrid flow), Phase 4 (Task 4.X.B - test pass), Basic check for NFR3.2 (Performance).
*   **Unit Under Test (UUT):** `HybridPqcHandler` instance.
*   **Preconditions & Test Data:**
    *   `plaintext_content = "This is secret Beancount data."`
    *   `suite_config = { "id": "X25519_KYBER768_AES256GCM", "classical_kem_algorithm": "X25519", "pqc_kem_algorithm": "ML-KEM-768", "symmetric_algorithm": "AES256GCM", "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512", ... }`
    *   `key_material_encrypt`: Contains mock PQC public keys (classical & PQC) for recipient.
    *   `key_material_decrypt`: Contains corresponding mock PQC private keys.
*   **Collaborators to Mock:**
    *   `oqs.KeyEncapsulation(kem_name).encapsulate(public_key)`
    *   `oqs.KeyEncapsulation(kem_name).decapsulate(secret_key, ciphertext)`
    *   `cryptography` X25519 key exchange/KEM functions.
    *   `cryptography` HKDF functions.
    *   `cryptography` AES-256-GCM encryption/decryption functions.
    *   `EncryptedFileBundle` serialization/deserialization.
*   **Mocked Interactions & Expected Calls (Simplified - focus on flow):**
    *   Encryption: KEM encapsulations (classical & PQC) are called, KDF derives symmetric key, AES encrypts. `EncryptedFileBundle` is constructed.
    *   Decryption: `EncryptedFileBundle` is parsed, KEM decapsulations occur, KDF derives symmetric key, AES decrypts.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Configure mocks for all crypto primitives to behave correctly (e.g., encapsulate returns valid ciphertext and shared secret, decapsulate with correct key returns same shared secret).
    3.  Call `encrypted_bundle = UUT.encrypt_content(plaintext_content, suite_config, key_material_encrypt)`.
    4.  Call `decrypted_content = UUT.decrypt_content(encrypted_bundle, suite_config, key_material_decrypt)`.
    5.  (Optional) Record time taken for basic performance smoke check.
*   **Observable Outcome & Assertions:**
    *   `decrypted_content` equals `plaintext_content`.
    *   No exceptions raised during happy path.
    *   All mocked crypto functions are called in the correct sequence with expected intermediate data (e.g., shared secrets match between KEM encapsulation and KDF input).
    *   (Optional) Assert encryption/decryption time is within a very generous smoke test range (e.g., < 2 seconds for small data).
*   **Recursive Testing Tags:** `@critical_path`, `@performance_smoke`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, verifies content integrity, and mock interactions demonstrate correct crypto flow.

#### Test Case ID: TP_DAR_HPH_004 (Encrypt Uses Suite Config)
*   **Description:** Verify `HybridPqcHandler.encrypt_content` uses the correct algorithms specified in the `suite_config`.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_pqc_handler_encrypt_uses_correct_algorithms_from_suite_config()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - config logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.encrypt_content` method.
*   **Preconditions & Test Data:**
    *   `plaintext_content = "Data"`
    *   `suite_config_kyber768 = { "id": "S1", "classical_kem_algorithm": "X25519", "pqc_kem_algorithm": "ML-KEM-768", ... }`
    *   `suite_config_kyber1024 = { "id": "S2", "classical_kem_algorithm": "X25519", "pqc_kem_algorithm": "ML-KEM-1024", ... }` (assuming Kyber1024 is mockable)
    *   `key_material_encrypt` (mocked public keys).
*   **Collaborators to Mock:**
    *   `oqs.KeyEncapsulation(kem_name)` constructor/factory.
    *   `cryptography` KEM/cipher factories.
*   **Mocked Interactions & Expected Calls:**
    *   When called with `suite_config_kyber768`, `oqs.KeyEncapsulation` is instantiated with `"ML-KEM-768"`.
    *   When called with `suite_config_kyber1024`, `oqs.KeyEncapsulation` is instantiated with `"ML-KEM-1024"`.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Configure mocks.
    3.  Call `UUT.encrypt_content(plaintext_content, suite_config_kyber768, key_material_encrypt)`.
    4.  Verify `oqs.KeyEncapsulation` was called with `"ML-KEM-768"`.
    5.  Reset mocks.
    6.  Call `UUT.encrypt_content(plaintext_content, suite_config_kyber1024, key_material_encrypt)`.
    7.  Verify `oqs.KeyEncapsulation` was called with `"ML-KEM-1024"`.
*   **Observable Outcome & Assertions:**
    *   The correct PQC KEM algorithm name from `suite_config` is passed to the `oqs.KeyEncapsulation` factory/constructor.
    *   Similar assertions for classical KEM and symmetric cipher if their factories are mockable.
*   **Recursive Testing Tags:** `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions confirm algorithm selection based on suite config.

#### Test Case ID: TP_DAR_HPH_005 (PQC KEM Encapsulation)
*   **Description:** Verify the PQC KEM encapsulation step produces a valid (mocked) ciphertext and shared secret.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_pqc_kem_encapsulation_produces_valid_ciphertext_and_shared_secret()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - PQC KEM logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** Internal PQC KEM encapsulation logic within `HybridPqcHandler.encrypt_content`.
*   **Preconditions & Test Data:**
    *   `pqc_recipient_pk` (mock PQC public key).
    *   `pqc_kem_alg = "ML-KEM-768"`.
*   **Collaborators to Mock:** `oqs.KeyEncapsulation(pqc_kem_alg).encapsulate(pqc_recipient_pk)`.
*   **Mocked Interactions & Expected Calls:**
    *   `mock_kem.encapsulate(pqc_recipient_pk)` returns `(mock_pqc_encapsulated_key, mock_pqc_shared_secret_part)`.
*   **Test Steps:**
    1.  Isolate or call the part of `encrypt_content` that performs PQC KEM encapsulation.
    2.  Configure `mock_kem.encapsulate` to return known mock values.
*   **Observable Outcome & Assertions:**
    *   The `encapsulate` method of the mocked KEM object is called with the correct public key.
    *   The returned (mocked) `pqc_encapsulated_key` and `pqc_shared_secret_part` are used in subsequent steps (e.g., bundle construction, KDF input).
*   **Recursive Testing Tags:** `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interaction verifies correct call and usage of KEM output.

#### Test Case ID: TP_DAR_HPH_006 (Hybrid KEM Symmetric Key Derivation)
*   **Description:** Verify consistent symmetric key derivation using KDF from combined classical and PQC shared secrets.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_kem_derives_consistent_symmetric_key_using_kdf()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - KDF logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** KDF logic within `HybridPqcHandler.encrypt_content` and `decrypt_content`.
*   **Preconditions & Test Data:**
    *   `classical_shared_secret_part = b'classical_secret'`
    *   `pqc_shared_secret_part = b'pqc_secret'`
    *   `kdf_salt_for_hybrid_sk = b'kdf_salt_123'`
    *   `kdf_for_hybrid_sk_alg = "HKDF-SHA3-512"`
    *   `required_length = 32` (for AES-256)
*   **Collaborators to Mock:** `cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand(...).derive()`.
*   **Mocked Interactions & Expected Calls:**
    *   `mock_hkdf.derive(b'classical_secret' + b'pqc_secret')` is called.
*   **Test Steps:**
    1.  Isolate or call the KDF step in `encrypt_content` (or `decrypt_content`).
    2.  Provide known `classical_shared_secret_part`, `pqc_shared_secret_part`, and `kdf_salt_for_hybrid_sk`.
    3.  Configure `mock_hkdf.derive` to return a known `derived_symmetric_key`.
*   **Observable Outcome & Assertions:**
    *   `HKDFExpand().derive()` is called with the concatenated shared secrets and the correct salt, KDF algorithm, and length.
    *   The returned `derived_symmetric_key` is used for symmetric encryption/decryption.
*   **Recursive Testing Tags:** `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interaction verifies correct KDF input and usage of its output.

#### Test Case ID: TP_DAR_HPH_007 (AES-GCM Encryption Produces Tag/IV)
*   **Description:** Verify AES-GCM encryption step produces valid (mocked) ciphertext, IV, and authentication tag.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_aes_gcm_encryption_produces_valid_tag_and_iv()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - AES logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** Symmetric encryption logic within `HybridPqcHandler.encrypt_content`.
*   **Preconditions & Test Data:**
    *   `plaintext_content = "data"`
    *   `derived_symmetric_key = b'32_byte_aes_key_mock'`
    *   `symmetric_alg = "AES256GCM"`
*   **Collaborators to Mock:** `cryptography.hazmat.primitives.ciphers.Cipher(...).encryptor().update/finalize()`, `encryptor.tag`.
*   **Mocked Interactions & Expected Calls:**
    *   AES-GCM cipher is initialized with `derived_symmetric_key` and a generated IV.
    *   `encryptor.update()` and `encryptor.finalize()` are called.
    *   `encryptor.tag` is accessed.
*   **Test Steps:**
    1.  Isolate symmetric encryption step.
    2.  Provide mock `derived_symmetric_key`.
    3.  Configure AES mocks to return known `encrypted_data`, `iv_or_nonce`, `auth_tag`.
*   **Observable Outcome & Assertions:**
    *   AES-GCM encryption is performed with the correct key.
    *   A (mocked) IV is generated and used.
    *   (Mocked) ciphertext and authentication tag are produced and used in the `EncryptedFileBundle`.
*   **Recursive Testing Tags:** `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and mock interactions verify correct AES-GCM encryption flow.

#### Test Case ID: TP_DAR_HPH_008 (Decrypt Fails for Wrong Key)
*   **Description:** Verify `HybridPqcHandler.decrypt_content` fails (raises `DecryptionError`) when an incorrect key is used.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_hybrid_pqc_handler_decrypt_fails_for_wrong_key()`
    *   Spec: TDD Anchor `test_hybrid_pqc_handler_decrypt_fails_for_wrong_key()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   `encrypted_bundle_bytes` (validly encrypted with key_A).
    *   `suite_config` (matching the encryption).
    *   `key_material_decrypt_wrong`: Contains key_B (private keys different from key_A).
*   **Collaborators to Mock:**
    *   KEM decapsulation functions (to simulate failure due to wrong key, e.g., return None or raise error).
    *   OR AES decryption (if KEMs "succeed" with wrong key but yield wrong symmetric key, AES-GCM tag verification will fail).
*   **Mocked Interactions & Expected Calls:**
    *   Mocked KEM decapsulation (e.g., `oqs_kem.decapsulate()`) is called with `key_material_decrypt_wrong`. It returns a value indicating failure (e.g., raises an internal crypto error, or returns a different shared secret that leads to AES tag mismatch).
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Create `encrypted_bundle_bytes` (can be from TP_DAR_HPH_003 encryption step).
    3.  Configure crypto mocks to simulate decryption failure with `key_material_decrypt_wrong`.
    4.  Call `UUT.decrypt_content(encrypted_bundle_bytes, suite_config, key_material_decrypt_wrong)`.
*   **Observable Outcome & Assertions:**
    *   Raises `DecryptionError`.
    *   Error message indicates decryption failure due to key or corruption.
*   **Recursive Testing Tags:** `@error_handling`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies `DecryptionError` is raised.

#### Test Case ID: TP_DAR_HPH_009 (Decrypt Fails on Tampered Ciphertext/Tag)
*   **Description:** Verify `HybridPqcHandler.decrypt_content` fails if ciphertext or AEAD tag is tampered.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_pqc_handler_decrypt_fails_on_tampered_ciphertext_or_tag()` (EC6.1, EC6.4)
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   Valid `encrypted_bundle_bytes`.
    *   `suite_config`.
    *   `key_material_decrypt` (correct keys).
    *   Scenario 1: Modify a byte in `encrypted_data_ciphertext` within the bundle.
    *   Scenario 2: Modify a byte in `authentication_tag` within the bundle.
*   **Collaborators to Mock:** `cryptography` AES-GCM decryption (it should raise `InvalidTag` internally).
*   **Mocked Interactions & Expected Calls:** AES-GCM decryption is attempted and is expected to fail due to tag mismatch.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Obtain a valid `encrypted_bundle_bytes`.
    3.  Deserialize, tamper (e.g., flip a bit in ciphertext or tag), re-serialize.
    4.  Call `UUT.decrypt_content(tampered_bundle_bytes, suite_config, key_material_decrypt)`.
*   **Observable Outcome & Assertions:**
    *   Raises `DecryptionError` (likely due to AES-GCM tag verification failure).
*   **Recursive Testing Tags:** `@error_handling`, `@bundle_format`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies `DecryptionError` for tampered data.

#### Test Case ID: TP_DAR_HPH_010 (Decrypt Fails on Corrupted KEM Ciphertext)
*   **Description:** Verify `HybridPqcHandler.decrypt_content` fails if PQC KEM ciphertext is corrupted.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_hybrid_pqc_handler_decrypt_fails_for_corrupted_kem_ciphertext()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   Valid `encrypted_bundle_bytes`.
    *   `suite_config`.
    *   `key_material_decrypt` (correct keys).
    *   Modify `pqc_kem_encapsulated_key` in the bundle.
*   **Collaborators to Mock:** `oqs.KeyEncapsulation(...).decapsulate()` (it should raise an error or return an invalid shared secret).
*   **Mocked Interactions & Expected Calls:** `oqs_kem.decapsulate()` is called with corrupted KEM ciphertext and is expected to fail.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Obtain valid `encrypted_bundle_bytes`.
    3.  Deserialize, tamper `pqc_kem_encapsulated_key`, re-serialize.
    4.  Call `UUT.decrypt_content(tampered_bundle_bytes, suite_config, key_material_decrypt)`.
*   **Observable Outcome & Assertions:**
    *   Raises `DecryptionError`.
*   **Recursive Testing Tags:** `@error_handling`, `@bundle_format`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies `DecryptionError` for corrupted KEM data.

#### Test Case ID: TP_DAR_HPH_011 (Encrypted Bundle Parser)
*   **Description:** Verify `EncryptedFileBundle` parser correctly extracts all fields from a serialized byte stream.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_encrypted_bundle_parser_extracts_all_fields_correctly()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - data format), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `EncryptedFileBundle` parsing logic (e.g., a static method `EncryptedFileBundle.from_bytes()`).
*   **Preconditions & Test Data:**
    *   A known, valid serialized `EncryptedFileBundle` byte stream with predefined values for all fields (format_id, suite_id, KEM outputs, IV, ciphertext, tag, salts).
*   **Collaborators to Mock:** None (testing parsing logic).
*   **Test Steps:**
    1.  Call `bundle_object = EncryptedFileBundle.from_bytes(serialized_bundle_bytes)`.
*   **Observable Outcome & Assertions:**
    *   The returned `bundle_object` has attributes matching all the predefined values from the input byte stream.
*   **Recursive Testing Tags:** `@bundle_format`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct parsing of all bundle fields.

#### Test Case ID: TP_DAR_HPH_012 (Decrypt Fails Mismatched Suite/Format ID)
*   **Description:** Verify decryption fails if `EncryptedFileBundle` has a mismatched `suite_id` or `format_identifier`.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_decrypt_fails_for_mismatched_suite_id_or_format_identifier()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `HybridPqcHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   `suite_config` expects `suite_id = "SUITE_A"`.
    *   Scenario 1: `encrypted_bundle_bytes` has `suite_id = "SUITE_B"`.
    *   Scenario 2: `encrypted_bundle_bytes` has `format_identifier = "OLD_FORMAT_V0"`.
*   **Collaborators to Mock:** `EncryptedFileBundle` parsing.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Create/mock `encrypted_bundle_bytes` for Scenario 1. Call UUT.
    3.  Create/mock `encrypted_bundle_bytes` for Scenario 2. Call UUT.
*   **Observable Outcome & Assertions:**
    *   Raises `DecryptionError` in both scenarios.
    *   Error message indicates format or suite mismatch.
*   **Recursive Testing Tags:** `@error_handling`, `@bundle_format`, `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies `DecryptionError` for mismatches.

---
### 5.3. `GpgHandler`

#### Test Case ID: TP_DAR_GPGH_001
*   **Description:** Verify `GpgHandler.can_handle()` correctly identifies GPG files by extension or magic bytes.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_gpg_handler_can_handle_by_extension_or_magic_bytes()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - GPG logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `GpgHandler.can_handle` method.
*   **Preconditions & Test Data:**
    *   `file_path_gpg = "data.bc.gpg"`
    *   `file_path_other = "data.bc.pqc_hybrid_fava"`
    *   `content_bytes_peek_gpg = b'\x85\x02...'` (example GPG magic bytes)
    *   `config = { "pqc_fallback_to_classical_gpg": True }`
*   **Collaborators to Mock:** None.
*   **Test Steps:**
    1.  Instantiate `GpgHandler`.
    2.  Call `UUT(file_path_gpg, None, config)`.
    3.  Call `UUT("data.txt", content_bytes_peek_gpg, config)`.
    4.  Call `UUT(file_path_other, None, config)`.
*   **Observable Outcome & Assertions:**
    *   Returns `True` for GPG extension and GPG magic bytes.
    *   Returns `False` for non-GPG file types.
*   **Recursive Testing Tags:** `@gpg_compatibility`, `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct identification.

#### Test Case ID: TP_DAR_GPGH_002 (GPG Decrypt Success)
*   **Description:** Verify `GpgHandler.decrypt_content` successfully decrypts a valid GPG-encrypted file (using mocked GPG tool).
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_gpg_handler_decrypts_valid_gpg_file()`
    *   Spec: FR2.2, TDD Anchor `test_gpg_handler_decrypts_valid_gpg_file()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - GPG logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `GpgHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   `encrypted_content_bundle_bytes` (mocked GPG encrypted data).
    *   `suite_config = { "gpg_options": "--some-option" }` (conceptual).
    *   `key_material` (often implicit for GPG agent, can be None).
    *   `expected_plaintext = "GPG decrypted data"`
*   **Collaborators to Mock:** `subprocess.run` (or similar for invoking GPG tool/library).
*   **Mocked Interactions & Expected Calls:**
    *   `mock_subprocess_run` called with GPG command (e.g., `['gpg', '--decrypt', '--some-option']`) and `input=encrypted_content_bundle_bytes`.
    *   Mock returns `CompletedProcess` object with `stdout=expected_plaintext.encode()` and `returncode=0`.
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Configure `mock_subprocess_run`.
    3.  Call `UUT(encrypted_content_bundle_bytes, suite_config, key_material)`.
*   **Observable Outcome & Assertions:**
    *   Returns `expected_plaintext`.
    *   `mock_subprocess_run` called correctly.
*   **Recursive Testing Tags:** `@gpg_compatibility`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct GPG invocation and plaintext return.

#### Test Case ID: TP_DAR_GPGH_003 (GPG Decrypt Failure)
*   **Description:** Verify `GpgHandler.decrypt_content` fails for invalid GPG file or wrong key (mocked GPG tool error).
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_gpg_handler_decrypt_fails_for_invalid_gpg_file_or_wrong_key()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - error conditions), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `GpgHandler.decrypt_content` method.
*   **Preconditions & Test Data:**
    *   `encrypted_content_bundle_bytes` (mocked).
*   **Collaborators to Mock:** `subprocess.run`.
*   **Mocked Interactions & Expected Calls:**
    *   `mock_subprocess_run` returns `CompletedProcess` with `returncode=1` (or raises an exception).
*   **Test Steps:**
    1.  Instantiate UUT.
    2.  Configure `mock_subprocess_run` to simulate GPG error.
    3.  Call `UUT(...)`.
*   **Observable Outcome & Assertions:**
    *   Raises `DecryptionError`.
*   **Recursive Testing Tags:** `@gpg_compatibility`, `@error_handling`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies `DecryptionError` on GPG failure.

---
### 5.4. `CryptoServiceLocator`

#### Test Case ID: TP_DAR_CSL_001 (Selects PQC Handler)
*   **Description:** Verify `CryptoServiceLocator.get_handler_for_file` selects `HybridPqcHandler` for a PQC file.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_crypto_service_locator_selects_pqc_handler_for_pqc_file()`
    *   Spec: TDD Anchor `test_crypto_service_locator_selects_pqc_handler_for_pqc_file()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - locator logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `CryptoServiceLocator.get_handler_for_file` method.
*   **Preconditions & Test Data:**
    *   `file_path = "data.bc.pqc_hybrid_fava"`
    *   `content_bytes_peek = None`
    *   `fava_options` (mocked, PQC enabled).
    *   Mock `HybridPqcHandler` instance where `can_handle()` returns `True` for this input.
    *   Mock `GpgHandler` instance where `can_handle()` returns `False`.
*   **Collaborators to Mock:** `HybridPqcHandler.can_handle`, `GpgHandler.can_handle`.
*   **Test Steps:**
    1.  Instantiate UUT with mocked handlers.
    2.  Call `UUT.get_handler_for_file(file_path, content_bytes_peek, fava_options)`.
*   **Observable Outcome & Assertions:**
    *   Returns an instance of `HybridPqcHandler`.
    *   `HybridPqcHandler.can_handle` was called.
*   **Recursive Testing Tags:** `@config_dependent`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct handler selection.

#### Test Case ID: TP_DAR_CSL_002 (Selects GPG Handler)
*   **Description:** Verify `CryptoServiceLocator.get_handler_for_file` selects `GpgHandler` for a GPG file.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_crypto_service_locator_selects_gpg_handler_for_gpg_file()`
    *   Spec: TDD Anchor `test_crypto_service_locator_selects_gpg_handler_for_gpg_file()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - locator logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `CryptoServiceLocator.get_handler_for_file` method.
*   **Preconditions & Test Data:**
    *   `file_path = "data.bc.gpg"`
    *   Mock `HybridPqcHandler.can_handle()` returns `False`.
    *   Mock `GpgHandler.can_handle()` returns `True`.
*   **Test Steps:** (Similar to CSL_001)
*   **Observable Outcome & Assertions:** Returns an instance of `GpgHandler`.
*   **Recursive Testing Tags:** `@config_dependent`, `@gpg_compatibility`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct handler selection.

#### Test Case ID: TP_DAR_CSL_003 (Handler Prioritization)
*   **Description:** Verify `CryptoServiceLocator` prioritizes handlers correctly if multiple `can_handle()` return true (e.g., a specific PQC handler before a generic fallback).
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_crypto_service_locator_prioritizes_handlers_correctly()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - locator logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `CryptoServiceLocator.get_handler_for_file` method.
*   **Preconditions & Test Data:**
    *   UUT initialized with handlers: `[MockHandlerPQC, MockHandlerGeneric]`
    *   Both `MockHandlerPQC.can_handle()` and `MockHandlerGeneric.can_handle()` return `True` for the input.
*   **Test Steps:** Call `UUT.get_handler_for_file(...)`.
*   **Observable Outcome & Assertions:** Returns `MockHandlerPQC` (assuming it's registered first).
*   **Recursive Testing Tags:** `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies handler prioritization.

#### Test Case ID: TP_DAR_CSL_004 (No Handler Matches)
*   **Description:** Verify `CryptoServiceLocator` returns `Null` or raises error if no handler matches.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_crypto_service_locator_returns_null_or_errors_if_no_handler_matches()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - locator logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `CryptoServiceLocator.get_handler_for_file` method.
*   **Preconditions & Test Data:** All registered mock handlers' `can_handle()` return `False`. `fava_options.pqc_fallback_to_classical_gpg = False`.
*   **Test Steps:** Call `UUT.get_handler_for_file(...)`.
*   **Observable Outcome & Assertions:** Returns `None` (or a specific `NullHandler` instance, or raises a specific "no handler found" error as per implementation choice).
*   **Recursive Testing Tags:** `@error_handling`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies the defined behavior when no handler matches.

#### Test Case ID: TP_DAR_CSL_005 (Get PQC Encrypt Handler)
*   **Description:** Verify `CryptoServiceLocator.get_pqc_encrypt_handler` returns a `HybridPqcHandler` for a valid PQC suite config.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_crypto_service_locator_returns_correct_pqc_encrypt_handler_for_suite()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - locator logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `CryptoServiceLocator.get_pqc_encrypt_handler` method.
*   **Preconditions & Test Data:**
    *   `suite_config = { "pqc_kem_algorithm": "ML-KEM-768", ... }`
    *   `fava_options` (mocked).
*   **Test Steps:** Call `UUT.get_pqc_encrypt_handler(suite_config, fava_options)`.
*   **Observable Outcome & Assertions:** Returns an instance of `HybridPqcHandler`.
*   **Recursive Testing Tags:** `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct handler provision.

---
### 5.5. `FavaLedger` Integration

#### Test Case ID: TP_DAR_FL_001 (Get Key Material - Decrypt Passphrase)
*   **Description:** Verify `FavaLedger._get_key_material_for_operation` correctly obtains/derives key material for decryption using passphrase mode.
*   **Source TDD Anchor(s)/Requirement(s):** Pseudocode: `test_fava_ledger_obtains_correct_key_material_for_decryption_passphrase()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - FavaLedger key logic), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `FavaLedger._get_key_material_for_operation` method.
*   **Preconditions & Test Data:**
    *   `fava_options` mock: `CONFIG_PQC_KEY_MANAGEMENT_MODE = "PASSPHRASE_DERIVED"`, active suite configured.
    *   `file_context = "test_file.pqc"`
    *   `operation_type = "decrypt"`
    *   Mock user prompt returns `test_passphrase`.
    *   Mock `derive_kem_keys_from_passphrase` returns mock private keys.
*   **Collaborators to Mock:** `PROMPT_USER_FOR_PASSPHRASE_SECURELY`, `RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT`, `derive_kem_keys_from_passphrase`.
*   **Test Steps:** Call `UUT(...)`.
*   **Observable Outcome & Assertions:**
    *   Returns object containing mock private keys.
    *   `PROMPT_USER_FOR_PASSPHRASE_SECURELY` called.
    *   `derive_kem_keys_from_passphrase` called with prompted passphrase and retrieved salt.
*   **Recursive Testing Tags:** `@key_management`, `@critical_path`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies correct interaction with key derivation collaborators.

#### Test Case ID: TP_DAR_FL_002 (Save and Reload PQC Encrypted File)
*   **Description:** Verify `FavaLedger` can save content with PQC encryption and then reload/decrypt it successfully.
*   **Source TDD Anchor(s)/Requirement(s):**
    *   Pseudocode: `test_fava_ledger_saves_and_reloads_pqc_encrypted_file()`
    *   Spec: TDD Anchor `test_fava_ledger_saves_and_reloads_pqc_encrypted_file()`
*   **Targeted AI Verifiable End Result(s):** Phase 2 (Task 2.1 - FavaLedger full flow), Phase 4 (Task 4.X.B - test pass).
*   **Unit Under Test (UUT):** `FavaLedger` instance.
*   **Preconditions & Test Data:**
    *   Mock `fava_options` for PQC Hybrid Suite X (passphrase derived).
    *   `plaintext_data = "ledger_content_to_encrypt"`.
    *   `file_path = "test.bc.pqc_fava"`.
*   **Collaborators to Mock:**
    *   `CryptoServiceLocator` (to return mock `HybridPqcHandler`).
    *   Mock `HybridPqcHandler` (whose `encrypt_content` and `decrypt_content` work with mock keys/data).
    *   `_get_key_material_for_operation` (to provide consistent mock keys for encryption and decryption based on a mock passphrase prompt).
    *   File I/O (`WRITE_BYTES_TO_FILE`, `READ_BYTES_FROM_FILE`).
    *   Fava's Beancount parsing logic (to verify final loaded data).
*   **Test Steps:**
    1.  Instantiate `FavaLedger` with mocks.
    2.  Call `UUT.save_file_pqc(file_path, plaintext_data, "context")`.
        *   Verify `HybridPqcHandler.encrypt_content` was called.
        *   Verify mock file write was called with encrypted bundle.
    3.  Call `loaded_entries = UUT.load_file(file_path)`. (This internally calls `_try_decrypt_content`).
        *   Verify `HybridPqcHandler.decrypt_content` was called with data from mock file read.
        *   Verify mock Beancount parser was called with `plaintext_data`.
*   **Observable Outcome & Assertions:**
    *   `loaded_entries` (or equivalent from parser) matches what would be parsed from `plaintext_data`.
    *   Correct sequence of calls to `CryptoServiceLocator`, `HybridPqcHandler`, key material functions, and file I/O mocks.
*   **Recursive Testing Tags:** `@critical_path`, `@config_dependent`
*   **AI Verifiable Completion Criterion for Test Case:** Test code exists, passes, and verifies the full save/load cycle through mock interactions.

---
*(Additional test cases for other TDD anchors and specific error conditions in `FavaLedger` like `MissingDependencyError`, `KeyManagementError` during load/save would follow a similar structure.)*

## 6. Test Data Management

*   **Plaintext Data:** Small, representative Beancount snippets will be used as strings within test files.
*   **Passphrases:** Fixed, non-sensitive passphrases (e.g., `"test_password"`) will be used for reproducible key derivation tests.
*   **Key Files (Mocked):** For tests involving `load_keys_from_external_file`, the content of key files will be mocked. Actual private key files will NOT be stored in the repository.
*   **`EncryptedFileBundle` Samples:**
    *   For parsing tests, byte strings representing valid bundles will be constructed or defined as test data.
    *   For tampering tests, valid bundles will be programmatically altered.
*   **Cryptographic Keys (Mocked):** Actual cryptographic operations will use mock key objects or byte strings returned by mocked library functions. Test vectors from PQC standards might be used to verify specific low-level crypto calls if testing library wrappers, but mostly we rely on the libraries being correct.
*   **Salts and IVs:** For tests requiring them, fixed byte strings will be used for predictability, or mocks will be configured to return predictable values.

**AI Verifiable Completion Criterion for Test Data Management:** This section describes the types of test data and how they will be handled or mocked, ensuring tests are reproducible and do not involve real sensitive material.

## 7. Document Review & Approval

*   **Reviewed By:** (Placeholder for reviewer names/AI Agent ID)
*   **Date:** (Placeholder for review date)
*   **Status:** (Placeholder: e.g., DRAFT, PENDING REVIEW, APPROVED)

**AI Verifiable Completion Criterion for Document Review:** This section is updated with review details upon completion of the review process.