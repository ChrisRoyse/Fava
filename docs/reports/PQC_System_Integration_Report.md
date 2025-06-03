# PQC System Integration Report

**Version:** 1.0
**Date:** 2025-06-03
**Integrator:** System Integrator AI Mode

## 1. Introduction

This report details the integration of Post-Quantum Cryptography (PQC) features (Data at Rest, Data in Transit, Hashing, WASM Module Integrity, Cryptographic Agility) into Fava, following project documentation.

## 2. Overall Configuration & Initialization

PQC integration relies on centralized configuration and service initialization.

**Key Files & Modules:**
*   [`src/fava/core/fava_options.py`](src/fava/core/fava_options.py): Defines/parses `FAVA_CRYPTO_SETTINGS`.
*   [`src/fava/pqc/global_config.py`](src/fava/pqc/global_config.py): Loads/validates/caches `FAVA_CRYPTO_SETTINGS`.
*   [`src/fava/pqc/app_startup.py`](src/fava/pqc/app_startup.py): Initializes `BackendCryptoService` and registers handlers.
*   [`src/fava/application.py`](src/fava/application.py): Calls PQC startup logic, stores PQC app config.
*   [`src/fava/json_api.py`](src/fava/json_api.py): New API endpoint to expose relevant `FAVA_CRYPTO_SETTINGS` to frontend.
*   [`frontend/src/generated/pqcWasmConfig.ts`](frontend/src/generated/pqcWasmConfig.ts): Build-time generated or dynamically populated WASM PQC config.

**Integration Steps:**
1.  **Extend `FavaOptions`**: Add parsing for `FAVA_CRYPTO_SETTINGS`.
2.  **Implement `GlobalConfig`**: Ensure loading/validation of `FAVA_CRYPTO_SETTINGS`.
3.  **Integrate PQC Startup**: Call `initialize_backend_crypto_service()` in `create_app` ([`src/fava/application.py`](src/fava/application.py)).
4.  **Expose Frontend Config**: Create API endpoint in [`src/fava/json_api.py`](src/fava/json_api.py); frontend fetches/caches this.

**Challenges:** Schema definition for `FAVA_CRYPTO_SETTINGS`; config file path resolution; robust error handling for PQC settings.

## 3. Data at Rest Integration

**Key Files & Modules:**
*   Backend: [`src/fava/core/ledger.py`](src/fava/core/ledger.py), [`src/fava/core/file.py`](src/fava/core/file.py), [`src/fava/pqc/backend_crypto_service.py`](src/fava/pqc/backend_crypto_service.py), [`src/fava/crypto/locator.py`](src/fava/crypto/locator.py), `fava.crypto.keys`.
*   Config: `data_at_rest` in `FAVA_CRYPTO_SETTINGS`.

**Integration Steps:**
1.  **Modify `FavaLedger.load_file`**: Use `CryptoServiceLocator` -> `BackendCryptoService.decrypt_data_at_rest_with_agility()`.
2.  **Implement `FavaLedger.save_file_pqc`**: Use `BackendCryptoService.get_active_encryption_handler()`.
3.  **Key Management**: Implement `_get_key_material_for_operation` in `FavaLedger` using `fava.crypto.keys`.
4.  **Handler Registration**: In [`src/fava/pqc/app_startup.py`](src/fava/pqc/app_startup.py), register `HybridPqcCryptoHandler`, GPG handler.

**Challenges:** Seamless PQC decryption flow in `load_file`; secure passphrase handling; `EncryptedFileBundle` format consistency.

## 4. Data in Transit Integration

**Key Files & Modules:**
*   Backend: [`src/fava/application.py`](src/fava/application.py), [`src/fava/pqc/proxy_awareness.py`](src/fava/pqc/proxy_awareness.py), [`src/fava/pqc/configuration_validator.py`](src/fava/pqc/configuration_validator.py).
*   Docs: Build process for proxy guides.
*   Config: `assume_pqc_tls_proxy_enabled`, `pqc_tls_embedded_server_kems`.

**Integration Steps:**
1.  **Proxy Awareness Logging**: In `_perform_global_filters` ([`src/fava/application.py`](src/fava/application.py)), call `determine_effective_pqc_status()`.
2.  **Embedded Server KEM Validation**: In `create_app` ([`src/fava/application.py`](src/fava/application.py)), call `validate_pqc_tls_embedded_server_options()`.
3.  **Documentation Generation**: Build-time step using [`src/fava/pqc/documentation_generator.py`](src/fava/pqc/documentation_generator.py).

**Challenges:** Implementing `detect_available_python_pqc_kems`; build pipeline for docs.

## 5. Hashing Integration

**Key Files & Modules:**
*   Backend: [`src/fava/core/file.py`](src/fava/core/file.py), hashing service in `BackendCryptoService` or `HashingProvider`.
*   Frontend: [`frontend/src/editor/SliceEditor.svelte`](frontend/src/editor/SliceEditor.svelte), hashing abstraction (e.g., [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts)).
*   Config: `hashing.default_algorithm` in `FAVA_CRYPTO_SETTINGS`.

