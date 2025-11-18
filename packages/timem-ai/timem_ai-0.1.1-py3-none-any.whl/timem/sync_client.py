"""
TiMEM同步客户端（兼容层）

为需要同步调用的用户提供兼容层，内部使用异步实现。
"""

import asyncio
from typing import Optional, Dict, Any, List
from .async_client import TiMEMClient as AsyncTiMEMClient
from .exceptions import TiMEMError, AuthenticationError, APIError, ValidationError


class TiMEMClient:
    """
    TiMEM同步客户端（兼容层）
    
    内部使用异步实现，对外提供同步接口。
    适用于需要同步调用的场景。
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001",
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = False,
        enable_connection_pool: bool = True,
        enable_circuit_breaker: bool = True,
        enable_monitoring: bool = True,
        **kwargs
    ):
        """
        初始化同步TiMEM客户端
        
        Args:
            api_key: TiMEM API密钥
            base_url: API基础URL
            timeout: 请求超时时间
            max_retries: 最大重试次数
            retry_delay: 重试延迟
            verify_ssl: 是否验证SSL证书
            enable_connection_pool: 启用连接池
            enable_circuit_breaker: 启用熔断器
            enable_monitoring: 启用监控
            **kwargs: 其他参数
        """
        self._async_client = AsyncTiMEMClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            verify_ssl=verify_ssl,
            enable_connection_pool=enable_connection_pool,
            enable_circuit_breaker=enable_circuit_breaker,
            enable_monitoring=enable_monitoring,
            **kwargs
        )
        self._loop = None
        self._loop_owner = False  # 标记是否拥有事件循环
    
    def __enter__(self):
        """同步上下文管理器入口"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_owner = True
        self._loop.run_until_complete(self._async_client.__aenter__())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器出口"""
        if self._loop:
            self._loop.run_until_complete(self._async_client.__aexit__(exc_type, exc_val, exc_tb))
            self._loop.close()
            self._loop = None
            self._loop_owner = False
    
    def _run_async(self, coro):
        """运行异步协程"""
        # 检查是否有可用的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                # 如果事件循环已关闭，创建新的
                loop = None
        except RuntimeError:
            # 如果没有事件循环，创建新的
            loop = None
        
        # 如果没有可用的事件循环，创建新的并保存
        if loop is None:
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                self._loop_owner = True
            asyncio.set_event_loop(self._loop)
            loop = self._loop
        
        # 运行协程
        try:
            return loop.run_until_complete(coro)
        except RuntimeError as e:
            # 如果事件循环出现问题，尝试重新创建
            if "Event loop is closed" in str(e) or "This event loop is already running" in str(e):
                if self._loop_owner and self._loop:
                    try:
                        self._loop.close()
                    except:
                        pass
                self._loop = asyncio.new_event_loop()
                self._loop_owner = True
                asyncio.set_event_loop(self._loop)
                return self._loop.run_until_complete(coro)
            raise
    
    # ==================== 经验学习引擎API ====================
    
    def learn(
        self,
        domain: str = "general",
        feedback_cases: Optional[List[Dict[str, Any]]] = None,
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """学习生成经验规则（同步版）"""
        return self._run_async(
            self._async_client.learn(
                domain=domain,
                feedback_cases=feedback_cases,
                min_case_count=min_case_count,
                min_adoption_rate=min_adoption_rate,
                min_confidence_score=min_confidence_score,
                strategy=strategy,
                user_id=user_id
            )
        )
    
    def recall(
        self,
        context: Dict[str, Any],
        domain: str = "general",
        top_k: int = 5,
        min_confidence: float = 0.5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """召回相关经验规则（同步版）"""
        return self._run_async(
            self._async_client.recall(
                context=context,
                domain=domain,
                top_k=top_k,
                min_confidence=min_confidence,
                user_id=user_id
            )
        )
    
    def batch_learn(
        self,
        domains: List[str],
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive"
    ) -> List[Dict[str, Any]]:
        """批量学习（同步版）"""
        return self._run_async(
            self._async_client.batch_learn(
                domains=domains,
                min_case_count=min_case_count,
                min_adoption_rate=min_adoption_rate,
                min_confidence_score=min_confidence_score,
                strategy=strategy
            )
        )
    
    # ==================== 记忆管理API ====================
    
    def add_memory(
        self,
        user_id: int,
        domain: str,
        content: Dict[str, Any],
        layer_type: str = "L1",
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """添加记忆（同步版）"""
        return self._run_async(
            self._async_client.add_memory(
                user_id=user_id,
                domain=domain,
                content=content,
                layer_type=layer_type,
                tags=tags,
                keywords=keywords
            )
        )
    
    def search_memory(
        self,
        user_id: Optional[int] = None,
        domain: Optional[str] = None,
        layer_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """搜索记忆（同步版）"""
        return self._run_async(
            self._async_client.search_memory(
                user_id=user_id,
                domain=domain,
                layer_type=layer_type,
                tags=tags,
                keywords=keywords,
                limit=limit,
                offset=offset
            )
        )
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """获取记忆（同步版）"""
        return self._run_async(self._async_client.get_memory(memory_id))
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """更新记忆（同步版）"""
        return self._run_async(
            self._async_client.update_memory(
                memory_id=memory_id,
                content=content,
                tags=tags,
                keywords=keywords
            )
        )
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """删除记忆（同步版）"""
        return self._run_async(self._async_client.delete_memory(memory_id))
    
    def batch_add_memories(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量添加记忆（同步版）"""
        return self._run_async(
            self._async_client.batch_add_memories(memories)
        )
    
    def generate_memory(
        self,
        character_id: str,
        session_id: str,
        messages: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        format: str = "compact"
    ) -> List[Dict[str, Any]]:
        """
        生成记忆（同步版）- 使用 compact 格式
        
        Args:
            character_id: 角色ID（expert_id）
            session_id: 会话ID
            messages: 对话消息列表
            user_id: 用户ID（可选）
            format: 响应格式，默认为 "compact"
        
        Returns:
            compact格式响应数组
        """
        return self._run_async(
            self._async_client.generate_memory(
                character_id=character_id,
                session_id=session_id,
                messages=messages,
                user_id=user_id,
                format=format
            )
        )
    
    def search_memories(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        character_id: Optional[str] = None,
        include_context: bool = False,
        format: str = "simple",
        search_mode: str = "enhanced_semantic",
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        智能搜索记忆（同步版）- 使用 simple 格式
        
        Args:
            query_text: 查询文本（语义搜索）
            user_id: 用户ID（可选）
            character_id: 角色ID（可选）
            include_context: 是否包含上下文信息
            format: 响应格式，默认为 "simple"
            search_mode: 搜索模式，默认为 "enhanced_semantic"
            score_threshold: 相似度分数阈值，默认 0.5
        
        Returns:
            simple格式响应对象
        """
        return self._run_async(
            self._async_client.search_memories(
                query_text=query_text,
                user_id=user_id,
                character_id=character_id,
                include_context=include_context,
                format=format,
                search_mode=search_mode,
                score_threshold=score_threshold
            )
        )
    
    # ==================== 用户画像API ====================
    
    def compute_profile(
        self,
        user_id: int,
        domain: str,
        source_memory_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """计算用户画像（同步版）"""
        return self._run_async(
            self._async_client.compute_profile(
                user_id=user_id,
                domain=domain,
                source_memory_ids=source_memory_ids
            )
        )
    
    def get_profile(
        self,
        user_id: int,
        domain: str
    ) -> Dict[str, Any]:
        """获取用户画像（同步版）"""
        return self._run_async(
            self._async_client.get_profile(user_id=user_id, domain=domain)
        )
    
    def search_users(
        self,
        criteria: Dict[str, Any],
        domain: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """搜索用户（同步版）"""
        return self._run_async(
            self._async_client.search_users(
                criteria=criteria,
                domain=domain,
                limit=limit
            )
        )
    
    # ==================== 系统API ====================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查（同步版）"""
        return self._run_async(self._async_client.health_check())
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态（同步版）"""
        return self._run_async(self._async_client.get_system_status())
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态（同步版）"""
        return self._run_async(self._async_client.get_health_status())
    
    def get_client_stats(self) -> Dict[str, Any]:
        """获取客户端统计（同步版）"""
        return self._async_client.get_client_stats()
    
    def reset_connections(self):
        """重置连接（同步版）"""
        return self._run_async(self._async_client.reset_connections())
    
    def reset_circuit_breaker(self):
        """重置熔断器（同步版）"""
        return self._async_client.reset_circuit_breaker()
    
    def close(self):
        """
        关闭客户端连接
        
        清理资源，关闭事件循环和异步客户端。
        """
        # 关闭异步客户端
        if self._async_client:
            try:
                if self._loop and not self._loop.is_closed():
                    self._loop.run_until_complete(self._async_client.close())
            except Exception:
                pass
        
        # 关闭事件循环
        if self._loop_owner and self._loop and not self._loop.is_closed():
            try:
                self._loop.close()
            except Exception:
                pass
        
        self._loop = None
        self._loop_owner = False
    
    def __del__(self):
        """析构函数，确保资源释放"""
        try:
            self.close()
        except Exception:
            pass


# 便利函数
def create_sync_client(
    api_key: str,
    base_url: str = "http://localhost:8001",
    enable_enhanced_features: bool = True,
    **kwargs
) -> TiMEMClient:
    """
    创建同步TiMEM客户端
    
    Args:
        api_key: TiMEM API密钥
        base_url: API基础URL
        enable_enhanced_features: 是否启用增强功能
        **kwargs: 其他参数
    
    Returns:
        同步TiMEM客户端
    """
    return TiMEMClient(
        api_key=api_key,
        base_url=base_url,
        enable_connection_pool=enable_enhanced_features,
        enable_circuit_breaker=enable_enhanced_features,
        enable_monitoring=enable_enhanced_features,
        **kwargs
    )
