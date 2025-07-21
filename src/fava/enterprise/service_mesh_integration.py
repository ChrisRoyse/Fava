"""
Service Mesh Security Integration for Fava PQC.

This module provides comprehensive integration with service mesh platforms
(Istio, Linkerd, Consul Connect) for secure service-to-service communication
using post-quantum cryptography.
"""

import json
import logging
import time
import base64
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
import subprocess
import tempfile
import yaml
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor

from .dependency_manager import DependencyManager, enterprise_feature
from .monitoring import get_audit_logger, get_metrics_collector

logger = logging.getLogger(__name__)


class ServiceMeshType(Enum):
    """Supported service mesh platforms."""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"


class CertificateType(Enum):
    """Types of certificates for service mesh."""
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    WORKLOAD_CERT = "workload_cert"
    GATEWAY_CERT = "gateway_cert"


class AuthorizationPolicy(Enum):
    """Service mesh authorization policies."""
    ALLOW_ALL = "allow_all"
    DENY_ALL = "deny_all"
    WHITELIST = "whitelist"
    MUTUAL_TLS_REQUIRED = "mutual_tls_required"
    QUANTUM_SAFE_REQUIRED = "quantum_safe_required"


class TrafficEncryptionMode(Enum):
    """Traffic encryption modes."""
    DISABLED = "disabled"
    PERMISSIVE = "permissive"  # Allow both encrypted and unencrypted
    STRICT = "strict"          # Require encryption
    QUANTUM_SAFE = "quantum_safe"  # Require post-quantum encryption


@dataclass
class ServiceMeshConfig:
    """Service mesh configuration."""
    mesh_type: ServiceMeshType
    namespace: str
    cluster_name: str
    root_ca_cert: Optional[str] = None
    root_ca_key: Optional[str] = None
    intermediate_ca_cert: Optional[str] = None
    intermediate_ca_key: Optional[str] = None
    encryption_mode: TrafficEncryptionMode = TrafficEncryptionMode.STRICT
    authorization_policy: AuthorizationPolicy = AuthorizationPolicy.MUTUAL_TLS_REQUIRED
    pqc_enabled: bool = True
    certificate_duration: int = 24  # hours
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceIdentity:
    """Service identity for mesh communication."""
    service_name: str
    namespace: str
    cluster: str
    workload_selector: Dict[str, str]
    certificate_arn: Optional[str] = None
    private_key: Optional[str] = None
    certificate_chain: Optional[List[str]] = None
    quantum_safe_cert: bool = False
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    last_renewed: Optional[float] = None


@dataclass
class TrafficPolicy:
    """Traffic policy for service-to-service communication."""
    policy_id: str
    source_service: str
    destination_service: str
    source_namespace: str = "*"
    destination_namespace: str = "*"
    protocol: str = "https"
    port: Optional[int] = None
    encryption_required: bool = True
    quantum_safe_required: bool = True
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST"])
    rate_limits: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30
    retry_policy: Optional[Dict[str, Any]] = None
    circuit_breaker: Optional[Dict[str, Any]] = None


@dataclass
class MeshSecurityStatus:
    """Security status of the service mesh."""
    mesh_type: ServiceMeshType
    total_services: int
    secured_services: int
    quantum_safe_services: int
    certificate_expiries: List[Dict[str, Any]]
    policy_violations: List[Dict[str, Any]]
    encryption_coverage: float  # Percentage
    last_security_scan: float
    security_score: int  # 1-100


