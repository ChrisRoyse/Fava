Understanding the Quantum Threat and PQC
Quantum computers, when sufficiently powerful, threaten to break much of today's public-key cryptography (e.g., RSA, ECC used in TLS, digital signatures, and file encryption like GPG). Symmetric encryption (like AES) and hash functions (like SHA-256, SHA-3) are considered more resistant, though larger key sizes or quantum-resistant hashes might be preferred for long-term security.
Post-Quantum Cryptography (PQC) refers to cryptographic algorithms believed to be secure against attacks by both classical and quantum computers. The NIST PQC Standardization project is a major effort to identify and standardize such algorithms. As of my last update, key candidates include:
Public-Key Encryption / Key Encapsulation Mechanisms (KEMs): CRYSTALS-Kyber.
Digital Signatures: CRYSTALS-Dilithium, Falcon, SPHINCS+.
An agile cryptographic strategy is crucial because the PQC landscape is still evolving. New attacks could be discovered, or new algorithms standardized. Your system should be able to switch algorithms with minimal code changes, ideally through configuration. Hybrid schemes, which combine a classical algorithm with a PQC algorithm (requiring an attacker to break both), are often recommended for a transition period.
Core Principles for PQC Upgrade in Fava:
Cryptographic Agility: Abstract all cryptographic operations (encryption, decryption, hashing, signing, verification) behind a service layer. This layer can then have different implementations (classical, PQC, hybrid) selectable via configuration.
Focus on Interfaces: Identify where Fava interacts with encrypted data or relies on cryptographic integrity.
Data at Rest: Primarily Beancount file encryption.
Data in Transit: HTTPS/TLS for all client-server communication.
Data Integrity: Hashing mechanisms (e.g., for file change detection).
Dependency Awareness: Fava relies on Beancount for some operations (like encrypted file handling via GPG). Beancount's own PQC readiness will be a factor.
Detailed Plan for PQC Integration in Fava
Here's a breakdown by area, identifying files, current code context, why changes are needed, and how to approach them with agility:
I. Data at Rest: Encrypted Beancount Files
Files Involved:
Backend: src/fava/beans/load.py, src/fava/core/__init__.py (FavaLedger class)
Current Situation:
Fava relies on Beancount's loader for encrypted files, which typically uses GPG.
src/fava/beans/load.py: load_uncached calls beancount.loader.load_file() or beancount.loader._load(), which handle decryption if an encryption_key is provided via Beancount options.
src/fava/core/__init__.py: FavaLedger checks self.config["is_encrypted"] and passes self.encryption_key to the loader.
Why Change: GPG's traditional algorithms (RSA, ElGamal for public key; various symmetric ciphers) are vulnerable to quantum attacks. If users encrypt their Beancount files with classical GPG, this data is at risk.
Proposed Changes & Agile Strategy:
Monitor Beancount/GPG PQC Support: The ideal scenario is for Beancount and GPG to adopt PQC standards. Fava would then benefit by updating its Beancount dependency and ensuring compatibility.
Introduce a Decryption Abstraction Layer (Fava-side):
Instead of relying solely on Beancount's internal decryption, Fava could introduce its own decryption service.
This service would be responsible for handling different encryption schemes based on file metadata or configuration.
Interface Example (src/fava/crypto_service.py - new file):
from abc import ABC, abstractmethod

class DecryptionService(ABC):
    @abstractmethod
    def decrypt_content(self, encrypted_content: bytes, key_info: Any) -> str:
        """Decrypts content, returns plaintext string."""
        pass

class PQCFileConfig: # Example config for a file
    algorithm_name: str # e.g., "hybrid-aes256-kyber768"
    key_derivation_method: str
    # ... other necessary parameters
