import { sha3_256 } from 'js-sha3';
// The global OQS object is declared in pqcOqsInterfaces.ts
// We will access it directly inside the function to ensure test stubs are picked up.

// Type for the hashing part of the PQC config from the API
interface PqcHashingConfig {
  default_algorithm?: string;
}

// Cache for the fetched hashing configuration
let fetchedHashingConfig: PqcHashingConfig | null = null;
let hashingConfigFetchPromise: Promise<PqcHashingConfig> | null = null;

async function fetchHashingConfig(): Promise<PqcHashingConfig> {
  if (fetchedHashingConfig) {
    return fetchedHashingConfig;
  }
  if (hashingConfigFetchPromise) {
    return hashingConfigFetchPromise;
  }

  hashingConfigFetchPromise = (async () => {
    try {
      const bfileSlugFromGlobal = (window as { FAVA_BEANCUNT_FILE_SLUG?: string }).FAVA_BEANCUNT_FILE_SLUG;
      const bfileSlug = bfileSlugFromGlobal ?? "default_ledger";
      const response = await fetch(`/${bfileSlug}/api/pqc_config`);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch PQC hashing config: ${String(response.status)} ${errorText}`);
      }
      const apiResponse = await response.json() as { data?: { hashing?: PqcHashingConfig } };
      if (apiResponse.data?.hashing) { // Used optional chaining here
        fetchedHashingConfig = apiResponse.data.hashing;
        return fetchedHashingConfig;
      }
      console.warn('PQC hashing config not found in API response. Using fallback.');
      fetchedHashingConfig = { default_algorithm: 'SHA256' }; // Fallback
      return fetchedHashingConfig;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error('Error fetching PQC hashing config:', message);
      fetchedHashingConfig = { default_algorithm: 'SHA256' }; // Fallback
      return fetchedHashingConfig;
    } finally {
      hashingConfigFetchPromise = null;
    }
  })();
  return hashingConfigFetchPromise;
}


/**
 * Decodes a Base64 string to a Uint8Array.
 * @param base64String The Base64 encoded string.
 * @returns A Uint8Array containing the decoded bytes, or null if decoding fails.
 */
function decodeBase64ToUint8Array(base64String: string): Uint8Array | null {
  // Validate Base64 format (VULN-002)
  // Regex allows for optional padding and ensures string length is a multiple of 4.
  if (!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(base64String)) {
    console.error('Invalid Base64 format detected for string.');
    return null;
  }

  // Validate length constraints (VULN-002)
  const MAX_BASE64_LENGTH = 8192; // Approx 6KB decoded
  if (base64String.length === 0 || base64String.length > MAX_BASE64_LENGTH) {
    console.error(`Base64 string length (current: ${String(base64String.length)}) out of acceptable range (1-${String(MAX_BASE64_LENGTH)}).`);
    return null;
  }

  try {
    const binaryString = atob(base64String); // This can throw if chars are not in Base64 alphabet
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  } catch (decodingError) {
    const message = decodingError instanceof Error ? decodingError.message : String(decodingError);
    console.error(`Base64 decoding failed (atob error or other): ${message}`);
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
    const CurrentOQS = globalThis.OQS; // Access global OQS here

    // VULN-003: Enhanced validation for globalThis.OQS
    if (
      !CurrentOQS || // This already covers null and undefined
      typeof CurrentOQS !== 'object' ||
      typeof CurrentOQS.Signature !== 'function'
    ) {
      console.error('OQS library is not available, not an object, or OQS.Signature constructor is missing globally.');
      return false;
    }
    
    let pqcVerifier;
    try {
      pqcVerifier = new CurrentOQS.Signature(algorithmName);
    } catch (e) {
      const constructorError = e instanceof Error ? e.message : String(e);
      console.error(`Failed to instantiate OQS.Signature for ${algorithmName}: ${constructorError}`);
      return false;
    }

    if (typeof pqcVerifier.verify !== 'function') {
      console.error(`Failed to obtain/initialize PQC verifier for algorithm: ${algorithmName}, or verifier is invalid.`);
      return false;
    }

    const publicKeyBytes = decodeBase64ToUint8Array(publicKeyBase64);
    if (!publicKeyBytes) { 
      console.error('PQC public key decoding failed or resulted in a null key.');
      return false;
    }
    if (publicKeyBytes.length === 0) {
        console.error('PQC public key decoding resulted in an empty key.');
        return false;
    }

    const messageBytes = new Uint8Array(wasmBuffer);
    const signatureBytes = new Uint8Array(signatureBuffer);

    const isVerified: boolean = await pqcVerifier.verify(
      messageBytes,
      signatureBytes,
      publicKeyBytes,
    );

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

/**
 * Calculates the hash of a string using the backend-configured algorithm.
 * @param data The string data to hash.
 * @returns A Promise that resolves to the hex-encoded hash string, or null on error.
 */
export async function calculateConfiguredHash(data: string): Promise<string | null> {
    try {
      const config = await fetchHashingConfig();
      const algorithm = (config.default_algorithm ?? 'SHA256').toUpperCase();
  
      if (typeof data !== 'string') {
        console.error('Invalid input: data to hash must be a string.');
        return null;
      }
      
      const encoder = new TextEncoder();
      const dataBytes = encoder.encode(data);
  
      let hashHex: string;
  
      switch (algorithm) {
        case 'SHA3-256':
          // Assuming js-sha3 is correctly installed and imported
          hashHex = sha3_256(dataBytes);
          break;
        case 'SHA256': { // Added block scope for lexical declaration
          const hashBuffer = await crypto.subtle.digest('SHA-256', dataBytes);
          hashHex = Array.from(new Uint8Array(hashBuffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
          break;
        }
        default:
          console.error(`Unsupported hashing algorithm configured: ${algorithm}`);
          return null;
      }
      return hashHex;
    } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error calculating configured hash: ${errorMessage}`);
    return null;
  }
}