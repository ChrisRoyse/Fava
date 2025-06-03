# PQC Integration Specification: Hashing

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document provides the specifications for integrating Post-Quantum Cryptography (PQC) considerations into Fava's hashing mechanisms. This primarily involves upgrading or abstracting current hashing functions (SHA-256) to support PQC-resistant alternatives like SHA-3 or SHAKE. Hashing is used in Fava for file integrity checks on save ([`src/fava/core/file.py`](../../src/fava/core/file.py)) and optimistic concurrency in the frontend editor ([`frontend/src/editor/SliceEditor.svelte`](../../frontend/src/editor/SliceEditor.svelte)).

This specification is derived from the PQC integration plan ([`docs/Plan.MD`](../../docs/Plan.MD)), research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure data integrity mechanisms remain robust against potential future attacks, including those from quantum computers, by adopting more resilient hash functions.

## 2. Functional Requirements

*   **FR2.1:** The system MUST provide an abstraction layer (`HashingService` in `fava.crypto_service` and a similar abstraction in `frontend/src/lib/crypto.ts`) for all hashing operations.
*   **FR2.2:** The default hashing algorithm SHOULD be configurable to a PQC-resistant hash function (e.g., SHA3-256 or SHAKE256 with a fixed output length).
*   **FR2.3:** The system MUST continue to support SHA-256 as a configurable option for hashing, for backward compatibility or specific needs, though a PQC-resistant hash should be the recommended default.
*   **FR2.4 (Backend):** Fava's backend file integrity check (e.g., in `src/fava/core/file.py` during save operations) MUST use the configured hashing algorithm via the `HashingService`.
*   **FR2.5 (Frontend):** Fava's frontend optimistic concurrency mechanism (e.g., in `SliceEditor.svelte`) MUST use the configured hashing algorithm via the frontend crypto abstraction.
*   **FR2.6:** The hashing algorithm used by the frontend MUST be consistent with the algorithm used by the backend for operations where hashes are compared (e.g., optimistic concurrency checks). Fava's options should provide the configured hash algorithm to the frontend.
*   **FR2.7:** The system MUST correctly calculate and compare hashes using the selected PQC-resistant algorithm (e.g., SHA3-256).

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The chosen PQC-resistant hash algorithms (e.g., SHA3-256, SHAKE256) MUST be implemented correctly, adhering to their respective standards.
*   **NFR3.2 (Performance):** The performance of PQC-resistant hashing operations (e.g., SHA3-256) SHOULD be comparable to SHA-256 and not introduce noticeable delays in file saving or frontend editor responsiveness. (SHA-3 can sometimes be slower than SHA-2 on certain platforms without hardware acceleration, this needs to be acceptable).
*   **NFR3.3 (Usability - Admin):** Configuration of the hashing algorithm MUST be straightforward via Fava's options.
*   **NFR3.4 (Reliability):** Hashing operations MUST be reliable and produce consistent output for the same input data.
*   **NFR3.5 (Maintainability):** The hashing abstraction layer MUST make it easy to add support for new hash algorithms in the future.
*   **NFR3.6 (Cryptographic Agility):** The system MUST allow easy switching between different configured hash algorithms. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))
*   **NFR3.7 (Frontend Bundle Size):** If JavaScript libraries are required for frontend PQC-resistant hashing (e.g., SHA-3), their impact on the frontend bundle size SHOULD be minimized.

## 4. User Stories

*   **US4.1:** As a Fava administrator, I want to configure Fava to use SHA3-256 for all internal hashing operations to enhance long-term data integrity protection.
*   **US4.2:** As a Fava user editing a Beancount file slice, I want the optimistic concurrency check to use the globally configured PQC-resistant hash algorithm to ensure consistency between my client-side calculations and server-side verifications.
*   **US4.3:** As a developer, I want Fava's hashing logic to be abstracted so that new hash algorithms can be integrated with minimal changes to the core application code.

## 5. Use Cases

### 5.1. Use Case: Backend File Integrity Check with Configured PQC-Resistant Hash

*   **Actor:** Fava System (Backend)
*   **Preconditions:**
    *   Fava is configured to use `PQC_Hash_Algorithm_X` (e.g., SHA3-256) via `FavaOptions`.
    *   The `HashingService` is initialized with this configuration.
*   **Main Flow:**
    1.  A user saves a Beancount file through Fava.
    2.  Before writing to disk (or as part of an integrity check), `src/fava/core/file.py` (or equivalent logic) needs to hash the file content.
    3.  It calls `hashing_service.hash_data(content_bytes)`.
    4.  The `HashingService` uses the configured `PQC_Hash_Algorithm_X` to compute the hash digest.
    5.  The digest is returned and used (e.g., stored, compared).
*   **Postconditions:**
    *   The file content is hashed using the configured PQC-resistant algorithm.
    *   The correct hash digest is produced.

### 5.2. Use Case: Frontend Optimistic Concurrency Check with Configured PQC-Resistant Hash

