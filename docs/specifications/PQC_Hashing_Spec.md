# PQC Integration Specification: Hashing

**Version:** 1.1
**Date:** 2025-06-02

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on new research findings and Devil's Advocate critique. Key changes include:
    *   Default hashing algorithm changed to SHA3-256.
    *   Updated performance NFRs based on research (`pf_hashing_pqc_frontend_PART_1.md`).
    *   Acknowledged frontend SHA-3 library requirements and bundle size considerations.
    *   Refined TDD anchors for backend and frontend.
*   **1.0 (2025-06-02):** Initial version.

## 1. Introduction

This document provides the specifications for integrating Post-Quantum Cryptography (PQC) considerations into Fava's hashing mechanisms. This primarily involves upgrading or abstracting current hashing functions (SHA-256) to support PQC-resistant alternatives like SHA3-256. Hashing is used in Fava for file integrity checks on save ([`src/fava/core/file.py`](../../src/fava/core/file.py)) and optimistic concurrency in the frontend editor ([`frontend/src/editor/SliceEditor.svelte`](../../frontend/src/editor/SliceEditor.svelte)).

This specification is derived from the PQC integration plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)), research findings ([`docs/research/`](../../docs/research/)), particularly `pf_hashing_pqc_frontend_PART_1.md`, and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure data integrity mechanisms remain robust against potential future attacks, including those from quantum computers, by adopting more resilient hash functions like SHA3-256.

## 2. Functional Requirements

*   **FR2.1:** The system MUST provide an abstraction layer (`HashingService` in `fava.crypto_service` and a similar abstraction in `frontend/src/lib/crypto.ts`) for all hashing operations.
*   **FR2.2:** The default hashing algorithm MUST be SHA3-256. This should be configurable via Fava options.
*   **FR2.3:** The system MUST continue to support SHA-256 as a configurable option for hashing, for backward compatibility or specific needs, though SHA3-256 is the recommended default.
*   **FR2.4 (Backend):** Fava's backend file integrity check (e.g., in `src/fava/core/file.py` during save operations) MUST use the configured hashing algorithm via the `HashingService`.
*   **FR2.5 (Frontend):** Fava's frontend optimistic concurrency mechanism (e.g., in `SliceEditor.svelte`) MUST use the configured hashing algorithm via the frontend crypto abstraction.
*   **FR2.6:** The hashing algorithm used by the frontend MUST be consistent with the algorithm used by the backend for operations where hashes are compared (e.g., optimistic concurrency checks). Fava's options (exposed via API) should provide the configured hash algorithm name to the frontend.
*   **FR2.7:** The system MUST correctly calculate and compare hashes using the selected PQC-resistant algorithm (SHA3-256) and any other configured algorithm (SHA-256).

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The chosen PQC-resistant hash algorithm (SHA3-256) MUST be implemented correctly, adhering to FIPS 202.
*   **NFR3.2 (Performance):**
    *   **Backend:** SHA3-256 hashing performance in Python (using `hashlib` if available, or `pysha3`) should not introduce noticeable delays in file saving. Target: Hashing a 1MB file should complete within 50-100ms on typical server hardware.
    *   **Frontend:** SHA3-256 hashing performance using a JS/WASM library should be acceptable for optimistic concurrency checks on typical editor slice sizes (e.g., a few KB to tens of KB). Target: Hashing a 50KB slice should complete within 20-50ms in the browser. (Acknowledging JS/WASM SHA-3 is slower than native SHA-2, as per `pf_hashing_pqc_frontend_PART_1.md`).
*   **NFR3.3 (Usability - Admin):** Configuration of the hashing algorithm MUST be straightforward via Fava's options.
*   **NFR3.4 (Reliability):** Hashing operations MUST be reliable and produce consistent output for the same input data across backend and frontend.
*   **NFR3.5 (Maintainability):** The hashing abstraction layer MUST make it easy to add support for new hash algorithms in the future.
*   **NFR3.6 (Cryptographic Agility):** The system MUST allow easy switching between different configured hash algorithms (SHA3-256, SHA-256). (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))
*   **NFR3.7 (Frontend Bundle Size):** The JavaScript/WASM library required for frontend SHA3-256 hashing (e.g., `js-sha3` or a WASM library) SHOULD have a minimal impact on the frontend bundle size. Target: Added library size < 50KB gzipped.

