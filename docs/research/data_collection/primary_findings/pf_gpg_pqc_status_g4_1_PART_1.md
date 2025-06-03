# Primary Findings: GnuPG (GPG) PQC Support Status and Alternatives (Addressing Gap G4.1)

**Date Compiled:** 2025-06-02
**Research Focus:** G4.1: Current status and realistic roadmap for GPG PQC support. Viable PQC-enabled GPG alternatives or wrappers if official support is distant.
**Source:** AI Search (Perplexity MCP) - Query: "Current status and realistic roadmap for GnuPG (GPG) support of Post-Quantum Cryptography (PQC) algorithms, especially for KEMs like Kyber and signatures like Dilithium. Are there official statements, development branches, or target versions? If official GPG PQC support is distant, what are viable PQC-enabled GPG alternatives or wrappers that could be used for user-side data-at-rest encryption with PQC? Cite GnuPG project communications, relevant mailing lists, or PQC community discussions."

This document summarizes findings on the current status of Post-Quantum Cryptography (PQC) support in GnuPG (GPG) and potential alternatives for user-side data-at-rest encryption.

## Current Status of PQC Support in GnuPG (GPG)

Based on the provided search results and general knowledge up to early 2025:

*   **No Native Official PQC Support in Stable GnuPG:** As of the latest stable GnuPG releases (e.g., 2.4.x), there is no official, native support for the NIST-selected PQC algorithms like Kyber (ML-KEM) or Dilithium (ML-DSA).
*   **Development and Roadmap:**
    *   The GnuPG project is aware of the PQC transition. However, a concrete, publicly announced roadmap with specific target versions or timelines for integrating NIST PQC standards (FIPS 203, 204, 205) into GnuPG is not readily available in mainstream project communications.
    *   Integration depends on the underlying cryptographic library used by GnuPG, primarily Libgcrypt. Libgcrypt would first need to incorporate robust and audited implementations of these PQC algorithms.
    *   Discussions on GnuPG development mailing lists (e.g., `gnupg-devel`) would be the primary source for tracking progress, but these were not included in the direct search results.
*   **Challenges:**
    *   Integrating PQC into the OpenPGP standard (RFC 4880 and its successors) requires defining new algorithm identifiers, key formats, and signature packet formats. This is a significant standards effort that typically involves IETF discussion and consensus.
    *   Ensuring backward compatibility and a smooth transition for existing GPG users and infrastructure is a major consideration.

## Realistic Roadmap Expectations

*   Given the timeline of NIST finalizing the initial PQC standards in August 2024, and the typical cycle for cryptographic library and application adoption:
    *   Experimental PQC support in GnuPG development branches might appear in the 2025-2027 timeframe, assuming Libgcrypt development proceeds accordingly.
    *   Stable, production-ready GPG versions with robust PQC support are likely further out, potentially 3-5+ years, depending on standardization maturity, implementation efforts, and security audits.
*   Hybrid schemes (combining classical algorithms like RSA/ECC with PQC algorithms) are a likely interim step for GPG, similar to approaches seen in TLS. This would allow users to start generating and using PQC keys while maintaining compatibility.

## Viable PQC-Enabled GPG Alternatives or Wrappers

If official GPG PQC support is distant, users needing PQC for data-at-rest have limited direct "GPG alternatives" that offer the same OpenPGP-compliant ecosystem. However, several strategies or tools can be considered as wrappers or complementary solutions:

1.  **Using PQC Libraries Alongside GPG (Manual Hybrid Approach):**
    *   **Concept:** Encrypt data with a strong symmetric cipher (e.g., AES-256-GCM). The symmetric key is then protected using a hybrid KEM approach.
        *   Generate a classical KEM ciphertext for the symmetric key using the recipient's existing GPG public key (if it's a classical key like RSA or ECC).
        *   Generate a PQC KEM ciphertext for the *same* symmetric key using the recipient's PQC public key (obtained via other means, e.g., using `oqs-python` with Kyber).
        *   Store/transmit both KEM ciphertexts. The recipient decrypts using either their classical GPG private key or their PQC private key to recover the symmetric key.
    *   **Tools:**
        *   GPG for the classical KEM part.
        *   Python scripts using `oqs-python` for the PQC KEM part (Kyber).
    *   **Pros:** Provides quantum resistance for new encryptions if the PQC part is used.
    *   **Cons:** Complex key management (users need PQC keys + classical GPG keys), not transparent, requires custom tooling/scripts, not OpenPGP standard compliant for the PQC part.

2.  **External PQC Encryption Tools + GPG for Classical Operations:**
    *   **Concept:** Use standalone tools based on libraries like `liboqs` (or `oqs-python` scripts) to perform PQC encryption/decryption or signing/verification for specific files or data. GPG can still be used for communication with parties who have not transitioned to PQC.
    *   **Example:** A user could encrypt a file using a script that implements Kyber for key encapsulation and AES for bulk encryption, then separately sign the PQC-encrypted file's hash using their existing GPG ECDSA key if needed for non-repudiation with legacy systems.
    *   **Pros:** Allows use of PQC immediately for sensitive data.
    *   **Cons:** Siloed from the GPG/OpenPGP ecosystem, manual process, tool availability and usability can be an issue for non-technical users.

3.  **Monitoring PQC-Aware Forks or Patches for GPG/Libgcrypt:**
    *   The Open Quantum Safe (OQS) project sometimes creates PQC-enabled forks or provides patches for popular cryptographic libraries (e.g., OpenSSL). It's conceivable that experimental PQC patches for Libgcrypt or even GPG might emerge from research communities.
    *   **Pros:** Could offer a more integrated experience if available.
    *   **Cons:** These would be experimental, potentially unstable, and not officially supported by the GnuPG project, carrying security risks.

4.  **Certificate-Based Hybrid Approaches (Future Potential):**
    *   As X.509 standards evolve to include PQC OIDs and hybrid certificate structures (as discussed in IETF), future versions of GPG that support these X.509 features (e.g., for S/MIME) might naturally gain some PQC capabilities through certificate processing, even if full OpenPGP PQC integration lags. This is speculative for GPG's core OpenPGP functionality.

## Conclusion for Fava's Context:

*   Fava users relying on GPG for Beancount file encryption currently do not have an official PQC-GPG solution.
*   The most realistic approach for Fava in the short to medium term, if PQC for data-at-rest is critical, is to:
    1.  **Educate users** about the current GPG limitations regarding PQC.
    2.  **Potentially guide users** on manual hybrid methods using external tools/scripts (like those based on `oqs-python`) if they need to protect highly sensitive new data with PQC KEMs, while still using classical GPG for broader compatibility. This would be an advanced user feature.
    3.  **Closely monitor** GnuPG and Libgcrypt project developments for official PQC support.
    4.  Design Fava's internal cryptographic agility layer to be able to accommodate future PQC decryption methods, whether they come from an updated GPG or a Fava-specific implementation.

Directly integrating PQC decryption for GPG-like formats *within Fava itself* without GPG/Libgcrypt support would mean Fava reimplementing significant parts of OpenPGP PQC handling, which is a very large and complex undertaking.

This information addresses knowledge gap G4.1 regarding the status of GPG PQC support and potential alternatives.