# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 12

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 12 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   ... (Parts 2-10) ...
*   Part 11: [PQC_Developer_Guide_v1.1_part11.md](PQC_Developer_Guide_v1.1_part11.md)

This part covers PQC testing strategies and developer best practices.

## 10. Testing

A comprehensive testing strategy is vital for ensuring the correctness, security, and performance of PQC features. Fava's PQC testing approach includes both granular (unit/integration) tests and high-level acceptance tests.

*   **Granular Tests:**
    *   Located in `tests/granular/` subdirectories (e.g., `tests/granular/pqc_data_at_rest/`, `tests/granular/pqc_wasm_module_integrity/`).
    *   **Focus:** Test individual PQC components and their interactions in isolation.
        *   `BackendCryptoService` and individual `CryptoHandler` implementations (e.g., encrypt/decrypt with known keys, error handling for wrong keys/corrupted data).
        *   `KeyManagement` functions (key derivation, loading).
        *   `HashingService` for different algorithms.
        *   Frontend PQC verification logic for WASM modules (mocking `liboqs-js` or using test vectors).
        *   Configuration loading and validation (`GlobalConfig`).
    *   **Methodology:** Follow Test-Driven Development (TDD) principles where applicable. Use mock objects and test vectors for cryptographic operations.
    *   **Test Plans:** Detailed granular test plans are located in [`docs/test-plans/`](../../docs/test-plans/) (e.g., [`docs/test-plans/PQC_Data_At_Rest_Test_Plan.md`](../../docs/test-plans/PQC_Data_At_Rest_Test_Plan.md)).

*   **Acceptance Tests:**
    *   Located in [`tests/acceptance/`](../../tests/acceptance/).
    *   **Focus:** Verify end-to-end PQC functionality from a user or system perspective, aligning with the requirements in the PQC Specification documents and the [`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](../../docs/tests/PQC_Master_Acceptance_Test_Plan.md).
    *   Examples:
        *   Successfully loading a PQC-hybrid encrypted Beancount file.
        *   Correctly handling an attempt to load a PQC file with an incorrect passphrase.
        *   Verifying Fava operates correctly behind a PQC-TLS enabled proxy.
        *   Ensuring WASM module integrity check prevents loading of a tampered module.
        *   Confirming cryptographic agility by switching configured algorithms and verifying behavior.
    *   **Execution:** These tests are typically run on a fully integrated Fava application. Results are documented in reports like [`docs/reports/PQC_Acceptance_Test_Report_v1.1.md`](../../docs/reports/PQC_Acceptance_Test_Report_v1.1.md).

*   **Developer Responsibility:**
    *   Write granular tests for any new PQC-related code or modifications.
    *   Ensure all tests pass before committing changes.
    *   Consult relevant test plans and acceptance criteria when developing features.
    *   Consider performance implications and write tests to monitor NFRs if applicable (e.g., decryption/encryption speed, hashing speed, WASM verification speed).

## 11. Developer Best Practices & Considerations

*   **Security First:**
    *   Always handle cryptographic keys and sensitive material with extreme care. Minimize their time in memory and zeroize them when no longer needed.
    *   Do not hardcode keys, passphrases, or sensitive configuration. Use Fava's configuration system.
    *   Be cautious of side-channel vulnerabilities. Rely on well-vetted cryptographic libraries (`oqs-python`, `cryptography`, `liboqs-js`) that aim to mitigate these.
    *   Validate all inputs to cryptographic functions.
    *   Follow secure coding practices for all PQC-related development.
*   **Cryptographic Agility:**
    *   When adding new cryptographic functionality, design it to be configurable and abstracted via the `BackendCryptoService` or frontend facades.
    *   Avoid hardcoding algorithm choices directly in application logic.
*   **Library Usage:**
    *   Use the specified versions of `oqs-python`, `cryptography`, `liboqs-js`, and other crypto libraries as defined in the project dependencies (e.g., [`pyproject.toml`](../../pyproject.toml) for backend, `frontend/package.json` for frontend).
    *   Keep abreast of security advisories for these libraries and update them as necessary (following a proper testing and integration process).
*   **Error Handling & Logging:**
    *   Implement robust error handling for all PQC operations.
    *   Provide clear, informative log messages that can help administrators diagnose issues, but avoid logging sensitive data (like keys or full plaintexts).
    *   User-facing error messages should be understandable and guide the user without revealing internal cryptographic details that could be exploited.
*   **Performance:**
    *   Be mindful of the performance implications of PQC algorithms, which can be more computationally intensive than classical ones.
    *   Profile PQC operations where performance is critical (e.g., file loading, WASM verification).
    *   Optimize code paths if necessary, but prioritize security and correctness over micro-optimizations that could introduce vulnerabilities.
*   **Code Clarity & Documentation:**
    *   Write clear, well-commented code for all PQC-related modules.
    *   Update this Developer Guide and other relevant documentation (e.g., code comments, architecture diagrams) when making changes to PQC features.
*   **Testing:**
    *   Adhere to the project's testing strategy. Write comprehensive unit and integration tests for PQC functionalities.
*   **Cross-Platform Considerations:**
    *   Ensure PQC features work consistently across different operating systems and environments where Fava is supported. This is particularly relevant for dependencies like `oqs-python` which may have system-specific build requirements for `liboqs`.
*   **Build Process (for WASM Integrity):**
    *   The security of WASM integrity verification heavily relies on the security of the build process where the WASM module is signed. Ensure the private signing key is protected.

This concludes the PQC Developer Guide v1.1. Developers should refer to the linked specification, architecture, and pseudocode documents for more in-depth details on specific PQC features.