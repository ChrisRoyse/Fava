# Primary Findings: Hybrid PQC Scheme Recommendations for Fava (Addressing Gap G2.2)

**Date Compiled:** 2025-06-02
**Research Focus:** G2.2: Specific recommendations for Fava's context.
**Source:** AI Search (Perplexity MCP) - Query: "Specific recommendations for implementing hybrid PQC schemes in the Fava application context. Consider Fava's use cases: data-at-rest (Beancount file encryption, possibly GPG-related), data-in-transit (HTTPS/TLS for client-server), and data integrity (WASM module signing, file hashing). Recommend suitable classical + PQC algorithm pairings (e.g., X25519+Kyber768 for KEMs, ECDSA P-256+Dilithium3 for signatures) and construction methods for each use case. Reference Fava's existing architecture if possible (Python backend, Svelte/JS frontend)."

This document provides specific recommendations for implementing hybrid Post-Quantum Cryptography (PQC) schemes within the Fava application, considering its distinct use cases and existing architecture.

## 1. Data-at-Rest: Encrypted Beancount Files

Fava's primary data-at-rest concern is the encryption of Beancount files, often handled via GPG.

**Recommended Hybrid Approach:**

*   **Algorithm Pairing:**
    *   **Classical KEM:** X25519 (ECDH for key agreement if a symmetric key is derived for file encryption).
    *   **PQC KEM:** Kyber-768 (ML-KEM, NIST Level 3).
*   **Construction Method (if Fava handles aspects of decryption/encryption directly or guides users for external tools):**
    1.  **Key Derivation:** If symmetric encryption (e.g., AES-256-GCM) is used for the file, the symmetric key should be derived from a hybrid shared secret.
    2.  **Hybrid Shared Secret Generation:**
        *   Generate an X25519 key pair.
        *   Generate a Kyber-768 key pair.
        *   If using a KEM approach for a symmetric key:
            *   The encapsulator generates a classical shared secret (`ss_c`) with the recipient's X25519 public key and a PQC shared secret (`ss_pqc`) via Kyber encapsulation with the recipient's Kyber public key.
            *   Concatenate: `combined_ss = ss_c || ss_pqc`.
            *   Derive the final symmetric encryption key using a strong KDF (e.g., HKDF with SHA-384 or SHA-512) from `combined_ss`.
    3.  **Ciphertext:** The file would be encrypted using the derived symmetric key. Metadata would need to store/reference the classical ephemeral public key (if applicable), the Kyber ciphertext, and necessary parameters (IV, tag).
*   **GPG Context:**
    *   If relying on GPG, Fava should monitor and support PQC-enabled GPG versions as they become stable.
    *   PQC-GPG would ideally implement a similar hybrid KEM approach internally for its public-key encryption operations. Fava would guide users on compatible GPG configurations.
*   **Fava's Python Backend:**
    *   Use `cryptography` library for X25519.
    *   Use `oqs-python` (liboqs wrapper) for Kyber-768 operations.
    *   Implement KDFs using `cryptography.hazmat.primitives.kdf`.

## 2. Data-in-Transit: HTTPS/TLS for Client-Server Communication

Fava uses HTTPS/TLS for securing communication between its Python backend and Svelte/JS frontend.

**Recommended Hybrid Approach:**

*   **Algorithm Pairing (for TLS Key Exchange):**
    *   **Classical KEM:** X25519 (standard in TLS 1.3).
    *   **PQC KEM:** Kyber-768 (ML-KEM, NIST Level 3).
*   **Construction Method (TLS 1.3 Hybrid Key Exchange):**
    *   Leverage emerging IETF standards for hybrid key exchange in TLS 1.3 (e.g., `draft-ietf-tls-hybrid-design`).
    *   This typically involves the client sending a concatenation of classical (e.g., X25519) and PQC (e.g., Kyber-768) key shares or encapsulated keys.
    *   The server processes both, and the resulting shared secrets are combined (e.g., via concatenation and KDF) to derive the TLS session keys.
*   **Fava's Python Backend (Server-Side):**
    *   The WSGI server (e.g., Cheroot) or a reverse proxy (e.g., Nginx) in front of Fava must be configured for PQC-TLS.
    *   This requires OpenSSL versions (e.g., OpenSSL 3.2+) that support PQC algorithms, potentially via the OQS provider.
    *   Fava's `cli.py` might need options to suggest or configure PQC cipher suites if the underlying server supports it directly, or provide guidance for reverse proxy configuration.
