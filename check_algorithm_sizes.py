#!/usr/bin/env python3
"""
Check actual algorithm parameter sizes in this environment.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_kyber768_sizes():
    """Check actual Kyber768 parameter sizes."""
    try:
        import oqs
        
        with oqs.KeyEncapsulation("Kyber768") as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()
            
            # Test encapsulation to get ciphertext size
            ciphertext, shared_secret = kem.encap_secret(public_key)
            
            logger.info("Kyber768 actual sizes:")
            logger.info(f"  Public key: {len(public_key)} bytes")
            logger.info(f"  Private key: {len(private_key)} bytes")
            logger.info(f"  Ciphertext: {len(ciphertext)} bytes")
            logger.info(f"  Shared secret: {len(shared_secret)} bytes")
            
            return {
                "public_key_length": len(public_key),
                "secret_key_length": len(private_key),
                "ciphertext_length": len(ciphertext),
                "shared_secret_length": len(shared_secret)
            }
            
    except Exception as e:
        logger.error(f"Failed to check Kyber768 sizes: {e}")
        return None


def check_dilithium3_sizes():
    """Check actual Dilithium3 parameter sizes."""
    try:
        import oqs
        
        with oqs.Signature("Dilithium3") as signer:
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            
            # Test signing to get signature size
            message = b"test message"
            signature = signer.sign(message)
            
            logger.info("Dilithium3 actual sizes:")
            logger.info(f"  Public key: {len(public_key)} bytes")
            logger.info(f"  Private key: {len(private_key)} bytes")
            logger.info(f"  Signature: {len(signature)} bytes")
            
            return {
                "public_key_length": len(public_key),
                "secret_key_length": len(private_key),
                "signature_length": len(signature)
            }
            
    except Exception as e:
        logger.error(f"Failed to check Dilithium3 sizes: {e}")
        return None


if __name__ == "__main__":
    logger.info("Checking algorithm parameter sizes in this environment...")
    
    kyber_sizes = check_kyber768_sizes()
    dilithium_sizes = check_dilithium3_sizes()
    
    if kyber_sizes:
        print(f"\nKyber768 sizes for updating code:")
        print(f"'public_key_length': {kyber_sizes['public_key_length']},")
        print(f"'secret_key_length': {kyber_sizes['secret_key_length']},")
        print(f"'ciphertext_length': {kyber_sizes['ciphertext_length']},")
        print(f"'shared_secret_length': {kyber_sizes['shared_secret_length']}")
    
    if dilithium_sizes:
        print(f"\nDilithium3 sizes for updating code:")
        print(f"'public_key_length': {dilithium_sizes['public_key_length']},")
        print(f"'secret_key_length': {dilithium_sizes['secret_key_length']},")
        print(f"'signature_length': {dilithium_sizes['signature_length']}")