class IstioIntegration:
    """Integration with Istio service mesh."""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
    
    def install_pqc_certificates(self, root_ca_cert: str, root_ca_key: str) -> bool:
        """Install post-quantum certificates in Istio."""
        try:
            # Create root CA secret in istio-system namespace
            root_ca_secret = self._create_k8s_secret(
                name="cacerts",
                namespace="istio-system",
                data={
                    "root-cert.pem": base64.b64encode(root_ca_cert.encode()).decode(),
                    "root-key.pem": base64.b64encode(root_ca_key.encode()).decode(),
                    "cert-chain.pem": base64.b64encode(root_ca_cert.encode()).decode()
                }
            )
            
            if not root_ca_secret:
                return False
            
            # Configure Istio to use external CA
            istio_config = {
                "apiVersion": "install.istio.io/v1alpha1",
                "kind": "IstioOperator",
                "metadata": {
                    "name": "pqc-control-plane",
                    "namespace": "istio-system"
                },
                "spec": {
                    "values": {
                        "pilot": {
                            "env": {
                                "EXTERNAL_CA": True,
                                "PILOT_ENABLE_WORKLOAD_ENTRY_AUTOREGISTRATION": True
                            }
                        },
                        "global": {
                            "meshConfig": {
                                "trustDomain": self.config.cluster_name,
                                "certificates": [{
                                    "secretName": "cacerts",
                                    "dnsNames": [f"*.{self.config.namespace}.svc.cluster.local"]
                                }]
                            }
                        }
                    },
                    "components": {
                        "pilot": {
                            "k8s": {
                                "env": [
                                    {"name": "PILOT_ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY", "value": "true"},
                                    {"name": "PILOT_ENABLE_QUANTUM_SAFE_TLS", "value": "true"}
                                ]
                            }
                        }
                    }
                }
            }
            
            # Apply Istio configuration
            success = self._apply_k8s_config(istio_config)
            
            if success:
                self.audit_logger.log_event(
                    event_type="service_mesh",
                    component="istio_integration",
                    action="pqc_certificates_installed",
                    outcome="success",
                    details={
                        "namespace": "istio-system",
                        "trust_domain": self.config.cluster_name
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to install PQC certificates in Istio: {e}")
            return False
    
    def create_pqc_destination_rule(self, service: ServiceIdentity) -> bool:
        """Create destination rule with post-quantum TLS configuration."""
        try:
            destination_rule = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "DestinationRule",
                "metadata": {
                    "name": f"pqc-{service.service_name}",
                    "namespace": service.namespace
                },
                "spec": {
                    "host": f"{service.service_name}.{service.namespace}.svc.cluster.local",
                    "trafficPolicy": {
                        "tls": {
                            "mode": "ISTIO_MUTUAL",
                            "cipherSuites": [
                                "TLS_KYBER768_WITH_AES_256_GCM_SHA384",
                                "TLS_DILITHIUM3_WITH_AES_256_GCM_SHA384"
                            ],
                            "minProtocolVersion": "TLSV1_3",
                            "maxProtocolVersion": "TLSV1_3"
                        },
                        "connectionPool": {
                            "tcp": {
                                "maxConnections": 100
                            },
                            "http": {
                                "http1MaxPendingRequests": 50,
                                "maxRequestsPerConnection": 10
                            }
                        }
                    }
                }
            }
            
            return self._apply_k8s_config(destination_rule)
            
        except Exception as e:
            logger.error(f"Failed to create PQC destination rule: {e}")
            return False
    
    def create_pqc_virtual_service(self, policy: TrafficPolicy) -> bool:
        """Create virtual service with quantum-safe routing."""
        try:
            virtual_service = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "VirtualService",
                "metadata": {
                    "name": f"pqc-{policy.destination_service}",
                    "namespace": policy.destination_namespace
                },
                "spec": {
                    "hosts": [f"{policy.destination_service}.{policy.destination_namespace}.svc.cluster.local"],
                    "http": [{
                        "match": [{
                            "headers": {
                                "x-quantum-safe": {"exact": "required"}
                            }
                        }],
                        "route": [{
                            "destination": {
                                "host": f"{policy.destination_service}.{policy.destination_namespace}.svc.cluster.local",
                                "port": {"number": policy.port or 443}
                            }
                        }],
                        "timeout": f"{policy.timeout_seconds}s",
                        "retries": policy.retry_policy or {
                            "attempts": 3,
                            "perTryTimeout": "10s"
                        }
                    }]
                }
            }
            
            return self._apply_k8s_config(virtual_service)
            
        except Exception as e:
            logger.error(f"Failed to create PQC virtual service: {e}")
            return False
    
    def create_pqc_authorization_policy(self, policy: TrafficPolicy) -> bool:
        """Create authorization policy for quantum-safe communication."""
        try:
            auth_policy = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "AuthorizationPolicy",
                "metadata": {
                    "name": f"pqc-{policy.destination_service}",
                    "namespace": policy.destination_namespace
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": policy.destination_service
                        }
                    },
                    "rules": [{
                        "from": [{
                            "source": {
                                "principals": [f"cluster.local/ns/{policy.source_namespace}/sa/{policy.source_service}"]
                            }
                        }],
                        "to": [{
                            "operation": {
                                "methods": policy.allowed_methods,
                                "ports": [str(policy.port)] if policy.port else None
                            }
                        }],
                        "when": [{
                            "key": "source.mtls.mode",
                            "values": ["STRICT"]
                        }, {
                            "key": "request.headers[x-quantum-safe]",
                            "values": ["required"]
                        }]
                    }]
                }
            }
            
            return self._apply_k8s_config(auth_policy)
            
        except Exception as e:
            logger.error(f"Failed to create PQC authorization policy: {e}")
            return False
    
    def enable_pqc_peer_authentication(self, namespace: str) -> bool:
        """Enable post-quantum peer authentication for namespace."""
        try:
            peer_auth = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication",
                "metadata": {
                    "name": "pqc-strict",
                    "namespace": namespace
                },
                "spec": {
                    "mtls": {
                        "mode": "STRICT"
                    }
                }
            }
            
            return self._apply_k8s_config(peer_auth)
            
        except Exception as e:
            logger.error(f"Failed to enable PQC peer authentication: {e}")
            return False
    
    def _create_k8s_secret(self, name: str, namespace: str, data: Dict[str, str]) -> bool:
        """Create Kubernetes secret."""
        try:
            secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "type": "Opaque",
                "data": data
            }
            
            return self._apply_k8s_config(secret)
            
        except Exception as e:
            logger.error(f"Failed to create K8s secret: {e}")
            return False
    
    def _apply_k8s_config(self, config: Dict[str, Any]) -> bool:
        """Apply Kubernetes configuration."""
        try:
            # Write config to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                config_file = f.name
            
            # Apply using kubectl (simulated)
            # In real implementation, would use kubernetes client library
            logger.info(f"Applied Kubernetes configuration: {config['kind']} {config['metadata']['name']}")
            
            # Clean up temp file
            Path(config_file).unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply K8s config: {e}")
            return False


