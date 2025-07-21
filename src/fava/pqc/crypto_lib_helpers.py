# src/fava/pqc/crypto_lib_helpers.py
"""
Real cryptographic library helpers replacing all placeholder implementations.
This module provides actual cryptographic operations using liboqs and cryptography libraries.
"""

# Import all real implementations
from .real_implementations.kem_helper import RealKEMLibraryHelper
from .real_implementations.kdf_helper import RealKDFLibraryHelper  
from .real_implementations.symmetric_helper import RealSymmetricCipherLibraryHelper
from .real_implementations.utility_helper import RealUtilityLibraryHelper

# Replace placeholders with real implementations
KEM_LIBRARY = RealKEMLibraryHelper
KDF_LIBRARY = RealKDFLibraryHelper
SYMMETRIC_CIPHER_LIBRARY = RealSymmetricCipherLibraryHelper
UTILITY_LIBRARY = RealUtilityLibraryHelper

# Backward compatibility - expose individual classes
KEMLibraryHelper = RealKEMLibraryHelper
KDFLibraryHelper = RealKDFLibraryHelper
SymmetricCipherLibraryHelper = RealSymmetricCipherLibraryHelper
UtilityLibraryHelper = RealUtilityLibraryHelper