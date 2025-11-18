from __future__ import annotations
import time
from enum import Enum
from typing import Any, Callable, TypeVar, ParamSpec, Optional
from collections import OrderedDict
from dataclasses import dataclass
from functools import _make_key as make_key
import gevent
import gevent.lock
import gevent.pool
from gevent import monkey
monkey.patch_all()

import ujson
import b64fx
from inspect import signature, Parameter
import logging
import threading
import gc

logger = logging.getLogger(__name__)

T = TypeVar('T')
P = ParamSpec('P')

class CacheStrategy(Enum):
    LRU = "lru"
    MRU = "mru" 
    TTL = "ttl"
    LFU = "lfu"

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
    __slots__ = ('value', 'timestamp', 'access_count', 'expires_at', 'size')
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.timestamp = time.time()
        self.access_count = 0
        self.expires_at = self.timestamp + ttl if ttl else None
        self.size = self._calculate_size(value)
    
    def _calculate_size(self, value) -> int:
        """Быстрый расчет размера объекта"""
        try:
            if isinstance(value, (int, float, bool, type(None))):
                return 64
            elif isinstance(value, str):
                return len(value.encode('utf-8')) + 48
            elif isinstance(value, (list, tuple)):
                if not value:
                    return 128
                return len(value) * 100 + 128
            elif isinstance(value, dict):
                if not value:
                    return 256
                return len(value) * 200 + 256
            else:
                return len(str(value)) + 128
        except:
            return 1024
    
    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at
    
    def touch(self):
        self.access_count += 1

class HighPerformanceCache:
    __slots__ = ('_cache', '_hits', '_misses', '_maxsize', '_strategy', '_lock', 
                 '_current_size', '_total_response_time', '_total_operations')
    
    def __init__(self, maxsize: Optional[int] = 128, strategy: CacheStrategy = CacheStrategy.LRU):
        self._cache = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._maxsize = maxsize
        self._strategy = strategy
        self._lock = gevent.lock.RLock()
        self._current_size = 0
        self._total_response_time = 0.0
        self._total_operations = 0
    
    def get(self, key: Any) -> Any:
        start_time = time.time()
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    self._current_size -= entry.size
                    del self._cache[key]
                    self._misses += 1
                    response_time = time.time() - start_time
                    self._total_response_time += response_time
                    self._total_operations += 1
                    return None
                
                entry.touch()
                self._hits += 1
                self._update_access(key, entry)
                response_time = time.time() - start_time
                self._total_response_time += response_time
                self._total_operations += 1
                return entry.value
            
            self._misses += 1
            response_time = time.time() - start_time
            self._total_response_time += response_time
            self._total_operations += 1
            return None
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        start_time = time.time()
        with self._lock:
            # Удаляем старую запись если есть
            if key in self._cache:
                old_entry = self._cache[key]
                self._current_size -= old_entry.size
                del self._cache[key]
            
            entry = CacheEntry(value, ttl)
            self._cache[key] = entry
            self._current_size += entry.size
            
            self._update_access(key, entry)
            self._evict_if_needed()
            
            response_time = time.time() - start_time
            self._total_response_time += response_time
            self._total_operations += 1
    
    def delete(self, key: Any) -> bool:
        start_time = time.time()
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                self._current_size -= entry.size
                del self._cache[key]
                response_time = time.time() - start_time
                self._total_response_time += response_time
                self._total_operations += 1
                return True
            
            response_time = time.time() - start_time
            self._total_response_time += response_time
            self._total_operations += 1
            return False
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._current_size = 0
            self._total_response_time = 0.0
            self._total_operations = 0
    
    def _update_access(self, key: Any, entry: CacheEntry) -> None:
        if self._strategy == CacheStrategy.LRU:
            self._cache.move_to_end(key)
        elif self._strategy == CacheStrategy.MRU:
            self._cache.move_to_end(key, last=False)
    
    def _evict_if_needed(self) -> None:
        if self._maxsize and len(self._cache) > self._maxsize:
            if self._strategy in (CacheStrategy.LRU, CacheStrategy.TTL):
                key, entry = self._cache.popitem(last=False)
                self._current_size -= entry.size
            elif self._strategy == CacheStrategy.MRU:
                key, entry = self._cache.popitem(last=True)
                self._current_size -= entry.size
            elif self._strategy == CacheStrategy.LFU:
                # Оптимизированный поиск наименее используемого
                min_key = None
                min_count = float('inf')
                
                for key, entry in self._cache.items():
                    if entry.access_count < min_count:
                        min_count = entry.access_count
                        min_key = key
                    if min_count == 0:  # Ранний выход
                        break
                
                if min_key is not None:
                    entry = self._cache[min_key]
                    self._current_size -= entry.size
                    del self._cache[min_key]
    
    def info(self) -> CacheInfo:
        with self._lock:
            avg_response_time = (self._total_response_time / self._total_operations 
                               if self._total_operations > 0 else 0)
            
            return CacheInfo(
                hits=self._hits,
                misses=self._misses,
                maxsize=self._maxsize or 0,
                currsize=len(self._cache),
                strategy=self._strategy,
                memory_used=self._current_size,
                avg_response_time=avg_response_time,
                total_operations=self._total_operations
            )