*   **Fava's Svelte/JS Frontend (Client-Side):**
    *   Relies on browser capabilities. Modern browsers are starting to experiment with PQC KEMs in TLS (e.g., Chrome's X25519Kyber768).
    *   No direct code changes in Fava's frontend `fetch` calls are typically needed, as the browser handles TLS. However, Fava should document supported browser versions or configurations for PQC-TLS.
    *   For testing or if browser support is lacking, a WASM-compiled PQC library could theoretically be used to implement a custom PQC-TLS handshake, but this is highly complex and generally not recommended for standard web applications.

## 3. Data Integrity

### a) WASM Module Signing

To ensure the integrity of WASM modules used in the frontend.

**Recommended Hybrid Approach:**

*   **Algorithm Pairing:**
    *   **Classical Signature:** ECDSA with P-256 and SHA-256.
    *   **PQC Signature:** Dilithium3 (ML-DSA-65, NIST Level 3).
*   **Construction Method:**
    1.  **Signing (Build Process):**
        *   Hash the WASM module (e.g., using SHA3-512 for future-proofing the hash input to signatures).
        *   Sign the hash with ECDSA P-256 to get `sig_c`.
        *   Sign the *same* hash with Dilithium3 to get `sig_pqc`.
        *   Distribute `sig_c` and `sig_pqc` alongside the WASM module (e.g., as separate `.sig_classical` and `.sig_pqc` files, or a combined metadata file).
    2.  **Verification (Frontend):**
        *   Fetch the WASM module, `sig_c`, and `sig_pqc`.
        *   Fetch the corresponding classical (ECDSA) and PQC (Dilithium3) public keys.
        *   Re-hash the WASM module locally using the same hash algorithm used during signing.
        *   Verify `sig_c` against the classical public key and the hash.
        *   Verify `sig_pqc` against the PQC public key and the hash.
        *   The WASM module is considered authentic if *both* signatures verify correctly.
*   **Fava's Frontend (Svelte/JS):**
    *   Use `window.crypto.subtle` for ECDSA P-256 verification and hashing.
    *   Use a WASM-compiled PQC library (e.g., `liboqs-js` or a dedicated Dilithium WASM module) for Dilithium3 verification.

### b) File Hashing (e.g., for optimistic concurrency in editor)

**Recommended Approach (Transition to PQC-Resistant Hash):**

*   **Algorithm:** SHA3-256 (or SHAKE256 with a fixed output length if preferred for certain PQC scheme compatibility).
*   **Rationale:** SHA-256's collision resistance is theoretically weakened by quantum computers (though preimage resistance is less affected). SHA-3 is considered more robust.
*   **Fava's Python Backend:**
    *   Use `hashlib.sha3_256()` for backend calculations.
*   **Fava's Svelte/JS Frontend:**
    *   Use a JavaScript SHA-3 library (e.g., `js-sha3`) or a WASM-compiled SHA-3 implementation. `window.crypto.subtle` does not natively support SHA-3.
    *   Ensure consistency in hashing (e.g., input encoding) between frontend and backend.

## General Implementation Considerations for Fava:

*   **Cryptographic Agility Layer:** Abstract cryptographic operations behind a service/utility layer in both Python and JavaScript to allow easier algorithm updates. This is outlined in [`docs/Plan.MD`](../../../../docs/Plan.MD).
*   **Library Management:**
    *   Python: Manage `oqs-python` and `cryptography` dependencies carefully.
    *   JavaScript: Manage WASM PQC libraries and JS crypto libraries, considering bundle size and performance.
*   **Performance:** Benchmark hybrid operations within Fava's context. While PQC operations can be slower, the impact depends on frequency and specific use case.
*   **User Experience:** For data-at-rest, if Fava takes a more active role beyond GPG, user-friendly key management for hybrid keys will be a significant challenge and design consideration.
*   **Configuration:** Fava's configuration options should allow specifying preferred algorithms or hybrid modes where applicable, with secure defaults.

These recommendations aim to align Fava's PQC integration with current best practices and the capabilities of its existing technology stack.