"""
Advanced Caching System

This module provides a comprehensive caching solution with multiple
cache strategies, TTL support, cache warming, and performance monitoring.
"""

import asyncio
import functools
import hashlib
import json
import pickle
import time
import weakref
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import threading
import logging


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns


class CacheLevel(Enum):
    """Cache levels for hierarchical caching"""
    L1_MEMORY = "l1_memory"
    L2_DISK = "l2_disk"
    L3_DISTRIBUTED = "l3_distributed"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    tags: Set[str] = field(default_factory=set)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get age in seconds"""
        return (datetime.now() - self.created_at).total_seconds()
    
    def touch(self) -> None:
        """Update access information"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self) -> None:
        """Update hit rate calculation"""
        total = self.hits + self.misses
        self.hit_rate = self.hits / total if total > 0 else 0.0


class CacheBackend(ABC):
    """Abstract cache backend"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry"""
        pass
    
    @abstractmethod
    async def set(self, key: str, entry: CacheEntry) -> None:
        """Set cache entry"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    async def keys(self) -> List[str]:
        """Get all cache keys"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get cache size in bytes"""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = OrderedDict()  # For LRU
        self.frequency_counter: Dict[str, int] = {}  # For LFU
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry"""
        with self.lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired:
                entry.touch()
                self._update_access_tracking(key)
                return entry
            elif entry and entry.is_expired:
                await self.delete(key)
            return None
    
    async def set(self, key: str, entry: CacheEntry) -> None:
        """Set cache entry"""
        with self.lock:
            # Calculate entry size
            entry.size_bytes = self._calculate_size(entry.value)
            
            # Check if we need to evict entries
            await self._ensure_capacity(entry.size_bytes)
            
            self.cache[key] = entry
            self._update_access_tracking(key)
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.pop(key, None)
                self.frequency_counter.pop(key, None)
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.frequency_counter.clear()
    
    async def keys(self) -> List[str]:
        """Get all cache keys"""
        with self.lock:
            return list(self.cache.keys())
    
    async def size(self) -> int:
        """Get cache size in bytes"""
        with self.lock:
            return sum(entry.size_bytes for entry in self.cache.values())
    
    def _update_access_tracking(self, key: str) -> None:
        """Update access tracking for LRU and LFU"""
        # Update LRU order
        self.access_order.pop(key, None)
        self.access_order[key] = True
        
        # Update LFU frequency
        self.frequency_counter[key] = self.frequency_counter.get(key, 0) + 1
    
    async def _ensure_capacity(self, new_entry_size: int) -> None:
        """Ensure cache has capacity for new entry"""
        current_size = await self.size()
        
        # Check memory limit
        while (current_size + new_entry_size > self.max_memory_bytes or 
               len(self.cache) >= self.max_size):
            if not self.cache:
                break
            
            # Find key to evict (using LRU for now)
            oldest_key = next(iter(self.access_order))
            await self.delete(oldest_key)
            current_size = await self.size()
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value"""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))


class DiskCacheBackend(CacheBackend):
    """Disk-based cache backend"""
    
    def __init__(self, cache_dir: str = "./cache", max_size_mb: int = 1000):
        import os
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.lock = threading.RLock()
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry from disk"""
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'rb') as f:
                entry = pickle.load(f)
                if not entry.is_expired:
                    entry.touch()
                    # Update file modification time
                    import os
                    os.utime(file_path)
                    return entry
                else:
                    await self.delete(key)
        except (FileNotFoundError, pickle.PickleError):
            pass
        return None
    
    async def set(self, key: str, entry: CacheEntry) -> None:
        """Set cache entry to disk"""
        with self.lock:
            file_path = self._get_file_path(key)
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                # Check disk usage and cleanup if needed
                await self._cleanup_if_needed()
            except Exception as e:
                logging.error(f"Failed to write cache entry to disk: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry from disk"""
        file_path = self._get_file_path(key)
        try:
            import os
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        import os
        import shutil
        try:
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to clear disk cache: {e}")
    
    async def keys(self) -> List[str]:
        """Get all cache keys"""
        import os
        try:
            files = os.listdir(self.cache_dir)
            return [f.replace('.cache', '') for f in files if f.endswith('.cache')]
        except Exception:
            return []
    
    async def size(self) -> int:
        """Get cache size in bytes"""
        import os
        total_size = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        except Exception:
            pass
        return total_size
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        import os
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    async def _cleanup_if_needed(self) -> None:
        """Cleanup old files if cache is too large"""
        current_size = await self.size()
        if current_size <= self.max_size_bytes:
            return
        
        import os
        # Get all cache files with their modification times
        files_info = []
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path) and filename.endswith('.cache'):
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                files_info.append((file_path, mtime, size))
        
        # Sort by modification time (oldest first)
        files_info.sort(key=lambda x: x[1])
        
        # Remove oldest files until under limit
        for file_path, _, file_size in files_info:
            if current_size <= self.max_size_bytes:
                break
            try:
                os.remove(file_path)
                current_size -= file_size
            except Exception:
                pass


