# src/fava/pqc/configuration_validator.py
"""
Module for validating Fava configuration options, specifically PQC
options for the embedded server and key management.
"""
import os
import platform
import stat
from pathlib import Path
from typing import Dict, Any, List

# Configuration option name for embedded server PQC KEMs
EMBEDDED_SERVER_PQC_KEMS_OPTION: str = "pqc_tls_embedded_server_kems"

# Valid key sources for dynamic key management
VALID_KEY_SOURCES = ["environment", "file", "vault", "hsm"]

# Valid signature algorithms
VALID_SIGNATURE_ALGORITHMS = ["Dilithium2", "Dilithium3", "Dilithium5", "Falcon-512", "Falcon-1024"]


def _format_user_friendly_error(error_type: str, field: str, issue: str, help_text: str = "") -> str:
    """
    Format a user-friendly error message with helpful context.
    
    Args:
        error_type: Type of error (e.g., "MISSING", "INVALID", "SECURITY")
        field: The configuration field name
        issue: Description of the issue
        help_text: Optional helpful guidance for resolution
        
    Returns:
        Formatted error message
    """
    base_msg = f"[{error_type}] {issue}"
    if help_text:
        return f"{base_msg}\n  [HELP] {help_text}"
    return base_msg


def validate_pqc_tls_embedded_server_options(
    fava_config: Dict[str, Any],
    known_supported_pqc_kems_by_python_env: List[str],
) -> List[str]:
    """
    Validates Fava configuration options for PQC TLS on the embedded server.
    Based on pseudocode: `validate_pqc_tls_embedded_server_options`.
    """
    errors: List[str] = []

    if EMBEDDED_SERVER_PQC_KEMS_OPTION not in fava_config:
        return errors  # Option not present, so no validation errors for it.

    configured_kems = fava_config[EMBEDDED_SERVER_PQC_KEMS_OPTION]

    if not isinstance(configured_kems, list):
        errors.append(
            f"Configuration option '{EMBEDDED_SERVER_PQC_KEMS_OPTION}' "
            f"must be a list of KEM strings."
        )
        return errors  # Stop further validation if the type is incorrect.

    # Check if the option is set but the environment lacks PQC support
    if configured_kems and not known_supported_pqc_kems_by_python_env:
        errors.append(
            f"Configuration option '{EMBEDDED_SERVER_PQC_KEMS_OPTION}' is set, "
            f"but the current Fava/Python environment does not support any "
            f"PQC KEMs for the embedded server."
        )
        # If environment has no support, further KEM validation against an empty list is less informative.
        # The primary issue is the lack of environment support.
        return errors # Return early for this specific scenario (TC-DIT-CONFVAL-004)

    if not configured_kems: # Empty list was provided
        errors.append(
            f"Configuration option '{EMBEDDED_SERVER_PQC_KEMS_OPTION}' is set "
            f"but contains no KEMs. Provide a list of desired KEMs or remove "
            f"the option."
        )
    else:
        for kem in configured_kems:
            if not isinstance(kem, str):
                errors.append(
                    f"KEM value '{kem}' in '{EMBEDDED_SERVER_PQC_KEMS_OPTION}' "
                    f"is not a string. All KEMs must be strings."
                )
                continue # Skip checking this non-string KEM against known_supported
            if kem not in known_supported_pqc_kems_by_python_env:
                supported_list_str = ', '.join(known_supported_pqc_kems_by_python_env)
                supported_display = (
                    f"Supported: {supported_list_str}"
                    if known_supported_pqc_kems_by_python_env
                    else "Supported: None"
                )
                errors.append(
                    f"KEM '{kem}' in '{EMBEDDED_SERVER_PQC_KEMS_OPTION}' is not "
                    f"supported by the current Fava/Python environment. "
                    f"{supported_display}"
                )
    return errors

# Hypothetical function, actual implementation depends on Python environment capabilities.
# This would live in a more appropriate place in a real Fava structure,
# perhaps an environment introspection module.
def detect_available_python_pqc_kems() -> List[str]:
    """
    Hypothetical function to detect PQC KEMs supported by the Python env.
    Based on pseudocode: `DETECT_AVAILABLE_PYTHON_PQC_KEMS`.
    For now, returns an empty list, simulating no current support.
    """
    # In a real implementation, this would involve checking versions of OpenSSL,
    # Python's ssl module, and potentially the web server (e.g., Cheroot)
    # for PQC KEM support. This is complex and environment-dependent.
    return []


def validate_wasm_module_integrity_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate WASM module integrity configuration for dynamic key management.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if "wasm_module_integrity" not in config:
        errors.append("Missing 'wasm_module_integrity' configuration section")
        return errors
    
    wasm_config = config["wasm_module_integrity"]
    
    # Validate verification_enabled
    if "verification_enabled" not in wasm_config:
        errors.append("Missing 'verification_enabled' in wasm_module_integrity config")
    elif not isinstance(wasm_config["verification_enabled"], bool):
        errors.append("'verification_enabled' must be a boolean value")
    
    # Validate signature_algorithm
    if "signature_algorithm" not in wasm_config:
        errors.append("Missing 'signature_algorithm' in wasm_module_integrity config")
    elif wasm_config["signature_algorithm"] not in VALID_SIGNATURE_ALGORITHMS:
        errors.append(
            f"Invalid signature_algorithm '{wasm_config['signature_algorithm']}'. "
            f"Valid options: {', '.join(VALID_SIGNATURE_ALGORITHMS)}"
        )
    
    # Validate key_source
    if "key_source" not in wasm_config:
        errors.append("Missing 'key_source' in wasm_module_integrity config")
    elif wasm_config["key_source"] not in VALID_KEY_SOURCES:
        errors.append(
            f"Invalid key_source '{wasm_config['key_source']}'. "
            f"Valid options: {', '.join(VALID_KEY_SOURCES)}"
        )
    else:
        # Validate key source specific configuration
        key_source = wasm_config["key_source"]
        errors.extend(_validate_key_source_config(wasm_config, key_source))
    
    # Validate module_path and signature_path_suffix
    if "module_path" not in wasm_config:
        errors.append("Missing 'module_path' in wasm_module_integrity config")
    elif not isinstance(wasm_config["module_path"], str):
        errors.append("'module_path' must be a string")
    
    if "signature_path_suffix" not in wasm_config:
        errors.append("Missing 'signature_path_suffix' in wasm_module_integrity config")
    elif not isinstance(wasm_config["signature_path_suffix"], str):
        errors.append("'signature_path_suffix' must be a string")
    
    # Validate key rotation settings
    if "key_rotation_enabled" in wasm_config:
        if not isinstance(wasm_config["key_rotation_enabled"], bool):
            errors.append("'key_rotation_enabled' must be a boolean value")
    
    if "key_rotation_interval_days" in wasm_config:
        interval = wasm_config["key_rotation_interval_days"]
        if not isinstance(interval, int) or interval <= 0:
            errors.append("'key_rotation_interval_days' must be a positive integer")
    
    # Check for deprecated hardcoded public key
    if "public_key_base64" in wasm_config:
        errors.append(
            _format_user_friendly_error(
                "SECURITY", "public_key_base64",
                "Hardcoded public key detected - this is a critical security vulnerability",
                "Remove 'public_key_base64' from configuration and use dynamic key management with 'key_source': 'environment', 'file', 'vault', or 'hsm'."
            )
        )
    
    return errors


def _validate_key_source_config(wasm_config: Dict[str, Any], key_source: str) -> List[str]:
    """
    Validate key source specific configuration.
    
    Args:
        wasm_config: WASM module integrity configuration
        key_source: The key source type
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if key_source == "environment":
        # Validate environment variable names
        if "public_key_env_var" not in wasm_config:
            errors.append("Missing 'public_key_env_var' for environment key source")
        elif not isinstance(wasm_config["public_key_env_var"], str):
            errors.append("'public_key_env_var' must be a string")
        
        if "private_key_env_var" not in wasm_config:
            errors.append("Missing 'private_key_env_var' for environment key source")
        elif not isinstance(wasm_config["private_key_env_var"], str):
            errors.append("'private_key_env_var' must be a string")
    
    elif key_source == "file":
        # Validate file path configuration
        if "key_file_path" not in wasm_config:
            errors.append("Missing 'key_file_path' for file key source")
        elif not isinstance(wasm_config["key_file_path"], str):
            errors.append("'key_file_path' must be a string")
        else:
            # Check if path is valid (but don't require it to exist yet)
            key_path = wasm_config["key_file_path"]
            try:
                Path(key_path)  # This validates the path format
            except Exception as e:
                errors.append(f"Invalid 'key_file_path' format: {e}")
    
    elif key_source == "vault":
        # Validate HashiCorp Vault specific configuration
        errors.extend(_validate_vault_config(wasm_config))
    
    elif key_source == "hsm":
        # Validate HSM (Hardware Security Module) specific configuration
        errors.extend(_validate_hsm_config(wasm_config))
    
    return errors


def _validate_vault_config(wasm_config: Dict[str, Any]) -> List[str]:
    """
    Validate HashiCorp Vault specific configuration.
    
    Args:
        wasm_config: WASM module integrity configuration
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Required Vault configuration
    required_fields = [
        "vault_url", "vault_mount_path", "vault_secret_path",
        "vault_auth_method"
    ]
    
    for field in required_fields:
        if field not in wasm_config:
            help_text = {
                "vault_url": "Example: https://vault.example.com:8200",
                "vault_mount_path": "Common values: 'kv-v2', 'secret'",
                "vault_secret_path": "Example: 'fava/pqc-keys' or 'applications/fava/keys'",
                "vault_auth_method": "Recommended: 'token' for development, 'tls' for production"
            }.get(field, f"This field is required for Vault integration")
            
            errors.append(
                _format_user_friendly_error(
                    "MISSING", field,
                    f"Required Vault configuration field '{field}' is missing",
                    help_text
                )
            )
        elif not isinstance(wasm_config[field], str):
            errors.append(
                _format_user_friendly_error(
                    "INVALID", field,
                    f"'{field}' must be a string value",
                    "Check your configuration file syntax and ensure the value is properly quoted."
                )
            )
    
    # Validate vault_url format
    if "vault_url" in wasm_config:
        vault_url = wasm_config["vault_url"]
        if not (vault_url.startswith("http://") or vault_url.startswith("https://")):
            errors.append("'vault_url' must be a valid HTTP/HTTPS URL")
    
    # Validate auth method
    if "vault_auth_method" in wasm_config:
        auth_method = wasm_config["vault_auth_method"]
        valid_auth_methods = ["token", "userpass", "ldap", "aws", "kubernetes", "tls"]
        if auth_method not in valid_auth_methods:
            errors.append(
                f"Invalid vault_auth_method '{auth_method}'. "
                f"Valid options: {', '.join(valid_auth_methods)}"
            )
    
    # Validate auth-specific configuration
    auth_method = wasm_config.get("vault_auth_method")
    if auth_method == "token":
        if "vault_token" not in wasm_config and "vault_token_env_var" not in wasm_config:
            errors.append(
                "Token auth method requires either 'vault_token' or 'vault_token_env_var'"
            )
    elif auth_method == "userpass":
        if "vault_username" not in wasm_config or "vault_password_env_var" not in wasm_config:
            errors.append(
                "Userpass auth method requires 'vault_username' and 'vault_password_env_var'"
            )
    elif auth_method == "tls":
        if "vault_client_cert" not in wasm_config or "vault_client_key" not in wasm_config:
            errors.append(
                "TLS auth method requires 'vault_client_cert' and 'vault_client_key'"
            )
    
    # Validate TLS settings
    if "vault_tls_verify" in wasm_config:
        if not isinstance(wasm_config["vault_tls_verify"], bool):
            errors.append("'vault_tls_verify' must be a boolean")
    
    if "vault_ca_cert" in wasm_config:
        ca_cert_path = Path(wasm_config["vault_ca_cert"])
        try:
            if not ca_cert_path.exists():
                errors.append(f"Vault CA certificate file not found: {ca_cert_path}")
        except Exception as e:
            errors.append(f"Invalid vault_ca_cert path: {e}")
    
    # Validate key rotation for Vault
    if "vault_key_rotation_enabled" in wasm_config:
        if not isinstance(wasm_config["vault_key_rotation_enabled"], bool):
            errors.append("'vault_key_rotation_enabled' must be a boolean")
    
    return errors


