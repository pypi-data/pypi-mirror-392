"""
TiMEM增强异步客户端

集成连接池、熔断器、监控等企业级特性的异步客户端。
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, List
from .exceptions import TiMEMError, AuthenticationError, APIError, ValidationError, ConnectionError, CircuitBreakerError
from .connection_pool import ConnectionPool, ConnectionConfig, get_connection_pool
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from .monitoring import PerformanceMonitor, get_global_monitor


class EnhancedAsyncTiMEMClient:
    """
    增强的异步TiMEM客户端
    
    集成企业级特性：
    - 连接池管理
    - 熔断器保护
    - 性能监控
    - 结构化日志
    - 自动重试
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001",
        connection_config: Optional[ConnectionConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        enable_monitoring: bool = True,
        verify_ssl: bool = False,
        **kwargs
    ):
        """
        初始化增强的异步TiMEM客户端
        
        Args:
            api_key: TiMEM API密钥
            base_url: API基础URL
            connection_config: 连接池配置
            circuit_breaker_config: 熔断器配置
            enable_monitoring: 是否启用监控
            verify_ssl: 是否验证SSL证书
            **kwargs: 其他参数
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        
        # 连接池配置
        self.connection_config = connection_config or ConnectionConfig()
        
        # 熔断器配置
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        
        # 监控配置
        self.enable_monitoring = enable_monitoring
        self.monitor = get_global_monitor() if enable_monitoring else None
        
        # 日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 连接池和熔断器（延迟初始化）
        self._pool: Optional[ConnectionPool] = None
        self._circuit_breaker: Optional[CircuitBreaker] = None
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_breaker_trips": 0,
            "connection_pool_resets": 0
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def initialize(self):
        """初始化客户端"""
        try:
            # 初始化连接池
            self._pool = await get_connection_pool(
                base_url=self.base_url,
                api_key=self.api_key,
                config=self.connection_config,
                verify_ssl=self.verify_ssl
            )
            
            # 初始化熔断器
            self._circuit_breaker = get_circuit_breaker(
                name=f"timem_{self.base_url}",
                config=self.circuit_breaker_config,
                fallback_func=self._fallback_handler
            )
            
            self.logger.info(f"增强TiMEM客户端已初始化: {self.base_url}")
            
        except Exception as e:
            self.logger.error(f"客户端初始化失败: {str(e)}")
            raise ConnectionError(f"Failed to initialize client: {str(e)}")
    
    async def close(self):
        """关闭客户端"""
        if self._pool:
            await self._pool.close()
            self._pool = None
        
        self.logger.info("增强TiMEM客户端已关闭")
    
    async def _fallback_handler(self, *args, **kwargs) -> Dict[str, Any]:
        """降级处理函数"""
        self.stats["circuit_breaker_trips"] += 1
        self.logger.warning("熔断器触发，使用降级处理")
        
        return {
            "success": False,
            "error": "Service temporarily unavailable",
            "fallback": True,
            "message": "TiMEM服务暂时不可用，请稍后重试"
        }
    
    async def _make_enhanced_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        domain: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送增强请求
        
        集成连接池、熔断器、监控等功能
        """
        if not self._pool:
            await self.initialize()
        
        start_time = time.time()
        success = False
        error_message = None
        status_code = 200
        
        try:
            # 使用熔断器保护
            result = await self._circuit_breaker.call(
                self._pool.make_request,
                method=method,
                endpoint=endpoint,
                data=data,
                params=params,
                **kwargs
            )
            
            success = True
            self.stats["successful_requests"] += 1
            
            return result
            
        except CircuitBreakerError as e:
            error_message = f"Circuit breaker open: {str(e)}"
            status_code = 503
            self.stats["circuit_breaker_trips"] += 1
            raise
            
        except (ConnectionError, APIError, AuthenticationError) as e:
            error_message = str(e)
            status_code = getattr(e, 'status_code', 500)
            self.stats["failed_requests"] += 1
            raise
            
        except Exception as e:
            error_message = str(e)
            status_code = 500
            self.stats["failed_requests"] += 1
            raise TiMEMError(f"Request failed: {str(e)}")
            
        finally:
            # 记录统计信息
            self.stats["total_requests"] += 1
            duration = time.time() - start_time
            
            # 记录监控数据
            if self.monitor:
                self.monitor.record_request(
                    method=method,
                    endpoint=endpoint,
                    duration=duration,
                    status_code=status_code,
                    success=success,
                    user_id=user_id,
                    domain=domain,
                    error_message=error_message
                )
    
    # ==================== Experience Learning Engine APIs ====================
    
    async def learn(
        self,
        domain: str = "general",
        feedback_cases: Optional[List[Dict[str, Any]]] = None,
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        学习生成经验规则（增强版）
        """
        if not domain:
            raise ValidationError("Domain is required")
        
        # 如果提供了反馈案例，先收集
        if feedback_cases:
            import datetime
            batch_id = f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            collect_data = {
                "batch_id": batch_id,
                "feedback_cases": feedback_cases
            }
            
            # 收集反馈
            await self._make_enhanced_request(
                "POST", "/api/v1/rules/feedback/collect",
                data=collect_data, user_id=user_id, domain=domain
            )
        
        # 触发学习
        data = {
            "domain": domain,
            "min_case_count": min_case_count,
            "min_adoption_rate": min_adoption_rate,
            "min_confidence_score": min_confidence_score
        }
        
        params = {"summarization_strategy": strategy}
        
        return await self._make_enhanced_request(
            "POST", "/api/v1/rules/learn-with-llm",
            data=data, params=params, user_id=user_id, domain=domain
        )
    
    async def recall(
        self,
        context: Dict[str, Any],
        domain: str = "general",
        top_k: int = 5,
        min_confidence: float = 0.5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        召回相关经验规则（增强版）
        """
        if not context:
            raise ValidationError("Context is required")
        
        data = {
            "domain": domain,
            "context": context,
            "top_k": top_k,
            "min_confidence": min_confidence
        }
        
        return await self._make_enhanced_request(
            "POST", "/api/v1/rules/rule-call",
            data=data, user_id=user_id, domain=domain
        )
    
    # ==================== Memory Management APIs ====================
    
    async def add_memory(
        self,
        user_id: int,
        domain: str,
        content: Dict[str, Any],
        layer_type: str = "L1",
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        添加记忆（增强版）
        """
        if not content:
            raise ValidationError("Memory content is required")
        
        data = {
            "user_id": user_id,
            "domain": domain,
            "content": content,
            "layer_type": layer_type,
            "tags": tags or [],
            "keywords": keywords or []
        }
        
        return await self._make_enhanced_request(
            "POST", "/api/v1/memory/memories",
            data=data, user_id=str(user_id), domain=domain
        )
    
    async def search_memory(
        self,
        user_id: Optional[int] = None,
        domain: Optional[str] = None,
        layer_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        搜索记忆（增强版）
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if user_id:
            params["user_id"] = user_id
        if domain:
            params["domain"] = domain
        if layer_type:
            params["layer_type"] = layer_type
        if tags:
            params["tags"] = ",".join(tags)
        if keywords:
            params["keywords"] = ",".join(keywords)
        
        return await self._make_enhanced_request(
            "GET", "/api/v1/memory/memories",
            params=params, user_id=str(user_id) if user_id else None, domain=domain
        )
    
    # ==================== 批量操作 ====================
    
    async def batch_learn(
        self,
        domains: List[str],
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive"
    ) -> List[Dict[str, Any]]:
        """
        批量学习（增强版）
        """
        if not domains:
            return []
        
        # 创建并发任务
        tasks = []
        for domain in domains:
            task = self.learn(
                domain=domain,
                min_case_count=min_case_count,
                min_adoption_rate=min_adoption_rate,
                min_confidence_score=min_confidence_score,
                strategy=strategy
            )
            tasks.append(task)
        
        # 并发执行
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'error': str(result),
                        'success': False,
                        'domain': domains[i]
                    })
                else:
                    processed_results.append({
                        'result': result,
                        'success': True,
                        'domain': domains[i]
                    })
            
            return processed_results
            
        except Exception as e:
            raise TiMEMError(f"Batch learn failed: {str(e)}")
    
    # ==================== 系统监控 ====================
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        获取健康状态（增强版）
        """
        try:
            # 基础健康检查
            health_data = await self._make_enhanced_request("GET", "/api/v1/health")
            
            # 添加增强信息
            enhanced_health = {
                **health_data,
                "enhanced_features": {
                    "connection_pool": self._pool.get_stats() if self._pool else None,
                    "circuit_breaker": self._circuit_breaker.get_state() if self._circuit_breaker else None,
                    "monitoring": self.monitor.get_health_status() if self.monitor else None,
                    "client_stats": self.stats.copy()
                }
            }
            
            return enhanced_health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "enhanced_features": {
                    "connection_pool": self._pool.get_stats() if self._pool else None,
                    "circuit_breaker": self._circuit_breaker.get_state() if self._circuit_breaker else None,
                    "monitoring": self.monitor.get_health_status() if self.monitor else None,
                    "client_stats": self.stats.copy()
                }
            }
    
    def get_client_stats(self) -> Dict[str, Any]:
        """获取客户端统计信息"""
        return {
            "client_stats": self.stats.copy(),
            "connection_pool": self._pool.get_stats() if self._pool else None,
            "circuit_breaker": self._circuit_breaker.get_state() if self._circuit_breaker else None,
            "monitoring": self.monitor.get_health_status() if self.monitor else None
        }
    
    async def reset_connections(self):
        """重置连接"""
        if self._pool:
            await self._pool.reset()
            self.stats["connection_pool_resets"] += 1
            self.logger.info("连接池已重置")
    
    def reset_circuit_breaker(self):
        """重置熔断器"""
        if self._circuit_breaker:
            self._circuit_breaker.reset()
            self.logger.info("熔断器已重置")


# 便利函数
async def create_enhanced_client(
    api_key: str,
    base_url: str = "http://localhost:8001",
    connection_config: Optional[ConnectionConfig] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    enable_monitoring: bool = True,
    verify_ssl: bool = False,
    **kwargs
) -> EnhancedAsyncTiMEMClient:
    """
    创建增强的异步TiMEM客户端
    
    Args:
        api_key: TiMEM API密钥
        base_url: API基础URL
        connection_config: 连接池配置
        circuit_breaker_config: 熔断器配置
        enable_monitoring: 是否启用监控
        verify_ssl: 是否验证SSL证书
        **kwargs: 其他参数
    
    Returns:
        增强的异步TiMEM客户端
    """
    client = EnhancedAsyncTiMEMClient(
        api_key=api_key,
        base_url=base_url,
        connection_config=connection_config,
        circuit_breaker_config=circuit_breaker_config,
        enable_monitoring=enable_monitoring,
        verify_ssl=verify_ssl,
        **kwargs
    )
    
    await client.initialize()
    return client
