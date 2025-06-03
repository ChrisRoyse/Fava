# Primary Findings: PQC Certificates and Browser Support - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Status of PQC certificate issuance by CAs, PQC-signed root and intermediate CAs, X.509 formats for PQC public keys and signatures. Major web browser support (Chrome, Firefox, Safari, Edge) for PQC KEMs in TLS, whether enabled by default, and frontend code impact.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on the status of Post-Quantum Cryptography (PQC) certificate issuance, PQC in the X.509 standard, and PQC KEM support in major web browsers.

## 1. PQC Certificate Authority (CA) Issuance

*   **Current Status:** As of mid-2025, Certificate Authorities (CAs) are **not yet issuing PQC-signed certificates** for general public use [5].
*   **Key Hurdles:**
    *   **HSM Upgrades:** CAs rely on Hardware Security Modules (HSMs) for private key protection. These HSMs require firmware and potentially hardware upgrades to support PQC algorithms (like CRYSTALS-Dilithium for signatures and SPHINCS+). These upgrades then need to undergo security audits [4, 5].
    *   **CA/Browser Forum Approval:** New PQC algorithms must be approved by the CA/Browser Forum for inclusion in publicly trusted certificates [5].
    *   **Dependency on Finalized Standards:** While NIST has finalized initial PQC standards (FIPS 203 for ML-KEM/Kyber, FIPS 204 for ML-DSA/Dilithium, FIPS 205 for SLH-DSA/SPHINCS+) as of March 2025 [1, 2], the ecosystem (CAs, software vendors) needs time to integrate and test these.
*   **Estimated Timeline:** The issuance of the first publicly trusted PQC certificates is considered unlikely before **2026** [5].

## 2. PQC-Signed Root and Intermediate CAs

*   **Current Status:** There are no publicly trusted PQC-signed root or intermediate CAs deployed yet.
*   **Hardware Readiness:** The availability of cryptographic hardware roots of trust (e.g., HSMs in CAs) capable of handling PQC operations is anticipated later in **2025** [4].
*   **Migration Strategy:** Early PQC CA hierarchies are expected to use a **hybrid approach**, where certificates might be co-signed with both a classical (RSA/ECC) and a PQC signature, or PQC public keys might be included alongside classical keys to ensure backward compatibility during the transition.
*   **Challenges:** Updating the entire trust chain from root CAs down to end-entity certificates is a multi-year process requiring coordination among CAs, browser vendors, and operating system providers.

## 3. X.509 Formats for PQC

While the search results did not point to specific finalized RFCs detailing X.509 extensions for all PQC algorithms, integration will necessitate adaptations to the X.509 standard:

*   **New Algorithm Identifiers (OIDs):** Unique OIDs will be required to identify PQC signature algorithms (e.g., CRYSTALS-Dilithium, Falcon, SPHINCS+) and PQC public key types (e.g., for CRYSTALS-Kyber) within certificate fields like `subjectPublicKeyInfo` and `signatureAlgorithm`.
*   **Signature Encoding:** Specific encoding rules for PQC signatures (which can be larger and structured differently than RSA/ECC signatures) within the `signatureValue` field. For example, SPHINCS+ has particular implementation details that would need to be reflected.
*   **Key Parameters:** Some PQC algorithms have different security parameter sets (e.g., Dilithium-II, Dilithium-III, Dilithium-V). The X.509 structure must accommodate these.
*   **Larger Data Sizes:** The larger sizes of PQC public keys and signatures may strain existing X.509 field size limits or parsing logic in some implementations.

## 4. Browser Support for PQC KEMs in TLS

Browser vendors are actively experimenting with PQC, primarily focusing on hybrid KEMs in TLS 1.3 to ensure security against future quantum threats while maintaining compatibility.

| Browser       | PQC KEM Support Status (as of mid-2025)      | Default Enabled? | Notes                                                                 |
| :------------ | :------------------------------------------- | :--------------- | :-------------------------------------------------------------------- |
| **Chrome**    | Experimental support for hybrid KEMs (e.g., X25519Kyber768) [5]. | No               | Typically available via feature flags (e.g., `chrome://flags`).         |
| **Firefox**   | Testing in Nightly/developer builds.         | No               | Usually requires manual configuration in `about:config`.                |
| **Safari**    | No public PQC KEM implementation announced.  | N/A              | Dependent on WebKit engine updates and Apple's PQC strategy.          |
| **Edge**      | Chromium-based; likely to follow Chrome's experimental support for hybrid KEMs. | No               | Support status mirrors Chrome's development for PQC KEMs.             |

*   **General Trend:** Major browser ecosystems are anticipated to have some form of PQC TLS support (likely hybrid KEMs) by late 2024 or early 2025, but widespread default enablement is further out [5].

## 5. Frontend Code Impact

For most web applications, the direct impact of PQC TLS on frontend code is expected to be **minimal** [5]. The TLS handshake and PQC operations are handled by the browser's underlying TLS stack or the operating system's cryptographic libraries.

However, frontend developers might encounter considerations if:
*   The application uses **client certificate authentication**, and PQC client certificates become a requirement.
*   The application employs a **custom TLS stack** (e.g., in WebAssembly or via custom JavaScript libraries), bypassing the browser's native capabilities.
*   The application needs to **parse or verify certificate chains** that include mixed classical/PQC signatures or PQC-specific extensions, once PQC certificates are issued.

## 6. Broader Ecosystem Readiness

*   Major TLS libraries like OpenSSL and BoringSSL are incorporating support for PQC, including configurations for multiple (hybrid) certificates [5].
*   Cloud providers (e.g., AWS, Azure) are expected to offer PQC-enabled load balancers and Content Delivery Networks (CDNs) by late 2025, which will facilitate PQC adoption for web services [3, 5].

## 7. Identified Knowledge Gaps from this Search

*   **Specific X.509 Drafts/RFCs:** Pointers to active IETF drafts or RFCs detailing the X.509 structures (OIDs, encoding rules) for the NIST-standardized PQC algorithms.
*   **Browser PQC Roadmaps:** More detailed public roadmaps from Mozilla (Firefox) and Apple (Safari/WebKit) regarding their PQC KEM integration plans and timelines.
*   **CA PQC Pilot Programs:** Information on any pilot programs or test certificates being offered by CAs for PQC.

*(This document will be updated or appended as more information is gathered.)*