class CacheManager:
    """Advanced cache manager with multiple strategies"""
    
    def __init__(
        self,
        backend: CacheBackend,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[int] = None
    ):
        self.backend = backend
        self.strategy = strategy
        self.default_ttl = default_ttl
        self.stats = CacheStats()
        self.cache_warmup_tasks: Set[str] = set()
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            entry = await self.backend.get(key)
            if entry:
                self.stats.hits += 1
                self.stats.update_hit_rate()
                return entry.value
            else:
                self.stats.misses += 1
                self.stats.update_hit_rate()
                return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ) -> None:
        """Set value in cache"""
        async with self.lock:
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl or self.default_ttl,
                tags=tags or set()
            )
            await self.backend.set(key, entry)
            await self._update_stats()
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self.lock:
            result = await self.backend.delete(key)
            if result:
                self.stats.evictions += 1
            await self._update_stats()
            return result
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self.lock:
            await self.backend.clear()
            self.stats = CacheStats()
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ) -> Any:
        """Get value or set it using factory function"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate value using factory
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl, tags)
        return value
    
    async def invalidate_by_tags(self, tags: Set[str]) -> int:
        """Invalidate cache entries by tags"""
        invalidated = 0
        keys = await self.backend.keys()
        
        for key in keys:
            entry = await self.backend.get(key)
            if entry and entry.tags.intersection(tags):
                await self.delete(key)
                invalidated += 1
        
        return invalidated
    
    async def warm_cache(self, warm_functions: Dict[str, Callable]) -> None:
        """Warm cache with predefined data"""
        for key, factory in warm_functions.items():
            if key not in self.cache_warmup_tasks:
                self.cache_warmup_tasks.add(key)
                try:
                    if asyncio.iscoroutinefunction(factory):
                        value = await factory()
                    else:
                        value = factory()
                    await self.set(key, value)
                finally:
                    self.cache_warmup_tasks.discard(key)
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        await self._update_stats()
        return self.stats
    
    async def _update_stats(self) -> None:
        """Update cache statistics"""
        self.stats.size_bytes = await self.backend.size()
        keys = await self.backend.keys()
        self.stats.entry_count = len(keys)


class HierarchicalCache:
    """Multi-level hierarchical cache"""
    
    def __init__(self):
        self.levels: Dict[CacheLevel, CacheManager] = {}
        self.promotion_threshold = 3  # Promote to higher level after N hits
        self.hit_counters: Dict[str, int] = {}
    
    def add_level(self, level: CacheLevel, cache_manager: CacheManager) -> None:
        """Add a cache level"""
        self.levels[level] = cache_manager
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from hierarchical cache"""
        # Try each level in order
        for level in [CacheLevel.L1_MEMORY, CacheLevel.L2_DISK, CacheLevel.L3_DISTRIBUTED]:
            if level in self.levels:
                value = await self.levels[level].get(key)
                if value is not None:
                    # Promote to higher levels if accessed frequently
                    await self._consider_promotion(key, level, value)
                    return value
        return None
    
    async def set(self, key: str, value: Any, **kwargs) -> None:
        """Set value in hierarchical cache"""
        # Set in all levels
        for cache_manager in self.levels.values():
            await cache_manager.set(key, value, **kwargs)
    
    async def delete(self, key: str) -> bool:
        """Delete from all cache levels"""
        deleted = False
        for cache_manager in self.levels.values():
            if await cache_manager.delete(key):
                deleted = True
        self.hit_counters.pop(key, None)
        return deleted
    
    async def _consider_promotion(self, key: str, current_level: CacheLevel, value: Any) -> None:
        """Consider promoting entry to higher cache level"""
        self.hit_counters[key] = self.hit_counters.get(key, 0) + 1
        
        if self.hit_counters[key] >= self.promotion_threshold:
            # Promote to higher levels
            if current_level == CacheLevel.L2_DISK and CacheLevel.L1_MEMORY in self.levels:
                await self.levels[CacheLevel.L1_MEMORY].set(key, value)
            elif current_level == CacheLevel.L3_DISTRIBUTED and CacheLevel.L2_DISK in self.levels:
                await self.levels[CacheLevel.L2_DISK].set(key, value)


# Decorators for easy caching
def cached(
    cache_manager: Optional[CacheManager] = None,
    ttl: Optional[int] = None,
    key_prefix: str = "",
    tags: Optional[Set[str]] = None
):
    """Decorator for caching function results"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal cache_manager
            if cache_manager is None:
                cache_manager = get_default_cache_manager()
            
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl, tags)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal cache_manager
            if cache_manager is None:
                cache_manager = get_default_cache_manager()
            
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # For sync functions, we need to handle async cache operations
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Try to get from cache
            cached_result = loop.run_until_complete(cache_manager.get(cache_key))
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            loop.run_until_complete(cache_manager.set(cache_key, result, ttl, tags))
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def cache_invalidate(cache_manager: Optional[CacheManager] = None, tags: Optional[Set[str]] = None):
    """Decorator for cache invalidation"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            nonlocal cache_manager
            if cache_manager is None:
                cache_manager = get_default_cache_manager()
            
            if tags:
                await cache_manager.invalidate_by_tags(tags)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            nonlocal cache_manager
            if cache_manager is None:
                cache_manager = get_default_cache_manager()
            
            if tags:
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(cache_manager.invalidate_by_tags(tags))
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key from function and arguments"""
    # Create a deterministic key from function name and arguments
    func_name = f"{func.__module__}.{func.__name__}"
    
    # Convert args and kwargs to a hashable representation
    key_data = {
        'function': func_name,
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}" if prefix else key_hash


# Global cache manager
_default_cache_manager: Optional[CacheManager] = None


def get_default_cache_manager() -> CacheManager:
    """Get the default cache manager"""
    global _default_cache_manager
    if _default_cache_manager is None:
        backend = MemoryCacheBackend()
        _default_cache_manager = CacheManager(backend)
    return _default_cache_manager


def set_default_cache_manager(cache_manager: CacheManager) -> None:
    """Set the default cache manager"""
    global _default_cache_manager
    _default_cache_manager = cache_manager