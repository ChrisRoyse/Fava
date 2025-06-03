# PQC Integration Specification: WASM Module Integrity

**Version:** 1.1
**Date:** 2025-06-02

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on new research findings and Devil's Advocate critique. Key changes include:
    *   Specified Dilithium3 as the default PQC signature algorithm.
    *   Updated performance NFRs based on research (`pf_wasm_pqc_sri_PART_1.md`, `pf_pqc_js_wasm_libs_g3_3_PART_1.md`).
    *   Acknowledged reliance on `liboqs-js` for frontend verification and `oqs-python` or `liboqs` CLI tools for build-time signing.
    *   Refined TDD anchors and build process stub.
    *   Addressed contingency for PQC CLI signing tools (`pf_pqc_cli_signing_tools_g4_3_PART_1.md`, `pf_tooling_contingency_PART_1.md`).
*   **1.0 (2025-06-02):** Initial version.

## 1. Introduction

This document specifies the requirements for enhancing the integrity verification of WebAssembly (WASM) modules used in Fava, specifically the `tree-sitter-beancount.wasm` parser, using Post-Quantum Cryptography (PQC) digital signatures. This aims to provide stronger assurance against tampering compared to Subresource Integrity (SRI) alone.

This specification is based on the PQC integration plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)), research findings ([`docs/research/`](../../docs/research/), particularly `pf_wasm_pqc_sri_PART_1.md`, `pf_pqc_js_wasm_libs_g3_3_PART_1.md`, `pf_pqc_cli_signing_tools_g4_3_PART_1.md`), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure that the WASM modules loaded by Fava's frontend are authentic and have not been maliciously altered, using a PQC signature scheme like ML-DSA/Dilithium.

## 2. Functional Requirements

*   **FR2.1:** During Fava's build/release process, the `tree-sitter-beancount.wasm` module MUST be digitally signed using ML-DSA/Dilithium3 (NIST Level 3 PQC digital signature algorithm).
*   **FR2.2:** The PQC public key (Dilithium3) corresponding to the private key used for signing MUST be securely distributed with the Fava frontend (e.g., embedded in JavaScript or fetched from a trusted Fava API endpoint).
*   **FR2.3:** The PQC signature of the WASM module MUST be distributed alongside the WASM module itself (e.g., as `tree-sitter-beancount.wasm.dilithium3.sig`).
*   **FR2.4:** Before Fava's frontend instantiates the `tree-sitter-beancount.wasm` module, it MUST fetch the WASM binary and its corresponding PQC signature.
*   **FR2.5:** The frontend MUST verify the PQC signature of the WASM binary against the distributed PQC public key using a PQC signature verification function from a JS/WASM PQC library (e.g., `liboqs-js`).
*   **FR2.6:** If PQC signature verification succeeds, the WASM module MUST be loaded and used as normal.
*   **FR2.7:** If PQC signature verification fails (e.g., invalid signature, tampered WASM, wrong public key), the WASM module MUST NOT be loaded. An error MUST be logged to the console, and Fava's parsing functionality dependent on this WASM module will be unavailable or degraded. This state should be clearly indicated to the user if possible (e.g., "Beancount syntax highlighting/parsing unavailable due to integrity check failure").
*   **FR2.8:** The PQC signature algorithm (Dilithium3) and public key management SHOULD allow for updates (e.g., key rotation), primarily managed through the build/release process and frontend configuration updates.
*   **FR2.9:** The system SHOULD allow for disabling PQC WASM signature verification via a frontend configuration option (e.g., fetched from Fava options, or a build-time flag for development builds), but verification MUST be enabled by default in production builds.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC digital signature scheme (Dilithium3) MUST be implemented correctly, adhering to FIPS 204. The private signing key MUST be kept secure within the build environment.
*   **NFR3.2 (Performance):** PQC signature verification (Dilithium3) in the frontend SHOULD be performant.
    *   Target: Verification time < 50ms on typical client hardware (based on `pf_wasm_pqc_sri_PART_1.md` and `liboqs-js` estimates). This should not noticeably delay Fava's startup or the availability of features dependent on the WASM module.
