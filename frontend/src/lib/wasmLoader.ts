import * as pqcConfig from '../generated/pqcWasmConfig';
import * as notifications from './notifications';
import { verifyPqcWasmSignature } from './pqcCrypto';

// Minimal interfaces for web-tree-sitter to avoid 'any' and for test mocking
export interface TreeSitterLanguage {
  /** Nominal property to make this interface non-empty */
  _isTreeSitterLanguage: true;
}

// Type alias for the Parser constructor
type TreeSitterParserConstructor = new () => TreeSitterParserInstance;

interface TreeSitterParserInstance {
  setLanguage(language: TreeSitterLanguage | null): void;
  // Add other methods like parse() if they were to be used by this loader directly
}

interface TreeSitterParserModule {
  init(options?: { locateFile?: (file: string, scriptDirectory: string) => string }): Promise<void>;
  Language: {
    load(buffer: Uint8Array | ArrayBuffer | string): Promise<TreeSitterLanguage>;
  };
  Parser: TreeSitterParserConstructor; // Use the constructor type
}

// Augment the global namespace to inform TypeScript about the global 'Parser' object.
// This is necessary because 'web-tree-sitter' might attach itself to the global scope.
// For tests, this global 'Parser' will be mocked.
declare global {
  // eslint-disable-next-line no-var
  var Parser: TreeSitterParserModule | undefined;
}

/**
 /**
  * Validates if the provided parser object conforms to the TreeSitterParserModule interface.
  * This is crucial for ensuring the global 'Parser' (from web-tree-sitter) is correctly loaded
  * and has the necessary methods and properties before use.
  * @param parser The parser object to validate, typically globalThis.Parser.
  * @returns True if the parser is valid, false otherwise.
  */
 function isValidParserGlobal(parser: typeof globalThis.Parser): parser is TreeSitterParserModule {
   // Check if parser is defined and an object
   if (!parser || typeof parser !== 'object') {
     return false;
   }
   // Check for init method
   if (typeof parser.init !== 'function') {
     return false;
   }
   // Check for Language property: must exist, be an object (and not null), and have a load method
   if (
     typeof parser.Language === 'undefined' || // Must exist
     typeof parser.Language !== 'object' || // Must be an object
     typeof parser.Language.load !== 'function' // Must have load method
   ) {
     return false;
   }
   // Check for Parser constructor (as per TreeSitterParserModule interface)
   // This ensures the Parser property itself is a function (constructor)
   if (typeof parser.Parser !== 'function') {
     return false;
   }
   return true;
 }

/**
 * Loads the Beancount WASM parser, performing PQC signature verification if enabled.
 * Based on pseudocode from docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md
 *
 * @returns A Promise that resolves to the TreeSitterLanguage instance or null if loading/verification fails.
 */
export async function loadBeancountParserWithPQCVerification(
  configOverride?: pqcConfig.PqcWasmConfig
): Promise<TreeSitterLanguage | null> {
  // Get the configuration. If no override, fetch it.
  const configPromise = configOverride
    ? Promise.resolve(configOverride)
    : pqcConfig.getFavaPqcWasmConfig();
  
  const config = await configPromise;

  if (!config.pqcWasmVerificationEnabled) {
    console.warn('PQC WASM signature verification is DISABLED via configuration. Loading WASM module directly.');
    try {
      const wasmPath = config.wasmModulePath;
      console.info(`Fetching WASM module (verification disabled): ${wasmPath}`);
      const wasmResponse = await fetch(wasmPath);
      if (!wasmResponse.ok) {
        const errorDetail = `Status: ${String(wasmResponse.status)}`;
        console.error(`Failed to fetch WASM module (verification disabled): ${wasmPath}. ${errorDetail}`);
        notifications.notifyUIDegradedFunctionality(`WASM module could not be loaded (PQC check disabled): Fetch failed ${errorDetail}`);
        return null; 
      }
      const wasmBuffer = await wasmResponse.arrayBuffer();
      // Actual WASM instantiation using web-tree-sitter
      const CurrentParser = globalThis.Parser;
      // VULN-003: Enhanced validation for globalThis.Parser, now using helper
      if (!isValidParserGlobal(CurrentParser)) {
        console.error('Tree-sitter Parser global is not correctly configured, not an object, or essential methods/properties are missing.');
        notifications.notifyUIDegradedFunctionality('Parser initialization failed (PQC check disabled).');
        return null;
      }
      await CurrentParser.init();
      const language = await CurrentParser.Language.load(wasmBuffer);
      return language;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`Error loading WASM module directly (verification disabled): ${errorMessage}`);
      notifications.notifyUIDegradedFunctionality(`WASM module could not be loaded (PQC check disabled): ${errorMessage}`);
      return null;
    }
  }

  console.info(`PQC WASM signature verification is ENABLED. Starting process for: ${config.wasmModulePath}`);
  try {
    const publicKeyBase64 = config.pqcWasmPublicKeyDilithium3Base64;
    if (!publicKeyBase64 || publicKeyBase64 === 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64') {
      const errorDetail = 'Missing or placeholder PQC Public Key';
      console.error(`PQC WASM public key is not configured or is a placeholder. Verification cannot proceed. Detail: ${errorDetail}`);
      notifications.notifyUIDegradedFunctionality(`WASM module loading failed: ${errorDetail}`);
      return null; 
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
      const errorDetail = `WASM Fetch Status: ${String(wasmResponse.status)}`;
      console.error(`Failed to fetch WASM module: ${wasmPath}. ${errorDetail}`);
      notifications.notifyUIDegradedFunctionality(`WASM module loading failed: ${errorDetail}`);
      return null; 
    }
    if (!signatureResponse.ok) {
      const errorDetail = `Signature Fetch Status: ${String(signatureResponse.status)}`;
      console.error(`Failed to fetch PQC signature: ${signaturePath}. ${errorDetail}`);
      notifications.notifyUIDegradedFunctionality(`WASM module loading failed: ${errorDetail}`);
      return null; 
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
      // Actual WASM instantiation using web-tree-sitter
      const CurrentParser = globalThis.Parser;
      // VULN-003: Enhanced validation for globalThis.Parser (repeated for verified load path), now using helper
      if (!isValidParserGlobal(CurrentParser)) {
        console.error('Tree-sitter Parser global is not correctly configured, not an object, or essential methods/properties are missing for verified load.');
        notifications.notifyUIDegradedFunctionality('Parser initialization failed post-verification.');
        return null;
      }
      await CurrentParser.init();
      const language = await CurrentParser.Language.load(wasmBuffer);
      console.info('WASM module instantiated successfully after PQC verification.');
      return language;
    } else {
      console.error(`WASM module '${config.wasmModulePath}' signature (${config.pqcWasmSignatureAlgorithmName}) verification FAILED. Module will NOT be loaded.`);
      notifications.notifyUIDegradedFunctionality(`Beancount parser integrity check failed. Features may be limited.`);
      return null;
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error during PQC-verified WASM loading process: ${errorMessage}`);
    notifications.notifyUIDegradedFunctionality(`WASM module loading failed: ${errorMessage}`);
    return null;
  }
}