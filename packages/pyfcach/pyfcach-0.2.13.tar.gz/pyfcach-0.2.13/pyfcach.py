from __future__ import annotations
import time
import sys
import b64fx
import xxhash
from enum import Enum
from typing import Any, Callable, TypeVar, ParamSpec, Optional
from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass
from functools import _make_key as make_key, wraps
import threading
import heapq
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from sympy import symbols, solve, Min, Max, ceiling

T = TypeVar('T')
P = ParamSpec('P')

class CacheStrategy(Enum):
    LRU = "lru"
    MRU = "mru"
    TTL = "ttl"
    LFU = "lfu"
    ARC = "arc"

@dataclass(frozen=True)
class CacheInfo:
    hits: int
    misses: int
    maxsize: int
    currsize: int
    strategy: CacheStrategy
    memory_used: int
    avg_response_time: float
    total_operations: int
    ttl: Optional[float] = None

class CacheEntry:
    __slots__ = ("value", "timestamp", "access_count", "expires_at", "size")

    def __init__(self, value: Any, ttl: Optional[float] = None, size_func: Optional[Callable[[Any], int]] = None):  
        self.value = value  
        self.timestamp = time.perf_counter()
        self.access_count = 0  
        self.expires_at = self.timestamp + ttl if ttl is not None else None  
          
        if size_func:  
            self.size = size_func(value)  
        else:  
            try:  
                self.size = max(64, sys.getsizeof(value))  
            except:  
                self.size = 128  

    def is_expired(self) -> bool:  
        return self.expires_at is not None and time.perf_counter() > self.expires_at  

    def touch(self):  
        self.access_count += 1

class CacheBase:
    __slots__ = ('_cache', '_hits', '_misses', '_maxsize', '_strategy', '_lock',
                 '_current_size', '_total_response_time', '_total_operations', '_memory_limit',
                 '_sample_counter', '_sample_rate', '_batch_operations', '_batch_lock')

    def __init__(self, maxsize: Optional[int] = 128, strategy: CacheStrategy = CacheStrategy.LRU,  
                 memory_limit: Optional[int] = None):  
        self._lock = threading.RLock()
        self._cache = {}  
        self._hits = 0  
        self._misses = 0  
        self._maxsize = maxsize  
        self._strategy = strategy  
        self._current_size = 0  
        self._total_response_time = 0.0  
        self._total_operations = 0  
        self._memory_limit = memory_limit  
        self._sample_counter = 0  
        self._sample_rate = 100  
        self._batch_operations = []
        self._batch_lock = threading.Lock()

    def _record_time(self, start_time: float) -> None:  
        self._sample_counter += 1  
        if self._sample_counter >= self._sample_rate:  
            end_time = time.perf_counter()  
            self._total_response_time += (end_time - start_time) * self._sample_rate  
            self._total_operations += self._sample_rate  
            self._sample_counter = 0  

    def get(self, key: Any) -> Any:  
        start_time = time.perf_counter() if self._sample_counter == 0 else 0  
          
        if key not in self._cache:
            self._misses += 1
            self._record_time(start_time)
            return None
            
        with self._lock:  
            if key in self._cache:  
                entry = self._cache[key]  
                if entry.is_expired():  
                    self._remove_key(key)  
                    self._misses += 1  
                else:  
                    self._update_access(key, entry)  
                    self._hits += 1  
                    self._record_time(start_time)  
                    return entry.value  
            else:  
                self._misses += 1  
              
            self._record_time(start_time)  
            return None  

    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:  
        start_time = time.perf_counter() if self._sample_counter == 0 else 0  
          
        with self._batch_lock:
            if len(self._batch_operations) < 10:
                self._batch_operations.append((key, value, ttl))
                if len(self._batch_operations) < 10:
                    self._record_time(start_time)
                    return
                operations = self._batch_operations.copy()
                self._batch_operations.clear()
            else:
                operations = [(key, value, ttl)]
        
        with self._lock:
            for op_key, op_value, op_ttl in operations:
                if op_key in self._cache:
                    self._remove_key(op_key)
                
                entry = CacheEntry(op_value, op_ttl, self._get_size_func())
                entry_size = entry.size
                
                if self._maxsize is not None and self._maxsize <= 0:
                    continue
                
                self._cache[op_key] = entry
                self._current_size += entry_size
                self._update_access(op_key, entry)
            
            self._evict_if_needed()
            
            self._record_time(start_time)

    def _get_size_func(self) -> Optional[Callable[[Any], int]]:  
        return None  

    def _remove_key(self, key: Any) -> None:  
        if key in self._cache:  
            entry = self._cache[key]  
            del self._cache[key]  
            self._current_size -= entry.size  

    def _update_access(self, key: Any, entry: CacheEntry) -> None:  
        pass  

    def _evict_if_needed(self) -> None:  
        pass  

    def _should_evict(self) -> bool:  
        if self._maxsize is not None and len(self._cache) > self._maxsize:  
            return True  
        if self._memory_limit is not None and self._current_size > self._memory_limit:  
            return True  
        return False  

    def delete(self, key: Any) -> bool:  
        start_time = time.perf_counter() if self._sample_counter == 0 else 0  
          
        with self._lock:  
            if key in self._cache:  
                self._remove_key(key)  
                self._record_time(start_time)  
                return True  
              
            self._record_time(start_time)  
            return False  

    def clear(self) -> None:  
        with self._lock:  
            self._cache.clear()  
            self._hits = 0  
            self._misses = 0  
            self._current_size = 0  
            self._total_response_time = 0.0  
            self._total_operations = 0  
            self._sample_counter = 0  
            self._batch_operations.clear()

    def info(self) -> CacheInfo:  
        with self._lock:  
            if self._total_operations > 0:  
                avg_response_time = self._total_response_time / self._total_operations  
            else:  
                avg_response_time = 0  
                  
            return CacheInfo(  
                hits=self._hits,  
                misses=self._misses,  
                maxsize=self._maxsize or 0,  
                currsize=len(self._cache),  
                strategy=self._strategy,  
                memory_used=self._current_size,  
                avg_response_time=avg_response_time,  
                total_operations=self._total_operations,  
                ttl=None  
            )

