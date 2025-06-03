# Primary Findings: PQC Algorithm Performance Benchmarks (Addressing Gap G1.3)

**Date Compiled:** 2025-06-02
**Research Focus:** G1.3: Concrete performance benchmarks (latency, throughput, memory) for selected PQC algorithms (Kyber, Dilithium, Falcon, SPHINCS+) specifically in Python contexts or with relevant C libraries callable from Python.
**Source:** AI Search (Perplexity MCP) - Query: "Performance benchmarks (latency, throughput, memory usage) for PQC algorithms Kyber (ML-KEM), Dilithium (ML-DSA), Falcon, and SPHINCS+ (SLH-DSA). Focus on results from implementations in Python (e.g., using oqs-python) or C libraries callable from Python (e.g., liboqs). Include key generation, encapsulation/decapsulation, signing, and verification operations. Cite sources, preferably academic papers, official library documentation, or NIST reports."

This document summarizes performance benchmark findings for selected NIST PQC algorithms, with a focus on C library implementations (like liboqs, which underpins `oqs-python`) and considerations for Python contexts.

## General Notes on Benchmarks:

*   Performance figures are highly dependent on the specific hardware (CPU, architecture like x86-64 or ARM), software implementation (e.g., reference C, AVX2 optimized), security level/parameter set chosen, and compiler.
*   Python implementations (e.g., via `oqs-python` wrapping `liboqs`) will generally incur overhead compared to direct C execution due to the Python interpreter and CFFI (C Foreign Function Interface) calls. This overhead can be significant for very frequent or low-latency operations.
*   The following data is primarily based on C library performance, often from `liboqs` or NIST's reference implementations.

## CRYSTALS-Kyber (ML-KEM)

*   **Operations (liboqs, C, often on x86-64 with AVX2 optimizations where available):**
    *   **Key Generation (e.g., Kyber-768):**
        *   Reference C: ~73µs - 144µs
        *   AVX2 Optimized: Can be significantly faster (e.g., ~40-70µs).
    *   **Encapsulation (e.g., Kyber-768):**
        *   Reference C: ~97µs
        *   AVX2 Optimized: ~42µs
    *   **Decapsulation (e.g., Kyber-768):**
        *   Reference C: ~114µs
        *   AVX2 Optimized: ~48µs
*   **Throughput (liboqs, C, x86 with AVX2, e.g., Kyber-768):**
    *   Reported in the range of 8,900 to 14,200 KEM operations (encaps/decaps pairs) per second.
*   **Memory Usage (Approximate):**
    *   Public Key (e.g., Kyber-768): ~1184 bytes
    *   Private Key (e.g., Kyber-768): ~2400 bytes
    *   Ciphertext (e.g., Kyber-768): ~1088 bytes
*   **Python (`oqs-python`) Considerations:**
    *   Expect latencies to be higher due to wrapper overhead. For instance, a C operation taking 100µs might take several hundred µs or even milliseconds in Python depending on call frequency and data marshalling. Throughput will be correspondingly lower.
    *   Memory for key objects in Python will include Python object overhead in addition to the raw key material size.

## CRYSTALS-Dilithium (ML-DSA)

*   **Operations (liboqs, C, often on x86-64 with AVX2 optimizations):**
    *   **Key Generation (e.g., Dilithium3):**
        *   Reference C: ~1120µs
        *   AVX2 Optimized: ~495µs
    *   **Signing (e.g., Dilithium3):**
        *   AVX2 Optimized: ~1.3 ms (1300µs)
    *   **Verification (e.g., Dilithium3):**
        *   AVX2 Optimized: ~236µs
*   **Memory Usage (Approximate):**
    *   Public Key (e.g., Dilithium3): ~1952 bytes
    *   Private Key (e.g., Dilithium3): ~4000 bytes
    *   Signature (e.g., Dilithium3): ~3293 bytes
*   **Python (`oqs-python`) Considerations:** Similar overheads as with Kyber. Signing and verification, being more complex, might show noticeable latency increases in Python for single operations.

## Falcon

*   **Operations (liboqs, C, often on x86-64):**
    *   **Key Generation (e.g., Falcon-512):** Can be relatively slow, potentially milliseconds.
    *   **Signing (e.g., Falcon-512):**
        *   Reported around 4.8ms on a quad-core system for Falcon-1024 (a higher security level). Falcon-512 would be faster but still generally slower than Dilithium signing.
        *   Some benchmarks show Falcon-512 signing in the range of 1-5 ms.
    *   **Verification (e.g., Falcon-512):**
        *   Very fast, often cited as one of its main advantages.
        *   Reported around 92µs for Falcon-1024. Falcon-512 verification is typically in the tens of microseconds (e.g., 20-50µs).
