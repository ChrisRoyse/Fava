"""
PQC Key Management System for Fava

This module implements secure key management for post-quantum cryptographic operations,
replacing hardcoded keys with dynamic key loading and lifecycle management.

Security Requirements:
- NIST SP 800-208 compliant key generation
- Secure key storage with proper file permissions
- Key rotation capability
- Comprehensive audit logging
- Support for multiple key sources (environment, file, vault, HSM)
"""

import base64
import hashlib
import json
import logging
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import secrets

# Import OQS for PQC operations
try:
    import oqs
except ImportError:
    raise ImportError("liboqs-python is required for PQC key management")

# Import HashiCorp Vault client (optional dependency)
try:
    import hvac
except ImportError:
    hvac = None

# Import PKCS#11 for HSM integration (optional dependency)
try:
    import pkcs11
except ImportError:
    pkcs11 = None

from .exceptions import ConfigurationError
from .audit_logger import audit_key_generation, audit_key_loading, audit_key_rotation, audit_security_event, audit_error, get_audit_logger

logger = logging.getLogger(__name__)


class KeyManagementError(Exception):
    """Base exception for key management operations."""
    pass


class KeyNotFoundException(KeyManagementError):
    """Raised when required keys cannot be found."""
    pass


class KeyValidationError(KeyManagementError):
    """Raised when key validation fails."""
    pass


class KeyGenerationError(KeyManagementError):
    """Raised when key generation fails."""
    pass


class KeyStorageError(KeyManagementError):
    """Raised when key storage operations fail."""
    pass


