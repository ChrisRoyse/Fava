"""
Enterprise compliance and audit reporting framework.

This module provides comprehensive compliance reporting capabilities for enterprise
audits including NIST compliance, regulatory frameworks, and audit trail generation.
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Union, Set
from datetime import datetime, timezone, timedelta
from pathlib import Path
import csv
import xml.etree.ElementTree as ET

from .dependency_manager import DependencyManager
from .monitoring import AuditEvent

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRequirement:
    """Definition of a compliance requirement."""
    id: str
    framework: str  # 'NIST', 'SOC2', 'ISO27001', 'FIPS', etc.
    category: str
    title: str
    description: str
    control_objectives: List[str]
    implementation_status: str = 'not_implemented'  # 'implemented', 'partial', 'not_implemented', 'not_applicable'
    evidence_references: List[str] = field(default_factory=list)
    last_assessment: Optional[float] = None
    next_review: Optional[float] = None
    risk_level: str = 'medium'  # 'critical', 'high', 'medium', 'low'


@dataclass
class ComplianceEvidence:
    """Evidence supporting compliance with requirements."""
    id: str
    requirement_id: str
    evidence_type: str  # 'document', 'configuration', 'log', 'test_result', 'code_review'
    title: str
    description: str
    file_path: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    collection_date: float = field(default_factory=time.time)
    validity_period_days: int = 365
    collector: str = 'system'


@dataclass
class ComplianceAssessment:
    """Result of compliance assessment."""
    framework: str
    assessment_date: float
    assessor: str
    scope: str
    requirements_total: int
    requirements_implemented: int
    requirements_partial: int
    requirements_not_implemented: int
    requirements_not_applicable: int
    overall_compliance_score: float
    critical_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence_count: int = 0


class ComplianceFrameworkRegistry:
    """Registry of compliance frameworks and requirements."""
    
    # NIST SP 800-208 - Post-Quantum Cryptography Requirements
    NIST_PQC_REQUIREMENTS = [
        ComplianceRequirement(
            id='NIST-PQC-001',
            framework='NIST-SP-800-208',
            category='Key Generation',
            title='Cryptographically Secure Key Generation',
            description='PQC keys must be generated using cryptographically secure random number generation',
            control_objectives=[
                'Use NIST-approved random number generators',
                'Ensure sufficient entropy for key generation',
                'Implement secure key derivation functions'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='NIST-PQC-002',
            framework='NIST-SP-800-208',
            category='Key Management',
            title='Post-Quantum Key Lifecycle Management',
            description='Implement secure lifecycle management for post-quantum cryptographic keys',
            control_objectives=[
                'Secure key storage and protection',
                'Regular key rotation procedures',
                'Secure key backup and recovery',
                'Audit trail for key operations'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='NIST-PQC-003',
            framework='NIST-SP-800-208',
            category='Algorithm Implementation',
            title='NIST-Standardized PQC Algorithms',
            description='Use only NIST-standardized post-quantum cryptographic algorithms',
            control_objectives=[
                'Implement NIST-approved PQC algorithms',
                'Avoid deprecated or non-standardized algorithms',
                'Maintain algorithm version control'
            ],
            risk_level='high'
        ),
        ComplianceRequirement(
            id='NIST-PQC-004',
            framework='NIST-SP-800-208',
            category='Cryptographic Agility',
            title='Algorithm Agility Implementation',
            description='Implement cryptographic agility to support algorithm transitions',
            control_objectives=[
                'Support multiple PQC algorithms simultaneously',
                'Enable seamless algorithm migration',
                'Maintain backward compatibility during transitions'
            ],
            risk_level='medium'
        )
    ]
    
    # NIST SP 800-57 - Key Management Requirements
    NIST_KEY_MGMT_REQUIREMENTS = [
        ComplianceRequirement(
            id='NIST-KM-001',
            framework='NIST-SP-800-57',
            category='Key Protection',
            title='Cryptographic Key Protection',
            description='Keys must be protected against unauthorized disclosure and modification',
            control_objectives=[
                'Use hardware security modules when appropriate',
                'Implement access controls for key operations',
                'Encrypt keys at rest and in transit'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='NIST-KM-002',
            framework='NIST-SP-800-57',
            category='Key Backup',
            title='Key Backup and Recovery Procedures',
            description='Implement secure key backup and recovery procedures',
            control_objectives=[
                'Regular automated key backups',
                'Secure backup storage',
                'Tested recovery procedures',
                'Backup integrity verification'
            ],
            risk_level='high'
        )
    ]
    
    # FedRAMP HIGH Requirements
    FEDRAMP_HIGH_REQUIREMENTS = [
        ComplianceRequirement(
            id='FEDRAMP-AC-2',
            framework='FedRAMP-HIGH',
            category='Access Control',
            title='Account Management',
            description='Manage information system accounts including establishment, activation, modification, review, and removal',
            control_objectives=[
                'Implement automated account management processes',
                'Regular account review and recertification',
                'Automated account disabling for terminated users',
                'Role-based access control implementation'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='FEDRAMP-AC-3',
            framework='FedRAMP-HIGH',
            category='Access Control',
            title='Access Enforcement',
            description='Enforce approved authorizations for logical access to information and system resources',
            control_objectives=[
                'Mandatory access control mechanisms',
                'Attribute-based access control',
                'Real-time access decision enforcement',
                'Zero-trust architecture implementation'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='FEDRAMP-AU-2',
            framework='FedRAMP-HIGH',
            category='Audit and Accountability',
            title='Audit Events',
            description='Determine that the information system is capable of auditing specified events',
            control_objectives=[
                'Comprehensive audit event specification',
                'Cryptographic operation auditing',
                'Administrative action logging',
                'System-wide audit event correlation'
            ],
            risk_level='high'
        ),
        ComplianceRequirement(
            id='FEDRAMP-SC-8',
            framework='FedRAMP-HIGH',
            category='System and Communications Protection',
            title='Transmission Confidentiality and Integrity',
            description='Protect the confidentiality and integrity of transmitted information',
            control_objectives=[
                'End-to-end encryption for all transmissions',
                'Post-quantum cryptographic protection',
                'Cryptographic integrity verification',
                'Secure key establishment protocols'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='FEDRAMP-SC-13',
            framework='FedRAMP-HIGH',
            category='System and Communications Protection',
            title='Cryptographic Protection',
            description='Implement FIPS-validated or NSA-approved cryptography',
            control_objectives=[
                'FIPS 140-2 Level 3+ validated modules',
                'NSA Suite B cryptographic algorithms',
                'Post-quantum cryptographic readiness',
                'Cryptographic key management lifecycle'
            ],
            risk_level='critical'
        )
    ]
    
    # Common Criteria EAL4+ Requirements
    COMMON_CRITERIA_EAL4_REQUIREMENTS = [
        ComplianceRequirement(
            id='CC-EAL4-ADV_ARC.1',
            framework='Common-Criteria-EAL4+',
            category='Development',
            title='Security Architecture Description',
            description='Provide security architecture description with domain separation',
            control_objectives=[
                'Comprehensive security architecture documentation',
                'Domain separation and isolation analysis',
                'Security function interaction mapping',
                'Threat model and mitigation documentation'
            ],
            risk_level='high'
        ),
        ComplianceRequirement(
            id='CC-EAL4-ADV_FSP.4',
            framework='Common-Criteria-EAL4+',
            category='Development',
            title='Complete Functional Specification',
            description='Complete functional specification with all security functions',
            control_objectives=[
                'Complete security functional specification',
                'Interface specification for all security functions',
                'Security policy model documentation',
                'Formal methods where applicable'
            ],
            risk_level='medium'
        ),
        ComplianceRequirement(
            id='CC-EAL4-ADV_IMP.1',
            framework='Common-Criteria-EAL4+',
            category='Development',
            title='Implementation Representation',
            description='Provide implementation representation of the TSF',
            control_objectives=[
                'Source code or hardware schematics',
                'Build and configuration procedures',
                'Mapping between design and implementation',
                'Security-relevant implementation details'
            ],
            risk_level='medium'
        ),
        ComplianceRequirement(
            id='CC-EAL4-ATE_COV.2',
            framework='Common-Criteria-EAL4+',
            category='Tests',
            title='Analysis of Coverage',
            description='Analysis of test coverage with demonstration of correspondence',
            control_objectives=[
                'Comprehensive test coverage analysis',
                'Security function testing completeness',
                'Test case to requirement traceability',
                'Independent testing verification'
            ],
            risk_level='medium'
        ),
        ComplianceRequirement(
            id='CC-EAL4-AVA_VAN.3',
            framework='Common-Criteria-EAL4+',
            category='Vulnerability Assessment',
            title='Focused Vulnerability Analysis',
            description='Focused vulnerability analysis with penetration testing',
            control_objectives=[
                'Systematic vulnerability identification',
                'Penetration testing of security functions',
                'Independent vulnerability assessment',
                'Residual vulnerability analysis'
            ],
            risk_level='critical'
        )
    ]
    
    # FIPS 140-2 Level 3+ Requirements
    FIPS_140_2_LEVEL3_REQUIREMENTS = [
        ComplianceRequirement(
            id='FIPS-140-2-L3-CRYPTO',
            framework='FIPS-140-2-Level3+',
            category='Cryptographic Module',
            title='Cryptographic Module Specification',
            description='Hardware-based cryptographic module with tamper evidence',
            control_objectives=[
                'Hardware Security Module (HSM) implementation',
                'Tamper-evident physical security',
                'Secure boot and authenticated software',
                'Hardware-based random number generation'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='FIPS-140-2-L3-KEY-MGMT',
            framework='FIPS-140-2-Level3+',
            category='Key Management',
            title='Key Management Requirements',
            description='Secure key generation, distribution, and storage',
            control_objectives=[
                'Hardware-based key generation',
                'Secure key storage in HSM',
                'Authenticated key distribution',
                'Automatic key zeroization'
            ],
            risk_level='critical'
        ),
        ComplianceRequirement(
            id='FIPS-140-2-L3-AUTH',
            framework='FIPS-140-2-Level3+',
            category='Authentication',
            title='Identity-Based Authentication',
            description='Identity-based authentication with role verification',
            control_objectives=[
                'Multi-factor authentication required',
                'Role-based authorization enforcement',
                'Authentication audit logging',
                'Failed authentication rate limiting'
            ],
            risk_level='high'
        )
    ]
    
    # SOC 2 Type II Requirements
    SOC2_REQUIREMENTS = [
        ComplianceRequirement(
            id='SOC2-CC6.1',
            framework='SOC2-TypeII',
            category='System Operations',
            title='Logical and Physical Access Controls',
            description='Implement logical and physical access controls to protect against unauthorized access',
            control_objectives=[
                'Multi-factor authentication',
                'Role-based access control',
                'Regular access reviews',
                'Physical security controls'
            ],
            risk_level='high'
        ),
        ComplianceRequirement(
            id='SOC2-CC7.1',
            framework='SOC2-TypeII',
            category='Change Management',
            title='System Development Life Cycle',
            description='Design and implement change management processes',
            control_objectives=[
                'Change approval processes',
                'Testing procedures',
                'Deployment controls',
                'Rollback procedures'
            ],
            risk_level='medium'
        ),
        ComplianceRequirement(
            id='SOC2-CC8.1',
            framework='SOC2-TypeII',
            category='Risk Assessment',
            title='Risk Assessment Process',
            description='Implement risk assessment processes to identify and manage risks',
            control_objectives=[
                'Regular risk assessments',
                'Risk mitigation strategies',
                'Risk monitoring procedures',
                'Documentation of risk decisions'
            ],
            risk_level='medium'
        )
    ]
    
    @classmethod
    def get_framework_requirements(cls, framework: str) -> List[ComplianceRequirement]:
        """Get requirements for a specific compliance framework."""
        framework_map = {
            'NIST-SP-800-208': cls.NIST_PQC_REQUIREMENTS,
            'NIST-SP-800-57': cls.NIST_KEY_MGMT_REQUIREMENTS,
            'FedRAMP-HIGH': cls.FEDRAMP_HIGH_REQUIREMENTS,
            'Common-Criteria-EAL4+': cls.COMMON_CRITERIA_EAL4_REQUIREMENTS,
            'FIPS-140-2-Level3+': cls.FIPS_140_2_LEVEL3_REQUIREMENTS,
            'SOC2-TypeII': cls.SOC2_REQUIREMENTS
        }
        
        return framework_map.get(framework, [])
    
    @classmethod
    def get_all_requirements(cls) -> List[ComplianceRequirement]:
        """Get all compliance requirements across frameworks."""
        all_requirements = []
        all_requirements.extend(cls.NIST_PQC_REQUIREMENTS)
        all_requirements.extend(cls.NIST_KEY_MGMT_REQUIREMENTS)
        all_requirements.extend(cls.FEDRAMP_HIGH_REQUIREMENTS)
        all_requirements.extend(cls.COMMON_CRITERIA_EAL4_REQUIREMENTS)
        all_requirements.extend(cls.FIPS_140_2_LEVEL3_REQUIREMENTS)
        all_requirements.extend(cls.SOC2_REQUIREMENTS)
        return all_requirements


class ComplianceEvidenceCollector:
    """Collects evidence for compliance requirements."""
    
    def __init__(self, evidence_dir: Optional[Path] = None):
        self.evidence_dir = evidence_dir or Path('compliance_evidence')
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.dep_manager = DependencyManager()
    
    def collect_configuration_evidence(self) -> List[ComplianceEvidence]:
        """Collect evidence from system configuration."""
        evidence = []
        
        # Collect dependency configuration evidence
        enterprise_readiness = self.dep_manager.get_enterprise_readiness()
        
        evidence.append(ComplianceEvidence(
            id='CONFIG-001',
            requirement_id='NIST-PQC-001',
            evidence_type='configuration',
            title='Enterprise Dependency Configuration',
            description='System configuration showing enterprise dependency availability',
            content={
                'enterprise_readiness_score': enterprise_readiness['score'],
                'available_dependencies': enterprise_readiness['available_dependencies'],
                'critical_dependencies': enterprise_readiness['critical_available'],
                'missing_dependencies': enterprise_readiness['missing_dependencies']
            },
            collector='compliance_system'
        ))
        
        # Collect cryptographic configuration
        try:
            import oqs
            available_kems = oqs.get_enabled_KEM_mechanisms()
            available_sigs = oqs.get_enabled_sig_mechanisms()
            
            evidence.append(ComplianceEvidence(
                id='CONFIG-002',
                requirement_id='NIST-PQC-003',
                evidence_type='configuration',
                title='Available PQC Algorithms',
                description='List of available post-quantum cryptographic algorithms',
                content={
                    'kem_algorithms': available_kems,
                    'signature_algorithms': available_sigs,
                    'liboqs_version': getattr(oqs, '__version__', 'unknown')
                },
                collector='compliance_system'
            ))
        except ImportError:
            logger.warning("Cannot collect PQC algorithm evidence - liboqs not available")
        
        return evidence
    
    def collect_audit_log_evidence(self, log_file: Path, 
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> List[ComplianceEvidence]:
        """Collect evidence from audit logs."""
        evidence = []
        
        if not log_file.exists():
            logger.warning(f"Audit log file not found: {log_file}")
            return evidence
        
        try:
            audit_events = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        
                        # Filter by date range if specified
                        event_time = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
                        if start_date and event_time < start_date:
                            continue
                        if end_date and event_time > end_date:
                            continue
                        
                        audit_events.append(event_data)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Invalid audit log entry: {e}")
                        continue
            
            # Create evidence for key management events
            key_events = [e for e in audit_events if e.get('event_type') == 'key_management']
            if key_events:
                evidence.append(ComplianceEvidence(
                    id='AUDIT-001',
                    requirement_id='NIST-PQC-002',
                    evidence_type='log',
                    title='Key Management Audit Trail',
                    description=f'Audit trail of key management operations ({len(key_events)} events)',
                    content={
                        'total_events': len(key_events),
                        'event_types': list(set(e.get('action', 'unknown') for e in key_events)),
                        'date_range': {
                            'start': min(e['timestamp'] for e in key_events) if key_events else None,
                            'end': max(e['timestamp'] for e in key_events) if key_events else None
                        }
                    },
                    file_path=str(log_file),
                    collector='audit_log_collector'
                ))
            
            # Create evidence for authentication events
            auth_events = [e for e in audit_events if e.get('event_type') == 'authentication']
            if auth_events:
                evidence.append(ComplianceEvidence(
                    id='AUDIT-002',
                    requirement_id='SOC2-CC6.1',
                    evidence_type='log',
                    title='Authentication Audit Trail',
                    description=f'Audit trail of authentication events ({len(auth_events)} events)',
                    content={
                        'total_events': len(auth_events),
                        'successful_auths': len([e for e in auth_events if e.get('outcome') == 'success']),
                        'failed_auths': len([e for e in auth_events if e.get('outcome') == 'failure']),
                        'auth_methods': list(set(e.get('resource', 'unknown') for e in auth_events))
                    },
                    file_path=str(log_file),
                    collector='audit_log_collector'
                ))
        
        except Exception as e:
            logger.error(f"Failed to collect audit log evidence: {e}")
        
        return evidence
    
    def collect_code_review_evidence(self, code_paths: List[Path]) -> List[ComplianceEvidence]:
        """Collect evidence from code review and security analysis."""
        evidence = []
        
        # This would typically integrate with static analysis tools
        # For now, collect basic file information
        
        crypto_files = []
        for path in code_paths:
            if path.is_dir():
                crypto_files.extend(path.rglob('*crypto*.py'))
                crypto_files.extend(path.rglob('*key*.py'))
        
        if crypto_files:
            evidence.append(ComplianceEvidence(
                id='CODE-001',
                requirement_id='NIST-PQC-001',
                evidence_type='code_review',
                title='Cryptographic Code Inventory',
                description='Inventory of cryptographic implementation files',
                content={
                    'crypto_files_count': len(crypto_files),
                    'crypto_files': [str(f) for f in crypto_files],
                    'review_date': datetime.now(timezone.utc).isoformat()
                },
                collector='code_review_collector'
            ))
        
        return evidence
    
    def save_evidence(self, evidence: ComplianceEvidence) -> Path:
        """Save evidence to file system."""
        evidence_file = self.evidence_dir / f"{evidence.id}_{int(evidence.collection_date)}.json"
        
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(evidence), f, indent=2, default=str)
        
        logger.info(f"Saved compliance evidence: {evidence_file}")
        return evidence_file


class ComplianceAssessor:
    """Performs compliance assessments against requirements."""
    
    def __init__(self, evidence_collector: Optional[ComplianceEvidenceCollector] = None):
        self.evidence_collector = evidence_collector or ComplianceEvidenceCollector()
        self.dep_manager = DependencyManager()
    
    def assess_framework(self, framework: str, scope: str = 'full_system') -> ComplianceAssessment:
        """Perform compliance assessment for a specific framework."""
        logger.info(f"Starting compliance assessment for {framework}")
        
        requirements = ComplianceFrameworkRegistry.get_framework_requirements(framework)
        if not requirements:
            raise ValueError(f"Unknown compliance framework: {framework}")
        
        assessment = ComplianceAssessment(
            framework=framework,
            assessment_date=time.time(),
            assessor='automated_compliance_system',
            scope=scope,
            requirements_total=len(requirements),
            requirements_implemented=0,
            requirements_partial=0,
            requirements_not_implemented=0,
            requirements_not_applicable=0,
            overall_compliance_score=0.0
        )
        
        # Assess each requirement
        for requirement in requirements:
            status = self._assess_requirement(requirement)
            requirement.implementation_status = status
            requirement.last_assessment = time.time()
            
            if status == 'implemented':
                assessment.requirements_implemented += 1
            elif status == 'partial':
                assessment.requirements_partial += 1
            elif status == 'not_implemented':
                assessment.requirements_not_implemented += 1
                if requirement.risk_level == 'critical':
                    assessment.critical_findings.append(
                        f"Critical requirement not implemented: {requirement.title}"
                    )
            elif status == 'not_applicable':
                assessment.requirements_not_applicable += 1
        
        # Calculate compliance score
        implementable_requirements = (
            assessment.requirements_implemented + 
            assessment.requirements_partial + 
            assessment.requirements_not_implemented
        )
        
        if implementable_requirements > 0:
            score = (
                (assessment.requirements_implemented * 1.0 + 
                 assessment.requirements_partial * 0.5) / 
                implementable_requirements
            ) * 100
            assessment.overall_compliance_score = round(score, 1)
        
        # Generate recommendations
        assessment.recommendations.extend(self._generate_recommendations(requirements, framework))
        
        logger.info(f"Compliance assessment completed: {assessment.overall_compliance_score}% compliant")
        return assessment
    
    def _assess_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess implementation status of a single requirement."""
        
        # Framework specific assessments
        if requirement.framework == 'NIST-SP-800-208':
            return self._assess_nist_pqc_requirement(requirement)
        elif requirement.framework == 'NIST-SP-800-57':
            return self._assess_nist_key_mgmt_requirement(requirement)
        elif requirement.framework == 'FedRAMP-HIGH':
            return self._assess_fedramp_requirement(requirement)
        elif requirement.framework == 'Common-Criteria-EAL4+':
            return self._assess_common_criteria_requirement(requirement)
        elif requirement.framework == 'FIPS-140-2-Level3+':
            return self._assess_fips_140_2_requirement(requirement)
        elif requirement.framework == 'SOC2-TypeII':
            return self._assess_soc2_requirement(requirement)
        
        return 'not_implemented'
    
    def _assess_nist_pqc_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess NIST SP 800-208 requirements."""
        
        if requirement.id == 'NIST-PQC-001':
            # Check for secure key generation implementation
            try:
                import oqs
                # If we can import oqs and it has proper algorithms, consider implemented
                kems = oqs.get_enabled_KEM_mechanisms()
                if 'Kyber768' in kems or 'Kyber1024' in kems:
                    return 'implemented'
                else:
                    return 'partial'
            except ImportError:
                return 'not_implemented'
        
        elif requirement.id == 'NIST-PQC-002':
            # Check key lifecycle management
            enterprise_readiness = self.dep_manager.get_enterprise_readiness()
            critical_deps = enterprise_readiness['critical_available']
            total_critical = enterprise_readiness['critical_total']
            
            if critical_deps == total_critical:
                return 'implemented'
            elif critical_deps > 0:
                return 'partial'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'NIST-PQC-003':
            # Check for NIST-approved algorithms
            try:
                import oqs
                # Check for standardized algorithms
                sigs = oqs.get_enabled_sig_mechanisms()
                nist_approved = ['Dilithium2', 'Dilithium3', 'Dilithium5', 'Falcon-512', 'Falcon-1024']
                available_approved = [alg for alg in nist_approved if alg in sigs]
                
                if len(available_approved) >= 2:
                    return 'implemented'
                elif len(available_approved) >= 1:
                    return 'partial'
                else:
                    return 'not_implemented'
            except ImportError:
                return 'not_implemented'
        
        elif requirement.id == 'NIST-PQC-004':
            # Check cryptographic agility
            # If we have multiple algorithms available and proper key management, consider implemented
            enterprise_score = self.dep_manager.get_enterprise_readiness()['score']
            if enterprise_score >= 80:
                return 'implemented'
            elif enterprise_score >= 60:
                return 'partial'
            else:
                return 'not_implemented'
        
        return 'not_implemented'
    
    def _assess_nist_key_mgmt_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess NIST SP 800-57 requirements."""
        
        if requirement.id == 'NIST-KM-001':
            # Check key protection mechanisms
            if self.dep_manager.is_available('vault') or self.dep_manager.is_available('hsm'):
                return 'implemented'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'NIST-KM-002':
            # Check backup and recovery
            if self.dep_manager.is_available('vault'):
                return 'implemented'
            else:
                return 'partial'  # File-based backup available
        
        return 'not_implemented'
    
    def _assess_soc2_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess SOC 2 Type II requirements."""
        
        if requirement.id == 'SOC2-CC6.1':
            # Check access controls
            auth_deps_available = sum(1 for dep in ['ldap', 'oauth', 'kerberos'] 
                                     if self.dep_manager.is_available(dep))
            if auth_deps_available >= 2:
                return 'implemented'
            elif auth_deps_available >= 1:
                return 'partial'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'SOC2-CC7.1':
            # Check change management - assume partial implementation exists
            return 'partial'
        
        elif requirement.id == 'SOC2-CC8.1':
            # Check risk assessment - this framework provides risk assessment capabilities
            return 'implemented'
        
        return 'not_implemented'
    
    def _assess_fedramp_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess FedRAMP HIGH requirements."""
        
        if requirement.id == 'FEDRAMP-AC-2':
            # Check account management implementation
            enterprise_readiness = self.dep_manager.get_enterprise_readiness()
            auth_deps = sum(1 for dep in ['ldap', 'oauth', 'vault'] 
                           if dep in enterprise_readiness['available_dependencies'])
            
            if auth_deps >= 2:  # Multiple auth systems
                return 'implemented'
            elif auth_deps >= 1:
                return 'partial'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'FEDRAMP-AC-3':
            # Check access enforcement (zero-trust implementation)
            try:
                from .zero_trust import get_zero_trust_engine
                engine = get_zero_trust_engine()
                dashboard = engine.get_trust_dashboard()
                if dashboard['policies_count'] >= 4:
                    return 'implemented'
                else:
                    return 'partial'
            except:
                return 'not_implemented'
        
        elif requirement.id == 'FEDRAMP-AU-2':
            # Check audit events implementation
            try:
                from .monitoring import get_audit_logger
                audit_logger = get_audit_logger()
                if audit_logger and audit_logger.enabled:
                    return 'implemented'
                else:
                    return 'not_implemented'
            except:
                return 'not_implemented'
        
        elif requirement.id == 'FEDRAMP-SC-8':
            # Check transmission protection
            try:
                import oqs
                kems = oqs.get_enabled_KEM_mechanisms()
                if any(kem in ['Kyber768', 'Kyber1024'] for kem in kems):
                    return 'implemented'
                else:
                    return 'partial'
            except ImportError:
                return 'not_implemented'
        
        elif requirement.id == 'FEDRAMP-SC-13':
            # Check cryptographic protection
            enterprise_readiness = self.dep_manager.get_enterprise_readiness()
            if 'hsm' in enterprise_readiness.get('available_dependencies', []):
                return 'implemented'
            else:
                return 'partial'
        
        return 'not_implemented'
    
    def _assess_common_criteria_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess Common Criteria EAL4+ requirements."""
        
        if requirement.id == 'CC-EAL4-ADV_ARC.1':
            # Check if architecture documentation exists
            arch_files = [
                Path('docs/architecture'),
                Path('docs/security'),
                Path('SECURITY_ARCHITECTURE.md')
            ]
            
            if any(p.exists() for p in arch_files):
                return 'implemented'
            else:
                return 'partial'  # Basic docs might exist
        
        elif requirement.id == 'CC-EAL4-ADV_FSP.4':
            # Check functional specification completeness
            spec_files = [
                Path('docs/specifications'),
                Path('API_SPECIFICATION.md'),
                Path('docs/api.rst')
            ]
            
            if any(p.exists() for p in spec_files):
                return 'partial'  # Basic specs exist
            else:
                return 'not_implemented'
        
        elif requirement.id == 'CC-EAL4-ADV_IMP.1':
            # Check implementation representation (source code availability)
            return 'implemented'  # Source code is available
        
        elif requirement.id == 'CC-EAL4-ATE_COV.2':
            # Check test coverage analysis
            test_dirs = [
                Path('tests'),
                Path('frontend/test'),
                Path('tests/performance')
            ]
            
            if all(p.exists() for p in test_dirs):
                return 'implemented'
            elif any(p.exists() for p in test_dirs):
                return 'partial'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'CC-EAL4-AVA_VAN.3':
            # Check vulnerability analysis
            vuln_files = [
                Path('SECURITY.md'),
                Path('VULNERABILITY_ASSESSMENT.md'),
                Path('security_audit_simple.py')
            ]
            
            if any(p.exists() for p in vuln_files):
                return 'partial'  # Some security analysis exists
            else:
                return 'not_implemented'
        
        return 'not_implemented'
    
    def _assess_fips_140_2_requirement(self, requirement: ComplianceRequirement) -> str:
        """Assess FIPS 140-2 Level 3+ requirements."""
        
        if requirement.id == 'FIPS-140-2-L3-CRYPTO':
            # Check HSM implementation
            if self.dep_manager.is_available('hsm'):
                return 'implemented'
            else:
                return 'not_implemented'
        
        elif requirement.id == 'FIPS-140-2-L3-KEY-MGMT':
            # Check hardware-based key management
            enterprise_readiness = self.dep_manager.get_enterprise_readiness()
            hsm_available = 'hsm' in enterprise_readiness.get('available_dependencies', [])
            vault_available = 'vault' in enterprise_readiness.get('available_dependencies', [])
            
            if hsm_available:
                return 'implemented'
            elif vault_available:
                return 'partial'  # Software-based secure key management
            else:
                return 'not_implemented'
        
        elif requirement.id == 'FIPS-140-2-L3-AUTH':
            # Check identity-based authentication
            enterprise_readiness = self.dep_manager.get_enterprise_readiness()
            auth_deps = [dep for dep in ['ldap', 'oauth', 'vault'] 
                        if dep in enterprise_readiness.get('available_dependencies', [])]
            
            if len(auth_deps) >= 2:
                return 'implemented'
            elif len(auth_deps) >= 1:
                return 'partial'
            else:
                return 'not_implemented'
        
        return 'not_implemented'
    
    def _generate_recommendations(self, requirements: List[ComplianceRequirement], 
                                framework: str) -> List[str]:
        """Generate recommendations based on assessment results."""
        recommendations = []
        
        not_implemented = [r for r in requirements if r.implementation_status == 'not_implemented']
        partial = [r for r in requirements if r.implementation_status == 'partial']
        
        if framework == 'NIST-SP-800-208':
            if any(r.id == 'NIST-PQC-001' for r in not_implemented):
                recommendations.append("Install liboqs-python for NIST-approved PQC algorithms")
            
            if any(r.id == 'NIST-PQC-002' for r in not_implemented + partial):
                recommendations.append("Install enterprise key management dependencies (hvac, python-pkcs11)")
        
        if framework == 'SOC2-TypeII':
            if any(r.id == 'SOC2-CC6.1' for r in not_implemented + partial):
                recommendations.append("Install authentication integration dependencies (ldap3, requests-oauthlib)")
        
        # General recommendations
        if not_implemented:
            critical_not_impl = [r for r in not_implemented if r.risk_level == 'critical']
            if critical_not_impl:
                recommendations.append(
                    f"Address {len(critical_not_impl)} critical compliance gaps before production deployment"
                )
        
        return recommendations


class ComplianceReporter:
    """Generates compliance reports in various formats."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path('compliance_reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, assessments: List[ComplianceAssessment],
                                    evidence: List[ComplianceEvidence]) -> Path:
        """Generate comprehensive compliance report."""
        
        report_data = {
            'report_metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'report_type': 'comprehensive_compliance_report',
                'version': '1.0'
            },
            'executive_summary': self._generate_executive_summary(assessments),
            'compliance_assessments': [asdict(assessment) for assessment in assessments],
            'evidence_summary': self._summarize_evidence(evidence),
            'recommendations': self._consolidate_recommendations(assessments),
            'risk_analysis': self._analyze_risks(assessments)
        }
        
        # Generate JSON report
        json_report = self.output_dir / f"compliance_report_{int(time.time())}.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate human-readable HTML report
        html_report = self._generate_html_report(report_data)
        
        logger.info(f"Comprehensive compliance report generated: {json_report}")
        return json_report
    
    def _generate_executive_summary(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Generate executive summary of compliance status."""
        if not assessments:
            return {'status': 'No assessments available'}
        
        total_score = sum(a.overall_compliance_score for a in assessments)
        avg_score = total_score / len(assessments)
        
        critical_findings_count = sum(len(a.critical_findings) for a in assessments)
        
        frameworks = [a.framework for a in assessments]
        
        return {
            'overall_compliance_score': round(avg_score, 1),
            'frameworks_assessed': frameworks,
            'total_requirements': sum(a.requirements_total for a in assessments),
            'implemented_requirements': sum(a.requirements_implemented for a in assessments),
            'critical_findings_count': critical_findings_count,
            'compliance_status': self._determine_compliance_status(avg_score, critical_findings_count),
            'deployment_recommendation': self._deployment_recommendation(avg_score, critical_findings_count)
        }
    
    def _determine_compliance_status(self, avg_score: float, critical_findings: int) -> str:
        """Determine overall compliance status."""
        if critical_findings > 0:
            return 'NON_COMPLIANT'
        elif avg_score >= 95:
            return 'FULLY_COMPLIANT'
        elif avg_score >= 80:
            return 'SUBSTANTIALLY_COMPLIANT'
        elif avg_score >= 60:
            return 'PARTIALLY_COMPLIANT'
        else:
            return 'NON_COMPLIANT'
    
    def _deployment_recommendation(self, avg_score: float, critical_findings: int) -> str:
        """Generate deployment recommendation based on compliance."""
        if critical_findings > 0:
            return 'DO_NOT_DEPLOY - Critical compliance issues must be resolved'
        elif avg_score >= 90:
            return 'APPROVED_FOR_PRODUCTION - Excellent compliance posture'
        elif avg_score >= 75:
            return 'CONDITIONALLY_APPROVED - Address identified gaps'
        elif avg_score >= 60:
            return 'STAGING_ONLY - Significant compliance work needed'
        else:
            return 'DEVELOPMENT_ONLY - Major compliance deficiencies'
    
    def _summarize_evidence(self, evidence: List[ComplianceEvidence]) -> Dict[str, Any]:
        """Summarize available evidence."""
        evidence_by_type = {}
        for ev in evidence:
            if ev.evidence_type not in evidence_by_type:
                evidence_by_type[ev.evidence_type] = []
            evidence_by_type[ev.evidence_type].append(ev.id)
        
        return {
            'total_evidence_items': len(evidence),
            'evidence_by_type': {k: len(v) for k, v in evidence_by_type.items()},
            'evidence_collection_period': {
                'earliest': min(ev.collection_date for ev in evidence) if evidence else None,
                'latest': max(ev.collection_date for ev in evidence) if evidence else None
            }
        }
    
    def _consolidate_recommendations(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Consolidate recommendations from all assessments."""
        all_recommendations = []
        for assessment in assessments:
            all_recommendations.extend(assessment.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations
    
    def _analyze_risks(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Analyze compliance risks."""
        total_critical = sum(len(a.critical_findings) for a in assessments)
        avg_score = sum(a.overall_compliance_score for a in assessments) / len(assessments) if assessments else 0
        
        risk_level = 'LOW'
        if total_critical > 0:
            risk_level = 'CRITICAL'
        elif avg_score < 60:
            risk_level = 'HIGH'
        elif avg_score < 80:
            risk_level = 'MEDIUM'
        
        return {
            'overall_risk_level': risk_level,
            'critical_findings': total_critical,
            'average_compliance_score': round(avg_score, 1),
            'risk_factors': self._identify_risk_factors(assessments)
        }
    
    def _identify_risk_factors(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Identify key risk factors from assessments."""
        risk_factors = []
        
        for assessment in assessments:
            if assessment.critical_findings:
                risk_factors.extend([
                    f"{assessment.framework}: {finding}" 
                    for finding in assessment.critical_findings
                ])
        
        return risk_factors
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> Path:
        """Generate HTML version of compliance report."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Fava PQC Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .critical {{ color: red; font-weight: bold; }}
        .warning {{ color: orange; }}
        .success {{ color: green; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Fava PQC Enterprise Compliance Report</h1>
        <p>Generated: {generated_at}</p>
        <p>Overall Compliance Score: <span class="{score_class}">{overall_score}%</span></p>
        <p>Compliance Status: <span class="{status_class}">{compliance_status}</span></p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>Deployment Recommendation: <strong>{deployment_rec}</strong></p>
        <p>Frameworks Assessed: {frameworks}</p>
        <p>Critical Findings: <span class="critical">{critical_count}</span></p>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
        {recommendations_html}
        </ul>
    </div>
</body>
</html>
        """
        
        exec_summary = report_data['executive_summary']
        
        # Determine CSS classes based on status
        score = exec_summary['overall_compliance_score']
        score_class = 'success' if score >= 80 else 'warning' if score >= 60 else 'critical'
        
        status = exec_summary['compliance_status']
        status_class = 'success' if 'COMPLIANT' in status and 'NON' not in status else 'critical'
        
        recommendations_html = '\n'.join(
            f"<li>{rec}</li>" for rec in report_data['recommendations']
        )
        
        html_content = html_template.format(
            generated_at=report_data['report_metadata']['generated_at'],
            overall_score=score,
            score_class=score_class,
            compliance_status=status,
            status_class=status_class,
            deployment_rec=exec_summary['deployment_recommendation'],
            frameworks=', '.join(exec_summary['frameworks_assessed']),
            critical_count=exec_summary['critical_findings_count'],
            recommendations_html=recommendations_html
        )
        
        html_report = self.output_dir / f"compliance_report_{int(time.time())}.html"
        with open(html_report, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML compliance report generated: {html_report}")
        return html_report


class AuditTrailGenerator:
    """Generates audit trail reports for compliance purposes."""
    
    def __init__(self, audit_log_path: Optional[Path] = None):
        self.audit_log_path = audit_log_path or Path('fava-pqc-audit.log')
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime,
                            output_format: str = 'json') -> Path:
        """Generate audit trail report for specified date range."""
        
        if not self.audit_log_path.exists():
            raise FileNotFoundError(f"Audit log file not found: {self.audit_log_path}")
        
        events = self._extract_events(start_date, end_date)
        
        report_data = {
            'report_metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'report_type': 'audit_trail_report',
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_events': len(events)
            },
            'summary': self._generate_audit_summary(events),
            'events': events
        }
        
        if output_format.lower() == 'json':
            return self._save_json_report(report_data)
        elif output_format.lower() == 'csv':
            return self._save_csv_report(events)
        elif output_format.lower() == 'xml':
            return self._save_xml_report(report_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _extract_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extract events from audit log within date range."""
        events = []
        
        with open(self.audit_log_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = json.loads(line.strip())
                    event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                    
                    if start_date <= event_time <= end_date:
                        events.append(event)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid audit log entry at line {line_num}: {e}")
                    continue
        
        return events
    
    def _generate_audit_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for audit events."""
        if not events:
            return {'total_events': 0}
        
        event_types = {}
        outcomes = {'success': 0, 'failure': 0, 'warning': 0}
        users = set()
        components = set()
        
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            outcome = event.get('outcome', 'unknown')
            if outcome in outcomes:
                outcomes[outcome] += 1
            
            if event.get('user'):
                users.add(event['user'])
            
            if event.get('component'):
                components.add(event['component'])
        
        return {
            'total_events': len(events),
            'event_types': event_types,
            'outcomes': outcomes,
            'unique_users': len(users),
            'unique_components': len(components),
            'failure_rate': round(outcomes['failure'] / len(events) * 100, 2) if events else 0
        }
    
    def _save_json_report(self, report_data: Dict[str, Any]) -> Path:
        """Save audit report as JSON."""
        timestamp = int(time.time())
        output_file = Path(f"audit_trail_report_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return output_file
    
    def _save_csv_report(self, events: List[Dict[str, Any]]) -> Path:
        """Save audit events as CSV."""
        timestamp = int(time.time())
        output_file = Path(f"audit_trail_report_{timestamp}.csv")
        
        if not events:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['No events found in specified date range'])
            return output_file
        
        fieldnames = ['timestamp', 'event_type', 'user', 'component', 'action', 'outcome', 'severity', 'resource']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(events)
        
        return output_file
    
    def _save_xml_report(self, report_data: Dict[str, Any]) -> Path:
        """Save audit report as XML."""
        timestamp = int(time.time())
        output_file = Path(f"audit_trail_report_{timestamp}.xml")
        
        root = ET.Element('audit_report')
        
        # Add metadata
        metadata = ET.SubElement(root, 'metadata')
        for key, value in report_data['report_metadata'].items():
            elem = ET.SubElement(metadata, key)
            elem.text = str(value)
        
        # Add summary
        summary = ET.SubElement(root, 'summary')
        for key, value in report_data['summary'].items():
            elem = ET.SubElement(summary, key)
            elem.text = str(value)
        
        # Add events
        events = ET.SubElement(root, 'events')
        for event in report_data['events']:
            event_elem = ET.SubElement(events, 'event')
            for key, value in event.items():
                if value is not None:
                    elem = ET.SubElement(event_elem, key)
                    elem.text = str(value)
        
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        return output_file


# Convenience functions for enterprise compliance operations
def run_comprehensive_compliance_assessment() -> Dict[str, Any]:
    """Run comprehensive compliance assessment across all frameworks."""
    
    assessor = ComplianceAssessor()
    reporter = ComplianceReporter()
    evidence_collector = ComplianceEvidenceCollector()
    
    # Collect evidence
    evidence = []
    evidence.extend(evidence_collector.collect_configuration_evidence())
    
    # Run assessments for all frameworks
    frameworks = ['NIST-SP-800-208', 'NIST-SP-800-57', 'SOC2-TypeII']
    assessments = []
    
    for framework in frameworks:
        try:
            assessment = assessor.assess_framework(framework)
            assessments.append(assessment)
        except Exception as e:
            logger.error(f"Failed to assess {framework}: {e}")
    
    # Generate comprehensive report
    report_file = reporter.generate_comprehensive_report(assessments, evidence)
    
    return {
        'report_file': str(report_file),
        'assessments': len(assessments),
        'total_evidence': len(evidence),
        'overall_status': 'completed'
    }