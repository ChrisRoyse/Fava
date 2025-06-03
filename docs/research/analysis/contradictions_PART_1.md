# Identified Contradictions or Ambiguities in PQC Research - Part 1

**Date Compiled:** 2025-06-02

This document notes any apparent contradictions, ambiguities, or areas where information from different sources or contexts might require further clarification during the Post-Quantum Cryptography (PQC) integration research for Fava.

## 1. Timelines for PQC Ecosystem Readiness

*   **Observation:** While NIST has finalized initial PQC algorithm standards (ML-KEM, ML-DSA, SLH-DSA in 2024; HQC selected in 2025), the readiness of the broader ecosystem (CAs, GPG, browsers, standard libraries) varies, and timelines can sometimes appear optimistic or differ slightly between sources.
*   **Specifics:**
    *   One search result mentioned "major ecosystems might have TLS support by early 2025" ([`pf_pqc_certs_browsers_PART_1.md`](../data_collection/primary_findings/pf_pqc_certs_browsers_PART_1.md), citing Cloudflare [5]), while also stating CA issuance of PQC certs is unlikely before 2026. This suggests a period where PQC KEMs might be usable in TLS but without full PQC certificate chain validation.
    *   NCSC (UK) expected hardware roots of trust for PQC later in 2025 ([`pf_pqc_certs_browsers_PART_1.md`](../data_collection/primary_findings/pf_pqc_certs_browsers_PART_1.md)), which is a prerequisite for PQC-signed CAs.
*   **Nature of "Contradiction":** Less a direct contradiction and more an ambiguity in the pace of different interdependent components maturing. The "TLS support" might refer to KEMs, while "PQC certificates" refer to the full PKI.
*   **Implication for Fava:** Reinforces the need for a flexible, phased approach and continuous monitoring rather than betting on a single, fixed timeline for all PQC components to be ready.

## 2. GPG PQC Support Status

*   **Observation:** Information regarding GPG's PQC support is somewhat mixed, highlighting a distinction between mainstream stable releases and experimental efforts.
*   **Specifics:**
    *   Mainline GPG stable releases do not yet have native PQC support ([`pf_gpg_beancount_pqc_PART_1.md`](../data_collection/primary_findings/pf_gpg_beancount_pqc_PART_1.md)).
    *   There's mention of "infrastructure support for GnuPG post-quantum keys" in development (Jan 2025 email) ([`pf_gpg_beancount_pqc_PART_1.md`](../data_collection/primary_findings/pf_gpg_beancount_pqc_PART_1.md)), but the scope and timeline for user-facing features are unclear.
    *   The Kicksecure wiki mentioned a "GnuPG-like program" using McEliece and that Tor's PQC migration (which might influence GPG) is stalled, and also noted debates about NIST algorithm choices impacting GPG [Source: pf_gpg_beancount_pqc_PART_1.md, citing Kicksecure [5]]. This suggests potential fragmentation or alternative paths rather than a single, clear GPG PQC roadmap.
*   **Nature of "Contradiction":** Ambiguity about the official GPG project's PQC integration path and timeline versus what might be available in forks or related experimental tools.
*   **Implication for Fava:** Fava cannot assume imminent PQC support in the GPG versions typically used by its users. The Fava-side decryption abstraction becomes more critical if PQC for file encryption is a priority.

## 3. Performance Figures for PQC

*   **Observation:** While there's a general consensus that PQC algorithms have larger keys/signatures and can be slower, specific performance benchmarks can vary based on the source, the specific PQC algorithm variant (e.g., Kyber-512 vs. Kyber-1024), the hardware platform, and the implementation library.
*   **Specifics:**
    *   One search mentioned Kyber key generation being "~10x slower than RSA on low-power devices" ([`pf_fava_sidedecryption_kems_PART_1.md`](../data_collection/primary_findings/pf_fava_sidedecryption_kems_PART_1.md), citing [5]), while another cited it as "2.4x slower key generation compared to RSA-2048 on x86 CPUs" ([`pf_fava_sidedecryption_kems_PART_1.md`](../data_collection/primary_findings/pf_fava_sidedecryption_kems_PART_1.md), citing [5] from a different context or interpretation). These are not directly contradictory if platforms differ but highlight variability.
    *   TLS handshake latency increases were cited as "15-20%" ([`pf_tls_proxies_python_pqc_PART_1.md`](../data_collection/primary_findings/pf_tls_proxies_python_pqc_PART_1.md), citing [4]) and "18-25%" ([`pf_tls_proxies_python_pqc_PART_1.md`](../data_collection/primary_findings/pf_tls_proxies_python_pqc_PART_1.md), citing [3]) for Kyber768. These are reasonably close but show a range.
*   **Nature of "Contradiction":** Variability in reported performance metrics, likely due to different testing conditions and algorithm parameters. Not direct contradictions but requires careful interpretation.
*   **Implication for Fava:** Fava should conduct its own targeted performance testing within its specific environment and for its specific use cases once PQC libraries are integrated, rather than solely relying on generic benchmarks.

## 4. Frontend SHA-3 Hashing Performance

*   **Observation:** The performance of SHA-3 in JavaScript (pure JS vs. WASM) compared to native SHA-256 was presented with figures.
*   **Specifics:**
    *   Pure JS SHA-3 cited as "~5x slower than native SHA-256."
    *   WASM SHA-3 cited as achieving "~2x speed improvement over JS."
    *   Benchmarks: "SHA3-256: ~50 MB/s (WASM) vs ~25 MB/s (pure JS)" and "SHA-256: ~500 MB/s (native)" ([`pf_hashing_pqc_frontend_PART_1.md`](../data_collection/primary_findings/pf_hashing_pqc_frontend_PART_1.md), citing [5]).
    *   The "~5x slower" for pure JS (500/25 = 20x by MB/s, or 500/50 = 10x for WASM) seems to be a general statement, while the MB/s figures are more specific. The "2x speed improvement" for WASM over pure JS (50MB/s vs 25MB/s) is consistent.
*   **Nature of "Contradiction":** Slight ambiguity in the "5x slower" statement versus the derived factors from MB/s data. The core message (JS SHA-3 is significantly slower than native SHA-256, WASM helps but doesn't reach native SHA-256 speed) remains consistent.
*   **Implication for Fava:** If frontend SHA-3 hashing is adopted, performance impact is expected and should be tested, especially for large inputs.

*(This document will be updated if more significant contradictions or ambiguities emerge.)*