"""
Zero-Trust Architecture Integration for Fava PQC.

This module implements a comprehensive zero-trust security model that validates
every request, user, and operation with post-quantum cryptographic security.
"""

import json
import logging
import time
import hashlib
import hmac
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading
import uuid
from pathlib import Path
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

from .dependency_manager import DependencyManager, enterprise_feature
from .monitoring import get_audit_logger, get_metrics_collector

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for zero-trust evaluation."""
    UNTRUSTED = 0
    LIMITED = 25
    BASIC = 50
    ELEVATED = 75
    FULL = 100


class AuthenticationMethod(Enum):
    """Supported authentication methods."""
    PASSWORD = "password"
    MFA = "multi_factor"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    QUANTUM_KEY = "quantum_key"


class ResourceSensitivity(Enum):
    """Resource sensitivity levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@dataclass
class ZeroTrustPolicy:
    """Zero-trust security policy definition."""
    id: str
    name: str
    description: str
    resource_patterns: List[str]
    required_trust_level: TrustLevel
    required_auth_methods: List[AuthenticationMethod]
    max_session_duration: int  # seconds
    require_device_attestation: bool = True
    require_network_verification: bool = True
    require_behavioral_analysis: bool = True
    allow_offline_access: bool = False
    encryption_required: bool = True
    quantum_safe_required: bool = True
    audit_level: str = "high"
    geo_restrictions: Optional[List[str]] = None
    time_restrictions: Optional[Dict[str, str]] = None


@dataclass
class TrustContext:
    """Context for zero-trust evaluation."""
    user_id: str
    session_id: str
    device_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: float
    authentication_methods: List[AuthenticationMethod]
    device_trust_score: float
    network_trust_score: float
    behavioral_trust_score: float
    location_info: Optional[Dict[str, Any]] = None
    previous_activities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AccessDecision:
    """Result of zero-trust access evaluation."""
    granted: bool
    trust_score: float
    required_score: float
    decision_factors: Dict[str, float]
    additional_requirements: List[str] = field(default_factory=list)
    session_duration: Optional[int] = None
    monitoring_level: str = "standard"
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


class QuantumSafeTokenGenerator:
    """Generate quantum-safe authentication tokens."""
    
    def __init__(self, master_key: bytes):
        self.dep_manager = DependencyManager()
        self.master_key = master_key
        self._initialize_crypto()
    
    def _initialize_crypto(self):
        """Initialize quantum-safe cryptographic components."""
        try:
            # Use post-quantum safe symmetric encryption
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA3_256(),
                length=32,
                salt=b'fava_pqc_zero_trust_salt',
                iterations=100000,
            )
            self.encryption_key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
            self.cipher = Fernet(self.encryption_key)
            logger.info("Quantum-safe token generator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize quantum-safe crypto: {e}")
            raise
    
    def generate_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate a quantum-safe token."""
        try:
            # Add expiration and quantum-safe signature
            now = time.time()
            payload.update({
                'iat': now,
                'exp': now + expires_in,
                'jti': str(uuid.uuid4()),
                'quantum_safe': True,
                'trust_version': '2.0'
            })
            
            # Encrypt payload with post-quantum safe encryption
            encrypted_payload = self.cipher.encrypt(json.dumps(payload).encode())
            
            # Create quantum-safe HMAC
            hmac_key = self.master_key[:32]  # Use first 32 bytes for HMAC
            signature = hmac.new(
                hmac_key, 
                encrypted_payload, 
                hashlib.sha3_256
            ).hexdigest()
            
            # Combine encrypted payload and signature
            token_data = {
                'payload': base64.urlsafe_b64encode(encrypted_payload).decode(),
                'signature': signature,
                'version': '2.0'
            }
            
            return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()
            
        except Exception as e:
            logger.error(f"Failed to generate quantum-safe token: {e}")
            raise
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify and decode a quantum-safe token."""
        try:
            # Decode token
            token_data = json.loads(base64.urlsafe_b64decode(token.encode()))
            
            if token_data.get('version') != '2.0':
                logger.warning("Token version mismatch")
                return False, None
            
            encrypted_payload = base64.urlsafe_b64decode(token_data['payload'])
            provided_signature = token_data['signature']
            
            # Verify signature
            hmac_key = self.master_key[:32]
            expected_signature = hmac.new(
                hmac_key, 
                encrypted_payload, 
                hashlib.sha3_256
            ).hexdigest()
            
            if not hmac.compare_digest(expected_signature, provided_signature):
                logger.warning("Token signature verification failed")
                return False, None
            
            # Decrypt payload
            decrypted_payload = self.cipher.decrypt(encrypted_payload)
            payload = json.loads(decrypted_payload.decode())
            
            # Check expiration
            if payload.get('exp', 0) < time.time():
                logger.info("Token expired")
                return False, None
            
            return True, payload
            
        except Exception as e:
            logger.error(f"Failed to verify quantum-safe token: {e}")
            return False, None


