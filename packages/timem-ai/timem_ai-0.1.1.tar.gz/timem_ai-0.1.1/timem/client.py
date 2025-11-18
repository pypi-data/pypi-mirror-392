"""
TiMEM Python SDK Client

Main client class for interacting with the TiMEM API.
"""

import httpx
from typing import Optional, Dict, Any, List
from .exceptions import TiMEMError, AuthenticationError, APIError, ValidationError


class TiMEMClient:
    """
    Main client for interacting with the TiMEM API.
    
    This client provides methods for:
    - Learning from feedback (learn)
    - Recalling rules (recall)
    - Adding memories (add_memory)
    - Searching memories (search_memory)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001",
        timeout: float = 60.0,
        verify_ssl: bool = False,  # 默认不验证SSL，简化使用
        **kwargs
    ):
        """
        Initialize the TiMEM client.
        
        Args:
            api_key: Your TiMEM API key
            base_url: Base URL for the API (default: http://localhost:8001)
            timeout: Request timeout in seconds (default: 60.0)
            verify_ssl: Whether to verify SSL certificates (default: False)
            **kwargs: Additional arguments passed to httpx.Client
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Set up default headers
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"timem-python/{__import__('timem').__version__}"
        }
        
        # Create httpx client with configurable SSL verification
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,  # 使用verify_ssl参数
            **kwargs
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
            TiMEMError: For other client errors
        """
        try:
            response = self.client.request(
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
            
        except httpx.RequestError as e:
            raise TiMEMError(f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            raise APIError(f"HTTP {e.response.status_code} error: {e.response.text}")
    
    # ==================== Experience Learning Engine APIs ====================
    
    def learn(
        self,
        domain: str = "general",
        feedback_cases: Optional[List[Dict[str, Any]]] = None,
        min_case_count: int = 3,
        min_adoption_rate: float = 0.6,
        min_confidence_score: float = 0.5,
        strategy: str = "adaptive"
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
            self._make_request("POST", "/api/v1/rules/feedback/collect", data=collect_data)
        
        # Trigger learning
        data = {
            "domain": domain,
            "min_case_count": min_case_count,
            "min_adoption_rate": min_adoption_rate,
            "min_confidence_score": min_confidence_score
        }
        
        params = {"summarization_strategy": strategy}
        
        return self._make_request("POST", "/api/v1/rules/learn-with-llm", data=data, params=params)
    
    def recall(
        self,
        context: Dict[str, Any],
        domain: str = "general",
        top_k: int = 5,
        min_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Recall relevant experience rules based on context.
        
        Args:
            context: Context for rule matching (e.g., job_title, issue_type, section)
            domain: Business domain
            top_k: Number of top rules to return
            min_confidence: Minimum confidence threshold
            
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
        
        return self._make_request("POST", "/api/v1/rules/rule-call", data=data)
    
    # ==================== Memory Management APIs ====================
    
    def add_memory(
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
            content: Memory content
            layer_type: Memory layer (L1-L5)
            tags: Optional tags for categorization
            keywords: Optional keywords for search
            
        Returns:
            Created memory information
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
        
        return self._make_request("POST", "/api/v1/memory/memories", data=data)
    
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
        
        return self._make_request("GET", "/api/v1/memory/memories", params=params)
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory information
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")
        
        return self._make_request("GET", f"/api/v1/memory/memories/{memory_id}")
    
    def update_memory(
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
        
        return self._make_request("PUT", f"/api/v1/memory/memories/{memory_id}", data=data)
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Deletion result
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")
        
        return self._make_request("DELETE", f"/api/v1/memory/memories/{memory_id}")
    
    # ==================== User Profile APIs ====================
    
    def compute_profile(
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
        
        return self._make_request("POST", "/api/v1/user-profile/compute", data=data)
    
    def get_profile(
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
        
        return self._make_request("GET", "/api/v1/user-profile/profiles", params=params)
    
    def search_users(
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
        
        return self._make_request("POST", "/api/v1/user-profile/search", data=data)
    
    # ==================== System APIs ====================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the TiMEM API.
        
        Returns:
            Health status
        """
        try:
            response = self.client.get("/api/v1/health")
            return response.json()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and module information.
        
        Returns:
            System status
        """
        return self._make_request("GET", "/api/v1/status")
