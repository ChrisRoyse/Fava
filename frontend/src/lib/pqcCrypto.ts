// @ts-expect-error: OQS is an external library (liboqs-js) and will be globally available.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const OQS: any; // Declaration for liboqs-js global object

/**
 * Decodes a Base64 string to a Uint8Array.
 * @param base64String The Base64 encoded string.
 * @returns A Uint8Array containing the decoded bytes, or null if decoding fails.
 */
function decodeBase64ToUint8Array(base64String: string): Uint8Array | null {
  try {
    const binaryString = atob(base64String);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  } catch (error) {
    console.error('Base64 decoding failed:', error);
    return null;
  }
}

/**
 * Verifies the PQC signature of a WASM module.
 * Based on pseudocode from docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md
 *
 * @param wasmBuffer ArrayBuffer containing the binary data of the WASM module.
 * @param signatureBuffer ArrayBuffer containing the PQC signature of the WASM module.
 * @param publicKeyBase64 String containing the Base64 encoded PQC public key.
 * @param algorithmName String specifying the PQC algorithm to use (e.g., "Dilithium3").
 * @returns Promise<boolean> TRUE if the signature is valid, FALSE otherwise.
 */
export async function verifyPqcWasmSignature(
  wasmBuffer: ArrayBuffer,
  signatureBuffer: ArrayBuffer,
  publicKeyBase64: string,
  algorithmName: string,
): Promise<boolean> {
  console.info(`Attempting PQC signature verification. Algorithm: ${algorithmName}`);

  if (algorithmName !== 'Dilithium3') {
    console.error(`Unsupported PQC algorithm specified for WASM verification: ${algorithmName}`);
    return false;
  }

  try {
    // This assumes OQS.Signature is available and works as described.
    // Actual liboqs-js usage might differ and require async initialization.
    const pqcVerifier = new OQS.Signature(algorithmName);
    if (!pqcVerifier) { // Basic check, library might throw instead
      console.error(`Failed to obtain/initialize PQC verifier for algorithm: ${algorithmName}`);
      return false;
    }

    const publicKeyBytes = decodeBase64ToUint8Array(publicKeyBase64);
    if (!publicKeyBytes || publicKeyBytes.length === 0) {
      console.error('PQC public key decoding failed or resulted in an empty key.');
      return false;
    }

    const messageBytes = new Uint8Array(wasmBuffer);
    const signatureBytes = new Uint8Array(signatureBuffer);

    // The OQS.Signature.verify method is assumed to be async based on typical JS crypto libs
    const isVerified: boolean = await pqcVerifier.verify(messageBytes, signatureBytes, publicKeyBytes);

    if (isVerified) {
      console.info(`PQC signature VERIFIED successfully for algorithm: ${algorithmName}`);
    } else {
      console.warn(`PQC signature verification FAILED for algorithm: ${algorithmName}`);
    }
    return isVerified;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Exception during PQC signature verification: ${errorMessage}`);
    return false;
  }
}