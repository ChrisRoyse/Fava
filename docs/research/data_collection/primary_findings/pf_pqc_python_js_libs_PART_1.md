# Primary Findings: PQC Libraries in Python and JavaScript/WASM - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Status of Python PQC library liboqs (oqs-python): supported algorithms, stability, installation. Other Python PQC libraries. PQC in standard Python crypto libraries (hashlib, ssl, cryptography package). JavaScript/WASM PQC libraries beyond liboqs-js: maturity, browser compatibility, bundle size.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on Post-Quantum Cryptography (PQC) library support in Python and JavaScript/WebAssembly (WASM) environments.

## 1. Python PQC Libraries

### 1.1. `liboqs-python` (package name `oqs`)

This appears to be the most comprehensive Python wrapper for PQC algorithms, leveraging the `liboqs` C library.

*   **Current Status & Version:** Actively maintained, with version 0.12.0 released in January 2025 [3].
*   **Supported Algorithms:**
    *   Provides access to the full suite of PQC algorithms implemented in the underlying `liboqs` C library. This includes NIST PQC competition candidates and standardized algorithms [2, 4].
    *   **Key Encapsulation Mechanisms (KEMs):** CRYSTALS-Kyber (all NIST security levels), FrodoKEM, NTRU, BIKE.
    *   **Digital Signature Algorithms:** CRYSTALS-Dilithium (all NIST security levels), Falcon, SPHINCS+.
*   **Stability:** Described as having extensive testing via CI/CD pipelines and regular quarterly releases, suggesting a good level of stability for experimental and research use [3].
*   **Installation:**
    *   Requires a pre-built shared library of `liboqs` (C library, e.g., version 0.12.0 or newer).
    *   The `liboqs` C library typically needs to be cloned, built (e.g., using CMake and Ninja), and installed system-wide or in a location findable by the Python wrapper [5].
    *   Once `liboqs` is available, the Python wrapper can be installed via pip: `pip install oqs`.
*   **Example Usage (KEM):**
    ```python
    from oqs import KeyEncapsulation

    # Initialize KEM with a specific algorithm
    kem = KeyEncapsulation('Kyber512') # Or other supported KEMs

    # Key pair generation
    public_key = kem.generate_keypair()
    # secret_key is kept within kem object or returned by generate_keypair() depending on API version.
    # For oqs-python, secret_key is typically exported after generation if needed.
    # secret_key_bytes = kem.export_secret_key()


    # Encapsulation (by party A, using recipient's public_key)
    ciphertext, shared_secret_A = kem.encap_secret(public_key)

    # Decapsulation (by party B, using their private_key and the ciphertext)
    # Party B would have initialized 'kem_B' with their private_key loaded.
    # shared_secret_B = kem_B.decap_secret(ciphertext)
    ```
    *(Note: Exact API usage for secret key handling in `oqs-python` should be verified from its specific documentation, as the search result snippet was illustrative).*

### 1.2. Other Python PQC Libraries Mentioned

*   **PQCrypto:** Described as a lightweight PQC implementation in Python, potentially without C dependencies. This might imply it's a pure Python implementation, which could be slower but easier to deploy in some environments. *Further research needed on its scope and maturity.*
*   **Crystals-Kyber-Python:** A pure-Python implementation specifically for Kyber. Noted as not being production-ready, likely suitable for educational or research purposes.

### 1.3. PQC in Standard Python Cryptographic Libraries

As of early 2025, direct PQC algorithm support in Python's core cryptographic libraries is limited or experimental:

*   **`hashlib`:** No mention of PQC hash algorithms. Standard hashes like SHA-2/SHA-3 are available.
*   **`ssl` module:**
    *   No native PQC TLS 1.3 cipher suites are directly configurable in the standard `ssl` module.
    *   Experimental support for QUIC (which can use TLS 1.3) might exist with OpenSSL providers that include PQC (like an OQS provider for OpenSSL 3.x), but this is an advanced configuration.
*   **`cryptography` package (PyCA):**
    *   Plans exist to support NIST-standardized PQC algorithms like Dilithium and Kyber *after* full NIST standardization and FIPS publication.
    *   Current work towards PQC might be happening via its OpenSSL 3.x backend, if the linked OpenSSL has PQC capabilities (e.g., through an OQS provider) [4].

## 2. JavaScript/WASM PQC Libraries (Frontend)

Implementing PQC in the browser typically relies on WebAssembly to run compiled C/Rust code.

| Library         | Maturity     | Bundle Size (Approx.) | Browser Support Notes                                  |
| :-------------- | :----------- | :-------------------- | :----------------------------------------------------- |
| **`liboqs-js`** | Production-ready (derived from `liboqs`) | ~1.2 MB (can vary)    | Works in all modern browsers supporting WASM.          |
| **`PQCrypto.js`** | Beta         | ~890 KB               | Primarily tested in Chromium-based browsers.           |
| **`WASM-SPHINCS+`**| Experimental | ~310 KB               | Might have specific browser version requirements (e.g., Firefox 90+ mentioned). |

*   **Key Challenges for Frontend PQC:**
    *   **Performance:** Computationally intensive operations like PQC key generation can block the browser's main thread if not offloaded to Web Workers. Even with workers, operations can take >50ms [Perplexity Analysis].
    *   **Bundle Size:** PQC algorithms and their implementations can be large, increasing the initial JavaScript/WASM bundle size delivered to the client. Tree-shaking (removing unused code) is often difficult due to the monolithic nature of many cryptographic algorithm implementations.
    *   **Key Storage:** Securely storing PQC private keys on the client-side is challenging. `IndexedDB` has storage limitations and is not designed as a secure keystore.
*   **WebCrypto API:**
    *   The standard `window.crypto.subtle` API does **not** yet include support for PQC algorithms like Kyber or Dilithium.
    *   The example `window.crypto.subtle.generateKey({ name: 'Kyber-768' }, ...)` is illustrative of how it *might* look if support were added, but this is not currently functional with standard browser APIs. PQC operations require libraries like `liboqs-js`.

## 3. General Outlook

*   The PQC library ecosystem is actively developing, with `liboqs` and its Python wrapper being key resources for developers needing broad PQC algorithm access.
*   Standard library integration in Python is expected to follow once NIST standards are fully finalized and widely adopted (potentially 2026 onwards for more complete support) [2, 4].
*   Frontend PQC is feasible via WASM but comes with performance and bundle size trade-offs that need careful consideration for user experience.

## 4. Identified Knowledge Gaps from this Search

*   **Maturity & Security Audits of `PQCrypto` (Python) and `PQCrypto.js`:** More details on their development status, algorithm coverage, and security reviews.
*   **Practical Installation/Deployment of `liboqs` for Fava:** Specific guidance or best practices for bundling/distributing `liboqs` if Fava were to use `oqs-python`, especially across different operating systems.
*   **Detailed Performance Benchmarks:** More granular performance benchmarks for `liboqs-python` and `liboqs-js` operations (key-gen, sign, verify, encaps, decaps) on typical user hardware.
*   **Browser Compatibility Nuances for WASM PQC:** Any specific browser versions or WASM features required for optimal performance or compatibility of libraries like `liboqs-js`.

*(This document will be updated or appended as more information is gathered.)*