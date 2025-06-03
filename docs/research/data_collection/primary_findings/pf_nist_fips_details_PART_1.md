# Primary Findings: NIST PQC Standards (FIPS 203, 204, 205) Details - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Tool: `get_documentation`, Query: "NIST PQC standards FIPS 203 ML-KEM (CRYSTALS-Kyber), FIPS 204 ML-DSA (CRYSTALS-Dilithium), FIPS 205 SLH-DSA (SPHINCS+)", Context: "Extract specific key sizes (public, private), signature/ciphertext sizes in bytes, and typical performance benchmarks (key-gen, encrypt/encaps, decrypt/decaps, sign, verify latency or ops/sec) for all security levels of these algorithms.") - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes specific details extracted for the initial NIST Post-Quantum Cryptography (PQC) standards: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA).

## 1. FIPS 203: ML-KEM (Module-Lattice-based Key-Encapsulation Mechanism - CRYSTALS-Kyber)

*   **Purpose:** A Key Encapsulation Mechanism (KEM) designed for secure key exchange, resistant to quantum attacks. Used to establish a shared secret between two parties [1, 2].
*   **Cryptographic Basis:** Security is based on the hardness of solving learning with errors (LWE) problems over module lattices [2].
*   **Security Levels:** Supports multiple security levels, typically corresponding to NIST PQC security strength categories 1, 3, and 5.
    *   **Level 1 (e.g., ML-KEM-512):** Comparable to AES-128 classical security.
    *   **Level 3 (e.g., ML-KEM-768):** Comparable to AES-192 classical security.
    *   **Level 5 (e.g., ML-KEM-1024):** Comparable to AES-256 classical security.

*   **Typical Parameters (Sizes in Bytes):**

    | Security Level (Kyber Variant) | Public Key | Private Key | Ciphertext (Encapsulated Secret) |
    | :----------------------------- | :--------- | :---------- | :------------------------------- |
    | Level 1 (ML-KEM-512)           | 800        | 1632        | 768                              |
    | Level 3 (ML-KEM-768)           | 1184       | 2400        | 1088                             |
    | Level 5 (ML-KEM-1024)          | 1568       | 3168        | 1568                             |
    *(Source: Perplexity analysis of FIPS 203 context)*

*   **Performance (Illustrative, from search result [5]):**
    *   **Key Generation:** Generally fast, cited as <10 ms for Level 1, scaling with security level.
    *   **Encapsulation/Decapsulation:** Very fast, often cited around ~0.1 ms on modern CPUs.

## 2. FIPS 204: ML-DSA (Module-Lattice-based Digital Signature Algorithm - CRYSTALS-Dilithium)

*   **Purpose:** A digital signature algorithm for ensuring data integrity and authenticity, resistant to quantum attacks [3, 4].
*   **Cryptographic Basis:** Security is based on the hardness of problems over module lattices [3].
*   **Security Levels:** Supports different security levels, often referred to by their underlying Dilithium variant.
    *   **Level 2 (e.g., ML-DSA-44 / Dilithium2):** Targets NIST PQC security strength category 2/3.
    *   **Level 3 (e.g., ML-DSA-65 / Dilithium3):** Targets NIST PQC security strength category 3/4.
    *   **Level 5 (e.g., ML-DSA-87 / Dilithium5):** Targets NIST PQC security strength category 5.

*   **Typical Parameters (Sizes in Bytes):**

    | Security Level (Dilithium Variant) | Public Key | Private Key | Signature |
    | :--------------------------------- | :--------- | :---------- | :-------- |
    | Level 2 (ML-DSA-44)                | 1312       | 2528        | 2420      |
    | Level 3 (ML-DSA-65)                | 1952       | 4000        | 3293      |
    | Level 5 (ML-DSA-87)                | 2592       | 4864        | 4595      |
    *(Source: Perplexity analysis of FIPS 204 context)*

*   **Performance (Illustrative, from search result [5]):**
    *   **Signing:** ~2.5 ms (Level 2) up to ~8 ms (Level 5).
    *   **Verification:** Very fast, around ~0.5 ms across all levels.

## 3. FIPS 205: SLH-DSA (Stateless Hash-Based Digital Signature Algorithm - SPHINCS+)

*   **Purpose:** A stateless hash-based digital signature algorithm, providing an alternative to lattice-based signatures with different security assumptions [4, 5]. Often considered a conservative choice due to reliance on well-understood hash function security.
*   **Cryptographic Basis:** Security relies on the properties of the underlying hash functions (e.g., SHA-256 or SHAKE). It is stateless, meaning the signer does not need to maintain state between signatures (unlike older stateful hash-based signatures).
*   **Security Levels:** Supports various parameter sets targeting different security levels.