Use code with caution.
Python
Configuration: Fava's options could specify the PQC algorithm and key management details if Fava handles decryption directly.
Agility: The DecryptionService can have multiple implementations:
GPGClassicalDecryptionService: Wraps current GPG logic.
PQCHybridDecryptionService: Implements a hybrid PQC scheme (e.g., AES-GCM for symmetric part, with key derived/unwrapped using a PQC KEM like Kyber).
A factory function would choose the service based on configuration or file metadata.
Modify FavaLedger.load_file() (src/fava/core/__init__.py):
Current Snippet (Conceptual):
# In FavaLedger.load_file()
entries, errors, options = load_uncached(
    self.beancount_file_path,
    is_encrypted=self.config["is_encrypted"],
    encryption_key=self.encryption_key, # This is Beancount's mechanism
)
Use code with caution.
Python
Proposed Snippet (Conceptual, if Fava handles PQC decryption):
# In FavaLedger.load_file()
# from fava.crypto_service import get_decryption_service, PQCFileConfig

content_bytes: bytes
with open(self.beancount_file_path, "rb") as f:
    content_bytes = f.read()

plaintext_content: str
if self.config["is_encrypted"]: # And potentially new config for PQC
    # file_pqc_config = self.fava_options.get_pqc_config_for_file(self.beancount_file_path) # Example
    # decryption_service = get_decryption_service(file_pqc_config.algorithm_name)
    # key_info = ... #  obtain key material, possibly from a PQC KEM process or derived key
    # plaintext_content = decryption_service.decrypt_content(content_bytes, key_info)
    # This part is complex and depends heavily on how PQC keys are managed and stored.
    # For now, Fava might need to rely on external tools to decrypt to a temporary PQC-GPG-like stream
    # if direct PQC library integration is too complex.
    # A simpler interim step could be to support Beancount files decrypted by an external PQC GPG utility.
    # For true agility, Fava would need to handle various PQC KEMs/schemes.
    # A more realistic first step is to support what Beancount/GPG support.
    # For this example, let's assume a PQC-aware GPG is used by Beancount:
    pass # Continue using Beancount's load_uncached if it becomes PQC-aware

# If Fava were to decrypt *before* passing to Beancount:
# if is_pqc_encrypted_fava_style(self.beancount_file_path):
#     pqc_config = self.fava_options.get_pqc_config(...)
#     dec_service = get_decryption_service(pqc_config.algo)
#     key_info = ...
#     content_str = dec_service.decrypt_content(content_bytes, key_info)
#     entries, errors, options = load_string(content_str) # load from string
# else: # classical GPG via Beancount
#     entries, errors, options = load_uncached(...)
Use code with caution.
Python
Challenge: Direct PQC decryption in Fava means Fava needs to manage PQC keys or interact with PQC key stores, which is a significant security responsibility. The most practical approach is to support formats that PQC-updated GPG or Beancount can handle.
User Guidance: Clearly document which PQC tools/GPG versions are compatible for encrypting Beancount files.
II. Data in Transit: HTTPS/TLS
Files Involved:
Backend: src/fava/cli.py (server setup), src/fava/application.py (Flask app).
Frontend: frontend/src/lib/fetch.ts, frontend/src/api/index.ts (all API calls).
Current Situation: Fava relies on the WSGI server (Cheroot or Flask's development server) and potentially a reverse proxy (Nginx, Apache) to handle HTTPS and TLS. Frontend fetch calls use the browser's HTTPS capabilities.
Why Change: The key exchange (e.g., RSA, ECDH) and digital signature algorithms (e.g., RSA, ECDSA) used in traditional TLS are vulnerable to quantum attacks.
Proposed Changes & Agile Strategy:
Server-Side TLS Configuration:
src/fava/cli.py: When launching Cheroot or Flask's dev server, there isn't direct TLS PQC configuration here. This is typically handled by:
Reverse Proxy: If users run Fava behind Nginx or Apache, these reverse proxies need to be configured to support TLS 1.3 with PQC key exchange mechanisms (KEMs) and PQC certificates (if available and CAs support them). Common KEMs being experimented with include Kyber.
Cheroot/Python Web Servers: Python's ssl module and web servers like Cheroot would need to support OpenSSL (or equivalent) versions that include PQC cipher suites. As of now, direct PQC cipher suite configuration in Python's ssl module is still emerging.
Agility: The Fava CLI could potentially offer options to specify preferred PQC cipher suites if the underlying server libraries support it, or guide users on reverse proxy configuration.
Recommendation: For Fava's direct deployment, strongly recommend using a PQC-capable reverse proxy for TLS termination.
Frontend: No direct code changes are needed in fetch.ts or api/index.ts as they rely on the browser's TLS stack. Browsers are gradually adding experimental support for PQC KEMs in TLS 1.3 (e.g., Chrome's X25519Kyber768). The security depends on both the client (browser) and server supporting compatible PQC cipher suites.
Documentation: Provide clear documentation on how to set up Fava with a PQC-capable reverse proxy.
III. Data Integrity: Hashing
Files Involved:
Backend: src/fava/core/file.py (SHA256 for file integrity on save).
Frontend: frontend/src/editor/SliceEditor.svelte (SHA256 for optimistic concurrency).
Current Situation: SHA256 is used.
Why Change: While SHA256's collision resistance is quadratically affected by Grover's algorithm (reducing effective strength to 128-bit for collisions), its preimage resistance (harder to find an input for a given hash) is more robust against quantum attacks. For non-cryptographic signing purposes like integrity checks or optimistic locking, SHA256 is likely to remain sufficient for a considerable time. However, for very long-term security or higher assurance, moving to SHA3 or a PQC-specific hash might be considered.
Proposed Changes & Agile Strategy:
Hashing Abstraction Layer:
Create a hashing service similar to the decryption service.
Interface Example (src/fava/crypto_service.py):
class HashingService(ABC):
    @abstractmethod
    def hash_data(self, data: bytes) -> str: # returns hex digest
        """Hashes data, returns hex digest."""
        pass
