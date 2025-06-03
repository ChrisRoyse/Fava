# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 5

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 5 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   Part 2: [PQC_Developer_Guide_v1.1_part2.md](PQC_Developer_Guide_v1.1_part2.md)
*   Part 3: [PQC_Developer_Guide_v1.1_part3.md](PQC_Developer_Guide_v1.1_part3.md)
*   Part 4: [PQC_Developer_Guide_v1.1_part4.md](PQC_Developer_Guide_v1.1_part4.md)

This part details the PQC Hashing integration.

## 6. PQC Hashing

Fava integrates PQC-resistant hashing to enhance data integrity mechanisms. The primary goal is to use SHA3-256 as the default, with SHA-256 as a configurable alternative.

### 6.1. Backend `HashingService`

As detailed in [`docs/architecture/PQC_Hashing_Arch.md`](../../docs/architecture/PQC_Hashing_Arch.md):

*   **Location:** Conceptually within `src/fava/pqc/backend_crypto_service.py` or a dedicated `src/fava/pqc/hashers.py`.
*   **Responsibilities:**
    *   Initialized with the `pqc_hashing_algorithm` (e.g., "SHA3-256", "SHA256") from `FAVA_CRYPTO_SETTINGS` (via `GlobalConfig`).
    *   Provides a method like `hash_data(data: bytes) -> str` that returns a hex digest.
    *   Implements logic for SHA3-256 (using `hashlib` or `pysha3` as fallback) and SHA-256 (using `hashlib`).
    *   Handles unsupported configured algorithms by logging a warning and defaulting to SHA3-256.
*   **Usage:**
    *   [`src/fava/core/file.py`](../../src/fava/core/file.py) uses this service for file integrity checks during save operations.
    *   Backend logic for optimistic concurrency control (verifying hashes from frontend editor saves) also uses this service.
*   **Developer Notes:**
    *   Ensure consistent UTF-8 encoding of string data before hashing if inputs can be strings. The `hash_data` method should expect `bytes`.
    *   The service should normalize algorithm names (e.g., "sha3-256" vs "SHA3256") if necessary, though configuration should define a standard string.

### 6.2. Frontend Hashing Abstraction

*   **Location:** Conceptually in `frontend/src/lib/pqcCrypto.ts` or `frontend/src/lib/crypto.ts`.
*   **Responsibilities:**
    *   Provides a method like `async calculateHash(data_string: string, algorithm_name_from_config: string): Promise<string>`.
    *   Fetches the `pqc_hashing_algorithm` string from a backend API endpoint (e.g., `/api/pqc_config`) which exposes the relevant part of `FAVA_CRYPTO_SETTINGS`.
    *   Implements hashing:
        *   For "SHA3-256": Uses a JavaScript SHA3 library (e.g., `js-sha3`).
        *   For "SHA256": Uses `window.crypto.subtle.digest("SHA-256", ...)`.
    *   Handles unsupported algorithm names by logging a warning and potentially defaulting (e.g., to SHA-256 if SHA3 library fails or is unavailable).
    *   Ensures input strings are UTF-8 encoded before hashing.
*   **Usage:**
    *   [`frontend/src/editor/SliceEditor.svelte`](../../frontend/src/editor/SliceEditor.svelte) uses this abstraction to calculate client-side hashes for optimistic concurrency control when saving edits.
*   **Developer Notes:**
    *   The choice of a JavaScript SHA3 library should consider performance (NFR3.2) and bundle size impact (NFR3.7 from [`docs/specifications/PQC_Hashing_Spec.md`](../../docs/specifications/PQC_Hashing_Spec.md)). Early benchmarking during development is crucial.
    *   The frontend must receive the exact algorithm string identifier from the backend to ensure consistency.

### 6.3. Configuration
*   A setting like `FAVA_CRYPTO_SETTINGS.hashing.default_algorithm` (string, e.g., "SHA3-256" or "SHA256") controls the hashing algorithm.
*   This setting is read by the backend `HashingService` and exposed via an API (e.g. `/api/pqc_config` from [`src/fava/json_api.py`](../../src/fava/json_api.py)) to the frontend.

---
End of Part 5. More content will follow in Part 6.