class ARCCache(CacheBase):
    __slots__ = ('_t1', '_t2', '_b1', '_b2', '_p', '_size', '_adaptive_lock')
    
    def __init__(self, maxsize: Optional[int] = 128, memory_limit: Optional[int] = None):
        super().__init__(maxsize, CacheStrategy.ARC, memory_limit)
        self._size = maxsize or 128
        self._t1 = OrderedDict()
        self._t2 = OrderedDict()
        self._b1 = OrderedDict()
        self._b2 = OrderedDict()
        self._p = 0
        self._adaptive_lock = threading.Lock()

    def _remove_key(self, key: Any) -> None:
        if key in self._t1:
            del self._t1[key]
        if key in self._t2:
            del self._t2[key]
        if key in self._cache:
            super()._remove_key(key)

    def _update_access(self, key: Any, entry: CacheEntry) -> None:
        entry.touch()
        if key in self._t1:
            del self._t1[key]
            self._t2[key] = entry
        elif key in self._t2:
            self._t2.move_to_end(key)

    def get(self, key: Any) -> Any:
        start_time = time.perf_counter() if self._sample_counter == 0 else 0
        
        if key not in self._cache and key not in self._b1 and key not in self._b2:
            self._misses += 1
            self._record_time(start_time)
            return None
            
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    self._remove_key(key)
                    self._misses += 1
                else:
                    self._update_access(key, entry)
                    self._hits += 1
                    self._record_time(start_time)
                    return entry.value
            
            with self._adaptive_lock:
                if key in self._b1:
                    b1_len, b2_len = len(self._b1), len(self._b2)
                    delta = 1
                    if b1_len >= b2_len and b1_len > 0:
                        delta = b2_len // b1_len
                    self._p = min(self._p + delta, self._size)
                    self._replace(key)
                    self._b1.pop(key)
                    self._t2[key] = self._cache[key]
                elif key in self._b2:
                    b1_len, b2_len = len(self._b1), len(self._b2)
                    delta = 1
                    if b2_len >= b1_len and b2_len > 0:
                        delta = b1_len // b2_len
                    self._p = max(self._p - delta, 0)
                    self._replace(key)
                    self._b2.pop(key)
                    self._t2[key] = self._cache[key]
                else:
                    self._misses += 1
            
            self._record_time(start_time)
            return None

    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        start_time = time.perf_counter() if self._sample_counter == 0 else 0
        
        with self._batch_lock:
            if len(self._batch_operations) < 15:
                self._batch_operations.append((key, value, ttl))
                if len(self._batch_operations) < 15:
                    self._record_time(start_time)
                    return
                operations = self._batch_operations.copy()
                self._batch_operations.clear()
            else:
                operations = [(key, value, ttl)]
        
        with self._lock:
            for op_key, op_value, op_ttl in operations:
                if op_key in self._cache:
                    self._remove_key(op_key)
                
                entry = CacheEntry(op_value, op_ttl, self._get_size_func())
                entry_size = entry.size
                
                if self._maxsize is not None and self._maxsize <= 0:
                    continue
                
                self._cache[op_key] = entry
                self._current_size += entry_size
                
                if op_key in self._b1 or op_key in self._b2:
                    self._t2[op_key] = entry
                    if op_key in self._b1:
                        self._b1.pop(op_key)
                    if op_key in self._b2:
                        self._b2.pop(op_key)
                else:
                    self._t1[op_key] = entry
            
            self._evict_if_needed()
            
            self._record_time(start_time)

    def _replace(self, key: Any) -> None:
        t1_len = len(self._t1)
        if t1_len > 0 and (t1_len > self._p or (key in self._b2 and t1_len == self._p)):
            old_key, old_entry = self._t1.popitem(last=False)
            self._b1[old_key] = old_entry
            if old_key in self._cache:
                super()._remove_key(old_key)
        else:
            if self._t2:
                old_key, old_entry = self._t2.popitem(last=False)
                self._b2[old_key] = old_entry
                if old_key in self._cache:
                    super()._remove_key(old_key)

    def _evict_if_needed(self) -> None:
        total_len = len(self._t1) + len(self._t2)
        
        while self._should_evict() and total_len > 0:
            total_size = len(self._t1) + len(self._b1)
            if total_size >= self._size:
                if len(self._t1) < self._size:
                    if self._b1:
                        self._b1.popitem(last=False)
                    self._replace(None)
                else:
                    key, entry = self._t1.popitem(last=False)
                    if key in self._cache:
                        super()._remove_key(key)
            else:
                total_all = len(self._t1) + len(self._t2) + len(self._b1) + len(self._b2)
                if total_all >= 2 * self._size:
                    if self._b1:
                        self._b1.popitem(last=False)
                    elif self._b2:
                        self._b2.popitem(last=False)
                self._replace(None)
            
            total_len = len(self._t1) + len(self._t2)

    def clear(self) -> None:
        with self._lock:
            self._t1.clear()
            self._t2.clear()
            self._b1.clear()
            self._b2.clear()
            self._p = 0
            super().clear()

