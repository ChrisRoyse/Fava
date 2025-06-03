# Primary Findings: PQC Signatures for WASM Integrity & SRI Comparison - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "PQC digital signatures (CRYSTALS-Dilithium, Falcon, SPHINCS+) for WASM module integrity. Tools for PQC signature generation. Secure PQC public key distribution for frontend verification. JavaScript/WASM PQC signature verification libraries (e.g., liboqs-js), client-side performance. Subresource Integrity (SRI) vs PQC for WASM integrity.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on using Post-Quantum Cryptography (PQC) digital signatures for WebAssembly (WASM) module integrity, including suitable algorithms, tools, frontend verification, and comparison with Subresource Integrity (SRI).

## 1. PQC Digital Signature Algorithms for WASM Integrity

Selecting a PQC signature scheme for WASM involves balancing signature size, verification speed (critical for client-side performance), and key sizes. NIST's PQC standardization effort provides key candidates [1, 3].

*   **CRYSTALS-Dilithium (Lattice-based):**
    *   **Strengths:** Considered a primary recommendation by NIST for general use due to a good balance between signature size (e.g., ~2.4 KB for Dilithium3) and fast verification speeds [1, 3]. Fast verification is advantageous for client-side WASM loading.
    *   **Considerations for WASM:** Public key sizes are around 1.2 KB, which could add to the initial download if embedded or fetched separately.
*   **Falcon (NTRU Lattice-based):**
    *   **Strengths:** Offers significantly smaller signatures (e.g., ~690 bytes for Falcon-512) compared to Dilithium, which is beneficial for bandwidth-constrained scenarios [1, 4].
    *   **Considerations for WASM:** Signing is generally slower, and its reliance on floating-point arithmetic can be complex to implement efficiently and securely in WASM runtimes, potentially impacting performance or increasing vulnerability surface if not handled carefully [5].
*   **SPHINCS+ (Hash-based):**
    *   **Strengths:** Strong security properties based on well-understood hash functions, offering resistance against quantum attacks without relying on structured mathematical problems like lattices [1, 4].
    *   **Considerations for WASM:** Produces very large signatures (e.g., ~8 KB to 16 KB or more), and verification can be slower than Dilithium or Falcon. This makes it less practical for frequently updated or performance-sensitive WASM modules [4, 5].

**Illustrative Use Case (Conceptual):**
The [`docs/Plan.MD`](docs/Plan.MD) suggests signing `tree-sitter-beancount.wasm`. If Dilithium3 were used:
```bash
# Example: Signing a WASM module with Dilithium using a tool like oqs-sign from liboqs
# oqs-sign -algorithm Dilithium3 -message tree-sitter-beancount.wasm -signature output.sig -public_key_out public_key.pem
```

## 2. Tools for PQC Signature Generation

*   **liboqs (Open Quantum Safe):** A C library providing implementations of many PQC algorithms, including Dilithium, Falcon, and SPHINCS+. It often includes command-line tools (like `oqs-sign`) and can be integrated into build processes. Language bindings (Python, Node.js) are also available [5].
*   **PQClean:** Offers reference implementations of PQC algorithms, useful for testing and building custom signing tools.
*   **Cloudflare's PQC Implementations:** Cloudflare has experimented with PQC, including in their TLS stack (e.g., using patched BoringSSL) [5]. While server-focused, their research and open-source contributions can be informative.
*   **OpenSSL (Future/Experimental):** As OpenSSL integrates PQC (e.g., via providers like OQS Provider), its command-line tools may eventually support PQC signing directly.

## 3. Secure Public Key Distribution for Frontend Verification

For the frontend to verify a PQC-signed WASM module, it needs access to the corresponding public key securely.

