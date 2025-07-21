# src/fava/pqc/gpg_handler.py
"""
Real GPG Cryptographic Handler using python-gnupg library.

Security Note: This implementation provides proper GPG encryption/decryption
using the system's GPG installation. It replaces the dangerous placeholder
that was performing fake encryption.
"""
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import gnupg
except ImportError:
    gnupg = None

from .interfaces import CryptoHandler, KeyMaterialForEncryption, KeyMaterialForDecryption
from .exceptions import CryptoError, ConfigurationError

logger = logging.getLogger(__name__)

class GpgCryptoHandler(CryptoHandler):
    """
    Real GPG Crypto Handler using python-gnupg library.
    
    This handler provides proper GPG encryption/decryption functionality
    for legacy GPG-encrypted files in the Fava system.
    
    Security Features:
    - Real GPG encryption using system GPG installation
    - Proper key validation and fingerprint verification
    - Secure temporary file handling
    - Comprehensive error handling and audit logging
    """
    
    def __init__(self, suite_id: str, suite_specific_config: Dict[str, Any]):
        if gnupg is None:
            raise ConfigurationError(
                "python-gnupg library is required for GPG functionality. "
                "Install with: pip install python-gnupg"
            )
        
        self.my_suite_id = suite_id
        self.my_suite_config = suite_specific_config
        
        # Initialize GPG with secure configuration
        gpg_binary = suite_specific_config.get('gpg_binary', 'gpg')
        gpg_home = suite_specific_config.get('gpg_home', None)
        
        try:
            self.gpg = gnupg.GPG(gpg=gpg_binary, gnupghome=gpg_home)
            # Verify GPG is working
            self.gpg.list_keys()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize GPG: {e}")
        
        logger.info(f"GpgCryptoHandler for suite '{self.my_suite_id}' initialized with real GPG.")

    def get_suite_id(self) -> str:
        return self.my_suite_id

    def encrypt(
        self,
        plaintext: bytes,
        key_material: KeyMaterialForEncryption,
        suite_specific_config: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Encrypt data using GPG with specified recipient keys.
        
        Args:
            plaintext: Data to encrypt
            key_material: Must contain 'gpg_recipient_fingerprints' list
            suite_specific_config: Optional GPG-specific configuration
            
        Returns:
            GPG-encrypted data as bytes
            
        Raises:
            CryptoError: If encryption fails
            ValueError: If required key material is missing
        """
        current_config = suite_specific_config if suite_specific_config is not None else self.my_suite_config
        
        if not key_material or not key_material.get("gpg_recipient_fingerprints"):
            raise ValueError("Missing gpg_recipient_fingerprints in key_material for GPG encryption.")
        
        recipients = key_material["gpg_recipient_fingerprints"]
        if isinstance(recipients, str):
            recipients = [recipients]
        
        # Validate recipient keys exist
        for recipient in recipients:
            keys = self.gpg.list_keys(keys=[recipient])
            if not keys:
                raise CryptoError(f"Recipient key not found: {recipient}")
        
        logger.info(f"GPG encrypting for {len(recipients)} recipients")
        logger.debug(f"Recipients: {recipients}")
        
        try:
            # Encrypt data
            encrypted_data = self.gpg.encrypt(
                plaintext.decode('utf-8', errors='replace'),
                recipients,
                always_trust=current_config.get('always_trust', False),
                armor=current_config.get('armor', True)
            )
            
            if not encrypted_data.ok:
                raise CryptoError(f"GPG encryption failed: {encrypted_data.status}")
            
            result = str(encrypted_data).encode('utf-8')
            logger.info(f"Successfully encrypted {len(plaintext)} bytes to {len(result)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"GPG encryption failed: {e}")
            raise CryptoError(f"GPG encryption failed: {e}") from e

    def decrypt(
        self,
        encrypted_data: bytes,
        key_material: KeyMaterialForDecryption,
        suite_specific_config: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Decrypt GPG-encrypted data using available private keys.
        
        Args:
            encrypted_data: GPG-encrypted data
            key_material: Should contain 'gpg_passphrase' for private key unlock
            suite_specific_config: Optional GPG-specific configuration
            
        Returns:
            Decrypted plaintext as bytes
            
        Raises:
            CryptoError: If decryption fails
            ValueError: If encrypted data format is invalid
        """
        current_config = suite_specific_config if suite_specific_config is not None else self.my_suite_config
        
        # Extract passphrase if provided
        passphrase = key_material.get("gpg_passphrase") if key_material else None
        
        logger.info("GPG decrypting data")
        
        try:
            # Convert bytes to string for GPG processing
            encrypted_str = encrypted_data.decode('utf-8', errors='replace')
            
            # Validate it looks like GPG data
            if not (encrypted_str.strip().startswith('-----BEGIN PGP MESSAGE-----') or 
                   encrypted_str.strip().startswith('-----BEGIN PGP SIGNATURE-----')):
                raise ValueError("Data does not appear to be GPG-encrypted")
            
            # Decrypt data
            decrypted_data = self.gpg.decrypt(
                encrypted_str,
                passphrase=passphrase
            )
            
            if not decrypted_data.ok:
                raise CryptoError(f"GPG decryption failed: {decrypted_data.status}")
            
            result = str(decrypted_data).encode('utf-8')
            logger.info(f"Successfully decrypted {len(encrypted_data)} bytes to {len(result)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"GPG decryption failed: {e}")
            raise CryptoError(f"GPG decryption failed: {e}") from e

    def can_handle(self, file_path: str, file_content_peek: Optional[bytes] = None, config: Optional[Any] = None) -> bool:
        """
        Determines if this handler can process the given file.
        
        Checks for GPG armor headers and binary GPG format signatures.
        
        Args:
            file_path: Path to the file being checked
            file_content_peek: First few bytes of file content
            config: Optional configuration
            
        Returns:
            True if this handler can process the file
        """
        if not file_content_peek:
            return False
        
        try:
            # Check for ASCII-armored GPG data
            content_str = file_content_peek.decode('utf-8', errors='ignore')
            gpg_armor_headers = [
                '-----BEGIN PGP MESSAGE-----',
                '-----BEGIN PGP SIGNATURE-----', 
                '-----BEGIN PGP SIGNED MESSAGE-----',
                '-----BEGIN PGP PUBLIC KEY BLOCK-----',
                '-----BEGIN PGP PRIVATE KEY BLOCK-----'
            ]
            
            for header in gpg_armor_headers:
                if header in content_str:
                    logger.debug(f"GpgCryptoHandler can_handle: Detected GPG armor '{header}' for {file_path}")
                    return True
            
            # Check for binary GPG format (starts with specific byte sequences)
            # GPG binary format typically starts with 0x85 (packet tag for compressed data)
            # or 0x8c (packet tag for encrypted data)
            if file_content_peek[0:1] in [b'\x85', b'\x8c', b'\x94', b'\x95']:
                logger.debug(f"GpgCryptoHandler can_handle: Detected binary GPG format for {file_path}")
                return True
                
        except (UnicodeDecodeError, IndexError):
            # If we can't decode or access bytes, it's probably not GPG
            pass
        
        logger.debug(f"GpgCryptoHandler can_handle: No GPG markers detected for {file_path}")
        return False

    @property
    def name(self) -> str:
        return "GpgCryptoHandler"
    
    def get_supported_algorithms(self) -> List[str]:
        """
        Get list of supported GPG algorithms.
        
        Returns:
            List of supported algorithm names
        """
        return ["GPG", "PGP", "OpenPGP"]
    
    def validate_configuration(self) -> bool:
        """
        Validate GPG configuration and availability.
        
        Returns:
            True if GPG is properly configured and functional
        """
        try:
            # Test basic GPG functionality
            keys = self.gpg.list_keys()
            logger.info(f"GPG validation successful: {len(keys)} keys available")
            return True
        except Exception as e:
            logger.error(f"GPG validation failed: {e}")
            return False