## 4. User Stories

*   **US4.1:** As a Fava administrator, I want Fava to use SHA3-256 by default for all internal hashing operations to enhance long-term data integrity protection.
*   **US4.2:** As a Fava user editing a Beancount file slice, I want the optimistic concurrency check to use the globally configured SHA3-256 hash algorithm to ensure consistency between my client-side calculations and server-side verifications.
*   **US4.3:** As a developer, I want Fava's hashing logic to be abstracted so that new hash algorithms can be integrated with minimal changes to the core application code.
*   **US4.4:** As a Fava administrator, if needed for specific interoperability reasons, I want to be able to configure Fava to use SHA-256 for hashing.

## 5. Use Cases

### 5.1. Use Case: Backend File Integrity Check with Configured SHA3-256 Hash

*   **Actor:** Fava System (Backend)
*   **Preconditions:**
    *   Fava is configured to use `SHA3-256` via `FavaOptions`.
    *   The `HashingService` is initialized with this configuration.
*   **Main Flow:**
    1.  A user saves a Beancount file through Fava.
    2.  Before writing to disk, `src/fava/core/file.py` needs to hash the file content.
    3.  It calls `hashing_service.hash_data(content_bytes)`.
    4.  The `HashingService` uses SHA3-256 to compute the hash digest.
    5.  The digest is returned and used (e.g., stored, compared).
*   **Postconditions:**
    *   The file content is hashed using SHA3-256.
    *   The correct hash digest is produced.

### 5.2. Use Case: Frontend Optimistic Concurrency Check with Configured SHA3-256 Hash

*   **Actor:** Fava User (via Frontend), Fava System (Frontend & Backend)
*   **Preconditions:**
    *   Fava is configured to use `SHA3-256`.
    *   The frontend has received this configuration (e.g., "SHA3-256" string) via an API call.
    *   The frontend crypto abstraction (`frontend/src/lib/crypto.ts`) supports SHA3-256 (e.g., via `js-sha3`).
*   **Main Flow:**
    1.  User is editing a slice of a Beancount file in `SliceEditor.svelte`.
    2.  The frontend editor calculates the hash of the current slice content using `calculateHash(slice_content, "SHA3-256")`.
    3.  When the user saves, this client-calculated hash is sent to the backend along with the content.
    4.  The backend receives the content and the client-calculated hash.
    5.  The backend recalculates the hash of the received content using its `HashingService` (configured for SHA3-256).
    6.  The backend compares its calculated hash with the client-provided hash.
    7.  If hashes match, the save proceeds. If not, an optimistic concurrency error is raised.
*   **Postconditions:**
    *   Both frontend and backend use SHA3-256 for the concurrency check.
    *   The save operation succeeds or fails correctly based on the hash comparison.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Configured hash algorithm is not supported by the `HashingService` (backend) or frontend crypto abstraction: System should log a clear error and default to a known secure hash (e.g., SHA3-256 if SHA-256 was misconfigured, or SHA-256 if SHA3-256 lib is missing). Fava startup might fail if a critical hash service cannot be initialized.
*   **EC6.2:** Input data for hashing is empty or extremely large: Hashing function should handle this correctly.
*   **EC6.3:** JavaScript library for frontend SHA3-256 hashing fails to load or initialize: Frontend hashing should fail gracefully, potentially disabling optimistic concurrency or alerting the user. A console error must be logged.
*   **EC6.4:** Inconsistency between frontend and backend hash calculation for SHA3-256 (e.g., due to different library implementations or subtle encoding issues): This would lead to false optimistic concurrency errors. Requires careful testing with consistent UTF-8 encoding of inputs.
*   **EC6.5:** User attempts to configure an unknown or insecure hash algorithm: Configuration validation should prevent this or log a severe warning, defaulting to SHA3-256.