**Integration Steps:**
1.  **Backend Hashing Service**: Initialize with `default_algorithm`. Modify [`src/fava/core/file.py`](src/fava/core/file.py) and editor save logic to use this service.
2.  **Frontend Hashing Abstraction**: Implement `calculateConfiguredHash` in [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts) (fetches config via API). Modify [`frontend/src/editor/SliceEditor.svelte`](frontend/src/editor/SliceEditor.svelte) to use it.
3.  **Config Propagation**: API endpoint in [`src/fava/json_api.py`](src/fava/json_api.py) exposes `hashing.default_algorithm`.

**Challenges:** Consistent UTF-8 encoding; frontend `js-sha3` dependency and performance.

## 6. WASM Module Integrity Integration

**Key Files & Modules:**
*   Frontend: [`frontend/src/lib/wasmLoader.ts`](frontend/src/lib/wasmLoader.ts), [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts), [`frontend/src/generated/pqcWasmConfig.ts`](frontend/src/generated/pqcWasmConfig.ts), [`frontend/src/lib/pqcOqsInterfaces.ts`](frontend/src/lib/pqcOqsInterfaces.ts).
*   Build Process: Signs WASM, generates `pqcWasmConfig.ts`.

**Integration Steps:**
1.  **WASM Loader Update**: Ensure `loadBeancountParserWithPQCVerification` uses `verifyPqcWasmSignature` and config from `pqcWasmConfig.ts`.
2.  **`liboqs-js` Integration**: [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts) uses global `OQS.Signature`.
3.  **Configuration File**: Build process generates `pqcWasmConfig.ts` with actual public key.
4.  **Error Handling**: `wasmLoader.ts` calls `notifications.notifyUIDegradedFunctionality`.

**Challenges:** Build process for signing and public key generation; `liboqs-js` bundling; replacing placeholder public key.

## 7. Cryptographic Agility Integration

**Key Files & Modules:**
*   Backend: [`src/fava/pqc/backend_crypto_service.py`](src/fava/pqc/backend_crypto_service.py), [`src/fava/pqc/global_config.py`](src/fava/pqc/global_config.py), [`src/fava/pqc/app_startup.py`](src/fava/pqc/app_startup.py).
*   Frontend: `FrontendCryptoFacade` (e.g., in [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts)).
*   Config: `FAVA_CRYPTO_SETTINGS`.

**Integration Steps:**
1.  **Backend Agility**: `app_startup.py` registers handlers from `FAVA_CRYPTO_SETTINGS`. `BackendCryptoService` uses `active_encryption_suite_id` and `decryption_attempt_order`. `decrypt_data_at_rest_with_agility` uses bundle metadata.
2.  **Frontend Agility**: Hashing abstraction fetches `hashing.default_algorithm`. WASM verification currently fixed to Dilithium3 via `pqcWasmConfig.ts`.
3.  **Config as Source of Truth**: All crypto choices driven by `FAVA_CRYPTO_SETTINGS`.

**Challenges:** Robust parsing/validation of `FAVA_CRYPTO_SETTINGS`; `suite_id_used` management in bundles; mapping suite configs to handlers.

## 8. Integration Issues & Resolutions (Anticipated Summary)

*   **Configuration Schema:** Define canonical `FAVA_CRYPTO_SETTINGS` schema.
*   **Library Dependencies:** Update project dependencies; ensure frontend bundling.
*   **Placeholder Values:** Implement build steps to replace placeholders (e.g., WASM public key).
*   **Performance:** Conduct testing; optimize if needed.
*   **Error Handling:** Ensure granular and informative PQC-specific error handling.

## 9. Verification of Basic Interactions (Conceptual Plan Summary)

*   **Data@Rest:** Encrypt/decrypt with PQC hybrid; test incorrect key failure.
*   **Hashing:** Configure SHA3-256/SHA256; test frontend/backend consistency in editor save.
*   **WASM Integrity:** Test successful verification, tampered signature failure, disabled verification mode.
*   **Agility:** Test decryption of old suite data after active suite changes.

## 10. Status of System Cohesion

Integration is planned. Cohesion relies on `FAVA_CRYPTO_SETTINGS`, `BackendCryptoService`, `FrontendCryptoFacade`, and consistent error handling.

## 11. List of Modified or Created Files (Anticipated Summary)

**Modified:** [`src/fava/core/fava_options.py`](src/fava/core/fava_options.py), [`src/fava/application.py`](src/fava/application.py), [`src/fava/core/ledger.py`](src/fava/core/ledger.py), [`src/fava/core/file.py`](src/fava/core/file.py), [`src/fava/json_api.py`](src/fava/json_api.py), [`src/fava/crypto/locator.py`](src/fava/crypto/locator.py), [`frontend/src/lib/wasmLoader.ts`](frontend/src/lib/wasmLoader.ts), [`frontend/src/editor/SliceEditor.svelte`](frontend/src/editor/SliceEditor.svelte), build scripts, dependency files.
**Potentially Created/Expanded:** Modules in `src/fava/pqc/`, [`frontend/src/lib/pqcCrypto.ts`](frontend/src/lib/pqcCrypto.ts), [`frontend/src/generated/pqcWasmConfig.ts`](frontend/src/generated/pqcWasmConfig.ts), `config/fava_crypto_settings.py`.

This report outlines the planned integration.