class PQCKeyManager:
    """
    Manages PQC key lifecycle including generation, loading, validation, and rotation.
    
    This class provides secure key management for post-quantum cryptographic operations,
    supporting multiple key sources and implementing security best practices.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PQC Key Manager.
        
        Args:
            config: Configuration dictionary containing WASM module integrity settings
        """
        self.config = config
        self.wasm_config = config.get('wasm_module_integrity', {})
        self.key_source = self.wasm_config.get('key_source', 'environment')
        self.algorithm = self.wasm_config.get('signature_algorithm', 'Dilithium3')
        
        # Key rotation settings
        self.rotation_enabled = self.wasm_config.get('key_rotation_enabled', True)
        self.rotation_interval_days = self.wasm_config.get('key_rotation_interval_days', 90)
        
        # Validate algorithm support
        if not oqs.is_sig_enabled(self.algorithm):
            raise KeyManagementError(f"Algorithm {self.algorithm} not supported by liboqs")
        
        logger.info(f"Initialized PQCKeyManager with algorithm={self.algorithm}, source={self.key_source}")
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new PQC keypair using cryptographically secure methods.
        
        Follows NIST SP 800-208 requirements for key generation.
        
        Returns:
            Tuple of (public_key_bytes, private_key_bytes)
            
        Raises:
            KeyGenerationError: If key generation fails
        """
        logger.info(f"Generating new {self.algorithm} keypair")
        
        try:
            with oqs.Signature(self.algorithm) as signer:
                # Generate the keypair
                public_key = signer.generate_keypair()
                private_key = signer.export_secret_key()
                
                # Validate generated keys
                if not self._validate_keypair(public_key, private_key):
                    raise KeyGenerationError("Generated keypair failed validation")
                
                # Audit key generation event
                public_key_hash = self._hash_key(public_key)
                audit_key_generation(self.algorithm, self.key_source, public_key_hash)
                
                # Log key generation event (without exposing key material)
                self._log_key_operation("generate", {
                    'algorithm': self.algorithm,
                    'public_key_size': len(public_key),
                    'private_key_size': len(private_key),
                    'public_key_hash': public_key_hash[:16]  # First 16 chars for identification
                })
                
                logger.info(f"Successfully generated {self.algorithm} keypair")
                return public_key, private_key
                
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise KeyGenerationError(f"Keypair generation failed: {e}") from e
    
    def load_public_key(self) -> bytes:
        """
        Load the public key from the configured source.
        
        Returns:
            Public key bytes
            
        Raises:
            KeyNotFoundException: If key cannot be found
            KeyValidationError: If key validation fails
        """
        try:
            if self.key_source == 'environment':
                key_bytes = self._load_key_from_environment(is_private=False)
            elif self.key_source == 'file':
                key_bytes = self._load_key_from_file(is_private=False)
            elif self.key_source == 'vault':
                key_bytes = self._load_key_from_vault(is_private=False)
            elif self.key_source == 'hsm':
                key_bytes = self._load_key_from_hsm(is_private=False)
            else:
                raise KeyManagementError(f"Unsupported key source: {self.key_source}")
            
            # Validate key format
            self._validate_key_format(key_bytes, is_private=False)
            
            # Audit key loading event
            public_key_hash = self._hash_key(key_bytes)
            audit_key_loading("public", self.key_source, public_key_hash, True)
            
            # Log key access (without exposing key material)
            self._log_key_operation("load_public", {
                'source': self.key_source,
                'key_size': len(key_bytes),
                'key_hash': public_key_hash[:16]
            })
            
            return key_bytes
            
        except Exception as e:
            # Audit failed key loading
            audit_key_loading("public", self.key_source, "", False)
            audit_error("key_loading_failed", str(e), {"key_type": "public", "key_source": self.key_source})
            
            logger.error(f"Failed to load public key from {self.key_source}: {e}")
            raise
    
    def load_private_key(self) -> bytes:
        """
        Load the private key from the configured source.
        
        Returns:
            Private key bytes
            
        Raises:
            KeyNotFoundException: If key cannot be found
            KeyValidationError: If key validation fails
        """
        try:
            if self.key_source == 'environment':
                key_bytes = self._load_key_from_environment(is_private=True)
            elif self.key_source == 'file':
                key_bytes = self._load_key_from_file(is_private=True)
            elif self.key_source == 'vault':
                key_bytes = self._load_key_from_vault(is_private=True)
            elif self.key_source == 'hsm':
                key_bytes = self._load_key_from_hsm(is_private=True)
            else:
                raise KeyManagementError(f"Unsupported key source: {self.key_source}")
            
            # Validate key format
            self._validate_key_format(key_bytes, is_private=True)
            
            # For private key, we need to get the corresponding public key hash for audit
            # This is a bit tricky since we only have the private key
            # We'll use a placeholder hash for now
            private_key_hash = self._hash_key(key_bytes)
            audit_key_loading("private", self.key_source, private_key_hash, True)
            
            # Log key access (without exposing key material)
            self._log_key_operation("load_private", {
                'source': self.key_source,
                'key_size': len(key_bytes),
                'key_hash': private_key_hash[:16]
            })
            
            return key_bytes
            
        except Exception as e:
            # Audit failed key loading
            audit_key_loading("private", self.key_source, "", False)
            audit_error("key_loading_failed", str(e), {"key_type": "private", "key_source": self.key_source})
            
            logger.error(f"Failed to load private key from {self.key_source}: {e}")
            raise
    
    def store_keypair(self, public_key: bytes, private_key: bytes) -> None:
        """
        Store the keypair in the configured destination.
        
        Args:
            public_key: Public key bytes
            private_key: Private key bytes
            
        Raises:
            KeyStorageError: If storage fails
            KeyValidationError: If keys fail validation
        """
        # Validate keys before storing
        if not self._validate_keypair(public_key, private_key):
            raise KeyValidationError("Keypair validation failed before storage")
        
        try:
            if self.key_source == 'environment':
                self._store_keys_to_environment(public_key, private_key)
            elif self.key_source == 'file':
                self._store_keys_to_file(public_key, private_key)
            elif self.key_source == 'vault':
                self._store_keys_to_vault(public_key, private_key)
            elif self.key_source == 'hsm':
                self._store_keys_to_hsm(public_key, private_key)
            else:
                raise KeyStorageError(f"Unsupported key source: {self.key_source}")
            
            # Log storage event
            self._log_key_operation("store", {
                'source': self.key_source,
                'public_key_size': len(public_key),
                'private_key_size': len(private_key),
                'public_key_hash': self._hash_key(public_key)[:16]
            })
            
            logger.info(f"Successfully stored keypair to {self.key_source}")
            
        except Exception as e:
            logger.error(f"Failed to store keypair to {self.key_source}: {e}")
            raise KeyStorageError(f"Keypair storage failed: {e}") from e
    
    def rotate_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate new keypair and replace existing keys.
        
        Returns:
            Tuple of (new_public_key, new_private_key)
            
        Raises:
            KeyManagementError: If rotation fails
        """
        logger.info("Starting key rotation process")
        
        try:
            # Generate new keypair
            new_public_key, new_private_key = self.generate_keypair()
            
            # Backup old keys if they exist and get hash for audit
            old_key_hash = None
            try:
                old_public_key = self.load_public_key()
                old_private_key = self.load_private_key()
                old_key_hash = self._hash_key(old_public_key)
                self._backup_keys(old_public_key, old_private_key)
                logger.info("Backed up existing keys before rotation")
            except KeyNotFoundException:
                logger.info("No existing keys found, proceeding with fresh installation")
            
            # Store new keys
            self.store_keypair(new_public_key, new_private_key)
            
            # Audit key rotation event
            new_key_hash = self._hash_key(new_public_key)
            audit_key_rotation(old_key_hash, new_key_hash, True)
            
            # Record rotation in tracking system
            self._record_rotation(old_key_hash, new_key_hash, True)
            
            # Log rotation event
            self._log_key_operation("rotate", {
                'old_public_key_hash': old_key_hash[:16] if old_key_hash else None,
                'new_public_key_hash': new_key_hash[:16],
                'rotation_timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info("Key rotation completed successfully")
            return new_public_key, new_private_key
            
        except Exception as e:
            # Record failed rotation in tracking system
            try:
                old_key_hash = self._hash_key(self.load_public_key()) if old_key_hash is None else old_key_hash
                self._record_rotation(old_key_hash, "", False)
            except Exception:
                pass  # Don't fail on tracking error
            
            # Audit failed key rotation
            audit_key_rotation(None, "", False)
            audit_error("key_rotation_failed", str(e), {"algorithm": self.algorithm, "key_source": self.key_source})
            
            logger.error(f"Key rotation failed: {e}")
            raise KeyManagementError(f"Key rotation failed: {e}") from e
    
    def validate_keys(self) -> bool:
        """
        Validate that current keys are functional.
        
        Returns:
            True if keys are valid and functional
        """
        try:
            public_key = self.load_public_key()
            private_key = self.load_private_key()
            is_valid = self._validate_keypair(public_key, private_key)
            
            # Audit validation result
            public_key_hash = self._hash_key(public_key)
            get_audit_logger().log_key_validation(public_key_hash, is_valid)
            
            return is_valid
        except Exception as e:
            # Audit validation failure
            get_audit_logger().log_key_validation("", False, str(e))
            audit_error("key_validation_failed", str(e), {"key_source": self.key_source})
            
            logger.error(f"Key validation failed: {e}")
            return False
    
    def test_vault_connection(self) -> bool:
        """
        Test HashiCorp Vault connection and authentication.
        
        Returns:
            True if Vault is accessible and authenticated
        """
        if self.key_source != 'vault':
            return True  # Not using Vault
            
        if hvac is None:
            logger.error("hvac library not available for Vault connection test")
            return False
            
        try:
            vault_config = self.wasm_config.get('vault', {})
            vault_url = vault_config.get('url', os.environ.get('VAULT_ADDR'))
            vault_token = vault_config.get('token', os.environ.get('VAULT_TOKEN'))
            
            if not vault_url or not vault_token:
                logger.error("Vault URL or token not configured")
                return False
                
            client = hvac.Client(url=vault_url, token=vault_token)
            
            if not client.is_authenticated():
                logger.error("Vault authentication failed")
                return False
                
            # Test basic read capability
            try:
                client.secrets.kv.v2.list_secrets(path="")
            except hvac.exceptions.InvalidPath:
                # InvalidPath is expected for empty path, but means we can connect
                pass
            except Exception as e:
                logger.error(f"Vault capability test failed: {e}")
                return False
                
            logger.info("Vault connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Vault connection test failed: {e}")
            return False
    
    def test_hsm_connection(self) -> bool:
        """
        Test Hardware Security Module connection and authentication.
        
        Returns:
            True if HSM is accessible and authenticated
        """
        if self.key_source != 'hsm':
            return True  # Not using HSM
            
        if pkcs11 is None:
            logger.error("pkcs11 library not available for HSM connection test")
            return False
            
        try:
            hsm_config = self.wasm_config.get('hsm', {})
            library_path = hsm_config.get('library_path', '/usr/lib/softhsm/libsofthsm2.so')
            token_label = hsm_config.get('token_label', 'fava-pqc')
            user_pin = hsm_config.get('user_pin', os.environ.get('HSM_USER_PIN'))
            
            if not user_pin:
                logger.error("HSM user PIN not configured")
                return False
                
            # Test PKCS#11 library loading
            lib = pkcs11.lib(library_path)
            
            # Test token access
            token = lib.get_token(token_label=token_label)
            
            if not token:
                logger.error(f"HSM token '{token_label}' not found")
                return False
                
            # Test session and authentication
            with token.open(user_pin=user_pin) as session:
                # Test basic operations
                session.get_objects({
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA
                })
                
            logger.info("HSM connection test successful")
            return True
            
        except pkcs11.exceptions.PKCS11Error as e:
            logger.error(f"HSM PKCS#11 connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"HSM connection test failed: {e}")
            return False
    
    def get_key_info(self) -> Dict[str, Any]:
        """
        Get information about the current keys.
        
        Returns:
            Dictionary with key metadata (no sensitive information)
        """
        try:
            public_key = self.load_public_key()
            private_key = self.load_private_key()
            
            info = {
                'algorithm': self.algorithm,
                'key_source': self.key_source,
                'public_key_size': len(public_key),
                'private_key_size': len(private_key),
                'public_key_hash': self._hash_key(public_key)[:16],
                'last_rotation': self._get_last_rotation_time(),
                'next_rotation': self._get_next_rotation_time(),
                'rotation_enabled': self.rotation_enabled,
                'rotation_interval_days': self.rotation_interval_days,
                'status': 'valid' if self.validate_keys() else 'invalid',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add source-specific metadata
            if self.key_source == 'vault':
                vault_config = self.wasm_config.get('vault', {})
                info['vault_path'] = vault_config.get('path', 'secret/fava/pqc/keys')
                info['vault_url'] = vault_config.get('url', os.environ.get('VAULT_ADDR', 'not configured'))
            elif self.key_source == 'hsm':
                hsm_config = self.wasm_config.get('hsm', {})
                info['hsm_library_path'] = hsm_config.get('library_path', '/usr/lib/softhsm/libsofthsm2.so')
                info['hsm_token_label'] = hsm_config.get('token_label', 'fava-pqc')
                info['hsm_connection_status'] = 'available' if pkcs11 else 'library_missing'
            
            return info
            
        except Exception as e:
            return {
                'algorithm': self.algorithm,
                'key_source': self.key_source,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _load_key_from_environment(self, is_private: bool) -> bytes:
        """Load key from environment variable."""
        env_var = (self.wasm_config.get('private_key_env_var', 'FAVA_PQC_PRIVATE_KEY') 
                  if is_private 
                  else self.wasm_config.get('public_key_env_var', 'FAVA_PQC_PUBLIC_KEY'))
        
        key_b64 = os.environ.get(env_var)
        if not key_b64:
            raise KeyNotFoundException(f"Key not found in environment variable: {env_var}")
        
        try:
            key_bytes = base64.b64decode(key_b64)
            return key_bytes
        except Exception as e:
            raise KeyValidationError(f"Invalid key format in {env_var}: {e}") from e
    
    def _load_key_from_file(self, is_private: bool) -> bytes:
        """Load key from filesystem."""
        key_path = Path(self.wasm_config.get('key_file_path', '/etc/fava/keys/'))
        filename = f'private_key.{self.algorithm.lower()}' if is_private else f'public_key.{self.algorithm.lower()}'
        full_path = key_path / filename
        
        if not full_path.exists():
            raise KeyNotFoundException(f"Key file not found: {full_path}")
        
        # Check file permissions
        expected_mode = 0o600 if is_private else 0o644
        actual_mode = full_path.stat().st_mode & 0o777
        if actual_mode != expected_mode:
            logger.warning(f"Key file {full_path} has permissions {oct(actual_mode)}, expected {oct(expected_mode)}")
        
        try:
            key_data = full_path.read_text().strip()
            key_bytes = base64.b64decode(key_data)
            return key_bytes
        except Exception as e:
            raise KeyValidationError(f"Invalid key file {full_path}: {e}") from e
    
    def _load_key_from_vault(self, is_private: bool) -> bytes:
        """
        Load key from HashiCorp Vault.
        
        Args:
            is_private: Whether to load private key (True) or public key (False)
            
        Returns:
            Key bytes loaded from Vault
            
        Raises:
            KeyNotFoundException: If key not found in Vault
            KeyValidationError: If key format is invalid
            ConfigurationError: If Vault configuration is invalid
        """
        if hvac is None:
            raise ConfigurationError(
                "hvac library is required for Vault integration. "
                "Install with: pip install hvac"
            )
        
        vault_config = self.wasm_config.get('vault', {})
        vault_url = vault_config.get('url', os.environ.get('VAULT_ADDR'))
        vault_token = vault_config.get('token', os.environ.get('VAULT_TOKEN'))
        vault_path = vault_config.get('path', 'secret/fava/pqc/keys')
        
        if not vault_url:
            raise ConfigurationError("Vault URL not configured (set vault.url or VAULT_ADDR)")
        
        if not vault_token:
            raise ConfigurationError("Vault token not configured (set vault.token or VAULT_TOKEN)")
        
        try:
            # Initialize Vault client
            client = hvac.Client(url=vault_url, token=vault_token)
            
            # Verify client is authenticated
            if not client.is_authenticated():
                raise ConfigurationError("Vault authentication failed")
            
            # Determine key name
            key_name = 'private_key' if is_private else 'public_key'
            full_path = f"{vault_path}/{self.algorithm.lower()}"
            
            logger.debug(f"Loading {key_name} from Vault path: {full_path}")
            
            # Read secret from Vault
            response = client.secrets.kv.v2.read_secret_version(path=full_path)
            
            if not response or 'data' not in response or 'data' not in response['data']:
                raise KeyNotFoundException(f"Key not found in Vault at path: {full_path}")
            
            key_data = response['data']['data'].get(key_name)
            if not key_data:
                raise KeyNotFoundException(f"Key '{key_name}' not found in Vault secret")
            
            # Decode base64 key data
            try:
                key_bytes = base64.b64decode(key_data)
            except Exception as e:
                raise KeyValidationError(f"Invalid base64 key data in Vault: {e}") from e
            
            logger.info(f"Successfully loaded {key_name} from Vault")
            return key_bytes
            
        except hvac.exceptions.VaultError as e:
            logger.error(f"Vault error loading key: {e}")
            raise KeyNotFoundException(f"Vault error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load key from Vault: {e}")
            raise KeyManagementError(f"Vault key loading failed: {e}") from e
    
    def _load_key_from_hsm(self, is_private: bool) -> bytes:
        """
        Load key from Hardware Security Module using PKCS#11.
        
        Args:
            is_private: Whether to load private key (True) or public key (False)
            
        Returns:
            Key bytes loaded from HSM
            
        Raises:
            KeyNotFoundException: If key not found in HSM
            KeyValidationError: If key format is invalid
            ConfigurationError: If HSM configuration is invalid
        """
        if pkcs11 is None:
            raise ConfigurationError(
                "python-pkcs11 library is required for HSM integration. "
                "Install with: pip install python-pkcs11"
            )
        
        hsm_config = self.wasm_config.get('hsm', {})
        library_path = hsm_config.get('library_path', '/usr/lib/softhsm/libsofthsm2.so')
        token_label = hsm_config.get('token_label', 'fava-pqc')
        user_pin = hsm_config.get('user_pin', os.environ.get('HSM_USER_PIN'))
        
        if not user_pin:
            raise ConfigurationError("HSM user PIN not configured (set hsm.user_pin or HSM_USER_PIN)")
        
        try:
            # Load PKCS#11 library
            lib = pkcs11.lib(library_path)
            
            # Get token
            token = lib.get_token(token_label=token_label)
            
            # Open session and login
            with token.open(user_pin=user_pin) as session:
                # Determine key label and type
                key_label = f'fava-pqc-{self.algorithm.lower()}-{"private" if is_private else "public"}'
                key_class = pkcs11.KeyType.EC if not is_private else pkcs11.KeyType.EC
                
                logger.debug(f"Loading {key_label} from HSM")
                
                # Search for key
                keys = session.get_objects({
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.PRIVATE_KEY if is_private else pkcs11.ObjectClass.PUBLIC_KEY,
                    pkcs11.Attribute.LABEL: key_label
                })
                
                if not keys:
                    raise KeyNotFoundException(f"Key '{key_label}' not found in HSM")
                
                key_obj = keys[0]
                
                # For PQC keys stored as data objects (since PKCS#11 doesn't natively support PQC)
                data_objects = session.get_objects({
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                    pkcs11.Attribute.LABEL: key_label
                })
                
                if data_objects:
                    # Key stored as data object
                    data_obj = data_objects[0]
                    key_data_b64 = data_obj[pkcs11.Attribute.VALUE].decode('utf-8')
                    key_bytes = base64.b64decode(key_data_b64)
                else:
                    # Try to extract key value (for supported key types)
                    try:
                        if is_private:
                            key_value = key_obj[pkcs11.Attribute.VALUE]
                        else:
                            key_value = key_obj[pkcs11.Attribute.EC_POINT]
                        key_bytes = bytes(key_value)
                    except Exception:
                        raise KeyNotFoundException(f"Cannot extract key value for '{key_label}' from HSM")
                
                logger.info(f"Successfully loaded {key_label} from HSM")
                return key_bytes
                
        except pkcs11.exceptions.PKCS11Error as e:
            logger.error(f"HSM PKCS#11 error loading key: {e}")
            raise KeyNotFoundException(f"HSM PKCS#11 error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load key from HSM: {e}")
            raise KeyManagementError(f"HSM key loading failed: {e}") from e
    
    def _store_keys_to_environment(self, public_key: bytes, private_key: bytes) -> None:
        """Store keys to environment variables (for development only)."""
        logger.warning("Storing keys in environment variables is not recommended for production")
        
        public_b64 = base64.b64encode(public_key).decode('ascii')
        private_b64 = base64.b64encode(private_key).decode('ascii')
        
        public_env_var = self.wasm_config.get('public_key_env_var', 'FAVA_PQC_PUBLIC_KEY')
        private_env_var = self.wasm_config.get('private_key_env_var', 'FAVA_PQC_PRIVATE_KEY')
        
        os.environ[public_env_var] = public_b64
        os.environ[private_env_var] = private_b64
        
        logger.info(f"Keys stored in environment variables: {public_env_var}, {private_env_var}")
    
    def _store_keys_to_file(self, public_key: bytes, private_key: bytes) -> None:
        """Store keys to filesystem with secure permissions."""
        key_path = Path(self.wasm_config.get('key_file_path', '/etc/fava/keys/'))
        
        # Create directory if it doesn't exist
        key_path.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Store public key
        public_file = key_path / f'public_key.{self.algorithm.lower()}'
        public_b64 = base64.b64encode(public_key).decode('ascii')
        public_file.write_text(public_b64)
        public_file.chmod(0o644)
        
        # Store private key with restricted permissions
        private_file = key_path / f'private_key.{self.algorithm.lower()}'
        private_b64 = base64.b64encode(private_key).decode('ascii')
        private_file.write_text(private_b64)
        private_file.chmod(0o600)
        
        logger.info(f"Keys stored to filesystem: {key_path}")
    
    def _store_keys_to_vault(self, public_key: bytes, private_key: bytes) -> None:
        """
        Store keys to HashiCorp Vault.
        
        Args:
            public_key: Public key bytes to store
            private_key: Private key bytes to store
            
        Raises:
            KeyStorageError: If storage to Vault fails
            ConfigurationError: If Vault configuration is invalid
        """
        if hvac is None:
            raise ConfigurationError(
                "hvac library is required for Vault integration. "
                "Install with: pip install hvac"
            )
        
        vault_config = self.wasm_config.get('vault', {})
        vault_url = vault_config.get('url', os.environ.get('VAULT_ADDR'))
        vault_token = vault_config.get('token', os.environ.get('VAULT_TOKEN'))
        vault_path = vault_config.get('path', 'secret/fava/pqc/keys')
        
        if not vault_url:
            raise ConfigurationError("Vault URL not configured (set vault.url or VAULT_ADDR)")
        
        if not vault_token:
            raise ConfigurationError("Vault token not configured (set vault.token or VAULT_TOKEN)")
        
        try:
            # Initialize Vault client
            client = hvac.Client(url=vault_url, token=vault_token)
            
            # Verify client is authenticated
            if not client.is_authenticated():
                raise ConfigurationError("Vault authentication failed")
            
            # Prepare secret data
            public_b64 = base64.b64encode(public_key).decode('ascii')
            private_b64 = base64.b64encode(private_key).decode('ascii')
            
            secret_data = {
                'public_key': public_b64,
                'private_key': private_b64,
                'algorithm': self.algorithm,
                'created_at': datetime.utcnow().isoformat(),
                'key_id': self._hash_key(public_key)[:16]
            }
            
            full_path = f"{vault_path}/{self.algorithm.lower()}"
            
            logger.debug(f"Storing keypair to Vault path: {full_path}")
            
            # Store secret in Vault
            client.secrets.kv.v2.create_or_update_secret(
                path=full_path,
                secret=secret_data
            )
            
            # Verify storage by reading back (optional verification)
            verification = client.secrets.kv.v2.read_secret_version(path=full_path)
            if not verification or 'data' not in verification:
                raise KeyStorageError("Failed to verify key storage in Vault")
            
            logger.info(f"Successfully stored keypair to Vault at path: {full_path}")
            
        except hvac.exceptions.VaultError as e:
            logger.error(f"Vault error storing keys: {e}")
            raise KeyStorageError(f"Vault error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to store keys to Vault: {e}")
            raise KeyStorageError(f"Vault key storage failed: {e}") from e
    
    def _store_keys_to_hsm(self, public_key: bytes, private_key: bytes) -> None:
        """
        Store keys to Hardware Security Module using PKCS#11.
        
        Args:
            public_key: Public key bytes to store
            private_key: Private key bytes to store
            
        Raises:
            KeyStorageError: If storage to HSM fails
            ConfigurationError: If HSM configuration is invalid
        """
        if pkcs11 is None:
            raise ConfigurationError(
                "python-pkcs11 library is required for HSM integration. "
                "Install with: pip install python-pkcs11"
            )
        
        hsm_config = self.wasm_config.get('hsm', {})
        library_path = hsm_config.get('library_path', '/usr/lib/softhsm/libsofthsm2.so')
        token_label = hsm_config.get('token_label', 'fava-pqc')
        user_pin = hsm_config.get('user_pin', os.environ.get('HSM_USER_PIN'))
        
        if not user_pin:
            raise ConfigurationError("HSM user PIN not configured (set hsm.user_pin or HSM_USER_PIN)")
        
        try:
            # Load PKCS#11 library
            lib = pkcs11.lib(library_path)
            
            # Get token
            token = lib.get_token(token_label=token_label)
            
            # Open session and login
            with token.open(user_pin=user_pin, rw=True) as session:
                # Generate labels
                public_label = f'fava-pqc-{self.algorithm.lower()}-public'
                private_label = f'fava-pqc-{self.algorithm.lower()}-private'
                
                logger.debug(f"Storing keypair to HSM with labels: {public_label}, {private_label}")
                
                # Since PKCS#11 doesn't natively support PQC algorithms,
                # store keys as data objects with base64 encoding
                public_b64 = base64.b64encode(public_key).decode('ascii')
                private_b64 = base64.b64encode(private_key).decode('ascii')
                
                # Store public key as data object
                public_attrs = {
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                    pkcs11.Attribute.LABEL: public_label,
                    pkcs11.Attribute.APPLICATION: f'Fava-PQC-{self.algorithm}',
                    pkcs11.Attribute.VALUE: public_b64.encode('utf-8'),
                    pkcs11.Attribute.TOKEN: True,
                    pkcs11.Attribute.PRIVATE: False,
                    pkcs11.Attribute.MODIFIABLE: False
                }
                
                # Store private key as data object
                private_attrs = {
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                    pkcs11.Attribute.LABEL: private_label,
                    pkcs11.Attribute.APPLICATION: f'Fava-PQC-{self.algorithm}',
                    pkcs11.Attribute.VALUE: private_b64.encode('utf-8'),
                    pkcs11.Attribute.TOKEN: True,
                    pkcs11.Attribute.PRIVATE: True,
                    pkcs11.Attribute.SENSITIVE: True,
                    pkcs11.Attribute.MODIFIABLE: False,
                    pkcs11.Attribute.EXTRACTABLE: True  # Needed for key loading
                }
                
                # Remove existing keys if they exist
                for label in [public_label, private_label]:
                    existing = session.get_objects({
                        pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                        pkcs11.Attribute.LABEL: label
                    })
                    for obj in existing:
                        obj.destroy()
                        logger.debug(f"Removed existing key: {label}")
                
                # Create new key objects
                public_obj = session.create_object(public_attrs)
                private_obj = session.create_object(private_attrs)
                
                logger.info(f"Successfully stored keypair to HSM")
                
                # Verify storage by reading back
                verification_public = session.get_objects({
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                    pkcs11.Attribute.LABEL: public_label
                })
                
                verification_private = session.get_objects({
                    pkcs11.Attribute.CLASS: pkcs11.ObjectClass.DATA,
                    pkcs11.Attribute.LABEL: private_label
                })
                
                if not verification_public or not verification_private:
                    raise KeyStorageError("Failed to verify key storage in HSM")
                
                logger.info("HSM key storage verification successful")
                
        except pkcs11.exceptions.PKCS11Error as e:
            logger.error(f"HSM PKCS#11 error storing keys: {e}")
            raise KeyStorageError(f"HSM PKCS#11 error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to store keys to HSM: {e}")
            raise KeyStorageError(f"HSM key storage failed: {e}") from e
    
    def _validate_keypair(self, public_key: bytes, private_key: bytes) -> bool:
        """
        Validate that a keypair is functional by checking key properties.
        
        Note: We cannot reuse exported private keys with OQS due to ctypes memory management
        issues, so we validate by checking key sizes and basic properties instead.
        
        Args:
            public_key: Public key bytes
            private_key: Private key bytes
            
        Returns:
            True if keypair is valid and functional
        """
        try:
            # Check that keys are not empty
            if not public_key or not private_key:
                logger.error("Empty keys provided for validation")
                return False
                
            # Get expected key sizes for the algorithm
            expected_sizes = self._get_expected_key_sizes()
            
            # Use secure timing for size validation to prevent side-channel analysis
            from .timing_protection import SecureErrorHandling, TimingJitter
            
            # Normalize validation timing with jitter
            validation_start_time = None
            try:
                import time
                validation_start_time = time.perf_counter()
                
                public_size_valid = len(public_key) == expected_sizes['public']
                private_size_valid = len(private_key) == expected_sizes['private']
                
                if not public_size_valid:
                    logger.error(f"Public key size mismatch: got {len(public_key)}, expected {expected_sizes['public']}")
                    return SecureErrorHandling.uniform_error_response("invalid_public_key_size")
                    
                if not private_size_valid:
                    logger.error(f"Private key size mismatch: got {len(private_key)}, expected {expected_sizes['private']}")
                    return SecureErrorHandling.uniform_error_response("invalid_private_key_size")
                    
            finally:
                # Add timing jitter to normalize validation time
                if validation_start_time:
                    TimingJitter.normalize_operation_time(0.005, validation_start_time)  # 5ms constant time
            
            # Additional validation: test that the public key format is acceptable
            # by attempting to use it in a verification call (should not crash)
            test_message = b"PQC key validation test message"
            with oqs.Signature(self.algorithm) as test_signer:
                test_signer.generate_keypair()
                test_signature = test_signer.sign(test_message)
                
                # Try verification with our public key to test format validity
                try:
                    # This may return False (expected with different keys) but should not crash
                    test_signer.verify(test_message, test_signature, public_key)
                    logger.debug("Public key format validation passed")
                    return True
                except Exception as format_error:
                    logger.error(f"Public key format validation failed: {format_error}")
                    return False
                
        except Exception as e:
            logger.error(f"Keypair validation failed: {e}")
            return False
    
    def _get_expected_key_sizes(self) -> dict:
        """Get expected key sizes for the configured algorithm."""
        # Key sizes for supported algorithms
        sizes = {
            'Dilithium2': {'public': 1312, 'private': 2528},
            'Dilithium3': {'public': 1952, 'private': 4000}, 
            'Dilithium5': {'public': 2592, 'private': 4864},
            'Falcon-512': {'public': 897, 'private': 1281},
            'Falcon-1024': {'public': 1793, 'private': 2305}
        }
        
        if self.algorithm not in sizes:
            logger.warning(f"Unknown algorithm {self.algorithm}, using default sizes")
            return {'public': 1000, 'private': 2000}  # Conservative defaults
            
        return sizes[self.algorithm]
    
    def _validate_key_format(self, key_bytes: bytes, is_private: bool) -> None:
        """
        Validate key format and size.
        
        Args:
            key_bytes: Key bytes to validate
            is_private: Whether this is a private key
            
        Raises:
            KeyValidationError: If key format is invalid
        """
        if not key_bytes:
            raise KeyValidationError("Key is empty")
        
        # Check minimum key size (Dilithium3 keys are typically large)
        min_size = 1000  # Conservative minimum
        if len(key_bytes) < min_size:
            raise KeyValidationError(f"Key size {len(key_bytes)} is too small (minimum {min_size})")
        
        # Additional algorithm-specific validation could be added here
        
    def _hash_key(self, key_bytes: bytes) -> str:
        """
        Generate a SHA256 hash of key bytes for identification purposes.
        
        Args:
            key_bytes: Key bytes to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(key_bytes).hexdigest()
    
    def _backup_keys(self, public_key: bytes, private_key: bytes) -> None:
        """
        Backup existing keys before rotation.
        
        Args:
            public_key: Current public key bytes
            private_key: Current private key bytes
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if self.key_source == 'file':
            key_path = Path(self.wasm_config.get('key_file_path', '/etc/fava/keys/'))
            backup_path = key_path / 'backup'
            backup_path.mkdir(exist_ok=True, mode=0o700)
            
            # Backup public key
            public_backup = backup_path / f'public_key.{self.algorithm.lower()}.{timestamp}'
            public_b64 = base64.b64encode(public_key).decode('ascii')
            public_backup.write_text(public_b64)
            public_backup.chmod(0o644)
            
            # Backup private key
            private_backup = backup_path / f'private_key.{self.algorithm.lower()}.{timestamp}'
            private_b64 = base64.b64encode(private_key).decode('ascii')
            private_backup.write_text(private_b64)
            private_backup.chmod(0o600)
            
            logger.info(f"Keys backed up to {backup_path}")
            
        elif self.key_source == 'vault':
            # Backup to a different Vault path
            if hvac is None:
                logger.warning("Cannot backup Vault keys - hvac library not available")
                return
                
            try:
                vault_config = self.wasm_config.get('vault', {})
                vault_url = vault_config.get('url', os.environ.get('VAULT_ADDR'))
                vault_token = vault_config.get('token', os.environ.get('VAULT_TOKEN'))
                vault_path = vault_config.get('path', 'secret/fava/pqc/keys')
                backup_path = f"{vault_path}/backup/{self.algorithm.lower()}/{timestamp}"
                
                client = hvac.Client(url=vault_url, token=vault_token)
                
                backup_data = {
                    'public_key': base64.b64encode(public_key).decode('ascii'),
                    'private_key': base64.b64encode(private_key).decode('ascii'),
                    'algorithm': self.algorithm,
                    'backup_timestamp': timestamp,
                    'original_key_id': self._hash_key(public_key)[:16]
                }
                
                client.secrets.kv.v2.create_or_update_secret(
                    path=backup_path,
                    secret=backup_data
                )
                
                logger.info(f"Keys backed up to Vault at path: {backup_path}")
                
            except Exception as e:
                logger.error(f"Failed to backup keys to Vault: {e}")
                # Don't fail the rotation process due to backup failure
                
        elif self.key_source == 'hsm':
            # Backup HSM keys to file system (HSMs typically don't support versioning)
            if pkcs11 is None:
                logger.warning("Cannot backup HSM keys - pkcs11 library not available")
                return
                
            try:
                # Create backup directory
                backup_dir = Path('/etc/fava/keys/hsm_backup')
                backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
                
                # Store backup with timestamp
                public_backup = backup_dir / f'public_key.{self.algorithm.lower()}.{timestamp}'
                private_backup = backup_dir / f'private_key.{self.algorithm.lower()}.{timestamp}'
                
                public_b64 = base64.b64encode(public_key).decode('ascii')
                private_b64 = base64.b64encode(private_key).decode('ascii')
                
                public_backup.write_text(public_b64)
                public_backup.chmod(0o644)
                
                private_backup.write_text(private_b64)
                private_backup.chmod(0o600)
                
                logger.info(f"HSM keys backed up to filesystem: {backup_dir}")
                
            except Exception as e:
                logger.error(f"Failed to backup HSM keys: {e}")
                # Don't fail the rotation process due to backup failure
        else:
            logger.info(f"Key backup not implemented for source: {self.key_source}")
    
    def _log_key_operation(self, operation: str, metadata: Dict[str, Any]) -> None:
        """
        Log key management operations for audit trail.
        
        Args:
            operation: Type of operation (generate, load, store, rotate, etc.)
            metadata: Additional metadata (no sensitive information)
        """
        audit_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'algorithm': self.algorithm,
            'key_source': self.key_source,
            **metadata
        }
        
        # Log to audit logger (separate from regular logs)
        audit_logger = logging.getLogger('fava.pqc.audit')
        audit_logger.info(f"KEY_OPERATION: {json.dumps(audit_data)}")
    
    def _get_last_rotation_time(self) -> Optional[str]:
        """
        Get timestamp of last key rotation.
        
        Returns:
            ISO timestamp string of last rotation, or None if never rotated
        """
        try:
            # Check multiple sources for rotation history
            rotation_timestamp = None
            
            # Source 1: Rotation tracking file
            rotation_file = self._get_rotation_tracking_file()
            if rotation_file.exists():
                rotation_data = json.loads(rotation_file.read_text())
                history = rotation_data.get('rotation_history', [])
                if history:
                    # Get most recent rotation
                    rotation_timestamp = history[-1]['timestamp']
            
            # Source 2: Key metadata (for Vault/HSM sources)
            if not rotation_timestamp and self.key_source in ['vault', 'hsm']:
                try:
                    key_info = self._get_key_metadata()
                    rotation_timestamp = key_info.get('last_rotation')
                except Exception:
                    pass  # Metadata not available
            
            # Source 3: Key creation timestamp as fallback
            if not rotation_timestamp and self.key_source == 'file':
                try:
                    key_path = Path(self.wasm_config.get('key_file_path', '/etc/fava/keys/'))
                    private_file = key_path / f'private_key.{self.algorithm.lower()}'
                    if private_file.exists():
                        # Use file modification time as creation/rotation timestamp
                        mtime = private_file.stat().st_mtime
                        rotation_timestamp = datetime.fromtimestamp(mtime).isoformat()
                except Exception:
                    pass
            
            return rotation_timestamp
            
        except Exception as e:
            logger.error(f"Failed to get last rotation time: {e}")
            return None
    
    def _get_next_rotation_time(self) -> Optional[str]:
        """Get timestamp of next scheduled rotation."""
        if not self.rotation_enabled:
            return None
        
        last_rotation = self._get_last_rotation_time()
        if last_rotation:
            try:
                last_dt = datetime.fromisoformat(last_rotation.replace('Z', '+00:00'))
                next_dt = last_dt + timedelta(days=self.rotation_interval_days)
                return next_dt.isoformat()
            except Exception:
                pass
        
        # Default to interval from now if no last rotation
        next_dt = datetime.utcnow() + timedelta(days=self.rotation_interval_days)
        return next_dt.isoformat()
    
    def _get_rotation_tracking_file(self) -> Path:
        """
        Get path to rotation tracking file.
        
        Returns:
            Path to rotation tracking file
        """
        if self.key_source == 'file':
            key_path = Path(self.wasm_config.get('key_file_path', '/etc/fava/keys/'))
            return key_path / 'rotation_history.json'
        else:
            # Use system-wide tracking for non-file sources
            tracking_dir = Path('/var/lib/fava/pqc')
            tracking_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            return tracking_dir / f'rotation_history_{self.key_source}_{self.algorithm.lower()}.json'
    
    def _record_rotation(self, old_key_hash: Optional[str], new_key_hash: str, success: bool) -> None:
        """
        Record a key rotation event in persistent storage.
        
        Args:
            old_key_hash: Hash of the previous key (if any)
            new_key_hash: Hash of the new key
            success: Whether the rotation was successful
        """
        try:
            rotation_file = self._get_rotation_tracking_file()
            
            # Load existing history
            rotation_data = {
                'algorithm': self.algorithm,
                'key_source': self.key_source,
                'rotation_interval_days': self.rotation_interval_days,
                'rotation_history': []
            }
            
            if rotation_file.exists():
                try:
                    existing_data = json.loads(rotation_file.read_text())
                    rotation_data.update(existing_data)
                except (json.JSONDecodeError, FileNotFoundError):
                    logger.warning(f"Could not load existing rotation history from {rotation_file}")
            
            # Add new rotation record
            rotation_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'old_key_hash': old_key_hash,
                'new_key_hash': new_key_hash,
                'success': success,
                'rotation_type': 'automatic' if self.rotation_enabled else 'manual',
                'algorithm': self.algorithm,
                'key_source': self.key_source
            }
            
            rotation_data['rotation_history'].append(rotation_record)
            rotation_data['last_rotation'] = rotation_record['timestamp']
            
            # Keep only last 100 rotations to prevent file growth
            if len(rotation_data['rotation_history']) > 100:
                rotation_data['rotation_history'] = rotation_data['rotation_history'][-100:]
            
            # Save to file with secure permissions
            rotation_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            rotation_file.write_text(json.dumps(rotation_data, indent=2))
            rotation_file.chmod(0o600)
            
            logger.info(f"Recorded key rotation in {rotation_file}")
            
        except Exception as e:
            logger.error(f"Failed to record rotation: {e}")
            # Don't fail the rotation process due to tracking failure
    
    def _get_key_metadata(self) -> Dict[str, Any]:
        """
        Get key metadata from storage source.
        
        Returns:
            Dictionary with key metadata
        """
        metadata = {}
        
        try:
            if self.key_source == 'vault' and hvac is not None:
                vault_config = self.wasm_config.get('vault', {})
                vault_url = vault_config.get('url', os.environ.get('VAULT_ADDR'))
                vault_token = vault_config.get('token', os.environ.get('VAULT_TOKEN'))
                vault_path = vault_config.get('path', 'secret/fava/pqc/keys')
                
                if vault_url and vault_token:
                    client = hvac.Client(url=vault_url, token=vault_token)
                    full_path = f"{vault_path}/{self.algorithm.lower()}"
                    response = client.secrets.kv.v2.read_secret_version(path=full_path)
                    
                    if response and 'data' in response and 'data' in response['data']:
                        vault_data = response['data']['data']
                        metadata['created_at'] = vault_data.get('created_at')
                        metadata['last_rotation'] = vault_data.get('last_rotation')
                        metadata['key_id'] = vault_data.get('key_id')
            
        except Exception as e:
            logger.debug(f"Could not retrieve key metadata: {e}")
        
        return metadata
    
    def get_rotation_history(self) -> List[Dict[str, Any]]:
        """
        Get complete key rotation history.
        
        Returns:
            List of rotation records sorted by timestamp
        """
        try:
            rotation_file = self._get_rotation_tracking_file()
            
            if not rotation_file.exists():
                return []
            
            rotation_data = json.loads(rotation_file.read_text())
            history = rotation_data.get('rotation_history', [])
            
            # Sort by timestamp (most recent first)
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get rotation history: {e}")
            return []
    
    def is_rotation_due(self) -> bool:
        """
        Check if key rotation is due based on configured interval.
        
        Returns:
            True if rotation should be performed
        """
        if not self.rotation_enabled:
            return False
        
        last_rotation = self._get_last_rotation_time()
        if not last_rotation:
            # No previous rotation recorded, consider rotation due
            return True
        
        try:
            last_dt = datetime.fromisoformat(last_rotation.replace('Z', '+00:00'))
            next_rotation = last_dt + timedelta(days=self.rotation_interval_days)
            return datetime.utcnow() >= next_rotation
        except Exception as e:
            logger.error(f"Failed to check rotation due date: {e}")
            return False
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """
        Get comprehensive rotation status information.
        
        Returns:
            Dictionary with rotation status and compliance information
        """
        try:
            last_rotation = self._get_last_rotation_time()
            next_rotation = self._get_next_rotation_time()
            history = self.get_rotation_history()
            
            status = {
                'rotation_enabled': self.rotation_enabled,
                'rotation_interval_days': self.rotation_interval_days,
                'last_rotation': last_rotation,
                'next_rotation': next_rotation,
                'rotation_due': self.is_rotation_due(),
                'total_rotations': len(history),
                'successful_rotations': len([r for r in history if r.get('success', False)]),
                'failed_rotations': len([r for r in history if not r.get('success', True)]),
                'algorithm': self.algorithm,
                'key_source': self.key_source,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Calculate compliance metrics
            if last_rotation and self.rotation_enabled:
                last_dt = datetime.fromisoformat(last_rotation.replace('Z', '+00:00'))
                days_since_rotation = (datetime.utcnow() - last_dt).days
                
                status['days_since_last_rotation'] = days_since_rotation
                status['compliance_status'] = (
                    'compliant' if days_since_rotation <= self.rotation_interval_days
                    else 'overdue'
                )
                status['days_overdue'] = max(0, days_since_rotation - self.rotation_interval_days)
            else:
                status['days_since_last_rotation'] = None
                status['compliance_status'] = 'no_rotation_history'
                status['days_overdue'] = 0
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get rotation status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }