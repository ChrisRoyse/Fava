# Primary Findings: PQC-Resistant Hashing & Frontend Considerations - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Quantum resistance of SHA-2 (SHA-256) vs SHA-3 hash functions. Need to replace SHA-256 for general data integrity. PQC-specific hash functions vs standard SHA-3. Frontend JavaScript/WASM SHA-3 hashing libraries and window.crypto.subtle SHA-3 support.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on the quantum resistance of common hash functions, the need to transition from SHA-256, the role of SHA-3, and frontend implementation options.

## 1. Quantum Resistance: SHA-2 (SHA-256) vs. SHA-3

*   **SHA-256 (SHA-2 family):**
    *   **Grover's Algorithm Impact:** Quantum computers running Grover's algorithm can reduce the effective security against collision attacks. For SHA-256, with a classical collision resistance of 2<sup>128</sup>, the quantum collision resistance is often cited as 2<sup>128/3</sup> (approximately 2<sup>85</sup>) or its preimage resistance from 2<sup>256</sup> to 2<sup>128</sup> [1, 2, 4]. While still considered secure against current classical computers, its long-term viability in the quantum era is a concern for high-security applications.
*   **SHA-3 (Keccak family):**
    *   **Design:** SHA-3 was designed with different internal structures (sponge construction) than SHA-2 (Merkle-Damgård construction), making it inherently more resistant to attacks that might affect SHA-2.
    *   **Quantum Resistance:** SHA-3 is generally considered to have better quantum resistance properties. For example, SHA3-256 aims for 128-bit security against all classical and quantum attacks (for collision resistance, this means 2<sup>128</sup> quantum operations) [2, 4]. It's often described as "quantum-proof" in the sense that its security margins are expected to hold up well against known quantum algorithms [2].
    *   **Longevity:** Some sources suggest SHA-3 is designed to remain secure for billions of years under current quantum attack models [2].

## 2. Need to Replace SHA-256 for Data Integrity in Fava

*   **Current Fava Usage:** Fava uses SHA-256 for file integrity checks on save ([`src/fava/core/file.py`](src/fava/core/file.py:1)) and optimistic concurrency in the frontend editor ([`frontend/src/editor/SliceEditor.svelte`](../../../frontend/src/editor/SliceEditor.svelte)).
*   **Immediate Threat Level:** For general data integrity and optimistic locking, where preimage resistance is often more critical than collision resistance, SHA-256 is likely sufficient for the near to medium term. Grover's algorithm primarily speeds up brute-force collision finding, not necessarily finding a specific preimage for a given hash as easily.
*   **Proactive Transition:** However, for long-term security and to align with a general move towards PQC-resistant primitives, transitioning to SHA-3 (e.g., SHA3-256) or its extendable-output function (XOF) variants like SHAKE128/SHAKE256 is recommended for new systems or significant upgrades [1, 5]. This provides a higher security margin.

## 3. PQC-Specific Hash Functions vs. Standard SHA-3

*   **General Recommendation:** The consensus leans towards using well-vetted, standardized hash functions like SHA-3 rather than entirely new "PQC-specific" hash functions, unless those are part of a specific PQC signature scheme (like SPHINCS+ which is hash-based).
*   **SHA-3 Variants:**
    *   **SHA3-256, SHA3-512:** Standard fixed-output length hashes from the SHA-3 family.
    *   **SHAKE128, SHAKE256:** Extendable-Output Functions from the SHA-3 family. They can produce hashes of arbitrary length and are often recommended for PQC contexts due to their flexibility and strong security properties. For example, SHAKE128 with a 256-bit output can provide 128-bit security [1, 5].
*   NIST recommends SHA3-256 for new systems requiring quantum resistance where a fixed-size hash is appropriate [5].

## 4. Frontend Hashing: SHA-3 in JavaScript/WASM

If Fava's backend transitions to SHA3-256 for integrity checks, the frontend ([`frontend/src/editor/SliceEditor.svelte`](../../../frontend/src/editor/SliceEditor.svelte)) would need to compute the same hash.

*   **`window.crypto.subtle`:**
    *   **No Native SHA-3 Support:** As of mid-2025, `window.crypto.subtle` in major browsers **does not** natively support SHA-3 algorithms. It primarily supports SHA-1 (deprecated for security), SHA-256, SHA-384, and SHA-512.
*   **Third-Party JavaScript Libraries:**
    *   To use SHA-3 in the frontend, third-party JavaScript libraries are necessary.
    *   **Example:** `js-sha3` is a common library.
        ```javascript
        // Illustrative usage with js-sha3
        // import { sha3_256 } from 'js-sha3'; // Or from a UMD/global if not using modules
        // const dataToHash = "some content from the editor";
        // const hashHex = sha3_256(dataToHash);
        ```
*   **WASM-Accelerated Libraries:**
    *   For better performance than pure JavaScript implementations, WebAssembly (WASM) compiled versions of SHA-3 libraries can be used (e.g., `wasm-sha3`). These can offer significant speed improvements [5].
*   **Performance Considerations:**
    *   Pure JavaScript SHA-3 implementations are considerably slower than native `window.crypto.subtle` SHA-256 (e.g., cited as ~5x slower) [5].
    *   WASM can bring performance closer to native speeds but still involves the overhead of loading and interacting with the WASM module. Benchmarks mentioned suggest ~50 MB/s for WASM SHA3-256 versus ~500 MB/s for native SHA-256 [5].
    *   Hardware acceleration for SHA-3 is available on many modern server CPUs (e.g., ARMv8, IBM zArchitecture), making server-side hashing much faster if the client were to send raw data [5]. However, for optimistic locking, the client often computes the hash.

## 5. Identified Knowledge Gaps from this Search

*   **Maturity and Security Audits of JS SHA-3 Libraries:** While libraries like `js-sha3` exist, their security audit status and long-term maintenance outlook would need verification before production use.
*   **Bundle Size Impact of JS/WASM SHA-3 Libraries:** The impact of adding such libraries on Fava's frontend bundle size.
*   **Specific SHAKE128/256 JS Libraries:** While SHAKE is recommended, readily available and well-maintained JS libraries specifically for SHAKE (and their ease of use for fixed-length output comparable to SHA3-256) were not detailed.

*(This document will be updated or appended as more information is gathered.)*