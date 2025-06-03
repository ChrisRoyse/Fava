# Primary Findings: GnuPG (GPG) and Beancount PQC Support - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Current status of PQC (Post-Quantum Cryptography) support in GnuPG (GPG): PQC algorithms supported (KEMs, signatures), stable GPG releases with PQC, command-line interface or API for PQC in GPG. Interaction with Beancount's encrypted file loading.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings regarding Post-Quantum Cryptography (PQC) support in GnuPG (GPG) and its implications for Beancount's encrypted file handling, which is relevant to Fava's "Data at Rest" PQC strategy.

## 1. GnuPG (GPG) PQC Support Status

*   **No Native PQC in Stable Releases:** As of early 2025, stable releases of GnuPG (e.g., 2.x series) do not include native support for standardized PQC algorithms like CRYSTALS-Kyber or CRYSTALS-Dilithium [2, 5]. The official GnuPG website does not prominently feature PQC integration in its current stable offerings [2].
*   **Experimental/Infrastructure Work:**
    *   There is evidence of ongoing infrastructure work within the GnuPG project to accommodate PQC key types. An email from January 2025 discussed "infrastructure support for GnuPG post-quantum keys" [1], suggesting foundational changes are being considered or implemented in development branches. However, specific algorithms or timelines for integration into stable releases were not detailed in this communication.
    *   The Kicksecure wiki mentions that GnuPG's full PQC integration might be pending broader ecosystem developments (e.g., related to Tor's PQC migration, which itself is waiting on other factors) and that there are ongoing debates regarding NIST's algorithm choices (e.g., Kyber vs. NTRU Prime) [5].
*   **Experimental Forks/Alternatives:**
    *   The search mentioned a "GnuPG-like Unix program for encryption and signing that only uses quantum-resistant algorithms: McEliece" using compact QC-MDPC variants [5]. This suggests that PQC capabilities might be found in experimental forks or alternative tools rather than in the mainstream GnuPG releases.
*   **Key Challenges for GPG PQC Integration (as per search context [5]):**
    *   Debates surrounding NIST PQC algorithm choices.
    *   Performance concerns of some PQC schemes on resource-constrained devices.
    *   Lack of implemented hybrid modes (classical + PQC) in GPG.

## 2. Implications for Beancount Encrypted File Loading

Beancount traditionally relies on GPG for encrypting and decrypting Beancount files. Fava, in turn, uses Beancount's loading mechanism.

*   **Dependency on GPG:** Beancount's ability to handle PQC-encrypted files is directly tied to GPG's PQC capabilities. If the version of GPG used by Beancount does not support PQC, then Beancount (and by extension, Fava) will not be able to process files encrypted with PQC algorithms through the standard GPG pathway.
*   **Current Workflow:** The typical Beancount decryption workflow (e.g., `bean-extract myconfig.py encrypted.bean.gpg`) relies on the system's GPG installation.
*   **Requirements for Beancount PQC Support (Hypothetical, based on GPG PQC availability):**
    1.  A version of GPG compiled with support for the desired PQC algorithms.
    2.  A mechanism to handle PQC keys, potentially including hybrid certificate structures (combining classical and PQC keys) if a hybrid approach is adopted by GPG.
    3.  Possible modifications to Beancount's file decryption routines if GPG's PQC interface or key handling differs significantly or if larger key/metadata sizes need accommodation.
*   **Development Status:** The search results suggest no active development is currently underway for PQC integration directly within Beancount's GPG-dependent workflows. Both projects seem to be awaiting more finalized NIST standards and stable PQC implementations in GPG itself [3, 4 – general PQC migration context].

## 3. Fava's Options for PQC Data at Rest

Given the current status:

*   **Monitoring GPG:** Fava's primary path for PQC-encrypted Beancount files via GPG is to monitor the GnuPG project for official PQC support in stable releases.
*   **Alternative Decryption in Fava:** As outlined in [`docs/Plan.MD`](docs/Plan.MD), Fava might need to consider its own decryption abstraction layer. This layer could potentially:
    *   Interface with experimental/PQC-enabled GPG forks if users install them.
    *   Integrate Python PQC libraries directly for specific PQC KEMs/schemes, bypassing GPG for PQC-encrypted files (a more complex undertaking requiring Fava to manage PQC key aspects).
*   **User Guidance:** Users needing immediate PQC for their Beancount files would likely have to rely on custom solutions involving experimental GPG versions or other PQC tools, and then potentially provide the decrypted content to Fava, or Fava would need a way to invoke these custom tools.

## 4. Identified Knowledge Gaps from this Search

*   **Specific GPG PQC Roadmap:** Detailed official roadmap or timeline from the GnuPG project regarding which PQC algorithms (KEMs, signatures from NIST list) they plan to integrate and when they might appear in stable releases.
*   **GPG PQC CLI/API:** If any experimental PQC support exists in GPG development branches, the specific command-line options or GPGME (GnuPG Made Easy library) API extensions for using PQC are not yet clear.
*   **Beancount Community Stance:** Specific discussions or plans from the Beancount development community regarding PQC.

*(This document will be updated or appended as more information is gathered.)*