*   **Hybrid Certificates:** X.509 certificates could be issued with dual signatures (e.g., classical ECDSA + PQC Dilithium) or include PQC public keys alongside classical ones. This allows a transitional period where browsers/systems can verify using whichever algorithm they support [2]. This relies on CAs supporting such hybrid certificates.
*   **Embedding Public Key:** The PQC public key could be embedded directly within the main JavaScript application code that loads the WASM module. This is simpler but requires updating the application if the key changes.
*   **Fetching Public Key:** The public key could be fetched from a trusted endpoint. This requires securing the endpoint itself (e.g., with traditional TLS, eventually PQC TLS).
*   **Signed HTTP Exchanges (SXGs):** Could potentially be used to package the WASM module, its signature, and the public key, all signed by a trusted source.
*   **Certificate Transparency & Pinning:** Standard web security practices like Certificate Transparency logs and public key pinning (HPKP - though deprecated for general websites, concepts might apply to specific app contexts) could provide additional layers of security for fetched public keys.

## 4. Client-Side (Frontend) PQC Signature Verification

*   **liboqs-js:** A WebAssembly-compiled version of `liboqs`, enabling PQC operations, including signature verification, directly in the browser [5].
*   **Web Crypto API Polyfills/Extensions:** In the future, browser Web Crypto APIs might be extended to support PQC algorithms natively. For now, WASM-based libraries like `liboqs-js` are the primary route.
*   **Performance Considerations (Illustrative, from search result [5]):**
    *   **Dilithium3:** Verification cited around ~15 ms on modern devices using `liboqs-js`.
    *   **Falcon-512:** Verification cited around ~22 ms.
    *   **SPHINCS+-SHAKE (variant):** Verification cited around ~85 ms.
    These times are generally acceptable for a one-time verification when loading a WASM module, but Dilithium offers the best performance among these.

## 5. Subresource Integrity (SRI) vs. PQC Signatures for WASM

*   **Subresource Integrity (SRI):**
    *   **Mechanism:** Uses a cryptographic hash (e.g., SHA-256, SHA-384, SHA-512) of the WASM file. The browser fetches the file, computes its hash, and compares it to the expected hash provided in the HTML tag's `integrity` attribute.
    *   **Provides:** Integrity (ensures the file hasn't been modified in transit or on the server after the hash was generated).
    *   **Limitations:**
        *   **No Authenticity:** SRI does not verify *who* provided the file or the hash. An attacker who compromises the server can replace both the file and its SRI hash.
        *   **Quantum Vulnerability:** The hash algorithms used by SRI (SHA-2, SHA-3) are susceptible to (though not easily broken by) quantum pre-image or collision attacks with Grover's algorithm, reducing their effective security over the very long term [4].
*   **PQC Digital Signatures:**
    *   **Mechanism:** The WASM module is signed with a PQC private key during the build/deployment. The frontend verifies this signature using the corresponding PQC public key.
    *   **Provides:**
        *   **Integrity:** Ensures the WASM module has not been altered.
        *   **Authenticity:** Verifies that the module was signed by the legitimate owner of the private key.
    *   **Advantages over SRI:** Stronger security guarantees, especially authenticity, and designed for quantum resistance.
*   **Complementary Use:**
    *   PQC signatures and SRI are not mutually exclusive and can be used together for defense-in-depth.
    *   SRI provides a quick integrity check against accidental corruption or CDN errors.
    *   PQC signatures provide stronger assurance of authenticity and integrity against sophisticated attackers, including those with quantum capabilities.
    *   **Example (Conceptual):**
        ```html
        <script src="app.wasm"
                integrity="sha384-{SRI_HASH} pqc-sig-dilithium3-{SIGNATURE_OR_LINK_TO_SIG}"
                pqc-public-key="{PUBLIC_KEY_OR_LINK_TO_KEY}">
        </script>
        ```
        *(Note: Actual implementation would involve JavaScript fetching and verifying the PQC signature).*

## 6. Identified Knowledge Gaps from this Search

*   **Standardized Formats for PQC Signatures/Keys in Web Contexts:** While SRI has a clear HTML attribute, how PQC signatures and public keys would be optimally referenced or embedded for JavaScript-based verification is not yet standardized.
*   **Maturity and Audit Status of `liboqs-js`:** Detailed information on the security audits, maintenance status, and production-readiness of `liboqs-js` for critical security functions.
*   **Real-world Performance of PQC Verification in Fava's Frontend Stack:** Specific benchmarks within Fava's Svelte frontend environment, considering bundle size impact of `liboqs-js`.

*(This document will be updated or appended as more information is gathered.)*