"""
Advanced Performance Monitoring and Auto-Tuning System
======================================================

Comprehensive performance monitoring, analysis, and auto-tuning system specifically
designed for post-quantum cryptography operations. This system provides:

- Real-time performance metrics collection
- Intelligent auto-tuning based on workload patterns
- Performance regression detection
- Resource usage optimization
- Bottleneck identification and resolution
- Adaptive configuration management

Key Features:
- Sub-millisecond timing accuracy
- Memory usage tracking and optimization
- CPU utilization monitoring
- Cache performance analysis
- Thread contention detection
- Automatic parameter tuning
- Performance anomaly detection

Target Benefits:
- 10-20% automatic performance improvement through tuning
- Early detection of performance degradation
- Optimal resource allocation
- Reduced system overhead
- Proactive performance management
"""

import os
import time
import logging
import threading
import multiprocessing
import math
import statistics
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import queue
import json
from collections import defaultdict, deque
import weakref

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .lock_free_structures import LockFreeCounter, ConcurrentHashMap, get_global_metrics

logger = logging.getLogger(__name__)

# ============================================================================
# Core Performance Metrics and Data Structures
# ============================================================================

@dataclass
class OperationMetrics:
    """Detailed metrics for a single crypto operation."""
    operation_type: str
    algorithm: str
    duration_ns: int
    memory_used_bytes: int
    cpu_cycles: Optional[int]
    thread_id: int
    timestamp: float
    batch_size: int = 1
    cache_hits: int = 0
    cache_misses: int = 0
    
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration_ns / 1_000_000
    
    def duration_us(self) -> float:
        """Get duration in microseconds."""
        return self.duration_ns / 1_000

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    timestamp: float
    cpu_percent: float
    memory_used_mb: float
    memory_available_mb: float
    threads_active: int
    context_switches: int
    page_faults: int
    io_read_bytes: int
    io_write_bytes: int
    network_sent_bytes: int
    network_recv_bytes: int

@dataclass
class PerformanceProfile:
    """Performance profile for different operation types."""
    operation_type: str
    algorithm: str
    sample_count: int
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    median_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    std_deviation_ms: float
    throughput_ops_per_sec: float
    memory_efficiency_ratio: float
    last_updated: float

@dataclass
class TuningParameter:
    """Auto-tuning parameter configuration."""
    name: str
    current_value: Any
    min_value: Any
    max_value: Any
    step_size: Any
    parameter_type: str  # 'int', 'float', 'bool', 'enum'
    impact_weight: float = 1.0
    last_changed: float = 0.0
    performance_history: List[float] = field(default_factory=list)

# ============================================================================
# High-Precision Performance Monitor
# ============================================================================

class HighPrecisionTimer:
    """High-precision timer for accurate performance measurements."""
    
    def __init__(self):
        self._overhead_ns = self._calibrate_overhead()
        
    def _calibrate_overhead(self) -> int:
        """Calibrate timer overhead for more accurate measurements."""
        calibration_samples = []
        
        for _ in range(1000):
            start = time.perf_counter_ns()
            end = time.perf_counter_ns()
            calibration_samples.append(end - start)
        
        # Use minimum as overhead estimate (best case)
        overhead = min(calibration_samples)
        logger.debug(f"Timer overhead calibrated: {overhead}ns")
        return overhead
    
    @contextmanager
    def measure(self):
        """Context manager for high-precision timing."""
        start_time = time.perf_counter_ns()
        yield
        end_time = time.perf_counter_ns()
        
        # Subtract overhead for more accurate measurement
        raw_duration = end_time - start_time
        adjusted_duration = max(0, raw_duration - self._overhead_ns)
        
        # Store result for retrieval
        self._last_measurement_ns = adjusted_duration
    
    def get_last_measurement_ns(self) -> int:
        """Get the last measurement in nanoseconds."""
        return getattr(self, '_last_measurement_ns', 0)

class MemoryTracker:
    """Memory usage tracker for detailed memory profiling."""
    
    def __init__(self):
        self._baseline_memory = self._get_memory_usage()
        
    def _get_memory_usage(self) -> Dict[str, int]:
        """Get detailed memory usage information."""
        if HAS_PSUTIL:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_bytes': memory_info.rss,
                'vms_bytes': memory_info.vms,
                'peak_bytes': getattr(memory_info, 'peak_wss', memory_info.rss),
                'shared_bytes': getattr(memory_info, 'shared', 0)
            }
        else:
            # Fallback using basic methods
            import sys
            return {
                'rss_bytes': sys.getsizeof({}),  # Minimal fallback
                'vms_bytes': 0,
                'peak_bytes': 0,
                'shared_bytes': 0
            }
    
    @contextmanager
    def track_memory(self):
        """Context manager for memory usage tracking."""
        start_memory = self._get_memory_usage()
        yield
        end_memory = self._get_memory_usage()
        
        # Calculate memory delta
        self._last_memory_delta = {
            'rss_delta': end_memory['rss_bytes'] - start_memory['rss_bytes'],
            'vms_delta': end_memory['vms_bytes'] - start_memory['vms_bytes'],
            'peak_used': end_memory['peak_bytes'],
            'efficiency_ratio': start_memory['rss_bytes'] / max(1, end_memory['rss_bytes'])
        }
    
    def get_last_memory_delta(self) -> Dict[str, int]:
        """Get the last memory usage delta."""
        return getattr(self, '_last_memory_delta', {
            'rss_delta': 0, 'vms_delta': 0, 'peak_used': 0, 'efficiency_ratio': 1.0
        })

