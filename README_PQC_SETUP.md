# Fava Post-Quantum Cryptography (PQC) Development Environment

This document provides comprehensive instructions for setting up a development environment for implementing Post-Quantum Cryptography features in Fava.

## 🎯 Overview

This environment is designed to support the implementation of quantum-resistant cryptography in Fava, including:

- **File Encryption**: PQC-based encryption for Beancount files
- **Data Integrity**: Quantum-resistant hashing algorithms
- **TLS Security**: Configuration for PQC-enabled web servers
- **Cryptographic Agility**: Abstraction layers for algorithm flexibility
- **WASM Security**: Digital signatures for WebAssembly modules

## 📋 Prerequisites

- **Conda or Miniconda** installed on your system
- **Git** for version control
- **Python 3.11+** (will be installed via conda)
- **Administrative privileges** (for some installations)

## 🚀 Quick Start

### 1. Create the Conda Environment

```bash
# Create the environment from the environment.yml file
conda env create -f environment.yml

# Activate the environment
conda activate fava-pqc
```

### 2. Verify Installation

```bash
# Run the setup verification script
python setup_pqc_environment.py
```

### 3. Install Additional PQC Libraries

Some PQC libraries may need manual installation:

```bash
# Install liboqs-python (core PQC library)
pip install liboqs-python

# If the above fails, try building from source:
# pip install git+https://github.com/open-quantum-safe/liboqs-python.git
```

## 🔧 Detailed Setup Instructions

### Environment Components

The environment includes:

#### Core Dependencies
- **Python 3.11**: Base language runtime
- **Flask & related**: Web framework for Fava
- **Beancount**: Core accounting library
- **Node.js & npm**: Frontend development tools

#### Cryptographic Libraries
- **liboqs-python**: Open Quantum Safe library for PQC algorithms
- **cryptography**: Enhanced Python cryptography library
- **pycryptodome**: Additional crypto primitives
- **pysha3**: SHA-3 hash implementations

#### Development Tools
- **pytest**: Testing framework
- **mypy**: Static type checking
- **ruff**: Fast Python linter
- **black**: Code formatting
- **pre-commit**: Git hooks

#### PQC-Specific Tools
- **PyOQS**: Python bindings for quantum-safe algorithms
- **tree-sitter**: For WASM parsing support
- **wasmtime-py**: WASM runtime for testing

### Manual Installation Steps

If some packages fail to install automatically:

#### 1. Install liboqs System Library (Linux/macOS)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install liboqs-dev

# macOS with Homebrew
brew install liboqs

# Then install Python bindings
pip install liboqs-python
```

#### 2. Install Node.js Dependencies (if needed)

```bash
# In the frontend directory
cd frontend
npm install
```

#### 3. Verify PQC Algorithms

```bash
# Test available PQC algorithms
python scripts/test_pqc_algorithms.py
```

## 🧪 Testing the Environment

### 1. Run PQC Algorithm Tests

```bash
python scripts/test_pqc_algorithms.py
```

Expected output:
```
🔐 Post-Quantum Cryptography Algorithm Testing
==================================================

Benchmarking Kyber512...
  Key sizes: Public=800, Ciphertext=768, Secret=32
  Performance: KeyGen=0.15ms, Encap=0.18ms, Decap=0.22ms

Benchmarking Kyber768...
  Key sizes: Public=1184, Ciphertext=1088, Secret=32
  Performance: KeyGen=0.23ms, Encap=0.28ms, Decap=0.31ms
```

### 2. Verify Development Tools

```bash
# Check linting
ruff check src/

# Check type hints
mypy src/

# Run existing tests
pytest tests/
```

### 3. Test Frontend Tools

```bash
# Check Node.js and npm
node --version
npm --version

