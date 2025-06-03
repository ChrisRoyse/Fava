# Fava Post-Quantum Cryptography (PQC) User Guide v1.1

**Version:** 1.1
**Date:** 2025-06-03

## 1. Introduction to PQC in Fava

Welcome to the world of enhanced security with Fava! This guide explains how Fava is incorporating Post-Quantum Cryptography (PQC) to provide stronger, future-proof protection for your financial data.

### 1.1. Why PQC?

As quantum computers become more powerful, they pose a potential threat to current cryptographic algorithms that protect our data online and at rest. PQC refers to cryptographic methods that are secure against attacks from both classical and quantum computers.

Fava is integrating PQC to:
*   **Enhance long-term security:** Ensure your financial data remains confidential and secure even in the face of future quantum computing advancements.
*   **Protect sensitive information:** Provide robust protection for your Beancount files and your interactions with Fava.

### 1.2. What This Means for You

For most users, Fava will continue to work seamlessly. The key changes involve:
*   New options for encrypting your Beancount data using PQC.
*   Guidance for administrators on setting up Fava with PQC-secured connections.
*   Enhanced integrity checks for parts of the Fava application.

This guide will walk you through these new features and configurations.

## 2. Configuration

Fava introduces several PQC-related configurations. Most of these are managed through Fava's standard options/settings interface, but understanding them can help you tailor Fava's security to your needs. Advanced settings might be found in a configuration file like `config/fava_crypto_settings.py` (see [`src/fava/pqc/global_config.py`](../../src/fava/pqc/global_config.py)), but Fava's UI should be the primary way to manage these.

### 2.1. General Cryptographic Settings

Fava now has a more comprehensive way to manage its cryptographic operations, ensuring it can adapt to new security standards over time (this is known as cryptographic agility).

Key settings you might encounter in Fava's options related to PQC include:

*   **Data at Rest (Beancount File Encryption):**
    *   `Enable PQC Decryption`: Allows Fava to decrypt files encrypted with supported PQC schemes. (Default: Enabled)
    *   `Enable Fava-PQC Encryption`: Allows Fava to encrypt files using its built-in PQC hybrid scheme. (Default: Enabled)
    *   `Active PQC Encryption Suite`: Determines which PQC algorithm combination Fava uses when you choose to encrypt a new file with PQC. The default is a hybrid scheme: `X25519` (classical) + `ML-KEM-768` (Kyber PQC KEM) + `AES-256-GCM` (symmetric encryption).
    *   `PQC Key Management Mode`:
        *   `PASSPHRASE_DERIVED`: (Default) Fava will derive the necessary PQC keys from a strong passphrase you provide.
        *   `EXTERNAL_KEY_FILE`: For advanced users, allows specifying paths to externally managed PQC key files.
    *   `Decryption Attempt Order`: Fava can try decrypting files using a list of configured methods, ensuring compatibility with files encrypted using older (but still supported) PQC schemes or classical GPG.

*   **Hashing Algorithm:**
    *   `Default Hashing Algorithm`: Fava uses hashing for data integrity checks (e.g., when saving files, for optimistic concurrency in the editor).
        *   Default: `SHA3-256` (a PQC-resistant hash algorithm).
        *   Option: `SHA256` (classical SHA-2).
    *   This ensures consistency between frontend and backend operations.

*   **WASM Module Integrity Verification:**
    *   `Enable WASM PQC Verification`: (Default: Enabled) Fava verifies the integrity of its Beancount parser (a WebAssembly module) using PQC digital signatures (Dilithium3) to protect against tampering.

You can typically find these settings in Fava's main configuration panel.

### 2.2. PQC for Data in Transit (HTTPS/TLS with a Reverse Proxy)

Fava itself does not directly handle the PQC TLS handshake for your browser connection. Instead, it relies on a **PQC-capable reverse proxy** (like Nginx or Caddy) that you, as the administrator deploying Fava, would set up.

*   **How it Works:**
    1.  Your browser connects to the reverse proxy using HTTPS with a PQC hybrid KEM (Key Encapsulation Mechanism), typically `X25519Kyber768`.
    2.  The reverse proxy handles the PQC-TLS encryption/decryption.
    3.  The reverse proxy then communicates with the Fava application (usually over plain HTTP on a secure internal network or localhost).

*   **Fava Configuration:**
    *   Fava has an option like `assume_pqc_tls_proxy_enabled` (see [`src/fava/application.py`](../../src/fava/application.py)). If set to `true`, Fava can log or assume that PQC protection is active at the proxy level, even if it doesn't detect specific PQC headers from the proxy.

*   **Reverse Proxy Setup (Admin Task):**
    *   Consult Fava's official deployment documentation for detailed examples on configuring Nginx or Caddy with PQC-TLS support (e.g., using OpenSSL compiled with OQS provider).
    *   The recommended PQC hybrid KEM for TLS is `X25519Kyber768`.
    *   You will use standard SSL/TLS certificates (e.g., ECC or RSA based) for your proxy, as PQC certificates are not yet standard.