# ============================================================================
# Advanced Performance Monitor
# ============================================================================

class PerformanceMonitor:
    """Advanced performance monitoring system."""
    
    def __init__(self, 
                 max_samples: int = 50000,
                 enable_system_monitoring: bool = True,
                 monitoring_interval_seconds: float = 1.0):
        
        self.max_samples = max_samples
        self.enable_system_monitoring = enable_system_monitoring
        self.monitoring_interval = monitoring_interval_seconds
        
        # Core data storage
        self._operation_metrics: deque = deque(maxlen=max_samples)
        self._system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 system snapshots
        self._performance_profiles: Dict[str, PerformanceProfile] = {}
        
        # High-precision timing
        self._timer = HighPrecisionTimer()
        self._memory_tracker = MemoryTracker()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring thread
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        
        # Performance analysis
        self._anomaly_detector = PerformanceAnomalyDetector()
        self._bottleneck_analyzer = BottleneckAnalyzer()
        
        # Statistics
        self._total_operations = LockFreeCounter()
        self._total_monitoring_time = LockFreeCounter()
        
        # Initialize
        self._initialization_time = time.time()
        
        if enable_system_monitoring:
            self._start_system_monitoring()
        
        logger.info(f"Performance monitor initialized: max_samples={max_samples}, "
                   f"system_monitoring={enable_system_monitoring}")
    
    def _start_system_monitoring(self):
        """Start background system monitoring."""
        if self._monitor_thread is None and HAS_PSUTIL:
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(target=self._system_monitoring_loop, daemon=True)
            self._monitor_thread.start()
    
    def _system_monitoring_loop(self):
        """Background system monitoring loop."""
        while not self._stop_monitoring.wait(self.monitoring_interval):
            try:
                if HAS_PSUTIL:
                    # Collect system metrics
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    cpu_percent = process.cpu_percent()
                    
                    system_wide = psutil.virtual_memory()
                    
                    metrics = SystemMetrics(
                        timestamp=time.time(),
                        cpu_percent=cpu_percent,
                        memory_used_mb=memory_info.rss / 1024 / 1024,
                        memory_available_mb=system_wide.available / 1024 / 1024,
                        threads_active=process.num_threads(),
                        context_switches=getattr(process, 'num_ctx_switches', lambda: (0, 0))().voluntary,
                        page_faults=getattr(process, 'memory_info_ex', lambda: type('', (), {'pfaults': 0}))().pfaults if hasattr(process, 'memory_info_ex') else 0,
                        io_read_bytes=getattr(process, 'io_counters', lambda: type('', (), {'read_bytes': 0}))().read_bytes if hasattr(process, 'io_counters') else 0,
                        io_write_bytes=getattr(process, 'io_counters', lambda: type('', (), {'write_bytes': 0}))().write_bytes if hasattr(process, 'io_counters') else 0,
                        network_sent_bytes=0,  # Would need network monitoring
                        network_recv_bytes=0
                    )
                    
                    with self._lock:
                        self._system_metrics.append(metrics)
                        
            except Exception as e:
                logger.debug(f"System monitoring error: {e}")
    
    @contextmanager
    def measure_operation(self, operation_type: str, algorithm: str = "", batch_size: int = 1):
        """Context manager for measuring crypto operations."""
        thread_id = threading.current_thread().ident
        
        # Start measurement
        with self._timer.measure():
            with self._memory_tracker.track_memory():
                yield
        
        # Collect measurements
        duration_ns = self._timer.get_last_measurement_ns()
        memory_delta = self._memory_tracker.get_last_memory_delta()
        
        # Create metrics record
        metrics = OperationMetrics(
            operation_type=operation_type,
            algorithm=algorithm,
            duration_ns=duration_ns,
            memory_used_bytes=memory_delta.get('rss_delta', 0),
            cpu_cycles=None,  # Could be measured with specialized hardware
            thread_id=thread_id,
            timestamp=time.time(),
            batch_size=batch_size
        )
        
        # Store metrics
        with self._lock:
            self._operation_metrics.append(metrics)
            self._total_operations.increment()
            self._total_monitoring_time.add(duration_ns)
        
        # Update performance profiles
        self._update_performance_profile(metrics)
        
        # Check for anomalies
        self._anomaly_detector.check_for_anomaly(metrics)
    
    def _update_performance_profile(self, metrics: OperationMetrics):
        """Update performance profile for operation type."""
        profile_key = f"{metrics.operation_type}_{metrics.algorithm}"
        
        with self._lock:
            if profile_key not in self._performance_profiles:
                # Create new profile
                self._performance_profiles[profile_key] = PerformanceProfile(
                    operation_type=metrics.operation_type,
                    algorithm=metrics.algorithm,
                    sample_count=0,
                    avg_duration_ms=0.0,
                    min_duration_ms=float('inf'),
                    max_duration_ms=0.0,
                    median_duration_ms=0.0,
                    p95_duration_ms=0.0,
                    p99_duration_ms=0.0,
                    std_deviation_ms=0.0,
                    throughput_ops_per_sec=0.0,
                    memory_efficiency_ratio=1.0,
                    last_updated=time.time()
                )
            
            profile = self._performance_profiles[profile_key]
            
            # Get recent samples for this profile
            recent_samples = [
                m for m in self._operation_metrics 
                if m.operation_type == metrics.operation_type and m.algorithm == metrics.algorithm
            ][-1000:]  # Last 1000 samples
            
            if recent_samples:
                durations_ms = [m.duration_ms() for m in recent_samples]
                
                # Update profile statistics
                profile.sample_count = len(recent_samples)
                profile.avg_duration_ms = statistics.mean(durations_ms)
                profile.min_duration_ms = min(durations_ms)
                profile.max_duration_ms = max(durations_ms)
                profile.median_duration_ms = statistics.median(durations_ms)
                
                # Calculate percentiles
                sorted_durations = sorted(durations_ms)
                profile.p95_duration_ms = sorted_durations[int(len(sorted_durations) * 0.95)]
                profile.p99_duration_ms = sorted_durations[int(len(sorted_durations) * 0.99)]
                
                # Standard deviation
                profile.std_deviation_ms = statistics.stdev(durations_ms) if len(durations_ms) > 1 else 0.0
                
                # Throughput calculation
                time_window = 60.0  # Last 60 seconds
                recent_time = time.time() - time_window
                recent_ops = [m for m in recent_samples if m.timestamp >= recent_time]
                profile.throughput_ops_per_sec = len(recent_ops) / time_window
                
                # Memory efficiency
                memory_used = [abs(m.memory_used_bytes) for m in recent_samples]
                avg_memory = statistics.mean(memory_used) if memory_used else 1
                profile.memory_efficiency_ratio = 1.0 / max(1, avg_memory / 1024)  # Inverse of KB used
                
                profile.last_updated = time.time()
    
    def get_operation_statistics(self, operation_type: str = None, algorithm: str = None) -> Dict[str, Any]:
        """Get detailed statistics for operations."""
        with self._lock:
            # Filter metrics
            filtered_metrics = self._operation_metrics
            
            if operation_type:
                filtered_metrics = [m for m in filtered_metrics if m.operation_type == operation_type]
            
            if algorithm:
                filtered_metrics = [m for m in filtered_metrics if m.algorithm == algorithm]
            
            if not filtered_metrics:
                return {'error': 'No matching metrics found'}
            
            # Calculate comprehensive statistics
            durations_ms = [m.duration_ms() for m in filtered_metrics]
            durations_ns = [m.duration_ns for m in filtered_metrics]
            memory_usage = [abs(m.memory_used_bytes) for m in filtered_metrics]
            
            # Time-based analysis
            sorted_durations_ms = sorted(durations_ms)
            
            # Throughput analysis
            time_windows = [1, 5, 15, 60]  # seconds
            current_time = time.time()
            throughput_stats = {}
            
            for window in time_windows:
                recent_ops = [m for m in filtered_metrics if current_time - m.timestamp <= window]
                throughput_stats[f'throughput_{window}s'] = len(recent_ops) / window
            
            # Thread distribution
            thread_distribution = defaultdict(int)
            for m in filtered_metrics:
                thread_distribution[m.thread_id] += 1
            
            # Batch size analysis
            batch_sizes = [m.batch_size for m in filtered_metrics]
            
            return {
                'sample_count': len(filtered_metrics),
                'time_range_seconds': max(m.timestamp for m in filtered_metrics) - min(m.timestamp for m in filtered_metrics),
                
                # Duration statistics
                'duration_ms': {
                    'avg': statistics.mean(durations_ms),
                    'median': statistics.median(durations_ms),
                    'min': min(durations_ms),
                    'max': max(durations_ms),
                    'std_dev': statistics.stdev(durations_ms) if len(durations_ms) > 1 else 0,
                    'p50': sorted_durations_ms[len(sorted_durations_ms) // 2],
                    'p90': sorted_durations_ms[int(len(sorted_durations_ms) * 0.90)],
                    'p95': sorted_durations_ms[int(len(sorted_durations_ms) * 0.95)],
                    'p99': sorted_durations_ms[int(len(sorted_durations_ms) * 0.99)],
                    'p99.9': sorted_durations_ms[int(len(sorted_durations_ms) * 0.999)]
                },
                
                # High-precision nanosecond stats
                'duration_ns': {
                    'avg': statistics.mean(durations_ns),
                    'min': min(durations_ns),
                    'max': max(durations_ns)
                },
                
                # Memory statistics
                'memory_bytes': {
                    'avg': statistics.mean(memory_usage),
                    'median': statistics.median(memory_usage),
                    'min': min(memory_usage),
                    'max': max(memory_usage),
                    'total': sum(memory_usage)
                } if memory_usage else {},
                
                # Throughput statistics
                'throughput': throughput_stats,
                
                # Thread distribution
                'thread_distribution': dict(thread_distribution),
                'unique_threads': len(thread_distribution),
                
                # Batch analysis
                'batch_analysis': {
                    'avg_batch_size': statistics.mean(batch_sizes),
                    'max_batch_size': max(batch_sizes),
                    'min_batch_size': min(batch_sizes)
                } if batch_sizes else {},
                
                # Performance targets analysis
                'target_analysis': self._analyze_performance_targets(durations_ms)
            }
    
    def _analyze_performance_targets(self, durations_ms: List[float]) -> Dict[str, Any]:
        """Analyze performance against target thresholds."""
        targets = {
            'excellent': 0.05,    # <0.05ms
            'good': 0.1,          # <0.1ms
            'acceptable': 0.15,   # <0.15ms
            'poor': 1.0           # <1.0ms
        }
        
        analysis = {}
        total_ops = len(durations_ms)
        
        for target_name, threshold_ms in targets.items():
            under_threshold = sum(1 for d in durations_ms if d <= threshold_ms)
            percentage = (under_threshold / total_ops) * 100 if total_ops > 0 else 0
            analysis[target_name] = {
                'threshold_ms': threshold_ms,
                'ops_under_threshold': under_threshold,
                'percentage': percentage
            }
        
        # Overall performance grade
        if analysis['excellent']['percentage'] >= 95:
            analysis['overall_grade'] = 'A+'
        elif analysis['good']['percentage'] >= 90:
            analysis['overall_grade'] = 'A'
        elif analysis['acceptable']['percentage'] >= 80:
            analysis['overall_grade'] = 'B'
        elif analysis['poor']['percentage'] >= 70:
            analysis['overall_grade'] = 'C'
        else:
            analysis['overall_grade'] = 'D'
        
        return analysis
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide performance statistics."""
        with self._lock:
            if not self._system_metrics:
                return {'error': 'No system metrics available'}
            
            # Recent metrics (last 5 minutes)
            recent_time = time.time() - 300
            recent_metrics = [m for m in self._system_metrics if m.timestamp >= recent_time]
            
            if not recent_metrics:
                return {'error': 'No recent system metrics'}
            
            # Calculate system statistics
            cpu_values = [m.cpu_percent for m in recent_metrics]
            memory_values = [m.memory_used_mb for m in recent_metrics]
            thread_values = [m.threads_active for m in recent_metrics]
            
            return {
                'sample_count': len(recent_metrics),
                'time_range_minutes': (max(m.timestamp for m in recent_metrics) - 
                                     min(m.timestamp for m in recent_metrics)) / 60,
                
                'cpu_usage': {
                    'avg_percent': statistics.mean(cpu_values),
                    'max_percent': max(cpu_values),
                    'min_percent': min(cpu_values),
                    'current_percent': recent_metrics[-1].cpu_percent
                },
                
                'memory_usage': {
                    'avg_mb': statistics.mean(memory_values),
                    'max_mb': max(memory_values),
                    'min_mb': min(memory_values),
                    'current_mb': recent_metrics[-1].memory_used_mb,
                    'available_mb': recent_metrics[-1].memory_available_mb
                },
                
                'thread_activity': {
                    'avg_threads': statistics.mean(thread_values),
                    'max_threads': max(thread_values),
                    'min_threads': min(thread_values),
                    'current_threads': recent_metrics[-1].threads_active
                }
            }
    
    def get_performance_profiles(self) -> Dict[str, PerformanceProfile]:
        """Get all performance profiles."""
        with self._lock:
            return self._performance_profiles.copy()
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        report = {
            'monitor_info': {
                'initialization_time': self._initialization_time,
                'uptime_seconds': time.time() - self._initialization_time,
                'total_operations_monitored': self._total_operations.get(),
                'total_monitoring_overhead_ms': self._total_monitoring_time.get() / 1_000_000,
                'avg_monitoring_overhead_ns': self._total_monitoring_time.get() / max(1, self._total_operations.get())
            },
            
            'operation_statistics': {},
            'system_statistics': self.get_system_statistics(),
            'performance_profiles': {k: v.__dict__ for k, v in self.get_performance_profiles().items()},
            'anomaly_report': self._anomaly_detector.get_anomaly_report(),
            'bottleneck_analysis': self._bottleneck_analyzer.analyze_bottlenecks(self._operation_metrics),
            'recommendations': self._generate_performance_recommendations()
        }
        
        # Get statistics for each unique operation type/algorithm combination
        unique_operations = set((m.operation_type, m.algorithm) for m in self._operation_metrics)
        
        for operation_type, algorithm in unique_operations:
            key = f"{operation_type}_{algorithm}" if algorithm else operation_type
            report['operation_statistics'][key] = self.get_operation_statistics(operation_type, algorithm)
        
        return report
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Analyze current performance profiles
        for profile_key, profile in self._performance_profiles.items():
            if profile.avg_duration_ms > 0.2:  # Slower than 0.2ms
                recommendations.append(f"Operation {profile_key} is slow (avg: {profile.avg_duration_ms:.3f}ms) - consider optimization")
            
            if profile.throughput_ops_per_sec < 1000:  # Low throughput
                recommendations.append(f"Operation {profile_key} has low throughput ({profile.throughput_ops_per_sec:.0f} ops/sec) - consider batching")
            
            if profile.std_deviation_ms > profile.avg_duration_ms * 0.5:  # High variance
                recommendations.append(f"Operation {profile_key} has high latency variance - investigate consistency issues")
        
        # System-level recommendations
        system_stats = self.get_system_statistics()
        if system_stats.get('cpu_usage', {}).get('avg_percent', 0) > 80:
            recommendations.append("High CPU usage detected - consider load balancing or optimization")
        
        if system_stats.get('memory_usage', {}).get('current_mb', 0) > 1000:
            recommendations.append("High memory usage detected - consider memory pool optimization")
        
        # Thread contention analysis
        thread_dist = {}
        for metrics in self._operation_metrics:
            thread_dist[metrics.thread_id] = thread_dist.get(metrics.thread_id, 0) + 1
        
        if len(thread_dist) > multiprocessing.cpu_count() * 2:
            recommendations.append("High thread count detected - consider thread pool optimization")
        
        return recommendations
    
    def export_metrics(self, filepath: str, format: str = 'json'):
        """Export metrics to file."""
        report = self.get_comprehensive_report()
        
        try:
            with open(filepath, 'w') as f:
                if format.lower() == 'json':
                    json.dump(report, f, indent=2, default=str)
                else:
                    # Simple text format
                    f.write("Performance Monitor Report\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for key, value in report.items():
                        f.write(f"{key}:\n{value}\n\n")
            
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def reset_statistics(self):
        """Reset all collected statistics."""
        with self._lock:
            self._operation_metrics.clear()
            self._system_metrics.clear()
            self._performance_profiles.clear()
            self._total_operations.reset()
            self._total_monitoring_time.reset()
            self._anomaly_detector.reset()
        
        logger.info("Performance statistics reset")
    
    def shutdown(self):
        """Shutdown the performance monitor."""
        logger.info("Shutting down performance monitor...")
        
        if self._monitor_thread:
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        
        logger.info("Performance monitor shutdown complete")

# ============================================================================
# Performance Anomaly Detection
# ============================================================================

class PerformanceAnomalyDetector:
    """Detect performance anomalies and regressions."""
    
    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity  # Number of standard deviations for anomaly
        self._baseline_metrics = {}
        self._anomalies_detected = []
        self._lock = threading.Lock()
    
    def check_for_anomaly(self, metrics: OperationMetrics):
        """Check if metrics represent a performance anomaly."""
        operation_key = f"{metrics.operation_type}_{metrics.algorithm}"
        
        with self._lock:
            if operation_key not in self._baseline_metrics:
                # Initialize baseline
                self._baseline_metrics[operation_key] = {
                    'durations': deque(maxlen=100),
                    'avg': 0.0,
                    'std_dev': 0.0,
                    'last_update': time.time()
                }
            
            baseline = self._baseline_metrics[operation_key]
            baseline['durations'].append(metrics.duration_ms())
            
            # Update baseline statistics
            if len(baseline['durations']) >= 10:
                durations = list(baseline['durations'])
                baseline['avg'] = statistics.mean(durations)
                baseline['std_dev'] = statistics.stdev(durations) if len(durations) > 1 else 0.0
                
                # Check for anomaly
                if baseline['std_dev'] > 0:
                    z_score = abs(metrics.duration_ms() - baseline['avg']) / baseline['std_dev']
                    
                    if z_score > self.sensitivity:
                        anomaly = {
                            'timestamp': metrics.timestamp,
                            'operation_key': operation_key,
                            'duration_ms': metrics.duration_ms(),
                            'baseline_avg': baseline['avg'],
                            'z_score': z_score,
                            'severity': 'high' if z_score > 3.0 else 'medium',
                            'description': f"Duration {metrics.duration_ms():.3f}ms is {z_score:.1f} std devs from baseline {baseline['avg']:.3f}ms"
                        }
                        
                        self._anomalies_detected.append(anomaly)
                        
                        # Keep only recent anomalies
                        if len(self._anomalies_detected) > 1000:
                            self._anomalies_detected = self._anomalies_detected[-1000:]
                        
                        logger.warning(f"Performance anomaly detected: {anomaly['description']}")
    
    def get_anomaly_report(self) -> Dict[str, Any]:
        """Get report of detected anomalies."""
        with self._lock:
            recent_anomalies = [a for a in self._anomalies_detected 
                              if time.time() - a['timestamp'] < 3600]  # Last hour
            
            severity_counts = defaultdict(int)
            for anomaly in recent_anomalies:
                severity_counts[anomaly['severity']] += 1
            
            return {
                'total_anomalies': len(self._anomalies_detected),
                'recent_anomalies': len(recent_anomalies),
                'severity_distribution': dict(severity_counts),
                'latest_anomalies': recent_anomalies[-10:] if recent_anomalies else []
            }
    
    def reset(self):
        """Reset anomaly detection state."""
        with self._lock:
            self._baseline_metrics.clear()
            self._anomalies_detected.clear()

# ============================================================================
# Bottleneck Analysis
# ============================================================================

class BottleneckAnalyzer:
    """Analyze performance bottlenecks and suggest optimizations."""
    
    def analyze_bottlenecks(self, operation_metrics: deque) -> Dict[str, Any]:
        """Analyze bottlenecks from operation metrics."""
        if not operation_metrics:
            return {'error': 'No metrics to analyze'}
        
        analysis = {
            'slowest_operations': self._find_slowest_operations(operation_metrics),
            'thread_contention': self._analyze_thread_contention(operation_metrics),
            'memory_intensive_operations': self._find_memory_intensive_operations(operation_metrics),
            'throughput_bottlenecks': self._analyze_throughput_bottlenecks(operation_metrics),
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_bottleneck_recommendations(analysis)
        
        return analysis
    
    def _find_slowest_operations(self, metrics: deque, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find the slowest operations."""
        sorted_metrics = sorted(metrics, key=lambda m: m.duration_ms(), reverse=True)
        
        return [
            {
                'operation_type': m.operation_type,
                'algorithm': m.algorithm,
                'duration_ms': m.duration_ms(),
                'thread_id': m.thread_id,
                'timestamp': m.timestamp
            }
            for m in sorted_metrics[:top_n]
        ]
    
    def _analyze_thread_contention(self, metrics: deque) -> Dict[str, Any]:
        """Analyze thread contention patterns."""
        thread_metrics = defaultdict(list)
        
        for metric in metrics:
            thread_metrics[metric.thread_id].append(metric)
        
        # Calculate thread statistics
        thread_stats = {}
        for thread_id, thread_ops in thread_metrics.items():
            durations = [m.duration_ms() for m in thread_ops]
            thread_stats[thread_id] = {
                'operation_count': len(thread_ops),
                'avg_duration_ms': statistics.mean(durations),
                'max_duration_ms': max(durations),
                'variance': statistics.variance(durations) if len(durations) > 1 else 0
            }
        
        # Identify contention indicators
        avg_ops_per_thread = len(metrics) / len(thread_stats)
        high_variance_threads = [
            tid for tid, stats in thread_stats.items()
            if stats['variance'] > stats['avg_duration_ms'] ** 2
        ]
        
        return {
            'total_threads': len(thread_stats),
            'avg_operations_per_thread': avg_ops_per_thread,
            'thread_statistics': thread_stats,
            'high_variance_threads': high_variance_threads,
            'contention_detected': len(high_variance_threads) > len(thread_stats) * 0.3
        }
    
    def _find_memory_intensive_operations(self, metrics: deque, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find operations that use the most memory."""
        memory_metrics = [m for m in metrics if m.memory_used_bytes > 0]
        sorted_by_memory = sorted(memory_metrics, key=lambda m: m.memory_used_bytes, reverse=True)
        
        return [
            {
                'operation_type': m.operation_type,
                'algorithm': m.algorithm,
                'memory_used_bytes': m.memory_used_bytes,
                'memory_used_kb': m.memory_used_bytes / 1024,
                'duration_ms': m.duration_ms(),
                'memory_efficiency': m.memory_used_bytes / max(1, m.duration_ns)  # bytes per nanosecond
            }
            for m in sorted_by_memory[:top_n]
        ]
    
    def _analyze_throughput_bottlenecks(self, metrics: deque) -> Dict[str, Any]:
        """Analyze throughput bottlenecks."""
        if not metrics:
            return {}
        
        # Group by operation type
        operation_groups = defaultdict(list)
        for metric in metrics:
            key = f"{metric.operation_type}_{metric.algorithm}"
            operation_groups[key].append(metric)
        
        throughput_analysis = {}
        
        for op_key, op_metrics in operation_groups.items():
            # Calculate throughput over time windows
            time_windows = [1, 5, 15, 60]  # seconds
            current_time = time.time()
            
            window_throughputs = {}
            for window in time_windows:
                recent_ops = [m for m in op_metrics if current_time - m.timestamp <= window]
                window_throughputs[f'{window}s'] = len(recent_ops) / window
            
            # Identify bottleneck patterns
            avg_duration = statistics.mean([m.duration_ms() for m in op_metrics])
            theoretical_max_throughput = 1000 / avg_duration  # ops per second
            
            throughput_analysis[op_key] = {
                'current_throughput': window_throughputs,
                'theoretical_max_throughput': theoretical_max_throughput,
                'efficiency_ratio': window_throughputs.get('5s', 0) / max(1, theoretical_max_throughput),
                'avg_duration_ms': avg_duration,
                'bottleneck_severity': 'high' if window_throughputs.get('5s', 0) < theoretical_max_throughput * 0.5 else 'low'
            }
        
        return throughput_analysis
    
    def _generate_bottleneck_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on bottleneck analysis."""
        recommendations = []
        
        # Slow operations recommendations
        slowest_ops = analysis.get('slowest_operations', [])
        if slowest_ops:
            avg_slowest = statistics.mean([op['duration_ms'] for op in slowest_ops[:5]])
            if avg_slowest > 1.0:
                recommendations.append(f"Top operations are very slow (avg: {avg_slowest:.2f}ms). Consider SIMD optimization or algorithm improvements.")
            elif avg_slowest > 0.2:
                recommendations.append(f"Top operations are slow (avg: {avg_slowest:.2f}ms). Consider memory pooling and batch processing.")
        
        # Thread contention recommendations
        thread_analysis = analysis.get('thread_contention', {})
        if thread_analysis.get('contention_detected', False):
            recommendations.append("Thread contention detected. Consider reducing lock scope or implementing lock-free data structures.")
        
        if thread_analysis.get('total_threads', 0) > multiprocessing.cpu_count() * 3:
            recommendations.append("High thread count detected. Consider implementing work-stealing or reducing thread pool size.")
        
        # Memory recommendations
        memory_ops = analysis.get('memory_intensive_operations', [])
        if memory_ops:
            avg_memory_mb = statistics.mean([op['memory_used_kb'] for op in memory_ops[:3]]) / 1024
            if avg_memory_mb > 10:
                recommendations.append(f"Memory-intensive operations detected (avg: {avg_memory_mb:.1f}MB). Consider memory pooling and object reuse.")
        
        # Throughput recommendations
        throughput_analysis = analysis.get('throughput_bottlenecks', {})
        for op_key, throughput_info in throughput_analysis.items():
            if throughput_info.get('bottleneck_severity') == 'high':
                efficiency = throughput_info.get('efficiency_ratio', 0) * 100
                recommendations.append(f"Operation {op_key} has low throughput efficiency ({efficiency:.1f}%). Consider batch processing or pipeline optimization.")
        
        return recommendations

# ============================================================================
# Auto-Tuning System
# ============================================================================

class AutoTuner:
    """Automatic performance tuning system."""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.monitor = performance_monitor
        self._tuning_parameters = {}
        self._tuning_history = []
        self._lock = threading.Lock()
        
        # Initialize default tuning parameters
        self._initialize_default_parameters()
        
        # Tuning state
        self._is_tuning = False
        self._last_tuning_time = time.time()
        self._tuning_interval = 300  # 5 minutes
        
        logger.info("Auto-tuner initialized")
    
    def _initialize_default_parameters(self):
        """Initialize default tuning parameters."""
        default_params = [
            TuningParameter(
                name='batch_size',
                current_value=50,
                min_value=1,
                max_value=1000,
                step_size=10,
                parameter_type='int',
                impact_weight=0.8
            ),
            TuningParameter(
                name='memory_pool_size',
                current_value=100,
                min_value=10,
                max_value=1000,
                step_size=20,
                parameter_type='int',
                impact_weight=0.6
            ),
            TuningParameter(
                name='thread_pool_size',
                current_value=multiprocessing.cpu_count() * 2,
                min_value=1,
                max_value=multiprocessing.cpu_count() * 4,
                step_size=1,
                parameter_type='int',
                impact_weight=0.7
            ),
            TuningParameter(
                name='cache_size',
                current_value=10000,
                min_value=1000,
                max_value=100000,
                step_size=1000,
                parameter_type='int',
                impact_weight=0.5
            ),
            TuningParameter(
                name='enable_simd',
                current_value=True,
                min_value=False,
                max_value=True,
                step_size=None,
                parameter_type='bool',
                impact_weight=0.9
            )
        ]
        
        with self._lock:
            for param in default_params:
                self._tuning_parameters[param.name] = param
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current tuning parameter values."""
        with self._lock:
            return {name: param.current_value for name, param in self._tuning_parameters.items()}
    
    def suggest_parameter_adjustment(self, target_metric: str = 'avg_duration_ms') -> Dict[str, Any]:
        """Suggest parameter adjustments based on current performance."""
        performance_profiles = self.monitor.get_performance_profiles()
        
        if not performance_profiles:
            return {'error': 'No performance data available for tuning'}
        
        # Calculate current performance score
        current_score = self._calculate_performance_score(performance_profiles, target_metric)
        
        suggestions = []
        
        with self._lock:
            for param_name, param in self._tuning_parameters.items():
                # Skip boolean parameters for gradient-based suggestions
                if param.parameter_type == 'bool':
                    continue
                
                # Try increasing parameter
                test_increase = min(param.max_value, param.current_value + param.step_size)
                increase_benefit = self._estimate_parameter_impact(param_name, test_increase, current_score)
                
                # Try decreasing parameter
                test_decrease = max(param.min_value, param.current_value - param.step_size)
                decrease_benefit = self._estimate_parameter_impact(param_name, test_decrease, current_score)
                
                # Determine best direction
                if increase_benefit > decrease_benefit and increase_benefit > 0:
                    suggestions.append({
                        'parameter': param_name,
                        'current_value': param.current_value,
                        'suggested_value': test_increase,
                        'estimated_benefit': increase_benefit,
                        'confidence': param.impact_weight
                    })
                elif decrease_benefit > 0:
                    suggestions.append({
                        'parameter': param_name,
                        'current_value': param.current_value,
                        'suggested_value': test_decrease,
                        'estimated_benefit': decrease_benefit,
                        'confidence': param.impact_weight
                    })
        
        # Sort suggestions by estimated benefit
        suggestions.sort(key=lambda x: x['estimated_benefit'] * x['confidence'], reverse=True)
        
        return {
            'current_performance_score': current_score,
            'target_metric': target_metric,
            'suggestions': suggestions[:5],  # Top 5 suggestions
            'tuning_history_count': len(self._tuning_history)
        }
    
    def _calculate_performance_score(self, performance_profiles: Dict[str, PerformanceProfile], 
                                   target_metric: str) -> float:
        """Calculate overall performance score."""
        if not performance_profiles:
            return 0.0
        
        scores = []
        
        for profile in performance_profiles.values():
            if target_metric == 'avg_duration_ms':
                # Lower is better - convert to score where higher is better
                score = 1.0 / max(0.001, profile.avg_duration_ms)
            elif target_metric == 'throughput_ops_per_sec':
                score = profile.throughput_ops_per_sec / 1000  # Normalize to reasonable scale
            elif target_metric == 'memory_efficiency_ratio':
                score = profile.memory_efficiency_ratio
            else:
                score = 1.0 / max(0.001, profile.avg_duration_ms)  # Default to duration
            
            scores.append(score)
        
        return statistics.mean(scores) if scores else 0.0
    
    def _estimate_parameter_impact(self, param_name: str, test_value: Any, baseline_score: float) -> float:
        """Estimate the performance impact of changing a parameter."""
        # This is a simplified heuristic-based estimation
        # In a real implementation, this could use ML models or A/B testing
        
        impact_estimates = {
            'batch_size': lambda current, test: (test - current) * 0.01 if test > current else (current - test) * -0.005,
            'memory_pool_size': lambda current, test: (test - current) * 0.001,
            'thread_pool_size': lambda current, test: abs(multiprocessing.cpu_count() * 2 - test) * -0.01,
            'cache_size': lambda current, test: (test - current) * 0.0001,
        }
        
        param = self._tuning_parameters.get(param_name)
        if not param or param_name not in impact_estimates:
            return 0.0
        
        try:
            estimated_change = impact_estimates[param_name](param.current_value, test_value)
            return estimated_change * param.impact_weight
        except:
            return 0.0
    
    def apply_tuning_suggestion(self, param_name: str, new_value: Any) -> bool:
        """Apply a tuning suggestion."""
        with self._lock:
            if param_name not in self._tuning_parameters:
                logger.error(f"Unknown tuning parameter: {param_name}")
                return False
            
            param = self._tuning_parameters[param_name]
            
            # Validate new value
            if param.parameter_type == 'int':
                if not isinstance(new_value, int) or new_value < param.min_value or new_value > param.max_value:
                    logger.error(f"Invalid value for parameter {param_name}: {new_value}")
                    return False
            elif param.parameter_type == 'float':
                if not isinstance(new_value, (int, float)) or new_value < param.min_value or new_value > param.max_value:
                    logger.error(f"Invalid value for parameter {param_name}: {new_value}")
                    return False
            elif param.parameter_type == 'bool':
                if not isinstance(new_value, bool):
                    logger.error(f"Invalid value for parameter {param_name}: {new_value}")
                    return False
            
            # Record the change
            old_value = param.current_value
            param.current_value = new_value
            param.last_changed = time.time()
            
            # Add to tuning history
            self._tuning_history.append({
                'timestamp': time.time(),
                'parameter': param_name,
                'old_value': old_value,
                'new_value': new_value,
                'reason': 'manual_adjustment'
            })
            
            logger.info(f"Applied tuning: {param_name} = {old_value} -> {new_value}")
            return True
    
    def auto_tune_performance(self) -> Dict[str, Any]:
        """Perform automatic performance tuning."""
        if self._is_tuning:
            return {'error': 'Auto-tuning already in progress'}
        
        if time.time() - self._last_tuning_time < self._tuning_interval:
            return {'error': f'Auto-tuning too frequent, wait {self._tuning_interval - (time.time() - self._last_tuning_time):.0f}s'}
        
        self._is_tuning = True
        self._last_tuning_time = time.time()
        
        try:
            # Get tuning suggestions
            suggestions = self.suggest_parameter_adjustment()
            
            if 'error' in suggestions:
                return suggestions
            
            # Apply top suggestion if it has good confidence
            applied_changes = []
            
            for suggestion in suggestions.get('suggestions', [])[:2]:  # Apply top 2
                if suggestion['confidence'] > 0.6 and suggestion['estimated_benefit'] > 0.01:
                    success = self.apply_tuning_suggestion(
                        suggestion['parameter'], 
                        suggestion['suggested_value']
                    )
                    
                    if success:
                        applied_changes.append(suggestion)
            
            # Record auto-tuning session
            tuning_session = {
                'timestamp': time.time(),
                'suggestions_considered': len(suggestions.get('suggestions', [])),
                'changes_applied': len(applied_changes),
                'applied_changes': applied_changes,
                'baseline_score': suggestions.get('current_performance_score', 0)
            }
            
            self._tuning_history.append(tuning_session)
            
            return {
                'status': 'completed',
                'session': tuning_session,
                'next_tuning_time': time.time() + self._tuning_interval
            }
            
        finally:
            self._is_tuning = False
    
    def get_tuning_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent tuning history."""
        with self._lock:
            return self._tuning_history[-limit:] if self._tuning_history else []
    
    def reset_to_defaults(self):
        """Reset all parameters to their default values."""
        with self._lock:
            self._initialize_default_parameters()
            self._tuning_history.append({
                'timestamp': time.time(),
                'action': 'reset_to_defaults',
                'reason': 'manual_reset'
            })
        
        logger.info("Tuning parameters reset to defaults")

# ============================================================================
# Global Performance Infrastructure
# ============================================================================

# Global performance monitor instance
_global_performance_monitor = None

def get_global_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _global_performance_monitor
    
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    
    return _global_performance_monitor

def shutdown_performance_monitoring():
    """Shutdown global performance monitoring."""
    global _global_performance_monitor
    
    if _global_performance_monitor:
        _global_performance_monitor.shutdown()
        _global_performance_monitor = None
        
    logger.info("Global performance monitoring shutdown complete")