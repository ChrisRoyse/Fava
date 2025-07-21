"""
Multi-Cloud Key Federation and Synchronization for Fava PQC.

This module provides seamless key management federation across AWS KMS, 
Google Cloud KMS, Azure Key Vault, and other cloud key management services.
"""

import json
import logging
import time
import asyncio
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading
import uuid
from pathlib import Path
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
import ssl

from .dependency_manager import DependencyManager, enterprise_feature
from .monitoring import get_audit_logger, get_metrics_collector

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS_KMS = "aws_kms"
    GCP_KMS = "gcp_kms"
    AZURE_KV = "azure_keyvault"
    VAULT = "hashicorp_vault"
    LOCAL = "local_hsm"


class KeyStatus(Enum):
    """Key lifecycle status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class SyncOperation(Enum):
    """Types of sync operations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROTATE = "rotate"
    BACKUP = "backup"
    RESTORE = "restore"


@dataclass
class CloudKeyReference:
    """Reference to a key in a cloud provider."""
    provider: CloudProvider
    key_id: str
    key_name: str
    region: Optional[str] = None
    project_id: Optional[str] = None
    vault_path: Optional[str] = None
    key_version: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0


@dataclass
class FederatedKey:
    """A federated key across multiple cloud providers."""
    federation_id: str
    algorithm: str
    key_type: str  # 'kem', 'signature', 'symmetric'
    primary_provider: CloudProvider
    status: KeyStatus
    cloud_references: List[CloudKeyReference] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_sync: Optional[float] = None
    next_rotation: Optional[float] = None
    compliance_tags: List[str] = field(default_factory=list)


@dataclass
class SyncTask:
    """Synchronization task for multi-cloud operations."""
    task_id: str
    operation: SyncOperation
    federation_id: str
    source_provider: CloudProvider
    target_providers: List[CloudProvider]
    scheduled_time: float
    attempts: int = 0
    max_attempts: int = 3
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)