*   **⚠️ CRITICAL SECURITY WARNING ⚠️**
    As detailed in [`docs/security/PQC_Deployment_Security_Considerations.md`](../security/PQC_Deployment_Security_Considerations.md), the communication link between your reverse proxy and the Fava application server is plain HTTP by default.
    *   **This is ONLY safe if the proxy and Fava are on the same host (communicating via `localhost`) OR within a physically/virtually secured private network segment.**
    *   If this internal link is not secure, you **MUST** secure it independently (e.g., by configuring Fava to listen on HTTPS for the proxy, using mTLS, or an IPSec tunnel). Failure to do so exposes unencrypted Fava data between the proxy and the application.

### 2.3. PQC Hashing Algorithm Configuration

As mentioned in Section 2.1, Fava uses hashing for data integrity.
*   **Default:** `SHA3-256` (PQC-resistant)
*   **Alternative:** `SHA256`
This can be configured in Fava's options. The frontend will use the same algorithm as the backend for consistency (e.g., for optimistic concurrency checks in the editor).

## 3. Fava-Driven PQC Encryption (Data at Rest)

Fava now offers built-in functionality to encrypt your Beancount files using a strong PQC hybrid scheme. This protects your financial data at rest against both current and future quantum threats.

### 3.1. How to Encrypt Your Beancount File with PQC

1.  **Ensure PQC Encryption is Enabled:** Check Fava's settings (see Section 2.1). The `Active PQC Encryption Suite` will typically be `X25519` + `ML-KEM-768` (Kyber) + `AES-256-GCM`.
2.  **Initiate Encryption:** Fava should provide an option in its UI (e.g., in the file browser or editor) like "Encrypt with PQC Hybrid" for your unencrypted Beancount file.
3.  **Key Management:**
    *   **Passphrase Mode (Default):** Fava will prompt you to enter a **strong, unique passphrase**. This passphrase will be used to derive the necessary PQC keys. Remember this passphrase! If you lose it, your data will be irrecoverable. Fava uses strong methods (Argon2id for passphrase stretching, then HKDF for key derivation) to protect your keys.
    *   **External Key File Mode (Advanced):** If configured, Fava might allow you to specify paths to PQC key files you manage externally.
4.  **Encryption Process:** Fava will encrypt your Beancount file and save it, typically with a new extension indicating PQC hybrid encryption (e.g., `yourfile.bc.pqc_hybrid_fava`).
5.  **Confirmation:** Fava will confirm the successful encryption and the name/location of the new encrypted file.

Your original unencrypted file will usually remain untouched. You can then choose to use the new PQC-encrypted version with Fava.

### 3.2. Passphrase Requirements and Key Management

*   **Strong Passphrases:** If using passphrase-derived keys, choose a long, complex, and unique passphrase. Treat it like the master key to your financial data.
*   **Key Derivation:** Fava uses robust cryptographic techniques (Argon2id for stretching your passphrase and HKDF for deriving keys) to generate the actual encryption keys. This makes it harder for attackers to guess your passphrase.
*   **Exporting Fava-Managed PQC Keys (Advanced & High Risk):**
    *   Fava may offer a feature to export your PQC private keys if they are managed by Fava (e.g., derived from your passphrase). This is for users who need to decrypt their files outside of Fava or for backup purposes.
    *   **WARNING:** Exporting raw private keys is extremely risky. If these exported keys are lost, stolen, or mishandled, your data's security is compromised.
    *   If you use this feature, Fava will require multiple confirmations and provide strong warnings. The exported key file itself should be protected with another strong passphrase.

### 3.3. Interaction with Classical GPG Encryption

Fava maintains backward compatibility with Beancount files encrypted using classical GPG.
*   **Loading GPG Files:** You can continue to load and use your existing GPG-encrypted (`.gpg`) files in Fava without any changes. Fava will use your system's GPG tools/agent to decrypt them.
*   **PQC for New Encryption:** The Fava-driven PQC encryption is for encrypting new files or for re-encrypting existing (plain or GPG-encrypted) files if you wish to upgrade their protection to PQC. Fava does not automatically convert GPG files to PQC.

## 4. PQC WASM Module Integrity

Fava uses a WebAssembly (WASM) module for parsing Beancount files in your browser (e.g., for syntax highlighting in the editor). To ensure this critical component hasn't been tampered with, Fava now verifies its integrity using PQC digital signatures.

*   **How it Works:**
    *   During Fava's build process, the WASM parser is signed with a PQC signature algorithm (Dilithium3).
    *   When your browser loads Fava, it fetches the WASM module and its PQC signature.
    *   Fava's frontend code then verifies this signature using an embedded PQC public key.
*   **What this means for you:**
    *   **Enhanced Security:** This provides stronger assurance that the Beancount parser you are using is authentic and unmodified.
    *   **Transparency:** If verification is successful (the default), this process is transparent.
    *   **Verification Failure:** If the signature verification fails (e.g., due to a corrupted module or a (highly unlikely) successful attack), Fava will:
        *   Log an error in your browser's developer console.
        *   Not load the WASM parser.
        *   Features dependent on the parser (like editor syntax highlighting or client-side validation) may be degraded or unavailable. Fava might display a message indicating this.
