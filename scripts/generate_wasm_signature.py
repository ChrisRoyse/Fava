#!/usr/bin/env python3
"""
Script to generate Dilithium3 signatures for WASM files.
This ensures cryptographic integrity of WebAssembly modules in the PQC-enhanced Fava.
"""

import base64
import sys
from pathlib import Path

# Add the src directory to Python path so we can import fava modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import oqs
    if not oqs.is_sig_enabled("Dilithium3"):
        raise ImportError("Dilithium3 signature algorithm is not enabled in liboqs")
except ImportError as e:
    print(f"Error: Could not import OQS library or Dilithium3 not available: {e}")
    print("Make sure liboqs-python is installed: pip install liboqs-python")
    sys.exit(1)


def generate_keypair_and_sign_wasm(wasm_file_path: str, output_dir: str = None) -> tuple[str, str, str]:
    """
    Generate a Dilithium3 keypair and sign the WASM file.
    
    Args:
        wasm_file_path: Path to the WASM file to sign
        output_dir: Directory to save signature file (defaults to same as WASM file)
    
    Returns:
        Tuple of (public_key_base64, private_key_base64, signature_file_path)
    """
    wasm_path = Path(wasm_file_path)
    if not wasm_path.exists():
        raise FileNotFoundError(f"WASM file not found: {wasm_file_path}")
    
    # Generate Dilithium3 keypair using liboqs
    print("Generating Dilithium3 keypair...")
    with oqs.Signature("Dilithium3") as signer:
        public_key = signer.generate_keypair()
        private_key = signer.export_secret_key()
        
        # Read WASM file
        print(f"Reading WASM file: {wasm_file_path}")
        wasm_data = wasm_path.read_bytes()
        
        # Sign the WASM file
        print("Signing WASM file with Dilithium3...")
        signature = signer.sign(wasm_data)
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = wasm_path.parent
        
        # Save signature file
        signature_file_path = output_path / f"{wasm_path.name}.dilithium3.sig"
        signature_file_path.write_bytes(signature)
        print(f"Signature saved to: {signature_file_path}")
        
        # Encode keys as base64 for configuration
        public_key_base64 = base64.b64encode(public_key).decode('ascii')
        private_key_base64 = base64.b64encode(private_key).decode('ascii')
    
    return public_key_base64, private_key_base64, str(signature_file_path)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python generate_wasm_signature.py <wasm_file_path> [output_dir]")
        print("Example: python generate_wasm_signature.py src/fava/static/tree-sitter-beancount.wasm")
        sys.exit(1)
    
    wasm_file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        public_key_b64, private_key_b64, sig_file = generate_keypair_and_sign_wasm(wasm_file_path, output_dir)
        
        print("\n" + "="*80)
        print("SUCCESS: WASM signature generated!")
        print("="*80)
        print(f"WASM file: {wasm_file_path}")
        print(f"Signature file: {sig_file}")
        print(f"Public key (base64): {public_key_b64[:50]}...")
        print(f"Private key (base64): {private_key_b64[:50]}...")
        print("\n" + "="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("1. Update config/fava_crypto_settings.py:")
        print(f'   "public_key_base64": "{public_key_b64}"')
        print("\n2. SECURELY STORE the private key for future re-signing if needed")
        print("3. The signature file has been created and will be served by Fava")
        print("4. WASM verification is now enabled and will protect against tampering")
        print("="*80)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 