*   **NFR3.3 (Usability - User):** WASM integrity verification should be transparent to the end-user if successful. If it fails, the impact (e.g., loss of syntax highlighting) should be clear.
*   **NFR3.4 (Reliability):** PQC signature verification MUST be reliable, consistently verifying valid signatures and rejecting invalid ones.
*   **NFR3.5 (Maintainability):** The frontend PQC verification logic (in `frontend/src/lib/pqcCrypto.ts` or similar) MUST be modular. Updating the PQC public key or signature algorithm (if necessary in the future) should be straightforward.
*   **NFR3.6 (Cryptographic Agility):** The system should be designed to potentially support different PQC signature algorithms in the future, managed by the build process and corresponding frontend verification logic. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))
*   **NFR3.7 (Frontend Bundle Size):** The JS/WASM PQC library used for signature verification (e.g., `liboqs-js` with only Dilithium enabled) SHOULD have a minimal impact on the overall frontend bundle size. Target: Added library size for Dilithium3 verification < 100-200KB (WASM part, gzipped), as per `pf_pqc_js_wasm_libs_g3_3_PART_1.md` considerations.

## 4. User Stories

*   **US4.1:** As a Fava user, I want the Fava application to verify the integrity of its WebAssembly parser using Dilithium3 PQC digital signatures before using it, so I can be confident it hasn't been tampered with.
*   **US4.2:** As a Fava developer/maintainer, I want the Fava build process to automatically sign the WASM parser with a Dilithium3 PQC digital signature so that it can be verified by the frontend.
*   **US4.3:** As a Fava user, if the WASM parser fails its PQC integrity check, I want to be informed (e.g., via a console error and potentially a UI indication that some features are degraded) rather than the application silently using a potentially compromised component.

## 5. Use Cases

### 5.1. Use Case: Frontend Verifies and Loads PQC-Signed WASM Module (Happy Path)

*   **Actor:** Fava Frontend
*   **Preconditions:**
    *   `tree-sitter-beancount.wasm` is available.
    *   `tree-sitter-beancount.wasm.dilithium3.sig` (Dilithium3 signature) is available.
    *   Fava's Dilithium3 public key for WASM verification is embedded/accessible.
    *   `liboqs-js` (or similar, configured for Dilithium3) is available.
    *   PQC WASM verification is enabled.
*   **Main Flow:**
    1.  Frontend logic initiates loading of the Beancount parser.
    2.  It fetches `tree-sitter-beancount.wasm` (as `wasmBuffer`).
    3.  It fetches `tree-sitter-beancount.wasm.dilithium3.sig` (as `signatureBuffer`).
    4.  It retrieves the embedded Fava Dilithium3 public key (`dilithiumPublicKeyBytes`).
    5.  It calls `pqcVerifySignature(dilithiumPublicKeyBytes, wasmBuffer, signatureBuffer, "Dilithium3")` using `liboqs-js`.
    6.  Verification succeeds.
    7.  The frontend proceeds to load/initialize the WASM module using `wasmBuffer`.
    8.  Console log: "WASM module 'tree-sitter-beancount.wasm' Dilithium3 signature verified successfully."
*   **Postconditions:**
    *   WASM parser is loaded and functional. Parser-dependent features are enabled.

### 5.2. Use Case: Frontend Fails to Verify PQC-Signed WASM Module (Invalid Signature)

*   **Actor:** Fava Frontend
*   **Preconditions:**
    *   Same as 5.1, but `tree-sitter-beancount.wasm` is tampered, or `.sig` is invalid.
