# PQC Integration Specification: WASM Module Integrity

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document specifies the requirements for enhancing the integrity verification of WebAssembly (WASM) modules used in Fava, specifically the `tree-sitter-beancount.wasm` parser, using Post-Quantum Cryptography (PQC) digital signatures. This aims to provide stronger assurance against tampering compared to Subresource Integrity (SRI) alone, especially if WASM modules could be served from less trusted sources or CDNs in some deployment scenarios.

This specification is based on the PQC integration plan ([`docs/Plan.MD`](../../docs/Plan.MD)), research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure that the WASM modules loaded by Fava's frontend are authentic and have not been maliciously altered.

## 2. Functional Requirements

*   **FR2.1:** During Fava's build/release process, the `tree-sitter-beancount.wasm` module MUST be digitally signed using a NIST-selected PQC digital signature algorithm (e.g., CRYSTALS-Dilithium).
*   **FR2.2:** The PQC public key corresponding to the private key used for signing MUST be distributed with the Fava frontend.
*   **FR2.3:** The PQC signature of the WASM module MUST be distributed alongside the WASM module itself (e.g., as `tree-sitter-beancount.wasm.sig`).
*   **FR2.4:** Before Fava's frontend instantiates the `tree-sitter-beancount.wasm` module, it MUST fetch the WASM binary and its corresponding PQC signature.
*   **FR2.5:** The frontend MUST verify the PQC signature of the WASM binary against the distributed PQC public key using a PQC signature verification function (likely from a JS/WASM PQC library).
*   **FR2.6:** If PQC signature verification succeeds, the WASM module MUST be loaded and used as normal.
*   **FR2.7:** If PQC signature verification fails (e.g., invalid signature, tampered WASM, wrong public key), the WASM module MUST NOT be loaded, and an error MUST be logged to the console. Fava's parsing functionality dependent on this WASM module will be unavailable or degraded, and this state should be clearly indicated to the user if possible (e.g., "Beancount syntax highlighting/parsing unavailable due to integrity check failure").
*   **FR2.8:** The PQC signature algorithm and public key management SHOULD allow for updates (e.g., if algorithms change or keys need to be rotated), though the mechanism for this is primarily a build/release process concern.
*   **FR2.9:** The system SHOULD allow for disabling PQC WASM signature verification via a configuration option (e.g., for development or specific debugging scenarios), but verification MUST be enabled by default in production builds.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC digital signature scheme used (e.g., CRYSTALS-Dilithium) MUST be implemented correctly, adhering to its standard. The private signing key MUST be kept secure.
*   **NFR3.2 (Performance):** PQC signature verification in the frontend SHOULD be performant enough not to noticeably delay Fava's startup or the availability of features dependent on the WASM module. Target: Verification time < 100-200ms on typical client hardware.
*   **NFR3.3 (Usability - User):** WASM integrity verification should be transparent to the end-user if successful. If it fails, the impact (e.g., loss of syntax highlighting) should be clear.
*   **NFR3.4 (Reliability):** PQC signature verification MUST be reliable, consistently verifying valid signatures and rejecting invalid ones.
*   **NFR3.5 (Maintainability):** The frontend PQC verification logic (in `frontend/src/lib/crypto.ts` or similar) MUST be modular. Updating the PQC public key or signature algorithm (if necessary) should be straightforward.
*   **NFR3.6 (Cryptographic Agility):** The system should be designed to potentially support different PQC signature algorithms in the future, managed by the build process and corresponding frontend verification logic. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))
*   **NFR3.7 (Frontend Bundle Size):** The JS/WASM PQC library used for signature verification SHOULD have a minimal impact on the overall frontend bundle size.

## 4. User Stories

*   **US4.1:** As a Fava user, I want the Fava application to verify the integrity of its WebAssembly parser using PQC digital signatures before using it, so I can be confident it hasn't been tampered with.
*   **US4.2:** As a Fava developer/maintainer, I want the Fava build process to automatically sign the WASM parser with a PQC digital signature so that it can be verified by the frontend.
*   **US4.3:** As a Fava user, if the WASM parser fails its PQC integrity check, I want to be informed (e.g., via a console error and potentially a UI indication that some features are degraded) rather than the application silently using a potentially compromised component.

