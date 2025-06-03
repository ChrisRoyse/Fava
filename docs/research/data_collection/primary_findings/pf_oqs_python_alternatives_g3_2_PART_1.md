# Primary Findings: Alternatives to oqs-python (Addressing Gap G3.2)

**Date Compiled:** 2025-06-02
**Research Focus:** G3.2: Alternatives to `oqs-python` if it's found lacking (maturity, security).
**Source:** AI Search (Perplexity MCP) - Query: "Are there viable alternative Python libraries to oqs-python for implementing Post-Quantum Cryptography (PQC) algorithms like Kyber, Dilithium, Falcon, SPHINCS+? Evaluate alternatives based on maturity (stability, production readiness), security (audits, known issues), algorithm coverage (especially NIST PQC standards), ease of integration with Python, and community support. Consider direct bindings to other C/Rust PQC libraries or pure Python PQC implementations if any exist."

This document evaluates potential Python library alternatives to `oqs-python` for implementing Post-Quantum Cryptography (PQC).

## Current Landscape of Python PQC Libraries

The Python ecosystem for PQC is still maturing. `oqs-python` (wrapping the C library `liboqs`) is currently the most prominent and comprehensive option for accessing a wide range of PQC algorithms, including NIST-selected KEMs and signature schemes.

**1. `oqs-python` (liboqs-python) - The Baseline**

*   **Strengths:**
    *   Wraps `liboqs`, which is actively developed by the Open Quantum Safe (OQS) project.
    *   Broad algorithm coverage, including Kyber, Dilithium, Falcon, SPHINCS+, and many experimental schemes.
    *   Relatively straightforward installation with automatic `liboqs` build/fetch.
    *   Active maintenance and alignment with `liboqs` releases.
*   **Weaknesses/Considerations:**
    *   `liboqs` itself is often marked as "for prototyping and evaluation purposes, not for production use" without thorough independent security audits of all algorithm implementations.
    *   Performance overhead due to Python CFFI calls compared to direct C usage.
    *   API can change as `liboqs` evolves with PQC standardization.

**2. Potential Alternatives & Related Approaches**

Based on the search, direct, mature, and widely supported drop-in Python alternatives to `oqs-python` with similar PQC algorithm coverage are scarce. However, some related packages or approaches exist:

*   **`pyoqs_sdk` (PyPI):**
    *   **Nature:** Appears to be another Python wrapper for `liboqs`.
    *   **Maturity:** The PyPI package information indicates a last update in 2023, which is significantly less recent than `oqs-python`'s ongoing development (e.g., `oqs-python` 0.12.0 released Jan 2025). This suggests it might be less maintained or an older fork/variant.
    *   **Security:** Relies on `liboqs`, so shares the same security considerations.
    *   **Algorithm Coverage:** Should mirror `liboqs` at the time of its last update.
    *   **Ease of Integration:** As a PyPI package, installation might be simple, but outdatedness is a concern.
    *   **Community Support:** Likely less community support than the primary `oqs-python` directly associated with the OQS project.
    *   **Viability as Alternative:** Potentially, but its apparent lack of recent maintenance makes it a less attractive option compared to the actively developed `oqs-python`.

*   **Custom Integration with OQS-OpenSSL:**
    *   **Nature:** This is not a standalone Python library but rather a system-level integration. It involves compiling OpenSSL with `liboqs` support (creating an OQS provider for OpenSSL 3.x or a patched OpenSSL 1.1.1) and then potentially having Python interact with this PQC-enabled OpenSSL via its `ssl` module or by calling the OpenSSL `s_client` / `s_server` command-line tools through `subprocess`.
    *   **Maturity:** Highly experimental and complex to set up and maintain.
    *   **Security:** Depends on the security of the OQS-OpenSSL integration and the underlying `liboqs` components.
    *   **Algorithm Coverage:** Limited to what the OQS provider for OpenSSL exposes (primarily KEMs for TLS).
    *   **Ease of Integration:** Very difficult for a typical Python application; more suited for specialized TLS server/client testing.
    *   **Community Support:** Niche, focused within the OQS and OpenSSL development communities.
    *   **Viability as Alternative:** Not a general-purpose library alternative for embedding PQC operations directly within Fava's application logic beyond TLS.