Use code with caution.
Python
Implementations: SHA256HashingService, SHA3_256HashingService, etc.
Configuration to select the hashing algorithm.
Modify Usage in src/fava/core/file.py:
Current Snippet (Conceptual):
# import hashlib
# current_hash = hashlib.sha256(content_bytes).hexdigest()
Use code with caution.
Python
Proposed Snippet (Conceptual):
# from fava.crypto_service import get_hashing_service
# hashing_service = get_hashing_service() # Reads from config
# current_hash = hashing_service.hash_data(content_bytes)
Use code with caution.
Python
Modify Usage in frontend/src/editor/SliceEditor.svelte:
The frontend calculates the SHA256 sum and sends it. If the backend hashing algorithm changes, the frontend might need to:
A) Send the raw content and let the backend calculate the hash for comparison (simplifies frontend, backend does more work).
B) Implement a similar hashing abstraction in JavaScript/WASM, allowing it to use the same PQC hash algorithm as the backend. This requires PQC hashing libraries in JS.
Given this is for optimistic concurrency, the exact hash algorithm might be less critical than consistency between client and server if the server re-calculates. However, if the client-provided hash is trusted for comparison, both must use the same (potentially PQC) algorithm.
Frontend Hashing Abstraction (Conceptual frontend/src/lib/crypto.ts):
// frontend/src/lib/crypto.ts - new file
export async function calculateHash(data: string, algorithm: string = "SHA-256"): Promise<string> {
    const subtleCrypto = window.crypto.subtle;
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    let hashBuffer: ArrayBuffer;
    if (algorithm.toUpperCase() === "SHA-256") {
        hashBuffer = await subtleCrypto.digest("SHA-256", dataBuffer);
    } else if (algorithm.toUpperCase() === "SHA3-256") { // Requires SHA3 JS lib
        // hashBuffer = await sha3_256_library(dataBuffer);
        throw new Error("SHA3-256 not implemented yet in frontend crypto.ts");
    } // Add other PQC hashes here
    else {
        throw new Error(`Unsupported hash algorithm: ${algorithm}`);
    }
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
Use code with caution.
TypeScript
SliceEditor.svelte would then call calculateHash(currentSlice, configured_hash_algorithm). The configured_hash_algorithm could be fetched from Fava's options.
IV. WASM Module Integrity
Files Involved:
Frontend: frontend/src/codemirror/beancount.ts (loads tree-sitter-beancount.wasm).
Current Situation: WASM files are loaded, typically assuming they are trusted as part of the Fava deployment.
Why Change (Enhanced Security): To ensure the WASM files haven't been tampered with, especially if they could be served from CDNs or less trusted paths in some deployment scenarios.
Proposed Changes & Agile Strategy:
Digital Signatures for WASM:
During the build/release process, sign the WASM modules using a PQC digital signature algorithm (e.g., Dilithium).
Distribute the public key with Fava's frontend.
Before instantiating the WASM module, the frontend fetches the WASM binary and its corresponding signature.
It then verifies the signature using the PQC public key.
Implementation (Conceptual frontend/src/codemirror/beancount.ts):
// In loadBeancountParser()
// const wasmPath = import.meta.resolve("./tree-sitter-beancount.wasm");
// const signaturePath = import.meta.resolve("./tree-sitter-beancount.wasm.sig"); // Example

// const [wasmBuffer, signatureBuffer] = await Promise.all([
//     fetch(wasmPath).then(res => res.arrayBuffer()),
//     fetch(signaturePath).then(res => res.arrayBuffer())
// ]);

// const publicKey = "..."; // Load Fava's PQC public key
// const isValid = await verifyPqcSignature(publicKey, wasmBuffer, signatureBuffer); // Needs PQC JS lib
// if (!isValid) {
//     throw new Error("WASM signature verification failed!");
// }
// const parser = await TSParser.init({
//     locateFile: (file: string, scriptDirectory: string) => {
//         if (file === "tree-sitter.wasm") return tsWasmPath;
//         return scriptDirectory + file;
//     },
// });
// const Beancount = await TSLanguage.load(wasmBuffer); // Use verified buffer
Use code with caution.
TypeScript
Agility: The verifyPqcSignature function would be part of a frontend crypto abstraction layer, allowing the signature algorithm to be updated.
Subresource Integrity (SRI): If WASM files are served from known URLs, SRI can also provide integrity but not authenticity against a compromised server. PQC signatures provide stronger authenticity.
V. Cryptographic Agility Implementation Details
Backend (src/fava/crypto_service.py - New File):
from abc import ABC, abstractmethod
from typing import Any, Dict
# Import PQC libraries (e.g., from PyOQS or future standard libs)
# import oqs # Example

class CryptoConfig:
    algorithm: str
    parameters: Dict[str, Any]

class AbstractCryptoService(ABC):
    def __init__(self, config: CryptoConfig):
        self.config = config

    @abstractmethod
    def encrypt(self, plaintext: bytes, key: bytes) -> bytes: pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, key: bytes) -> bytes: pass

    @abstractmethod
    def generate_kem_keypair(self) -> tuple[bytes, bytes]: pass # pub, priv

    @abstractmethod
    def kem_encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]: pass # ciphertext, shared_secret

    @abstractmethod
    def kem_decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes: pass # shared_secret

    @abstractmethod
    def sign(self, message: bytes, private_key: bytes) -> bytes: pass

    @abstractmethod
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool: pass

    @abstractmethod
    def hash_data(self, data: bytes) -> str: pass # hex digest

