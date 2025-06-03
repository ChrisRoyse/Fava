// Declaration file for 'js-sha3'
// This provides type information to TypeScript when @types/js-sha3 is not available.

declare module 'js-sha3' {
  /**
   * Calculates the SHA3-256 hash of the input data.
   * @param data The data to hash. Can be a Uint8Array, ArrayBuffer, or a string.
   * @returns The hexadecimal string representation of the hash.
   */
  export function sha3_256(data: Uint8Array | ArrayBuffer | string): string;

  // Add declarations for other functions from 'js-sha3' if they are used elsewhere.
  // For example:
  // export function keccak256(data: Uint8Array | ArrayBuffer | string): string;
  // export function shake128(data: Uint8Array | ArrayBuffer | string, outputBits: number): string;
  // export function shake256(data: Uint8Array | ArrayBuffer | string, outputBits: number): string;
}