## 5. Use Cases

### 5.1. Use Case: Frontend Verifies and Loads PQC-Signed WASM Module (Happy Path)

*   **Actor:** Fava Frontend
*   **Preconditions:**
    *   `tree-sitter-beancount.wasm` is available.
    *   `tree-sitter-beancount.wasm.sig` (PQC signature for the WASM file) is available.
    *   Fava's PQC public key for WASM verification is embedded in the frontend.
    *   A JS/WASM PQC signature verification library (e.g., `liboqs-js` supporting Dilithium) is available to the frontend.
    *   PQC WASM verification is enabled.
*   **Main Flow:**
    1.  Frontend logic (e.g., in `frontend/src/codemirror/beancount.ts` before `TSLanguage.load()`) initiates loading of the Beancount parser.
    2.  It fetches `tree-sitter-beancount.wasm` (as `wasmBuffer`).
    3.  It fetches `tree-sitter-beancount.wasm.sig` (as `signatureBuffer`).
    4.  It retrieves the embedded Fava PQC public key (`pqcPublicKey`).
    5.  It calls `pqcVerifySignature(pqcPublicKey, wasmBuffer, signatureBuffer)` using the PQC library.
    6.  The PQC library verifies the signature. Verification succeeds.
    7.  The frontend proceeds to load/initialize the WASM module using the verified `wasmBuffer`.
    8.  A success message is logged to the console (e.g., "WASM module 'tree-sitter-beancount.wasm' PQC signature verified successfully.").
*   **Postconditions:**
    *   The WASM parser is loaded and functional.
    *   Fava features relying on the parser (e.g., syntax highlighting, advanced editing features) are enabled.

### 5.2. Use Case: Frontend Fails to Verify PQC-Signed WASM Module (Invalid Signature)

*   **Actor:** Fava Frontend
*   **Preconditions:**
    *   Same as 5.1, but `tree-sitter-beancount.wasm` has been tampered with, or `tree-sitter-beancount.wasm.sig` is an invalid signature for the WASM file.
*   **Main Flow:**
    1.  Frontend fetches WASM binary and signature (Steps 1-4 from 5.1).
    2.  It calls `pqcVerifySignature(pqcPublicKey, wasmBuffer, signatureBuffer)`.
    3.  PQC signature verification fails.
    4.  The frontend logs an error (e.g., "ERROR: WASM module 'tree-sitter-beancount.wasm' PQC signature verification FAILED. Module not loaded.").
    5.  The WASM module is NOT loaded or initialized.
    6.  (Optional) A UI indication might show that parser-dependent features are unavailable.
*   **Postconditions:**
    *   The WASM parser is not loaded.
    *   Fava features relying on the parser are disabled or degraded.
    *   Fava application itself remains operational but with reduced functionality.

### 5.3. Use Case: PQC WASM Verification Disabled

*   **Actor:** Fava Frontend
*   **Preconditions:**
    *   PQC WASM signature verification is disabled via a configuration flag.
*   **Main Flow:**
    1.  Frontend logic checks the configuration flag.
    2.  Verification steps (fetching signature, calling `pqcVerifySignature`) are skipped.
    3.  The frontend proceeds to load/initialize the WASM module directly from the fetched `wasmBuffer`.
    4.  A warning might be logged to the console indicating that WASM integrity verification is disabled.
