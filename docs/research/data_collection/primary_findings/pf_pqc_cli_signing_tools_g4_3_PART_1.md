# Primary Findings: Command-Line PQC Signing Tools for WASM Integrity (Addressing Gap G4.3)

**Date Compiled:** 2025-06-02
**Research Focus:** G4.3: Availability and maturity of a command-line `pqc-signing-tool` suitable for the WASM module signing build process.
**Source:** AI Search (Perplexity MCP) - Query: "Availability and maturity of command-line tools for PQC digital signatures (e.g., Dilithium, Falcon, SPHINCS+) suitable for a build process, specifically for signing WASM modules. Are there tools based on liboqs, PQClean, or other PQC libraries? Evaluate based on stability, ease of use for scripting, supported algorithms, and output signature formats. Cite project repositories or official documentation."

This document summarizes findings on command-line tools for Post-Quantum Cryptography (PQC) digital signatures, suitable for build processes like WASM module signing.

## Overview of PQC Command-Line Signing Tools

The availability of mature, dedicated, and universally packaged command-line PQC signing tools is still evolving alongside the PQC ecosystem. Most current options are often example programs or utilities bundled with cryptographic libraries like `liboqs` or reference implementations from projects like PQClean.

**1. Tools Based on `liboqs` (Open Quantum Safe Project):**

*   **Availability & Nature:** The OQS project, primarily through its `liboqs` C library, provides the foundational implementations for many PQC algorithms. Command-line utilities are often included as examples or testing tools within the `liboqs` repository or its language wrapper projects.
*   **Example Tool (`pq-sign` or similar from `liboqs` examples/tests):**
    *   The research paper cited in the search results ([5] from the original query context, though not directly provided in this specific search's results) mentioned a command-line tool named `pq-sign` used in conjunction with `liboqs-python` for signing files. Such tools typically offer functionalities like:
        *   `generate-keypair --alg <algorithm_name> --pubkey <pubkey_file> --privkey <privkey_file>`
        *   `sign --alg <algorithm_name> --privkey <privkey_file> --infile <file_to_sign> --outfile <signature_file>`
        *   `verify --alg <algorithm_name> --pubkey <pubkey_file> --infile <file_to_verify> --sigfile <signature_file>`
*   **Supported Algorithms:** Would support algorithms available in the linked `liboqs` version, including:
    *   Dilithium (ML-DSA)
    *   Falcon
    *   SPHINCS+ (SLH-DSA)
*   **Maturity & Stability:**
    *   These tools are often intended for demonstration, testing, or development rather than as hardened production utilities.
    *   Stability depends on the underlying `liboqs` version. `liboqs` itself is for "prototyping and evaluation."
*   **Ease of Use for Scripting:** Generally straightforward command-line arguments, making them suitable for scripting in a build process.
*   **Output Signature Formats:** Typically raw binary signature data. The build process would need to handle this format, potentially Base64 encoding it or embedding it as needed for WASM module verification.
*   **Source/Repository:** Found within the `liboqs` GitHub repository (e.g., in `tests/` or `examples/` subdirectories) or related OQS language wrapper projects.
    *   [Open Quantum Safe `liboqs` GitHub](https://github.com/open-quantum-safe/liboqs)

**2. Tools Based on PQClean:**

*   **Availability & Nature:** The PQClean project provides reference C implementations of PQC schemes submitted to the NIST PQC standardization process. These implementations often come with basic command-line utilities (e.g., `PQCgenKAT_sign`, `PQCsign`) for generating Known Answer Tests (KATs) and performing sign/verify operations.
*   **Supported Algorithms:** Covers a wide range of PQC algorithms, including all NIST finalists and winners like Dilithium, Falcon, and SPHINCS+.
*   **Maturity & Stability:**
    *   Implementations aim for clarity and correctness ("clean") rather than high optimization or production hardening.
    *   Primarily for testing and algorithm evaluation.
*   **Ease of Use for Scripting:** The KAT generation tools might be adaptable for build process signing, but their primary interface is for testing. Custom scripting would likely be required.
*   **Output Signature Formats:** Raw binary.
*   **Source/Repository:**
    *   [PQClean GitHub](https://github.com/PQClean/PQClean)

**3. OpenSSL with PQC Provider (via OQS):**

*   **Availability & Nature:** If OpenSSL is compiled with a PQC provider (like the one from OQS for OpenSSL 3.x), the `openssl dgst` or `openssl pkeyutl` commands *might* be extendable or usable for PQC signatures if the provider exposes these capabilities appropriately.
    *   Example (Conceptual - actual commands depend on provider implementation):
        ```bash
        # Key generation might still be via liboqs tools
        # openssl dgst -sign pqc_privkey.pem -sigopt alg:Dilithium3 -out signature.sig message.bin
        # openssl dgst -verify pqc_pubkey.pem -sigopt alg:Dilithium3 -signature signature.sig message.bin
        ```
*   **Maturity & Stability:** Experimental. Depends heavily on the maturity of the OQS provider for OpenSSL and its integration.
*   **Ease of Use:** Could be familiar to those used to OpenSSL's CLI, but PQC-specific options and handling would be new.
*   **Supported Algorithms:** Dependent on what the OQS provider exposes to OpenSSL.

**4. Commercial/SDK-Based Tools:**

*   Some commercial entities like DigiCert are developing SDKs (e.g., TrustCore SDK) and tools that support PQC algorithms.
*   These are typically not open-source command-line tools suitable for general build processes without licensing and integration with the vendor's ecosystem. They are more geared towards PKI and certificate management.

## Considerations for WASM Module Signing in a Build Process:

*   **Automation:** The chosen tool must be easily scriptable.
*   **Key Management:** The build process needs secure access to the PQC private key used for signing.
*   **Signature Distribution:** The generated signature needs to be distributed alongside the WASM module. The frontend will then fetch the module and its signature for verification.
*   **Reproducibility:** The signing process should be deterministic if possible (though some PQC signature schemes have inherent randomness, the verification must still work).
*   **Dependency Management:** Integrating C-based tools (from `liboqs` or PQClean) into a build environment requires compiling them, which can add complexity (especially cross-platform).

## Recommendations for Fava:

1.  **Primary Option: Utilities from `liboqs` / `oqs-python`:**
    *   The most straightforward path is likely to use or adapt the example command-line signing utilities provided with `liboqs` or potentially accessible/scriptable via `oqs-python`.
    *   This aligns with using `oqs-python` for other backend PQC tasks and `liboqs-js` for frontend verification, ensuring algorithm consistency.
    *   The build script would call these utilities to sign the WASM module.

2.  **Alternative: Custom Tool using PQClean Implementations:**
    *   If a more lightweight or specific implementation is needed, one could compile a chosen signature scheme (e.g., Dilithium) from PQClean and create a minimal command-line wrapper around its sign function. This offers more control but requires more C development/integration effort.

3.  **Avoid reliance on complex OpenSSL PQC CLI for this specific task** unless already deeply integrated for other reasons, as the PQC CLI support there is less direct for simple file signing compared to dedicated library examples.

**Conclusion:**
For signing WASM modules in Fava's build process, leveraging the command-line examples/utilities from the `liboqs` project (potentially scripted via Python if `oqs-python` offers such CLI access or by directly calling compiled C utilities) appears to be the most direct and consistent approach, given the project's likely use of the OQS ecosystem. Stability will be tied to `liboqs`'s development status.

This information addresses knowledge gap G4.3 regarding command-line PQC signing tools.