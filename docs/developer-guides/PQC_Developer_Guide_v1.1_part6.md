# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 6

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 6 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   Part 2: [PQC_Developer_Guide_v1.1_part2.md](PQC_Developer_Guide_v1.1_part2.md)
*   Part 3: [PQC_Developer_Guide_v1.1_part3.md](PQC_Developer_Guide_v1.1_part3.md)
*   Part 4: [PQC_Developer_Guide_v1.1_part4.md](PQC_Developer_Guide_v1.1_part4.md)
*   Part 5: [PQC_Developer_Guide_v1.1_part5.md](PQC_Developer_Guide_v1.1_part5.md)

This part details the PQC WASM Module Integrity features.

## 7. PQC WASM Module Integrity

Fava uses PQC digital signatures (Dilithium3 by default) to verify the integrity of its WebAssembly (WASM) modules, specifically `tree-sitter-beancount.wasm`, before loading them in the frontend.

### 7.1. Frontend Architecture for WASM Loading and PQC Signature Verification

As detailed in [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md):

*   **Core Services:**
    *   **`WasmLoaderService` (Conceptual: `frontend/src/lib/wasmLoader.ts` or integrated into `frontend/src/codemirror/beancount.ts`):**
        *   Orchestrates fetching the WASM module (e.g., `tree-sitter-beancount.wasm`) and its corresponding PQC signature file (e.g., `tree-sitter-beancount.wasm.dilithium3.sig`).
        *   Fetches PQC configuration (enabled status, public key, algorithm name) from `ConfigService`.
        *   If verification is enabled, calls `PqcVerificationService`.
        *   If verification succeeds, instantiates the WASM module.
        *   If verification fails or is disabled, handles fallback/error reporting via `NotificationService`.
    *   **`PqcVerificationService` (Conceptual: `frontend/src/lib/pqcCrypto.ts`):**
        *   Performs the actual Dilithium3 signature verification using `liboqs-js`.
        *   Takes WASM buffer, signature buffer, and public key as input.
    *   **`ConfigService` (Conceptual: `frontend/src/generated/pqcWasmConfig.ts`):**
        *   Provides PQC WASM configuration: `pqcWasmVerificationEnabled` (boolean), `pqcWasmPublicKeyDilithium3Base64` (string), `pqcWasmSignatureAlgorithmName` (string, e.g., "Dilithium3"), paths to WASM and signature files.
        *   This configuration is typically generated at build time and embedded in the frontend. The public key is exposed via the `/api/pqc_config` endpoint from [`src/fava/json_api.py`](../../src/fava/json_api.py).
    *   **`NotificationService` (Conceptual: `frontend/src/lib/notifications.ts`):**
        *   Informs the user of degraded functionality if WASM verification fails.

*   **Process Flow:**
    1.  `WasmLoaderService` is invoked to load the Beancount parser.
    2.  It fetches configuration from `ConfigService`.
    3.  If `pqcWasmVerificationEnabled` is true:
        *   Fetches WASM module and its `.sig` file.
        *   Calls `PqcVerificationService.verifyPqcWasmSignature()` with the module bytes, signature bytes, and public key.
        *   If verification is successful, logs success and proceeds to instantiate the WASM module.
        *   If verification fails, logs an error, notifies the user via `NotificationService` (e.g., "Parser integrity check failed, syntax features may be limited"), and does not load the WASM module.
    4.  If `pqcWasmVerificationEnabled` is false:
        *   Logs a warning that verification is disabled.
        *   Proceeds to fetch and instantiate the WASM module directly (without signature check).

*   **`liboqs-js` Integration:**
    *   The `PqcVerificationService` uses `liboqs-js` (specifically `OQS.Signature` for "Dilithium3") to perform the `verify` operation.
    *   The Base64 encoded public key from `ConfigService` is decoded to `Uint8Array` for use with `liboqs-js`.
    *   WASM module content and signature file content are also passed as `Uint8Array`.

### 7.2. Signature Generation and Management (Build Process Aspect)

While the runtime architecture focuses on verification, it relies on a secure build process:

*   **Signing:** During Fava's build/release process, the `tree-sitter-beancount.wasm` module is signed using a Dilithium3 private key. This produces the `.sig` file.
    *   Tools like `oqs-python` scripts or `liboqs` CLI utilities can be used for this.
*   **Public Key Distribution:** The corresponding Dilithium3 public key is Base64 encoded and embedded into the `ConfigService`'s data source (e.g., the generated `pqcWasmConfig.ts` file) and made available via the `/api/pqc_config` endpoint.
*   **Private Key Security:** The Dilithium3 private key used for signing MUST be kept highly secure within the build environment. Compromise of this key would allow attackers to sign malicious WASM modules that would pass verification.
*   **Artifacts:** The build process must ensure the WASM module, its `.sig` file, and the frontend code (with embedded public key config) are correctly packaged and distributed.

*   **Developer Notes:**
    *   The paths to the WASM module and its signature file are configurable via `ConfigService` to allow flexibility in deployment.
    *   Error handling in `WasmLoaderService` should be robust to network issues, missing files, or failures in the `liboqs-js` library itself.
    *   The performance of `liboqs-js` verification (NFR3.2 from spec) should be monitored. The target is <50ms.
    *   The impact of `liboqs-js` on frontend bundle size (NFR3.7 from spec) is a key consideration. A minimal build of `liboqs-js` containing only Dilithium3 is preferred.

---
End of Part 6. More content will follow in Part 7.