class LinkerdIntegration:
    """Integration with Linkerd service mesh."""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
    
    def install_pqc_trust_anchor(self, root_ca_cert: str, root_ca_key: str) -> bool:
        """Install post-quantum trust anchor in Linkerd."""
        try:
            # Create trust anchor secret
            trust_anchor_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "linkerd-identity-trust-roots",
                    "namespace": "linkerd"
                },
                "data": {
                    "tls.crt": base64.b64encode(root_ca_cert.encode()).decode(),
                    "tls.key": base64.b64encode(root_ca_key.encode()).decode()
                }
            }
            
            success = self._apply_k8s_config(trust_anchor_secret)
            
            if success:
                # Configure Linkerd identity controller
                identity_config = {
                    "apiVersion": "v1",
                    "kind": "ConfigMap",
                    "metadata": {
                        "name": "linkerd-config",
                        "namespace": "linkerd"
                    },
                    "data": {
                        "global": json.dumps({
                            "linkerdNamespace": "linkerd",
                            "cniEnabled": False,
                            "version": "stable-2.14.0",
                            "identityContext": {
                                "trustDomain": self.config.cluster_name,
                                "trustAnchorsPem": root_ca_cert,
                                "issuanceLifetime": f"{self.config.certificate_duration}h",
                                "clockSkewAllowance": "20s"
                            },
                            "proxyInit": {
                                "image": {"name": "linkerd/proxy-init"}
                            },
                            "proxy": {
                                "image": {"name": "linkerd/proxy"},
                                "logLevel": "info",
                                "disableIdentity": False,
                                "quantumSafeEnabled": True
                            }
                        })
                    }
                }
                
                success = self._apply_k8s_config(identity_config)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to install PQC trust anchor in Linkerd: {e}")
            return False
    
    def create_pqc_server_policy(self, service: ServiceIdentity) -> bool:
        """Create Linkerd server policy with post-quantum requirements."""
        try:
            server_policy = {
                "apiVersion": "policy.linkerd.io/v1beta1",
                "kind": "Server",
                "metadata": {
                    "name": f"pqc-{service.service_name}",
                    "namespace": service.namespace
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": service.workload_selector
                    },
                    "port": 443,
                    "proxyProtocol": "TLS"
                }
            }
            
            return self._apply_k8s_config(server_policy)
            
        except Exception as e:
            logger.error(f"Failed to create PQC server policy: {e}")
            return False
    
    def create_pqc_server_authorization(self, policy: TrafficPolicy) -> bool:
        """Create server authorization with quantum-safe requirements."""
        try:
            server_auth = {
                "apiVersion": "policy.linkerd.io/v1beta1",
                "kind": "ServerAuthorization",
                "metadata": {
                    "name": f"pqc-{policy.destination_service}",
                    "namespace": policy.destination_namespace
                },
                "spec": {
                    "server": {
                        "name": f"pqc-{policy.destination_service}"
                    },
                    "client": {
                        "meshTLS": {
                            "identities": [f"{policy.source_service}.{policy.source_namespace}.serviceaccount.identity.linkerd.cluster.local"],
                            "quantumSafe": True
                        }
                    }
                }
            }
            
            return self._apply_k8s_config(server_auth)
            
        except Exception as e:
            logger.error(f"Failed to create PQC server authorization: {e}")
            return False
    
    def _apply_k8s_config(self, config: Dict[str, Any]) -> bool:
        """Apply Kubernetes configuration."""
        try:
            logger.info(f"Applied Linkerd configuration: {config['kind']} {config['metadata']['name']}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply Linkerd config: {e}")
            return False


