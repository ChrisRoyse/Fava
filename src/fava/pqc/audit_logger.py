"""
PQC Audit Logging System

This module provides comprehensive audit logging for all PQC key management operations
and security-related events. It implements secure logging practices to maintain
a complete audit trail without exposing sensitive cryptographic material.

Security Requirements:
- Log all key management operations
- Never log sensitive key material
- Tamper-resistant log format
- Structured logging with timestamps
- Separate audit logs from application logs
"""

import json
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import os


class PQCAuditLogger:
    """
    Secure audit logger for PQC operations.
    
    This logger maintains a complete audit trail of all key management operations,
    security events, and configuration changes while ensuring no sensitive
    cryptographic material is ever logged.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the PQC audit logger.
        
        Args:
            log_file: Optional path to audit log file. If None, uses default location.
        """
        self.log_file = log_file or self._get_default_log_file()
        self.session_id = self._generate_session_id()
        
        # Configure the audit logger
        self.audit_logger = self._setup_audit_logger()
        
        # Log session start
        self._log_session_start()
    
    def _get_default_log_file(self) -> str:
        """Get the default audit log file path."""
        # Try to use a secure location for audit logs
        possible_paths = [
            "/var/log/fava/pqc_audit.log",
            "/opt/fava/logs/pqc_audit.log",
            os.path.expanduser("~/.fava/logs/pqc_audit.log"),
            "./logs/pqc_audit.log"
        ]
        
        for path_str in possible_paths:
            path = Path(path_str)
            try:
                # Create parent directories if they don't exist
                path.parent.mkdir(parents=True, exist_ok=True)
                # Test if we can write to this location
                test_file = path.parent / "test_write"
                test_file.touch()
                test_file.unlink()
                return str(path)
            except (PermissionError, OSError):
                continue
        
        # Fallback to current directory
        fallback_path = Path("./pqc_audit.log")
        return str(fallback_path)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        timestamp = str(int(time.time() * 1000000))  # Microseconds for uniqueness
        process_id = str(os.getpid())
        content = f"{timestamp}:{process_id}:{id(self)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Set up the audit logger with proper formatting and security."""
        # Create a separate logger for audit events
        audit_logger = logging.getLogger(f'fava.pqc.audit.{self.session_id}')
        audit_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers to avoid duplication
        audit_logger.handlers.clear()
        audit_logger.propagate = False
        
        # Create file handler for audit logs
        try:
            file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Set secure file permissions (600 - owner read/write only)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.log_file, 0o600)
            
            # Create detailed formatter for audit logs
            formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)s | AUDIT | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S UTC'
            )
            formatter.converter = time.gmtime  # Use UTC time
            file_handler.setFormatter(formatter)
            
            audit_logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, fall back to console logging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            formatter = logging.Formatter('AUDIT: %(message)s')
            console_handler.setFormatter(formatter)
            audit_logger.addHandler(console_handler)
            audit_logger.warning(f"Failed to setup file logging, using console: {e}")
        
        return audit_logger
    
    def _log_session_start(self) -> None:
        """Log the start of an audit session."""
        self._log_event("session_start", {
            "session_id": self.session_id,
            "pid": os.getpid(),
            "log_file": self.log_file,
            "user": os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        })
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an audit event with structured data.
        
        Args:
            event_type: Type of event (e.g., 'key_generation', 'key_rotation')
            data: Event-specific data (must not contain sensitive information)
        """
        # Create the audit record
        audit_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data,
            "integrity_hash": ""  # Will be computed below
        }
        
        # Compute integrity hash (excluding the hash field itself)
        record_copy = audit_record.copy()
        record_copy.pop("integrity_hash")
        record_json = json.dumps(record_copy, sort_keys=True, separators=(',', ':'))
        integrity_hash = hashlib.sha256(record_json.encode()).hexdigest()[:32]
        audit_record["integrity_hash"] = integrity_hash
        
        # Log the structured record
        audit_json = json.dumps(audit_record, separators=(',', ':'))
        self.audit_logger.info(audit_json)
    
    def log_key_generation(self, algorithm: str, key_source: str, public_key_hash: str) -> None:
        """
        Log a key generation event.
        
        Args:
            algorithm: Cryptographic algorithm used
            key_source: Where keys are stored (environment, file, etc.)
            public_key_hash: Hash of the public key (for identification)
        """
        self._log_event("key_generation", {
            "algorithm": algorithm,
            "key_source": key_source,
            "public_key_hash": public_key_hash[:16],  # Only first 16 chars for identification
            "operation": "generate_keypair"
        })
    
    def log_key_loading(self, key_type: str, key_source: str, public_key_hash: str, success: bool) -> None:
        """
        Log a key loading event.
        
        Args:
            key_type: Type of key loaded (public, private)
            key_source: Source of the key
            public_key_hash: Hash of the public key (for identification)
            success: Whether the loading was successful
        """
        self._log_event("key_loading", {
            "key_type": key_type,
            "key_source": key_source,
            "public_key_hash": public_key_hash[:16] if public_key_hash else None,
            "success": success,
            "operation": f"load_{key_type}_key"
        })
    
    def log_key_storage(self, key_source: str, public_key_hash: str, success: bool) -> None:
        """
        Log a key storage event.
        
        Args:
            key_source: Where keys are being stored
            public_key_hash: Hash of the public key (for identification)
            success: Whether the storage was successful
        """
        self._log_event("key_storage", {
            "key_source": key_source,
            "public_key_hash": public_key_hash[:16],
            "success": success,
            "operation": "store_keypair"
        })
    
    def log_key_rotation(self, old_key_hash: Optional[str], new_key_hash: str, success: bool) -> None:
        """
        Log a key rotation event.
        
        Args:
            old_key_hash: Hash of the old public key (None if no old key)
            new_key_hash: Hash of the new public key
            success: Whether the rotation was successful
        """
        self._log_event("key_rotation", {
            "old_key_hash": old_key_hash[:16] if old_key_hash else None,
            "new_key_hash": new_key_hash[:16],
            "success": success,
            "operation": "rotate_keys"
        })
    
    def log_key_validation(self, public_key_hash: str, success: bool, error: Optional[str] = None) -> None:
        """
        Log a key validation event.
        
        Args:
            public_key_hash: Hash of the public key being validated
            success: Whether validation passed
            error: Error message if validation failed
        """
        data = {
            "public_key_hash": public_key_hash[:16],
            "success": success,
            "operation": "validate_keys"
        }
        if error:
            data["error"] = str(error)[:200]  # Limit error message length
        
        self._log_event("key_validation", data)
    
    def log_configuration_change(self, change_type: str, old_value: Any, new_value: Any) -> None:
        """
        Log a configuration change event.
        
        Args:
            change_type: Type of configuration change
            old_value: Previous value (sanitized)
            new_value: New value (sanitized)
        """
        # Sanitize values to avoid logging sensitive data
        old_sanitized = self._sanitize_config_value(old_value)
        new_sanitized = self._sanitize_config_value(new_value)
        
        self._log_event("configuration_change", {
            "change_type": change_type,
            "old_value": old_sanitized,
            "new_value": new_sanitized,
            "operation": "config_update"
        })
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO") -> None:
        """
        Log a security-related event.
        
        Args:
            event_type: Type of security event
            details: Event details (must not contain sensitive data)
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        self._log_event("security_event", {
            "security_event_type": event_type,
            "severity": severity,
            "details": details,
            "operation": "security_check"
        })
    
    def log_access_attempt(self, resource: str, success: bool, user: Optional[str] = None) -> None:
        """
        Log an access attempt to PQC resources.
        
        Args:
            resource: Resource being accessed
            success: Whether access was successful
            user: User attempting access (if available)
        """
        self._log_event("access_attempt", {
            "resource": resource,
            "success": success,
            "user": user or os.environ.get('USER', os.environ.get('USERNAME', 'unknown')),
            "operation": "access_control"
        })
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error event.
        
        Args:
            error_type: Type of error
            error_message: Error message (sanitized)
            context: Additional context (must not contain sensitive data)
        """
        data = {
            "error_type": error_type,
            "error_message": str(error_message)[:500],  # Limit message length
            "operation": "error_handling"
        }
        if context:
            data["context"] = context
        
        self._log_event("error", data)
    
    def _sanitize_config_value(self, value: Any) -> Any:
        """
        Sanitize configuration values to remove sensitive data.
        
        Args:
            value: Configuration value to sanitize
            
        Returns:
            Sanitized value safe for logging
        """
        if isinstance(value, str):
            # Check for potential keys or sensitive data
            if len(value) > 100 and any(char in value for char in "+=/_"):
                # Likely base64 encoded data - don't log it
                return f"[REDACTED_DATA_{len(value)}_CHARS]"
            elif "key" in str(value).lower() and len(value) > 20:
                # Potential key data
                return f"[REDACTED_KEY_{len(value)}_CHARS]"
            else:
                return value
        elif isinstance(value, dict):
            # Recursively sanitize dictionary values
            return {k: self._sanitize_config_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively sanitize list items
            return [self._sanitize_config_value(item) for item in value]
        else:
            return value
    
    def close(self) -> None:
        """Close the audit logger and log session end."""
        self._log_event("session_end", {
            "session_id": self.session_id,
            "duration_seconds": time.time()
        })
        
        # Close all handlers
        for handler in self.audit_logger.handlers:
            handler.close()
        
        self.audit_logger.handlers.clear()


# Global audit logger instance
_global_audit_logger: Optional[PQCAuditLogger] = None


def get_audit_logger() -> PQCAuditLogger:
    """Get the global audit logger instance."""
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = PQCAuditLogger()
    return _global_audit_logger


def close_audit_logger() -> None:
    """Close the global audit logger."""
    global _global_audit_logger
    if _global_audit_logger is not None:
        _global_audit_logger.close()
        _global_audit_logger = None


# Convenience functions for common audit events
def audit_key_generation(algorithm: str, key_source: str, public_key_hash: str) -> None:
    """Audit a key generation event."""
    get_audit_logger().log_key_generation(algorithm, key_source, public_key_hash)


def audit_key_loading(key_type: str, key_source: str, public_key_hash: str, success: bool) -> None:
    """Audit a key loading event."""
    get_audit_logger().log_key_loading(key_type, key_source, public_key_hash, success)


def audit_key_rotation(old_key_hash: Optional[str], new_key_hash: str, success: bool) -> None:
    """Audit a key rotation event."""
    get_audit_logger().log_key_rotation(old_key_hash, new_key_hash, success)


def audit_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO") -> None:
    """Audit a security event."""
    get_audit_logger().log_security_event(event_type, details, severity)


def audit_error(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Audit an error event."""
    get_audit_logger().log_error(error_type, error_message, context)