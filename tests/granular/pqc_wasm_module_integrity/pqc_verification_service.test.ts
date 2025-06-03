// tests/granular/pqc_wasm_module_integrity/pqc_verification_service.test.ts
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { verifyPqcWasmSignature } from '../../../frontend/src/lib/pqcCrypto';
import type { IOqsGlobal, IOqsSignatureInstance } from '../../../frontend/src/lib/pqcOqsInterfaces';

// Mock OQS and atob globally for all tests in this suite
const mockOqsVerify = vi.fn<(...args: unknown[]) => Promise<boolean>>();
const mockOqsSignatureInstance: IOqsSignatureInstance = {
  verify: mockOqsVerify,
};

// Helper to create ArrayBuffer from string
function strToArrayBuffer(str: string): ArrayBuffer {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

describe('PqcVerificationService', () => {
  let originalOQS: IOqsGlobal | undefined;
  const validTestKey1 = "SGVsbG8sIFdvcmxkIQ=="; // "Hello, World!"
  const decodedTestKey1 = "Hello, World!";
  const validTestKey2 = "Vml0ZXN0IFRlc3Qh";   // "Vitest Test!" - Note: Base64 of "Vitest Test!" is Vml0ZXN0IFRlc3Qh not Vml0ZXN0IFRlc3QhAA== unless padding is strictly enforced by encoder
  const decodedTestKey2 = "Vitest Test!";
  const invalidBase64TestKey = "bad!"; // Intended to fail atob
  const emptyBase64Key = ""; // For testing empty key scenario

  beforeEach(() => {
    originalOQS = globalThis.OQS as IOqsGlobal | undefined; // Store before stubbing
    const mockOQSGlobal: IOqsGlobal = {
      Signature: vi.fn(() => mockOqsSignatureInstance),
    };
    vi.stubGlobal('OQS', mockOQSGlobal);
    vi.stubGlobal('atob', (b64Encoded: string) => {
      if (b64Encoded === validTestKey1) {
        return decodedTestKey1;
      }
      if (b64Encoded === validTestKey2) {
        return decodedTestKey2;
      }
      if (b64Encoded === invalidBase64TestKey) {
        throw new DOMException('Failed to execute \'atob\' on \'Window\': The string to be decoded contains characters outside of the Latin1 range.', 'InvalidCharacterError');
      }
      if (b64Encoded === emptyBase64Key) {
        return ""; // atob of empty string is empty string
      }
      // Fallback for any other non-empty string to catch unexpected test values.
      // This indicates a test setup issue if reached with an unexpected key.
      console.warn(`Mock atob received unexpected input: ${b64Encoded}`);
      throw new DOMException(`Mock atob received unexpected input: ${b64Encoded}`, 'InvalidCharacterError');
    });
    mockOqsVerify.mockReset();
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
    globalThis.OQS = originalOQS; // Restore OQS after each test
  });

  describe('verifyPqcWasmSignature', () => {
    test('PWMI_TC_PVS_001: Valid Dilithium3 signature returns true', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature');
      const publicKeyBase64 = validTestKey1;
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(true);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(true);
      expect(globalThis.OQS?.Signature).toHaveBeenCalledWith(algorithmName);
      expect(mockOqsVerify).toHaveBeenCalledWith(
        new Uint8Array(wasmBuffer),
        new Uint8Array(signatureBuffer),
        new Uint8Array(strToArrayBuffer(decodedTestKey1))
      );
      expect(console.info).toHaveBeenCalledWith('PQC signature VERIFIED successfully for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_002: Invalid Dilithium3 signature returns false', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('invalid signature');
      const publicKeyBase64 = validTestKey1;
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(false);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith('PQC signature verification FAILED for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_003: Tampered WASM (valid signature) returns false', async () => {
      const wasmBuffer = strToArrayBuffer('tampered wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature for original content');
      const publicKeyBase64 = validTestKey1;
      const algorithmName = 'Dilithium3';
      
      mockOqsVerify.mockResolvedValue(false);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith('PQC signature verification FAILED for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_004: Wrong public key returns false', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature');
      const publicKeyBase64 = validTestKey2;
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(false); // Assuming verify fails with wrong key

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(mockOqsVerify).toHaveBeenCalledWith(
        new Uint8Array(wasmBuffer),
        new Uint8Array(signatureBuffer),
        new Uint8Array(strToArrayBuffer(decodedTestKey2))
      );
    });

    test('PWMI_TC_PVS_005: Unsupported algorithm returns false and logs error', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = validTestKey1; // Use a valid key format for this part
      const algorithmName = 'UnsupportedAlgo';

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Unsupported PQC algorithm specified for WASM verification: UnsupportedAlgo');
    });

    test('PWMI_TC_PVS_006: Public key decoding failure returns false and logs error', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = invalidBase64TestKey; 
      const algorithmName = 'Dilithium3';

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      // The error message comes from the new Base64 validation logic
      expect(console.error).toHaveBeenCalledWith('Invalid Base64 format detected for string.');
    });

    test('PWMI_TC_PVS_007: PQC library verifier initialization failure returns false', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = validTestKey1; // Use a valid key format
      const algorithmName = 'Dilithium3';

      const brokenMockOQSGlobal: IOqsGlobal = {
        Signature: vi.fn(() => { throw new Error("Cannot construct Signature"); }) // Simulate constructor failure
      };
      vi.stubGlobal('OQS', brokenMockOQSGlobal);


      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Failed to instantiate OQS.Signature for Dilithium3: Cannot construct Signature');
    });

    test('PWMI_TC_PVS_008: OQS verify method throws exception', async () => {
      const wasmBufferLocal = strToArrayBuffer('valid wasm content'); 
      const signatureBufferLocal = strToArrayBuffer('valid signature'); 
      const publicKeyBase64Local = validTestKey1; // Use a valid key format
      const algorithmNameLocal = 'Dilithium3'; 

      mockOqsVerify.mockRejectedValue(new Error('OQS Verify Error'));

      const result = await verifyPqcWasmSignature(wasmBufferLocal, signatureBufferLocal, publicKeyBase64Local, algorithmNameLocal);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Exception during PQC signature verification: OQS Verify Error');
    });

    // New test for empty base64 key after validation
    test('PWMI_TC_PVS_009: Empty Base64 string after validation returns false', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = emptyBase64Key; // atob('') is '', length 0
      const algorithmName = 'Dilithium3';
    
      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      // Empty string "" fails the length check first in decodeBase64ToUint8Array
      expect(console.error).toHaveBeenCalledWith('Base64 string length (current: 0) out of acceptable range (1-8192).');
    });
  });
});