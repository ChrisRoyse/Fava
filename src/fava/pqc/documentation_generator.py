# src/fava/pqc/documentation_generator.py
"""
Module for generating PQC-related documentation sections for Fava.
"""
from typing import List

# Default KEM recommendation, can be updated based on research
DEFAULT_KEM_RECOMMENDATION = "X25519Kyber768"

def generate_pqc_tls_reverse_proxy_config_guide(
    proxy_type: str,
    kem_recommendation: str = DEFAULT_KEM_RECOMMENDATION,
    relevant_research_docs: List[str] = None,
) -> str:
    """
    Generates Markdown documentation for configuring a specific reverse proxy
    for PQC-TLS. Based on pseudocode.
    """
    if relevant_research_docs is None:
        relevant_research_docs = []

    doc_parts = [
        f"# Securing Fava with Post-Quantum TLS (Experimental) via {proxy_type}\n",
        f"To protect Fava's data in transit against future quantum threats, "
        f"configure your {proxy_type} reverse proxy to use Post-Quantum "
        f"Cryptography (PQC) hybrid Key Encapsulation Mechanisms (KEMs) for "
        f"TLS 1.3.\n",
        f"The currently recommended hybrid KEM is `{kem_recommendation}`.\n",
        f"This setup relies on experimental features in browsers and server "
        f"software. Always consult the latest official documentation for "
        f"{proxy_type}, OpenSSL (or its variant), and the OQS project.\n",
    ]
    if relevant_research_docs:
        research_links = ", ".join(
            [f"[`{doc}`](../../docs/research/{doc})" for doc in relevant_research_docs]
        ) # Assuming research docs are in docs/research
        doc_parts.append(
            f"Refer to Fava's research documents for more background: {research_links}\n"
        )

# Insert PQC-DIT-ARCH-001 Warning
    warning_section_str = (
        "\n## ⚠️ CRITICAL SECURITY WARNING: Securing the Reverse Proxy to Fava Link ⚠️\n\n"
        "The PQC-TLS configuration described above secures the connection between the user's browser and your reverse proxy. "
        "However, **by default, the connection between your reverse proxy and the Fava application server is plain HTTP.**\n\n"
        "**Risk (PQC-DIT-ARCH-001):** If your reverse proxy and Fava are not on the same host "
        "(communicating strictly via `localhost` or a secure Unix socket) OR are not within a physically or "
        "virtually secured private network segment, this unencrypted HTTP link is vulnerable to eavesdropping and modification. "
        "This would **undermine the end-to-end security** provided by PQC-TLS to the client.\n\n"
        "**You MUST secure this internal link if it traverses an untrusted network.**\n\n"
        "### Recommended Mitigation Strategies:\n\n"
        "1.  **Configure Fava for HTTPS (Recommended for different hosts):**\n"
        "    *   Set up Fava to listen on HTTPS for its internal connection from the proxy.\n"
        "    *   Configure your reverse proxy to connect to Fava using `https://` for the `proxy_pass` (or equivalent) directive.\n"
        "    *   This involves generating a separate TLS certificate for Fava's internal use.\n\n"
        "2.  **Mutual TLS (mTLS):**\n"
        "    *   Implement mTLS between the reverse proxy and Fava for strong mutual authentication and encryption. "
        "This requires both Fava and the proxy to present and validate certificates.\n\n"
        "3.  **IPSec or Network-Layer Encryption:**\n"
        "    *   If Fava and the proxy are on different hosts in an untrusted network segment, "
        "use an IPSec tunnel or a similar network-layer encryption mechanism (e.g., WireGuard) to secure all traffic between them.\n\n"
        "4.  **Same Host: Restrict to Localhost:**\n"
        "    *   If the reverse proxy and Fava are running on the **same physical host**, ensure that:\n"
        "        *   Fava listens only on a localhost interface (e.g., `127.0.0.1` or `::1`).\n"
        "        *   The reverse proxy connects to Fava via this localhost interface (e.g., `proxy_pass http://127.0.0.1:5000;`).\n"
        "    *   This significantly reduces the risk of external interception on the local machine.\n\n"
        "**Failure to address this in untrusted environments will expose your Fava data and communications.** "
        "Always refer to the Fava security documentation and the PQC Data in Transit architecture for more details.\n\n"
    )
    doc_parts.append(warning_section_str)
    if proxy_type.lower() == "nginx":
        doc_parts.extend(_generate_nginx_guide_content(kem_recommendation))
    elif proxy_type.lower() == "caddy":
        doc_parts.extend(_generate_caddy_guide_content(kem_recommendation))
    else:
        doc_parts.append(
            f"\nGuidance for {proxy_type} is not yet specifically available. "
            f"Please consult its documentation for enabling TLS 1.3 and custom KEMs "
            f"like `{kem_recommendation}`.\n"
        )
    
    doc_parts.append(
        f"\n**Note:** The PQC landscape and software support are rapidly evolving. "
        f"Use classical certificates; PQC CAs are not yet standard. Hybrid KEMs "
        f"like `{kem_recommendation}` work with classical certificates.\n"
    )
    doc_parts.append(
        "Ensure your OpenSSL configuration (`openssl.cnf`) enables PQC "
        "providers/algorithms if using a modular setup.\n"
    )
    return "".join(doc_parts)

