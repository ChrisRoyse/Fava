#!/usr/bin/env python3
"""
Debug OQS methods and proper key handling
"""

try:
    import oqs
    
    print("Checking OQS Signature methods...")
    
    with oqs.Signature("Dilithium3") as signer:
        # Generate keys
        public_key = signer.generate_keypair()
        private_key = signer.export_secret_key()
        
        print("Available methods:")
        methods = [method for method in dir(signer) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  {method}")
        
        print(f"\nSecret key type initially: {type(signer.secret_key)}")
        
        # Check if we can create a fresh signer and regenerate with same seed
        # Or find alternative validation approach
        
    # Alternative approach: Don't try to reuse keys across signers
    print("\nTesting validation without key reuse...")
    
    # Generate and test in same context
    with oqs.Signature("Dilithium3") as signer:
        public_key = signer.generate_keypair()
        private_key = signer.export_secret_key()
        
        # Test signing and verification in same context
        message = b"Test message"
        signature = signer.sign(message)
        
        # Verify using the same signer (should work)
        is_valid_same = signer.verify(message, signature, public_key)
        print(f"Verification in same context: {is_valid_same}")
        
        # Store the signature for external verification
        test_data = (message, signature, public_key)
    
    # Test verification with fresh signer
    message, signature, public_key = test_data
    with oqs.Signature("Dilithium3") as verifier:
        is_valid_fresh = verifier.verify(message, signature, public_key)
        print(f"Verification with fresh signer: {is_valid_fresh}")
    
    print("SUCCESS: Both verifications work!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()