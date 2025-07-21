#!/usr/bin/env python3
"""
PQC Key Setup Script for Fava

This script helps administrators set up PQC keys for Fava deployments.
It supports different deployment scenarios and key storage options.

Usage:
    python setup_pqc_keys.py --help
    python setup_pqc_keys.py --key-source environment
    python setup_pqc_keys.py --key-source file --key-path /etc/fava/keys
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from fava.pqc.key_manager import PQCKeyManager
    from fava.pqc.global_config import GlobalConfig
    from fava.pqc.configuration_validator import validate_full_pqc_configuration, get_configuration_recommendations
    from fava.pqc.audit_logger import audit_security_event
except ImportError as e:
    print(f"Error: Failed to import Fava PQC modules: {e}")
    print("Make sure you're running this script from the Fava directory with PQC modules installed.")
    sys.exit(1)


def print_banner():
    """Print the setup banner."""
    print("=" * 70)
    print("         Fava PQC Key Setup Script")
    print("         Post-Quantum Cryptography Key Management")
    print("=" * 70)
    print()


def load_config(config_path: str) -> dict:
    """Load the crypto configuration."""
    try:
        return GlobalConfig.get_crypto_settings(config_path)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def validate_config(config: dict) -> bool:
    """Validate the configuration and show recommendations."""
    print("Validating PQC configuration...")
    
    errors = validate_full_pqc_configuration(config)
    recommendations = get_configuration_recommendations(config)
    
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    
    print("✓ Configuration validation passed")
    
    if recommendations:
        print("\nSecurity recommendations:")
        for rec in recommendations:
            print(f"  ⚠ {rec}")
    
    return True


def setup_environment_keys(config: dict) -> bool:
    """Set up keys using environment variables."""
    print("Setting up PQC keys using environment variables...")
    
    try:
        key_manager = PQCKeyManager(config)
        
        # Generate new keypair
        print("Generating new keypair...")
        public_key, private_key = key_manager.generate_keypair()
        
        # Store in environment variables
        print("Storing keys in environment variables...")
        key_manager.store_keypair(public_key, private_key)
        
        # Show environment variables
        wasm_config = config.get('wasm_module_integrity', {})
        public_env_var = wasm_config.get('public_key_env_var', 'FAVA_PQC_PUBLIC_KEY')
        private_env_var = wasm_config.get('private_key_env_var', 'FAVA_PQC_PRIVATE_KEY')
        
        print(f"\n✓ Keys generated and stored in environment variables:")
        print(f"  Public key: {public_env_var}")
        print(f"  Private key: {private_env_var}")
        
        print(f"\nTo use these keys, export them in your shell:")
        print(f"  export {public_env_var}='{os.environ.get(public_env_var)}'")
        print(f"  export {private_env_var}='{os.environ.get(private_env_var)}'")
        
        print(f"\nOr add them to your environment file (.env, systemd service, etc.)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to set up environment keys: {e}")
        return False


def setup_file_keys(config: dict, key_path: str) -> bool:
    """Set up keys using file storage."""
    print(f"Setting up PQC keys using file storage in {key_path}...")
    
    # Update config with the specified path
    config['wasm_module_integrity']['key_file_path'] = key_path
    
    try:
        key_manager = PQCKeyManager(config)
        
        # Generate new keypair
        print("Generating new keypair...")
        public_key, private_key = key_manager.generate_keypair()
        
        # Store in files
        print(f"Storing keys in {key_path}...")
        key_manager.store_keypair(public_key, private_key)
        
        # Show file locations
        algorithm = config.get('wasm_module_integrity', {}).get('signature_algorithm', 'Dilithium3')
        public_file = Path(key_path) / f"public_key.{algorithm.lower()}"
        private_file = Path(key_path) / f"private_key.{algorithm.lower()}"
        
        print(f"\n✓ Keys generated and stored:")
        print(f"  Public key: {public_file}")
        print(f"  Private key: {private_file}")
        
        # Check file permissions
        if os.name != 'nt':  # Unix-like systems
            public_perms = oct(public_file.stat().st_mode)[-3:]
            private_perms = oct(private_file.stat().st_mode)[-3:]
            print(f"\nFile permissions:")
            print(f"  Public key: {public_perms} (should be 644)")
            print(f"  Private key: {private_perms} (should be 600)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to set up file keys: {e}")
        return False


def test_keys(config: dict) -> bool:
    """Test that the generated keys work correctly."""
    print("\nTesting generated keys...")
    
    try:
        key_manager = PQCKeyManager(config)
        
        # Test key loading
        print("  Testing key loading...")
        public_key = key_manager.load_public_key()
        private_key = key_manager.load_private_key()
        print("  ✓ Keys loaded successfully")
        
        # Test key validation
        print("  Testing key validation...")
        is_valid = key_manager.validate_keys()
        if is_valid:
            print("  ✓ Key validation passed")
        else:
            print("  ✗ Key validation failed")
            return False
        
        # Show key info
        key_info = key_manager.get_key_info()
        print(f"\nKey Information:")
        print(f"  Algorithm: {key_info['algorithm']}")
        print(f"  Key Source: {key_info['key_source']}")
        print(f"  Public Key Size: {key_info['public_key_size']} bytes")
        print(f"  Private Key Size: {key_info['private_key_size']} bytes")
        print(f"  Public Key Hash: {key_info['public_key_hash']}")
        print(f"  Status: {key_info['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Key testing failed: {e}")
        return False


def show_next_steps(key_source: str):
    """Show next steps after key setup."""
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    
    if key_source == "environment":
        print("1. Set the environment variables in your deployment environment")
        print("2. Restart your Fava application")
        print("3. Verify PQC functionality with: fava pqc validate")
    elif key_source == "file":
        print("1. Ensure the key files are accessible by your Fava application")
        print("2. Update your Fava configuration to use file-based keys")
        print("3. Restart your Fava application")
        print("4. Verify PQC functionality with: fava pqc validate")
    
    print("\nSecurity Reminders:")
    print("- Keep private keys secure and backed up")
    print("- Consider setting up key rotation (enabled by default)")
    print("- Monitor audit logs for key management events")
    print("- Test your backup and recovery procedures")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Set up PQC keys for Fava deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --key-source environment
  %(prog)s --key-source file --key-path /etc/fava/keys
  %(prog)s --key-source file --key-path ./keys --config my_config.py
        """
    )
    
    parser.add_argument(
        "--key-source",
        choices=["environment", "file"],
        required=True,
        help="Where to store the generated keys"
    )
    
    parser.add_argument(
        "--key-path",
        type=str,
        help="Path for file-based key storage (required for --key-source file)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to crypto settings configuration file"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing keys without asking"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration, don't generate keys"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.key_source == "file" and not args.key_path:
        parser.error("--key-path is required when --key-source is 'file'")
    
    print_banner()
    
    # Load configuration
    print("Loading configuration...")
    config = load_config(args.config)
    
    # Override key source in config
    config['wasm_module_integrity']['key_source'] = args.key_source
    
    # Validate configuration
    if not validate_config(config):
        sys.exit(1)
    
    if args.validate_only:
        print("\n✓ Configuration validation completed successfully")
        sys.exit(0)
    
    # Check for existing keys
    if not args.force:
        try:
            key_manager = PQCKeyManager(config)
            existing_public = key_manager.load_public_key()
            if existing_public:
                response = input("\nExisting keys found. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print("Setup cancelled.")
                    sys.exit(0)
        except Exception:
            pass  # No existing keys, proceed
    
    # Set up keys based on source
    success = False
    if args.key_source == "environment":
        success = setup_environment_keys(config)
    elif args.key_source == "file":
        success = setup_file_keys(config, args.key_path)
    
    if not success:
        sys.exit(1)
    
    # Test the generated keys
    if not test_keys(config):
        sys.exit(1)
    
    # Audit the setup completion
    audit_security_event(
        "key_setup_completed",
        {
            "key_source": args.key_source,
            "key_path": args.key_path if args.key_source == "file" else None,
            "algorithm": config.get('wasm_module_integrity', {}).get('signature_algorithm', 'Dilithium3')
        },
        "INFO"
    )
    
    # Show next steps
    show_next_steps(args.key_source)
    
    print("\n✓ PQC key setup completed successfully!")


if __name__ == "__main__":
    main()