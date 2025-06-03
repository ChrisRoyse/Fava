# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 11

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 11 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   ... (Parts 2-9) ...
*   Part 10: [PQC_Developer_Guide_v1.1_part10.md](PQC_Developer_Guide_v1.1_part10.md)

This part continues detailing Fava's Cryptographic Agility Framework and API Documentation.

## 8. Cryptographic Agility Framework - Continued

### 8.3. Management of Multiple Decryption Suites for Data at Rest - Continued

Continuing from Part 10:

*   **Iterative Fallback using `decryption_attempt_order`:**
    *   If the `EncryptedFileBundle` does not contain a `suite_id_used` (e.g., it's an older format or a non-Fava encrypted file like a GPG file), or if the targeted decryption attempt with the `suite_id_used` fails (e.g., incorrect key for that suite), Fava then consults the `FAVA_CRYPTO_SETTINGS.data_at_rest.decryption_attempt_order` list.
    *   The `BackendCryptoService` (conceptually in `src/fava/pqc/backend_crypto_service.py`) provides `CryptoHandler` instances for each `suite_id` in this list, in the specified order.
    *   Fava iterates through these handlers, attempting to decrypt the file with each one until:
        *   Decryption is successful.
        *   All handlers in the list have been tried and failed.
    *   This mechanism allows Fava to open files encrypted with different (but still supported and configured) cryptographic suites, including falling back to classical GPG if it's in the `decryption_attempt_order` list and a `GpgCryptoHandler` is registered.

*   **Developer Notes for Decryption Agility:**
    *   The `CryptoHandler.can_handle()` method (see Part 1, Section 3.1) can play a role in quickly disqualifying handlers during the iterative fallback if file metadata (e.g., magic numbers for GPG files, specific bundle version markers) can give clues, reducing unnecessary decryption attempts. However, for Fava-PQC-hybrid bundles, the `suite_id_used` field is the primary mechanism for direct suite identification.
    *   Clear logging is important to trace which cryptographic suites were attempted during a decryption operation, especially if multiple fallbacks occur. This aids in troubleshooting and understanding system behavior.
    *   The order in `decryption_attempt_order` matters. More common or recent suites should generally be listed earlier if `suite_id_used` is not available or fails, to optimize decryption time for the most likely scenarios.

## 9. API Documentation

As part of the PQC integration, certain backend configurations are exposed to the frontend via an API endpoint. This is crucial for features like frontend hashing consistency and WASM module integrity verification.

*   **Endpoint:** `/api/pqc_config` (or a similar path integrated into existing settings endpoints like `/api/fava/settings`).
    *   This endpoint is served by [`src/fava/json_api.py`](../../src/fava/json_api.py).
*   **Purpose:** To provide the frontend with necessary PQC-related configuration values that are managed on the backend.
*   **Key Data Exposed (Conceptual JSON Response):**
    ```json
    {
        "hashing": {
            "default_algorithm": "SHA3-256" // From FAVA_CRYPTO_SETTINGS.hashing.default_algorithm
        },
        "wasm_integrity": {
            "verification_enabled": true, // From FAVA_CRYPTO_SETTINGS.wasm_integrity.verification_enabled
            "public_key_dilithium3_base64": "BASE64_ENCODED_DILITHIUM3_PUBLIC_KEY", // From FAVA_CRYPTO_SETTINGS
            "signature_algorithm": "Dilithium3", // From FAVA_CRYPTO_SETTINGS
            "module_path": "/static/wasm/tree-sitter-beancount.wasm", // Example path
            "signature_path_suffix": ".dilithium3.sig" // Example suffix
        }
        // Other PQC-related frontend-relevant settings could be added here if needed.
    }
    ```
*   **Frontend Usage:**
    *   The `FrontendCryptoFacade` (conceptual: `frontend/src/lib/pqcCryptoFacade.ts`) fetches this configuration on initialization or as needed.
    *   The `hashing.default_algorithm` is used by the frontend `calculateHash` function to select the correct hashing implementation (SHA3-256 or SHA-256).
    *   The `wasm_integrity` settings are used by the `WasmLoaderService` and `PqcVerificationService` (conceptual: `frontend/src/lib/wasmLoader.ts` and `frontend/src/lib/pqcCrypto.ts`) to perform PQC signature verification of the WASM module.
*   **Developer Notes:**
    *   The API endpoint should be read-only from the frontend's perspective.
    *   Ensure that only necessary and non-sensitive configuration is exposed. For instance, private keys or detailed internal suite parameters should not be part of this API response.
    *   The structure of the JSON response should be stable and versioned if significant changes are anticipated.
    *   The frontend should implement appropriate error handling if the API call fails or returns unexpected data, potentially falling back to secure defaults (e.g., for hashing algorithm if config is unavailable).

---
End of Part 11. More content will follow in Part 12.