# Example PQC KEM Implementation (Conceptual)
# class KyberKEMService(AbstractCryptoService):
#     def generate_kem_keypair(self):
#         with oqs.KeyEncapsulation(self.config.parameters.get("kem_name", "Kyber768")) as kem:
#             public_key = kem.generate_keypair()
#             secret_key = kem.export_secret_key()
#             return public_key, secret_key
#     # ... other methods

_SERVICE_REGISTRY = {}
_CURRENT_CONFIGS = {} # Loaded from Fava options

def register_crypto_service(name: str, service_class: type[AbstractCryptoService]):
    _SERVICE_REGISTRY[name] = service_class

def get_crypto_service(context_name: str = "default") -> AbstractCryptoService:
    config = _CURRENT_CONFIGS.get(context_name)
    if not config:
        raise ValueError(f"No crypto config found for context: {context_name}")
    service_class = _SERVICE_REGISTRY.get(config.algorithm)
    if not service_class:
        raise ValueError(f"Unsupported crypto algorithm: {config.algorithm}")
    return service_class(config)

def load_crypto_configs_from_fava_options(options: FavaOptions):
    # Logic to parse crypto algorithm choices from fava_options
    # e.g., options.get("pqc_file_encryption_algorithm", "hybrid-kyber-aes")
    # Populate _CURRENT_CONFIGS
    # _CURRENT_CONFIGS["file_encryption"] = CryptoConfig(algorithm="hybrid-kyber-aes", params={...})
    # _CURRENT_CONFIGS["default_hash"] = CryptoConfig(algorithm="SHA3-256", params={})
    pass
