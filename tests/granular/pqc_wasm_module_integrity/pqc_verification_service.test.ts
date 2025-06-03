// tests/granular/pqc_wasm_module_integrity/pqc_verification_service.test.ts
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { verifyPqcWasmSignature } from '../../../frontend/src/lib/pqcCrypto';

// @ts-expect-error: OQS is an external library (liboqs-js) and will be globally available at runtime.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const OQS: any;

// Mock OQS and atob globally for all tests in this suite
const mockOqsVerify = vi.fn();
const mockOqsSignatureInstance = {
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
  beforeEach(() => {
    vi.stubGlobal('OQS', {
      Signature: vi.fn(() => mockOqsSignatureInstance),
    });
    vi.stubGlobal('atob', (b64Encoded: string) => {
      if (b64Encoded === 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID' || b64Encoded === 'anotherValidKey') {
        return 'decodedPublicKey'; // Dummy decoded string
      }
      if (b64Encoded === 'bad!') {
        throw new Error('Invalid base64 string');
      }
      return '';
    });
    mockOqsVerify.mockReset();
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('verifyPqcWasmSignature', () => {
    test('PWMI_TC_PVS_001: Valid Dilithium3 signature returns true', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(true);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(true);
      expect(OQS.Signature).toHaveBeenCalledWith(algorithmName);
      expect(mockOqsVerify).toHaveBeenCalledWith(
        new Uint8Array(wasmBuffer),
        new Uint8Array(signatureBuffer),
        new Uint8Array(strToArrayBuffer('decodedPublicKey'))
      );
      expect(console.info).toHaveBeenCalledWith('PQC signature VERIFIED successfully for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_002: Invalid Dilithium3 signature returns false', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('invalid signature');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(false);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith('PQC signature verification FAILED for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_003: Tampered WASM (valid signature) returns false', async () => {
      const wasmBuffer = strToArrayBuffer('tampered wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature for original content');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'Dilithium3';
      
      mockOqsVerify.mockResolvedValue(false);

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.warn).toHaveBeenCalledWith('PQC signature verification FAILED for algorithm: Dilithium3');
    });

    test('PWMI_TC_PVS_004: Wrong public key returns false', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature');
      const publicKeyBase64 = 'anotherValidKey';
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockResolvedValue(false); // Assuming verify fails with wrong key

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(mockOqsVerify).toHaveBeenCalledWith(
        new Uint8Array(wasmBuffer),
        new Uint8Array(signatureBuffer),
        new Uint8Array(strToArrayBuffer('decodedPublicKey')) // from 'anotherValidKey'
      );
    });

    test('PWMI_TC_PVS_005: Unsupported algorithm returns false and logs error', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'UnsupportedAlgo';

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Unsupported PQC algorithm specified for WASM verification: UnsupportedAlgo');
    });

    test('PWMI_TC_PVS_006: Public key decoding failure returns false and logs error', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = 'bad!'; // Invalid Base64
      const algorithmName = 'Dilithium3';

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('PQC public key decoding failed or resulted in an empty key.');
    });

    test('PWMI_TC_PVS_007: PQC library verifier initialization failure returns false', async () => {
      const wasmBuffer = strToArrayBuffer('wasm content');
      const signatureBuffer = strToArrayBuffer('signature');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'Dilithium3';

      // Override global OQS for this specific test
      const originalOQS = globalThis.OQS;
      // @ts-expect-error: Intentionally breaking OQS for this test
      globalThis.OQS = { Signature: vi.fn(() => null) };


      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Failed to obtain/initialize PQC verifier for algorithm: Dilithium3');
      
      globalThis.OQS = originalOQS; // Restore OQS
    });
     test('PWMI_TC_PVS_008: OQS verify method throws exception', async () => {
      const wasmBuffer = strToArrayBuffer('valid wasm content');
      const signatureBuffer = strToArrayBuffer('valid signature');
      const publicKeyBase64 = 'REPLACE_WITH_ACTUAL_DILITHIUM3_PUBLIC_KEY_BASE64_VALID';
      const algorithmName = 'Dilithium3';

      mockOqsVerify.mockRejectedValue(new Error('OQS Verify Error'));

      const result = await verifyPqcWasmSignature(wasmBuffer, signatureBuffer, publicKeyBase64, algorithmName);
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Exception during PQC signature verification: OQS Verify Error');
    });
  });
});