*   **Actor:** Fava User (via Frontend), Fava System (Frontend & Backend)
*   **Preconditions:**
    *   Fava is configured to use `PQC_Hash_Algorithm_X` (e.g., SHA3-256).
    *   The frontend has received this configuration (e.g., via an API call to fetch Fava options).
    *   The frontend crypto abstraction (`frontend/src/lib/crypto.ts`) supports `PQC_Hash_Algorithm_X`.
*   **Main Flow:**
    1.  User is editing a slice of a Beancount file in `SliceEditor.svelte`.
    2.  The frontend editor (`SliceEditor.svelte`) calculates the hash of the current content of the slice using `calculateHash(slice_content, configured_pqc_hash_algorithm)`.
    3.  When the user saves, this client-calculated hash is sent to the backend along with the content.
    4.  The backend receives the content and the client-calculated hash.
    5.  The backend recalculates the hash of the received content using its `HashingService` (configured with the same `PQC_Hash_Algorithm_X`).
    6.  The backend compares its calculated hash with the client-provided hash.
    7.  If hashes match, the save proceeds. If not, an optimistic concurrency error is typically raised.
*   **Postconditions:**
    *   Both frontend and backend use the same configured PQC-resistant hash algorithm for the concurrency check.
    *   The save operation succeeds or fails correctly based on the hash comparison.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Configured hash algorithm is not supported by the `HashingService` (backend) or frontend crypto abstraction: System should gracefully handle this, possibly falling back to a default (e.g., SHA-256) or logging a clear error. Fava startup might fail if a critical hash service cannot be initialized.
*   **EC6.2:** Input data for hashing is empty or extremely large: Hashing function should handle this correctly as per its specification.
*   **EC6.3:** JavaScript library for frontend PQC-resistant hashing fails to load or initialize: Frontend hashing should fail gracefully, possibly disabling optimistic concurrency or alerting the user.
*   **EC6.4:** Inconsistency between frontend and backend hash calculation for the same PQC-resistant algorithm (e.g., due to different library implementations or subtle encoding issues): This would lead to false optimistic concurrency errors. Requires careful testing.
*   **EC6.5:** User attempts to configure an unknown or insecure hash algorithm: Configuration validation should prevent this or log a severe warning.

## 7. Constraints

*   **C7.1:** Backend PQC-resistant hashing (e.g., SHA-3) might rely on Python libraries like `pysha3` or `cryptography` if not yet in `hashlib` by default, or `oqs-python` if using a PQC-specific hash.
*   **C7.2:** Frontend PQC-resistant hashing (e.g., SHA-3) will likely require a JavaScript library (e.g., `js-sha3` or a WASM-based solution like `liboqs-js` if it provides suitable hash functions).
*   **C7.3:** Performance of chosen PQC-resistant hash functions must be acceptable (see NFR3.2).
*   **C7.4:** The set of supported PQC-resistant hash algorithms will initially be small (e.g., SHA3-256, possibly SHAKE256).

## 8. Data Models (if applicable)

### 8.1. Hashing Configuration Parameters (Conceptual)

Stored within Fava's options/configuration system:

*   `pqc_hashing_algorithm`: string (e.g., "SHA3-256", "SHAKE256_OUTPUT_256BIT", "SHA256")
    *   Default: "SHA3-256" (or other PQC-resistant choice)
*   (Possibly other parameters if a chosen hash function requires them, e.g., output length for SHAKE if not part of the algorithm name string).

This configuration value would be accessible to both backend services and exposed to the frontend via an API endpoint.

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (Configuration):**
    *   A setting in Fava's options UI to select the preferred hashing algorithm from a predefined list (e.g., SHA3-256, SHA-256).
    *   Clear indication of the recommended (PQC-resistant) default.
*   **UI9.2 (User-facing):**
    *   No direct UI changes for hashing operations themselves. These are background processes.
    *   Optimistic concurrency error messages (if hashes mismatch) will remain, but the underlying hash calculation method will have changed.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. `HashingService` (Backend - `fava.crypto_service`)