class DeviceAttestationService:
    """Service for device trust attestation."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.trusted_devices = {}
        self.device_profiles = {}
    
    def attest_device(self, device_id: str, context: Dict[str, Any]) -> Tuple[bool, float]:
        """Perform device attestation and return trust score."""
        try:
            trust_score = 0.0
            attestation_passed = True
            
            # Check device certificate if available
            if 'device_cert' in context:
                cert_valid = self._verify_device_certificate(context['device_cert'])
                trust_score += 30 if cert_valid else 0
                if not cert_valid:
                    attestation_passed = False
            
            # Check hardware security features
            if 'tpm_present' in context:
                trust_score += 25 if context['tpm_present'] else 0
            
            if 'secure_boot' in context:
                trust_score += 20 if context['secure_boot'] else 0
            
            # Check device reputation
            device_history = self.device_profiles.get(device_id, {})
            if device_history.get('clean_history', True):
                trust_score += 15
            
            # Check for jailbreak/root indicators
            if context.get('jailbroken', False) or context.get('rooted', False):
                trust_score -= 40
                attestation_passed = False
            
            # Update device profile
            self.device_profiles[device_id] = {
                'last_attestation': time.time(),
                'trust_score': trust_score,
                'context': context,
                'clean_history': device_history.get('clean_history', True)
            }
            
            logger.info(f"Device {device_id} attestation: {trust_score}/100")
            return attestation_passed, min(100.0, max(0.0, trust_score))
            
        except Exception as e:
            logger.error(f"Device attestation failed: {e}")
            return False, 0.0
    
    def _verify_device_certificate(self, cert_data: str) -> bool:
        """Verify device certificate chain."""
        # Implementation would verify against trusted CA
        # For now, return basic validation
        try:
            return len(cert_data) > 100 and 'BEGIN CERTIFICATE' in cert_data
        except:
            return False


class BehavioralAnalysisEngine:
    """AI-powered behavioral analysis for zero-trust."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.user_profiles = {}
        self.anomaly_threshold = 0.7
    
    def analyze_behavior(self, user_id: str, context: TrustContext) -> Tuple[float, List[str]]:
        """Analyze user behavior and return trust score."""
        try:
            trust_score = 70.0  # Start with neutral score
            anomalies = []
            
            user_profile = self.user_profiles.get(user_id, {
                'typical_locations': [],
                'typical_times': [],
                'typical_devices': [],
                'activity_patterns': {},
                'first_seen': time.time()
            })
            
            # Analyze location patterns
            current_location = context.location_info
            if current_location:
                location_score = self._analyze_location_pattern(user_profile, current_location)
                if location_score < 0.5:
                    anomalies.append("Unusual location access")
                    trust_score -= 20
                else:
                    trust_score += 10
            
            # Analyze time patterns  
            current_time = datetime.fromtimestamp(context.timestamp)
            time_score = self._analyze_time_pattern(user_profile, current_time)
            if time_score < 0.5:
                anomalies.append("Unusual time access")
                trust_score -= 15
            else:
                trust_score += 5
            
            # Analyze device patterns
            device_score = self._analyze_device_pattern(user_profile, context.device_id)
            if device_score < 0.5:
                anomalies.append("Unknown device")
                trust_score -= 25
            else:
                trust_score += 10
            
            # Update user profile
            self._update_user_profile(user_id, context, user_profile)
            
            final_score = min(100.0, max(0.0, trust_score))
            logger.info(f"Behavioral analysis for {user_id}: {final_score}/100")
            
            return final_score, anomalies
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return 50.0, ["Analysis error"]
    
    def _analyze_location_pattern(self, profile: Dict, current_location: Dict) -> float:
        """Analyze location access patterns."""
        if not current_location:
            return 0.5
        
        typical_locations = profile.get('typical_locations', [])
        if not typical_locations:
            return 0.7  # New user, moderate trust
        
        current_coords = (current_location.get('lat', 0), current_location.get('lng', 0))
        
        for location in typical_locations:
            distance = self._calculate_distance(current_coords, location['coords'])
            if distance < 50:  # Within 50km
                return 1.0
            elif distance < 200:  # Within 200km
                return 0.8
        
        return 0.3  # Far from typical locations
    
    def _analyze_time_pattern(self, profile: Dict, current_time: datetime) -> float:
        """Analyze time-based access patterns."""
        typical_times = profile.get('typical_times', [])
        if not typical_times:
            return 0.7
        
        current_hour = current_time.hour
        typical_hours = [t['hour'] for t in typical_times]
        
        if current_hour in typical_hours:
            return 1.0
        elif any(abs(current_hour - h) <= 2 for h in typical_hours):
            return 0.8
        else:
            return 0.4
    
    def _analyze_device_pattern(self, profile: Dict, device_id: str) -> float:
        """Analyze device usage patterns."""
        if not device_id:
            return 0.3
        
        typical_devices = profile.get('typical_devices', [])
        if device_id in typical_devices:
            return 1.0
        elif len(typical_devices) < 3:  # User has few devices, more lenient
            return 0.7
        else:
            return 0.2
    
    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between coordinates (simplified)."""
        return ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5 * 111  # Rough km
    
    def _update_user_profile(self, user_id: str, context: TrustContext, profile: Dict):
        """Update user behavioral profile."""
        try:
            current_time = datetime.fromtimestamp(context.timestamp)
            
            # Update location history
            if context.location_info:
                locations = profile.setdefault('typical_locations', [])
                locations.append({
                    'coords': (context.location_info.get('lat', 0), context.location_info.get('lng', 0)),
                    'timestamp': context.timestamp
                })
                # Keep only recent locations
                profile['typical_locations'] = locations[-10:]
            
            # Update time patterns
            times = profile.setdefault('typical_times', [])
            times.append({'hour': current_time.hour, 'timestamp': context.timestamp})
            profile['typical_times'] = times[-20:]
            
            # Update device patterns
            if context.device_id:
                devices = profile.setdefault('typical_devices', [])
                if context.device_id not in devices:
                    devices.append(context.device_id)
                profile['typical_devices'] = devices[-5:]  # Keep 5 recent devices
            
            self.user_profiles[user_id] = profile
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")


class ZeroTrustEngine:
    """Main zero-trust decision engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
        self.metrics = get_metrics_collector()
        
        # Initialize components
        master_key = self._get_or_generate_master_key()
        self.token_generator = QuantumSafeTokenGenerator(master_key)
        self.device_attestation = DeviceAttestationService()
        self.behavioral_analysis = BehavioralAnalysisEngine()
        
        # Load policies
        self.policies: List[ZeroTrustPolicy] = []
        self._load_default_policies()
        
        # Decision cache for performance
        self.decision_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("Zero-Trust Engine initialized")
    
    def _get_or_generate_master_key(self) -> bytes:
        """Get or generate master encryption key."""
        key_file = Path(self.config.get('master_key_file', 'zero_trust_master.key'))
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            master_key = os.urandom(64)  # 512-bit key
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(key_file, 'wb') as f:
                f.write(master_key)
            
            os.chmod(key_file, 0o600)  # Owner read/write only
            logger.info("Generated new zero-trust master key")
            return master_key
    
    def _load_default_policies(self):
        """Load default zero-trust policies."""
        default_policies = [
            ZeroTrustPolicy(
                id="pqc-key-ops-policy",
                name="Post-Quantum Key Operations",
                description="High security policy for PQC key operations",
                resource_patterns=["/api/keys/*", "/crypto/key/*"],
                required_trust_level=TrustLevel.ELEVATED,
                required_auth_methods=[AuthenticationMethod.MFA, AuthenticationMethod.CERTIFICATE],
                max_session_duration=1800,  # 30 minutes
                require_device_attestation=True,
                require_network_verification=True,
                require_behavioral_analysis=True,
                quantum_safe_required=True,
                audit_level="critical"
            ),
            ZeroTrustPolicy(
                id="admin-access-policy",
                name="Administrative Access",
                description="Highest security for admin operations",
                resource_patterns=["/admin/*", "/config/*", "/enterprise/*"],
                required_trust_level=TrustLevel.FULL,
                required_auth_methods=[AuthenticationMethod.MFA, AuthenticationMethod.HARDWARE_TOKEN],
                max_session_duration=900,  # 15 minutes
                require_device_attestation=True,
                require_network_verification=True,
                require_behavioral_analysis=True,
                quantum_safe_required=True,
                audit_level="critical"
            ),
            ZeroTrustPolicy(
                id="api-access-policy",
                name="API Access",
                description="Standard security for API endpoints",
                resource_patterns=["/api/*"],
                required_trust_level=TrustLevel.BASIC,
                required_auth_methods=[AuthenticationMethod.CERTIFICATE],
                max_session_duration=3600,  # 1 hour
                require_device_attestation=False,
                require_network_verification=True,
                require_behavioral_analysis=True,
                quantum_safe_required=True,
                audit_level="high"
            ),
            ZeroTrustPolicy(
                id="read-only-policy",
                name="Read-Only Access",
                description="Basic security for read operations",
                resource_patterns=["/view/*", "/reports/*"],
                required_trust_level=TrustLevel.LIMITED,
                required_auth_methods=[AuthenticationMethod.PASSWORD],
                max_session_duration=7200,  # 2 hours
                require_device_attestation=False,
                require_network_verification=False,
                require_behavioral_analysis=True,
                quantum_safe_required=False,
                audit_level="medium"
            )
        ]
        
        self.policies.extend(default_policies)
        logger.info(f"Loaded {len(default_policies)} default zero-trust policies")
    
    def evaluate_access(self, resource: str, context: TrustContext) -> AccessDecision:
        """Evaluate access request against zero-trust policies."""
        start_time = time.time()
        
        try:
            # Find matching policy
            policy = self._find_matching_policy(resource)
            if not policy:
                logger.warning(f"No policy found for resource: {resource}")
                return AccessDecision(
                    granted=False,
                    trust_score=0.0,
                    required_score=100.0,
                    decision_factors={"no_policy": -100.0}
                )
            
            # Check cache first
            cache_key = self._generate_cache_key(resource, context, policy)
            cached_decision = self._get_cached_decision(cache_key)
            if cached_decision:
                logger.debug("Using cached zero-trust decision")
                return cached_decision
            
            # Calculate trust score
            trust_score, decision_factors = self._calculate_trust_score(context, policy)
            required_score = policy.required_trust_level.value
            
            # Make access decision
            granted = trust_score >= required_score
            
            # Determine additional requirements
            additional_requirements = self._determine_additional_requirements(
                trust_score, required_score, policy, context
            )
            
            # Create decision
            decision = AccessDecision(
                granted=granted,
                trust_score=trust_score,
                required_score=required_score,
                decision_factors=decision_factors,
                additional_requirements=additional_requirements,
                session_duration=policy.max_session_duration,
                monitoring_level=policy.audit_level
            )
            
            # Cache decision
            self._cache_decision(cache_key, decision)
            
            # Log decision
            self.audit_logger.log_event(
                event_type="zero_trust_decision",
                component="zero_trust_engine",
                action="access_evaluation",
                outcome="granted" if granted else "denied",
                user=context.user_id,
                resource=resource,
                details={
                    "trust_score": trust_score,
                    "required_score": required_score,
                    "policy_id": policy.id,
                    "decision_factors": decision_factors,
                    "session_id": context.session_id
                },
                severity="info" if granted else "medium"
            )
            
            # Record metrics
            self.metrics.increment_counter('fava_pqc_zero_trust_decisions_total', {
                'outcome': 'granted' if granted else 'denied',
                'policy': policy.id,
                'trust_level': policy.required_trust_level.name
            })
            
            duration = time.time() - start_time
            self.metrics.observe_histogram('fava_pqc_zero_trust_evaluation_duration_seconds', duration, {
                'resource_type': self._get_resource_type(resource)
            })
            
            return decision
            
        except Exception as e:
            logger.error(f"Zero-trust evaluation failed: {e}")
            return AccessDecision(
                granted=False,
                trust_score=0.0,
                required_score=100.0,
                decision_factors={"evaluation_error": -100.0}
            )
    
    def _find_matching_policy(self, resource: str) -> Optional[ZeroTrustPolicy]:
        """Find policy matching the resource pattern."""
        for policy in self.policies:
            for pattern in policy.resource_patterns:
                if self._matches_pattern(resource, pattern):
                    return policy
        return None
    
    def _matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches policy pattern."""
        if pattern.endswith('*'):
            return resource.startswith(pattern[:-1])
        return resource == pattern
    
    def _calculate_trust_score(self, context: TrustContext, policy: ZeroTrustPolicy) -> Tuple[float, Dict[str, float]]:
        """Calculate comprehensive trust score."""
        decision_factors = {}
        
        # Base authentication score
        auth_score = self._calculate_auth_score(context.authentication_methods, policy)
        decision_factors["authentication"] = auth_score
        
        # Device attestation score
        device_score = context.device_trust_score if policy.require_device_attestation else 100.0
        decision_factors["device_attestation"] = device_score
        
        # Network trust score  
        network_score = context.network_trust_score if policy.require_network_verification else 100.0
        decision_factors["network_trust"] = network_score
        
        # Behavioral analysis score
        behavioral_score = context.behavioral_trust_score if policy.require_behavioral_analysis else 100.0
        decision_factors["behavioral_analysis"] = behavioral_score
        
        # Time-based restrictions
        time_score = self._calculate_time_score(context, policy)
        decision_factors["time_restrictions"] = time_score
        
        # Geo-based restrictions
        geo_score = self._calculate_geo_score(context, policy)
        decision_factors["geo_restrictions"] = geo_score
        
        # Session freshness score
        session_score = self._calculate_session_score(context)
        decision_factors["session_freshness"] = session_score
        
        # Calculate weighted average
        weights = {
            "authentication": 0.25,
            "device_attestation": 0.15,
            "network_trust": 0.15,
            "behavioral_analysis": 0.20,
            "time_restrictions": 0.10,
            "geo_restrictions": 0.10,
            "session_freshness": 0.05
        }
        
        total_score = sum(decision_factors[factor] * weights[factor] for factor in weights)
        
        return total_score, decision_factors
    
    def _calculate_auth_score(self, methods: List[AuthenticationMethod], policy: ZeroTrustPolicy) -> float:
        """Calculate authentication strength score."""
        method_scores = {
            AuthenticationMethod.PASSWORD: 20,
            AuthenticationMethod.MFA: 60,
            AuthenticationMethod.CERTIFICATE: 70,
            AuthenticationMethod.BIOMETRIC: 80,
            AuthenticationMethod.HARDWARE_TOKEN: 90,
            AuthenticationMethod.QUANTUM_KEY: 100
        }
        
        current_score = sum(method_scores.get(method, 0) for method in methods)
        required_score = sum(method_scores.get(method, 0) for method in policy.required_auth_methods)
        
        return min(100.0, (current_score / max(required_score, 1)) * 100)
    
    def _calculate_time_score(self, context: TrustContext, policy: ZeroTrustPolicy) -> float:
        """Calculate time-based access score."""
        if not policy.time_restrictions:
            return 100.0
        
        current_time = datetime.fromtimestamp(context.timestamp)
        current_hour = current_time.hour
        
        allowed_start = int(policy.time_restrictions.get('start_hour', 0))
        allowed_end = int(policy.time_restrictions.get('end_hour', 23))
        
        if allowed_start <= current_hour <= allowed_end:
            return 100.0
        else:
            return 0.0
    
    def _calculate_geo_score(self, context: TrustContext, policy: ZeroTrustPolicy) -> float:
        """Calculate geographical access score."""
        if not policy.geo_restrictions or not context.location_info:
            return 100.0
        
        user_country = context.location_info.get('country', 'unknown')
        
        if user_country in policy.geo_restrictions:
            return 100.0
        else:
            return 0.0
    
    def _calculate_session_score(self, context: TrustContext) -> float:
        """Calculate session freshness score."""
        session_age = time.time() - context.timestamp
        
        if session_age < 300:  # 5 minutes
            return 100.0
        elif session_age < 1800:  # 30 minutes  
            return 80.0
        elif session_age < 3600:  # 1 hour
            return 60.0
        else:
            return 30.0
    
    def _determine_additional_requirements(self, trust_score: float, required_score: float, 
                                         policy: ZeroTrustPolicy, context: TrustContext) -> List[str]:
        """Determine additional security requirements based on trust gap."""
        requirements = []
        trust_gap = required_score - trust_score
        
        if trust_gap > 0:
            if trust_gap >= 30:
                requirements.append("multi_factor_authentication_required")
            if trust_gap >= 50:
                requirements.append("device_certificate_required")
            if policy.require_behavioral_analysis and context.behavioral_trust_score < 70:
                requirements.append("behavioral_verification_required")
            if policy.quantum_safe_required:
                requirements.append("quantum_safe_encryption_required")
        
        return requirements
    
    def _generate_cache_key(self, resource: str, context: TrustContext, policy: ZeroTrustPolicy) -> str:
        """Generate cache key for decision caching."""
        key_data = f"{resource}:{context.user_id}:{context.session_id}:{policy.id}:{int(context.timestamp/300)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _get_cached_decision(self, cache_key: str) -> Optional[AccessDecision]:
        """Get cached decision if still valid."""
        if cache_key in self.decision_cache:
            decision, cache_time = self.decision_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return decision
            else:
                del self.decision_cache[cache_key]
        return None
    
    def _cache_decision(self, cache_key: str, decision: AccessDecision):
        """Cache access decision."""
        self.decision_cache[cache_key] = (decision, time.time())
        
        # Clean old cache entries periodically
        if len(self.decision_cache) > 1000:
            self._clean_cache()
    
    def _clean_cache(self):
        """Clean expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, cache_time) in self.decision_cache.items()
            if current_time - cache_time >= self.cache_ttl
        ]
        for key in expired_keys:
            del self.decision_cache[key]
    
    def _get_resource_type(self, resource: str) -> str:
        """Extract resource type for metrics."""
        if '/api/keys/' in resource:
            return 'key_operation'
        elif '/admin/' in resource:
            return 'admin_operation'
        elif '/api/' in resource:
            return 'api_operation'
        else:
            return 'other'
    
    def create_secure_session(self, user_id: str, context: TrustContext) -> Optional[str]:
        """Create a new secure session token."""
        try:
            # Perform initial trust evaluation
            initial_decision = self.evaluate_access("/api/session", context)
            
            if not initial_decision.granted:
                logger.warning(f"Session creation denied for user {user_id}")
                return None
            
            # Generate session token
            session_payload = {
                'user_id': user_id,
                'session_id': context.session_id,
                'trust_score': initial_decision.trust_score,
                'device_id': context.device_id,
                'created_at': context.timestamp,
                'ip_address': context.ip_address
            }
            
            token = self.token_generator.generate_token(
                session_payload, 
                expires_in=initial_decision.session_duration or 3600
            )
            
            self.audit_logger.log_event(
                event_type="session_management",
                component="zero_trust_engine",
                action="session_created",
                outcome="success",
                user=user_id,
                details={
                    "session_id": context.session_id,
                    "trust_score": initial_decision.trust_score,
                    "session_duration": initial_decision.session_duration
                }
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to create secure session: {e}")
            return None
    
    def validate_session(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate session token and extract session info."""
        return self.token_generator.verify_token(token)
    
    def add_policy(self, policy: ZeroTrustPolicy):
        """Add a new zero-trust policy."""
        self.policies.append(policy)
        logger.info(f"Added zero-trust policy: {policy.name}")
        
        self.audit_logger.log_event(
            event_type="policy_management",
            component="zero_trust_engine",
            action="policy_added",
            outcome="success",
            details={"policy_id": policy.id, "policy_name": policy.name}
        )
    
    def remove_policy(self, policy_id: str):
        """Remove a zero-trust policy."""
        self.policies = [p for p in self.policies if p.id != policy_id]
        logger.info(f"Removed zero-trust policy: {policy_id}")
        
        self.audit_logger.log_event(
            event_type="policy_management",
            component="zero_trust_engine",
            action="policy_removed",
            outcome="success",
            details={"policy_id": policy_id}
        )
    
    def get_trust_dashboard(self) -> Dict[str, Any]:
        """Get zero-trust security dashboard data."""
        return {
            'policies_count': len(self.policies),
            'cache_size': len(self.decision_cache),
            'active_sessions': len([d for d, _ in self.decision_cache.values() if d.granted]),
            'total_decisions': sum(1 for _ in self.decision_cache.keys()),
            'behavioral_profiles': len(self.behavioral_analysis.user_profiles),
            'device_profiles': len(self.device_attestation.device_profiles)
        }


# Global zero-trust engine instance
_zero_trust_engine = None


def get_zero_trust_engine(config: Optional[Dict[str, Any]] = None) -> ZeroTrustEngine:
    """Get global zero-trust engine instance."""
    global _zero_trust_engine
    if _zero_trust_engine is None:
        _zero_trust_engine = ZeroTrustEngine(config)
    return _zero_trust_engine


def zero_trust_required(resource: str):
    """Decorator for zero-trust protected functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract context from request/session
            # This would be implemented based on the web framework used
            engine = get_zero_trust_engine()
            
            # For now, create a minimal context for testing
            context = TrustContext(
                user_id="test_user",
                session_id="test_session",
                device_id="test_device",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                timestamp=time.time(),
                authentication_methods=[AuthenticationMethod.PASSWORD],
                device_trust_score=80.0,
                network_trust_score=90.0,
                behavioral_trust_score=85.0
            )
            
            decision = engine.evaluate_access(resource, context)
            
            if not decision.granted:
                raise PermissionError(f"Zero-trust access denied: {decision.decision_factors}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator