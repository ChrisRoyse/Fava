# src/fava/pqc/exceptions.py
"""
Custom exceptions for PQC cryptographic agility features in Fava.
"""

class PQCError(Exception):
    """Base class for PQC related errors."""
    pass

class CriticalConfigurationError(PQCError):
    """Indicates a critical error in PQC configuration that prevents startup."""
    pass

class ConfigurationError(PQCError):
    """Indicates an error in PQC configuration."""
    pass

class ParsingError(PQCError):
    """Indicates an error during parsing of configuration or data."""
    pass

class AlgorithmNotFoundError(PQCError):
    """Indicates that a requested cryptographic algorithm or suite is not found/registered."""
    pass

class AlgorithmUnavailableError(PQCError):
    """Indicates that a cryptographic algorithm is unavailable in the environment."""
    pass

class InvalidArgumentError(PQCError, ValueError):
    """Indicates an invalid argument was passed to a PQC function."""
    pass

class DecryptionError(PQCError):
    """Indicates an error during a decryption operation."""
    pass

class EncryptionFailedError(PQCError):
    """Indicates an error during an encryption operation."""
    pass

class HashingOperationFailedError(PQCError):
    """Indicates an error during a hashing operation."""
    pass

class ApplicationStartupError(PQCError):
    """Indicates an error during application startup related to PQC initialization."""
    pass

class BundleParsingError(PQCError):
    """Indicates an error while parsing an encrypted bundle."""
    pass

class CryptoError(PQCError):
    """Generic error from an underlying crypto library operation."""
    pass


class FavaAPIError(Exception):
    """Base class for Fava API errors."""
    pass


class FileLoadError(Exception):
    """Error loading a file."""
    pass