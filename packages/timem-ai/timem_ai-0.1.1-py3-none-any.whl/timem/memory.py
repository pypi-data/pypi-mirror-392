"""
简化的 Memory 类，提供更友好的用户接口

提供简化的 API，让用户可以直接使用 `memory = Memory()` 然后调用 `memory.search()` 和 `memory.add()`
"""

import os
from typing import Optional, Dict, Any, List, Union
from .sync_client import TiMEMClient
from .exceptions import TiMEMError


class Memory:
    """
    简化的记忆管理类
    
    提供更简洁的 API 接口，隐藏底层的复杂性。
    
    Example:
        ```python
        memory = Memory()
        
        # 搜索相关记忆
        results = memory.search(query="用户问题", user_id="user123", limit=3)
        
        # 添加对话记忆
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "您好！有什么可以帮您的吗？"}
        ]
        memory.add(messages, user_id="user123")
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化 Memory 实例
        
        Args:
            api_key: TiMEM API 密钥。如果不提供，从环境变量 TIMEM_API_KEY 读取
            base_url: API 基础 URL。如果不提供，从环境变量 TIMEM_BASE_URL 读取，默认为 "http://localhost:8001"
            **kwargs: 其他传递给 TiMEMClient 的参数
        """
        # 从环境变量读取配置，如果没有提供
        api_key = api_key or os.getenv("TIMEM_API_KEY", "")
        base_url = base_url or os.getenv("TIMEM_BASE_URL", "http://localhost:8001")
        
        if not api_key:
            raise ValueError("api_key 必须提供，可以通过参数传入或设置环境变量 TIMEM_API_KEY")
        
        self._client = TiMEMClient(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
    
    def _to_user_id_int(self, user_id: Union[str, int]) -> Optional[int]:
        """
        将 user_id 转换为整数
        
        如果 user_id 是字符串：
        - 如果是纯数字字符串，转换为整数
        - 否则，使用 hash 生成稳定的整数ID（取绝对值确保为正数）
        
        Args:
            user_id: 用户ID（字符串或整数）
        
        Returns:
            整数用户ID，如果无法转换则返回 None
        """
        if isinstance(user_id, int):
            return user_id
        
        if isinstance(user_id, str):
            # 尝试直接转换为整数
            if user_id.isdigit():
                return int(user_id)
            # 对于非数字字符串，使用 hash 生成稳定的整数ID
            # 使用 abs 确保为正数，避免负数ID问题
            return abs(hash(user_id)) % (10 ** 9)  # 限制在合理范围内
        
        return None
    
    def search(
        self,
        query: str,
        user_id: Union[str, int] = "default_user",
        limit: int = 10,
        character_id: Optional[str] = None,
        include_context: bool = False
    ) -> Dict[str, Any]:
        """
        搜索相关记忆 - 使用智能语义搜索
        
        Args:
            query: 搜索查询文本（语义搜索）
            user_id: 用户ID，可以是字符串或整数
            limit: 返回结果数量限制（注意：实际返回数量可能受 score_threshold 影响）
            character_id: 角色ID（可选），用于过滤特定角色的记忆
            include_context: 是否包含上下文信息（session_id, character_id等）
        
        Returns:
            包含搜索结果的字典，格式：
            {
                "results": [
                    {
                        "memory": "记忆内容",
                        "score": 0.95,
                        "id": "记忆ID",
                        "layer": "L1",
                        "metadata": {...},
                        "created_at": "...",
                        ...
                    },
                    ...
                ],
                "total": 10,
                "query": "查询文本"
            }
        """
        # 转换 user_id 为字符串（新API使用字符串类型）
        user_id_str = str(user_id) if user_id else None
        
        try:
            # 调用新的智能搜索API
            result = self._client.search_memories(
                query_text=query,
                user_id=user_id_str,
                character_id=character_id,
                include_context=include_context,
                format="simple",
                search_mode="enhanced_semantic",
                score_threshold=0.5
            )
            
            # 格式化返回结果，匹配用户期望的格式
            formatted_results = []
            memories = result.get("memories", [])
            
            # 如果指定了limit，只取前limit个结果
            if limit and limit > 0:
                memories = memories[:limit]
            
            for mem in memories:
                # 提取记忆内容
                memory_text = mem.get("memory", mem.get("content", ""))
                if not memory_text and isinstance(mem.get("data"), dict):
                    memory_text = mem["data"].get("memory", "")
                
                # 提取相似度分数
                metadata = mem.get("metadata", {})
                score = metadata.get("score", mem.get("score", 0.0))
                
                formatted_results.append({
                    "memory": memory_text,
                    "score": score,
                    "id": mem.get("id"),
                    "layer": mem.get("layer"),
                    "metadata": metadata,
                    "created_at": mem.get("created_at"),
                    "updated_at": mem.get("updated_at"),
                    **{k: v for k, v in mem.items() if k not in [
                        "memory", "content", "score", "id", "layer", 
                        "metadata", "created_at", "updated_at", "data"
                    ]}
                })
            
            return {
                "results": formatted_results,
                "total": result.get("total", len(formatted_results)),
                "query": query
            }
        except Exception as e:
            raise TiMEMError(f"搜索记忆失败: {str(e)}") from e
    
    def add(
        self,
        messages: List[Dict[str, str]],
        user_id: Union[str, int] = "default_user",
        character_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加对话记忆 - 使用智能记忆生成
        
        从对话消息中自动提取并生成记忆。
        
        Args:
            messages: 对话消息列表，格式：[{"role": "user", "content": "..."}, ...]
            user_id: 用户ID，可以是字符串或整数
            character_id: 角色ID（expert_id），可选
            session_id: 会话ID，如果不提供则自动生成
        
        Returns:
            添加结果字典，格式：
            {
                "success": True,
                "memories": [
                    {
                        "id": "记忆ID",
                        "data": {"memory": "记忆内容"},
                        "event": "ADD"
                    },
                    ...
                ],
                "total": 1
            }
        """
        if not messages:
            raise ValueError("messages 不能为空")
        
        if not character_id:
            raise ValueError("character_id 必须提供")
        
        # 转换 user_id 为字符串（新API使用字符串类型）
        user_id_str = str(user_id) if user_id else None
        
        # 如果没有提供 session_id，生成一个基于 user_id 的默认值
        if not session_id:
            import hashlib
            session_id = f"session_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}"
        
        try:
            # 调用新的生成记忆API
            result = self._client.generate_memory(
                character_id=character_id,
                session_id=session_id,
                messages=messages,
                user_id=user_id_str,
                format="compact"
            )
            
            # 处理返回结果
            if isinstance(result, list):
                # compact格式返回数组
                memory_ids = []
                for item in result:
                    memory_id = item.get("id")
                    if memory_id:
                        memory_ids.append(memory_id)
                
                return {
                    "success": True,
                    "memories": result,
                    "memory_id": memory_ids[0] if memory_ids else None,
                    "memory_ids": memory_ids,
                    "total": len(result),
                    "message": f"成功生成 {len(result)} 条记忆"
                }
            else:
                # 兼容其他格式
                return {
                    "success": True,
                    "memories": [result] if result else [],
                    "memory_id": result.get("id") if isinstance(result, dict) else None,
                    "total": 1 if result else 0,
                    "message": "记忆添加成功"
                }
        except Exception as e:
            raise TiMEMError(f"添加记忆失败: {str(e)}") from e
    
    def close(self):
        """
        关闭客户端连接
        
        清理资源，关闭连接池和事件循环等。
        """
        if hasattr(self, '_client') and self._client:
            try:
                self._client.close()
            except Exception:
                pass
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

