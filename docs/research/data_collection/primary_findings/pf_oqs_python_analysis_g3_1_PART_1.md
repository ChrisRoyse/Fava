# Primary Findings: oqs-python Library Analysis (Addressing Gap G3.1)

**Date Compiled:** 2025-06-02
**Research Focus:** G3.1: Deep dive into `oqs-python`: current maintenance status, reported vulnerabilities, community support, ease of use for Kyber/Dilithium/Falcon/SPHINCS+.
**Source:** AI Search (Perplexity MCP) - Query: "Detailed analysis of oqs-python library: current maintenance status (last commit, release frequency), known reported vulnerabilities (CVEs or security advisories), community support (GitHub issues, contributors, dependent projects), and ease of use for implementing Kyber (ML-KEM), Dilithium (ML-DSA), Falcon, and SPHINCS+ (SLH-DSA). Include information on installation, API stability, and documentation quality. Cite official Open Quantum Safe (OQS) project resources or reputable security databases."

This document provides an analysis of the `oqs-python` library, a key component for integrating Post-Quantum Cryptography (PQC) into Python applications like Fava.

## 1. Maintenance Status

*   **Project Affiliation:** `oqs-python` is part of the Open Quantum Safe (OQS) project, which aims to support the development and prototyping of PQC.
*   **Release Frequency:** The library sees regular updates, typically aligning with releases of the underlying `liboqs` C library.
    *   Example releases noted:
        *   Version 0.8.0 (July 2023): Introduced `pyproject.toml` and automatic `liboqs` installation.
        *   Version 0.9.0 (October 2023): Standardized Python function naming conventions (snake_case).
        *   Version 0.10.0 (April 2024): Updated to `liboqs` 0.10.0, removed NIST PRNG.
        *   Version 0.12.0 (January 16, 2025): Aligned with `liboqs` 0.13.0.
*   **CI/CD:** Migrated to GitHub Actions for continuous integration and testing, indicating modern development practices.
*   **Source:** Information primarily derived from the library's `CHANGES.md` file and OQS project announcements.

## 2. Reported Vulnerabilities and Security

*   **Security Audits:** The underlying `liboqs` C library, which `oqs-python` wraps, underwent a security assessment by Trail of Bits. The report was published in April 2025. Users should consult this report for detailed findings.
*   **CVEs:** No specific CVEs for `oqs-python` itself were highlighted in the provided search results. Vulnerabilities in `liboqs` would directly impact `oqs-python`.
*   **Security Focus:** The OQS project actively tracks and addresses security issues in its libraries. The removal of the NIST PRNG in v0.10.0 was due to API changes in `liboqs`, likely to improve security or rely on system PRNGs.

## 3. Community Support

*   **Parent Project:** Strong backing from the Open Quantum Safe (OQS) project, which is a collaborative effort involving researchers and developers.
*   **Ecosystem Integration:** `liboqs` (and by extension, `oqs-python`) is integrated or experimented with in larger projects like OpenSSL (via OQS provider), BoringSSL, and OpenSSH. This indicates a level of community adoption and testing.
*   **GitHub Activity:** The project is hosted on GitHub, allowing for issue tracking and community contributions. Specific metrics like the number of active contributors or response times for issues would require direct repository analysis.

## 4. Ease of Use for Target Algorithms

`oqs-python` provides access to PQC algorithms standardized or under consideration by NIST.

*   **Supported Algorithms:**
    *   **Kyber (ML-KEM):** Fully supported. Accessible via the `KeyEncapsulation` class.
    *   **Dilithium (ML-DSA):** Fully supported. Accessible via the `Signature` class.
    *   **Falcon:** Fully supported. Accessible via the `Signature` class.
    *   **SPHINCS+ (SLH-DSA):** Fully supported. Accessible via the `Signature` class.
    *   The library provides methods like `KeyEncapsulation.get_enabled_kem_mechanisms()` and `Signature.get_enabled_sig_mechanisms()` to list available algorithm variants.
*   **API:**
    *   The API aims to be straightforward for common operations like key generation, encapsulation/decapsulation, signing, and verification.
    *   Pythonic naming conventions (snake_case for functions and methods) were adopted in version 0.9.0, improving consistency for Python developers.
    *   Example Usage (Kyber KEM):
        ```python
        import oqs

        # List available KEMs
        # print(oqs.KeyEncapsulation.get_enabled_kem_mechanisms())

        kem_alg = "Kyber768" # Or other variants like Kyber512, Kyber1024
        with oqs.KeyEncapsulation(kem_alg) as kem:
            public_key = kem.generate_keypair()
            ciphertext, shared_secret_sender = kem.encap_secret(public_key)
            shared_secret_recipient = kem.decap_secret(ciphertext)
            # assert shared_secret_sender == shared_secret_recipient
        ```
    *   Example Usage (Dilithium Signature):
        ```python
        import oqs

        sig_alg = "Dilithium3" # Or other variants
        with oqs.Signature(sig_alg) as signer:
            public_key_sig = signer.generate_keypair()
            message = b"This is the message to sign."
            signature = signer.sign(message)
            is_valid = signer.verify(message, signature, public_key_sig)
            # assert is_valid
        ```
*   **API Stability:** While generally stable, users should check `CHANGES.md` for any breaking changes between versions, especially when upgrading `liboqs` and `oqs-python` major versions. The core OQS C API itself evolves as PQC standards are finalized.

## 5. Installation

*   **Simplified Installation:** Since version 0.8.0, `oqs-python` uses `pyproject.toml`.
*   **Automatic `liboqs` Handling:** The Python package attempts to automatically download and build `liboqs` if a system-wide installation is not detected. This significantly simplifies setup for users.
*   **PyPI:** Available on PyPI, installable via `pip install oqs`.

## 6. Documentation Quality

*   **Release Notes:** The `CHANGES.md` file in the repository provides a good overview of changes per version.
*   **OQS Project Documentation:** The main Open Quantum Safe project website and `liboqs` GitHub repository are primary sources for more detailed documentation on algorithms, API specifics, and build instructions.
*   **Examples:** The OQS project often includes example code in its repositories.

## Summary

`oqs-python` is a actively maintained and evolving library crucial for Python developers working with PQC. It offers:
*   Support for key NIST-selected algorithms (Kyber, Dilithium, Falcon, SPHINCS+).
*   Simplified installation and dependency management.
*   An API that is becoming more Pythonic and user-friendly.
*   Backed by the broader OQS community and undergoing security assessments (via `liboqs`).

Potential challenges include the evolving nature of PQC standards which can lead to API changes in underlying libraries, and the inherent performance overhead of Python wrappers compared to direct C implementations for highly sensitive applications. For Fava, `oqs-python` appears to be the most viable option for accessing PQC primitives in the Python backend.