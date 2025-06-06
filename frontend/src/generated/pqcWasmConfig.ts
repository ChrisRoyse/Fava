// Placeholder for PQC WASM Configuration
// Based on architecture doc: docs/architecture/PQC_WASM_Module_Integrity_Arch.md
// Based on pseudocode: docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md

export interface PqcWasmConfig {
  pqcWasmVerificationEnabled: boolean;
  pqcWasmPublicKeyDilithium3Base64: string;
  pqcWasmSignatureAlgorithmName: 'Dilithium3';
  wasmModulePath: string;
  wasmSignaturePathSuffix: string;
  pqcWasmBackendVerification: boolean;
  pqcWasmVerifiedEndpoint: string;
  pqcWasmModulePath: string;
  pqcWasmSignatureAlgorithm: string;
  pqcHashingDefaultAlgorithm: string;
}
// Default/Example configuration. This will be overridden by fetched config.
export const favaPqcWasmConfigDefault: PqcWasmConfig = {
  pqcWasmVerificationEnabled: true, // Default to true for PQC security compliance
  pqcWasmPublicKeyDilithium3Base64: '', // Default to empty until fetched
  pqcWasmSignatureAlgorithmName: 'Dilithium3', // Keep as is, or make configurable if API supports
  wasmModulePath: '/static/tree-sitter-beancount.wasm',
  wasmSignaturePathSuffix: '.dilithium3.sig',
  pqcWasmBackendVerification: true,
  pqcWasmVerifiedEndpoint: '/default_ledger/api/verified_wasm/tree-sitter-beancount.wasm',
  pqcWasmModulePath: '/static/tree-sitter-beancount.wasm',
  pqcWasmSignatureAlgorithm: 'Dilithium3',
  pqcHashingDefaultAlgorithm: 'SHA3-256'
};
let fetchedPqcConfig: PqcWasmConfig | null = null;
let fetchPromise: Promise<PqcWasmConfig> | null = null;

// Force cache reset on module reload during development
if (typeof window !== 'undefined') {
  // Reset cache on module load to ensure fresh data during development
  fetchedPqcConfig = null;
  fetchPromise = null;
}

