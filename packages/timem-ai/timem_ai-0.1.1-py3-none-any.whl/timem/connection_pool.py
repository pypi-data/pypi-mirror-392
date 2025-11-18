"""
TiMEM连接池管理器

提供企业级连接池管理，支持连接复用、健康检查、自动重连等功能。
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import httpx
from .exceptions import TiMEMError, ConnectionError


@dataclass
class ConnectionConfig:
    """连接配置"""
    max_connections: int = 20
    max_keepalive_connections: int = 10
    keepalive_expiry: float = 30.0  # httpx使用keepalive_expiry而不是keepalive_timeout
    connect_timeout: float = 10.0
    read_timeout: float = 60.0
    write_timeout: float = 60.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 30.0
    max_retries: int = 3


class ConnectionPool:
    """连接池管理器"""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        config: Optional[ConnectionConfig] = None,
        verify_ssl: bool = False
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.config = config or ConnectionConfig()
        self.verify_ssl = verify_ssl
        
        # 连接池状态
        self._pool: Optional[httpx.AsyncClient] = None
        self._last_health_check = 0
        self._is_healthy = True
        self._connection_count = 0
        self._failed_requests = 0
        self._successful_requests = 0
        
        # 日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 健康检查任务
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def initialize(self):
        """初始化连接池"""
        if self._pool is None:
            await self._create_pool()
            await self._start_health_check()
    
    async def _create_pool(self):
        """创建连接池"""
        try:
            headers = {
                "accept": "application/json",
                "X-API-Key": self.api_key,  # TiMEM Engine 使用 X-API-Key 头
                "Content-Type": "application/json",
                "User-Agent": f"timem-python-pool/{__import__('timem').__version__}"
            }
            
            limits = httpx.Limits(
                max_connections=self.config.max_connections,
                max_keepalive_connections=self.config.max_keepalive_connections,
                keepalive_expiry=self.config.keepalive_expiry
            )
            
            timeout = httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.read_timeout,
                write=self.config.write_timeout,
                pool=None  # httpx要求所有4个参数或default参数
            )
            
            self._pool = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                limits=limits,
                timeout=timeout,
                verify=self.verify_ssl
            )
            
            self._connection_count = 0
            self.logger.info(f"连接池已创建: {self.base_url}")
            
        except Exception as e:
            self.logger.error(f"创建连接池失败: {str(e)}")
            raise ConnectionError(f"Failed to create connection pool: {str(e)}")
    
    async def _start_health_check(self):
        """启动健康检查任务"""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._pool is not None:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.warning(f"健康检查失败: {str(e)}")
                self._is_healthy = False
    
    async def _perform_health_check(self):
        """执行健康检查"""
        if self._pool is None:
            return
        
        try:
            start_time = time.time()
            response = await self._pool.get("/api/v1/health", timeout=5.0)
            
            if response.status_code == 200:
                self._is_healthy = True
                self._last_health_check = time.time()
                self.logger.debug(f"健康检查通过: {time.time() - start_time:.2f}s")
            else:
                self._is_healthy = False
                self.logger.warning(f"健康检查失败: HTTP {response.status_code}")
                
        except Exception as e:
            self._is_healthy = False
            self.logger.warning(f"健康检查异常: {str(e)}")
    
    async def get_connection(self) -> httpx.AsyncClient:
        """获取连接"""
        if self._pool is None:
            await self.initialize()
        
        if not self._is_healthy:
            await self._perform_health_check()
        
        if not self._is_healthy:
            raise ConnectionError("连接池不健康")
        
        return self._pool
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """使用连接池发送请求"""
        client = await self.get_connection()
        
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    params=params,
                    **kwargs
                )
                
                # 记录成功请求
                self._successful_requests += 1
                self.logger.debug(
                    f"请求成功: {method} {endpoint} "
                    f"({time.time() - start_time:.2f}s)"
                )
                
                # 处理响应
                if response.status_code >= 400:
                    self._failed_requests += 1
                    try:
                        error_data = response.json()
                        error_message = error_data.get('message', f'HTTP {response.status_code} error')
                    except:
                        error_message = f'HTTP {response.status_code} error'
                    raise httpx.HTTPStatusError(error_message, request=response.request, response=response)
                
                return response.json()
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._failed_requests += 1
                
                if attempt == self.config.retry_attempts - 1:
                    self.logger.error(f"请求失败 (尝试 {attempt + 1}/{self.config.retry_attempts}): {str(e)}")
                    raise
                
                # 等待重试
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                self.logger.warning(f"请求重试 {attempt + 1}/{self.config.retry_attempts}: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            "base_url": self.base_url,
            "is_healthy": self._is_healthy,
            "last_health_check": self._last_health_check,
            "connection_count": self._connection_count,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "success_rate": (
                self._successful_requests / (self._successful_requests + self._failed_requests)
                if (self._successful_requests + self._failed_requests) > 0 else 0
            ),
            "config": {
                "max_connections": self.config.max_connections,
                "max_keepalive_connections": self.config.max_keepalive_connections,
                "health_check_interval": self.config.health_check_interval
            }
        }
    
    async def close(self):
        """关闭连接池"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._pool:
            await self._pool.aclose()
            self._pool = None
        
        self.logger.info("连接池已关闭")
    
    async def reset(self):
        """重置连接池"""
        await self.close()
        await self.initialize()
        self.logger.info("连接池已重置")


class ConnectionPoolManager:
    """连接池管理器 - 支持多实例管理"""
    
    def __init__(self):
        self._pools: Dict[str, ConnectionPool] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def get_pool(
        self,
        base_url: str,
        api_key: str,
        config: Optional[ConnectionConfig] = None,
        verify_ssl: bool = False
    ) -> ConnectionPool:
        """获取或创建连接池"""
        pool_key = f"{base_url}:{api_key}"
        
        if pool_key not in self._pools:
            pool = ConnectionPool(
                base_url=base_url,
                api_key=api_key,
                config=config,
                verify_ssl=verify_ssl
            )
            await pool.initialize()
            self._pools[pool_key] = pool
            self.logger.info(f"创建新连接池: {base_url}")
        
        return self._pools[pool_key]
    
    async def close_all(self):
        """关闭所有连接池"""
        for pool in self._pools.values():
            await pool.close()
        self._pools.clear()
        self.logger.info("所有连接池已关闭")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有连接池统计信息"""
        return {
            pool_key: pool.get_stats()
            for pool_key, pool in self._pools.items()
        }


# 全局连接池管理器实例
_global_pool_manager = ConnectionPoolManager()


async def get_connection_pool(
    base_url: str,
    api_key: str,
    config: Optional[ConnectionConfig] = None,
    verify_ssl: bool = False
) -> ConnectionPool:
    """获取全局连接池"""
    return await _global_pool_manager.get_pool(
        base_url=base_url,
        api_key=api_key,
        config=config,
        verify_ssl=verify_ssl
    )


async def close_all_pools():
    """关闭所有全局连接池"""
    await _global_pool_manager.close_all()