*   **Main Flow:**
    1.  Frontend fetches WASM binary and signature.
    2.  Calls `pqcVerifySignature(...)`.
    3.  Verification fails.
    4.  Console log: "ERROR: WASM module 'tree-sitter-beancount.wasm' Dilithium3 signature verification FAILED. Module not loaded."
    5.  WASM module is NOT loaded. UI indicates degraded functionality if applicable.
*   **Postconditions:**
    *   WASM parser not loaded. Parser-dependent features disabled/degraded. Fava remains operational with reduced functionality.

### 5.3. Use Case: PQC WASM Verification Disabled

*   **Actor:** Fava Frontend
*   **Preconditions:** PQC WASM signature verification is disabled (dev build/config).
*   **Main Flow:**
    1.  Frontend checks config flag. Skips verification steps.
    2.  Loads WASM module directly.
    3.  Console log: "WARNING: PQC WASM signature verification is disabled."
*   **Postconditions:**
    *   WASM parser loaded (if otherwise valid). Security assurance bypassed.

## 6. Edge Cases & Error Handling

*   **EC6.1:** WASM signature file (`.sig`) missing: Verification fails. Log error, do not load WASM.
*   **EC6.2:** Embedded PQC public key corrupted/malformed: Verification fails. Critical deployment error.
*   **EC6.3:** `liboqs-js` (or PQC lib) fails to load/initialize: Verification cannot proceed. Log error, do not load WASM.
*   **EC6.4:** Network error fetching WASM/signature: Standard network error handling.
*   **EC6.5:** Incompatible versions of Dilithium3 (signing vs. verification): Verification fails. Build process must ensure consistent algorithm versions.

## 7. Constraints

*   **C7.1:** Frontend PQC signature verification will rely on `liboqs-js` (or similar) capable of Dilithium3.
*   **C7.2:** Build process must use a PQC signing tool (e.g., `liboqs` CLI examples, `oqs-python` script) for Dilithium3 and include signature/public key in distribution. Contingency plans from `pf_tooling_contingency_PART_1.md` apply.
*   **C7.3:** Performance of Dilithium3 verification in browser must be acceptable (NFR3.2).
*   **C7.4:** Size of PQC signature, public key, and `liboqs-js` impact frontend assets (NFR3.7).

## 8. Data Models

### 8.1. PQC WASM Verification Configuration (Conceptual)

*   Frontend build configuration or runtime options:
    *   `pqc_wasm_verification_enabled`: boolean (Default: true)
    *   `pqc_wasm_public_key_dilithium3_base64`: string (Embedded Base64 Dilithium3 public key)
    *   `pqc_wasm_signature_algorithm_name`: string (Fixed to "Dilithium3" initially)

### 8.2. Distributed Files

*   `tree-sitter-beancount.wasm`
*   `tree-sitter-beancount.wasm.dilithium3.sig`

## 9. UI/UX Flow Outlines

*   **UI9.1 (Successful Verification):** Transparent.
*   **UI9.2 (Failed Verification):** Console error. Optional UI indication of reduced functionality.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. Frontend PQC Signature Verification (`frontend/src/lib/pqcCrypto.ts`)

