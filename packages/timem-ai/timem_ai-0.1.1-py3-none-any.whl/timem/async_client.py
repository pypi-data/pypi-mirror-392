"""
TiMEM Python SDK Async Client

Async client class for interacting with the TiMEM API with full async support.
"""

import asyncio
import httpx
import time
import logging
from typing import Optional, Dict, Any, List
from .exceptions import TiMEMError, AuthenticationError, APIError, ValidationError, ConnectionError, CircuitBreakerError
from .connection_pool import ConnectionPool, ConnectionConfig, get_connection_pool
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from .monitoring import PerformanceMonitor, get_global_monitor


class TiMEMClient:
    """
    TiMEM API client with enterprise-grade features.
    
    This client provides methods for:
    - Learning from feedback (learn)
    - Recalling rules (recall)
    - Adding memories (add_memory)
    - Searching memories (search_memory)
    - Connection pooling, circuit breaker, monitoring
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001",
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = False,  # 默认不验证SSL，简化使用
        # 增强功能参数
        enable_connection_pool: bool = True,
        enable_circuit_breaker: bool = True,
        enable_monitoring: bool = True,
        connection_config: Optional[ConnectionConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        **kwargs
    ):
        """
        Initialize the TiMEM client.
        
        Args:
            api_key: Your TiMEM API key
            base_url: Base URL for the API (default: http://localhost:8001)
            timeout: Request timeout in seconds (default: 60.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
            verify_ssl: Whether to verify SSL certificates (default: False)
            enable_connection_pool: Enable connection pooling (default: True)
            enable_circuit_breaker: Enable circuit breaker (default: True)
            enable_monitoring: Enable performance monitoring (default: True)
            connection_config: Connection pool configuration
            circuit_breaker_config: Circuit breaker configuration
            **kwargs: Additional arguments passed to httpx.AsyncClient
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        # 保存配置供后续使用
        self._connection_config = connection_config
        self._circuit_breaker_config = circuit_breaker_config
        
        # 增强功能配置
        self.enable_connection_pool = enable_connection_pool
        self.enable_circuit_breaker = enable_circuit_breaker
        self.enable_monitoring = enable_monitoring
        
        # 连接池和熔断器（延迟初始化）
        self._pool: Optional[ConnectionPool] = None
        self._circuit_breaker: Optional[CircuitBreaker] = None
        self._monitor: Optional[PerformanceMonitor] = None
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_breaker_trips": 0,
            "connection_pool_resets": 0
        }
        
        # 日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 传统httpx客户端（作为备用）
        headers = {
            "accept": "application/json",
            "X-API-Key": api_key,  # TiMEM Engine 使用 X-API-Key 头
            "Content-Type": "application/json",
            "User-Agent": f"timem-python-async/{__import__('timem').__version__}"
        }
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,
            **kwargs
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_enhanced_features()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _initialize_enhanced_features(self):
        """初始化增强功能"""
        try:
            # 初始化连接池
            if self.enable_connection_pool:
                self._pool = await get_connection_pool(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    config=self._connection_config,
                    verify_ssl=self.verify_ssl
                )
                self.logger.info("连接池已初始化")
            
            # 初始化熔断器
            if self.enable_circuit_breaker:
                self._circuit_breaker = get_circuit_breaker(
                    name=f"timem_{self.base_url}",
                    config=self._circuit_breaker_config,
                    fallback_func=self._fallback_handler
                )
                self.logger.info("熔断器已初始化")
            
            # 初始化监控
            if self.enable_monitoring:
                self._monitor = get_global_monitor()
                self.logger.info("监控已初始化")
                
        except Exception as e:
            self.logger.warning(f"增强功能初始化失败: {str(e)}")
    
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
    
    async def close(self):
        """Close the async HTTP client and release all resources."""
        # 关闭连接池
        if self._pool:
            await self._pool.close()
            self._pool = None
        
        # 关闭httpx客户端
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()
            self.client = None
        
        self.logger.info("TiMEM客户端已关闭")
    
    async def _make_request(
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
        Make an async HTTP request to the API with enhanced features.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            user_id: User ID for monitoring
            domain: Domain for monitoring
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
            TiMEMError: For other client errors
        """
        start_time = time.time()
        success = False
        error_message = None
        status_code = 200
        
        try:
            # 使用增强功能
            if self._pool and self._circuit_breaker:
                # 使用连接池和熔断器
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
            else:
                # 使用传统方式
                return await self._make_traditional_request(
                    method, endpoint, data, params, **kwargs
                )
                
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
            if self._monitor:
                self._monitor.record_request(
                    method=method,
                    endpoint=endpoint,
                    duration=duration,
                    status_code=status_code,
                    success=success,
                    user_id=user_id,
                    domain=domain,
                    error_message=error_message
                )
    
    async def _make_traditional_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """传统请求方式（备用）"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    params=params,
                    **kwargs
                )
                
                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                
                # Handle other HTTP errors
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_message = error_data.get('message', error_data.get('detail', f'HTTP {response.status_code} error'))
                    except:
                        error_message = f'HTTP {response.status_code} error'
                    raise APIError(error_message, status_code=response.status_code)
                
                # Return JSON response
                return response.json()
                
            except (httpx.RequestError, httpx.HTTPStatusError, APIError, AuthenticationError) as e:
                last_exception = e
                
                # Don't retry authentication errors
                if isinstance(e, AuthenticationError):
                    raise e
                
                # Don't retry on last attempt
                if attempt == self.max_retries:
                    break
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # Re-raise the last exception
        if isinstance(last_exception, httpx.RequestError):
            raise TiMEMError(f"Request failed after {self.max_retries + 1} attempts: {str(last_exception)}")
        elif isinstance(last_exception, httpx.HTTPStatusError):
            raise APIError(f"HTTP {last_exception.response.status_code} error after {self.max_retries + 1} attempts: {last_exception.response.text}")
        else:
            raise last_exception
    
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
        Learn from feedback cases to generate experience rules.
        
        Uses LLM to analyze feedback cases and generate actionable rules.
        No clustering - direct LLM call for more intelligent rule generation.
        
        If feedback_cases provided, will first collect them then trigger learning.
        If not provided, will learn from existing unprocessed cases in the system.
        
        Args:
            domain: Business domain (e.g., "aicv", "education", "general")
            feedback_cases: Optional feedback cases to collect before learning
            min_case_count: Minimum number of cases required to generate a rule
            min_adoption_rate: Minimum adoption rate threshold (0-1)
            min_confidence_score: Minimum confidence score threshold (0-1)
            strategy: Summarization strategy ("single", "cluster", "adaptive")
            user_id: Optional user identifier for monitoring
            
        Returns:
            Learning result with generated rules
        """
        if not domain:
            raise ValidationError("Domain is required")
        
        # If feedback cases provided, collect them first
        if feedback_cases:
            import datetime
            batch_id = f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            collect_data = {
                "batch_id": batch_id,
                "feedback_cases": feedback_cases
            }
            
            # Collect feedback
            await self._make_request("POST", "/api/v1/rules/feedback/collect", data=collect_data)
        
        # Trigger learning
        data = {
            "domain": domain,
            "min_case_count": min_case_count,
            "min_adoption_rate": min_adoption_rate,
            "min_confidence_score": min_confidence_score
        }
        
        params = {"summarization_strategy": strategy}
        
        return await self._make_request("POST", "/api/v1/rules/learn-with-llm", data=data, params=params, user_id=user_id, domain=domain)
    
    async def recall(
        self,
        context: Dict[str, Any],
        domain: str = "general",
        top_k: int = 5,
        min_confidence: float = 0.5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recall relevant experience rules based on context.
        
        Args:
            context: Context for rule matching (e.g., job_title, issue_type, section)
            domain: Business domain
            top_k: Number of top rules to return
            min_confidence: Minimum confidence threshold
            user_id: Optional user identifier for monitoring
            
        Returns:
            Recalled rules with relevance scores
        """
        if not context:
            raise ValidationError("Context is required")
        
        data = {
            "domain": domain,
            "context": context,
            "top_k": top_k,
            "min_confidence": min_confidence
        }
        
        return await self._make_request("POST", "/api/v1/rules/rule-call", data=data, user_id=user_id, domain=domain)
    
    async def batch_learn(
        self,
        domains: List[str],
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive"
    ) -> List[Dict[str, Any]]:
        """
        Learn from feedback cases for multiple domains concurrently.
        
        Args:
            domains: List of business domains
            min_case_count: Minimum number of cases required to generate a rule
            min_adoption_rate: Minimum adoption rate threshold (0-1)
            min_confidence_score: Minimum confidence score threshold (0-1)
            strategy: Summarization strategy
            
        Returns:
            List of learning results for each domain
        """
        if not domains:
            return []
        
        # Create tasks for concurrent execution
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
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
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
        Add a memory to the TiMEM system.
        
        Args:
            user_id: User identifier
            domain: Business domain
            content: Memory content (will be converted to JSON string)
            layer_type: Memory layer (L1-L5)
            tags: Optional tags for categorization
            keywords: Optional keywords for search
            
        Returns:
            Created memory information
        """
        if not content:
            raise ValidationError("Memory content is required")
        
        # 将content转换为字符串格式（API期望字符串类型）
        import json
        content_str = json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else str(content)
        
        # 确保domain是有效值：aicv, education, consulting, customer_service, general
        valid_domains = ['aicv', 'education', 'consulting', 'customer_service', 'general']
        if domain not in valid_domains:
            domain = 'general'  # 默认使用general
        
        # 注意：TiMEM Engine的API中，memory_type和layer使用相同的值（L1-L5）
        data = {
            "user_id": str(user_id),  # API期望字符串类型
            "layer": layer_type,  # 记忆层级
            "memory_type": layer_type,  # memory_type也使用相同的值（L1-L5）
            "content": content_str,
            "domain": domain,
            "tags": tags or [],
            "keywords": keywords or []
        }
        
        # 调试日志
        self.logger.debug(f"[add_memory] 发送数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        return await self._make_request("POST", "/api/v1/memory/create", data=data)
    
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
        Search memories in the TiMEM system.
        
        Args:
            user_id: Optional user filter
            domain: Optional domain filter
            layer_type: Optional layer type filter
            tags: Optional tags filter
            keywords: Optional keywords filter
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Search results with memories
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
        
        return await self._make_request("GET", "/api/v1/memory/query", params=params)
    
    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory information
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")
        
        return await self._make_request("GET", f"/api/v1/memory/{memory_id}")
    
    async def update_memory(
        self,
        memory_id: str,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id: Memory identifier
            content: Updated content
            tags: Updated tags
            keywords: Updated keywords
            
        Returns:
            Update result
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")
        
        data = {}
        if content is not None:
            data["content"] = content
        if tags is not None:
            data["tags"] = tags
        if keywords is not None:
            data["keywords"] = keywords
        
        return await self._make_request("PUT", f"/api/v1/memory/{memory_id}", data=data)
    
    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Deletion result
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")
        
        return await self._make_request("DELETE", f"/api/v1/memory/{memory_id}")
    
    async def batch_add_memories(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add multiple memories concurrently.
        
        Args:
            memories: List of memory dictionaries (user_id, domain, content, etc.)
            
        Returns:
            List of creation results
        """
        if not memories:
            return []
        
        # Create tasks for concurrent execution
        tasks = []
        for mem in memories:
            task = self.add_memory(
                user_id=mem.get('user_id'),
                domain=mem.get('domain'),
                content=mem.get('content'),
                layer_type=mem.get('layer_type', 'L1'),
                tags=mem.get('tags'),
                keywords=mem.get('keywords')
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'error': str(result),
                        'success': False,
                        'index': i
                    })
                else:
                    processed_results.append({
                        'result': result,
                        'success': True,
                        'index': i
                    })
            
            return processed_results
            
        except Exception as e:
            raise TiMEMError(f"Batch add memories failed: {str(e)}")
    
    # ==================== 对话记忆生成和智能搜索 API ====================
    
    async def generate_memory(
        self,
        character_id: str,
        session_id: str,
        messages: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        format: str = "compact"
    ) -> List[Dict[str, Any]]:
        """
        生成记忆 - 使用 compact 格式（简化响应）
        
        从对话消息中自动提取并生成记忆。
        
        Args:
            character_id: 角色ID（expert_id）
            session_id: 会话ID
            messages: 对话消息列表 [{"role": "user/assistant", "content": "..."}]
            user_id: 用户ID（可选）
            format: 响应格式，默认为 "compact"
        
        Returns:
            compact格式响应：数组格式
            [
                {
                    "id": "记忆ID",
                    "data": {"memory": "记忆内容"},
                    "event": "ADD"
                }
            ]
        """
        if not character_id:
            raise ValidationError("character_id 必须提供")
        if not session_id:
            raise ValidationError("session_id 必须提供")
        if not messages:
            raise ValidationError("messages 不能为空")
        
        payload = {
            "expert_id": character_id,
            "session_id": session_id,
            "messages": messages,
            "format": format
        }
        if user_id:
            payload["user_id"] = user_id
        
        result = await self._make_request("POST", "/api/v1/memory/", data=payload)
        
        # compact格式返回数组
        if isinstance(result, list):
            return result
        # 如果不是数组，尝试从响应中提取
        if isinstance(result, dict):
            return result.get("data", result.get("memories", [result]))
        return [result] if result else []
    
    async def search_memories(
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
        智能搜索记忆 - 使用 simple 格式（简化响应）
        
        基于语义搜索相关记忆。
        
        Args:
            query_text: 查询文本（语义搜索）
            user_id: 用户ID（可选）
            character_id: 角色ID（可选）
            include_context: 是否包含上下文信息（session_id, character_id等）
            format: 响应格式，默认为 "simple"
            search_mode: 搜索模式，默认为 "enhanced_semantic"
            score_threshold: 相似度分数阈值，默认 0.5
        
        Returns:
            simple格式响应：对象格式
            {
                "memories": [
                    {
                        "id": "记忆ID",
                        "memory": "记忆内容",
                        "layer": "L1",
                        "metadata": {
                            "score": 0.85,  # 相似度分数
                            "session_id": "...",  # include_context=true时包含
                            "character_id": "..."  # include_context=true时包含
                        },
                        "created_at": "...",
                        "updated_at": "..."
                    }
                ],
                "total": 10
            }
        """
        if not query_text:
            raise ValidationError("query_text 必须提供")
        
        payload = {
            "query_text": query_text,
            "format": format,
            "include_context": include_context,
            "config": {
                "search_mode": search_mode,
                "score_threshold": score_threshold
            }
        }
        if user_id:
            payload["user_id"] = user_id
        if character_id:
            payload["character_id"] = character_id
        
        result = await self._make_request("POST", "/api/v1/memory/search", data=payload)
        
        # 处理响应
        if result is None:
            return {"memories": [], "total": 0}
        
        # 如果已经是期望的格式，直接返回
        if isinstance(result, dict) and "memories" in result:
            return result
        
        # 尝试转换格式
        if isinstance(result, list):
            return {"memories": result, "total": len(result)}
        
        # 如果返回的是单个对象，包装成列表
        return {"memories": [result] if result else [], "total": 1 if result else 0}
    
    # ==================== User Profile APIs ====================
    
    async def compute_profile(
        self,
        user_id: int,
        domain: str,
        source_memory_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compute user profile from L5 level memories.
        
        Args:
            user_id: User identifier
            domain: Business domain
            source_memory_ids: Optional specific memory IDs to use
            
        Returns:
            Computed profile information
        """
        data = {
            "user_id": user_id,
            "domain": domain
        }
        
        if source_memory_ids:
            data["source_memory_ids"] = source_memory_ids
        
        return await self._make_request("POST", "/api/v1/user-profile/compute", data=data)
    
    async def get_profile(
        self,
        user_id: int,
        domain: str
    ) -> Dict[str, Any]:
        """
        Get user profile.
        
        Args:
            user_id: User identifier
            domain: Business domain
            
        Returns:
            User profile information
        """
        params = {
            "user_id": user_id,
            "domain": domain
        }
        
        return await self._make_request("GET", "/api/v1/user-profile/profiles", params=params)
    
    async def search_users(
        self,
        criteria: Dict[str, Any],
        domain: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search users by profile criteria.
        
        Args:
            criteria: Search criteria (e.g., preferences, behavior patterns)
            domain: Optional domain filter
            limit: Maximum number of results
            
        Returns:
            Matching users
        """
        if not criteria:
            raise ValidationError("Search criteria is required")
        
        data = {
            "criteria": criteria,
            "limit": limit
        }
        
        if domain:
            data["domain"] = domain
        
        return await self._make_request("POST", "/api/v1/user-profile/search", data=data)
    
    # ==================== System APIs ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the TiMEM API.
        
        Returns:
            Health status
        """
        try:
            response = await self.client.get("/api/v1/health")
            return response.json()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and module information.
        
        Returns:
            System status
        """
        return await self._make_request("GET", "/api/v1/status")
    
    # ==================== 增强功能方法 ====================
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        获取健康状态（增强版）
        """
        try:
            # 基础健康检查
            health_data = await self._make_request("GET", "/api/v1/health")
            
            # 添加增强信息
            enhanced_health = {
                **health_data,
                "enhanced_features": {
                    "connection_pool": self._pool.get_stats() if self._pool else None,
                    "circuit_breaker": self._circuit_breaker.get_state() if self._circuit_breaker else None,
                    "monitoring": self._monitor.get_health_status() if self._monitor else None,
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
                    "monitoring": self._monitor.get_health_status() if self._monitor else None,
                    "client_stats": self.stats.copy()
                }
            }
    
    def get_client_stats(self) -> Dict[str, Any]:
        """获取客户端统计信息"""
        return {
            "client_stats": self.stats.copy(),
            "connection_pool": self._pool.get_stats() if self._pool else None,
            "circuit_breaker": self._circuit_breaker.get_state() if self._circuit_breaker else None,
            "monitoring": self._monitor.get_health_status() if self._monitor else None
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


# ==================== Convenience Functions ====================

async def create_client(
    api_key: str,
    base_url: str = "http://localhost:8001",
    enable_enhanced_features: bool = True,
    **kwargs
) -> TiMEMClient:
    """
    创建TiMEM客户端（简化版）
    
    Args:
        api_key: TiMEM API密钥
        base_url: API基础URL
        enable_enhanced_features: 是否启用增强功能
        **kwargs: 其他参数
    
    Returns:
        TiMEM客户端
    """
    if enable_enhanced_features:
        return TiMEMClient(
            api_key=api_key,
            base_url=base_url,
            enable_connection_pool=True,
            enable_circuit_breaker=True,
            enable_monitoring=True,
            **kwargs
        )
    else:
        return TiMEMClient(
            api_key=api_key,
            base_url=base_url,
            enable_connection_pool=False,
            enable_circuit_breaker=False,
            enable_monitoring=False,
            **kwargs
        )


async def learn_async(
    api_key: str,
    domain: str = "general",
    min_case_count: int = 3,
    min_adoption_rate: float = 0.6,
    min_confidence_score: float = 0.5,
    strategy: str = "adaptive",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to learn from feedback asynchronously.
    
    Args:
        api_key: Your TiMEM API key
        domain: Business domain
        min_case_count: Minimum number of cases required
        min_adoption_rate: Minimum adoption rate threshold
        min_confidence_score: Minimum confidence score threshold
        strategy: Summarization strategy
        **kwargs: Additional arguments for AsyncTiMEMClient
        
    Returns:
        Learning result
    """
    async with TiMEMClient(api_key=api_key, **kwargs) as client:
        return await client.learn(
            domain=domain,
            min_case_count=min_case_count,
            min_adoption_rate=min_adoption_rate,
            min_confidence_score=min_confidence_score,
            strategy=strategy
        )


async def recall_async(
    api_key: str,
    context: Dict[str, Any],
    domain: str = "general",
    top_k: int = 5,
    min_confidence: float = 0.5,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to recall rules asynchronously.
    
    Args:
        api_key: Your TiMEM API key
        context: Context for rule matching
        domain: Business domain
        top_k: Number of top rules to return
        min_confidence: Minimum confidence threshold
        **kwargs: Additional arguments for AsyncTiMEMClient
        
    Returns:
        Recalled rules
    """
    async with TiMEMClient(api_key=api_key, **kwargs) as client:
        return await client.recall(
            context=context,
            domain=domain,
            top_k=top_k,
            min_confidence=min_confidence
        )