## 7. Constraints

*   **C7.1:** Backend SHA3-256 hashing will use Python's `hashlib` (if Python version is >= 3.6) or a fallback like `pysha3`.
*   **C7.2:** Frontend SHA3-256 hashing will require a JavaScript library (e.g., `js-sha3`) or a WASM-based solution. Native `window.crypto.subtle` does not support SHA-3.
*   **C7.3:** Performance of chosen hash functions must be acceptable (see NFR3.2).
*   **C7.4:** The set of supported hash algorithms will initially be SHA3-256 (default) and SHA-256.

## 8. Data Models

### 8.1. Hashing Configuration Parameters

Stored within Fava's options/configuration system:

*   `pqc_hashing_algorithm`: string (e.g., "SHA3-256", "SHA256")
    *   Default: "SHA3-256"

This configuration value would be accessible to backend services and exposed to the frontend via an API endpoint.

## 9. UI/UX Flow Outlines

*   **UI9.1 (Configuration):**
    *   A setting in Fava's options UI to select the preferred hashing algorithm from a predefined list ("SHA3-256", "SHA-256").
    *   Clear indication of the recommended default (SHA3-256).
*   **UI9.2 (User-facing):**
    *   No direct UI changes for hashing operations themselves.
    *   Optimistic concurrency error messages remain, but underlying hash calculation method changes.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. `HashingService` (Backend - `fava.crypto_service`)

```python
# In fava.crypto_service.py

import hashlib

class HashingService:
    def __init__(self, algorithm_name: str = "SHA3-256"):
        self.algorithm_name = algorithm_name.lower()
        if self.algorithm_name not in ["sha3-256", "sha256"]:
            # Log warning, default to sha3-256
            self.algorithm_name = "sha3-256"
            # print(f"Warning: Unsupported hash algorithm '{algorithm_name}'. Defaulting to 'sha3-256'.")

    def hash_data(self, data: bytes) -> str:
        """Hashes data using the configured algorithm, returns hex digest."""
        if self.algorithm_name == "sha3-256":
            try:
                return hashlib.sha3_256(data).hexdigest()
            except AttributeError: # hashlib might not have sha3 on older pythons
                # import pysha3 # Placeholder for actual fallback logic
                # return pysha3.sha3_256(data).hexdigest()
                raise NotImplementedError("SHA3-256 not available and fallback not implemented")
        elif self.algorithm_name == "sha256":
            return hashlib.sha256(data).hexdigest()
        else: # Should not happen due to constructor logic
            raise ValueError(f"Internal error: Unsupported hash algorithm '{self.algorithm_name}'")

# TEST: test_hashing_service_sha3_256_correct_hash()
#   SETUP: Instantiate HashingService(algorithm_name="SHA3-256"). Known input data and its SHA3-256 hash.
#   ACTION: Call hash_data(input_data).
#   ASSERT: Returned hash matches the known SHA3-256 hash.

# TEST: test_hashing_service_sha256_correct_hash()
#   SETUP: Instantiate HashingService(algorithm_name="SHA256"). Known input data and its SHA256 hash.
#   ACTION: Call hash_data(input_data).
#   ASSERT: Returned hash matches the known SHA256 hash.

# TEST: test_hashing_service_defaults_to_sha3_on_invalid_algo()
#   SETUP: Instantiate HashingService(algorithm_name="MD5_INVALID"). Known input data.
#   ACTION: Call hash_data(input_data).
#   ASSERT: Returned hash matches the SHA3-256 hash of the input data. (Service should log warning).

# def get_hashing_service(configured_algorithm_name: str) -> HashingService:
#     return HashingService(configured_algorithm_name)
```

### 10.2. Frontend Hashing Abstraction (`frontend/src/lib/crypto.ts`)

