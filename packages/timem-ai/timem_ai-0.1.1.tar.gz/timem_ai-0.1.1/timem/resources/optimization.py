from typing import Dict, Any, Optional, List, AsyncGenerator
from ..types.optimization import OptimizationRequest, OptimizationResponse

class Optimization:
    """优化相关API"""
    
    def __init__(self, client):
        self.client = client
    
    async def optimize(
        self,
        request: OptimizationRequest
    ) -> OptimizationResponse:
        """
        优化简历内容
        
        Args:
            request: 优化请求
            
        Returns:
            优化结果
        """
        data = request.dict()
        response = await self.client._request("POST", "/optimization/optimize", data)
        return OptimizationResponse(**response)
    
    async def get_optimization_result(self, optimization_id: str) -> OptimizationResponse:
        """
        获取优化结果
        
        Args:
            optimization_id: 优化ID
            
        Returns:
            优化结果
        """
        response = await self.client._request("GET", f"/optimization/{optimization_id}")
        return OptimizationResponse(**response)
    
    async def stream_optimization(
        self,
        request: OptimizationRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式优化
        
        Args:
            request: 优化请求
            
        Yields:
            优化进度更新
        """
        data = request.dict()
        
        async with self.client._client.stream(
            "POST",
            f"{self.client.api_base}/optimization/stream",
            json=data
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