*   **Bindings to other C/Rust PQC Libraries (Hypothetical/Emerging):**
    *   **PQClean:** Provides clean, reference implementations of PQC algorithms in C. While direct Python bindings for PQClean implementations are not widely established as a comprehensive library, individual developers might create wrappers for specific algorithms. This would be a fragmented approach.
    *   **Rust PQC Libraries (e.g., `pqcrypto` crate family):** Rust has a growing PQC ecosystem. Python bindings to Rust libraries are possible (e.g., via `PyO3` or `rust-cpython`), but a mature, comprehensive PQC library for Python built this way, covering all NIST finalists, is not yet prominent. This remains an area for future development.
    *   **Cloudflare CIRCL (Go):** CIRCL is a strong cryptographic library in Go, including PQC. While Go code can be called from Python (e.g., via gRPC, or by compiling Go to a shared library and using CFFI), this introduces significant cross-language complexity and is not a straightforward "Python library" alternative.

*   **Pure Python PQC Implementations:**
    *   **Viability:** Generally considered impractical for PQC due to:
        *   **Performance:** PQC algorithms, especially lattice-based ones, are computationally intensive. Pure Python implementations would likely be too slow for most practical uses.
        *   **Security:** Implementing complex cryptographic primitives in a high-level, garbage-collected language like Python increases the risk of side-channel vulnerabilities (e.g., timing attacks) that are harder to mitigate than in C or Rust.
    *   **Availability:** No mature, widely recognized pure Python libraries implementing the full suite of NIST PQC finalists currently exist.

## Evaluation Summary for Alternatives

| Criterion            | `pyoqs_sdk` (Potential) | OQS-OpenSSL Custom | Other C/Rust Bindings | Pure Python Impls. |
|----------------------|-------------------------|--------------------|-----------------------|--------------------|
| **Maturity**         | Low (stagnant?)         | Experimental       | Emerging/Fragmented   | Non-existent/Low   |
| **Security**         | `liboqs`-dependent      | Complex/Custom     | Variable              | High Risk          |
| **NIST Coverage**    | `liboqs`-dependent      | TLS KEMs focused   | Variable/Incomplete   | Unlikely           |
| **Python Integration**| PyPI (if works)         | Very Complex       | Complex to Develop    | Easy (if available)|
| **Community**        | Likely Low              | Niche              | Small/Specific        | None               |

## Conclusion on Alternatives

For Fava's requirement of accessing NIST PQC algorithms like Kyber, Dilithium, Falcon, and SPHINCS+ from Python, **`oqs-python` (from the official OQS project) currently stands out as the most comprehensive and actively maintained option, despite its prototyping status.**

*   `pyoqs_sdk` appears to be a less maintained wrapper around the same `liboqs` core.
*   Custom OQS-OpenSSL integrations are too specialized for general in-application crypto.
*   Mature, comprehensive Python bindings to alternative C/Rust PQC libraries (other than `liboqs`) or robust pure Python PQC implementations are not yet readily available for the full suite of algorithms Fava needs.

Therefore, if `oqs-python` were found lacking (e.g., due to a critical unaddressed flaw in `liboqs` relevant to Fava's chosen algorithms, or severe long-term maintenance issues), the project would face a significant challenge. The most likely path in such a scenario would be to:
1.  Contribute to fixing/improving `liboqs`/`oqs-python`.
2.  Investigate creating custom Python bindings for a specific, audited C or Rust implementation of a *minimal set* of required PQC algorithms, which would be a substantial undertaking.

For now, focusing on `oqs-python` and closely monitoring the OQS project's progress, security audits, and alignment with finalized NIST standards seems the most pragmatic approach.