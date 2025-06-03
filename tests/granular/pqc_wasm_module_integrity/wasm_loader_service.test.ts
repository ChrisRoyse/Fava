import { describe, test, expect, vi, beforeEach, afterEach, type Mocked } from 'vitest';
import { loadBeancountParserWithPQCVerification } from '../../../frontend/src/lib/wasmLoader';
import type { TreeSitterLanguage } from '../../../frontend/src/lib/wasmLoader'; // Type-only import
// Import pqcCrypto for type annotations if needed, but we will mock it.
import type * as PqcCryptoTypes from '../../../frontend/src/lib/pqcCrypto';
// Import the module to be mocked
import * as pqcConfigModuleActual from '../../../frontend/src/generated/pqcWasmConfig';
import * as notificationsModule from '../../../frontend/src/lib/notifications';

// Use vi.hoisted to define the mock function
const { mockVerifyPqcWasmSignatureFn } = vi.hoisted(() => {
  return { mockVerifyPqcWasmSignatureFn: vi.fn<typeof PqcCryptoTypes.verifyPqcWasmSignature>() };
});

// Mock the pqcCrypto module, referencing the hoisted mock
vi.mock('../../../frontend/src/lib/pqcCrypto', () => {
  return {
    verifyPqcWasmSignature: mockVerifyPqcWasmSignatureFn,
  };
});

// Minimal mock for TreeSitterLanguage
import type { PqcWasmConfig as PqcWasmConfigTypeActual } from '../../../frontend/src/generated/pqcWasmConfig';


// Minimal mock for TreeSitterLanguage
const mockTreeSitterLanguage: TreeSitterLanguage = { _isTreeSitterLanguage: true };

// Corrected valid test key for loader service tests
const validTestKeyForLoader = "SGVsbG8sIFdvcmxkIQ=="; // "Hello, World!"

// Mock PqcWasmConfig
const mockGoodConfig: PqcWasmConfigTypeActual = {
  pqcWasmVerificationEnabled: true,
  pqcWasmPublicKeyDilithium3Base64: validTestKeyForLoader,
  pqcWasmSignatureAlgorithmName: 'Dilithium3' as const,
  wasmModulePath: '/assets/tree-sitter-beancount.wasm',
  wasmSignaturePathSuffix: '.dilithium3.sig',
};