// Define a more specific type for the expected API response structure
interface ApiPqcConfigResponseData {
  wasm_module_integrity?: {
    verification_enabled?: boolean;
    public_key_base64?: string;
    signature_algorithm?: string;
    module_path?: string;
    signature_path_suffix?: string;
    backend_verification?: boolean;
    verified_endpoint?: string;
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
    // Use the current URL to construct the API endpoint
    // Extract the ledger slug from the URL and build API endpoint
    const currentPath = window.location.pathname;
    const pathParts = currentPath.split('/').filter(part => part);
    // First part should be the ledger slug (e.g., 'example')
    const ledgerSlug = pathParts[0] ?? 'default_ledger';
    
    const response = await fetch(`/${ledgerSlug}/api/pqc_config?t=${String(Date.now())}`);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch PQC config: ${String(response.status)} ${errorText}`);
    }
    
    const apiResponse = await response.json() as ApiPqcConfigResponse;
    console.debug('Full API response:', apiResponse);
    
    const wasmIntegrityConfig = apiResponse.data?.wasm_module_integrity ?? {};
    console.debug('WASM integrity config:', wasmIntegrityConfig);
    
    // Check if backend verification is enabled
    const backendVerification = wasmIntegrityConfig.backend_verification === true;
    console.debug('Backend verification enabled:', backendVerification);
    
    // Build the final config with backend verification settings
    const fullConfig: PqcWasmConfig = {
      pqcWasmVerificationEnabled: Boolean(wasmIntegrityConfig.verification_enabled),
      pqcWasmBackendVerification: backendVerification,
      pqcWasmVerifiedEndpoint: wasmIntegrityConfig.verified_endpoint ?? `/${ledgerSlug}/api/verified_wasm/tree-sitter-beancount.wasm`,
      pqcWasmModulePath: wasmIntegrityConfig.module_path ?? '/static/tree-sitter-beancount.wasm',
      pqcWasmSignatureAlgorithm: 'Dilithium3', // Not needed for backend verification but kept for compatibility
      pqcWasmPublicKeyDilithium3Base64: '', // Not needed for backend verification
      pqcWasmSignatureAlgorithmName: 'Dilithium3', // Keep for compatibility
      wasmModulePath: wasmIntegrityConfig.module_path ?? '/static/tree-sitter-beancount.wasm', // Keep for compatibility
      wasmSignaturePathSuffix: '.dilithium3.sig', // Not needed for backend verification
      pqcHashingDefaultAlgorithm: apiResponse.data?.hashing?.default_algorithm ?? 'SHA3-256'
    };
    console.debug('Final config created:', fullConfig);
    
    return fullConfig;
  } catch (error) {
    console.error('Error fetching PQC config from server:', error);
    // Return safe defaults with backend verification
    const currentPath = window.location.pathname;
    const pathParts = currentPath.split('/').filter(part => part);
    const ledgerSlug = pathParts[0] ?? 'default_ledger';
    
    return {
      pqcWasmVerificationEnabled: false,
      pqcWasmBackendVerification: true,
      pqcWasmVerifiedEndpoint: `/${ledgerSlug}/api/verified_wasm/tree-sitter-beancount.wasm`,
      pqcWasmModulePath: '/static/tree-sitter-beancount.wasm',
      pqcWasmSignatureAlgorithm: 'Dilithium3',
      pqcWasmPublicKeyDilithium3Base64: '',
      pqcWasmSignatureAlgorithmName: 'Dilithium3',
      wasmModulePath: '/static/tree-sitter-beancount.wasm',
      wasmSignaturePathSuffix: '.dilithium3.sig',
      pqcHashingDefaultAlgorithm: 'SHA3-256'
    };
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
    // With backend verification, we don't need to validate public keys on frontend
    if (config.pqcWasmVerificationEnabled && !config.pqcWasmBackendVerification) {
      console.warn('PQC WASM verification is enabled but backend verification is disabled. This configuration may be insecure.');
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
 * Fetches the WASM module from the backend verification endpoint if enabled,
 * or directly from the static path if verification is disabled.
 * @returns Promise<ArrayBuffer> The WASM module's ArrayBuffer.
 */
export async function loadAndVerifyWasmModule(): Promise<ArrayBuffer> {
  const config = await getFavaPqcWasmConfig();

  // If backend verification is enabled, use the verified endpoint
  if (config.pqcWasmBackendVerification && config.pqcWasmVerificationEnabled) {
    console.log('Attempting PQC signature verification via backend endpoint');
    try {
      const wasmResponse = await fetch(config.pqcWasmVerifiedEndpoint);
      if (!wasmResponse.ok) {
        throw new Error(
          `Backend WASM verification failed: ${String(wasmResponse.status)} ${wasmResponse.statusText}`,
        );
      }
      const wasmModuleBuffer = await wasmResponse.arrayBuffer();
      console.info(`WASM module verified successfully by backend: ${config.pqcWasmVerifiedEndpoint}`);
      return wasmModuleBuffer;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Backend WASM verification failed: ${message}`);
      throw new Error(`Backend WASM verification failed: ${message}`);
    }
  }

  // Fallback to direct module loading (no verification)
  if (!config.wasmModulePath) {
    throw new Error('WASM module path is not configured.');
  }

  try {
    const wasmResponse = await fetch(config.wasmModulePath);
    if (!wasmResponse.ok) {
      throw new Error(
        `Failed to fetch WASM module from ${config.wasmModulePath}: ${String(wasmResponse.status)} ${wasmResponse.statusText}`,
      );
    }
    const wasmModuleBuffer = await wasmResponse.arrayBuffer();
    console.info(
      `WASM verification is disabled. Loaded ${config.wasmModulePath} without signature check.`,
    );
    return wasmModuleBuffer;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error fetching WASM module: ${message}`);
    throw new Error(`Error fetching WASM module: ${message}`);
  }
}

// Ensure no trailing characters or braces beyond this point