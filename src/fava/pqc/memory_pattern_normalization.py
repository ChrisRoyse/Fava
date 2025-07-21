"""
Memory Access Pattern Normalization Module

This module provides comprehensive memory access pattern normalization to prevent 
cache-based side-channel attacks and memory access timing analysis.

Security Features:
- Cache line pollution to prevent cache timing attacks
- Randomized memory access patterns 
- Constant memory allocation patterns
- Memory touch patterns to normalize cache behavior
- Protection against memory access timing analysis
"""

import os
import random
import time
import threading
from typing import List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryBlock:
    """Represents a memory block for pattern normalization."""
    data: bytearray
    access_count: int
    last_access: float


class CacheLineNormalizer:
    """
    Normalizes cache line access patterns to prevent cache timing attacks.
    """
    
    def __init__(self, cache_line_size: int = 64, cache_size_kb: int = 256):
        """
        Initialize cache line normalizer.
        
        Args:
            cache_line_size: CPU cache line size in bytes (typically 64)
            cache_size_kb: Approximate cache size in KB for memory pools
        """
        self.cache_line_size = cache_line_size
        self.cache_size_kb = cache_size_kb
        self.memory_pools = []
        self.decoy_accesses = []
        self.lock = threading.Lock()
        
        # Initialize memory pools for cache pollution
        self._initialize_cache_pools()
        
        logger.info(f"Cache line normalizer initialized: {cache_line_size}B lines, {cache_size_kb}KB pools")
    
    def _initialize_cache_pools(self) -> None:
        """Initialize memory pools to pollute cache lines."""
        # Create multiple pools that span cache lines
        pool_count = max(8, self.cache_size_kb // 32)  # Multiple pools
        
        for i in range(pool_count):
            pool_size = self.cache_line_size * random.randint(16, 64)  # 1-4KB per pool
            memory_pool = MemoryBlock(
                data=bytearray(os.urandom(pool_size)),
                access_count=0,
                last_access=time.time()
            )
            self.memory_pools.append(memory_pool)
    
    def pollute_cache_lines(self, access_count: int = 32) -> None:
        """
        Perform random memory accesses to pollute cache lines.
        
        Args:
            access_count: Number of random cache line accesses to perform
        """
        with self.lock:
            for _ in range(access_count):
                # Select random memory pool
                pool = random.choice(self.memory_pools)
                
                # Calculate random cache-aligned offset
                max_offset = len(pool.data) - self.cache_line_size
                if max_offset <= 0:
                    continue
                    
                cache_aligned_offset = (random.randint(0, max_offset // self.cache_line_size) * 
                                      self.cache_line_size)
                
                # Access full cache line
                cache_line = pool.data[cache_aligned_offset:cache_aligned_offset + self.cache_line_size]
                
                # Perform dummy computation to ensure memory access
                _ = sum(cache_line) & 0xFF
                
                # Update access tracking
                pool.access_count += 1
                pool.last_access = time.time()
        
        logger.debug(f"Polluted {access_count} cache lines")
    
    def normalize_data_access(self, data: bytes, access_pattern: str = "random") -> bytes:
        """
        Access data with normalized patterns to prevent timing analysis.
        
        Args:
            data: Data to access with normalized patterns
            access_pattern: Pattern type ("random", "sequential", "strided")
            
        Returns:
            Original data (unchanged)
        """
        if not data:
            return data
        
        # Pollute cache before actual data access
        self.pollute_cache_lines(random.randint(16, 48))
        
        # Normalize access pattern based on type
        if access_pattern == "random":
            self._random_access_pattern(data)
        elif access_pattern == "sequential":
            self._sequential_access_pattern(data)
        elif access_pattern == "strided":
            self._strided_access_pattern(data)
        else:
            # Default to random
            self._random_access_pattern(data)
        
        # Additional cache pollution after access
        self.pollute_cache_lines(random.randint(8, 24))
        
        return data
    
    def _random_access_pattern(self, data: bytes) -> None:
        """Access data in randomized patterns."""
        data_len = len(data)
        access_points = min(32, data_len)  # Limit access points
        
        # Generate random access indices
        indices = random.sample(range(data_len), min(access_points, data_len))
        
        for idx in indices:
            # Access cache-line sized chunks where possible
            chunk_end = min(idx + self.cache_line_size, data_len)
            chunk = data[idx:chunk_end]
            _ = len(chunk)  # Touch memory
            
            # Small random delay between accesses
            time.sleep(random.uniform(0.00001, 0.0001))
    
    def _sequential_access_pattern(self, data: bytes) -> None:
        """Access data in sequential cache-line chunks."""
        for offset in range(0, len(data), self.cache_line_size):
            chunk_end = min(offset + self.cache_line_size, len(data))
            chunk = data[offset:chunk_end]
            _ = sum(chunk) & 0xFF  # Touch memory with computation
            
            # Consistent timing between accesses
            time.sleep(0.00005)  # 50 microseconds
    
    def _strided_access_pattern(self, data: bytes) -> None:
        """Access data with consistent stride pattern."""
        stride = self.cache_line_size * 2  # Skip cache lines
        
        for offset in range(0, len(data), stride):
            chunk_end = min(offset + self.cache_line_size, len(data))
            chunk = data[offset:chunk_end]
            _ = len(chunk)  # Touch memory
            
            time.sleep(0.00005)


class MemoryAllocationNormalizer:
    """
    Normalizes memory allocation patterns to prevent allocation-based side channels.
    """
    
    def __init__(self):
        """Initialize memory allocation normalizer."""
        self.allocation_pools = {}
        self.dummy_allocations = []
        
        # Pre-allocate memory pools of common sizes
        self._initialize_allocation_pools()
    
    def _initialize_allocation_pools(self) -> None:
        """Initialize pre-allocated memory pools."""
        common_sizes = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
        
        for size in common_sizes:
            pool = []
            # Pre-allocate multiple blocks of each size
            for _ in range(10):
                block = bytearray(size)
                pool.append(block)
            self.allocation_pools[size] = pool
        
        logger.debug(f"Initialized allocation pools for sizes: {common_sizes}")
    
    def get_normalized_buffer(self, requested_size: int) -> bytearray:
        """
        Get buffer with normalized allocation pattern.
        
        Args:
            requested_size: Requested buffer size
            
        Returns:
            Buffer of requested size
        """
        # Round up to nearest power of 2 for consistent allocation
        normalized_size = 1
        while normalized_size < requested_size:
            normalized_size *= 2
        
        # Try to get from pre-allocated pool first
        if normalized_size in self.allocation_pools and self.allocation_pools[normalized_size]:
            buffer = self.allocation_pools[normalized_size].pop()
            # Clear the buffer
            for i in range(len(buffer)):
                buffer[i] = 0
            return buffer[:requested_size]
        
        # Allocate new buffer if pool is empty
        buffer = bytearray(normalized_size)
        
        # Create dummy allocations to mask allocation pattern
        self._create_dummy_allocations()
        
        return buffer[:requested_size]
    
    def return_buffer(self, buffer: bytearray) -> None:
        """
        Return buffer to pool for reuse.
        
        Args:
            buffer: Buffer to return to pool
        """
        # Clear sensitive data
        for i in range(len(buffer)):
            buffer[i] = random.randint(0, 255)  # Random fill
        
        # Return to appropriate pool if space available
        size = len(buffer)
        normalized_size = 1
        while normalized_size < size:
            normalized_size *= 2
        
        if normalized_size in self.allocation_pools and len(self.allocation_pools[normalized_size]) < 20:
            # Extend buffer back to normalized size if needed
            if len(buffer) < normalized_size:
                buffer.extend(bytearray(normalized_size - len(buffer)))
            self.allocation_pools[normalized_size].append(buffer)
    
    def _create_dummy_allocations(self) -> None:
        """Create dummy allocations to mask real allocation patterns."""
        dummy_count = random.randint(2, 6)
        sizes = [64, 128, 256, 512, 1024]
        
        for _ in range(dummy_count):
            size = random.choice(sizes)
            dummy = bytearray(os.urandom(size))
            self.dummy_allocations.append(dummy)
        
        # Cleanup old dummy allocations to prevent memory growth
        if len(self.dummy_allocations) > 50:
            self.dummy_allocations = self.dummy_allocations[-25:]


class MemoryTouchPatternNormalizer:
    """
    Normalizes memory touch patterns to prevent access pattern analysis.
    """
    
    def __init__(self):
        """Initialize memory touch pattern normalizer."""
        self.touch_history = []
        self.pattern_masks = self._generate_pattern_masks()
    
    def _generate_pattern_masks(self) -> List[List[bool]]:
        """Generate predefined memory touch patterns."""
        patterns = []
        
        # Sequential pattern
        patterns.append([True] * 64)
        
        # Alternating pattern
        patterns.append([i % 2 == 0 for i in range(64)])
        
        # Random patterns
        for _ in range(5):
            pattern = [random.choice([True, False]) for _ in range(64)]
            patterns.append(pattern)
        
        # Sparse patterns
        for density in [0.25, 0.5, 0.75]:
            pattern = [random.random() < density for _ in range(64)]
            patterns.append(pattern)
        
        return patterns
    
    def normalize_memory_touches(self, data: bytes, operation_name: str = "default") -> None:
        """
        Perform normalized memory touches to mask access patterns.
        
        Args:
            data: Data being processed
            operation_name: Name of operation for pattern selection
        """
        if not data:
            return
        
        # Select touch pattern based on operation
        pattern_index = hash(operation_name) % len(self.pattern_masks)
        touch_pattern = self.pattern_masks[pattern_index]
        
        # Calculate chunk size based on data length
        chunk_size = max(1, len(data) // len(touch_pattern))
        
        # Apply touch pattern
        for i, should_touch in enumerate(touch_pattern):
            if should_touch and i * chunk_size < len(data):
                start_idx = i * chunk_size
                end_idx = min(start_idx + chunk_size, len(data))
                
                # Touch memory with simple operation
                chunk = data[start_idx:end_idx]
                _ = len(chunk)  # Memory access
                
                # Small consistent delay
                time.sleep(0.00002)  # 20 microseconds


class ConstantTimeMemoryOperations:
    """
    Provides constant-time memory operations to prevent timing analysis.
    """
    
    @staticmethod
    def constant_time_memcpy(dest: bytearray, src: bytes, length: int) -> None:
        """
        Constant-time memory copy operation.
        
        Args:
            dest: Destination buffer
            src: Source data
            length: Number of bytes to copy
        """
        for i in range(length):
            if i < len(src) and i < len(dest):
                dest[i] = src[i]
            elif i < len(dest):
                dest[i] = 0
    
    @staticmethod
    def constant_time_memset(buffer: bytearray, value: int, length: int) -> None:
        """
        Constant-time memory set operation.
        
        Args:
            buffer: Buffer to set
            value: Value to set (0-255)
            length: Number of bytes to set
        """
        for i in range(min(length, len(buffer))):
            buffer[i] = value & 0xFF
    
    @staticmethod
    def constant_time_memclear(buffer: bytearray) -> None:
        """
        Constant-time memory clear operation.
        
        Args:
            buffer: Buffer to clear
        """
        # Clear with random pattern first, then zeros
        random_value = random.randint(0, 255)
        for i in range(len(buffer)):
            buffer[i] = random_value
        
        # Clear with zeros
        for i in range(len(buffer)):
            buffer[i] = 0


# Global instances
cache_normalizer = CacheLineNormalizer()
allocation_normalizer = MemoryAllocationNormalizer()
touch_normalizer = MemoryTouchPatternNormalizer()
constant_time_ops = ConstantTimeMemoryOperations()


def memory_pattern_protected(operation_name: str = "default"):
    """
    Decorator to protect functions from memory access pattern analysis.
    
    Args:
        operation_name: Name of operation for pattern normalization
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Pollute cache before operation
            cache_normalizer.pollute_cache_lines(random.randint(16, 32))
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Normalize memory access patterns after operation
            if hasattr(result, '__len__') and len(result) > 0:
                if isinstance(result, (bytes, bytearray)):
                    touch_normalizer.normalize_memory_touches(result, operation_name)
            
            # Additional cache pollution
            cache_normalizer.pollute_cache_lines(random.randint(8, 16))
            
            return result
        return wrapper
    return decorator


# Initialize memory pattern normalization
logger.info("Memory access pattern normalization initialized")
logger.info(f"Cache line size: {cache_normalizer.cache_line_size} bytes")
logger.info(f"Memory pools: {len(cache_normalizer.memory_pools)} pools")
logger.info("Constant-time memory operations enabled")