const mockDisabledConfig: PqcWasmConfigTypeActual = { ...mockGoodConfig, pqcWasmVerificationEnabled: false };
const mockMissingKeyConfig: PqcWasmConfigTypeActual = { ...mockGoodConfig, pqcWasmPublicKeyDilithium3Base64: '' };
const mockPlaceholderKeyConfig: PqcWasmConfigTypeActual = { ...mockGoodConfig, pqcWasmPublicKeyDilithium3Base64: 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64' };


// Mock global fetch
const mockFetch = vi.fn();

// Mock web-tree-sitter Parser module
const mockParserLanguageLoad = vi.fn();
const mockParserInit = vi.fn();
const mockTreeSitterParserInstance = {
  setLanguage: vi.fn(),
};

const mockParserModule = {
  init: mockParserInit,
  Language: {
    load: mockParserLanguageLoad,
  },
  Parser: vi.fn(() => mockTreeSitterParserInstance),
};

// const verifyPqcWasmSignatureSpy = vi.spyOn(pqcCrypto, 'verifyPqcWasmSignature'); // No longer needed due to vi.mock
const notifyUIDegradedFunctionalityMock = vi.fn();

// Helper to create ArrayBuffer
function strToArrayBuffer(str: string): ArrayBuffer {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}
const mockWasmBuffer = strToArrayBuffer('wasm_content');
const mockSignatureBuffer = strToArrayBuffer('signature_content');
const decodedValidTestKeyForLoader = "Hello, World!"; // Corresponds to validTestKeyForLoader

describe('WasmLoaderService', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch);
    vi.stubGlobal('Parser', mockParserModule as any);
    // Add atob mock for wasm_loader_service.test.ts
    vi.stubGlobal('atob', (b64Encoded: string) => {
      if (b64Encoded === validTestKeyForLoader) {
        return decodedValidTestKeyForLoader;
      }
      if (b64Encoded === 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64') {
        // Placeholder key used in mockPlaceholderKeyConfig
        return "decoded_placeholder_key"; // Needs to be decodable for the test path
      }
      if (b64Encoded === '') { // For mockMissingKeyConfig
        return "";
      }
      // Fallback to catch unexpected keys during tests
      console.warn(`WasmLoaderService mock atob received unexpected input: ${b64Encoded}`);
      throw new DOMException(`WasmLoaderService mock atob received unexpected input: ${b64Encoded}`, 'InvalidCharacterError');
    });
    
    mockParserInit.mockReset().mockResolvedValue(undefined);
    mockParserLanguageLoad.mockReset().mockResolvedValue(mockTreeSitterLanguage);
    mockParserModule.Parser.mockClear();
    (mockParserModule.Parser as Mocked<typeof mockParserModule.Parser>).mockImplementation(() => mockTreeSitterParserInstance);

    mockVerifyPqcWasmSignatureFn.mockReset(); // Reset the mock function via the outer variable
    notifyUIDegradedFunctionalityMock.mockReset();
    // Ensure the spy is on the actual imported module's function
    vi.spyOn(notificationsModule, 'notifyUIDegradedFunctionality').mockImplementation(notifyUIDegradedFunctionalityMock);
    mockFetch.mockReset();

    // Default successful mocks
    mockFetch.mockImplementation(async (path: string) => {
      if (path === mockGoodConfig.wasmModulePath) {
        return { ok: true, arrayBuffer: async () => mockWasmBuffer };
      }
      if (path === mockGoodConfig.wasmModulePath + mockGoodConfig.wasmSignaturePathSuffix) {
        return { ok: true, arrayBuffer: async () => mockSignatureBuffer };
      }
      return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
    });
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('loadBeancountParserWithPQCVerification', () => {
    test('PWMI_TC_WLS_001: Verification enabled, valid sig: loads WASM', async () => {
      mockVerifyPqcWasmSignatureFn.mockResolvedValue(true);

      const result = await loadBeancountParserWithPQCVerification(mockGoodConfig);
      expect(result).toEqual(mockTreeSitterLanguage);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockVerifyPqcWasmSignatureFn).toHaveBeenCalledWith(
        mockWasmBuffer,
        mockSignatureBuffer,
        mockGoodConfig.pqcWasmPublicKeyDilithium3Base64,
        mockGoodConfig.pqcWasmSignatureAlgorithmName,
      );
      expect(mockParserInit).toHaveBeenCalledTimes(1);
      expect(mockParserLanguageLoad).toHaveBeenCalledWith(mockWasmBuffer);
      expect(notifyUIDegradedFunctionalityMock).not.toHaveBeenCalled();
      expect(console.info).toHaveBeenCalledWith(expect.stringContaining('VERIFIED successfully'));
    });

    test('PWMI_TC_WLS_002: Verification enabled, invalid sig: fails, notifies UI', async () => {
      const localMockGoodConfig = { ...mockGoodConfig }; // Ensure a fresh config object for this test
      mockVerifyPqcWasmSignatureFn.mockResolvedValue(false);

      const result = await loadBeancountParserWithPQCVerification(localMockGoodConfig);
      expect(result).toBeNull();
      expect(mockFetch).toHaveBeenCalledTimes(2); // Check if fetches happened
      expect(mockVerifyPqcWasmSignatureFn).toHaveBeenCalled();
      expect(mockParserLanguageLoad).not.toHaveBeenCalled();
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('integrity check failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('verification FAILED'));
    });

    test('PWMI_TC_WLS_003: Verification disabled: loads WASM if successful, otherwise notifies', async () => {
      
      // Scenario 1: Successful load
      mockParserInit.mockResolvedValueOnce(undefined); // Ensure fresh mock for this call
      mockParserLanguageLoad.mockResolvedValueOnce(mockTreeSitterLanguage); // Ensure fresh mock
      
      let result = await loadBeancountParserWithPQCVerification(mockDisabledConfig);
      expect(result).toEqual(mockTreeSitterLanguage);
      expect(mockVerifyPqcWasmSignatureFn).not.toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(mockDisabledConfig.wasmModulePath);
      expect(mockParserInit).toHaveBeenCalledTimes(1);
      expect(mockParserLanguageLoad).toHaveBeenCalledWith(mockWasmBuffer);
      expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('verification is DISABLED'));
      expect(notifyUIDegradedFunctionalityMock).not.toHaveBeenCalled();

      // Reset for Scenario 2
      mockFetch.mockClear(); // Clear call counts for fetch
      mockParserInit.mockClear(); // Clear call counts
      mockParserLanguageLoad.mockClear(); // Clear call counts
      notifyUIDegradedFunctionalityMock.mockClear(); // Clear call counts for notification spy
      (console.warn as Mocked<typeof console.warn>).mockClear(); // Clear console.warn spy

      // Scenario 2: Parser.init fails
      mockParserInit.mockRejectedValueOnce(new Error('Parser Init Failed'));
      result = await loadBeancountParserWithPQCVerification(mockDisabledConfig); // Call again, pass config
      expect(result).toBeNull();
      // Check that the specific notification for this error path is called
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('WASM module could not be loaded (PQC check disabled): Parser Init Failed'));
    });

    test('PWMI_TC_WLS_004: WASM file fetch fail: fails, notifies UI', async () => {
      mockFetch.mockImplementation(async (path: string) => {
        if (path === mockGoodConfig.wasmModulePath) {
          return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) }; // This mock will cause the failure
        }
        return { ok: true, arrayBuffer: async () => mockSignatureBuffer };
      });

      const result = await loadBeancountParserWithPQCVerification(mockGoodConfig);
      expect(result).toBeNull();
      // The error message comes from the 'enabled' path now, as config is good.
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed: WASM Fetch Status: 404'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining(`Failed to fetch WASM module: ${mockGoodConfig.wasmModulePath}. WASM Fetch Status: 404`));
      expect(mockVerifyPqcWasmSignatureFn).not.toHaveBeenCalled();
    });

    test('PWMI_TC_WLS_005: Signature file fetch fail: fails, notifies UI', async () => {
      mockFetch.mockImplementation(async (path: string) => {
        if (path === mockGoodConfig.wasmModulePath) {
          return { ok: true, arrayBuffer: async () => mockWasmBuffer };
        }
        if (path === mockGoodConfig.wasmModulePath + mockGoodConfig.wasmSignaturePathSuffix) {
          return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
        }
        return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
      });
      
      const result = await loadBeancountParserWithPQCVerification(mockGoodConfig);
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed: Signature Fetch Status: 404'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining(`Failed to fetch PQC signature: ${mockGoodConfig.wasmModulePath + mockGoodConfig.wasmSignaturePathSuffix}. Signature Fetch Status: 404`));
      expect(mockVerifyPqcWasmSignatureFn).not.toHaveBeenCalled();
    });

    test('PWMI_TC_WLS_006a: Missing public key config (empty string): fails, notifies UI', async () => {
      
      const result = await loadBeancountParserWithPQCVerification(mockMissingKeyConfig);
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed: Missing or placeholder PQC Public Key'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('PQC WASM public key is not configured or is a placeholder. Verification cannot proceed. Detail: Missing or placeholder PQC Public Key'));
      expect(mockFetch).not.toHaveBeenCalled();
    });
    
    test('PWMI_TC_WLS_006b: Placeholder public key config: fails, notifies UI', async () => {
      
      const result = await loadBeancountParserWithPQCVerification(mockPlaceholderKeyConfig);
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed: Missing or placeholder PQC Public Key'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('PQC WASM public key is not configured or is a placeholder. Verification cannot proceed. Detail: Missing or placeholder PQC Public Key'));
      expect(mockFetch).not.toHaveBeenCalled();
    }); // End of PWMI_TC_WLS_006b

    test('PWMI_TC_WLS_007: PQC lib init fail (verifyPqcWasmSignature throws): fails, notifies UI', async () => { // Start of PWMI_TC_WLS_007
      mockVerifyPqcWasmSignatureFn.mockImplementation(async () => {
        throw new Error('PQC Lib Init Error');
      });

      const result = await loadBeancountParserWithPQCVerification(mockGoodConfig);
      // This test expects verifyPqcWasmSignatureSpy to throw an error.
      // The SUT catches this and logs it, then notifies.
      expect(result).toBeNull();
      // Corrected expected message based on wasmLoader.ts's catch block
      expect(notifyUIDegradedFunctionalityMock).toHaveBeenCalledWith(
        `WASM module loading failed: PQC Lib Init Error`
      );
      expect(console.error).toHaveBeenCalledWith(
        `Error during PQC-verified WASM loading process: PQC Lib Init Error`
      );
    });
  });
});