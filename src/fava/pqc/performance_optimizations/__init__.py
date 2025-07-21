"""
Performance Optimizations Package
================================

This package provides high-performance optimizations for post-quantum cryptography operations,
specifically targeting Kyber768 KEM operations with the goal of achieving enterprise-grade
performance requirements.

Target Performance Improvements:
- Kyber768 Encapsulation: <0.15ms (3x improvement)
- Kyber768 Decapsulation: <0.15ms (2.7x improvement)
- Memory usage reduction: 15-25%
- Concurrent throughput: 4x improvement

Key Features:
- SIMD vectorization for polynomial arithmetic
- Advanced memory pooling system
- Lock-free concurrent data structures
- Batch processing capabilities
- Performance monitoring and auto-tuning
- Compiler optimizations

Usage:
    from fava.pqc.performance_optimizations import OptimizedKyber768
    
    # Initialize optimized crypto engine
    crypto = OptimizedKyber768()
    
    # Perform optimized operations
    result = crypto.encapsulate_optimized(public_key)
    shared_secret = crypto.decapsulate_optimized(ciphertext, secret_key)
    
    # Get performance metrics
    report = crypto.get_performance_report()
"""

from .optimized_kyber768 import OptimizedKyber768, initialize_optimizations, shutdown_optimizations
from .advanced_memory_pool import AdvancedMemoryPool, SmartMemoryManager, get_smart_memory_manager
from .lock_free_structures import LockFreeQueue, LockFreeCounter, ConcurrentHashMap, get_global_crypto_cache
from .performance_monitor import PerformanceMonitor, OperationMetrics, AutoTuner, get_global_performance_monitor

__version__ = "1.0.0"

__all__ = [
    'OptimizedKyber768',
    'AdvancedMemoryPool', 
    'SmartMemoryManager',
    'get_smart_memory_manager',
    'LockFreeQueue',
    'LockFreeCounter', 
    'ConcurrentHashMap',
    'get_global_crypto_cache',
    'PerformanceMonitor',
    'OperationMetrics',
    'AutoTuner',
    'get_global_performance_monitor',
    'initialize_optimizations',
    'shutdown_optimizations'
]

# Auto-initialize optimizations on package import
initialize_optimizations()