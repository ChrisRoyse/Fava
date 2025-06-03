# src/fava/pqc/configuration_validator.py
"""
Module for validating Fava configuration options, specifically future PQC
options for the embedded server.
"""
from typing import Dict, Any, List

# Configuration option name for embedded server PQC KEMs
EMBEDDED_SERVER_PQC_KEMS_OPTION: str = "pqc_tls_embedded_server_kems"


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