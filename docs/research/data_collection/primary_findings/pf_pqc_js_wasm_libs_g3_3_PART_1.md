# Primary Findings: JavaScript/WASM PQC Library Options (Addressing Gap G3.3)

**Date Compiled:** 2025-06-02
**Research Focus:** G3.3: PQC library options for JavaScript/WASM (for frontend WASM signing) - re-evaluate `liboqs-js` or alternatives.
**Source:** AI Search (Perplexity MCP) - Query: "Re-evaluate JavaScript/WASM PQC library options for frontend applications, specifically for WASM module signing and verification. Focus on liboqs-js: current status, maintenance, algorithm support (Kyber, Dilithium, Falcon, SPHINCS+), performance in browser, bundle size impact. Also, identify and evaluate any viable alternatives to liboqs-js, considering maturity, security, and ease of use for frontend PQC tasks. Cite official OQS resources, library repositories, or performance studies."

This document re-evaluates JavaScript/WebAssembly (WASM) library options for implementing Post-Quantum Cryptography (PQC) in frontend applications, particularly for tasks like WASM module signing and verification. The focus is on `liboqs-js` and potential alternatives.

## 1. `liboqs-js` (Open Quantum Safe Project)

`liboqs-js` is the official JavaScript/WASM wrapper for the `liboqs` C library.

*   **Current Status & Maintenance:**
    *   Actively maintained as part of the OQS project. Releases of `liboqs-js` generally align with `liboqs` C library updates.
    *   Recent `liboqs` releases (e.g., 0.10.0, 0.12.0, 0.13.0 in Jan 2025) include updates for NIST PQC algorithms and security fixes (e.g., for HQC vulnerability CVE-2025-48946 fixed in liboqs 0.13.0). `liboqs-js` would inherit these.
    *   The OQS Technical Steering Committee (TSC) meetings discuss ongoing work on language wrappers, including JavaScript/WASM compatibility.
    *   CI tests are in place, indicating ongoing development and testing.
*   **Algorithm Support:**
    *   Inherits algorithm support from the version of `liboqs` it's compiled against.
    *   **Kyber (ML-KEM):** Supported.
    *   **Dilithium (ML-DSA):** Supported.
    *   **Falcon:** Supported (fixed-length signature variants added in `liboqs` 0.10.0).
    *   **SPHINCS+ (SLH-DSA):** Supported.
    *   Also supports other experimental/round candidate algorithms available in `liboqs`.
*   **Performance in Browser:**
    *   WASM execution generally incurs some overhead compared to native C execution (often cited as 2-3x slower for CPU-bound tasks, but can vary).
    *   Specific performance for PQC operations (keygen, sign, verify, encaps, decaps) in `liboqs-js` would depend on the algorithm, parameter set, browser's WASM engine, and underlying hardware.
    *   Lack of direct WebAssembly features like widespread SIMD or mature multi-threading (though WASI 0.3 and Component Model are evolving) can impact highly optimized PQC implementations.
*   **Bundle Size Impact:**
    *   `liboqs` is a comprehensive library supporting many algorithms. A WASM build including all algorithms can be substantial (e.g., several megabytes).
    *   The ability to create custom, lean builds of `liboqs-js` (compiling only specific required algorithms) is crucial for frontend applications to manage bundle size. The OQS project has been working on improving build customization.
*   **Ease of Use:**
    *   Provides a JavaScript API to access PQC functionalities.
    *   Requires integration of the WASM module into the frontend build process (e.g., with Webpack, Rollup).
    *   Memory management for cryptographic objects created via WASM might require manual `free()` calls, which can be error-prone if not handled carefully.
*   **Security:**
    *   Relies on the security of the underlying `liboqs` C implementations. Audits of `liboqs` (like the one by Trail of Bits) are important.
    *   WASM environment itself offers some sandboxing, but vulnerabilities in the C code can still be exposed.

## 2. Potential Alternatives to `liboqs-js`