```typescript
// In frontend/src/lib/crypto.ts (conceptual)
// Assumes js-sha3 is imported as 'sha3' or similar

// import { sha3_256 } from 'js-sha3'; // Example import

// export async function calculateHash(
//   data: string, // Expects string data, will be UTF-8 encoded
//   algorithmName: string = "SHA3-256" // Algorithm name fetched from Fava options
// ): Promise<string> {
//   const encoder = new TextEncoder(); // Always use UTF-8 for consistency
//   const dataBuffer = encoder.encode(data);
//   let hashHex: string;

//   const algo = algorithmName.toUpperCase();

//   if (algo === "SHA3-256") {
//     // hashHex = sha3_256(dataBuffer); // js-sha3 typically takes ArrayBuffer or string directly
//     // For ArrayBuffer input with js-sha3, ensure library supports it or convert if needed.
//     // Example: hashHex = sha3_256.create().update(dataBuffer).hex();
//     throw new Error("SHA3-256 frontend hashing stub not fully implemented with js-sha3 specifics");
//   } else if (algo === "SHA-256") { // Note: Fava config uses "SHA256", frontend might get "SHA-256" from Web Crypto
//     const hashBuffer = await window.crypto.subtle.digest("SHA-256", dataBuffer);
//     const hashArray = Array.from(new Uint8Array(hashBuffer));
//     hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
//   } else {
//     console.warn(`Unsupported hash algorithm requested by frontend: ${algorithmName}. Defaulting to SHA-256 for safety.`);
//     // Fallback to SHA-256 if an unknown algo is somehow requested by frontend logic
//     const hashBuffer = await window.crypto.subtle.digest("SHA-256", dataBuffer);
//     const hashArray = Array.from(new Uint8Array(hashBuffer));
//     hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
//     // OR: throw new Error(`Unsupported hash algorithm: ${algorithmName}`);
//   }
//   return hashHex;
// }

// TEST (e.g., Vitest/Jest for frontend): test_calculate_hash_frontend_sha3_256_correct()
//   SETUP: Known input string and its SHA3-256 hash (pre-calculated with a trusted tool, using UTF-8 encoding).
//          Ensure js-sha3 or equivalent library is mocked/imported.
//   ACTION: await calculateHash(input_string, "SHA3-256");
//   ASSERT: Returned hash matches the known SHA3-256 hash.

// TEST: test_calculate_hash_frontend_sha256_correct()
//   SETUP: Known input string and its SHA-256 hash.
//   ACTION: await calculateHash(input_string, "SHA-256");
//   ASSERT: Returned hash matches the known SHA-256 hash.
```

## 11. Dependencies

*   **External Libraries (Backend):**
    *   `hashlib` (standard Python, for SHA-256 and SHA3-256 if Python >= 3.6).
    *   `pysha3` (optional, as fallback for SHA-3 if `hashlib` doesn't support it on older Python).
*   **External Libraries (Frontend):**
    *   A JavaScript SHA-3 implementation (e.g., `js-sha3`) or a WASM-based library.
*   **Internal Fava Modules:**
    *   `fava.core.FavaOptions`: To store and provide the configured hashing algorithm.
    *   `fava.core.file`: Backend logic using hashing.
    *   `fava.crypto_service`: New module for backend `HashingService`.
    *   `frontend/src/editor/SliceEditor.svelte`: Frontend logic using hashing.
    *   `frontend/src/lib/crypto.ts`: Module for frontend hashing abstraction.
    *   Fava API endpoint to expose the configured hash algorithm to the frontend.

## 12. Integration Points

*   **IP12.1 (`HashingService` in Backend):** All backend hashing calls routed through `get_hashing_service().hash_data()`.
*   **IP12.2 (Frontend Hashing Abstraction):** All frontend hashing calls use `calculateHash()` from `frontend/src/lib/crypto.ts`.
*   **IP12.3 (Fava Configuration):** Fava's options loading reads `pqc_hashing_algorithm`. This initializes backend `HashingService` and is exposed via API for the frontend.
*   **IP12.4 (API for Frontend Configuration):** An API endpoint provides the configured `pqc_hashing_algorithm` string to the frontend.