class TTLCache(HighPerformanceCache):
    __slots__ = ('_default_ttl', '_last_cleanup')
    
    def __init__(self, maxsize: Optional[int] = 128, default_ttl: Optional[float] = None):
        super().__init__(maxsize, CacheStrategy.TTL)
        self._default_ttl = default_ttl
        self._last_cleanup = time.time()
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        actual_ttl = ttl if ttl is not None else self._default_ttl
        super().set(key, value, actual_ttl)
        
        # Авто-очистка каждые 30 секунд
        if time.time() - self._last_cleanup > 30:
            self.cleanup_expired()
    
    def get(self, key: Any) -> Any:
        # Быстрая проверка на необходимость очистки
        if time.time() - self._last_cleanup > 30:
            self.cleanup_expired()
        return super().get(key)
    
    def cleanup_expired(self) -> int:
        with self._lock:
            self._last_cleanup = time.time()
            expired_keys = []
            
            for key, entry in list(self._cache.items()):
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self._cache[key]
                self._current_size -= entry.size
                del self._cache[key]
            
            return len(expired_keys)

class GeventCache(HighPerformanceCache):
    """Кэш с поддержкой gevent корутин"""
    __slots__ = ('_greenlet_pool',)
    
    def __init__(self, maxsize: Optional[int] = 128, strategy: CacheStrategy = CacheStrategy.LRU):
        super().__init__(maxsize, strategy)
        self._greenlet_pool = gevent.pool.Pool(100)  # Пул из 100 зеленых потоков
    
    def get_async(self, key: Any) -> gevent.Greenlet:
        """Асинхронное получение через gevent"""
        return self._greenlet_pool.spawn(self.get, key)
    
    def set_async(self, key: Any, value: Any, ttl: Optional[float] = None) -> gevent.Greenlet:
        """Асинхронная установка через gevent"""
        return self._greenlet_pool.spawn(self.set, key, value, ttl)
    
    def delete_async(self, key: Any) -> gevent.Greenlet:
        """Асинхронное удаление через gevent"""
        return self._greenlet_pool.spawn(self.delete, key)
    
    def clear_async(self) -> gevent.Greenlet:
        """Асинхронная очистка через gevent"""
        return self._greenlet_pool.spawn(self.clear)

# Глобальный реестр кэшей
_cache_registry = set()
_registry_lock = threading.RLock()