*   **Typical Parameters (Sizes in Bytes):** (Note: SPHINCS+ parameters can be tuned; these are representative examples)

    | Security Level (SPHINCS+ Variant) | Public Key | Private Key | Signature |
    | :-------------------------------- | :--------- | :---------- | :-------- |
    | Level 1 (e.g., SPHINCS+-SHA256-128f-simple) | 32         | 64          | 7856      |
    | Level 3 (e.g., SPHINCS+-SHA256-192f-simple) | 48         | 96          | 17088 (*Adjusted based on typical SPHINCS+ sizes, Perplexity provided 16216 which might be for a specific variant*) |
    | Level 5 (e.g., SPHINCS+-SHA256-256f-simple) | 64         | 128         | 35664 (*Perplexity provided 35664, public/private key sizes were small in its output, usually they are this small for SPHINCS+*) |
    *(Source: Perplexity analysis of FIPS 205 context, with some typical SPHINCS+ size context. Original Perplexity output for L3 Pub/Priv was 32/64, L5 Pub/Priv was 32/64. SPHINCS+ public/private keys are indeed very small.)*

*   **Performance (Illustrative, from search result [5]):**
    *   **Signing:** Slower than lattice-based schemes, e.g., ~15 ms (Level 1) up to ~50 ms (Level 5).
    *   **Verification:** Relatively fast, around ~1 ms across all levels.

## 4. Installation and Usage (General Approach)

*   **Library Integration:** The primary way to use these algorithms is through cryptographic libraries that implement the NIST standards. The Open Quantum Safe (OQS) project's `liboqs` is a prominent C library.
    ```bash
    # Example: Cloning and building liboqs (from Perplexity output)
    git clone https://github.com/open-quantum-safe/liboqs
    # cd liboqs && mkdir build && cd build
    # cmake -S . -B build -DBUILD_SHARED_LIBS=ON # (Path adjusted)
    # cmake --build build
    ```
    (Actual build steps for liboqs might involve `cmake ..` from within the build directory, then `make` or `ninja`).
*   **Language Bindings:** Wrappers like `oqs-python` (for Python) or `liboqs-js` (for JavaScript/WASM) provide access to `liboqs` functionalities.
*   **Example Usage (Python with `cryptography` package, if/when PQC is integrated, conceptual):**
    The Perplexity output provided illustrative examples using the `cryptography` package's API style, which is a good target for future usability.
    ```python
    # ML-KEM (Kyber) - Conceptual based on cryptography package style
    # from cryptography.hazmat.primitives.asymmetric import kyber # Hypothetical import
    # private_key = kyber.generate_private_key(kyber.KyberLevel3) # Or specific variant
    # public_key = private_key.public_key()
    # ciphertext, shared_secret = public_key.encapsulate() # On sender side with recipient's public key
    # recovered_shared_secret = private_key.decapsulate(ciphertext) # On recipient side

    # ML-DSA (Dilithium) - Conceptual
    # from cryptography.hazmat.primitives.asymmetric import dilithium # Hypothetical import
    # private_key = dilithium.generate_private_key(dilithium.DilithiumLevel3)
    # public_key = private_key.public_key()
    # signature = private_key.sign(b"Message to sign")
    # public_key.verify(signature, b"Message to sign")
    ```

## 5. Best Practices and Pitfalls (General from Perplexity output)

*   **Best Practices:**
    *   **Hybrid Deployments:** Combine PQC with proven classical algorithms (e.g., ECDSA + ML-DSA, or a classical KEM + ML-KEM) during the transition for backward compatibility and defense-in-depth [5].
    *   **Key Rotation:** Implement robust key lifecycle management, including regular key rotation. PQC key management is an active area of research.
    *   **Benchmarking:** Thoroughly test PQC algorithm performance in the specific target environments and use cases.
*   **Pitfalls to Avoid:**
    *   **Over-reliance on a Single Algorithm Type:** Diversify cryptographic primitives where possible (e.g., not using lattice-based schemes for everything if alternatives exist and are suitable).
    *   **Ignoring Parameter Updates:** Stay informed about NIST updates to security levels, parameter sets, or implementation guidelines for the standardized algorithms.
    *   **Underestimating Performance of SPHINCS+:** While very secure, SPHINCS+ has significantly larger signatures and can be slower for signing than lattice-based schemes; it may not be suitable for all high-throughput applications.

## 6. Official Documentation Links (from Perplexity output)

*   **FIPS 203 (ML-KEM):** [https://csrc.nist.gov/pubs/fips/203/final](https://csrc.nist.gov/pubs/fips/203/final) [2]
*   **FIPS 204 (ML-DSA):** [https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards) [3] (This link is a news release, the actual FIPS doc would be separate).
*   **FIPS 205 (SLH-DSA):** [https://csrc.nist.gov/news/2024/postquantum-cryptography-fips-approved](https://csrc.nist.gov/news/2024/postquantum-cryptography-fips-approved) [4] (This link is also a news release).

*Note: The actual FIPS documents should be consulted for definitive parameter sets and specifications.*

## 7. Identified Knowledge Gaps from this Search (Related to G1.1)

*   **Consolidated Official Performance Benchmarks:** While the search provided some illustrative performance numbers, official, comprehensive benchmark suites and results from NIST or trusted third parties across various platforms for all security levels of FIPS 203, 204, 205 would be valuable. The provided figures are helpful but may not cover all conditions.
*   **Official OIDs (Reiteration of G1.2):** This search did not yield the official OIDs for these FIPS standards.

*(This document will be updated or appended as more information is gathered.)*