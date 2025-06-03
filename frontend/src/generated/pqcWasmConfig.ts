// Placeholder for PQC WASM Configuration
// Based on architecture doc: docs/architecture/PQC_WASM_Module_Integrity_Arch.md
// Based on pseudocode: docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md

import { verifyPqcWasmSignature } from '../lib/pqcCrypto'; // Added import

export interface PqcWasmConfig {
  pqcWasmVerificationEnabled: boolean;
  pqcWasmPublicKeyDilithium3Base64: string;
  pqcWasmSignatureAlgorithmName: 'Dilithium3'; // Currently fixed
  wasmModulePath: string;
  wasmSignaturePathSuffix: string;
}
// Default/Example configuration. This will be overridden by fetched config.
export const favaPqcWasmConfigDefault: PqcWasmConfig = {
  pqcWasmVerificationEnabled: false, // Default to false until fetched
  pqcWasmPublicKeyDilithium3Base64: '', // Default to empty until fetched
  pqcWasmSignatureAlgorithmName: 'Dilithium3', // Keep as is, or make configurable if API supports
  wasmModulePath: '/assets/tree-sitter-beancount.wasm',
  wasmSignaturePathSuffix: '.dilithium3.sig',
};
let fetchedPqcConfig: PqcWasmConfig | null = null;
let fetchPromise: Promise<PqcWasmConfig> | null = null;

// Define a more specific type for the expected API response structure
interface ApiPqcConfigResponseData {
  wasm_module_integrity?: {
    verification_enabled?: boolean;
    public_key_base64?: string;
    signature_algorithm?: string;
    module_path?: string;
    signature_path_suffix?: string;
  };
  hashing?: {
    default_algorithm?: string;
  };
  // Add other expected top-level config keys if necessary
}

interface ApiPqcConfigResponse {
  data?: ApiPqcConfigResponseData;
  // mtime?: string; // If mtime is also part of the response
}


async function fetchPqcConfigFromServer(): Promise<PqcWasmConfig> {
  try {
    // Acknowledge FAVA_BEANCUNT_FILE_SLUG might not be standard on window
    // Consider a more robust way to get this if possible, e.g., from a global store or script tag data
    const bfileSlugFromGlobal = (window as { FAVA_BEANCUNT_FILE_SLUG?: string }).FAVA_BEANCUNT_FILE_SLUG;
    const bfileSlug = bfileSlugFromGlobal ?? "default_ledger";
    
    const response = await fetch(`/${bfileSlug}/api/pqc_config`);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch PQC config: ${String(response.status)} ${errorText}`);
    }
    
    const apiResponse = await response.json() as ApiPqcConfigResponse;

    if (apiResponse.data?.wasm_module_integrity) { // apiResponse itself is not optional here
        const wasmIntegrityConf = apiResponse.data.wasm_module_integrity;
        const fullConfig: PqcWasmConfig = {
            pqcWasmVerificationEnabled: wasmIntegrityConf.verification_enabled ?? favaPqcWasmConfigDefault.pqcWasmVerificationEnabled,
            pqcWasmPublicKeyDilithium3Base64: wasmIntegrityConf.public_key_base64 ?? favaPqcWasmConfigDefault.pqcWasmPublicKeyDilithium3Base64,
            pqcWasmSignatureAlgorithmName: wasmIntegrityConf.signature_algorithm === 'Dilithium3' ? 'Dilithium3' : favaPqcWasmConfigDefault.pqcWasmSignatureAlgorithmName,
            wasmModulePath: wasmIntegrityConf.module_path ?? favaPqcWasmConfigDefault.wasmModulePath,
            wasmSignaturePathSuffix: wasmIntegrityConf.signature_path_suffix ?? favaPqcWasmConfigDefault.wasmSignaturePathSuffix,
        };
        if (!fullConfig.pqcWasmPublicKeyDilithium3Base64 && fullConfig.pqcWasmVerificationEnabled) {
            console.warn('PQC WASM verification enabled but no public key fetched from API. Using defaults, which might be insecure.');
        }
        return fullConfig;
    } else {
      console.warn('PQC config fetched from API is missing wasm_module_integrity section or data. Using defaults.');
      return favaPqcWasmConfigDefault;
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error fetching PQC config from server: ${message}`);
    return favaPqcWasmConfigDefault; // Fallback to default on error
  }
}


