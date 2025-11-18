"""
TiMEM Python SDK

A comprehensive Time-based Memory Management and Experience Learning toolkit.
"""

__version__ = "0.1.1"
__author__ = "AIGility Cloud Innovation"
__email__ = "contact@aigility.com"
__description__ = "Time-based Memory Management and Experience Learning toolkit"

# 导入同步和异步客户端
from .sync_client import TiMEMClient, create_sync_client
from .async_client import TiMEMClient as AsyncTiMEMClient, learn_async, recall_async, create_client
from .connection_pool import ConnectionPool, ConnectionConfig, get_connection_pool
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from .monitoring import PerformanceMonitor, get_global_monitor
from .memory import Memory
from .exceptions import (
    TiMEMError, AuthenticationError, APIError, ValidationError,
    ConnectionError, CircuitBreakerError, TimeoutError, RateLimitError
)

__all__ = [
    # 简化的记忆管理接口（推荐使用）
    "Memory",
    
    # 主客户端（同步，简单易用）
    "TiMEMClient",
    "create_sync_client",
    
    # 异步客户端（高性能）
    "AsyncTiMEMClient",
    "learn_async",
    "recall_async",
    "create_client",
    
    # 连接池
    "ConnectionPool",
    "ConnectionConfig",
    "get_connection_pool",
    
    # 熔断器
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "get_circuit_breaker",
    
    # 监控
    "PerformanceMonitor",
    "get_global_monitor",
    
    # 异常
    "TiMEMError", 
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "ConnectionError",
    "CircuitBreakerError",
    "TimeoutError",
    "RateLimitError",
    
    # 元信息
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