*   **Memory Usage (Approximate):**
    *   Public Key (e.g., Falcon-512): ~897 bytes
    *   Private Key (e.g., Falcon-512): ~1281 bytes (can be larger for other variants or if expanded for signing)
    *   Signature (e.g., Falcon-512): ~690 bytes (compact signatures are a key feature)
*   **Python (`oqs-python`) Considerations:** Verification speed advantage might be somewhat diminished by Python overhead but should still be relatively fast. Signing latency will be noticeable.

## SPHINCS+ (SLH-DSA)

*   **Operations (liboqs, C, often on x86-64):**
    *   **Key Generation (e.g., SPHINCS+-SHA256-128f-simple):** Can be slow, often multiple milliseconds.
    *   **Signing (e.g., SPHINCS+-SHA256-128f-simple):**
        *   Relatively slow, often in the range of 25-70ms depending on the parameter set and specific optimizations. Some robust variants can be slower.
    *   **Verification (e.g., SPHINCS+-SHA256-128f-simple):**
        *   Generally faster than signing, often around 1-2ms, but can be up to a few milliseconds for some variants.
*   **Memory Usage (Approximate):**
    *   Public Key (e.g., SPHINCS+-SHA256-128f): 32 bytes
    *   Private Key (e.g., SPHINCS+-SHA256-128f): 64 bytes
    *   Signature (e.g., SPHINCS+-SHA256-128f-simple): ~17 KB (kilobytes). Some parameter sets have smaller signatures (e.g., "s" variants around 8KB), while others can be larger (up to ~41KB).
*   **Python (`oqs-python`) Considerations:** Signing, being already slow in C, will be very noticeable in Python. The large signature sizes also mean more data to pass through the CFFI layer, potentially adding to overhead.

## Summary Table (Illustrative, based on C library performance, typical x86-64, Level 3 equivalent where applicable)

| Algorithm         | Operation         | Typical Latency (C, Optimized) | Est. Python Latency | Key/Sig Size (Approx.) | Notes                                       |
|-------------------|-------------------|--------------------------------|-----------------------|------------------------|---------------------------------------------|
| **Kyber-768**     | KeyGen            | ~50 µs                         | Sub-millisecond       | PK:1.2KB, SK:2.4KB     | Fast KEM operations                         |
|                   | Encapsulate       | ~40 µs                         | Sub-millisecond       | CT: 1.1KB              |                                             |
|                   | Decapsulate       | ~50 µs                         | Sub-millisecond       |                        |                                             |
| **Dilithium3**    | KeyGen            | ~500 µs                        | Milliseconds          | PK:2KB, SK:4KB         | Balanced signature scheme                   |
|                   | Sign              | ~1300 µs (1.3 ms)              | Few Milliseconds      | Sig: 3.3KB             |                                             |
|                   | Verify            | ~240 µs                        | Sub-millisecond       |                        |                                             |
| **Falcon-512**    | KeyGen            | Milliseconds                   | Many Milliseconds     | PK:0.9KB, SK:1.3KB     | Very fast verification, compact signatures  |
|                   | Sign              | ~1-5 ms                        | Many Milliseconds     | Sig: 0.7KB             | Slower signing                              |
|                   | Verify            | ~20-50 µs                      | Sub-millisecond       |                        |                                             |
| **SPHINCS+-128f** | KeyGen            | Milliseconds                   | Many Milliseconds     | PK:32B, SK:64B         | Stateless hash-based, conservative choice   |
|                   | Sign              | ~25-70 ms                      | Tens of Milliseconds  | Sig: ~17KB             | Slow signing, large signatures              |
|                   | Verify            | ~1-2 ms                        | Few Milliseconds      |                        |                                             |

**Note on Python Latency Estimation:** "Sub-millisecond" implies likely < 1ms but noticeably more than C. "Milliseconds" implies 1-10ms. "Few Milliseconds" implies 2-5ms. "Many Milliseconds" implies >5-10ms. "Tens of Milliseconds" implies >20ms. These are rough estimates for single operations; actuals depend heavily on the system and Python environment.

**Sources for further details:**
*   NIST PQC Project website and official FIPS documents.
*   `liboqs` documentation and benchmark reports.
*   Academic papers presenting PQC algorithm benchmarks (often found on ePrint IACR).
*   Presentations from PQC standardization workshops.

This information addresses knowledge gap G1.3 by providing concrete performance benchmark data and considerations for Python contexts.