export async function getFavaPqcWasmConfig(): Promise<PqcWasmConfig> {
  if (fetchedPqcConfig) {
    return fetchedPqcConfig;
  }
  if (fetchPromise) {
    return fetchPromise;
  }

  fetchPromise = fetchPqcConfigFromServer().then(config => {
    fetchedPqcConfig = config;
    if (config.pqcWasmVerificationEnabled && (config.pqcWasmPublicKeyDilithium3Base64 === '' || config.pqcWasmPublicKeyDilithium3Base64 === 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64')) {
      console.error('PQC WASM verification is enabled, but a valid public key was not fetched or is a placeholder. WASM integrity checks may fail or be insecure.');
    }
    return config;
  }).catch((error: unknown) => { // Explicitly type error as unknown
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Failed to initialize PQC WASM config, using defaults: ${message}`);
    fetchedPqcConfig = favaPqcWasmConfigDefault;
    return favaPqcWasmConfigDefault;
  }).finally(() => {
    fetchPromise = null;
  });

  return fetchPromise;
}
// End of getFavaPqcWasmConfig

// Function to allow resetting for tests or re-fetching if necessary
export function resetPqcWasmConfigCache(): void {
  fetchedPqcConfig = null;
  fetchPromise = null;
}

/**
 * Fetches the WASM module and its signature, verifies the signature if enabled,
 * and returns the WASM module as an ArrayBuffer.
 * Throws an error if verification is enabled and fails, or if fetching fails.
 * @returns Promise<ArrayBuffer> The WASM module's ArrayBuffer.
 */
export async function loadAndVerifyWasmModule(): Promise<ArrayBuffer> {
  const config = await getFavaPqcWasmConfig();

  if (!config.wasmModulePath) {
    throw new Error('WASM module path is not configured.');
  }

  // Fetch the WASM module
  let wasmModuleBuffer: ArrayBuffer;
  try {
    const wasmResponse = await fetch(config.wasmModulePath);
    if (!wasmResponse.ok) {
      throw new Error(
        `Failed to fetch WASM module from ${config.wasmModulePath}: ${String(wasmResponse.status)} ${wasmResponse.statusText}`,
      );
    }
    wasmModuleBuffer = await wasmResponse.arrayBuffer();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error fetching WASM module: ${message}`);
    throw new Error(`Error fetching WASM module: ${message}`);
  }

  if (config.pqcWasmVerificationEnabled) {
    if (!config.pqcWasmPublicKeyDilithium3Base64) {
      console.error('WASM verification enabled, but no public key is configured.');
      throw new Error('WASM verification failed: Public key not configured.');
    }
    if (!config.wasmSignaturePathSuffix) {
        console.error('WASM verification enabled, but signature path suffix is not configured.');
        throw new Error('WASM verification failed: Signature path suffix not configured.');
    }

    const signaturePath = config.wasmModulePath + config.wasmSignaturePathSuffix;
    let signatureBuffer: ArrayBuffer;
    try {
      const signatureResponse = await fetch(signaturePath);
      if (!signatureResponse.ok) {
        throw new Error(
          `Failed to fetch WASM signature from ${signaturePath}: ${String(signatureResponse.status)} ${signatureResponse.statusText}`,
        );
      }
      signatureBuffer = await signatureResponse.arrayBuffer();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Error fetching WASM signature: ${message}`);
      throw new Error(`Error fetching WASM signature: ${message}`);
    }

    const isVerified = await verifyPqcWasmSignature(
      wasmModuleBuffer,
      signatureBuffer,
      config.pqcWasmPublicKeyDilithium3Base64,
      config.pqcWasmSignatureAlgorithmName,
    );

    if (!isVerified) {
      console.error(
        `WASM module signature verification failed for ${config.wasmModulePath}`,
      );
      throw new Error(
        `WASM module signature verification failed for ${config.wasmModulePath}`,
      );
    }
    console.info(
      `WASM module ${config.wasmModulePath} verified successfully.`,
    );
  } else {
    console.info(
      `WASM verification is disabled. Loading ${config.wasmModulePath} without signature check.`,
    );
  }

  return wasmModuleBuffer;
}

// Ensure no trailing characters or braces beyond this point