*   **Postconditions:**
    *   The WASM parser is loaded (assuming it's otherwise valid).
    *   Security assurance from PQC signature is bypassed.

## 6. Edge Cases & Error Handling

*   **EC6.1:** WASM signature file (`.sig`) is missing: Verification should fail. Frontend should log an error and not load the WASM.
*   **EC6.2:** Embedded PQC public key is corrupted or malformed: Verification will likely fail. This is a critical deployment error.
*   **EC6.3:** PQC JS/WASM library for verification fails to load or initialize: Verification cannot proceed. Frontend should log an error and not load the WASM.
*   **EC6.4:** Network error while fetching WASM or signature file: Standard network error handling. Verification cannot proceed.
*   **EC6.5:** Extremely large WASM file (not expected for tree-sitter parsers): PQC signature verification time might become noticeable.
*   **EC6.6:** Incompatible versions of PQC algorithm between signing (build time) and verification (runtime in frontend): Verification will fail.

## 7. Constraints

*   **C7.1:** Frontend PQC signature verification will rely on a JavaScript/WASM PQC library (e.g., `liboqs-js` or similar) capable of handling the chosen PQC signature algorithm (e.g., Dilithium).
*   **C7.2:** The build process must incorporate steps to PQC-sign the WASM module and include the signature and public key in the Fava distribution.
*   **C7.3:** Performance of PQC signature verification in the browser must be acceptable (NFR3.2).
*   **C7.4:** The size of the PQC signature and public key, and the PQC JS library, will contribute to the overall frontend assets size.

## 8. Data Models (if applicable)

### 8.1. PQC WASM Verification Configuration (Conceptual)

*   Stored as part of Fava's frontend build configuration or runtime options exposed to the frontend:
    *   `pqc_wasm_verification_enabled`: boolean (Default: true in production, false in dev potentially)
    *   `pqc_wasm_public_key_pem_or_jwk`: string (The embedded PQC public key)
    *   `pqc_wasm_signature_algorithm_name`: string (e.g., "Dilithium2", "Falcon512" - for informational or future agility purposes, the key itself often implies the algorithm)

### 8.2. Distributed Files

*   `tree-sitter-beancount.wasm`: The WebAssembly binary.
*   `tree-sitter-beancount.wasm.sig`: The PQC signature of the WASM binary.

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (Successful Verification):** Transparent to the user. Fava works as expected.
*   **UI9.2 (Failed Verification):**
    *   Primary feedback: Console error message detailing the failure.
    *   Secondary feedback (optional, if deemed important): A subtle, non-intrusive UI indicator that some advanced editor features might be unavailable due to a parser integrity issue. This should not block core Fava usage if possible. For example, basic text editing might still work, but syntax highlighting fails.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. Frontend PQC Signature Verification (`frontend/src/lib/crypto.ts` or similar)

```typescript
// In frontend/src/lib/pqcCrypto.ts (conceptual new file or part of crypto.ts)

// interface PQCVerificationLib {
//   verify(publicKeyBytes: Uint8Array, messageBytes: Uint8Array, signatureBytes: Uint8Array, algorithm: string): Promise<boolean>;
// }
// let pqcLib: PQCVerificationLib; // Loaded dynamically, e.g., liboqs-js

// async function initializePQCLib() {
//   // Dynamically import and initialize liboqs-js or similar
//   // pqcLib = await import('liboqs-js').then(lib => new lib.Signature('Dilithium2')); // Example
//   throw new Error("PQC Lib initialization stub");
// }

// export async function verifyPqcWasmSignature(
//   wasmBuffer: ArrayBuffer,
//   signatureBuffer: ArrayBuffer,
//   publicKeyPem: string, // Or raw key bytes
//   algorithmName: string // e.g., "Dilithium2"
// ): Promise<boolean> {
//   // if (!pqcLib) await initializePQCLib();

//   // const publicKeyBytes = ...; // Convert PEM/JWK to raw bytes recognized by the PQC lib
//   // const messageBytes = new Uint8Array(wasmBuffer);
//   // const sigBytes = new Uint8Array(signatureBuffer);

//   // return await pqcLib.verify(publicKeyBytes, messageBytes, sigBytes, algorithmName);
//   throw new Error("verifyPqcWasmSignature stub");
// }

// TEST (e.g., Vitest/Jest): test_verifyPqcWasmSignature_valid_signature()
//   SETUP:
//     Mock `fetch` to return known good WASM buffer and its valid PQC signature buffer.
//     Provide a known good PQC public key (matching the signature).
//     Mock the PQC verification library (e.g., `liboqs-js Dilithium.verify`) to return `true`.
//   ACTION: Call `verifyPqcWasmSignature(wasmBuffer, sigBuffer, pubKey, "Dilithium2")`.
//   ASSERT: Returns `true`.

// TEST: test_verifyPqcWasmSignature_invalid_signature()
//   SETUP:
//     Mock `fetch` for WASM buffer and an INVALID signature buffer.
//     Provide the correct PQC public key.
//     Mock PQC lib `verify` to return `false`.
//   ACTION: Call `verifyPqcWasmSignature(wasmBuffer, invalidSigBuffer, pubKey, "Dilithium2")`.
//   ASSERT: Returns `false`.
```

### 10.2. WASM Loader Integration (`frontend/src/codemirror/beancount.ts`)

```typescript
// In frontend/src/codemirror/beancount.ts (conceptual modification)

// async function loadBeancountParserWithPQCVerification() {
//   // const wasmPath = new URL("./tree-sitter-beancount.wasm", import.meta.url).href;
//   // const signaturePath = new URL("./tree-sitter-beancount.wasm.sig", import.meta.url).href;
//   // const favaPqcConfig = getFavaPqcConfig(); // From global state or options API

//   // if (!favaPqcConfig.pqcWasmVerificationEnabled) {
//   //   console.warn("PQC WASM signature verification is disabled.");
//   //   return await TSLanguage.load(wasmPath); // Load directly
//   // }

//   // try {
//   //   const [wasmRes, sigRes] = await Promise.all([fetch(wasmPath), fetch(signaturePath)]);
//   //   if (!wasmRes.ok || !sigRes.ok) {
//   //     throw new Error(`Failed to fetch WASM/signature: ${wasmRes.status}, ${sigRes.status}`);
//   //   }
//   //   const wasmBuffer = await wasmRes.arrayBuffer();
//   //   const signatureBuffer = await sigRes.arrayBuffer();

//   //   const isValid = await verifyPqcWasmSignature(
//   //     wasmBuffer,
//   //     signatureBuffer,
//   //     favaPqcConfig.pqcWasmPublicKey,
//   //     favaPqcConfig.pqcWasmSignatureAlgorithm
//   //   );

//   //   if (isValid) {
//   //     console.info("WASM PQC signature verified successfully.");
//   //     // For TSLanguage.load, it might expect a path or a pre-initialized module.
//   //     // If TSLanguage.load can take a buffer, that's ideal.
//   //     // Otherwise, this logic needs to fit how tree-sitter/web-tree-sitter loads WASM.
//   //     // One way: TSLanguage.load uses fetch internally. We might need to intercept that
//   //     // or use a lower-level Parser.init() with the verified buffer.
//   //     // This part needs careful integration with web-tree-sitter's API.
//   //     // Assuming Parser.init() and TSLanguage.load(buffer) for now:
//   //     await Parser.init({ /* ... options ... */ }); // General tree-sitter init
//   //     const lang = await TSLanguage.load(wasmBuffer); // Pass verified buffer
//   //     return lang;
//   //   } else {
//   //     console.error("WASM PQC signature verification FAILED. Parser not loaded.");
//   //     throw new Error("WASM PQC signature verification failed.");
//   //   }
//   // } catch (error) {
//   //   console.error("Error during WASM PQC verification or loading:", error);
//   //   // Fallback or error state for Fava UI
//   //   return null; // Or throw to be caught by higher-level error handler
//   // }
// }


// TEST (e.g., Vitest/Jest integration): test_loadBeancountParser_succeeds_with_valid_pqc_signature()
//   SETUP:
//     Mock `fetch` for WASM and signature.
//     Mock `verifyPqcWasmSignature` to return `true`.
//     Mock `TSLanguage.load` and `Parser.init` to check they are called correctly.
//     Set `pqcWasmVerificationEnabled` to true.
//   ACTION: Call `loadBeancountParserWithPQCVerification()`.
//   ASSERT: `TSLanguage.load` is called with the WASM buffer. No errors thrown. Console info logged.

// TEST: test_loadBeancountParser_fails_with_invalid_pqc_signature()
//   SETUP:
//     Mock `fetch`.
//     Mock `verifyPqcWasmSignature` to return `false`.
//     Spy on `TSLanguage.load` (should not be called).
//     Set `pqcWasmVerificationEnabled` to true.
//   ACTION: Call `loadBeancountParserWithPQCVerification()`.
//   ASSERT: `TSLanguage.load` is NOT called. Error is thrown or null returned. Console error logged.

// TEST: test_loadBeancountParser_skips_verification_if_disabled()
//   SETUP:
//     Mock `fetch`.
//     Spy on `verifyPqcWasmSignature` (should not be called).
//     Mock `TSLanguage.load`.
//     Set `pqcWasmVerificationEnabled` to false.
//   ACTION: Call `loadBeancountParserWithPQCVerification()`.
//   ASSERT: `verifyPqcWasmSignature` is NOT called. `TSLanguage.load` is called. Console warn logged.
```

### 10.3. Build Process Stub (Conceptual - e.g., in a Makefile or release script)

```bash
# Conceptual commands in a release script

# PQC_SIGNING_KEY="path/to/fava_pqc_wasm_signing_private.key"
# PQC_SIGN_ALGORITHM="Dilithium2" # Or as understood by the PQC signing tool
# WASM_FILE="frontend/public/tree-sitter-beancount.wasm" # Path after build
# SIG_FILE="frontend/public/tree-sitter-beancount.wasm.sig"
# PUBLIC_KEY_OUTPUT="frontend/src/generated/pqcWasmPublicKey.ts" # To embed in frontend

# # Step 1: Sign the WASM file
# pqc-signing-tool sign --key "${PQC_SIGNING_KEY}" \
#                       --algorithm "${PQC_SIGN_ALGORITHM}" \
#                       --in "${WASM_FILE}" \
#                       --out "${SIG_FILE}"

# # Step 2: Extract/format public key for embedding in frontend
# pqc-signing-tool export-public --key "${PQC_SIGNING_KEY}" \
#                                --format "pem_for_frontend_lib" \
#                                --out - > temp_public_key.pem
# echo "export const pqcWasmPublicKey = \`$(cat temp_public_key.pem)\`;" > "${PUBLIC_KEY_OUTPUT}"
# echo "export const pqcWasmSignatureAlgorithm = '${PQC_SIGN_ALGORITHM}';" >> "${PUBLIC_KEY_OUTPUT}"
# rm temp_public_key.pem

# TEST (Build process): test_build_produces_signed_wasm_and_public_key()
#   ACTION: Run the build/release script steps related to WASM signing.
#   ASSERT:
#     - `${SIG_FILE}` is created and is not empty.
#     - `${PUBLIC_KEY_OUTPUT}` is created and contains a public key string and algorithm name.
#     - (Manual/Advanced) Optionally, verify the generated signature against the WASM and public key using a trusted PQC tool.
```

## 11. Dependencies

*   **External Libraries (Frontend):**
    *   A JavaScript/WASM PQC signature verification library (e.g., `liboqs-js` supporting Dilithium/Falcon).
*   **External Tools (Build Process):**
    *   A command-line PQC signing tool compatible with the chosen PQC signature algorithm and the verification library. This might come from `liboqs` or another PQC SDK.
*   **Internal Fava Modules:**
    *   `frontend/src/codemirror/beancount.ts`: Needs modification to integrate the verification logic before loading the WASM.
    *   `frontend/src/lib/pqcCrypto.ts` (or similar): New module for frontend PQC signature verification abstraction.
    *   Fava's build scripts (`Makefile`, `pyproject.toml` tasks, etc.): Need to incorporate the WASM signing step.
    *   Frontend configuration mechanism to enable/disable verification and provide the public key.

## 12. Integration Points

*   **IP12.1 (Fava Build Process):** A new step in the build/release pipeline to PQC-sign the `tree-sitter-beancount.wasm` file and prepare the public key for frontend embedding.
*   **IP12.2 (Frontend WASM Loading):** The logic in `frontend/src/codemirror/beancount.ts` (or wherever `tree-sitter-beancount.wasm` is loaded) must be modified to:
    1.  Fetch the WASM binary and its `.sig` file.
    2.  Call the PQC verification function from `frontend/src/lib/pqcCrypto.ts`.
    3.  Conditionally load the WASM based on verification success.
*   **IP12.3 (Frontend PQC Crypto Library):** The chosen JS/WASM PQC library needs to be integrated into the frontend, providing the `verifyPqcWasmSignature` functionality.
*   **IP12.4 (Frontend Configuration):** A mechanism to provide the embedded public key and potentially enable/disable verification for the frontend logic.