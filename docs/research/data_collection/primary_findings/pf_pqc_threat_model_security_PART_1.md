# Primary Findings: PQC Threat Model & Security Considerations - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Post-Quantum Cryptography threat model beyond Shor's algorithm, side-channel vulnerabilities of NIST PQC candidates (Kyber, Dilithium, Falcon, SPHINCS+), implications of larger PQC key and signature sizes, and effects of PQC on existing security protocols and practices.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on the PQC threat model, security considerations for NIST PQC candidates, and the impact of PQC adoption.

## 1. Threat Model Beyond Shor's Algorithm

While Shor's algorithm is the primary quantum threat to classical public-key cryptography (RSA, ECC) [1, 4], another significant quantum algorithm impacts symmetric cryptography:

*   **Grover's Algorithm:** This quantum search algorithm can speed up brute-force key searches against symmetric ciphers (like AES). It effectively halves the security strength of such algorithms. For instance, AES-128's effective quantum security is reduced to 64-bit, necessitating a move to AES-256 (which offers 128-bit quantum security) for robust protection [5]. This has implications for computational overhead and systems with lightweight cryptography requirements (e.g., IoT) [5].

## 2. Side-Channel Vulnerabilities in NIST PQC Candidates

The introduction of new PQC algorithms brings new considerations for implementation security, including side-channel attacks. The Perplexity search result provided the following insights on NIST candidates:

*   **CRYSTALS-Kyber (KEM):** As a lattice-based scheme, Kyber implementations may be susceptible to timing attacks or power analysis during polynomial multiplication operations if not carefully hardened.
*   **CRYSTALS-Dilithium & Falcon (Digital Signatures):** These lattice-based signature schemes could be vulnerable to fault injection attacks that target the signature generation process. Falcon's use of floating-point arithmetic introduces additional implementation complexity, potentially increasing side-channel risks.
*   **SPHINCS+ (Stateless Hash-Based Signatures):** While generally robust against quantum attacks due to its hash-based nature, implementations might be vulnerable to timing attacks related to hash tree traversal or if randomized hashing steps are not constant-time.

The search output emphasizes the need for constant-time implementations and potential hardware-level mitigations for these PQC algorithms when deployed.

## 3. Implications of Larger Key and Signature Sizes

PQC algorithms generally feature larger key and signature sizes compared to their classical counterparts, leading to several practical implications [3, 5]:

*   **Increased Data Overhead:**
    *   **Kyber:** Public keys are cited as ranging from 800–1,500 bytes (compared to RSA's typical 256 bytes for a 2048-bit key, or ~65 bytes for ECC P-256 keys). This can increase TLS handshake sizes by a factor of 2 to 4.
    *   **Dilithium:** Signatures can be 2,420–4,595 bytes (compared to ECDSA P-256's ~64–72 bytes). This impacts applications like blockchain transactions and code signing.
    *   **SPHINCS+:** Signatures are noted as exceeding 8,000 bytes, potentially making it less suitable for bandwidth-constrained environments like sensor networks.
*   **System Impact:**
    *   **Legacy Systems:** May struggle with increased data sizes.
    *   **Network Protocols:** May require adjustments (e.g., TCP Maximum Segment Size - MSS).
    *   **Storage:** Increased storage costs, particularly for Certificate Authorities (CAs) managing many PQC certificates.

## 4. Effects on Existing Security Protocols and Practices

The transition to PQC will significantly affect various security protocols and practices:

*   **TLS/SSL:** Hybrid PQC solutions (e.g., classical ECDHE combined with a PQC KEM like Kyber) are seen as interim steps. Full PQC migration will necessitate updates to cipher suites and potentially protocol standards (e.g., RFC 8446 for TLS 1.3) [3].
*   **Public Key Infrastructure (PKI):** Certificate chains incorporating PQC signatures might exceed current X.509 size limits, potentially requiring changes in CA/Browser Forum policies and certificate parsing logic.
*   **Hardware Security Modules (HSMs):** Existing HSMs may lack the computational capabilities or specific instruction sets for efficient PQC operations, potentially requiring firmware updates or hardware replacement.
*   **Cryptographic Agility:** NIST's call for "crypto-agile" systems [3] implies that organizations need to adopt modular cryptographic architectures. This can complicate compliance with frameworks like FIPS 140-3, which traditionally favor fixed, validated modules.
*   **Symmetric Key Lengths:** As noted with Grover's algorithm, the standard for symmetric key lengths effectively increases (e.g., AES-256 becomes the baseline for 128-bit equivalent security) [5].

The overall message is that PQC adoption requires a holistic approach, including auditing existing crypto-dependencies, prioritizing high-risk systems, and likely employing hybrid strategies during the transition period [3, 5].

## 5. Identified Knowledge Gaps from this Search

*   **Detailed Side-Channel Attack Vectors & Countermeasures:** While general concerns were raised, specific, documented side-channel attacks against mature implementations of the NIST PQC finalists and standardized countermeasures were not detailed in this search.
*   **Quantitative Performance Impact of Larger Sizes:** While "larger" is stated, precise performance figures (e.g., latency increase in milliseconds for TLS handshakes with specific hybrid KEMs on typical hardware) were not provided.
*   **Status of Protocol Updates for PQC:** Specific draft RFCs or working group progress on updating protocols like X.509 or TLS for PQC (beyond general hybrid concepts) were not detailed.

*(This document will be updated or appended as more information is gathered.)*