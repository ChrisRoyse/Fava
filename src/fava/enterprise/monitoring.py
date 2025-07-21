"""
Enterprise monitoring and observability integration.

This module provides comprehensive monitoring capabilities including Prometheus metrics,
OpenTelemetry tracing, SIEM integration, and audit logging for enterprise deployments.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timezone
import threading
import queue
import uuid
from pathlib import Path

from .dependency_manager import DependencyManager, enterprise_feature

logger = logging.getLogger(__name__)


@dataclass
class MetricDefinition:
    """Definition of a Prometheus metric."""
    name: str
    metric_type: str  # 'counter', 'histogram', 'gauge', 'summary'
    description: str
    labels: List[str] = field(default_factory=list)


@dataclass
class AuditEvent:
    """Audit event structure for enterprise compliance."""
    event_id: str
    timestamp: float
    event_type: str
    user: Optional[str]
    component: str
    action: str
    resource: Optional[str]
    outcome: str  # 'success', 'failure', 'warning'
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = 'info'  # 'critical', 'high', 'medium', 'low', 'info'


class MetricsCollector:
    """Enterprise metrics collection with Prometheus integration."""
    
    # Standard Fava PQC metrics
    STANDARD_METRICS = [
        MetricDefinition(
            'fava_pqc_key_operations_total',
            'counter',
            'Total number of PQC key operations',
            ['operation', 'algorithm', 'outcome']
        ),
        MetricDefinition(
            'fava_pqc_key_rotation_duration_seconds',
            'histogram',
            'Time taken for PQC key rotation operations',
            ['algorithm', 'key_source']
        ),
        MetricDefinition(
            'fava_pqc_vault_connection_status',
            'gauge',
            'Vault connection status (1=connected, 0=disconnected)',
            ['vault_url']
        ),
        MetricDefinition(
            'fava_pqc_hsm_connection_status',
            'gauge',
            'HSM connection status (1=connected, 0=disconnected)',
            ['hsm_token']
        ),
        MetricDefinition(
            'fava_pqc_active_sessions',
            'gauge',
            'Number of active user sessions',
            ['auth_method']
        ),
        MetricDefinition(
            'fava_pqc_signature_operations_total',
            'counter',
            'Total number of signature operations',
            ['algorithm', 'operation', 'outcome']
        ),
        MetricDefinition(
            'fava_pqc_encryption_operations_total',
            'counter',
            'Total number of encryption/decryption operations',
            ['algorithm', 'operation', 'outcome']
        ),
        MetricDefinition(
            'fava_pqc_key_age_days',
            'gauge',
            'Age of current active keys in days',
            ['key_type', 'algorithm']
        ),
        MetricDefinition(
            'fava_pqc_audit_events_total',
            'counter',
            'Total number of audit events',
            ['event_type', 'severity', 'outcome']
        ),
        MetricDefinition(
            'fava_pqc_performance_duration_seconds',
            'histogram',
            'Duration of various performance-sensitive operations',
            ['operation', 'component']
        )
    ]
    
    def __init__(self, enable_prometheus: bool = True):
        self.dep_manager = DependencyManager()
        self.prometheus_enabled = enable_prometheus
        self._metrics_registry = {}
        self._prometheus_metrics = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize metrics based on available dependencies."""
        if self.prometheus_enabled and self.dep_manager.is_available('prometheus'):
            self._setup_prometheus_metrics()
        else:
            self._setup_fallback_metrics()
    
    @enterprise_feature('prometheus', fallback_value=None)
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics if available."""
        prometheus_client = self.dep_manager.get_module('prometheus')
        if not prometheus_client:
            logger.warning("Prometheus client not available, using fallback metrics")
            self._setup_fallback_metrics()
            return
        
        logger.info("Setting up Prometheus metrics for Fava PQC")
        
        for metric_def in self.STANDARD_METRICS:
            try:
                if metric_def.metric_type == 'counter':
                    metric = prometheus_client.Counter(
                        metric_def.name, 
                        metric_def.description,
                        labelnames=metric_def.labels
                    )
                elif metric_def.metric_type == 'histogram':
                    metric = prometheus_client.Histogram(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels,
                        buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
                    )
                elif metric_def.metric_type == 'gauge':
                    metric = prometheus_client.Gauge(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels
                    )
                elif metric_def.metric_type == 'summary':
                    metric = prometheus_client.Summary(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels
                    )
                else:
                    logger.warning(f"Unknown metric type: {metric_def.metric_type}")
                    continue
                
                self._prometheus_metrics[metric_def.name] = metric
                self._metrics_registry[metric_def.name] = metric_def
                
            except Exception as e:
                logger.error(f"Failed to create metric {metric_def.name}: {e}")
        
        logger.info(f"Initialized {len(self._prometheus_metrics)} Prometheus metrics")
    
    def _setup_fallback_metrics(self):
        """Setup fallback metrics collection when Prometheus is not available."""
        logger.info("Setting up fallback metrics collection")
        
        for metric_def in self.STANDARD_METRICS:
            self._metrics_registry[metric_def.name] = metric_def
            self._prometheus_metrics[metric_def.name] = FallbackMetric(metric_def)
        
        logger.info(f"Initialized {len(self._metrics_registry)} fallback metrics")
    
    def increment_counter(self, metric_name: str, labels: Optional[Dict[str, str]] = None, value: float = 1):
        """Increment a counter metric."""
        metric = self._prometheus_metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric not found: {metric_name}")
            return
        
        try:
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
        except Exception as e:
            logger.error(f"Failed to increment counter {metric_name}: {e}")
    
    def set_gauge(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        metric = self._prometheus_metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric not found: {metric_name}")
            return
        
        try:
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
        except Exception as e:
            logger.error(f"Failed to set gauge {metric_name}: {e}")
    
    def observe_histogram(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a value in a histogram metric."""
        metric = self._prometheus_metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric not found: {metric_name}")
            return
        
        try:
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)
        except Exception as e:
            logger.error(f"Failed to observe histogram {metric_name}: {e}")
    
    def time_operation(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        return MetricTimer(self, metric_name, labels)
    
    def record_key_operation(self, operation: str, algorithm: str, outcome: str, duration: Optional[float] = None):
        """Record a PQC key operation."""
        self.increment_counter('fava_pqc_key_operations_total', {
            'operation': operation,
            'algorithm': algorithm,
            'outcome': outcome
        })
        
        if duration is not None:
            self.observe_histogram('fava_pqc_performance_duration_seconds', duration, {
                'operation': operation,
                'component': 'key_management'
            })
    
    def record_vault_status(self, vault_url: str, connected: bool):
        """Record Vault connection status."""
        self.set_gauge('fava_pqc_vault_connection_status', 1.0 if connected else 0.0, {
            'vault_url': vault_url
        })
    
    def record_hsm_status(self, hsm_token: str, connected: bool):
        """Record HSM connection status."""
        self.set_gauge('fava_pqc_hsm_connection_status', 1.0 if connected else 0.0, {
            'hsm_token': hsm_token
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of metrics status."""
        return {
            'prometheus_enabled': self.prometheus_enabled,
            'prometheus_available': self.dep_manager.is_available('prometheus'),
            'metrics_count': len(self._metrics_registry),
            'initialized_metrics': list(self._prometheus_metrics.keys()),
            'fallback_mode': not self.dep_manager.is_available('prometheus')
        }


class FallbackMetric:
    """Fallback metric implementation when Prometheus is not available."""
    
    def __init__(self, metric_def: MetricDefinition):
        self.metric_def = metric_def
        self._value = 0.0
        self._observations = []
        self._labels_values = {}
    
    def inc(self, value: float = 1):
        self._value += value
        logger.debug(f"Fallback metric {self.metric_def.name}: incremented by {value}")
    
    def set(self, value: float):
        self._value = value
        logger.debug(f"Fallback metric {self.metric_def.name}: set to {value}")
    
    def observe(self, value: float):
        self._observations.append(value)
        logger.debug(f"Fallback metric {self.metric_def.name}: observed {value}")
    
    def labels(self, **kwargs):
        """Return self for label chaining (simplified fallback)."""
        return self
    
    def time(self):
        """Return self for timing context (simplified fallback)."""
        return self
    
    def __enter__(self):
        self._start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, '_start_time'):
            duration = time.time() - self._start_time
            self.observe(duration)


class MetricTimer:
    """Context manager for timing operations with metrics."""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.observe_histogram(self.metric_name, duration, self.labels)


class AuditLogger:
    """Enterprise audit logging with SIEM integration."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dep_manager = DependencyManager()
        
        # Audit configuration
        self.enabled = self.config.get('enabled', True)
        self.destinations = self.config.get('destinations', ['file'])
        self.log_level = self.config.get('log_level', 'INFO')
        self.log_file = Path(self.config.get('log_file', 'fava-pqc-audit.log'))
        self.retention_days = self.config.get('retention_days', 2555)  # 7 years default
        
        # Event queue for async logging
        self._event_queue = queue.Queue()
        self._logging_thread = None
        self._shutdown_event = threading.Event()
        
        if self.enabled:
            self._start_logging_thread()
    
    def _start_logging_thread(self):
        """Start background thread for audit logging."""
        self._logging_thread = threading.Thread(target=self._log_worker, daemon=True)
        self._logging_thread.start()
        logger.info("Audit logging thread started")
    
    def _log_worker(self):
        """Background worker for processing audit events."""
        while not self._shutdown_event.is_set():
            try:
                # Get event with timeout to allow for shutdown check
                event = self._event_queue.get(timeout=1.0)
                self._process_audit_event(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audit logging error: {e}")
    
    def _process_audit_event(self, event: AuditEvent):
        """Process a single audit event."""
        try:
            # Format event for logging
            log_entry = {
                'event_id': event.event_id,
                'timestamp': datetime.fromtimestamp(event.timestamp, timezone.utc).isoformat(),
                'event_type': event.event_type,
                'user': event.user,
                'component': event.component,
                'action': event.action,
                'resource': event.resource,
                'outcome': event.outcome,
                'severity': event.severity,
                'details': event.details
            }
            
            # Send to configured destinations
            if 'file' in self.destinations:
                self._write_to_file(log_entry)
            
            if 'syslog' in self.destinations:
                self._write_to_syslog(log_entry)
            
            if 'json' in self.destinations:
                self._write_to_json(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to process audit event {event.event_id}: {e}")
    
    def _write_to_file(self, log_entry: Dict[str, Any]):
        """Write audit entry to log file."""
        try:
            # Ensure log directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")
    
    def _write_to_syslog(self, log_entry: Dict[str, Any]):
        """Write audit entry to syslog."""
        try:
            import syslog
            
            # Map severity to syslog priority
            severity_map = {
                'critical': syslog.LOG_CRIT,
                'high': syslog.LOG_ERR,
                'medium': syslog.LOG_WARNING,
                'low': syslog.LOG_INFO,
                'info': syslog.LOG_INFO
            }
            
            priority = severity_map.get(log_entry['severity'], syslog.LOG_INFO)
            message = f"FAVA_PQC_AUDIT: {json.dumps(log_entry)}"
            
            syslog.openlog("fava-pqc", syslog.LOG_PID)
            syslog.syslog(priority, message)
            syslog.closelog()
            
        except Exception as e:
            logger.error(f"Failed to write audit log to syslog: {e}")
    
    def _write_to_json(self, log_entry: Dict[str, Any]):
        """Write audit entry to JSON file for SIEM ingestion."""
        try:
            json_log_file = self.log_file.with_suffix('.json')
            
            with open(json_log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit log to JSON: {e}")
    
    def log_event(self, event_type: str, component: str, action: str,
                  outcome: str = 'success', user: Optional[str] = None,
                  resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                  severity: str = 'info'):
        """Log an audit event."""
        if not self.enabled:
            return
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=event_type,
            user=user or 'system',
            component=component,
            action=action,
            resource=resource,
            outcome=outcome,
            details=details or {},
            severity=severity
        )
        
        try:
            self._event_queue.put(event, timeout=1.0)
        except queue.Full:
            logger.error("Audit event queue is full, dropping event")
    
    # Convenience methods for common audit events
    def log_key_operation(self, operation: str, algorithm: str, outcome: str = 'success',
                         user: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log a key management operation."""
        self.log_event(
            event_type='key_management',
            component='crypto_service',
            action=f'key_{operation}',
            outcome=outcome,
            user=user,
            resource=f'{algorithm}_key',
            details=details,
            severity='medium' if outcome == 'failure' else 'info'
        )
    
    def log_authentication(self, auth_method: str, user: str, outcome: str = 'success',
                          details: Optional[Dict[str, Any]] = None):
        """Log an authentication event."""
        self.log_event(
            event_type='authentication',
            component='auth_service',
            action='login',
            outcome=outcome,
            user=user,
            resource=auth_method,
            details=details,
            severity='high' if outcome == 'failure' else 'info'
        )
    
    def log_configuration_change(self, setting: str, user: str, old_value: Any = None,
                               new_value: Any = None, outcome: str = 'success'):
        """Log a configuration change."""
        details = {}
        if old_value is not None:
            details['old_value'] = str(old_value)
        if new_value is not None:
            details['new_value'] = str(new_value)
        
        self.log_event(
            event_type='configuration',
            component='config_service',
            action='modify',
            outcome=outcome,
            user=user,
            resource=setting,
            details=details,
            severity='medium'
        )
    
    def log_security_event(self, event_type: str, component: str, action: str,
                          outcome: str = 'failure', user: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None):
        """Log a security-related event."""
        self.log_event(
            event_type=event_type,
            component=component,
            action=action,
            outcome=outcome,
            user=user,
            details=details,
            severity='high' if outcome == 'failure' else 'medium'
        )
    
    def shutdown(self):
        """Shutdown audit logger gracefully."""
        if self._logging_thread and not self._shutdown_event.is_set():
            logger.info("Shutting down audit logger...")
            self._shutdown_event.set()
            
            # Wait for queue to empty
            self._event_queue.join()
            
            # Wait for thread to finish
            self._logging_thread.join(timeout=5.0)
            
            if self._logging_thread.is_alive():
                logger.warning("Audit logging thread did not shut down cleanly")
            else:
                logger.info("Audit logger shut down successfully")


class OpenTelemetryTracer:
    """OpenTelemetry integration for distributed tracing."""
    
    def __init__(self, service_name: str = 'fava-pqc'):
        self.service_name = service_name
        self.dep_manager = DependencyManager()
        self._tracer = None
        self._initialize_tracer()
    
    @enterprise_feature('opentelemetry', fallback_value=None)
    def _initialize_tracer(self):
        """Initialize OpenTelemetry tracer if available."""
        otel = self.dep_manager.get_module('opentelemetry')
        if not otel:
            logger.info("OpenTelemetry not available, tracing disabled")
            return
        
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.resources import Resource
            
            # Set up tracer provider
            resource = Resource(attributes={"service.name": self.service_name})
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            self._tracer = trace.get_tracer(__name__)
            logger.info(f"OpenTelemetry tracer initialized for {self.service_name}")
            
        except ImportError as e:
            logger.warning(f"OpenTelemetry SDK not fully available: {e}")
    
    def start_span(self, span_name: str, **kwargs):
        """Start a new trace span."""
        if self._tracer:
            return self._tracer.start_span(span_name, **kwargs)
        else:
            # Return a no-op context manager
            return NoOpSpan()
    
    def trace_operation(self, operation_name: str):
        """Decorator for tracing operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.start_span(operation_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


class NoOpSpan:
    """No-op span context manager for when tracing is not available."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_attribute(self, key: str, value: Any):
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        pass


# Global instances for easy access
_metrics_collector = None
_audit_logger = None
_tracer = None


def get_metrics_collector(enable_prometheus: bool = True) -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(enable_prometheus)
    return _metrics_collector


def get_audit_logger(config: Optional[Dict[str, Any]] = None) -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(config)
    return _audit_logger


def get_tracer(service_name: str = 'fava-pqc') -> OpenTelemetryTracer:
    """Get global OpenTelemetry tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = OpenTelemetryTracer(service_name)
    return _tracer


def shutdown_monitoring():
    """Shutdown all monitoring components gracefully."""
    global _audit_logger
    if _audit_logger:
        _audit_logger.shutdown()
    
    logger.info("Enterprise monitoring components shut down")