# Install frontend dependencies (if not already done)
cd frontend && npm install
```

## 📁 Project Structure for PQC Implementation

```
fava/
├── src/fava/
│   ├── crypto_service.py          # New: PQC abstraction layer
│   ├── pqc/                       # New: PQC-specific modules
│   │   ├── __init__.py
│   │   ├── kem.py                 # Key Encapsulation Mechanisms
│   │   ├── signatures.py          # Digital signatures
│   │   └── hash.py                # Quantum-resistant hashing
│   ├── core/
│   │   ├── file.py                # Modified: PQC hashing
│   │   └── __init__.py            # Modified: PQC file encryption
│   └── cli.py                     # Modified: PQC TLS options
├── frontend/src/
│   ├── lib/
│   │   └── crypto.ts              # New: Frontend crypto abstraction
│   └── codemirror/
│       └── beancount.ts           # Modified: WASM signature verification
├── scripts/
│   ├── test_pqc_algorithms.py     # PQC testing script
│   └── benchmark_crypto.py        # Performance testing
├── tests/
│   ├── test_pqc_integration.py    # New: PQC integration tests
│   └── test_crypto_service.py     # New: Crypto service tests
├── pqc_config_template.json       # PQC configuration template
└── environment.yml                # Conda environment definition
```

## ⚙️ Configuration

### 1. PQC Configuration Template

Copy and customize the configuration:

```bash
cp pqc_config_template.json pqc_config.json
```

Edit `pqc_config.json` to customize:

```json
{
  "pqc_settings": {
    "default_kem": "Kyber768",
    "default_signature": "Dilithium3",
    "default_hash": "SHA3-256",
    "file_encryption": {
      "algorithm": "hybrid-kyber-aes",
      "enabled": false,
      "backup_classical": true
    }
  }
}
```

### 2. Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# .env
PQC_CONFIG_PATH=./pqc_config.json
FAVA_DEBUG_PQC=true
FAVA_CRYPTO_AGILITY_MODE=hybrid
```

## 🔒 Security Considerations

### Development Security

1. **Never commit private keys** or secrets to version control
2. **Use environment variables** for sensitive configuration
3. **Enable git hooks** for security checks (automatically set up)
4. **Regular dependency updates** for security patches

### PQC Implementation Security

1. **Hybrid mode first**: Combine classical and PQC algorithms
2. **Cryptographic agility**: Design for algorithm changes
3. **Test with known vectors**: Verify against standard test vectors
4. **Performance monitoring**: Track algorithm performance impacts

## 🚀 Getting Started with PQC Implementation

### Phase 1: Abstraction Layer

1. **Implement CryptoService interface**:
   ```bash
   # Create the base crypto service
   touch src/fava/crypto_service.py
   ```

2. **Add configuration support**:
   ```bash
   # Extend Fava options for PQC settings
   # Modify src/fava/util/fava_options.py
   ```

### Phase 2: File Encryption

1. **Update file handling**:
   ```bash
   # Modify src/fava/core/file.py for PQC hashing
   # Modify src/fava/core/__init__.py for PQC decryption
   ```

### Phase 3: Frontend Integration

1. **Add frontend crypto support**:
   ```bash
   # Create frontend/src/lib/crypto.ts
   # Update frontend build process for WASM libraries
   ```

## 📚 Learning Resources

### PQC Background
- [NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Open Quantum Safe Project](https://openquantumsafe.org/)
- [CRYSTALS-Kyber](https://pq-crystals.org/kyber/)
- [CRYSTALS-Dilithium](https://pq-crystals.org/dilithium/)

### Implementation Guides
- [liboqs Documentation](https://github.com/open-quantum-safe/liboqs)
- [PQC Migration Guide](https://media.defense.gov/2021/Aug/04/2002821837/-1/-1/1/Quantum_FAQs_20210804.PDF)

## 🐛 Troubleshooting

### Common Issues

#### 1. liboqs-python Installation Fails

```bash
# Try installing system dependencies first
sudo apt-get install cmake ninja-build  # Ubuntu/Debian
brew install cmake ninja                 # macOS

# Then retry
pip install liboqs-python
```

#### 2. Node.js Version Issues

```bash
# Update Node.js in conda
conda update nodejs npm
```

#### 3. Permission Errors

```bash
# Make sure scripts are executable
chmod +x scripts/*.py
chmod +x setup_pqc_environment.py
```

### Getting Help

1. **Check the setup script**: `python setup_pqc_environment.py`
2. **Review conda environment**: `conda list`
3. **Check environment activation**: `conda info --envs`
4. **Validate PQC libraries**: Import test in Python

## 🤝 Contributing

When contributing to the PQC implementation:

1. **Follow security practices**: Never commit keys or secrets
2. **Write tests**: Include both unit and integration tests
3. **Document changes**: Update this README and code documentation
4. **Performance testing**: Benchmark new algorithms
5. **Security review**: Have crypto code reviewed by security experts

## 📊 Performance Benchmarks

Run performance tests to monitor PQC impact:

```bash
# Benchmark current algorithms
python scripts/test_pqc_algorithms.py

# Full performance suite (when implemented)
python scripts/benchmark_crypto.py
```

Expected performance characteristics:
- **Kyber768**: ~0.2ms key generation, ~0.3ms encap/decap
- **Dilithium3**: ~1ms key generation, ~2ms sign, ~0.5ms verify
- **SHA3-256**: ~10% slower than SHA-256

---

🔐 **Remember**: This is a development environment for implementing quantum-resistant cryptography. Always use proper security practices and have cryptographic implementations reviewed by security experts before production use. 