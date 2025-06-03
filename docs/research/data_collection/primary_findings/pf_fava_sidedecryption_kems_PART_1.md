# Primary Findings: Fava-Side PQC Decryption, KEMs, and Key Management - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Challenges of PQC key management for application-side file encryption (non-GPG), secure user key provision for PQC, metadata for PQC encrypted files. Suitability and performance of NIST PQC KEMs like CRYSTALS-Kyber for hybrid file encryption (PQC KEM + AES).", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings related to implementing PQC decryption directly within an application like Fava (i.e., "Fava-side"), focusing on key management challenges, user key provision, metadata considerations, and the suitability of KEMs like CRYSTALS-Kyber for hybrid file encryption.

## 1. Challenges for Application-Side PQC Key Management (Non-GPG)

Implementing PQC file encryption/decryption directly within Fava, without relying on an external tool like GPG, presents several key management challenges:

*   **Expanded Key Sizes & Storage:** PQC algorithms generally have larger public and private keys compared to classical algorithms. For example, CRYSTALS-Kyber public keys can be 2-3KB or more [2, 5]. Managing these larger keys within the application or for users can lead to:
    *   Increased storage requirements if keys are stored by the application or user profiles.
    *   Potential performance degradation if large keys need to be frequently loaded or processed.
*   **Technical Complexity & Lack of Knowledge:** Integrating and managing PQC primitives directly requires specialized cryptographic knowledge, which might be a barrier [1].
*   **Performance Issues:** Some PQC algorithms, including lattice-based ones like Kyber, can have higher computational requirements for key generation and cryptographic operations compared to classical counterparts, especially on resource-constrained environments or without hardware acceleration [2, 5]. This impacts key generation speed and overall encryption/decryption performance.
*   **Key Provisioning and Rotation:**
    *   Securely distributing and updating larger PQC keys to users or different parts of an application is more complex [2, 4].
    *   Key rotation cycles might be more computationally intensive [5].

## 2. Secure User Key Provision for PQC

If Fava were to handle PQC keys directly for file encryption, secure provision and handling of user keys would be critical:

*   **User Experience:** Users would need to manage potentially larger and more complex PQC key materials.
*   **Methods for Key Provisioning (General PQC Context):**
    *   **Quantum-Safe HSMs:** Utilizing Hardware Security Modules that support PQC for key generation and storage [4]. This is likely overkill for a typical Fava user but relevant in broader PQC deployment.
    *   **Modernized Key Ceremonies:** Multi-Party Computation (MPC) protocols adapted for PQC key generation, though these can have higher bandwidth requirements [2]. Again, likely not directly applicable to individual Fava users but indicates complexity.
    *   **PQC-Enabled TLS:** Using TLS 1.3 with PQC KEMs for secure transmission of keys or keying material if Fava had a client-server component for key management [5].
    *   **Passphrase-Based Key Derivation:** If keys are derived from user passphrases, the Key Derivation Functions (KDFs) must be robust, and the entropy of passphrases becomes even more critical given the new algorithms. The interaction between PQC KEMs and passphrase-derived keys needs careful design.

## 3. Metadata for PQC Encrypted Files

Files encrypted with PQC (especially in hybrid schemes) will likely require more extensive or differently structured metadata:

*   **Algorithm Identification:** Clear identifiers for the specific PQC KEM, signature algorithm (if used for integrity), and symmetric cipher (in hybrid modes) will be needed. These might be longer or different from traditional ASN.1 OIDs [Perplexity Analysis].
*   **Key Wrapping Information:** For hybrid schemes where a PQC KEM wraps a symmetric key, metadata related to the KEM ciphertext (the encapsulated key) must be stored alongside the symmetrically encrypted data [4, 5].
*   **Parameter Storage:** Some PQC schemes might have different parameter sets (e.g., security levels of Kyber like Kyber-512, Kyber-768, Kyber-1024). The chosen parameters might need to be stored or inferred.
*   **Impact:** This expanded metadata can affect file format design, compatibility, and parsing logic.

## 4. Suitability and Performance of CRYSTALS-Kyber for Hybrid File Encryption

CRYSTALS-Kyber (standardized as ML-KEM in FIPS 203) is a prominent candidate for the KEM part of a hybrid file encryption scheme (e.g., Kyber to establish a shared secret, which is then used as an AES key for bulk encryption).

*   **Advantages:**
    *   **Standardization:** Being a NIST standard provides a strong assurance of security analysis and community review [3].
    *   **Relatively Small Ciphertext Sizes:** Compared to some other PQC KEM candidates, Kyber's encapsulated key ciphertexts are relatively compact (e.g., around 1.5KB for ML-KEM-768) [5].
*   **Limitations/Performance Considerations:**
    *   **Key Generation Speed:** Kyber key generation can be slower than classical algorithms like RSA on similar platforms (e.g., cited as ~2.4x slower on x86 CPUs) [5].
    *   **Computational Requirements:** Lattice-based cryptography involves operations like polynomial multiplication which can be resource-intensive without dedicated hardware acceleration [5].
    *   **Hybrid Overhead:** Even in a hybrid scheme (Kyber + AES), the PQC KEM operations (encapsulation/decapsulation) add latency compared to a purely symmetric AES encryption scheme where the key is already known or derived via classical methods. The search mentioned an 18-22% latency overhead for Kyber+AES vs. pure AES in file encryption benchmarks [4].

*   **Example Hybrid Workflow (Conceptual, based on search result's Python snippet [User-Interpreted]):**
    1.  Generate a Kyber key pair (public_key, private_key).
    2.  When encrypting: Use the recipient's Kyber public_key to `encapsulate()`. This yields a `ciphertext` (the encapsulated shared secret) and the `shared_secret` itself.
    3.  Use the derived `shared_secret` as an AES key (e.g., AES-GCM) to encrypt the actual file data.
    4.  Store the KEM `ciphertext` (encapsulated key) along with the AES-encrypted data.
    5.  When decrypting: Use the recipient's Kyber private_key and the stored KEM `ciphertext` to `decapsulate()` and recover the `shared_secret` (AES key).
    6.  Use the recovered AES key to decrypt the file data.
    This workflow requires careful management of the KEM ciphertext and AES parameters within the encrypted file's structure or metadata [3, 4].

## 5. Identified Knowledge Gaps from this Search

*   **Specific PQC Key Management Libraries for Python:** While general challenges are noted, specific, mature Python libraries designed for PQC key management (beyond raw PQC primitive libraries) were not highlighted.
*   **Standardized Metadata Formats for Hybrid PQC Files:** Are there emerging best practices or draft standards for how to structure metadata in files using hybrid PQC encryption (e.g., PQC KEM + AES)?
*   **Usability of PQC Keys for End-Users:** More research into the practicalities of how end-users would manage raw PQC key files or passphrases if Fava were to implement direct PQC handling.
*   **Performance Benchmarks on Diverse Hardware:** While some general performance notes were provided, benchmarks across a wider range of typical user hardware (especially for key generation and KEM operations) would be valuable.

*(This document will be updated or appended as more information is gathered.)*