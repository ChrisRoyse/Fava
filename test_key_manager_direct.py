#!/usr/bin/env python3
"""
Test key manager directly without going through the package __init__.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_direct_key_manager():
    """Test key manager import and functionality directly."""
    print("Testing direct key manager import...")
    
    try:
        # Import key manager directly 
        from fava.pqc.key_manager import PQCKeyManager
        print("PASS: Key manager imported directly")
        
        # Create minimal config
        config = {
            "wasm_module_integrity": {
                "signature_algorithm": "Dilithium3",
                "key_source": "environment",
                "public_key_env_var": "TEST_PQC_PUBLIC_KEY",
                "private_key_env_var": "TEST_PQC_PRIVATE_KEY",
                "key_rotation_enabled": True,
                "key_rotation_interval_days": 90
            }
        }
        
        # Initialize key manager
        key_manager = PQCKeyManager(config)
        print("PASS: Key manager initialized")
        
        # Test key generation
        public_key, private_key = key_manager.generate_keypair()
        if public_key and private_key:
            print(f"PASS: Keys generated - pub: {len(public_key)}, priv: {len(private_key)}")
            
            # Test validation
            is_valid = key_manager._validate_keypair(public_key, private_key)
            if is_valid:
                print("PASS: Key validation successful")
                return True
            else:
                print("FAIL: Key validation failed")
                return False
        else:
            print("FAIL: Key generation failed")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_direct_key_manager()
    print(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)