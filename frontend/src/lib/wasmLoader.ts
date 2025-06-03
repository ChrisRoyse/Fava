import { getFavaPqcWasmConfig, type PqcWasmConfig } from '../generated/pqcWasmConfig';
import { notifyUIDegradedFunctionality } from './notifications';
import { verifyPqcWasmSignature } from './pqcCrypto';

// WebAssembly is a standard global object in modern JS environments.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const WebAssembly: { instantiate: (bufferSource: ArrayBuffer, importObject?: any) => Promise<{ instance: any, module: any }> };


/**
 * Loads the Beancount WASM parser, performing PQC signature verification if enabled.
 * Based on pseudocode from docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md
 *
 * @returns A Promise that resolves to the WASM module instance's exports (or type unknown) or null if loading/verification fails.
 */
export async function loadBeancountParserWithPQCVerification(): Promise<unknown | null> {
  const config: PqcWasmConfig = getFavaPqcWasmConfig();

  if (!config.pqcWasmVerificationEnabled) {
    console.warn('PQC WASM signature verification is DISABLED via configuration. Loading WASM module directly.');
    try {
      const wasmPath = config.wasmModulePath;
      console.info(`Fetching WASM module (verification disabled): ${wasmPath}`);
      const wasmResponse = await fetch(wasmPath);
      if (!wasmResponse.ok) {
        console.error(`Failed to fetch WASM module (verification disabled): ${wasmPath}. Status: ${String(wasmResponse.status)}`);
        throw new Error('WASM Fetch Failed (verification disabled)');
      }
      const wasmBuffer = await wasmResponse.arrayBuffer();
      // Actual WASM instantiation depends on tree-sitter or the specific WASM module's API
      // For tree-sitter, it's usually: await Parser.init(); const lang = await Parser.Language.load(wasmBuffer);
      // This is a generic placeholder:
      const wasmModule = await WebAssembly.instantiate(wasmBuffer, {});
      console.info(`WASM module loaded directly (PQC verification disabled): ${wasmPath}`);
      // Assuming instance and exports exist on a successfully instantiated module
      return wasmModule.instance.exports;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`Error loading WASM module directly (verification disabled): ${errorMessage}`);
      notifyUIDegradedFunctionality(`WASM module could not be loaded (PQC check disabled): ${errorMessage}`);
      return null;
    }
  }

  console.info(`PQC WASM signature verification is ENABLED. Starting process for: ${config.wasmModulePath}`);
  try {
    const publicKeyBase64 = config.pqcWasmPublicKeyDilithium3Base64;
    if (!publicKeyBase64 || publicKeyBase64 === 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64') {
      console.error('PQC WASM public key is not configured or is a placeholder. Verification cannot proceed.');
      throw new Error('Missing or placeholder PQC Public Key Configuration');
    }

    const wasmPath = config.wasmModulePath;
    const signaturePath = wasmPath + config.wasmSignaturePathSuffix;

    console.info(`Fetching WASM module from: ${wasmPath}`);
    console.info(`Fetching PQC signature from: ${signaturePath}`);
    
    const [wasmResponse, signatureResponse] = await Promise.all([
      fetch(wasmPath),
      fetch(signaturePath),
    ]);

    if (!wasmResponse.ok) {
      console.error(`Failed to fetch WASM module: ${wasmPath}. Status: ${String(wasmResponse.status)}`);
      throw new Error('WASM Module Fetch Failed');
    }
    if (!signatureResponse.ok) {
      console.error(`Failed to fetch PQC signature: ${signaturePath}. Status: ${String(signatureResponse.status)}`);
      throw new Error('PQC Signature Fetch Failed');
    }

    const wasmBuffer = await wasmResponse.arrayBuffer();
    const signatureBuffer = await signatureResponse.arrayBuffer();

    const isSignatureValid = await verifyPqcWasmSignature(
      wasmBuffer,
      signatureBuffer,
      publicKeyBase64,
      config.pqcWasmSignatureAlgorithmName,
    );

    if (isSignatureValid) {
      console.info(`WASM module '${config.wasmModulePath}' signature (${config.pqcWasmSignatureAlgorithmName}) VERIFIED successfully.`);
      // Actual WASM instantiation:
      const wasmModule = await WebAssembly.instantiate(wasmBuffer, {});
      console.info('WASM module instantiated successfully after PQC verification.');
      // Assuming instance and exports exist on a successfully instantiated module
      return wasmModule.instance.exports;
    } else {
      console.error(`WASM module '${config.wasmModulePath}' signature (${config.pqcWasmSignatureAlgorithmName}) verification FAILED. Module will NOT be loaded.`);
      notifyUIDegradedFunctionality(`Beancount parser integrity check failed. Features may be limited.`);
      return null;
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error during PQC-verified WASM loading process: ${errorMessage}`);
    notifyUIDegradedFunctionality(`WASM module loading failed: ${errorMessage}`);
    return null;
  }
}