```python
# In fava.crypto_service (conceptual)

class HashingService(ABC):
    @abstractmethod
    def hash_data(self, data: bytes) -> str:  # returns hex digest
        """Hashes data using the configured algorithm, returns hex digest."""
        pass

# Example Implementation:
# class SHA3_256HashingService(HashingService):
#     def hash_data(self, data: bytes) -> str:
#         # import hashlib or pysha3
#         # return hashlib.sha3_256(data).hexdigest()
#         pass

# class SHA256HashingService(HashingService):
#     def hash_data(self, data: bytes) -> str:
#         # import hashlib
#         # return hashlib.sha256(data).hexdigest()
#         pass

# Factory/Getter:
# def get_hashing_service(configured_algorithm_name: str) -> HashingService:
#     if configured_algorithm_name == "SHA3-256":
#         return SHA3_256HashingService()
#     elif configured_algorithm_name == "SHA256":
#         return SHA256HashingService()
#     # ... other algorithms
#     else:
#         raise ValueError(f"Unsupported hash algorithm: {configured_algorithm_name}")

# TEST: test_sha3_256_hashing_service_correct_hash()
#   SETUP: Instantiate SHA3_256HashingService. Known input data and its SHA3-256 hash.
#   ACTION: Call hash_data(input_data).
#   ASSERT: Returned hash matches the known SHA3-256 hash.

# TEST: test_get_hashing_service_returns_correct_service_based_on_config()
#   SETUP: Fava configured to use "SHA3-256".
#   ACTION: Call get_hashing_service(fava_options.pqc_hashing_algorithm).
#   ASSERT: Returns an instance of SHA3_256HashingService.

# TEST: test_backend_file_save_uses_configured_hash_algorithm()
#   SETUP: Configure Fava for "SHA3-256". Mock the hashing service to record calls.
#          Simulate a file save operation in src/fava/core/file.py.
#   ACTION: Trigger the part of file saving that calculates a hash.
#   ASSERT: The SHA3_256HashingService's hash_data method was called.
```

### 10.2. Frontend Hashing Abstraction (`frontend/src/lib/crypto.ts`)

```typescript
// In frontend/src/lib/crypto.ts (conceptual)

// export async function calculateHash(
//   data: string,
//   algorithm: string = "SHA-256" // Algorithm name fetched from Fava options
// ): Promise<string> {
//   const encoder = new TextEncoder();
//   const dataBuffer = encoder.encode(data);
//   let hashBuffer: ArrayBuffer;

//   if (algorithm.toUpperCase() === "SHA3-256") {
//     // const { sha3_256 } = await import('js-sha3'); // Or other SHA3 library
//     // hashBuffer = sha3_256.arrayBuffer(dataBuffer);
//     throw new Error("SHA3-256 not implemented yet in frontend crypto.ts stub");
//   } else if (algorithm.toUpperCase() === "SHA-256") {
//     hashBuffer = await window.crypto.subtle.digest("SHA-256", dataBuffer);
//   } else {
//     throw new Error(`Unsupported hash algorithm: ${algorithm}`);
//   }

//   const hashArray = Array.from(new Uint8Array(hashBuffer));
//   return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
// }

// TEST (e.g., Vitest/Jest for frontend): test_calculate_hash_sha3_256_correct()
//   SETUP: Mock Fava options to return "SHA3-256" as configured algorithm.
//          Known input string and its SHA3-256 hash (pre-calculated with a trusted tool).
//          Ensure js-sha3 or equivalent library is available and mocked/imported.
//   ACTION: await calculateHash(input_string, "SHA3-256");
//   ASSERT: Returned hash matches the known SHA3-256 hash.

// TEST: test_slice_editor_uses_calculate_hash_with_configured_algorithm()
//   SETUP: Mock Fava options to return "SHA3-256".
//          Spy on `calculateHash` function.
//          Simulate content change and save trigger in SliceEditor.svelte.
//   ACTION: Trigger the optimistic concurrency hash calculation in SliceEditor.
//   ASSERT: `calculateHash` was called with the slice content and "SHA3-256".
```

## 11. Dependencies

*   **External Libraries (Backend):**
    *   `pysha3` or `cryptography` (if Python's `hashlib` does not include SHA-3 by the time of implementation).
*   **External Libraries (Frontend):**
    *   A JavaScript SHA-3 implementation (e.g., `js-sha3`) or a WASM-based library providing SHA-3.
*   **Internal Fava Modules:**
    *   `fava.core.FavaOptions`: To store and provide the configured hashing algorithm.
    *   `fava.core.file`: Backend logic using hashing for integrity.
    *   `fava.crypto_service`: New module for backend `HashingService`.
    *   `frontend/src/editor/SliceEditor.svelte`: Frontend logic using hashing for optimistic concurrency.
    *   `frontend/src/lib/crypto.ts`: New module for frontend hashing abstraction.
    *   Fava API endpoint to expose the configured hash algorithm to the frontend.

## 12. Integration Points

*   **IP12.1 (`HashingService` in Backend):** All backend hashing calls (e.g., in `src/fava/core/file.py`) will be routed through the `get_hashing_service().hash_data()` method.
*   **IP12.2 (Frontend Hashing Abstraction):** All frontend hashing calls (e.g., in `SliceEditor.svelte`) will use the `calculateHash()` function from `frontend/src/lib/crypto.ts`.
*   **IP12.3 (Fava Configuration):** Fava's options loading mechanism will read the `pqc_hashing_algorithm` setting. This setting will be used to initialize the backend `HashingService` and will be exposed via an API endpoint for the frontend to fetch.
*   **IP12.4 (API for Frontend Configuration):** A Fava API endpoint (e.g., part of the existing options/context API) will provide the configured `pqc_hashing_algorithm` string to the frontend so it can use the consistent algorithm.