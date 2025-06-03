// frontend/src/lib/pqcOqsInterfaces.ts

/**
 * Interface for the signature instance returned by OQS.Signature constructor.
 */
export interface IOqsSignatureInstance {
  /**
   * Verifies a signature against a message and public key.
   * @param messageBytes The message that was signed.
   * @param signatureBytes The signature to verify.
   * @param publicKeyBytes The public key to use for verification.
   * @returns A promise that resolves to true if the signature is valid, false otherwise.
   */
  verify(
    messageBytes: Uint8Array,
    signatureBytes: Uint8Array,
    publicKeyBytes: Uint8Array
  ): Promise<boolean>;
}

/**
 * Type alias for the OQS.Signature constructor.
 */
export type IOqsSignatureConstructor = new (
  algorithmName: string
) => IOqsSignatureInstance;

/**
 * Interface for the global OQS object.
 */
export interface IOqsGlobal {
  Signature: IOqsSignatureConstructor;
}

/**
 * Declares the global OQS variable.
 * This assumes that 'liboqs-js' or a similar library will provide this global.
 * For testing, this global is mocked.
 * For runtime, ensure liboqs-js is loaded and makes OQS available globally.
 */
declare global {
  // eslint-disable-next-line no-var
  var OQS: IOqsGlobal | undefined;
}

// Export an empty object to make this a module, which is good practice
// and helps avoid potential issues with global scope in some bundlers.
export {};