#!/usr/bin/env python3
"""
Setup script for Fava PQC Development Environment

This script helps set up the development environment for Post-Quantum Cryptography
integration into Fava, including checking for required tools and setting up
initial configurations.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, check=True, shell=False):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd if shell else cmd.split(),
            capture_output=True,
            text=True,
            check=check,
            shell=shell
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print(f"Error: {e.stderr}")
        return None

def check_conda_environment():
    """Check if conda environment exists and is activated."""
    try:
        result = run_command("conda info --json")
        if result:
            info = json.loads(result.stdout)
            active_env = info.get("active_prefix_name", "base")
            print(f"Current conda environment: {active_env}")
            
            if active_env != "fava-pqc":
                print("⚠️  Warning: You're not in the fava-pqc environment")
                print("Please run: conda activate fava-pqc")
                return False
            return True
    except Exception as e:
        print(f"Error checking conda environment: {e}")
        return False

def check_liboqs_installation():
    """Check if liboqs is properly installed."""
    try:
        import oqs
        print("✅ liboqs-python is installed and working")
        
        # Test basic KEM functionality
        kem = oqs.KeyEncapsulation("Kyber512")
        public_key = kem.generate_keypair()
        print(f"✅ Kyber512 KEM test successful (public key size: {len(public_key)} bytes)")
        
        # Test basic signature functionality
        sig = oqs.Signature("Dilithium2")
        public_key = sig.generate_keypair()
        message = b"Test message for PQC signature"
        signature = sig.sign(message)
        is_valid = sig.verify(message, signature, public_key)
        print(f"✅ Dilithium2 signature test {'successful' if is_valid else 'failed'}")
        
        return True
    except ImportError:
        print("❌ liboqs-python not installed or not working")
        print("Try: pip install liboqs-python")
        return False
    except Exception as e:
        print(f"❌ Error testing liboqs: {e}")
        return False

def setup_git_hooks():
    """Set up git hooks for the project."""
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("❌ Not in a git repository or .git/hooks directory not found")
        return False
    
    # Create a pre-commit hook that runs security checks
    pre_commit_hook = hooks_dir / "pre-commit"
    hook_content = """#!/bin/bash
# Pre-commit hook for Fava PQC project

echo "Running security and crypto checks..."

# Check for hardcoded secrets or keys
if git diff --cached --name-only | xargs grep -l "private.*key\|secret\|password" 2>/dev/null; then
    echo "❌ Warning: Potential secrets or keys detected in staged files"
    echo "Please review and use environment variables or secure key storage"
    exit 1
fi

# Run basic linting
python -m ruff check src/ tests/ 2>/dev/null || echo "⚠️  Ruff not available or errors found"

# Check for PQC algorithm usage consistency
if git diff --cached --name-only | xargs grep -l "sha256\|md5\|sha1" 2>/dev/null; then
    echo "⚠️  Classical hash algorithms detected - consider PQC alternatives in new code"
fi

