import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { loadBeancountParserWithPQCVerification } from '../../../frontend/src/lib/wasmLoader';
import * as pqcCrypto from '../../../frontend/src/lib/pqcCrypto';
import * as pqcConfig from '../../../frontend/src/generated/pqcWasmConfig';
import * as notifications from '../../../frontend/src/lib/notifications';

// Mock PqcWasmConfig
const mockGoodConfig = {
  pqcWasmVerificationEnabled: true,
  pqcWasmPublicKeyDilithium3Base64: 'VALID_PUBLIC_KEY_BASE64',
  pqcWasmSignatureAlgorithmName: 'Dilithium3' as const,
  wasmModulePath: '/assets/tree-sitter-beancount.wasm',
  wasmSignaturePathSuffix: '.dilithium3.sig',
};

const mockDisabledConfig = { ...mockGoodConfig, pqcWasmVerificationEnabled: false };
const mockMissingKeyConfig = { ...mockGoodConfig, pqcWasmPublicKeyDilithium3Base64: '' };
const mockPlaceholderKeyConfig = { ...mockGoodConfig, pqcWasmPublicKeyDilithium3Base64: 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64' };


// Mock global fetch
const mockFetch = vi.fn();
// Mock WebAssembly.instantiate
const mockWasmInstantiate = vi.fn();

// Spy on service functions
const verifyPqcWasmSignatureSpy = vi.spyOn(pqcCrypto, 'verifyPqcWasmSignature');
const getFavaPqcWasmConfigSpy = vi.spyOn(pqcConfig, 'getFavaPqcWasmConfig');
const notifyUIDegradedFunctionalitySpy = vi.spyOn(notifications, 'notifyUIDegradedFunctionality');

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
const mockWasmInstanceExports = { beancountParser: () => 'parsed' };


describe('WasmLoaderService', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch);
    vi.stubGlobal('WebAssembly', { instantiate: mockWasmInstantiate });
    
    verifyPqcWasmSignatureSpy.mockReset();
    getFavaPqcWasmConfigSpy.mockReset();
    notifyUIDegradedFunctionalitySpy.mockReset();
    mockFetch.mockReset();
    mockWasmInstantiate.mockReset();

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
    mockWasmInstantiate.mockResolvedValue({ instance: { exports: mockWasmInstanceExports } });
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('loadBeancountParserWithPQCVerification', () => {
    test('PWMI_TC_WLS_001: Verification enabled, valid sig: loads WASM', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockGoodConfig);
      verifyPqcWasmSignatureSpy.mockResolvedValue(true);

      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toEqual(mockWasmInstanceExports);
      expect(getFavaPqcWasmConfigSpy).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(verifyPqcWasmSignatureSpy).toHaveBeenCalledWith(
        mockWasmBuffer,
        mockSignatureBuffer,
        mockGoodConfig.pqcWasmPublicKeyDilithium3Base64,
        mockGoodConfig.pqcWasmSignatureAlgorithmName
      );
      expect(mockWasmInstantiate).toHaveBeenCalledWith(mockWasmBuffer, {});
      expect(notifyUIDegradedFunctionalitySpy).not.toHaveBeenCalled();
      expect(console.info).toHaveBeenCalledWith(expect.stringContaining('VERIFIED successfully'));
    });

    test('PWMI_TC_WLS_002: Verification enabled, invalid sig: fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockGoodConfig);
      verifyPqcWasmSignatureSpy.mockResolvedValue(false);

      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(verifyPqcWasmSignatureSpy).toHaveBeenCalled();
      expect(mockWasmInstantiate).not.toHaveBeenCalled();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('integrity check failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('verification FAILED'));
    });

    test('PWMI_TC_WLS_003: Verification disabled: loads WASM, bypasses verification', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockDisabledConfig);

      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toEqual(mockWasmInstanceExports);
      expect(verifyPqcWasmSignatureSpy).not.toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(mockDisabledConfig.wasmModulePath);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Only wasm, not signature
      expect(mockWasmInstantiate).toHaveBeenCalledWith(mockWasmBuffer, {});
      expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('verification is DISABLED'));
    });

    test('PWMI_TC_WLS_004: WASM file fetch fail: fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockGoodConfig);
      mockFetch.mockImplementation(async (path: string) => {
        if (path === mockGoodConfig.wasmModulePath) {
          return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
        }
        return { ok: true, arrayBuffer: async () => mockSignatureBuffer }; // Sig fetch ok
      });

      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('WASM Module Fetch Failed'));
      expect(verifyPqcWasmSignatureSpy).not.toHaveBeenCalled();
    });

    test('PWMI_TC_WLS_005: Signature file fetch fail: fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockGoodConfig);
      mockFetch.mockImplementation(async (path: string) => {
        if (path === mockGoodConfig.wasmModulePath) {
          return { ok: true, arrayBuffer: async () => mockWasmBuffer }; // Wasm fetch ok
        }
        if (path === mockGoodConfig.wasmModulePath + mockGoodConfig.wasmSignaturePathSuffix) {
          return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
        }
        return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
      });
      
      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('PQC Signature Fetch Failed'));
      expect(verifyPqcWasmSignatureSpy).not.toHaveBeenCalled();
    });

    test('PWMI_TC_WLS_006a: Missing public key config (empty string): fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockMissingKeyConfig);
      
      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('Missing or placeholder PQC Public Key Configuration'));
      expect(mockFetch).not.toHaveBeenCalled();
    });
    
    test('PWMI_TC_WLS_006b: Placeholder public key config: fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockPlaceholderKeyConfig);
      
      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed'));
      expect(console.error).toHaveBeenCalledWith(expect.stringContaining('Missing or placeholder PQC Public Key Configuration'));
      expect(mockFetch).not.toHaveBeenCalled();
    });

    test('PWMI_TC_WLS_007: PQC lib init fail (verifyPqcWasmSignature throws): fails, notifies UI', async () => {
      getFavaPqcWasmConfigSpy.mockReturnValue(mockGoodConfig);
      verifyPqcWasmSignatureSpy.mockRejectedValue(new Error('PQC Lib Init Error'));

      const result = await loadBeancountParserWithPQCVerification();
      expect(result).toBeNull();
      expect(notifyUIDegradedFunctionalitySpy).toHaveBeenCalledWith(expect.stringContaining('WASM module loading failed: PQC Lib Init Error'));
      expect(console.error).toHaveBeenCalledWith('Error during PQC-verified WASM loading process: PQC Lib Init Error');
    });
  });
});