```typescript
// In frontend/src/lib/pqcCrypto.ts

// Assume liboqs-js is loaded and provides 'OQS_Signature' class or similar
// let sig; // instance of OQS_Signature for Dilithium3

// async function initializeDilithium3Verifier(publicKeyBase64: string): Promise<void> {
//   // const OQS = await getLibOqsInstance(); // Hypothetical liboqs-js loader
//   // sig = new OQS.Signature("Dilithium3");
//   // const publicKeyBytes = Uint8Array.from(atob(publicKeyBase64), c => c.charCodeAt(0));
//   // // Note: liboqs-js might have its own way to load keys, this is conceptual
//   // // It might also handle public key directly in verify if not stateful
//   throw new Error("initializeDilithium3Verifier stub");
// }

// export async function verifyPqcWasmSignature(
//   wasmBuffer: ArrayBuffer,
//   signatureBuffer: ArrayBuffer,
//   publicKeyBase64: string // Dilithium3 public key
// ): Promise<boolean> {
//   // if (!sig) await initializeDilithium3Verifier(publicKeyBase64); // Or pass key to verify
//   // const OQS = await getLibOqsInstance();
//   // const verifier = new OQS.Signature("Dilithium3"); // Or the configured algorithm
//   // const messageBytes = new Uint8Array(wasmBuffer);
//   // const sigBytes = new Uint8Array(signatureBuffer);
//   // const pkBytes = Uint8Array.from(atob(publicKeyBase64), c => c.charCodeAt(0));
//   // return await verifier.verify(messageBytes, sigBytes, pkBytes);
//   throw new Error("verifyPqcWasmSignature stub for Dilithium3");
// }

// TEST (Vitest/Jest): test_verifyPqcWasmSignature_dilithium3_valid()
//   SETUP: Mock fetch for WASM & valid Dilithium3 signature. Known good Dilithium3 pubkey. Mock liboqs-js `verify` to return true.
//   ACTION: Call `verifyPqcWasmSignature(wasmBuffer, sigBuffer, pubKeyBase64)`.
//   ASSERT: Returns `true`.

// TEST: test_verifyPqcWasmSignature_dilithium3_invalid()
//   SETUP: Mock fetch for WASM & INVALID Dilithium3 signature. Correct pubkey. Mock liboqs-js `verify` to return false.
//   ACTION: Call `verifyPqcWasmSignature(wasmBuffer, invalidSigBuffer, pubKeyBase64)`.
//   ASSERT: Returns `false`.
```

### 10.2. WASM Loader Integration (`frontend/src/codemirror/beancount.ts`)

```typescript
// In frontend/src/codemirror/beancount.ts (conceptual modification)
// import { verifyPqcWasmSignature } from '@/lib/pqcCrypto';
// import { favaPqcWasmConfig } from '@/stores/favaPqcConfig'; // Hypothetical store/config access

// async function loadBeancountParserWithPQCVerification() {
//   // const wasmPath = new URL("./tree-sitter-beancount.wasm", import.meta.url).href;
//   // const signaturePath = new URL("./tree-sitter-beancount.wasm.dilithium3.sig", import.meta.url).href;
//   // const config = getFavaPqcWasmConfig(); // Fetch from store or global

//   // if (!config.pqcWasmVerificationEnabled) {
//   //   console.warn("PQC WASM signature verification is disabled.");
//   //   return await TSLanguage.load(wasmPath); // Load directly
//   // }

//   // try {
//   //   const [wasmRes, sigRes] = await Promise.all([fetch(wasmPath), fetch(signaturePath)]);
//   //   if (!wasmRes.ok || !sigRes.ok) { throw new Error("Fetch failed"); }
//   //   const wasmBuffer = await wasmRes.arrayBuffer();
//   //   const signatureBuffer = await sigRes.arrayBuffer();

//   //   const isValid = await verifyPqcWasmSignature(
//   //     wasmBuffer,
//   //     signatureBuffer,
//   //     config.pqcWasmPublicKeyDilithium3Base64
//   //   );

//   //   if (isValid) {
//   //     console.info("WASM Dilithium3 signature verified successfully.");
//   //     // Proceed to load WASM using wasmBuffer with web-tree-sitter's API
//   //     // await Parser.init(); const lang = await Parser.Language.load(wasmBuffer); return lang;
//   //   } else {
//   //     console.error("WASM Dilithium3 signature verification FAILED. Parser not loaded.");
//   //     throw new Error("WASM PQC signature verification failed.");
//   //   }
//   // } catch (error) {
//   //   console.error("Error during WASM PQC verification/loading:", error);
//   //   return null;
//   // }
//   throw new Error("loadBeancountParserWithPQCVerification stub");
// }

// TEST (Integration): test_loadBeancountParser_succeeds_with_valid_dilithium3_sig()
//   SETUP: Mock fetch. Mock `verifyPqcWasmSignature` to return true. Mock Parser/TSLanguage.load. Config enabled.
//   ACTION: Call `loadBeancountParserWithPQCVerification()`.
//   ASSERT: `Parser.Language.load` (or equivalent) called with wasmBuffer. Console info logged.
```