*   **Configuration:** This verification is enabled by default. An option like `Enable WASM PQC Verification` (see Section 2.1) might be available in Fava's settings for troubleshooting or development builds, but disabling it in production is strongly discouraged.

## 5. Cryptographic Agility in Fava

The world of cryptography is always evolving. "Cryptographic Agility" means Fava is designed to adapt to these changes.

*   **Future-Proofing:** Fava can be updated to support new or improved PQC algorithms as they become standardized and available in the underlying cryptographic libraries. This ensures Fava can maintain strong security for your data over the long term.
*   **User-Visible Aspects:**
    *   **Algorithm Selection (Configuration):** As new PQC suites are supported, you might see them as options in Fava's cryptographic settings (e.g., for the `Active PQC Encryption Suite`).
    *   **Backward Compatibility for Decryption:** Even if Fava is updated to use a new PQC scheme for encrypting *new* files, it will still be able to decrypt files that were encrypted with older (but still supported and secure) PQC schemes you used previously. Fava's `Decryption Attempt Order` setting helps manage this.

This design means you don't have to worry about your PQC-encrypted files becoming inaccessible if Fava updates its preferred algorithms, as long as the older schemes remain secure and supported.

## 6. Troubleshooting & FAQs

**Q: What PQC algorithms does Fava use by default?**
A: For encrypting data at rest, Fava uses a hybrid scheme combining X25519 (classical) and ML-KEM-768 (Kyber PQC KEM) with AES-256-GCM for symmetric encryption. For hashing, it defaults to SHA3-256. For WASM module integrity, it uses Dilithium3 PQC signatures.

**Q: I'm trying to load my PQC-encrypted Beancount file, but Fava shows an error. What could be wrong?**
A: Possible reasons include:
    *   **Incorrect Passphrase:** If your keys are passphrase-derived, ensure you're entering the exact passphrase.
    *   **Corrupted File:** The encrypted file itself might be corrupted.
    *   **Algorithm Mismatch:** Fava might be configured differently than when the file was encrypted (though Fava tries to handle older supported schemes). Check Fava's logs for specific error messages.
    *   **Missing PQC Libraries:** Ensure Fava's underlying PQC libraries (`oqs-python`, `cryptography`) are correctly installed. Fava should log an error if these are missing.

**Q: My Fava instance is behind a PQC-TLS reverse proxy, but I'm getting connection errors.**
A:
    *   Check your reverse proxy configuration (e.g., Nginx, Caddy) carefully. Ensure it's set up for the correct PQC KEM (e.g., `X25519Kyber768`) and TLS 1.3.
    *   Verify your browser supports the PQC KEM configured on the proxy. Some browsers require experimental flags to be enabled.
    *   Ensure your proxy's SSL certificates are valid.
    *   Check proxy logs for TLS handshake errors.
    *   Remember to secure the connection *between* your proxy and Fava if they are not on the same trusted machine/network (see Section 2.2).

**Q: Fava's editor isn't showing syntax highlighting, or I see errors about WASM verification.**
A: This could mean the PQC signature verification for Fava's Beancount parser (WASM module) failed.
    *   Check your browser's developer console for error messages related to "WASM signature verification" or "Dilithium3".
    *   This could be due to a (very unlikely) corrupted Fava installation, network issues preventing the signature file from loading, or a misconfiguration.
    *   If PQC WASM verification is disabled in Fava's settings, this protection is bypassed.

**Q: How do I update Fava's PQC settings?**
A: Most PQC-related settings should be available in Fava's main options/configuration UI. For very advanced settings, you might need to consult Fava's documentation regarding the `config/fava_crypto_settings.py` file, but direct editing should only be done if you understand the implications.

**Q: What if I forget the passphrase for my PQC-encrypted Beancount file?**
A: Unfortunately, like with GPG-encrypted files, if you lose the passphrase and Fava was using it to derive the PQC keys, your data will be irrecoverable. There is no backdoor. Always store your passphrases securely.

**Q: Will PQC slow down Fava?**
A: PQC operations can be more computationally intensive than some classical algorithms. However, Fava's PQC integration is designed with performance in mind, using efficient libraries and targeting acceptable performance levels for typical user interactions (e.g., file loading, saving, hashing). You generally shouldn't notice prohibitive slowdowns.

**Q: Can I use my existing GPG keys with Fava's new PQC encryption?**
A: No. Fava's PQC encryption uses new PQC algorithms (like Kyber and Dilithium). It is separate from GPG. Fava will continue to *decrypt* your existing GPG-encrypted files, but for new PQC encryption, you'll use Fava's built-in PQC mechanisms, likely with a new passphrase or PQC-specific key files.

---

For further details, please refer to Fava's official documentation and the specific PQC-related documents in the `docs` directory of your Fava installation or the project repository.