def _validate_hsm_config(wasm_config: Dict[str, Any]) -> List[str]:
    """
    Validate HSM (Hardware Security Module) specific configuration.
    
    Args:
        wasm_config: WASM module integrity configuration
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Required HSM configuration
    required_fields = [
        "hsm_library_path", "hsm_slot_id", "hsm_token_label"
    ]
    
    for field in required_fields:
        if field not in wasm_config:
            errors.append(f"Missing '{field}' for hsm key source")
    
    # Validate HSM library path
    if "hsm_library_path" in wasm_config:
        library_path = Path(wasm_config["hsm_library_path"])
        try:
            if not library_path.exists():
                errors.append(f"HSM library file not found: {library_path}")
            elif not library_path.is_file():
                errors.append(f"HSM library path is not a file: {library_path}")
        except Exception as e:
            errors.append(f"Invalid hsm_library_path: {e}")
    
    # Validate slot ID
    if "hsm_slot_id" in wasm_config:
        slot_id = wasm_config["hsm_slot_id"]
        if not isinstance(slot_id, int) or slot_id < 0:
            errors.append("'hsm_slot_id' must be a non-negative integer")
    
    # Validate token label
    if "hsm_token_label" in wasm_config:
        if not isinstance(wasm_config["hsm_token_label"], str):
            errors.append("'hsm_token_label' must be a string")
    
    # Validate authentication
    auth_required_fields = ["hsm_pin_env_var"]
    for field in auth_required_fields:
        if field not in wasm_config:
            errors.append(f"Missing '{field}' for hsm key source")
        elif not isinstance(wasm_config[field], str):
            errors.append(f"'{field}' must be a string")
    
    # Validate key IDs
    if "hsm_public_key_id" in wasm_config:
        if not isinstance(wasm_config["hsm_public_key_id"], str):
            errors.append("'hsm_public_key_id' must be a string")
    
    if "hsm_private_key_id" in wasm_config:
        if not isinstance(wasm_config["hsm_private_key_id"], str):
            errors.append("'hsm_private_key_id' must be a string")
    
    # Validate HSM-specific settings
    if "hsm_key_usage" in wasm_config:
        valid_usages = ["sign", "verify", "sign_verify"]
        key_usage = wasm_config["hsm_key_usage"]
        if key_usage not in valid_usages:
            errors.append(
                f"Invalid hsm_key_usage '{key_usage}'. "
                f"Valid options: {', '.join(valid_usages)}"
            )
    
    # Validate HSM session settings
    if "hsm_session_timeout" in wasm_config:
        timeout = wasm_config["hsm_session_timeout"]
        if not isinstance(timeout, int) or timeout <= 0:
            errors.append("'hsm_session_timeout' must be a positive integer")
    
    if "hsm_max_retries" in wasm_config:
        retries = wasm_config["hsm_max_retries"]
        if not isinstance(retries, int) or retries < 0:
            errors.append("'hsm_max_retries' must be a non-negative integer")
    
    return errors


def _check_file_permissions(file_path: Path, file_type: str) -> List[str]:
    """
    Check file permissions in a cross-platform manner.
    
    Args:
        file_path: Path to the file
        file_type: Type of file for error messages (e.g., "private key")
        
    Returns:
        List of permission-related error messages
    """
    errors = []
    
    try:
        file_stat = file_path.stat()
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            errors.append(f"{file_type.title()} file is not readable: {file_path}")
            return errors
        
        # Platform-specific permission checks
        if platform.system() == "Windows":
            # Windows ACL-based permissions - basic check
            try:
                # Check if file has restrictive permissions
                # On Windows, we mainly check ownership and basic access
                if not file_path.owner() == os.getlogin():
                    errors.append(
                        _format_user_friendly_error(
                            "SECURITY", f"{file_type}_ownership",
                            f"{file_type.title()} file is not owned by the current user: {file_path}",
                            "Use 'icacls' or File Properties -> Security to change ownership to your user account."
                        )
                    )
            except (OSError, AttributeError):
                # Fallback for systems where getlogin() fails or owner() is not available
                pass
            
            # Check if file is hidden (Windows security practice)
            if hasattr(file_stat, 'st_file_attributes'):
                # FILE_ATTRIBUTE_HIDDEN = 0x2
                if not (file_stat.st_file_attributes & 0x2):
                    errors.append(
                        f"RECOMMENDATION: {file_type.title()} file should be hidden on Windows: {file_path}"
                    )
        else:
            # Unix-like systems (Linux, macOS, etc.)
            file_mode = file_stat.st_mode & 0o777
            
            if file_type == "private key":
                # Private keys should have restrictive permissions (600 or 400)
                if file_mode not in [0o600, 0o400]:
                    errors.append(
                        f"{file_type.title()} file has insecure permissions {oct(file_mode)}, "
                        f"should be 0o600 or 0o400: {file_path}"
                    )
            elif file_type == "public key":
                # Public keys can be more permissive but shouldn't be world-writable
                if file_mode & 0o002:  # World writable
                    errors.append(
                        f"{file_type.title()} file is world-writable {oct(file_mode)}, "
                        f"consider more restrictive permissions: {file_path}"
                    )
    
    except Exception as e:
        errors.append(f"Error checking {file_type} file permissions: {e}")
    
    return errors


def _check_vault_accessibility(wasm_config: Dict[str, Any]) -> List[str]:
    """
    Check HashiCorp Vault accessibility and authentication.
    
    Args:
        wasm_config: WASM module integrity configuration
        
    Returns:
        List of accessibility error messages
    """
    errors = []
    
    # Check required Vault environment variables or credentials
    auth_method = wasm_config.get("vault_auth_method", "token")
    
    if auth_method == "token":
        token_env_var = wasm_config.get("vault_token_env_var", "VAULT_TOKEN")
        if not os.environ.get(token_env_var) and "vault_token" not in wasm_config:
            errors.append(f"Vault token not available via environment variable '{token_env_var}' or configuration")
    
    elif auth_method == "userpass":
        password_env_var = wasm_config.get("vault_password_env_var")
        if password_env_var and not os.environ.get(password_env_var):
            errors.append(f"Vault password not available via environment variable '{password_env_var}'")
    
    # Check Vault URL accessibility (basic validation)
    vault_url = wasm_config.get("vault_url")
    if vault_url:
        # Validate URL format more thoroughly
        try:
            from urllib.parse import urlparse
            parsed = urlparse(vault_url)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"Invalid Vault URL format: {vault_url}")
        except ImportError:
            # Fallback for minimal validation
            pass
    
    # Check TLS certificate files if specified
    ca_cert = wasm_config.get("vault_ca_cert")
    if ca_cert:
        ca_cert_path = Path(ca_cert)
        if not ca_cert_path.exists():
            errors.append(f"Vault CA certificate file not found: {ca_cert_path}")
        elif not ca_cert_path.is_file():
            errors.append(f"Vault CA certificate path is not a file: {ca_cert_path}")
    
    client_cert = wasm_config.get("vault_client_cert")
    if client_cert:
        client_cert_path = Path(client_cert)
        if not client_cert_path.exists():
            errors.append(f"Vault client certificate file not found: {client_cert_path}")
    
    client_key = wasm_config.get("vault_client_key")
    if client_key:
        client_key_path = Path(client_key)
        if not client_key_path.exists():
            errors.append(f"Vault client key file not found: {client_key_path}")
        else:
            # Check permissions on client key
            errors.extend(_check_file_permissions(client_key_path, "Vault client key"))
    
    return errors


def _check_hsm_accessibility(wasm_config: Dict[str, Any]) -> List[str]:
    """
    Check HSM (Hardware Security Module) accessibility and authentication.
    
    Args:
        wasm_config: WASM module integrity configuration
        
    Returns:
        List of accessibility error messages
    """
    errors = []
    
    # Check HSM library accessibility
    library_path = wasm_config.get("hsm_library_path")
    if library_path:
        lib_path = Path(library_path)
        if not lib_path.exists():
            errors.append(f"HSM library file not found: {lib_path}")
        elif not lib_path.is_file():
            errors.append(f"HSM library path is not a file: {lib_path}")
        else:
            # Check if library is executable/loadable
            try:
                if not os.access(lib_path, os.R_OK):
                    errors.append(f"HSM library file is not readable: {lib_path}")
                # On Unix systems, shared libraries should be executable
                if platform.system() != "Windows" and not os.access(lib_path, os.X_OK):
                    errors.append(f"HSM library file is not executable: {lib_path}")
            except Exception as e:
                errors.append(f"Error checking HSM library accessibility: {e}")
    
    # Check HSM PIN availability
    pin_env_var = wasm_config.get("hsm_pin_env_var", "HSM_PIN")
    if not os.environ.get(pin_env_var):
        errors.append(f"HSM PIN not available via environment variable '{pin_env_var}'")
    
    # Validate slot ID is reasonable (basic sanity check)
    slot_id = wasm_config.get("hsm_slot_id")
    if isinstance(slot_id, int) and (slot_id < 0 or slot_id > 65535):
        errors.append(f"HSM slot ID {slot_id} is outside reasonable range (0-65535)")
    
    # Check token label is provided
    token_label = wasm_config.get("hsm_token_label")
    if not token_label:
        errors.append("HSM token label is required but not specified")
    
    return errors


def validate_key_accessibility(config: Dict[str, Any]) -> List[str]:
    """
    Validate that keys are accessible based on current configuration.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if "wasm_module_integrity" not in config:
        return ["Missing 'wasm_module_integrity' configuration section"]
    
    wasm_config = config["wasm_module_integrity"]
    key_source = wasm_config.get("key_source")
    
    if key_source == "environment":
        # Check if environment variables are set
        public_env_var = wasm_config.get("public_key_env_var", "FAVA_PQC_PUBLIC_KEY")
        private_env_var = wasm_config.get("private_key_env_var", "FAVA_PQC_PRIVATE_KEY")
        
        if not os.environ.get(public_env_var):
            errors.append(f"Environment variable '{public_env_var}' not set")
        
        if not os.environ.get(private_env_var):
            errors.append(f"Environment variable '{private_env_var}' not set")
    
    elif key_source == "file":
        # Check if key files exist and have correct permissions
        key_path = Path(wasm_config.get("key_file_path", "/etc/fava/keys/"))
        signature_algorithm = wasm_config.get("signature_algorithm", "Dilithium3")
        
        public_file = key_path / f"public_key.{signature_algorithm.lower()}"
        private_file = key_path / f"private_key.{signature_algorithm.lower()}"
        
        if not public_file.exists():
            errors.append(f"Public key file not found: {public_file}")
        else:
            # Check permissions for public key (should be readable)
            try:
                if not public_file.is_file():
                    errors.append(f"Public key path is not a file: {public_file}")
                elif not os.access(public_file, os.R_OK):
                    errors.append(f"Public key file is not readable: {public_file}")
            except Exception as e:
                errors.append(f"Error checking public key file: {e}")
        
        if not private_file.exists():
            errors.append(f"Private key file not found: {private_file}")
        else:
            # Check permissions for private key (should be 600)
            try:
                if not private_file.is_file():
                    errors.append(f"Private key path is not a file: {private_file}")
                elif not os.access(private_file, os.R_OK):
                    errors.append(f"Private key file is not readable: {private_file}")
                else:
                    # Check file permissions (cross-platform)
                    errors.extend(_check_file_permissions(private_file, "private key"))
            except Exception as e:
                errors.append(f"Error checking private key file: {e}")
    
    elif key_source == "vault":
        # Check Vault connectivity and authentication
        errors.extend(_check_vault_accessibility(wasm_config))
    
    elif key_source == "hsm":
        # Check HSM availability and authentication
        errors.extend(_check_hsm_accessibility(wasm_config))
    
    return errors