class OptimizedLFUCache(CacheBase):
    __slots__ = ('_freq_nodes', '_min_freq', '_freq_dict')

    def __init__(self, maxsize: Optional[int] = 128, memory_limit: Optional[int] = None):  
        super().__init__(maxsize, CacheStrategy.LFU, memory_limit)  
        self._freq_nodes = defaultdict(OrderedDict)  
        self._min_freq = 0  
        self._freq_dict = {}  

    def _remove_key(self, key: Any) -> None:  
        if key in self._cache:  
            old_entry = self._cache[key]  
            old_freq = self._freq_dict[key]  
              
            del self._freq_nodes[old_freq][key]  
            if not self._freq_nodes[old_freq]:  
                del self._freq_nodes[old_freq]  
                if old_freq == self._min_freq:  
                    self._min_freq = old_freq + 1  
              
            del self._freq_dict[key]  
            super()._remove_key(key)  

    def _update_access(self, key: Any, entry: CacheEntry) -> None:  
        entry.touch()  
        if key in self._freq_dict:  
            old_freq = self._freq_dict[key]  
            new_freq = old_freq + 1  
              
            del self._freq_nodes[old_freq][key]  
            if not self._freq_nodes[old_freq]:  
                del self._freq_nodes[old_freq]  
                if old_freq == self._min_freq:  
                    self._min_freq = new_freq  
              
            self._freq_nodes[new_freq][key] = entry  
            self._freq_dict[key] = new_freq  
        else:  
            self._freq_nodes[1][key] = entry  
            self._freq_dict[key] = 1  
            self._min_freq = 1  

    def _evict_if_needed(self) -> None:  
        while self._should_evict() and self._freq_nodes:  
            while self._min_freq not in self._freq_nodes and self._freq_nodes:  
                self._min_freq = min(self._freq_nodes.keys())  
              
            if not self._freq_nodes.get(self._min_freq):  
                continue  
              
            key, _ = self._freq_nodes[self._min_freq].popitem(last=False)  
            if not self._freq_nodes[self._min_freq]:  
                del self._freq_nodes[self._min_freq]  
              
            if key in self._freq_dict:  
                del self._freq_dict[key]  
            if key in self._cache:  
                super()._remove_key(key)