### 10.3. Build Process Stub (Conceptual - e.g., in a release script)

```bash
# Conceptual commands in a release script

# PQC_SIGNING_KEY_DILITHIUM3="path/to/fava_dilithium3_private.key"
# WASM_FILE="frontend/public/tree-sitter-beancount.wasm"
# SIG_FILE="frontend/public/tree-sitter-beancount.wasm.dilithium3.sig"
# PUBLIC_KEY_OUTPUT_TS="frontend/src/generated/pqcWasmConfig.ts" # To embed in frontend

# # Step 1: Sign the WASM file using oqs-python script or liboqs CLI tool
# # python scripts/sign_wasm.py --key "${PQC_SIGNING_KEY_DILITHIUM3}" \
# #                             --algorithm "Dilithium3" \
# #                             --in "${WASM_FILE}" \
# #                             --out "${SIG_FILE}"
# # OR using a hypothetical liboqs CLI:
# # oqs_sig_tool sign --alg Dilithium3 --key_in "${PQC_SIGNING_KEY_DILITHIUM3}" --data_in "${WASM_FILE}" --sig_out "${SIG_FILE}"


# # Step 2: Extract/format public key for embedding (Python script or liboqs tool)
# # PUBLIC_KEY_BASE64=$(python scripts/export_pubkey.py --key "${PQC_SIGNING_KEY_DILITHIUM3}" --format base64)
# # echo "export const favaPqcWasmConfig = {" > "${PUBLIC_KEY_OUTPUT_TS}"
# # echo "  pqcWasmVerificationEnabled: true," >> "${PUBLIC_KEY_OUTPUT_TS}"
# # echo "  pqcWasmPublicKeyDilithium3Base64: \"${PUBLIC_KEY_BASE64}\"," >> "${PUBLIC_KEY_OUTPUT_TS}"
# # echo "  pqcWasmSignatureAlgorithmName: \"Dilithium3\"" >> "${PUBLIC_KEY_OUTPUT_TS}"
# # echo "};" >> "${PUBLIC_KEY_OUTPUT_TS}"

# TEST (Build process): test_build_produces_dilithium3_signed_wasm_and_public_key()
#   ACTION: Run build script steps for WASM signing.
#   ASSERT: `${SIG_FILE}` created. `${PUBLIC_KEY_OUTPUT_TS}` created with Base64 public key and "Dilithium3".
```

## 11. Dependencies

*   **External Libraries (Frontend):**
    *   `liboqs-js` (custom build for Dilithium3 if possible to reduce size).
*   **External Tools (Build Process):**
    *   A command-line PQC signing tool for Dilithium3 (e.g., from `liboqs` examples) or a Python script using `oqs-python`.
*   **Internal Fava Modules:**
    *   `frontend/src/codemirror/beancount.ts`: Modified for verification.
    *   `frontend/src/lib/pqcCrypto.ts` (or similar): For PQC verification abstraction.
    *   Fava's build scripts: Incorporate WASM signing.
    *   Frontend configuration for public key and enabling verification.

## 12. Integration Points

*   **IP12.1 (Fava Build Process):** New step to PQC-sign `tree-sitter-beancount.wasm` with Dilithium3 and embed public key.
*   **IP12.2 (Frontend WASM Loading):** Logic in `frontend/src/codemirror/beancount.ts` modified to fetch WASM, signature, call verification, and conditionally load.
*   **IP12.3 (Frontend PQC Crypto Library):** `liboqs-js` integrated for Dilithium3 verification.
*   **IP12.4 (Frontend Configuration):** Mechanism to provide embedded public key and enable/disable verification.