def validate_full_pqc_configuration(config: Dict[str, Any]) -> List[str]:
    """
    Perform comprehensive validation of PQC configuration.
    
    Args:
        config: The full configuration dictionary
        
    Returns:
        List of all validation error messages
    """
    errors = []
    
    # Validate basic structure
    errors.extend(validate_wasm_module_integrity_config(config))
    
    # Validate key accessibility if basic structure is valid
    if not errors:  # Only check accessibility if structure is valid
        errors.extend(validate_key_accessibility(config))
    
    # Validate TLS configuration (existing functionality)
    known_kems = detect_available_python_pqc_kems()
    errors.extend(validate_pqc_tls_embedded_server_options(config, known_kems))
    
    return errors


def get_configuration_recommendations(config: Dict[str, Any]) -> List[str]:
    """
    Provide security recommendations for PQC configuration.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        List of security recommendations
    """
    recommendations = []
    
    if "wasm_module_integrity" not in config:
        return recommendations
    
    wasm_config = config["wasm_module_integrity"]
    
    # Key source recommendations
    key_source = wasm_config.get("key_source", "environment")
    if key_source == "environment":
        recommendations.append(
            "SECURITY: Environment variable key storage is suitable for development "
            "but consider file-based or HSM storage for production"
        )
    
    # Key rotation recommendations
    rotation_enabled = wasm_config.get("key_rotation_enabled", True)
    if not rotation_enabled:
        recommendations.append(
            "SECURITY: Key rotation is disabled. Enable rotation for better security"
        )
    else:
        interval = wasm_config.get("key_rotation_interval_days", 90)
        if interval > 365:
            recommendations.append(
                f"SECURITY: Key rotation interval is very long ({interval} days). "
                "Consider shorter intervals for better security"
            )
    
    # Algorithm recommendations
    algorithm = wasm_config.get("signature_algorithm", "Dilithium3")
    if algorithm in ["Dilithium2", "Falcon-512"]:
        recommendations.append(
            f"SECURITY: {algorithm} provides NIST Level 1 security. "
            "Consider Dilithium3 or Falcon-1024 for higher security levels"
        )
    
    return recommendations