Viable, mature, and comprehensive alternatives to `liboqs-js` for the full suite of NIST PQC algorithms in JavaScript/WASM are limited. Most efforts are concentrated around the OQS ecosystem or are algorithm-specific.

*   **Algorithm-Specific JavaScript/WASM Libraries:**
    *   **PQC.js (Community Effort):** Some community-driven projects like "PQC.js" might exist, potentially offering pure JavaScript implementations or WASM builds of specific algorithms (e.g., Kyber, Dilithium).
        *   **Maturity & Security:** Often less mature, may lack formal security audits, and maintenance can be inconsistent compared to larger projects like OQS.
        *   **Bundle Size:** Might be smaller if focused on a single algorithm.
    *   **Tink-WASM (Google):** Google's Tink cryptographic library has some WebAssembly support. While primarily focused on classical cryptography, it might include select PQC algorithms (e.g., Kyber was mentioned in search results for KEMs).
        *   **Maturity & Security:** Tink is generally well-regarded for security and has a production focus.
        *   **Algorithm Coverage:** PQC coverage might be limited compared to `liboqs-js`.
        *   **Bundle Size:** Likely optimized for size if offering specific algorithms.
*   **PQClean-WASM (Hypothetical/Research-Oriented):**
    *   PQClean provides reference C implementations. Compiling these to WASM is feasible.
    *   **Maturity:** Would likely be experimental or research-focused unless a dedicated project maintains stable WASM bindings for PQClean.
    *   **Ease of Use:** Would require significant effort to create and maintain user-friendly JavaScript APIs.
*   **Pure JavaScript PQC Implementations:**
    *   **Performance & Security Concerns:** As with Python, pure JS implementations of complex PQC algorithms are generally too slow for practical use and are harder to secure against side-channels. They are rare for NIST finalists.

## Evaluation Criteria for Alternatives:

*   **Maturity:** `liboqs-js` benefits from the OQS project's ongoing development. Alternatives are often less mature or more narrowly focused.
*   **Security:** Security of `liboqs-js` is tied to `liboqs` (which has had some audits). Alternatives would need their own security vetting.
*   **Algorithm Coverage:** `liboqs-js` aims for broad coverage. Alternatives are often algorithm-specific.
*   **Ease of Use:** `liboqs-js` provides a direct path, though WASM integration has its complexities. Alternatives might offer simpler APIs for specific tasks if they exist.
*   **Bundle Size:** This is a critical concern for frontend. `liboqs-js` can be large if not customized. Algorithm-specific alternatives might be smaller.

## Recommendations for Fava's Frontend WASM Signing:

1.  **Primary Option: `liboqs-js`**
    *   **Action:** Continue to evaluate and use `liboqs-js`, focusing on the latest versions aligned with audited `liboqs` releases.
    *   **Mitigation for Bundle Size:** Investigate and utilize any available mechanisms for creating custom builds of `liboqs-js` that include only the necessary signature schemes (e.g., Dilithium, Falcon, SPHINCS+) for Fava's WASM module integrity checks.
    *   **Performance Testing:** Benchmark the chosen signature verification algorithms in target browsers.
    *   **Memory Management:** Pay close attention to memory management in the JavaScript code interacting with the WASM module.

2.  **Secondary/Contingency: Algorithm-Specific WASM Modules**
    *   If `liboqs-js` proves too large or problematic, consider using or even sponsoring the development/maintenance of a standalone, optimized WASM module for just Dilithium (or the chosen PQC signature algorithm). This could be based on PQClean C code or a minimal `liboqs` build.
    *   This approach increases integration effort but can provide better control over bundle size and performance for a specific need.

3.  **Avoid Pure JS Implementations:** For security-critical signature verification, pure JS PQC implementations are generally not recommended.

**Conclusion:**
For Fava's frontend PQC needs, `liboqs-js` remains the most comprehensive starting point due to its direct link to the OQS C library and its broad algorithm support. The main challenges are managing bundle size and ensuring robust integration. Exploring custom builds of `liboqs-js` or, as a fallback, highly specific single-algorithm WASM modules, are key strategies.