class TTLCache(CacheBase):
    __slots__ = ('_default_ttl', '_expiry_heap', '_cleanup_thread', '_cleanup_interval', '_running', '_cleanup_batch_size')

    def __init__(self, maxsize: Optional[int] = 128, default_ttl: Optional[float] = None,   
                 memory_limit: Optional[int] = None, cleanup_interval: float = 60.0):  
        super().__init__(maxsize, CacheStrategy.TTL, memory_limit)  
        self._default_ttl = default_ttl  
        self._expiry_heap = []  
        self._cleanup_interval = cleanup_interval  
        self._running = True  
        self._cleanup_batch_size = 1000
          
        self._cleanup_thread = threading.Thread(target=self._background_cleanup, daemon=True)  
        self._cleanup_thread.start()  
      
    def _background_cleanup(self) -> None:  
        while self._running:  
            with self._lock:  
                if self._expiry_heap:  
                    next_expire = self._expiry_heap[0][0]  
                    timeout = max(0, next_expire - time.perf_counter())  
                else:  
                    timeout = self._cleanup_interval  
              
            time.sleep(min(timeout, self._cleanup_interval))  
            self.cleanup_expired()  
      
    def cleanup_expired(self) -> int:  
        with self._lock:  
            now = time.perf_counter()  
            expired_count = 0  
            expired_keys = []
              
            while self._expiry_heap and self._expiry_heap[0][0] <= now and expired_count < self._cleanup_batch_size:
                expires_at, key = heapq.heappop(self._expiry_heap)  
                if key in self._cache and self._cache[key].expires_at == expires_at:  
                    if self._cache[key].is_expired():  
                        expired_keys.append(key)
                        expired_count += 1
              
            for key in expired_keys:
                super()._remove_key(key)
              
            return expired_count  
      
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:  
        start_time = time.perf_counter() if self._sample_counter == 0 else 0  
          
        with self._lock:  
            if key in self._cache:  
                super()._remove_key(key)  
              
            actual_ttl = ttl if ttl is not None else self._default_ttl  
            entry = CacheEntry(value, actual_ttl, self._get_size_func())  
            entry_size = entry.size  
              
            if self._maxsize is not None and self._maxsize <= 0:  
                pass  
            else:  
                self._cache[key] = entry  
                self._current_size += entry_size  
                  
                if actual_ttl is not None:  
                    heapq.heappush(self._expiry_heap, (entry.expires_at, key))  
                  
                self._evict_if_needed()  
              
            self._record_time(start_time)  
      
    def _evict_if_needed(self) -> None:  
        while self._should_evict() and self._cache:  
            oldest_key = None  
            oldest_time = float('inf')  
              
            for key, entry in self._cache.items():  
                if entry.timestamp < oldest_time:  
                    oldest_time = entry.timestamp  
                    oldest_key = key  
                    if oldest_time < time.perf_counter() - 3600:
                        break
              
            if oldest_key is not None:  
                super()._remove_key(oldest_key)  
      
    def close(self) -> None:  
        self._running = False  
        if self._cleanup_thread.is_alive():  
            self._cleanup_thread.join(timeout=1.0)  
      
    def info(self) -> CacheInfo:
        with self._lock:
            base_info = super().info()
            base_dict = base_info.__dict__.copy()
            base_dict['ttl'] = self._default_ttl
            return CacheInfo(**base_dict)