Use code with caution.
Python
This service would be initialized by FavaLedger after parsing FavaOptions.
Fava's options (fava_options.py) would need new entries to specify preferred PQC algorithms for different contexts (file encryption, hashing).
Frontend (frontend/src/lib/crypto.ts - New File):
Similar abstraction for JavaScript, likely using WASM-compiled PQC libraries (like liboqs-js).
The frontend would fetch its PQC configuration (e.g., which hash algorithm to use) from a Fava API endpoint that exposes relevant parts of FavaOptions.
VI. Extension System (src/fava/ext/__init__.py)
Current Situation: Extensions can be arbitrary Python code.
Why Change: If extensions handle sensitive data or perform cryptographic operations, they should also adopt PQC.
Proposed Changes:
Documentation and Guidance: Provide clear documentation to extension developers about PQC and recommend they use Fava's (future) CryptoService if their extensions need crypto.
Expose CryptoService (Optional): Fava could potentially pass an instance of the configured CryptoService to extensions if there's a common need.
This is more about guidance than direct code changes in Fava's core extension loading, unless Fava wants to enforce or provide PQC tools to extensions.
VII. Testing and Validation
Unit Tests: For the new CryptoService and its implementations. Test with known PQC test vectors if available.
Integration Tests:
Test PQC file decryption (requires creating test files encrypted with PQC tools).
Test PQC hashing consistency between frontend and backend.
Test WASM signature verification.
TLS Configuration Testing: Use tools like testssl.sh or online SSL checkers (once they support PQC) to verify server TLS PQC setup.
VIII. Phased Rollout / Hybrid Approach
Phase 1: Abstraction and Classical Support:
Implement the CryptoService abstraction layers (backend and frontend) but initially only with implementations for the current classical algorithms (GPG pass-through, SHA256).
Refactor existing code to use this abstraction layer. This prepares the codebase.
Phase 2: Hybrid Mode for Critical Areas:
For Beancount file encryption, prioritize supporting a hybrid GPG mode if/when it becomes available and Beancount supports it. This offers backward compatibility and forward security.
For TLS, encourage users to adopt reverse proxies that support hybrid PQC KEMs.
Phase 3: Pure PQC Options:
As PQC algorithms stabilize and libraries mature, add pure PQC implementations to the CryptoService.
Allow users to configure Fava to use these pure PQC modes, understanding the trade-offs (e.g., potential lack of widespread tool support for pure PQC encrypted files initially).
Hashing: Transition from SHA256 to SHA3 (e.g., SHA3-256) via the abstraction layer can be an earlier step, as SHA3 is generally considered more robust than SHA2-variants against future attacks, including quantum.
IX. Libraries and Tooling
Python:
liboqs (Open Quantum Safe project): Provides C library with Python bindings for many PQC algorithms. This would be a primary candidate for implementing PQC KEMs and signatures in CryptoService.
Future Python standard library ssl / hashlib / cryptography package updates may include PQC algorithms.
JavaScript/Frontend:
liboqs-js: WASM-compiled version of liboqs.
Web Cryptography API (window.crypto.subtle): Browser vendors may eventually add PQC algorithms here. For now, custom WASM libraries are needed for most PQC operations.
GPG: Monitor GnuPG project for PQC support.
X. Important Considerations
Performance: PQC algorithms can have different performance characteristics (key sizes, computation time) than classical ones. This needs to be benchmarked, especially for KEMs and signatures.
Key Management: PQC keys can be larger. How keys for file encryption are managed, stored, and input by the user needs careful consideration. If relying on a PQC-GPG, this is delegated. If Fava implements its own, it's a major task.
Standardization Flux: The PQC landscape is still somewhat in flux, although NIST's selections provide strong candidates. The agile approach is key to adapting to changes.
User Experience: Introducing PQC, especially for file encryption, must be done with clear guidance for users on how to generate/manage PQC keys and encrypt their files.