echo "✅ Pre-commit checks passed"
"""
    
    try:
        with open(pre_commit_hook, 'w') as f:
            f.write(hook_content)
        os.chmod(pre_commit_hook, 0o755)
        print("✅ Git pre-commit hook installed")
        return True
    except Exception as e:
        print(f"❌ Error setting up git hooks: {e}")
        return False

def create_pqc_config_template():
    """Create a template configuration file for PQC settings."""
    config_template = {
        "pqc_settings": {
            "default_kem": "Kyber768",
            "default_signature": "Dilithium3",
            "default_hash": "SHA3-256",
            "file_encryption": {
                "algorithm": "hybrid-kyber-aes",
                "enabled": False,
                "backup_classical": True
            },
            "tls_settings": {
                "prefer_pqc_kems": True,
                "min_tls_version": "1.3",
                "cipher_suites": [
                    "TLS_AES_256_GCM_SHA384",
                    "TLS_CHACHA20_POLY1305_SHA256"
                ]
            },
            "development": {
                "crypto_agility_testing": True,
                "algorithm_benchmarking": True,
                "test_vectors_enabled": True
            }
        },
        "security_policy": {
            "hybrid_mode_duration": "24_months",
            "pure_pqc_timeline": "2026-01-01",
            "classical_deprecation": "2027-01-01"
        }
    }
    
    config_file = Path("pqc_config_template.json")
    try:
        with open(config_file, 'w') as f:
            json.dump(config_template, f, indent=2)
        print(f"✅ PQC configuration template created: {config_file}")
        print("   Copy this to pqc_config.json and customize as needed")
        return True
    except Exception as e:
        print(f"❌ Error creating PQC config template: {e}")
        return False

def setup_development_tools():
    """Set up additional development tools and scripts."""
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    # Create a PQC testing script
    pqc_test_script = scripts_dir / "test_pqc_algorithms.py"
    test_script_content = '''#!/usr/bin/env python3
"""
Test script for PQC algorithm performance and functionality
"""

import time
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import oqs
except ImportError:
    print("liboqs-python not available")
    sys.exit(1)

def benchmark_kem(kem_name, iterations=100):
    """Benchmark a KEM algorithm."""
    print(f"\\nBenchmarking {kem_name}...")
    
    kem = oqs.KeyEncapsulation(kem_name)
    
    # Benchmark key generation
    start_time = time.time()
    for _ in range(iterations):
        public_key = kem.generate_keypair()
    keygen_time = (time.time() - start_time) / iterations
    
    # Benchmark encapsulation
    public_key = kem.generate_keypair()
    start_time = time.time()
    for _ in range(iterations):
        ciphertext, shared_secret = kem.encap_secret(public_key)
    encap_time = (time.time() - start_time) / iterations
    
    # Benchmark decapsulation
    ciphertext, shared_secret = kem.encap_secret(public_key)
    start_time = time.time()
    for _ in range(iterations):
        decap_secret = kem.decap_secret(ciphertext)
    decap_time = (time.time() - start_time) / iterations
    
    print(f"  Key sizes: Public={len(public_key)}, Ciphertext={len(ciphertext)}, Secret={len(shared_secret)}")
    print(f"  Performance: KeyGen={keygen_time*1000:.2f}ms, Encap={encap_time*1000:.2f}ms, Decap={decap_time*1000:.2f}ms")

def main():
    """Main function to run PQC benchmarks."""
    print("🔐 Post-Quantum Cryptography Algorithm Testing")
    print("=" * 50)
    
    # Test available KEMs
    kems_to_test = ["Kyber512", "Kyber768", "Kyber1024"]
    
    for kem_name in kems_to_test:
        try:
            if kem_name in oqs.get_enabled_KEM_mechanisms():
                benchmark_kem(kem_name)
            else:
                print(f"❌ {kem_name} not available")
        except Exception as e:
            print(f"❌ Error testing {kem_name}: {e}")
    
    print("\\n🔐 Testing complete!")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(pqc_test_script, 'w') as f:
            f.write(test_script_content)
        os.chmod(pqc_test_script, 0o755)
        print(f"✅ PQC testing script created: {pqc_test_script}")
        return True
    except Exception as e:
        print(f"❌ Error creating PQC test script: {e}")
        return False

def check_frontend_tools():
    """Check if frontend development tools are available."""
    print("\\n🔧 Checking frontend development tools...")
    
    # Check Node.js
    node_result = run_command("node --version", check=False)
    if node_result and node_result.returncode == 0:
        print(f"✅ Node.js: {node_result.stdout.strip()}")
    else:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    npm_result = run_command("npm --version", check=False)
    if npm_result and npm_result.returncode == 0:
        print(f"✅ npm: {npm_result.stdout.strip()}")
    else:
        print("❌ npm not found")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Fava PQC Development Environment")
    print("=" * 50)
    
    # Check conda environment
    print("\\n📦 Checking conda environment...")
    conda_ok = check_conda_environment()
    
    # Check PQC libraries
    print("\\n🔐 Checking PQC libraries...")
    pqc_ok = check_liboqs_installation()
    
    # Check frontend tools
    frontend_ok = check_frontend_tools()
    
    # Setup development tools
    print("\\n🛠️  Setting up development tools...")
    git_hooks_ok = setup_git_hooks()
    config_ok = create_pqc_config_template()
    scripts_ok = setup_development_tools()
    
    # Summary
    print("\\n📋 Setup Summary:")
    print(f"  Conda environment: {'✅' if conda_ok else '❌'}")
    print(f"  PQC libraries: {'✅' if pqc_ok else '❌'}")
    print(f"  Frontend tools: {'✅' if frontend_ok else '❌'}")
    print(f"  Git hooks: {'✅' if git_hooks_ok else '❌'}")
    print(f"  Configuration: {'✅' if config_ok else '❌'}")
    print(f"  Scripts: {'✅' if scripts_ok else '❌'}")
    
    if all([conda_ok, pqc_ok, frontend_ok]):
        print("\\n🎉 Environment setup complete! Ready for PQC development.")
        print("\\nNext steps:")
        print("  1. Review and customize pqc_config_template.json")
        print("  2. Run: python scripts/test_pqc_algorithms.py")
        print("  3. Start implementing the CryptoService abstraction layer")
    else:
        print("\\n⚠️  Some issues were found. Please address them before proceeding.")
        print("\\nTroubleshooting:")
        if not conda_ok:
            print("  - Make sure you've created and activated the fava-pqc conda environment")
        if not pqc_ok:
            print("  - Install liboqs-python: pip install liboqs-python")
        if not frontend_ok:
            print("  - Install Node.js and npm through conda or your system package manager")

if __name__ == "__main__":
    main() 