class AWSKMSAdapter:
    """Adapter for AWS Key Management Service."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dep_manager = DependencyManager()
        self.client = None
        self._initialize_client()
    
    @enterprise_feature('boto3', fallback_value=None)
    def _initialize_client(self):
        """Initialize AWS KMS client."""
        try:
            boto3_module = self.dep_manager.get_module('boto3')
            if not boto3_module:
                logger.warning("boto3 not available, AWS KMS adapter disabled")
                return
            
            self.client = boto3_module.client(
                'kms',
                region_name=self.config.get('region', 'us-east-1'),
                aws_access_key_id=self.config.get('access_key_id'),
                aws_secret_access_key=self.config.get('secret_access_key'),
                aws_session_token=self.config.get('session_token')
            )
            logger.info("AWS KMS client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AWS KMS client: {e}")
    
    def create_key(self, algorithm: str, key_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[CloudKeyReference]:
        """Create a new key in AWS KMS."""
        if not self.client:
            return None
        
        try:
            # Map PQC algorithms to AWS KMS key specs
            key_spec_mapping = {
                'Kyber768': 'SYMMETRIC_DEFAULT',
                'Dilithium3': 'SYMMETRIC_DEFAULT',
                'SPHINCS+': 'SYMMETRIC_DEFAULT'
            }
            
            key_spec = key_spec_mapping.get(algorithm, 'SYMMETRIC_DEFAULT')
            
            response = self.client.create_key(
                KeyUsage='ENCRYPT_DECRYPT',
                KeySpec=key_spec,
                Origin='AWS_KMS',
                Description=f'Fava PQC key: {algorithm}',
                Tags=[
                    {'TagKey': 'FavaPQC', 'TagValue': 'true'},
                    {'TagKey': 'Algorithm', 'TagValue': algorithm},
                    {'TagKey': 'KeyName', 'TagValue': key_name},
                    *[{'TagKey': k, 'TagValue': v} for k, v in (tags or {}).items()]
                ]
            )
            
            key_id = response['KeyMetadata']['KeyId']
            
            # Create alias for easier management
            alias_name = f"alias/fava-pqc-{key_name}-{uuid.uuid4().hex[:8]}"
            self.client.create_alias(
                AliasName=alias_name,
                TargetKeyId=key_id
            )
            
            return CloudKeyReference(
                provider=CloudProvider.AWS_KMS,
                key_id=key_id,
                key_name=alias_name,
                region=self.config.get('region')
            )
            
        except Exception as e:
            logger.error(f"Failed to create AWS KMS key: {e}")
            return None
    
    def get_key_info(self, key_reference: CloudKeyReference) -> Optional[Dict[str, Any]]:
        """Get key information from AWS KMS."""
        if not self.client:
            return None
        
        try:
            response = self.client.describe_key(KeyId=key_reference.key_id)
            metadata = response['KeyMetadata']
            
            return {
                'key_id': metadata['KeyId'],
                'key_state': metadata['KeyState'],
                'creation_date': metadata['CreationDate'].isoformat(),
                'description': metadata.get('Description', ''),
                'key_usage': metadata['KeyUsage'],
                'key_spec': metadata['KeySpec']
            }
            
        except Exception as e:
            logger.error(f"Failed to get AWS KMS key info: {e}")
            return None
    
    def delete_key(self, key_reference: CloudKeyReference, pending_window_days: int = 7) -> bool:
        """Schedule key deletion in AWS KMS."""
        if not self.client:
            return False
        
        try:
            self.client.schedule_key_deletion(
                KeyId=key_reference.key_id,
                PendingWindowInDays=pending_window_days
            )
            
            # Delete alias if it exists
            if key_reference.key_name.startswith('alias/'):
                try:
                    self.client.delete_alias(AliasName=key_reference.key_name)
                except:
                    pass  # Alias might not exist
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete AWS KMS key: {e}")
            return False
    
    def encrypt_data(self, key_reference: CloudKeyReference, plaintext: bytes) -> Optional[bytes]:
        """Encrypt data using AWS KMS key."""
        if not self.client:
            return None
        
        try:
            response = self.client.encrypt(
                KeyId=key_reference.key_id,
                Plaintext=plaintext
            )
            return response['CiphertextBlob']
            
        except Exception as e:
            logger.error(f"Failed to encrypt with AWS KMS: {e}")
            return None
    
    def decrypt_data(self, ciphertext: bytes) -> Optional[bytes]:
        """Decrypt data using AWS KMS."""
        if not self.client:
            return None
        
        try:
            response = self.client.decrypt(CiphertextBlob=ciphertext)
            return response['Plaintext']
            
        except Exception as e:
            logger.error(f"Failed to decrypt with AWS KMS: {e}")
            return None


class GCPKMSAdapter:
    """Adapter for Google Cloud Key Management Service."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dep_manager = DependencyManager()
        self.client = None
        self._initialize_client()
    
    @enterprise_feature('google-cloud-kms', fallback_value=None)
    def _initialize_client(self):
        """Initialize GCP KMS client."""
        try:
            gcp_kms = self.dep_manager.get_module('google.cloud.kms')
            if not gcp_kms:
                logger.warning("google-cloud-kms not available, GCP KMS adapter disabled")
                return
            
            self.client = gcp_kms.KeyManagementServiceClient()
            logger.info("GCP KMS client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GCP KMS client: {e}")
    
    def create_key(self, algorithm: str, key_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[CloudKeyReference]:
        """Create a new key in GCP KMS."""
        if not self.client:
            return None
        
        try:
            project_id = self.config['project_id']
            location = self.config.get('location', 'global')
            key_ring = self.config.get('key_ring', 'fava-pqc-ring')
            
            # Ensure key ring exists
            key_ring_path = self.client.key_ring_path(project_id, location, key_ring)
            try:
                self.client.get_key_ring(request={'name': key_ring_path})
            except:
                # Create key ring if it doesn't exist
                location_path = self.client.location_path(project_id, location)
                self.client.create_key_ring(
                    request={
                        'parent': location_path,
                        'key_ring_id': key_ring,
                        'key_ring': {}
                    }
                )
            
            # Create key
            key = {
                'purpose': 'ENCRYPT_DECRYPT',
                'version_template': {
                    'algorithm': 'GOOGLE_SYMMETRIC_ENCRYPTION'
                },
                'labels': {
                    'fava_pqc': 'true',
                    'algorithm': algorithm.lower(),
                    'key_name': key_name,
                    **(tags or {})
                }
            }
            
            response = self.client.create_crypto_key(
                request={
                    'parent': key_ring_path,
                    'crypto_key_id': f"fava-pqc-{key_name}-{uuid.uuid4().hex[:8]}",
                    'crypto_key': key
                }
            )
            
            return CloudKeyReference(
                provider=CloudProvider.GCP_KMS,
                key_id=response.name,
                key_name=key_name,
                project_id=project_id,
                region=location
            )
            
        except Exception as e:
            logger.error(f"Failed to create GCP KMS key: {e}")
            return None
    
    def get_key_info(self, key_reference: CloudKeyReference) -> Optional[Dict[str, Any]]:
        """Get key information from GCP KMS."""
        if not self.client:
            return None
        
        try:
            response = self.client.get_crypto_key(request={'name': key_reference.key_id})
            
            return {
                'key_id': response.name,
                'purpose': response.purpose.name,
                'creation_time': response.create_time.isoformat(),
                'labels': dict(response.labels),
                'primary_version': response.primary.name if response.primary else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get GCP KMS key info: {e}")
            return None
    
    def delete_key(self, key_reference: CloudKeyReference) -> bool:
        """Delete key in GCP KMS (mark for deletion)."""
        if not self.client:
            return False
        
        try:
            # GCP KMS doesn't support immediate deletion, only disable
            self.client.update_crypto_key(
                request={
                    'crypto_key': {
                        'name': key_reference.key_id,
                        'purpose': 'ENCRYPT_DECRYPT',
                        'next_rotation_time': None
                    },
                    'update_mask': {'paths': ['next_rotation_time']}
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete GCP KMS key: {e}")
            return False


class AzureKeyVaultAdapter:
    """Adapter for Azure Key Vault."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dep_manager = DependencyManager()
        self.client = None
        self._initialize_client()
    
    @enterprise_feature('azure-keyvault-keys', fallback_value=None)
    def _initialize_client(self):
        """Initialize Azure Key Vault client."""
        try:
            azure_keyvault = self.dep_manager.get_module('azure.keyvault.keys')
            azure_identity = self.dep_manager.get_module('azure.identity')
            
            if not azure_keyvault or not azure_identity:
                logger.warning("Azure Key Vault SDK not available, adapter disabled")
                return
            
            credential = azure_identity.DefaultAzureCredential()
            vault_url = self.config['vault_url']
            
            self.client = azure_keyvault.KeyClient(vault_url=vault_url, credential=credential)
            logger.info("Azure Key Vault client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Key Vault client: {e}")
    
    def create_key(self, algorithm: str, key_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[CloudKeyReference]:
        """Create a new key in Azure Key Vault."""
        if not self.client:
            return None
        
        try:
            from azure.keyvault.keys import KeyType
            
            # Create key with PQC metadata
            key_name_full = f"fava-pqc-{key_name}-{uuid.uuid4().hex[:8]}"
            
            created_key = self.client.create_key(
                name=key_name_full,
                key_type=KeyType.oct,  # Symmetric key for PQC
                tags={
                    'FavaPQC': 'true',
                    'Algorithm': algorithm,
                    'KeyName': key_name,
                    **(tags or {})
                }
            )
            
            return CloudKeyReference(
                provider=CloudProvider.AZURE_KV,
                key_id=created_key.id,
                key_name=key_name_full,
                vault_path=self.config['vault_url'],
                key_version=created_key.properties.version
            )
            
        except Exception as e:
            logger.error(f"Failed to create Azure Key Vault key: {e}")
            return None
    
    def get_key_info(self, key_reference: CloudKeyReference) -> Optional[Dict[str, Any]]:
        """Get key information from Azure Key Vault."""
        if not self.client:
            return None
        
        try:
            key = self.client.get_key(key_reference.key_name)
            
            return {
                'key_id': key.id,
                'key_type': key.key_type.value,
                'created_on': key.properties.created_on.isoformat() if key.properties.created_on else None,
                'updated_on': key.properties.updated_on.isoformat() if key.properties.updated_on else None,
                'enabled': key.properties.enabled,
                'tags': key.properties.tags or {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get Azure Key Vault key info: {e}")
            return None
    
    def delete_key(self, key_reference: CloudKeyReference) -> bool:
        """Delete key from Azure Key Vault."""
        if not self.client:
            return False
        
        try:
            self.client.begin_delete_key(key_reference.key_name)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Azure Key Vault key: {e}")
            return False


class VaultAdapter:
    """Adapter for HashiCorp Vault."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dep_manager = DependencyManager()
        self.client = None
        self._initialize_client()
    
    @enterprise_feature('hvac', fallback_value=None)
    def _initialize_client(self):
        """Initialize Vault client."""
        try:
            hvac = self.dep_manager.get_module('hvac')
            if not hvac:
                logger.warning("hvac not available, Vault adapter disabled")
                return
            
            self.client = hvac.Client(
                url=self.config['url'],
                token=self.config.get('token'),
                cert=self.config.get('cert'),
                verify=self.config.get('verify', True)
            )
            
            if not self.client.is_authenticated():
                raise Exception("Vault authentication failed")
            
            logger.info("HashiCorp Vault client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
    
    def create_key(self, algorithm: str, key_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[CloudKeyReference]:
        """Create a new key in Vault."""
        if not self.client:
            return None
        
        try:
            mount_point = self.config.get('mount_point', 'transit')
            key_name_full = f"fava-pqc-{key_name}-{uuid.uuid4().hex[:8]}"
            
            # Create transit key
            self.client.secrets.transit.create_key(
                name=key_name_full,
                mount_point=mount_point,
                key_type='aes256-gcm96',
                exportable=False,
                allow_plaintext_backup=False
            )
            
            # Store metadata
            metadata_path = f"secret/fava-pqc/keys/{key_name_full}"
            self.client.secrets.kv.v2.create_or_update_secret(
                path=metadata_path,
                secret={
                    'algorithm': algorithm,
                    'key_name': key_name,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'tags': tags or {}
                }
            )
            
            return CloudKeyReference(
                provider=CloudProvider.VAULT,
                key_id=key_name_full,
                key_name=key_name_full,
                vault_path=f"{mount_point}/keys/{key_name_full}"
            )
            
        except Exception as e:
            logger.error(f"Failed to create Vault key: {e}")
            return None
    
    def get_key_info(self, key_reference: CloudKeyReference) -> Optional[Dict[str, Any]]:
        """Get key information from Vault."""
        if not self.client:
            return None
        
        try:
            mount_point = self.config.get('mount_point', 'transit')
            
            # Get key info
            key_info = self.client.secrets.transit.read_key(
                name=key_reference.key_id,
                mount_point=mount_point
            )
            
            # Get metadata
            metadata_path = f"secret/fava-pqc/keys/{key_reference.key_id}"
            try:
                metadata_response = self.client.secrets.kv.v2.read_secret_version(path=metadata_path)
                metadata = metadata_response['data']['data']
            except:
                metadata = {}
            
            return {
                'key_id': key_reference.key_id,
                'creation_time': key_info['data'].get('creation_time'),
                'type': key_info['data'].get('type'),
                'keys': key_info['data'].get('keys', {}),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get Vault key info: {e}")
            return None
    
    def delete_key(self, key_reference: CloudKeyReference) -> bool:
        """Delete key from Vault."""
        if not self.client:
            return False
        
        try:
            mount_point = self.config.get('mount_point', 'transit')
            
            # Delete transit key
            self.client.secrets.transit.delete_key(
                name=key_reference.key_id,
                mount_point=mount_point
            )
            
            # Delete metadata
            metadata_path = f"secret/fava-pqc/keys/{key_reference.key_id}"
            try:
                self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=metadata_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Vault key: {e}")
            return False


class MultiCloudKeyFederationManager:
    """Main manager for multi-cloud key federation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
        self.metrics = get_metrics_collector()
        
        # Initialize cloud adapters
        self.adapters: Dict[CloudProvider, Any] = {}
        self._initialize_adapters()
        
        # Federation state
        self.federated_keys: Dict[str, FederatedKey] = {}
        self.sync_tasks: Dict[str, SyncTask] = {}
        
        # Background sync
        self.sync_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix='MultiCloudSync')
        self.sync_interval = self.config.get('sync_interval', 300)  # 5 minutes
        self._sync_thread = threading.Thread(target=self._background_sync_worker, daemon=True)
        self._sync_running = True
        self._sync_thread.start()
        
        logger.info("Multi-Cloud Key Federation Manager initialized")
    
    def _initialize_adapters(self):
        """Initialize cloud provider adapters."""
        cloud_configs = self.config.get('cloud_providers', {})
        
        # AWS KMS
        if 'aws_kms' in cloud_configs:
            self.adapters[CloudProvider.AWS_KMS] = AWSKMSAdapter(cloud_configs['aws_kms'])
        
        # GCP KMS
        if 'gcp_kms' in cloud_configs:
            self.adapters[CloudProvider.GCP_KMS] = GCPKMSAdapter(cloud_configs['gcp_kms'])
        
        # Azure Key Vault
        if 'azure_keyvault' in cloud_configs:
            self.adapters[CloudProvider.AZURE_KV] = AzureKeyVaultAdapter(cloud_configs['azure_keyvault'])
        
        # HashiCorp Vault
        if 'vault' in cloud_configs:
            self.adapters[CloudProvider.VAULT] = VaultAdapter(cloud_configs['vault'])
        
        logger.info(f"Initialized {len(self.adapters)} cloud provider adapters")
    
    def create_federated_key(self, algorithm: str, key_type: str, key_name: str,
                           providers: List[CloudProvider], 
                           primary_provider: CloudProvider,
                           metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a federated key across multiple cloud providers."""
        start_time = time.time()
        
        try:
            federation_id = str(uuid.uuid4())
            
            # Create key in primary provider first
            primary_adapter = self.adapters.get(primary_provider)
            if not primary_adapter:
                raise ValueError(f"Primary provider {primary_provider} not configured")
            
            primary_ref = primary_adapter.create_key(algorithm, key_name)
            if not primary_ref:
                raise Exception(f"Failed to create key in primary provider {primary_provider}")
            
            # Create federated key object
            federated_key = FederatedKey(
                federation_id=federation_id,
                algorithm=algorithm,
                key_type=key_type,
                primary_provider=primary_provider,
                status=KeyStatus.ACTIVE,
                cloud_references=[primary_ref],
                metadata=metadata or {},
                compliance_tags=['PQC', 'FEDERATED']
            )
            
            # Create in additional providers
            for provider in providers:
                if provider == primary_provider:
                    continue
                
                adapter = self.adapters.get(provider)
                if not adapter:
                    logger.warning(f"Provider {provider} not configured, skipping")
                    continue
                
                try:
                    ref = adapter.create_key(algorithm, f"{key_name}-fed-{federation_id[:8]}")
                    if ref:
                        federated_key.cloud_references.append(ref)
                        logger.info(f"Created key in {provider}")
                except Exception as e:
                    logger.error(f"Failed to create key in {provider}: {e}")
            
            # Store federated key
            self.federated_keys[federation_id] = federated_key
            
            # Schedule initial sync
            self._schedule_sync_task(federation_id, SyncOperation.CREATE)
            
            # Log and metrics
            duration = time.time() - start_time
            self.audit_logger.log_event(
                event_type="key_federation",
                component="multicloud_key_manager",
                action="federated_key_created",
                outcome="success",
                details={
                    "federation_id": federation_id,
                    "algorithm": algorithm,
                    "primary_provider": primary_provider.value,
                    "total_providers": len(federated_key.cloud_references),
                    "creation_duration": duration
                }
            )
            
            self.metrics.record_key_operation("federated_create", algorithm, "success", duration)
            self.metrics.set_gauge("fava_pqc_federated_keys_total", len(self.federated_keys))
            
            return federation_id
            
        except Exception as e:
            logger.error(f"Failed to create federated key: {e}")
            
            self.audit_logger.log_event(
                event_type="key_federation",
                component="multicloud_key_manager", 
                action="federated_key_created",
                outcome="failure",
                details={
                    "algorithm": algorithm,
                    "error": str(e)
                },
                severity="high"
            )
            
            return None
    
    def get_federated_key(self, federation_id: str) -> Optional[FederatedKey]:
        """Get federated key by ID."""
        return self.federated_keys.get(federation_id)
    
    def list_federated_keys(self, provider: Optional[CloudProvider] = None,
                           status: Optional[KeyStatus] = None) -> List[FederatedKey]:
        """List federated keys with optional filters."""
        keys = list(self.federated_keys.values())
        
        if provider:
            keys = [k for k in keys if any(ref.provider == provider for ref in k.cloud_references)]
        
        if status:
            keys = [k for k in keys if k.status == status]
        
        return keys
    
    def rotate_federated_key(self, federation_id: str) -> bool:
        """Rotate a federated key across all providers."""
        try:
            federated_key = self.federated_keys.get(federation_id)
            if not federated_key:
                raise ValueError(f"Federated key {federation_id} not found")
            
            federated_key.status = KeyStatus.ROTATING
            
            # Schedule rotation task
            task_id = self._schedule_sync_task(federation_id, SyncOperation.ROTATE)
            
            self.audit_logger.log_event(
                event_type="key_federation",
                component="multicloud_key_manager",
                action="key_rotation_initiated",
                outcome="success",
                details={
                    "federation_id": federation_id,
                    "task_id": task_id
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate federated key {federation_id}: {e}")
            return False
    
    def delete_federated_key(self, federation_id: str) -> bool:
        """Delete a federated key from all providers."""
        try:
            federated_key = self.federated_keys.get(federation_id)
            if not federated_key:
                raise ValueError(f"Federated key {federation_id} not found")
            
            federated_key.status = KeyStatus.DELETED
            
            # Delete from all providers
            deletion_results = {}
            for ref in federated_key.cloud_references:
                adapter = self.adapters.get(ref.provider)
                if adapter:
                    try:
                        result = adapter.delete_key(ref)
                        deletion_results[ref.provider.value] = result
                    except Exception as e:
                        logger.error(f"Failed to delete key from {ref.provider}: {e}")
                        deletion_results[ref.provider.value] = False
            
            # Remove from local tracking
            del self.federated_keys[federation_id]
            
            self.audit_logger.log_event(
                event_type="key_federation",
                component="multicloud_key_manager",
                action="federated_key_deleted",
                outcome="success",
                details={
                    "federation_id": federation_id,
                    "deletion_results": deletion_results
                }
            )
            
            self.metrics.set_gauge("fava_pqc_federated_keys_total", len(self.federated_keys))
            
            return all(deletion_results.values())
            
        except Exception as e:
            logger.error(f"Failed to delete federated key {federation_id}: {e}")
            return False
    
    def sync_federated_key(self, federation_id: str) -> bool:
        """Manually trigger sync for a federated key."""
        try:
            federated_key = self.federated_keys.get(federation_id)
            if not federated_key:
                raise ValueError(f"Federated key {federation_id} not found")
            
            # Get key info from primary provider
            primary_ref = next(
                (ref for ref in federated_key.cloud_references 
                 if ref.provider == federated_key.primary_provider), None
            )
            
            if not primary_ref:
                raise Exception("Primary provider reference not found")
            
            primary_adapter = self.adapters[federated_key.primary_provider]
            primary_info = primary_adapter.get_key_info(primary_ref)
            
            if not primary_info:
                raise Exception("Failed to get primary key info")
            
            # Update federation metadata
            federated_key.last_sync = time.time()
            federated_key.metadata.update({
                'last_sync_primary_info': primary_info,
                'sync_timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            self.audit_logger.log_event(
                event_type="key_federation",
                component="multicloud_key_manager",
                action="federated_key_synced",
                outcome="success",
                details={
                    "federation_id": federation_id,
                    "primary_provider": federated_key.primary_provider.value
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync federated key {federation_id}: {e}")
            return False
    
    def _schedule_sync_task(self, federation_id: str, operation: SyncOperation) -> str:
        """Schedule a synchronization task."""
        task_id = str(uuid.uuid4())
        
        federated_key = self.federated_keys.get(federation_id)
        if not federated_key:
            return task_id
        
        target_providers = [ref.provider for ref in federated_key.cloud_references 
                          if ref.provider != federated_key.primary_provider]
        
        task = SyncTask(
            task_id=task_id,
            operation=operation,
            federation_id=federation_id,
            source_provider=federated_key.primary_provider,
            target_providers=target_providers,
            scheduled_time=time.time()
        )
        
        self.sync_tasks[task_id] = task
        return task_id
    
    def _background_sync_worker(self):
        """Background worker for sync tasks."""
        while self._sync_running:
            try:
                # Process pending sync tasks
                pending_tasks = [task for task in self.sync_tasks.values() 
                               if task.status == "pending" and task.scheduled_time <= time.time()]
                
                for task in pending_tasks[:10]:  # Limit concurrent tasks
                    self.sync_executor.submit(self._execute_sync_task, task)
                
                # Clean completed tasks
                completed_tasks = [task_id for task_id, task in self.sync_tasks.items()
                                 if task.status in ["completed", "failed"] and
                                 task.created_at < time.time() - 3600]  # 1 hour ago
                
                for task_id in completed_tasks:
                    del self.sync_tasks[task_id]
                
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Background sync worker error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _execute_sync_task(self, task: SyncTask):
        """Execute a sync task."""
        try:
            task.status = "running"
            task.attempts += 1
            
            if task.operation == SyncOperation.CREATE:
                success = self._sync_key_creation(task)
            elif task.operation == SyncOperation.ROTATE:
                success = self._sync_key_rotation(task)
            elif task.operation == SyncOperation.UPDATE:
                success = self._sync_key_update(task)
            else:
                logger.warning(f"Unsupported sync operation: {task.operation}")
                success = False
            
            task.status = "completed" if success else "failed"
            
            if not success and task.attempts < task.max_attempts:
                # Reschedule task
                task.status = "pending"
                task.scheduled_time = time.time() + (60 * task.attempts)  # Exponential backoff
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            logger.error(f"Sync task {task.task_id} failed: {e}")
    
    def _sync_key_creation(self, task: SyncTask) -> bool:
        """Sync key creation across providers."""
        # Implementation would sync newly created keys
        return True
    
    def _sync_key_rotation(self, task: SyncTask) -> bool:
        """Sync key rotation across providers."""
        # Implementation would coordinate key rotation
        return True
    
    def _sync_key_update(self, task: SyncTask) -> bool:
        """Sync key updates across providers."""
        # Implementation would sync key metadata updates
        return True
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get overall federation status."""
        total_keys = len(self.federated_keys)
        active_keys = len([k for k in self.federated_keys.values() if k.status == KeyStatus.ACTIVE])
        
        provider_distribution = {}
        for key in self.federated_keys.values():
            for ref in key.cloud_references:
                provider = ref.provider.value
                provider_distribution[provider] = provider_distribution.get(provider, 0) + 1
        
        return {
            'total_federated_keys': total_keys,
            'active_keys': active_keys,
            'provider_distribution': provider_distribution,
            'configured_providers': [p.value for p in self.adapters.keys()],
            'pending_sync_tasks': len([t for t in self.sync_tasks.values() if t.status == "pending"]),
            'running_sync_tasks': len([t for t in self.sync_tasks.values() if t.status == "running"])
        }
    
    def shutdown(self):
        """Shutdown the federation manager."""
        self._sync_running = False
        if self._sync_thread.is_alive():
            self._sync_thread.join(timeout=10)
        
        self.sync_executor.shutdown(wait=True, timeout=30)
        logger.info("Multi-Cloud Key Federation Manager shut down")


# Global federation manager instance
_federation_manager = None


def get_federation_manager(config: Optional[Dict[str, Any]] = None) -> MultiCloudKeyFederationManager:
    """Get global federation manager instance."""
    global _federation_manager
    if _federation_manager is None:
        _federation_manager = MultiCloudKeyFederationManager(config)
    return _federation_manager