def _generate_nginx_guide_content(kem_recommendation: str) -> List[str]:
    """Helper to generate Nginx specific part of the guide."""
    return [
        f"\n### Example: Nginx with OpenSSL (OQS Provider or PQC-enabled build)\n",
        f"This example assumes Nginx compiled with an OpenSSL version that "
        f"supports `{kem_recommendation}`.\n",
        f"1. **Install/Compile PQC-enabled Nginx and OpenSSL.** (Refer to OQS "
        f"project and Nginx documentation).\n",
        f"2. **Configure Nginx:**\n"
        f"   In your Nginx server block for Fava:\n"
        f"   ```nginx\n"
        f"   server {{\n"
        f"       listen 443 ssl http2;\n"
        f"       listen [::]:443 ssl http2;\n"
        f"       server_name fava.example.com;\n\n"
        f"       # Enable PQC KEMs (e.g., {kem_recommendation})\n"
        f"       # Consult your OpenSSL/Nginx-OQS version documentation for specific directives.\n"
        f"       # Example for TLS 1.3 groups (syntax may vary):\n"
        f"       # ssl_conf_command Groups {kem_recommendation}:X25519:secp256r1; # Prioritize PQC hybrid\n\n"
        f"       ssl_protocols TLSv1.3;\n"
        f"       ssl_prefer_server_ciphers off;\n"
        f"       ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';\n\n"
        f"       ssl_certificate /path/to/your/fullchain.pem; # Standard ECC/RSA certificate\n"
        f"       ssl_certificate_key /path/to/your/privkey.pem;\n\n"
        f"       location / {{\n"
        f"           proxy_pass http://localhost:5000; # Assuming Fava runs on port 5000\n"
        f"           proxy_set_header Host $host;\n"
        f"           # ... other proxy headers\n"
        f"       }}\n"
        f"   }}\n"
        f"   ```\n",
        f"3. **Test:** Use a browser with experimental PQC support or "
        f"`openssl s_client -groups {kem_recommendation} ...`.\n",
    ]

def _generate_caddy_guide_content(kem_recommendation: str) -> List[str]:
    """Helper to generate Caddy specific part of the guide."""
    return [
        f"\n### Example: Caddy\n",
        f"Caddy may support PQC KEMs through custom builds or future official "
        f"support. Consult Caddy documentation for enabling specific KEMs like "
        f"`{kem_recommendation}`.\n",
        f"Example (conceptual Caddyfile snippet):\n"
        f"   ```caddyfile\n"
        f"   fava.example.com {{\n"
        f"       reverse_proxy localhost:5000\n"
        f"       tls {{\n"
        f"           # Hypothetical directive for PQC KEMs\n"
        f"           # key_exchange_algorithms {kem_recommendation} x25519\n"
        f"       }}\n"
        f"   }}\n"
        f"   ```\n",
    ]

def generate_pqc_tls_contingency_guide(contingency_research_doc: str) -> str:
    """
    Generates Markdown documentation for PQC-TLS contingency plans.
    Based on pseudocode.
    """
    research_link = f"[`{contingency_research_doc}`](../../docs/research/{contingency_research_doc})"
    return (
        f"## Contingency Planning for PQC-TLS\n\n"
        f"If PQC-TLS reverse proxies prove unstable or too complex for your "
        f"environment at this time, consider the following:\n"
        f"*   **Fallback to Classical TLS:** Ensure your proxy configuration "
        f"allows fallback to robust classical TLS (e.g., TLS 1.3 with ECDHE "
        f"and AES-GCM) if PQC negotiation fails or is not supported by the client.\n"
        f"*   **Application-Layer PQC:** For extremely sensitive data, and as an "
        f"interim measure, you might explore application-layer PQC encryption "
        f"for specific data fields before they are transmitted over a classical "
        f"TLS channel. This adds complexity and is not a full substitute for PQC-TLS.\n"
        f"*   **Monitor Developments:** Keep abreast of updates in PQC standards, "
        f"browser support, and proxy software capabilities.\n\n"
        f"Refer to Fava's research on tooling and contingencies: {research_link}\n"
    )

def generate_pqc_tls_future_embedded_server_guide(
    supported_kems_by_fava_embedded: List[str],
) -> str:
    """
    Generates Markdown documentation for future PQC-TLS support in Fava's
    embedded server. Based on pseudocode.
    """
    if not supported_kems_by_fava_embedded:
        return ""

    kems_str = '", "'.join(supported_kems_by_fava_embedded)
    return (
        f"## (Future) PQC-TLS with Fava's Embedded Web Server\n\n"
        f"**Note:** This is a forward-looking section. Direct PQC-TLS support "
        f"in Fava's embedded server (e.g., Cheroot via Flask's development "
        f"server) depends on the Python `ssl` module and underlying libraries "
        f"gaining robust PQC cipher suite support, which is not standard as of "
        f"this writing.\n\n"
        f"Should such support become available, Fava might allow configuration "
        f"of PQC KEMs via Fava options.\n"
        f"Example hypothetical Fava configuration option:\n"
        f"```python\n"
        f"# In your Fava configuration file\n"
        f'PQC_TLS_EMBEDDED_SERVER_KEMS = ["{kems_str}"]\n'
        f"```\n"
        f"This would instruct Fava's embedded server, if capable, to negotiate "
        f"one of the specified PQC KEMs.\n"
        f"This is **not recommended for production use**; a dedicated reverse "
        f"proxy is always preferred for production deployments.\n"
    )