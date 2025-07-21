"""
Advanced Memory Pool System
===========================

High-performance memory management system designed for cryptographic operations.
Provides significant performance improvements through:

- Pre-allocated memory blocks to eliminate allocation overhead
- Size-specific pools for different data types (keys, ciphertexts, secrets)
- Thread-safe operations with minimal locking
- Memory usage tracking and optimization
- Auto-scaling based on demand patterns
- Memory alignment for optimal CPU cache performance

Target Benefits:
- 15-25% memory usage reduction
- 40-60% reduction in allocation overhead
- Improved cache locality for crypto operations
- Reduced garbage collection pressure
"""

import os
import time
import logging
import threading
import multiprocessing
import weakref
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import queue
import mmap

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)

# ============================================================================
# Memory Pool Configuration and Statistics
# ============================================================================

@dataclass
class PoolStatistics:
    """Statistics for memory pool usage and performance."""
    pool_name: str
    block_size: int
    total_blocks: int
    available_blocks: int
    allocated_blocks: int
    peak_allocated: int
    total_allocations: int
    total_deallocations: int
    cache_hits: int
    cache_misses: int
    memory_saved_bytes: int
    creation_time: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class MemoryPoolConfig:
    """Configuration for memory pool behavior."""
    
    # Kyber768 specific sizes
    KYBER768_PUBLIC_KEY_SIZE = 1184
    KYBER768_SECRET_KEY_SIZE = 2400
    KYBER768_CIPHERTEXT_SIZE = 1088
    KYBER768_SHARED_SECRET_SIZE = 32
    
    # X25519 specific sizes
    X25519_KEY_SIZE = 32
    
    # Common buffer sizes
    SMALL_BUFFER_SIZE = 64
    MEDIUM_BUFFER_SIZE = 256
    LARGE_BUFFER_SIZE = 1024
    
    # Pool configuration
    DEFAULT_INITIAL_BLOCKS = 20
    DEFAULT_MAX_BLOCKS = 200
    DEFAULT_GROWTH_FACTOR = 1.5
    DEFAULT_SHRINK_THRESHOLD = 0.25
    
    # Performance tuning
    CACHE_LINE_SIZE = 64  # CPU cache line size for alignment
    PAGE_SIZE = 4096      # Memory page size
    
    @classmethod
    def get_optimal_pool_config(cls) -> Dict[str, Dict[str, Any]]:
        """Get optimized pool configuration for crypto operations."""
        return {
            'kyber768_public_keys': {
                'block_size': cls.KYBER768_PUBLIC_KEY_SIZE,
                'initial_blocks': 30,
                'max_blocks': 300,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'kyber768_secret_keys': {
                'block_size': cls.KYBER768_SECRET_KEY_SIZE,
                'initial_blocks': 30,
                'max_blocks': 300,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'kyber768_ciphertexts': {
                'block_size': cls.KYBER768_CIPHERTEXT_SIZE,
                'initial_blocks': 50,
                'max_blocks': 500,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'shared_secrets': {
                'block_size': cls.KYBER768_SHARED_SECRET_SIZE,
                'initial_blocks': 100,
                'max_blocks': 1000,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'x25519_keys': {
                'block_size': cls.X25519_KEY_SIZE,
                'initial_blocks': 50,
                'max_blocks': 500,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'small_buffers': {
                'block_size': cls.SMALL_BUFFER_SIZE,
                'initial_blocks': 100,
                'max_blocks': 1000,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'medium_buffers': {
                'block_size': cls.MEDIUM_BUFFER_SIZE,
                'initial_blocks': 50,
                'max_blocks': 500,
                'align_size': cls.CACHE_LINE_SIZE
            },
            'large_buffers': {
                'block_size': cls.LARGE_BUFFER_SIZE,
                'initial_blocks': 20,
                'max_blocks': 200,
                'align_size': cls.CACHE_LINE_SIZE
            }
        }

# ============================================================================
# Advanced Memory Block Management
# ============================================================================

class AlignedMemoryBlock:
    """Memory block with optimal CPU cache alignment."""
    
    def __init__(self, size: int, align_size: int = 64):
        self.size = size
        self.align_size = align_size
        self._raw_memory = None
        self._aligned_memory = None
        self._is_zeroed = True
        self._last_used = time.time()
        
        self._allocate_aligned_memory()
    
    def _allocate_aligned_memory(self):
        """Allocate cache-aligned memory block."""
        if HAS_NUMPY:
            # Use numpy for aligned memory allocation
            self._raw_memory = np.zeros(self.size + self.align_size, dtype=np.uint8)
            
            # Calculate aligned offset
            raw_addr = self._raw_memory.ctypes.data
            aligned_addr = (raw_addr + self.align_size - 1) & ~(self.align_size - 1)
            offset = aligned_addr - raw_addr
            
            self._aligned_memory = self._raw_memory[offset:offset + self.size]
        else:
            # Fallback to regular bytearray
            self._raw_memory = bytearray(self.size + self.align_size)
            
            # Simple alignment (not truly aligned but better than nothing)
            self._aligned_memory = memoryview(self._raw_memory)[self.align_size:self.align_size + self.size]
    
    def get_memory(self) -> Union[np.ndarray, memoryview]:
        """Get the aligned memory block."""
        self._last_used = time.time()
        return self._aligned_memory
    
    def zero_memory(self):
        """Zero out the memory block."""
        if HAS_NUMPY and isinstance(self._aligned_memory, np.ndarray):
            self._aligned_memory.fill(0)
        else:
            for i in range(len(self._aligned_memory)):
                self._aligned_memory[i] = 0
        self._is_zeroed = True
    
    def is_zeroed(self) -> bool:
        """Check if memory block is zeroed."""
        return self._is_zeroed
    
    def mark_dirty(self):
        """Mark memory block as containing data."""
        self._is_zeroed = False
    
    def get_last_used(self) -> float:
        """Get timestamp of last usage."""
        return self._last_used

# ============================================================================
# High-Performance Memory Pool
# ============================================================================

class AdvancedMemoryPool:
    """Advanced memory pool with performance optimizations."""
    
    def __init__(self, 
                 pool_name: str,
                 block_size: int,
                 initial_blocks: int = 20,
                 max_blocks: int = 200,
                 align_size: int = 64,
                 auto_scale: bool = True,
                 enable_statistics: bool = True):
        
        self.pool_name = pool_name
        self.block_size = block_size
        self.initial_blocks = initial_blocks
        self.max_blocks = max_blocks
        self.align_size = align_size
        self.auto_scale = auto_scale
        self.enable_statistics = enable_statistics
        
        # Thread-safe block storage
        self._available_blocks = queue.LifoQueue()  # LIFO for better cache locality
        self._allocated_blocks = weakref.WeakSet()
        
        # Statistics tracking
        self._stats = PoolStatistics(
            pool_name=pool_name,
            block_size=block_size,
            total_blocks=0,
            available_blocks=0,
            allocated_blocks=0,
            peak_allocated=0,
            total_allocations=0,
            total_deallocations=0,
            cache_hits=0,
            cache_misses=0,
            memory_saved_bytes=0
        )
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Auto-scaling parameters
        self._last_scale_check = time.time()
        self._scale_check_interval = 10.0  # seconds
        self._usage_history = []
        
        # Initialize pool
        self._initialize_pool()
        
        logger.info(f"Created advanced memory pool '{pool_name}': "
                   f"block_size={block_size}, initial_blocks={initial_blocks}, "
                   f"max_blocks={max_blocks}, aligned={align_size}")
    
    def _initialize_pool(self):
        """Initialize the memory pool with initial blocks."""
        for _ in range(self.initial_blocks):
            block = AlignedMemoryBlock(self.block_size, self.align_size)
            self._available_blocks.put(block)
            
        with self._lock:
            self._stats.total_blocks = self.initial_blocks
            self._stats.available_blocks = self.initial_blocks
    
    def get_block(self, timeout: float = None) -> AlignedMemoryBlock:
        """Get a memory block from the pool."""
        start_time = time.perf_counter()
        
        try:
            # Try to get an available block
            if timeout is None:
                block = self._available_blocks.get_nowait()
                cache_hit = True
            else:
                block = self._available_blocks.get(timeout=timeout)
                cache_hit = True
                
        except queue.Empty:
            # No available blocks, create new one if under limit
            with self._lock:
                if self._stats.total_blocks < self.max_blocks:
                    block = AlignedMemoryBlock(self.block_size, self.align_size)
                    self._stats.total_blocks += 1
                    cache_hit = False
                else:
                    # Pool exhausted, wait for a block or create temporary
                    if timeout and timeout > 0:
                        try:
                            block = self._available_blocks.get(timeout=timeout)
                            cache_hit = True
                        except queue.Empty:
                            # Create temporary block (not managed by pool)
                            logger.warning(f"Pool '{self.pool_name}' exhausted, creating temporary block")
                            block = AlignedMemoryBlock(self.block_size, self.align_size)
                            cache_hit = False
                    else:
                        # Create temporary block immediately
                        block = AlignedMemoryBlock(self.block_size, self.align_size)
                        cache_hit = False
        
        # Update statistics
        if self.enable_statistics:
            with self._lock:
                self._stats.total_allocations += 1
                self._stats.allocated_blocks += 1
                self._stats.peak_allocated = max(self._stats.peak_allocated, self._stats.allocated_blocks)
                self._stats.available_blocks = max(0, self._stats.available_blocks - 1)
                
                if cache_hit:
                    self._stats.cache_hits += 1
                else:
                    self._stats.cache_misses += 1
                
                # Estimate memory savings (vs individual allocations)
                allocation_overhead = 32  # Estimated overhead per malloc
                self._stats.memory_saved_bytes += allocation_overhead
                
                self._stats.last_updated = time.time()
        
        # Ensure block is clean
        if not block.is_zeroed():
            block.zero_memory()
        
        # Track allocated block
        self._allocated_blocks.add(block)
        
        # Log performance for very slow allocations
        allocation_time = time.perf_counter() - start_time
        if allocation_time > 0.001:  # >1ms is concerning
            logger.warning(f"Slow memory allocation in pool '{self.pool_name}': {allocation_time*1000:.2f}ms")
        
        return block
    
    def return_block(self, block: AlignedMemoryBlock):
        """Return a memory block to the pool."""
        if block is None:
            return
        
        # Remove from allocated tracking
        self._allocated_blocks.discard(block)
        
        # Clean the block
        block.zero_memory()
        
        # Return to pool if there's space
        try:
            self._available_blocks.put_nowait(block)
            
            # Update statistics
            if self.enable_statistics:
                with self._lock:
                    self._stats.total_deallocations += 1
                    self._stats.allocated_blocks = max(0, self._stats.allocated_blocks - 1)
                    self._stats.available_blocks += 1
                    self._stats.last_updated = time.time()
                    
        except queue.Full:
            # Pool is full, let block be garbage collected
            with self._lock:
                if self._stats.total_blocks > 0:
                    self._stats.total_blocks -= 1
    
    @contextmanager
    def get_temporary_block(self, timeout: float = None):
        """Context manager for temporary block usage."""
        block = self.get_block(timeout=timeout)
        try:
            yield block
        finally:
            self.return_block(block)
    
    def get_statistics(self) -> PoolStatistics:
        """Get current pool statistics."""
        with self._lock:
            # Update current counts
            self._stats.available_blocks = self._available_blocks.qsize()
            return self._stats
    
    def auto_scale_check(self):
        """Check if pool should be scaled based on usage patterns."""
        if not self.auto_scale:
            return
            
        current_time = time.time()
        if current_time - self._last_scale_check < self._scale_check_interval:
            return
            
        with self._lock:
            usage_ratio = self._stats.allocated_blocks / max(1, self._stats.total_blocks)
            self._usage_history.append(usage_ratio)
            
            # Keep only recent history
            if len(self._usage_history) > 10:
                self._usage_history = self._usage_history[-10:]
            
            avg_usage = sum(self._usage_history) / len(self._usage_history)
            
            # Scale up if consistently high usage
            if avg_usage > 0.8 and self._stats.total_blocks < self.max_blocks:
                new_blocks = min(10, self.max_blocks - self._stats.total_blocks)
                for _ in range(new_blocks):
                    block = AlignedMemoryBlock(self.block_size, self.align_size)
                    self._available_blocks.put(block)
                    self._stats.total_blocks += 1
                    self._stats.available_blocks += 1
                
                logger.info(f"Auto-scaled pool '{self.pool_name}' up by {new_blocks} blocks "
                          f"(usage: {avg_usage:.1%})")
            
            # Scale down if consistently low usage
            elif avg_usage < 0.2 and self._stats.available_blocks > self.initial_blocks:
                blocks_to_remove = min(5, self._stats.available_blocks - self.initial_blocks)
                for _ in range(blocks_to_remove):
                    try:
                        block = self._available_blocks.get_nowait()
                        self._stats.total_blocks -= 1
                        self._stats.available_blocks -= 1
                    except queue.Empty:
                        break
                
                if blocks_to_remove > 0:
                    logger.info(f"Auto-scaled pool '{self.pool_name}' down by {blocks_to_remove} blocks "
                              f"(usage: {avg_usage:.1%})")
            
            self._last_scale_check = current_time
    
    def optimize_for_pattern(self, operation_pattern: Dict[str, Any]):
        """Optimize pool configuration based on usage patterns."""
        if not operation_pattern:
            return
            
        # Analyze request rate and adjust pool size
        requests_per_second = operation_pattern.get('requests_per_second', 0)
        if requests_per_second > 1000:  # High throughput scenario
            target_blocks = min(self.max_blocks, int(requests_per_second / 100))
            
            with self._lock:
                current_blocks = self._stats.total_blocks
                if target_blocks > current_blocks:
                    blocks_to_add = target_blocks - current_blocks
                    for _ in range(blocks_to_add):
                        if self._stats.total_blocks < self.max_blocks:
                            block = AlignedMemoryBlock(self.block_size, self.align_size)
                            self._available_blocks.put(block)
                            self._stats.total_blocks += 1
                            self._stats.available_blocks += 1
                    
                    logger.info(f"Optimized pool '{self.pool_name}' for high throughput: "
                              f"added {blocks_to_add} blocks for {requests_per_second} req/s")
    
    def clear_pool(self):
        """Clear all blocks from the pool."""
        with self._lock:
            # Empty the queue
            while not self._available_blocks.empty():
                try:
                    self._available_blocks.get_nowait()
                except queue.Empty:
                    break
            
            # Reset statistics
            self._stats.total_blocks = 0
            self._stats.available_blocks = 0
            self._stats.allocated_blocks = 0
            
            logger.info(f"Cleared memory pool '{self.pool_name}'")

# ============================================================================
# Smart Memory Manager
# ============================================================================

class SmartMemoryManager:
    """Intelligent memory manager for crypto operations."""
    
    def __init__(self, enable_auto_tuning: bool = True):
        self.enable_auto_tuning = enable_auto_tuning
        self._pools = {}
        self._global_stats = {
            'total_memory_managed': 0,
            'total_allocations': 0,
            'total_memory_saved': 0,
            'initialization_time': time.time()
        }
        
        # Create optimized pools
        self._create_optimized_pools()
        
        # Auto-tuning thread
        self._tuning_thread = None
        self._stop_tuning = threading.Event()
        
        if enable_auto_tuning:
            self._start_auto_tuning()
    
    def _create_optimized_pools(self):
        """Create memory pools with optimized configurations."""
        configs = MemoryPoolConfig.get_optimal_pool_config()
        
        for pool_name, config in configs.items():
            pool = AdvancedMemoryPool(
                pool_name=pool_name,
                block_size=config['block_size'],
                initial_blocks=config['initial_blocks'],
                max_blocks=config['max_blocks'],
                align_size=config['align_size'],
                auto_scale=True,
                enable_statistics=True
            )
            
            self._pools[pool_name] = pool
            self._global_stats['total_memory_managed'] += (
                config['block_size'] * config['initial_blocks']
            )
        
        logger.info(f"Smart memory manager initialized with {len(self._pools)} pools, "
                   f"managing {self._global_stats['total_memory_managed']} bytes")
    
    def get_pool(self, pool_name: str) -> Optional[AdvancedMemoryPool]:
        """Get a memory pool by name."""
        return self._pools.get(pool_name)
    
    def get_kyber768_public_key_block(self) -> AlignedMemoryBlock:
        """Get a block for Kyber768 public key."""
        return self._pools['kyber768_public_keys'].get_block()
    
    def get_kyber768_secret_key_block(self) -> AlignedMemoryBlock:
        """Get a block for Kyber768 secret key."""
        return self._pools['kyber768_secret_keys'].get_block()
    
    def get_kyber768_ciphertext_block(self) -> AlignedMemoryBlock:
        """Get a block for Kyber768 ciphertext."""
        return self._pools['kyber768_ciphertexts'].get_block()
    
    def get_shared_secret_block(self) -> AlignedMemoryBlock:
        """Get a block for shared secret."""
        return self._pools['shared_secrets'].get_block()
    
    @contextmanager
    def get_kyber768_workspace(self):
        """Context manager providing complete Kyber768 workspace."""
        public_key_block = self.get_kyber768_public_key_block()
        secret_key_block = self.get_kyber768_secret_key_block()
        ciphertext_block = self.get_kyber768_ciphertext_block()
        shared_secret_block = self.get_shared_secret_block()
        
        try:
            yield {
                'public_key': public_key_block,
                'secret_key': secret_key_block,
                'ciphertext': ciphertext_block,
                'shared_secret': shared_secret_block
            }
        finally:
            # Return all blocks
            self._pools['kyber768_public_keys'].return_block(public_key_block)
            self._pools['kyber768_secret_keys'].return_block(secret_key_block)
            self._pools['kyber768_ciphertexts'].return_block(ciphertext_block)
            self._pools['shared_secrets'].return_block(shared_secret_block)
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all pools."""
        pool_stats = {}
        
        for pool_name, pool in self._pools.items():
            pool_stats[pool_name] = pool.get_statistics().__dict__
        
        # Calculate global statistics
        total_blocks = sum(stats['total_blocks'] for stats in pool_stats.values())
        total_allocated = sum(stats['allocated_blocks'] for stats in pool_stats.values())
        total_memory_managed = sum(
            stats['total_blocks'] * stats['block_size'] 
            for stats in pool_stats.values()
        )
        total_memory_saved = sum(stats['memory_saved_bytes'] for stats in pool_stats.values())
        
        return {
            'global_stats': {
                'total_pools': len(self._pools),
                'total_blocks': total_blocks,
                'total_allocated_blocks': total_allocated,
                'total_memory_managed_bytes': total_memory_managed,
                'total_memory_managed_mb': total_memory_managed / 1024 / 1024,
                'total_memory_saved_bytes': total_memory_saved,
                'memory_efficiency': (total_memory_saved / max(1, total_memory_managed)) * 100,
                'average_utilization': (total_allocated / max(1, total_blocks)) * 100,
                'uptime_seconds': time.time() - self._global_stats['initialization_time']
            },
            'pool_stats': pool_stats,
            'optimization_recommendations': self._get_optimization_recommendations(pool_stats)
        }
    
    def _get_optimization_recommendations(self, pool_stats: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on usage patterns."""
        recommendations = []
        
        for pool_name, stats in pool_stats.items():
            utilization = (stats['allocated_blocks'] / max(1, stats['total_blocks'])) * 100
            
            if utilization > 90:
                recommendations.append(f"Pool '{pool_name}' is heavily utilized ({utilization:.1f}%) - consider increasing max_blocks")
            elif utilization < 10:
                recommendations.append(f"Pool '{pool_name}' is underutilized ({utilization:.1f}%) - consider reducing initial_blocks")
            
            hit_rate = (stats['cache_hits'] / max(1, stats['cache_hits'] + stats['cache_misses'])) * 100
            if hit_rate < 80:
                recommendations.append(f"Pool '{pool_name}' has low cache hit rate ({hit_rate:.1f}%) - consider increasing pool size")
        
        return recommendations
    
    def _start_auto_tuning(self):
        """Start the auto-tuning thread."""
        if self._tuning_thread is None:
            self._stop_tuning.clear()
            self._tuning_thread = threading.Thread(target=self._auto_tuning_loop, daemon=True)
            self._tuning_thread.start()
            logger.info("Started memory manager auto-tuning")
    
    def _auto_tuning_loop(self):
        """Main auto-tuning loop."""
        while not self._stop_tuning.wait(30):  # Check every 30 seconds
            try:
                # Run auto-scale check on all pools
                for pool in self._pools.values():
                    pool.auto_scale_check()
                
                # Log periodic statistics
                if time.time() % 300 < 30:  # Every 5 minutes
                    stats = self.get_comprehensive_statistics()
                    logger.info(f"Memory manager stats: "
                              f"{stats['global_stats']['total_memory_managed_mb']:.1f}MB managed, "
                              f"{stats['global_stats']['average_utilization']:.1f}% utilization, "
                              f"{stats['global_stats']['memory_efficiency']:.1f}% efficiency")
                
            except Exception as e:
                logger.error(f"Auto-tuning error: {e}")
    
    def optimize_for_workload(self, workload_profile: Dict[str, Any]):
        """Optimize memory pools for a specific workload profile."""
        logger.info(f"Optimizing memory manager for workload: {workload_profile}")
        
        # Extract workload characteristics
        kyber_ops_per_sec = workload_profile.get('kyber768_ops_per_second', 0)
        concurrent_ops = workload_profile.get('max_concurrent_operations', 1)
        memory_pressure = workload_profile.get('memory_pressure_level', 'normal')  # low, normal, high
        
        # Adjust pool sizes based on workload
        if kyber_ops_per_sec > 5000:  # High throughput
            # Increase pool sizes for high throughput scenarios
            for pool_name in ['kyber768_ciphertexts', 'shared_secrets']:
                pool = self._pools.get(pool_name)
                if pool:
                    operation_pattern = {'requests_per_second': kyber_ops_per_sec}
                    pool.optimize_for_pattern(operation_pattern)
        
        if concurrent_ops > 50:  # High concurrency
            # Increase all crypto-related pools
            for pool_name in ['kyber768_public_keys', 'kyber768_secret_keys', 'kyber768_ciphertexts']:
                pool = self._pools.get(pool_name)
                if pool:
                    operation_pattern = {'requests_per_second': concurrent_ops * 10}
                    pool.optimize_for_pattern(operation_pattern)
        
        if memory_pressure == 'high':
            # Reduce pool sizes under memory pressure
            logger.info("Optimizing for high memory pressure - reducing pool sizes")
            for pool in self._pools.values():
                pool.max_blocks = max(pool.initial_blocks, pool.max_blocks // 2)
    
    def shutdown(self):
        """Shutdown the memory manager and clean up resources."""
        logger.info("Shutting down smart memory manager...")
        
        # Stop auto-tuning
        if self._tuning_thread:
            self._stop_tuning.set()
            self._tuning_thread.join(timeout=5)
            self._tuning_thread = None
        
        # Clear all pools
        for pool in self._pools.values():
            pool.clear_pool()
        
        # Log final statistics
        final_stats = self.get_comprehensive_statistics()
        logger.info(f"Memory manager shutdown complete. Final stats: "
                   f"{final_stats['global_stats']['total_memory_managed_mb']:.1f}MB managed, "
                   f"{final_stats['global_stats']['total_memory_saved_bytes']} bytes saved")

# Global smart memory manager instance
_smart_memory_manager = SmartMemoryManager()

def get_smart_memory_manager() -> SmartMemoryManager:
    """Get the global smart memory manager instance."""
    return _smart_memory_manager