def cache(
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    strategy: CacheStrategy = CacheStrategy.LRU,
    typed: bool = False,
    name: Optional[str] = None,
    use_gevent: bool = False,
    redis_client = None
):
    strategy_map = {
        "lru": CacheStrategy.LRU,
        "lfu": CacheStrategy.LFU, 
        "mru": CacheStrategy.MRU,
        "ttl": CacheStrategy.TTL,
    }
    
    # Поддержка строковых стратегий
    if isinstance(strategy, str):
        cache_strategy = strategy_map.get(strategy.lower(), CacheStrategy.LRU)
    else:
        cache_strategy = strategy
    
    def decorator(user_function: Callable[P, T]) -> Callable[P, T]:
        if redis_client:
            # Redis cache implementation would go here
            cache_instance = None
        else:
            if strategy == CacheStrategy.TTL:
                cache_instance = TTLCache(maxsize, ttl)
            elif use_gevent:
                cache_instance = GeventCache(maxsize, cache_strategy)
            else:
                cache_instance = HighPerformanceCache(maxsize, cache_strategy)
        
        # Регистрируем кэш
        with _registry_lock:
            _cache_registry.add(cache_instance)
        
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = make_key(args, kwargs, typed)
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                return cached_result
            
            result = user_function(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            return result
        
        # Добавляем методы управления кэшем
        sync_wrapper.cache_clear = cache_instance.clear
        sync_wrapper.cache_info = cache_instance.info
        sync_wrapper.cache_delete = cache_instance.delete
        
        # Добавляем gevent методы если используется
        if use_gevent and hasattr(cache_instance, 'get_async'):
            sync_wrapper.get_async = lambda *a, **kw: cache_instance.get_async(make_key(a, kw, typed))
            sync_wrapper.set_async = lambda *a, **kw: cache_instance.set_async(make_key(a, kw, typed), user_function(*a, **kw), ttl)
            sync_wrapper.delete_async = lambda *a, **kw: cache_instance.delete_async(make_key(a, kw, typed))
            sync_wrapper.clear_async = cache_instance.clear_async
        
        if isinstance(cache_instance, TTLCache):
            sync_wrapper.cleanup_expired = cache_instance.cleanup_expired
        
        return sync_wrapper
    
    return decorator

class cached_property:
    __slots__ = ('ttl', 'func', 'attrname', '__doc__')
    
    def __init__(self, ttl: Optional[float] = None):
        self.ttl = ttl
        self.func = None
        self.attrname = None
        self.__doc__ = None
    
    def __call__(self, func: Callable) -> 'cached_property':
        self.func = func
        self.__doc__ = func.__doc__
        return self
    
    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(f"Cannot assign cached_property to different names")
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        cache = instance.__dict__
        cache_key = f"_{self.attrname}_cached"
        cache_time_key = f"_{self.attrname}_timestamp"
        
        now = time.time()
        cached_value = cache.get(cache_key)
        cached_time = cache.get(cache_time_key, 0)
        
        if (cached_value is not None and 
            (self.ttl is None or now - cached_time < self.ttl)):
            return cached_value
        
        result = self.func(instance)
        cache[cache_key] = result
        cache[cache_time_key] = now
        return result
    
    def expire(self, instance) -> bool:
        cache_key = f"_{self.attrname}_cached"
        cache_time_key = f"_{self.attrname}_timestamp"
        
        if cache_key in instance.__dict__:
            del instance.__dict__[cache_key]
        if cache_time_key in instance.__dict__:
            del instance.__dict__[cache_time_key]
        return True

def cache_clear_all() -> None:
    """Очищает все зарегистрированные кэши"""
    with _registry_lock:
        for cache_instance in list(_cache_registry):
            try:
                cache_instance.clear()
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
    
    # Принудительный сбор мусора
    gc.collect()

def get_cache_info() -> list[CacheInfo]:
    """Возвращает информацию о всех зарегистрированных кэшах"""
    with _registry_lock:
        return [cache.info() for cache in list(_cache_registry)]

def get_global_stats() -> dict:
    """Глобальная статистика по всем кэшам"""
    all_info = get_cache_info()
    total_hits = sum(info.hits for info in all_info)
    total_misses = sum(info.misses for info in all_info)
    total_operations = sum(info.total_operations for info in all_info)
    total_memory = sum(info.memory_used for info in all_info)
    
    return {
        'total_caches': len(all_info),
        'total_hits': total_hits,
        'total_misses': total_misses,
        'total_operations': total_operations,
        'total_memory_bytes': total_memory,
        'total_memory_mb': total_memory / 1024 / 1024,
        'global_hit_rate': total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0,
        'avg_operations_per_cache': total_operations / len(all_info) if all_info else 0
    }

# Утилиты для массовых операций
def run_concurrent_operations(operations: list, max_workers: int = 100) -> list:
    """Запуск операций конкурентно через gevent"""
    pool = gevent.pool.Pool(max_workers)
    return pool.map(lambda op: op[0](*op[1]), operations)

def batch_set_operations(cache_func, key_value_pairs: list, ttl: Optional[float] = None) -> list:
    """Пакетная установка значений"""
    operations = [(cache_func.set, (key, value, ttl)) for key, value in key_value_pairs]
    return run_concurrent_operations(operations)

def batch_get_operations(cache_func, keys: list) -> list:
    """Пакетное получение значений"""
    operations = [(cache_func.get, (key,)) for key in keys]
    return run_concurrent_operations(operations)