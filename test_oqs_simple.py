#!/usr/bin/env python3
"""
Test OQS usage patterns to understand the correct API
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_oqs_simple():
    """Test simple OQS usage."""
    try:
        import oqs
        
        print("Testing basic OQS usage...")
        
        # Test with Dilithium3
        with oqs.Signature("Dilithium3") as signer:
            # Generate keypair
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            
            print(f"Keys generated: pub={len(public_key)}, priv={len(private_key)}")
            
            # Test signing
            message = b"Test message"
            signature = signer.sign(message)
            print(f"Signature created: {len(signature)} bytes")
            
            # Test verification - method 1 (with public key as parameter)
            is_valid1 = signer.verify(message, signature, public_key)
            print(f"Verification method 1: {is_valid1}")
            
            return public_key, private_key, signature
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def test_validation_with_new_signer():
    """Test validation with a fresh signer instance."""
    try:
        import oqs
        
        print("\nTesting validation with separate signer instances...")
        
        # Generate keys
        with oqs.Signature("Dilithium3") as signer1:
            public_key = signer1.generate_keypair()
            private_key = signer1.export_secret_key()
            
            message = b"Test validation message"
            signature = signer1.sign(message)
            
        # Verify with new signer
        with oqs.Signature("Dilithium3") as signer2:
            # Method 1: Direct verification with public key
            is_valid = signer2.verify(message, signature, public_key)
            print(f"Direct verification: {is_valid}")
            
            return is_valid
            
    except Exception as e:
        print(f"Error in validation test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    pub, priv, sig = test_oqs_simple()
    if pub and priv:
        result = test_validation_with_new_signer()
        print(f"\nFinal result: {result}")
    else:
        print("Basic test failed")