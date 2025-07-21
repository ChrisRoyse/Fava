#!/usr/bin/env python3
"""
Debug OQS secret key assignment
"""

try:
    import oqs
    
    print("Testing OQS secret key assignment...")
    
    # Generate a keypair first
    with oqs.Signature("Dilithium3") as signer1:
        public_key = signer1.generate_keypair()
        private_key = signer1.export_secret_key()
        
        print(f"Generated keys: pub={len(public_key)}, priv={len(private_key)}")
        print(f"Private key type: {type(private_key)}")
        print(f"Private key first 20 bytes: {private_key[:20].hex()}")
        
        # Test signing with the original signer
        message = b"test message"
        signature = signer1.sign(message)
        print(f"Original signer signature: {len(signature)} bytes")
    
    # Now try to use the exported private key with a new signer
    print("\nTesting secret key assignment...")
    with oqs.Signature("Dilithium3") as signer2:
        try:
            # Try direct assignment
            print("Attempting direct assignment...")
            signer2.secret_key = private_key
            print("Secret key assigned successfully")
            
            # Try signing
            signature2 = signer2.sign(message)
            print(f"New signer signature: {len(signature2)} bytes")
            
            # Try verification
            is_valid = signer2.verify(message, signature2, public_key)
            print(f"Verification result: {is_valid}")
            
        except Exception as e:
            print(f"Error with secret key assignment: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
    
    # Try alternative approach - check what attributes are available
    print("\nChecking available attributes...")
    with oqs.Signature("Dilithium3") as signer3:
        attrs = [attr for attr in dir(signer3) if not attr.startswith('_')]
        print(f"Available attributes: {attrs}")
        
        # Check if there's a different way to import keys
        if hasattr(signer3, 'import_secret_key'):
            print("Found import_secret_key method")
        if hasattr(signer3, 'load_secret_key'):
            print("Found load_secret_key method")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()