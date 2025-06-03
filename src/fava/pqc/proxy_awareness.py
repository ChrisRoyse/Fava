# src/fava/pqc/proxy_awareness.py
"""
Module for Fava to determine or assert PQC protection status based on
request headers or Fava's configuration.
"""
from typing import Dict, Any, List

# Define constants for PQC status, aligning with pseudocode and test plans.
# These could be moved to a central constants file if used more broadly.
PQC_CONFIRMED_VIA_HEADER = "PQC_CONFIRMED_VIA_HEADER"
PQC_ABSENT_VIA_HEADER = "PQC_ABSENT_VIA_HEADER"
PQC_UNKNOWN_VIA_HEADER = "PQC_UNKNOWN_VIA_HEADER"
PQC_ASSUMED_ENABLED_VIA_CONFIG = "PQC_ASSUMED_ENABLED_VIA_CONFIG"
PQC_ASSUMED_DISABLED_VIA_CONFIG = "PQC_ASSUMED_DISABLED_VIA_CONFIG"
PQC_STATUS_UNCERTAIN = "PQC_STATUS_UNCERTAIN"

# Configuration for PQC header inspection
KNOWN_PQC_INDICATOR_HEADER_NAME: str = "X-PQC-KEM"
RECOGNIZED_PQC_KEMS: List[str] = ["X25519Kyber768", "Kyber768"]


def check_pqc_proxy_headers(request_headers: Dict[str, Any]) -> str:
    """
    Checks request headers for a known PQC indicator.
    Based on pseudocode: `check_pqc_proxy_headers`.
    """
    header_value = request_headers.get(KNOWN_PQC_INDICATOR_HEADER_NAME)

    if header_value is None:
        return PQC_UNKNOWN_VIA_HEADER

    if not isinstance(header_value, str):
        # Malformed header value, treat as PQC absent or unrecognized
        return PQC_ABSENT_VIA_HEADER

    if header_value in RECOGNIZED_PQC_KEMS:
        return PQC_CONFIRMED_VIA_HEADER
    
    # Header present but value not a recognized PQC KEM
    return PQC_ABSENT_VIA_HEADER


def get_pqc_status_from_config(fava_config: Dict[str, Any]) -> str:
    """
    Gets PQC status based on Fava's application configuration.
    Based on pseudocode: `get_pqc_status_from_config`.
    """
    pqc_config_flag_name: str = "assume_pqc_tls_proxy_enabled"

    if fava_config.get(pqc_config_flag_name, False):
        return PQC_ASSUMED_ENABLED_VIA_CONFIG
    
    return PQC_ASSUMED_DISABLED_VIA_CONFIG


def determine_effective_pqc_status(
    request_headers: Dict[str, Any], fava_config: Dict[str, Any]
) -> str:
    """
    Determines the effective PQC status by first checking headers,
    then falling back to configuration.
    Based on pseudocode: `determine_effective_pqc_status`.
    """
    header_status = check_pqc_proxy_headers(request_headers)

    if header_status == PQC_CONFIRMED_VIA_HEADER:
        return PQC_CONFIRMED_VIA_HEADER
    if header_status == PQC_ABSENT_VIA_HEADER:
        return PQC_ABSENT_VIA_HEADER

    # If header_status is PQC_UNKNOWN_VIA_HEADER, fall back to config
    config_status = get_pqc_status_from_config(fava_config)
    if config_status == PQC_ASSUMED_ENABLED_VIA_CONFIG:
        return PQC_ASSUMED_ENABLED_VIA_CONFIG
    
    # Config status is PQC_ASSUMED_DISABLED_VIA_CONFIG
    return PQC_STATUS_UNCERTAIN