def generate_configuration_report(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive configuration report for enterprise monitoring.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        Dictionary containing validation results, recommendations, and metrics
    """
    errors = validate_full_pqc_configuration(config)
    recommendations = get_configuration_recommendations(config)
    
    # Calculate configuration health score
    total_checks = 10  # Base number of configuration checks
    error_count = len(errors)
    warning_count = len([r for r in recommendations if r.startswith("SECURITY:")])
    
    health_score = max(0, ((total_checks - error_count - (warning_count * 0.5)) / total_checks) * 100)
    
    # Determine security level
    wasm_config = config.get("wasm_module_integrity", {})
    key_source = wasm_config.get("key_source", "environment")
    signature_algorithm = wasm_config.get("signature_algorithm", "Dilithium3")
    
    security_level = "Basic"
    if key_source in ["vault", "hsm"]:
        security_level = "Enterprise"
    elif key_source == "file":
        security_level = "Production"
    elif key_source == "environment":
        security_level = "Development"
    
    # Check for enterprise features
    enterprise_features = {
        "key_rotation_enabled": wasm_config.get("key_rotation_enabled", False),
        "vault_integration": key_source == "vault",
        "hsm_integration": key_source == "hsm",
        "cross_platform_compatibility": True,  # Now supported
        "comprehensive_validation": True,  # Now implemented
    }
    
    return {
        "validation_status": "PASS" if not errors else "FAIL",
        "health_score": round(health_score, 1),
        "security_level": security_level,
        "errors": errors,
        "recommendations": recommendations,
        "enterprise_features": enterprise_features,
        "configuration_summary": {
            "key_source": key_source,
            "signature_algorithm": signature_algorithm,
            "rotation_enabled": wasm_config.get("key_rotation_enabled", False),
            "verification_enabled": wasm_config.get("verification_enabled", True),
        },
        "compliance_status": {
            "nist_pqc_ready": signature_algorithm in VALID_SIGNATURE_ALGORITHMS,
            "enterprise_ready": security_level in ["Enterprise", "Production"],
            "rotation_compliant": wasm_config.get("key_rotation_enabled", False),
        }
    }


def validate_enterprise_compliance(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration against enterprise compliance requirements.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        Dictionary containing compliance validation results
    """
    compliance_results = {
        "overall_status": "COMPLIANT",
        "requirements": {},
        "score": 0,
        "total_requirements": 8
    }
    
    wasm_config = config.get("wasm_module_integrity", {})
    
    # Requirement 1: Strong signature algorithm
    signature_algorithm = wasm_config.get("signature_algorithm", "")
    if signature_algorithm in ["Dilithium3", "Dilithium5", "Falcon-1024"]:
        compliance_results["requirements"]["strong_signatures"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["strong_signatures"] = "FAIL"
        compliance_results["overall_status"] = "NON_COMPLIANT"
    
    # Requirement 2: Secure key storage
    key_source = wasm_config.get("key_source", "")
    if key_source in ["vault", "hsm"]:
        compliance_results["requirements"]["secure_key_storage"] = "PASS"
        compliance_results["score"] += 1
    elif key_source == "file":
        compliance_results["requirements"]["secure_key_storage"] = "PARTIAL"
        compliance_results["score"] += 0.5
    else:
        compliance_results["requirements"]["secure_key_storage"] = "FAIL"
        compliance_results["overall_status"] = "NON_COMPLIANT"
    
    # Requirement 3: Key rotation enabled
    if wasm_config.get("key_rotation_enabled", False):
        compliance_results["requirements"]["key_rotation"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["key_rotation"] = "FAIL"
        compliance_results["overall_status"] = "NON_COMPLIANT"
    
    # Requirement 4: Reasonable rotation interval
    rotation_interval = wasm_config.get("key_rotation_interval_days", 0)
    if 30 <= rotation_interval <= 365:
        compliance_results["requirements"]["rotation_interval"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["rotation_interval"] = "FAIL"
    
    # Requirement 5: Module integrity verification
    if wasm_config.get("verification_enabled", True):
        compliance_results["requirements"]["integrity_verification"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["integrity_verification"] = "FAIL"
        compliance_results["overall_status"] = "NON_COMPLIANT"
    
    # Requirement 6: No hardcoded keys
    if "public_key_base64" not in wasm_config:
        compliance_results["requirements"]["no_hardcoded_keys"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["no_hardcoded_keys"] = "FAIL"
        compliance_results["overall_status"] = "NON_COMPLIANT"
    
    # Requirement 7: Proper TLS configuration
    tls_verify = wasm_config.get("vault_tls_verify", True) if key_source == "vault" else True
    if tls_verify:
        compliance_results["requirements"]["tls_security"] = "PASS"
        compliance_results["score"] += 1
    else:
        compliance_results["requirements"]["tls_security"] = "FAIL"
    
    # Requirement 8: Environment-specific security
    if key_source == "hsm":
        # HSM requires PIN protection
        if wasm_config.get("hsm_pin_env_var"):
            compliance_results["requirements"]["environment_security"] = "PASS"
            compliance_results["score"] += 1
        else:
            compliance_results["requirements"]["environment_security"] = "FAIL"
    elif key_source == "vault":
        # Vault requires proper authentication
        auth_method = wasm_config.get("vault_auth_method", "")
        if auth_method in ["tls", "kubernetes", "aws"]:
            compliance_results["requirements"]["environment_security"] = "PASS"
            compliance_results["score"] += 1
        else:
            compliance_results["requirements"]["environment_security"] = "PARTIAL"
            compliance_results["score"] += 0.5
    else:
        compliance_results["requirements"]["environment_security"] = "PARTIAL"
        compliance_results["score"] += 0.5
    
    # Calculate final compliance percentage
    compliance_percentage = (compliance_results["score"] / compliance_results["total_requirements"]) * 100
    compliance_results["compliance_percentage"] = round(compliance_percentage, 1)
    
    return compliance_results


def export_configuration_audit_log(config: Dict[str, Any], output_file: str = None) -> str:
    """
    Export configuration audit log for enterprise compliance tracking.
    
    Args:
        config: The configuration dictionary
        output_file: Optional file path to save the audit log
        
    Returns:
        JSON-formatted audit log string
    """
    import json
    from datetime import datetime, timezone
    
    audit_data = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_version": "1.0",
        "configuration_report": generate_configuration_report(config),
        "compliance_validation": validate_enterprise_compliance(config),
        "system_information": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }
    }
    
    audit_json = json.dumps(audit_data, indent=2, sort_keys=True)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(audit_json)
        except Exception as e:
            print(f"Warning: Could not write audit log to {output_file}: {e}")
    
    return audit_json