class HighPerformanceCache(CacheBase):
    __slots__ = ('_order',)

    def __init__(self, maxsize: Optional[int] = 128, strategy: CacheStrategy = CacheStrategy.LRU,   
                 memory_limit: Optional[int] = None):  
        super().__init__(maxsize, strategy, memory_limit)  
        self._order = OrderedDict()  
      
    def _update_access(self, key: Any, entry: CacheEntry) -> None:  
        if self._strategy == CacheStrategy.LRU:  
            if key in self._order:  
                self._order.move_to_end(key)  
            else:  
                self._order[key] = True  
        elif self._strategy == CacheStrategy.MRU:  
            if key in self._order:  
                self._order.move_to_end(key, last=False)  
            else:  
                self._order[key] = True  
      
    def _remove_key(self, key: Any) -> None:  
        if key in self._order:  
            del self._order[key]  
        super()._remove_key(key)  
      
    def _evict_if_needed(self) -> None:  
        while self._should_evict() and self._order:  
            if self._strategy == CacheStrategy.LRU:  
                key, _ = self._order.popitem(last=False)  
            elif self._strategy == CacheStrategy.MRU:  
                key, _ = self._order.popitem(last=True)  
              
            if key in self._cache:  
                super()._remove_key(key)  
      
    def clear(self) -> None:  
        with self._lock:  
            self._order.clear()  
            super().clear()

class AsyncCache:
    __slots__ = ('_cache', '_lock', '_strategy', '_batch_operations', '_batch_lock')
    
    def __init__(self, maxsize: int = 128, strategy: CacheStrategy = CacheStrategy.LRU):
        self._strategy = strategy
        self._lock = asyncio.Lock()
        self._batch_operations = []
        self._batch_lock = asyncio.Lock()
        
        if strategy == CacheStrategy.ARC:
            self._cache = ARCCache(maxsize)
        elif strategy == CacheStrategy.LFU:
            self._cache = OptimizedLFUCache(maxsize)
        elif strategy == CacheStrategy.TTL:
            self._cache = TTLCache(maxsize)
        else:
            self._cache = HighPerformanceCache(maxsize, strategy)

    async def get(self, key: Any) -> Any:
        result = self._cache.get(key)
        if result is not None:
            return result
            
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        async with self._batch_lock:
            if len(self._batch_operations) < 5:
                self._batch_operations.append((key, value, ttl))
                if len(self._batch_operations) < 5:
                    return
                operations = self._batch_operations.copy()
                self._batch_operations.clear()
            else:
                operations = [(key, value, ttl)]
        
        async with self._lock:
            for op_key, op_value, op_ttl in operations:
                self._cache.set(op_key, op_value, op_ttl)

    async def delete(self, key: Any) -> bool:
        async with self._lock:
            return self._cache.delete(key)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

    async def info(self) -> CacheInfo:
        async with self._lock:
            return self._cache.info()

def _optimized_make_key(args, kwargs, typed):
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return hash(tuple(key_parts))

async def async_cache(
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    strategy: CacheStrategy | str = CacheStrategy.LRU,
    typed: bool = False
):
    strategy_map = {
        "lru": CacheStrategy.LRU,
        "lfu": CacheStrategy.LFU,
        "mru": CacheStrategy.MRU,
        "ttl": CacheStrategy.TTL,
        "arc": CacheStrategy.ARC,
    }

    if isinstance(strategy, str):  
        cache_strategy = strategy_map.get(strategy.lower(), CacheStrategy.LRU)  
    else:  
        cache_strategy = strategy
    
    def decorator(user_function: Callable[P, T]) -> Callable[P, T]:
        cache_instance = AsyncCache(maxsize, cache_strategy)
        
        @wraps(user_function)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = _optimized_make_key(args, kwargs, typed)
            
            cached_result = await cache_instance.get(key)
            if cached_result is not None:
                return cached_result
            
            result = user_function(*args, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            
            asyncio.create_task(cache_instance.set(key, result, ttl))
            return result
        
        async_wrapper.cache_clear = cache_instance.clear
        async_wrapper.cache_info = cache_instance.info
        async_wrapper.cache_delete = lambda *args, **kwargs: cache_instance.delete(
            _optimized_make_key(args, kwargs, typed)
        )
        
        return async_wrapper
    
    return decorator

_cache_registry = set()
_registry_lock = threading.Lock()
_local_executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix="cache_batch")
_uloop = None
_uloop_lock = threading.Lock()

def _get_uloop() -> asyncio.AbstractEventLoop:
    global _uloop
    with _uloop_lock:
        if _uloop is None:
            try:
                _uloop = asyncio.get_running_loop()
            except RuntimeError:
                _uloop = asyncio.new_event_loop()
                asyncio.set_event_loop(_uloop)
        return _uloop

async def async_batch_set_operations(cache_instance: HighPerformanceCache, key_value_pairs: list, ttl: Optional[float] = None) -> list:
    def _batch_set_chunk(chunk):
        results = []
        for key, value in chunk:
            cache_instance.set(key, value, ttl)
            results.append(True)
        return results

    n = len(key_value_pairs)
    workers = min(16, n)
    chunk_size = int(ceiling(Max(10, n / workers))) if workers > 0 else n
    
    chunks = [key_value_pairs[i:i + chunk_size] for i in range(0, n, chunk_size)]  
    
    loop = _get_uloop()  
    
    with ThreadPoolExecutor(max_workers=workers) as executor:  
        futures = [  
            loop.run_in_executor(executor, _batch_set_chunk, chunk)  
            for chunk in chunks  
        ]  
        results = []  
        for future in asyncio.as_completed(futures):  
            chunk_results = await future  
            results.extend(chunk_results)  
    
    return results

async def async_batch_get_operations(cache_instance: HighPerformanceCache, keys: list) -> list:
    def _batch_get_chunk(chunk):
        results = []
        for key in chunk:
            results.append(cache_instance.get(key))
        return results

    n = len(keys)
    workers = min(16, n)
    chunk_size = int(ceiling(Max(10, n / workers))) if workers > 0 else n
    
    chunks = [keys[i:i + chunk_size] for i in range(0, n, chunk_size)]  
    
    loop = _get_uloop()  
    
    with ThreadPoolExecutor(max_workers=workers) as executor:  
        futures = [  
            loop.run_in_executor(executor, _batch_get_chunk, chunk)  
            for chunk in chunks  
        ]  
        results = []  
        for future in asyncio.as_completed(futures):  
            chunk_results = await future  
            results.extend(chunk_results)  
    
    return results

def batch_set_operations(cache_instance: HighPerformanceCache, key_value_pairs: list, ttl: Optional[float] = None) -> list:
    def _batch_set_chunk(chunk):
        results = []
        for key, value in chunk:
            cache_instance.set(key, value, ttl)
            results.append(True)
        return results

    n = len(key_value_pairs)
    workers = min(16, n)
    chunk_size = int(ceiling(Max(10, n / workers))) if workers > 0 else n
    
    chunks = [key_value_pairs[i:i + chunk_size] for i in range(0, n, chunk_size)]  
    
    with ThreadPoolExecutor(max_workers=workers) as executor:  
        futures = [executor.submit(_batch_set_chunk, chunk) for chunk in chunks]  
        results = []  
        for future in as_completed(futures):  
            results.extend(future.result())  
    
    return results

def batch_get_operations(cache_instance: HighPerformanceCache, keys: list) -> list:
    def _batch_get_chunk(chunk):
        results = []
        for key in chunk:
            results.append(cache_instance.get(key))
        return results

    n = len(keys)
    workers = min(16, n)
    chunk_size = int(ceiling(Max(10, n / workers))) if workers > 0 else n
    
    chunks = [keys[i:i + chunk_size] for i in range(0, n, chunk_size)]  
    
    with ThreadPoolExecutor(max_workers=workers) as executor:  
        futures = [executor.submit(_batch_get_chunk, chunk) for chunk in chunks]  
        results = []  
        for future in as_completed(futures):  
            results.extend(future.result())  
    
    return results