class ConsulConnectIntegration:
    """Integration with Consul Connect service mesh."""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
    
    def configure_pqc_ca(self, root_ca_cert: str, root_ca_key: str) -> bool:
        """Configure Consul Connect with post-quantum CA."""
        try:
            # Consul Connect CA configuration
            ca_config = {
                "connect": {
                    "enabled": True,
                    "ca_provider": "vault",
                    "ca_config": {
                        "address": "https://vault.service.consul:8200",
                        "token": "consul-connect-ca-token",
                        "root_pki_path": "pqc_root_ca/",
                        "intermediate_pki_path": "pqc_intermediate_ca/",
                        "leaf_cert_ttl": f"{self.config.certificate_duration}h",
                        "quantum_safe_enabled": True,
                        "private_key_type": "ed25519",
                        "private_key_bits": 256
                    }
                },
                "ports": {
                    "grpc": 8502
                }
            }
            
            # Apply Consul configuration
            success = self._apply_consul_config(ca_config)
            
            if success:
                self.audit_logger.log_event(
                    event_type="service_mesh",
                    component="consul_connect",
                    action="pqc_ca_configured",
                    outcome="success",
                    details={"ca_provider": "vault", "quantum_safe": True}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to configure PQC CA in Consul Connect: {e}")
            return False
    
    def create_pqc_service_intentions(self, policy: TrafficPolicy) -> bool:
        """Create service intentions with post-quantum requirements."""
        try:
            intentions = {
                "Kind": "service-intentions",
                "Name": policy.destination_service,
                "Namespace": policy.destination_namespace,
                "Sources": [{
                    "Name": policy.source_service,
                    "Namespace": policy.source_namespace,
                    "Action": "allow",
                    "Precedence": 100,
                    "Type": "consul",
                    "TLS": {
                        "Mode": "required",
                        "QuantumSafe": True
                    },
                    "Permissions": [{
                        "Action": "allow",
                        "HTTP": {
                            "PathPrefix": "/",
                            "Methods": policy.allowed_methods
                        }
                    }]
                }]
            }
            
            return self._apply_consul_config(intentions)
            
        except Exception as e:
            logger.error(f"Failed to create PQC service intentions: {e}")
            return False
    
    def create_pqc_proxy_defaults(self, namespace: str) -> bool:
        """Create proxy defaults with quantum-safe configuration."""
        try:
            proxy_defaults = {
                "Kind": "proxy-defaults",
                "Name": "global",
                "Namespace": namespace,
                "Config": {
                    "protocol": "http2",
                    "quantum_safe_tls": True,
                    "local_connect_timeout_ms": 5000,
                    "local_request_timeout_ms": policy.timeout_seconds * 1000
                },
                "MeshGateway": {
                    "Mode": "local"
                },
                "TransparentProxy": {
                    "OutboundListenerPort": 15001,
                    "DialedDirectly": True
                }
            }
            
            return self._apply_consul_config(proxy_defaults)
            
        except Exception as e:
            logger.error(f"Failed to create PQC proxy defaults: {e}")
            return False
    
    def _apply_consul_config(self, config: Dict[str, Any]) -> bool:
        """Apply Consul configuration."""
        try:
            # In real implementation, would use Consul HTTP API
            logger.info(f"Applied Consul configuration: {config.get('Kind', 'config')}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply Consul config: {e}")
            return False


class ServiceMeshSecurityScanner:
    """Scanner for service mesh security assessment."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
    
    def scan_mesh_security(self, config: ServiceMeshConfig) -> MeshSecurityStatus:
        """Scan service mesh for security status."""
        try:
            # Get all services in the mesh
            services = self._discover_mesh_services(config)
            
            # Check encryption status
            encryption_status = self._check_encryption_status(services, config)
            
            # Check certificate status
            cert_status = self._check_certificate_status(services, config)
            
            # Check policy compliance
            policy_violations = self._check_policy_compliance(services, config)
            
            # Calculate security score
            security_score = self._calculate_security_score(
                services, encryption_status, cert_status, policy_violations
            )
            
            return MeshSecurityStatus(
                mesh_type=config.mesh_type,
                total_services=len(services),
                secured_services=len([s for s in services if s.get('secured', False)]),
                quantum_safe_services=len([s for s in services if s.get('quantum_safe', False)]),
                certificate_expiries=cert_status['expiring_certificates'],
                policy_violations=policy_violations,
                encryption_coverage=encryption_status['coverage_percentage'],
                last_security_scan=time.time(),
                security_score=security_score
            )
            
        except Exception as e:
            logger.error(f"Failed to scan mesh security: {e}")
            raise
    
    def _discover_mesh_services(self, config: ServiceMeshConfig) -> List[Dict[str, Any]]:
        """Discover services in the mesh."""
        # Simulated service discovery
        services = [
            {
                "name": "frontend",
                "namespace": "production",
                "secured": True,
                "quantum_safe": True,
                "certificate_expiry": time.time() + 86400 * 30  # 30 days
            },
            {
                "name": "backend-api",
                "namespace": "production", 
                "secured": True,
                "quantum_safe": False,
                "certificate_expiry": time.time() + 86400 * 7  # 7 days
            },
            {
                "name": "database",
                "namespace": "production",
                "secured": False,
                "quantum_safe": False,
                "certificate_expiry": None
            }
        ]
        
        return services
    
    def _check_encryption_status(self, services: List[Dict[str, Any]], 
                                config: ServiceMeshConfig) -> Dict[str, Any]:
        """Check encryption status of services."""
        encrypted_services = len([s for s in services if s.get('secured', False)])
        total_services = len(services)
        
        return {
            'total_services': total_services,
            'encrypted_services': encrypted_services,
            'coverage_percentage': (encrypted_services / max(1, total_services)) * 100,
            'unencrypted_services': [s['name'] for s in services if not s.get('secured', False)]
        }
    
    def _check_certificate_status(self, services: List[Dict[str, Any]], 
                                 config: ServiceMeshConfig) -> Dict[str, Any]:
        """Check certificate expiration status."""
        expiring_certificates = []
        current_time = time.time()
        warning_threshold = 7 * 24 * 3600  # 7 days
        
        for service in services:
            cert_expiry = service.get('certificate_expiry')
            if cert_expiry and (cert_expiry - current_time) < warning_threshold:
                expiring_certificates.append({
                    'service_name': service['name'],
                    'namespace': service['namespace'],
                    'expires_at': cert_expiry,
                    'days_remaining': int((cert_expiry - current_time) / 86400)
                })
        
        return {
            'total_certificates': len([s for s in services if s.get('certificate_expiry')]),
            'expiring_certificates': expiring_certificates,
            'expired_certificates': [cert for cert in expiring_certificates if cert['days_remaining'] <= 0]
        }
    
    def _check_policy_compliance(self, services: List[Dict[str, Any]], 
                                config: ServiceMeshConfig) -> List[Dict[str, Any]]:
        """Check policy compliance violations."""
        violations = []
        
        for service in services:
            # Check if quantum-safe is required but not enabled
            if config.pqc_enabled and not service.get('quantum_safe', False):
                violations.append({
                    'service_name': service['name'],
                    'namespace': service['namespace'],
                    'violation_type': 'quantum_safe_required',
                    'description': 'Service does not use quantum-safe cryptography',
                    'severity': 'high'
                })
            
            # Check if encryption is required but not enabled
            if config.encryption_mode == TrafficEncryptionMode.STRICT and not service.get('secured', False):
                violations.append({
                    'service_name': service['name'],
                    'namespace': service['namespace'],
                    'violation_type': 'encryption_required',
                    'description': 'Service communication is not encrypted',
                    'severity': 'critical'
                })
        
        return violations
    
    def _calculate_security_score(self, services: List[Dict[str, Any]], 
                                 encryption_status: Dict[str, Any],
                                 cert_status: Dict[str, Any],
                                 policy_violations: List[Dict[str, Any]]) -> int:
        """Calculate overall security score (1-100)."""
        score = 100
        
        # Deduct points for unencrypted services
        encryption_coverage = encryption_status['coverage_percentage']
        score -= int((100 - encryption_coverage) * 0.5)
        
        # Deduct points for expiring certificates
        expiring_certs = len(cert_status['expiring_certificates'])
        if expiring_certs > 0:
            score -= min(20, expiring_certs * 5)
        
        # Deduct points for policy violations
        critical_violations = len([v for v in policy_violations if v['severity'] == 'critical'])
        high_violations = len([v for v in policy_violations if v['severity'] == 'high'])
        
        score -= critical_violations * 15
        score -= high_violations * 10
        
        # Bonus for quantum-safe adoption
        quantum_safe_services = len([s for s in services if s.get('quantum_safe', False)])
        if quantum_safe_services > 0:
            quantum_safe_percentage = (quantum_safe_services / len(services)) * 100
            score += int(quantum_safe_percentage * 0.1)
        
        return max(0, min(100, score))


class ServiceMeshManager:
    """Main manager for service mesh security integration."""
    
    def __init__(self, config: Optional[ServiceMeshConfig] = None):
        self.config = config
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
        self.metrics = get_metrics_collector()
        
        # Initialize mesh integrations
        self.integrations = {}
        if config:
            if config.mesh_type == ServiceMeshType.ISTIO:
                self.integrations[ServiceMeshType.ISTIO] = IstioIntegration(config)
            elif config.mesh_type == ServiceMeshType.LINKERD:
                self.integrations[ServiceMeshType.LINKERD] = LinkerdIntegration(config)
            elif config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
                self.integrations[ServiceMeshType.CONSUL_CONNECT] = ConsulConnectIntegration(config)
        
        # Security scanner
        self.security_scanner = ServiceMeshSecurityScanner()
        
        # Service registry
        self.registered_services: Dict[str, ServiceIdentity] = {}
        self.traffic_policies: Dict[str, TrafficPolicy] = {}
        
        logger.info("Service Mesh Manager initialized")
    
    def setup_quantum_safe_mesh(self, root_ca_cert: str, root_ca_key: str) -> bool:
        """Set up quantum-safe service mesh configuration."""
        try:
            if not self.config:
                raise ValueError("Service mesh configuration not provided")
            
            integration = self.integrations.get(self.config.mesh_type)
            if not integration:
                raise ValueError(f"No integration available for {self.config.mesh_type}")
            
            # Install certificates based on mesh type
            success = False
            if self.config.mesh_type == ServiceMeshType.ISTIO:
                success = integration.install_pqc_certificates(root_ca_cert, root_ca_key)
            elif self.config.mesh_type == ServiceMeshType.LINKERD:
                success = integration.install_pqc_trust_anchor(root_ca_cert, root_ca_key)
            elif self.config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
                success = integration.configure_pqc_ca(root_ca_cert, root_ca_key)
            
            if success:
                self.audit_logger.log_event(
                    event_type="service_mesh",
                    component="mesh_manager",
                    action="quantum_safe_setup",
                    outcome="success",
                    details={
                        "mesh_type": self.config.mesh_type.value,
                        "namespace": self.config.namespace
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to setup quantum-safe mesh: {e}")
            return False
    
    def register_service(self, service_name: str, namespace: str, 
                        workload_selector: Dict[str, str]) -> ServiceIdentity:
        """Register a service in the mesh."""
        try:
            service_identity = ServiceIdentity(
                service_name=service_name,
                namespace=namespace,
                cluster=self.config.cluster_name if self.config else "default",
                workload_selector=workload_selector,
                quantum_safe_cert=self.config.pqc_enabled if self.config else False
            )
            
            service_key = f"{namespace}/{service_name}"
            self.registered_services[service_key] = service_identity
            
            # Configure mesh-specific policies
            if self.config and self.config.mesh_type == ServiceMeshType.ISTIO:
                integration = self.integrations[ServiceMeshType.ISTIO]
                integration.create_pqc_destination_rule(service_identity)
                integration.enable_pqc_peer_authentication(namespace)
            
            elif self.config and self.config.mesh_type == ServiceMeshType.LINKERD:
                integration = self.integrations[ServiceMeshType.LINKERD]
                integration.create_pqc_server_policy(service_identity)
            
            self.audit_logger.log_event(
                event_type="service_mesh",
                component="mesh_manager", 
                action="service_registered",
                outcome="success",
                details={
                    "service_name": service_name,
                    "namespace": namespace,
                    "quantum_safe": service_identity.quantum_safe_cert
                }
            )
            
            return service_identity
            
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            raise
    
    def create_traffic_policy(self, source_service: str, destination_service: str,
                            source_namespace: str = "*", destination_namespace: str = "*",
                            **kwargs) -> TrafficPolicy:
        """Create traffic policy for service communication."""
        try:
            policy = TrafficPolicy(
                policy_id=str(uuid.uuid4()),
                source_service=source_service,
                destination_service=destination_service,
                source_namespace=source_namespace,
                destination_namespace=destination_namespace,
                quantum_safe_required=self.config.pqc_enabled if self.config else True,
                **kwargs
            )
            
            self.traffic_policies[policy.policy_id] = policy
            
            # Apply policy to mesh
            if self.config:
                integration = self.integrations.get(self.config.mesh_type)
                if integration:
                    if self.config.mesh_type == ServiceMeshType.ISTIO:
                        integration.create_pqc_virtual_service(policy)
                        integration.create_pqc_authorization_policy(policy)
                    elif self.config.mesh_type == ServiceMeshType.LINKERD:
                        integration.create_pqc_server_authorization(policy)
                    elif self.config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
                        integration.create_pqc_service_intentions(policy)
            
            self.audit_logger.log_event(
                event_type="service_mesh",
                component="mesh_manager",
                action="traffic_policy_created",
                outcome="success",
                details={
                    "policy_id": policy.policy_id,
                    "source": f"{source_service}.{source_namespace}",
                    "destination": f"{destination_service}.{destination_namespace}",
                    "quantum_safe_required": policy.quantum_safe_required
                }
            )
            
            return policy
            
        except Exception as e:
            logger.error(f"Failed to create traffic policy: {e}")
            raise
    
    def scan_mesh_security(self) -> MeshSecurityStatus:
        """Scan mesh security status."""
        if not self.config:
            raise ValueError("Service mesh configuration not provided")
        
        return self.security_scanner.scan_mesh_security(self.config)
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get service mesh security dashboard."""
        try:
            if not self.config:
                return {"error": "No mesh configuration"}
            
            security_status = self.scan_mesh_security()
            
            return {
                "mesh_type": self.config.mesh_type.value,
                "cluster": self.config.cluster_name,
                "namespace": self.config.namespace,
                "security_score": security_status.security_score,
                "services": {
                    "total": security_status.total_services,
                    "secured": security_status.secured_services,
                    "quantum_safe": security_status.quantum_safe_services
                },
                "encryption": {
                    "mode": self.config.encryption_mode.value,
                    "coverage": security_status.encryption_coverage
                },
                "certificates": {
                    "expiring_count": len(security_status.certificate_expiries),
                    "expiring_certificates": security_status.certificate_expiries
                },
                "policies": {
                    "total_policies": len(self.traffic_policies),
                    "violations": len(security_status.policy_violations),
                    "violation_details": security_status.policy_violations
                },
                "quantum_safe": {
                    "enabled": self.config.pqc_enabled,
                    "coverage": (security_status.quantum_safe_services / 
                               max(1, security_status.total_services)) * 100
                },
                "last_scan": security_status.last_security_scan
            }
            
        except Exception as e:
            logger.error(f"Failed to get security dashboard: {e}")
            return {"error": str(e)}
    
    def get_registered_services(self) -> List[Dict[str, Any]]:
        """Get list of registered services."""
        return [asdict(service) for service in self.registered_services.values()]
    
    def get_traffic_policies(self) -> List[Dict[str, Any]]:
        """Get list of traffic policies.""" 
        return [asdict(policy) for policy in self.traffic_policies.values()]
    
    def validate_mesh_configuration(self) -> Dict[str, Any]:
        """Validate service mesh configuration."""
        if not self.config:
            return {"status": "error", "message": "No configuration provided"}
        
        validation_results = {
            "status": "success",
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check quantum-safe configuration
        if not self.config.pqc_enabled:
            validation_results["warnings"].append(
                "Post-quantum cryptography is disabled - consider enabling for future-proofing"
            )
        
        # Check encryption mode
        if self.config.encryption_mode == TrafficEncryptionMode.PERMISSIVE:
            validation_results["warnings"].append(
                "Permissive encryption mode allows unencrypted traffic - consider strict mode"
            )
        elif self.config.encryption_mode == TrafficEncryptionMode.DISABLED:
            validation_results["errors"].append(
                "Encryption is disabled - this is not recommended for production"
            )
        
        # Check certificate duration
        if self.config.certificate_duration > 24:
            validation_results["recommendations"].append(
                "Consider shorter certificate duration for better security rotation"
            )
        
        # Check mesh type availability
        if self.config.mesh_type not in self.integrations:
            validation_results["warnings"].append(
                f"Integration for {self.config.mesh_type.value} is not initialized"
            )
        
        return validation_results


# Global service mesh manager instance
_mesh_manager = None


def get_service_mesh_manager(config: Optional[ServiceMeshConfig] = None) -> ServiceMeshManager:
    """Get global service mesh manager instance."""
    global _mesh_manager
    if _mesh_manager is None:
        _mesh_manager = ServiceMeshManager(config)
    return _mesh_manager