def cache(
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    strategy: CacheStrategy | str = CacheStrategy.LRU,
    typed: bool = False,
    memory_limit: Optional[int] = None
):
    strategy_map = {
        "lru": CacheStrategy.LRU,
        "lfu": CacheStrategy.LFU,
        "mru": CacheStrategy.MRU,
        "ttl": CacheStrategy.TTL,
        "arc": CacheStrategy.ARC,
    }

    if isinstance(strategy, str):  
        cache_strategy = strategy_map.get(strategy.lower(), CacheStrategy.LRU)  
    else:  
        cache_strategy = strategy  
    
    def decorator(user_function: Callable[P, T]) -> Callable[P, T]:  
        if cache_strategy == CacheStrategy.TTL or ttl is not None:  
            cache_instance = TTLCache(maxsize, ttl, memory_limit)  
        elif cache_strategy == CacheStrategy.LFU:  
            cache_instance = OptimizedLFUCache(maxsize, memory_limit)  
        elif cache_strategy == CacheStrategy.ARC:
            cache_instance = ARCCache(maxsize, memory_limit)
        else:  
            cache_instance = HighPerformanceCache(maxsize, cache_strategy, memory_limit)  
          
        with _registry_lock:  
            _cache_registry.add(cache_instance)  
          
        @wraps(user_function)  
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  
            key = _optimized_make_key(args, kwargs, typed)  
              
            cached_result = cache_instance.get(key)  
            if cached_result is not None:  
                return cached_result  
              
            result = user_function(*args, **kwargs)  
            if sys.getsizeof(result) > 1024:
                threading.Thread(target=cache_instance.set, args=(key, result, ttl), daemon=True).start()
            else:
                cache_instance.set(key, result, ttl)
            return result  
          
        @wraps(user_function)  
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  
            key = _optimized_make_key(args, kwargs, typed)  
              
            cached_result = cache_instance.get(key)  
            if cached_result is not None:  
                return cached_result  
              
            result = user_function(*args, **kwargs)  
            if asyncio.iscoroutine(result):  
                result = await result  
              
            asyncio.create_task(cache_instance.set(key, result, ttl))
            return result  
          
        wrapper = async_wrapper if asyncio.iscoroutinefunction(user_function) else sync_wrapper  
          
        wrapper.cache_clear = cache_instance.clear  
        wrapper.cache_info = cache_instance.info  
          
        def cache_delete_wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:  
            key_to_delete = _optimized_make_key(args, kwargs, typed)  
            return cache_instance.delete(key_to_delete)  
          
        wrapper.cache_delete = cache_delete_wrapper  
          
        if isinstance(cache_instance, TTLCache):  
            wrapper.cleanup_expired = cache_instance.cleanup_expired  
            wrapper.close = cache_instance.close  
          
        return wrapper  
    
    return decorator

class cached_property:
    __slots__ = ('_ttl', '_func', '_attrname', '_lock', '__doc__')

    def __init__(self, ttl: Optional[float] = None):  
        self._ttl = ttl  
        self._func = None  
        self._attrname = None  
        self._lock = threading.RLock()  
        self.__doc__ = None
  
    def __call__(self, func: Callable) -> 'cached_property':  
        self._func = func  
        self.__doc__ = func.__doc__  
        return self  
      
    def __set_name__(self, owner, name):  
        if self._attrname is None:  
            self._attrname = name  
        elif name != self._attrname:  
            raise TypeError("Cannot assign cached_property to different names")  
      
    def __get__(self, instance, owner=None):  
        if instance is None:  
            return self  
          
        cache = instance.__dict__  
        cache_key = f"_{self._attrname}_cached"  
        cache_time_key = f"_{self._attrname}_timestamp"  
          
        now = time.perf_counter()  
          
        with self._lock:  
            cached_value = cache.get(cache_key)  
            cached_time = cache.get(cache_time_key, 0)  
              
            is_valid = (cached_value is not None and   
                        (self._ttl is None or now - cached_time < self._ttl))  
              
            if is_valid:  
                return cached_value  
              
            result = self._func(instance)  
              
            cache[cache_key] = result  
            cache[cache_time_key] = now  
            return result  
      
    def expire(self, instance) -> bool:  
        cache_key = f"_{self._attrname}_cached"  
        cache_time_key = f"_{self._attrname}_timestamp"  
          
        with self._lock:  
            deleted = False  
            if cache_key in instance.__dict__:  
                del instance.__dict__[cache_key]  
                deleted = True  
            if cache_time_key in instance.__dict__:  
                del instance.__dict__[cache_time_key]  
            return deleted

class AsyncCachedProperty:
    __slots__ = ('_ttl', '_func', '_attrname', '_lock', '__doc__')

    def __init__(self, ttl: Optional[float] = None):  
        self._ttl = ttl  
        self._func = None  
        self._attrname = None  
        self._lock = asyncio.Lock()  
        self.__doc__ = None  
      
    def __call__(self, func: Callable) -> 'AsyncCachedProperty':  
        self._func = func  
        self.__doc__ = func.__doc__  
        return self  
      
    def __set_name__(self, owner, name):  
        if self._attrname is None:  
            self._attrname = name  
        elif name != self._attrname:  
            raise TypeError("Cannot assign AsyncCachedProperty to different names")  
      
    async def __get__(self, instance, owner=None):  
        if instance is None:  
            return self  
          
        cache = instance.__dict__  
        cache_key = f"_{self._attrname}_cached"  
        cache_time_key = f"_{self._attrname}_timestamp"  
          
        now = time.perf_counter()  
          
        async with self._lock:  
            cached_value = cache.get(cache_key)  
            cached_time = cache.get(cache_time_key, 0)  
              
            is_valid = (cached_value is not None and   
                        (self._ttl is None or now - cached_time < self._ttl))  
              
            if is_valid:  
                return cached_value  
              
            result = self._func(instance)  
            if asyncio.iscoroutine(result):  
                result = await result  
              
            cache[cache_key] = result  
            cache[cache_time_key] = now  
            return result  
      
    def expire(self, instance) -> bool:  
        cache_key = f"_{self._attrname}_cached"  
        cache_time_key = f"_{self._attrname}_timestamp"  
          
        deleted = False  
        if cache_key in instance.__dict__:  
            del instance.__dict__[cache_key]  
            deleted = True  
        if cache_time_key in instance.__dict__:  
            del instance.__dict__[cache_time_key]  
        return deleted

def cache_clear_all() -> None:
    with _registry_lock:
        for cache_instance in list(_cache_registry):
            try:
                cache_instance.clear()
            except Exception:
                pass

def get_cache_info() -> list[CacheInfo]:
    with _registry_lock:
        return [cache_instance.info() for cache_instance in list(_cache_registry)]

def get_global_stats() -> dict:
    all_info = get_cache_info()
    total_hits = sum(info.hits for info in all_info)
    total_misses = sum(info.misses for info in all_info)
    total_operations = sum(info.total_operations for info in all_info)
    total_memory = sum(info.memory_used for info in all_info)

    total_requests = total_hits + total_misses  
    
    return {  
        'total_caches': len(all_info),  
        'total_hits': total_hits,  
        'total_misses': total_misses,  
        'total_operations': total_operations,  
        'total_memory_bytes': total_memory,  
        'total_memory_mb': total_memory / 1024 / 1024,  
        'global_hit_rate': total_hits / total_requests if total_requests > 0 else 0,  
        'avg_operations_per_cache': total_operations / len(all_info) if all_info else 0  
    }

async def async_cache_clear_all() -> None:
    with _registry_lock:
        for cache_instance in list(_cache_registry):
            try:
                cache_instance.clear()
            except Exception:
                pass

async def async_get_cache_info() -> list[CacheInfo]:
    with _registry_lock:
        return [cache_instance.info() for cache_instance in list(_cache_registry)]

async def async_get_global_stats() -> dict:
    all_info = await async_get_cache_info()
    total_hits = sum(info.hits for info in all_info)
    total_misses = sum(info.misses for info in all_info)
    total_operations = sum(info.total_operations for info in all_info)
    total_memory = sum(info.memory_used for info in all_info)

    total_requests = total_hits + total_misses  
    
    return {  
        'total_caches': len(all_info),  
        'total_hits': total_hits,  
        'total_misses': total_misses,  
        'total_operations': total_operations,  
        'total_memory_bytes': total_memory,  
        'total_memory_mb': total_memory / 1024 / 1024,  
        'global_hit_rate': total_hits / total_requests if total_requests > 0 else 0,  
        'avg_operations_per_cache': total_operations / len(all_info) if all_info else 0  
    }

def shutdown_all_executors():
    _local_executor.shutdown(wait=False, cancel_futures=True)

async def async_shutdown_all_executors():
    _local_executor.shutdown(wait=False, cancel_futures=True)