"""
TiMEM熔断器

提供企业级熔断器功能，支持自动故障检测、熔断恢复、降级策略等。
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
from .exceptions import TiMEMError, CircuitBreakerError


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5          # 失败阈值
    recovery_timeout: float = 60.0      # 恢复超时时间（秒）
    success_threshold: int = 3          # 半开状态下的成功阈值
    timeout: float = 30.0               # 请求超时时间
    max_requests: int = 100             # 最大请求数（用于统计）
    error_rate_threshold: float = 0.5   # 错误率阈值


class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback_func: Optional[Callable] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback_func = fallback_func
        
        # 状态管理
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.request_count = 0
        self.error_count = 0
        
        # 日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.{name}")
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opened_count": 0,
            "fallback_calls": 0
        }
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        if self.state != CircuitState.OPEN:
            return False
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """处理成功请求"""
        self.failure_count = 0
        self.success_count += 1
        self.stats["successful_requests"] += 1
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                self.logger.info(f"熔断器 {self.name} 已恢复为正常状态")
    
    def _on_failure(self):
        """处理失败请求"""
        self.failure_count += 1
        self.error_count += 1
        self.last_failure_time = time.time()
        self.stats["failed_requests"] += 1
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.stats["circuit_opened_count"] += 1
                self.logger.warning(f"熔断器 {self.name} 已打开，失败次数: {self.failure_count}")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.logger.warning(f"熔断器 {self.name} 在半开状态下失败，重新打开")
    
    def _get_error_rate(self) -> float:
        """获取错误率"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count
    
    def _should_open_circuit(self) -> bool:
        """检查是否应该打开熔断器"""
        # 基于失败次数
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # 基于错误率
        if (self.request_count >= self.config.max_requests and 
            self._get_error_rate() >= self.config.error_rate_threshold):
            return True
        
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数调用，带熔断保护"""
        self.stats["total_requests"] += 1
        self.request_count += 1
        
        # 检查熔断器状态
        if self.state == CircuitState.OPEN:
            if not self._should_attempt_reset():
                # 调用降级函数
                if self.fallback_func:
                    self.stats["fallback_calls"] += 1
                    self.logger.info(f"熔断器 {self.name} 处于打开状态，调用降级函数")
                    return await self._call_fallback(*args, **kwargs)
                else:
                    raise CircuitBreakerError(f"熔断器 {self.name} 处于打开状态")
            else:
                # 尝试重置为半开状态
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"熔断器 {self.name} 尝试重置为半开状态")
        
        # 执行函数调用
        try:
            start_time = time.time()
            
            # 设置超时
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, func, *args, **kwargs),
                    timeout=self.config.timeout
                )
            
            # 记录成功
            self._on_success()
            
            duration = time.time() - start_time
            self.logger.debug(f"熔断器 {self.name} 调用成功: {duration:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.warning(f"熔断器 {self.name} 调用超时")
            self._on_failure()
            raise CircuitBreakerError(f"熔断器 {self.name} 调用超时")
            
        except Exception as e:
            self.logger.warning(f"熔断器 {self.name} 调用失败: {str(e)}")
            self._on_failure()
            
            # 检查是否应该打开熔断器
            if self._should_open_circuit():
                self.state = CircuitState.OPEN
                self.stats["circuit_opened_count"] += 1
                self.logger.warning(f"熔断器 {self.name} 因错误率过高而打开")
            
            # 如果是熔断器打开状态，调用降级函数
            if self.state == CircuitState.OPEN and self.fallback_func:
                self.stats["fallback_calls"] += 1
                self.logger.info(f"熔断器 {self.name} 调用降级函数")
                return await self._call_fallback(*args, **kwargs)
            
            raise
    
    async def _call_fallback(self, *args, **kwargs) -> Any:
        """调用降级函数"""
        if not self.fallback_func:
            raise CircuitBreakerError(f"熔断器 {self.name} 没有配置降级函数")
        
        try:
            if asyncio.iscoroutinefunction(self.fallback_func):
                return await self.fallback_func(*args, **kwargs)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self.fallback_func, *args, **kwargs
                )
        except Exception as e:
            self.logger.error(f"降级函数调用失败: {str(e)}")
            raise CircuitBreakerError(f"降级函数调用失败: {str(e)}")
    
    def get_state(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self._get_error_rate(),
            "last_failure_time": self.last_failure_time,
            "stats": self.stats.copy(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "max_requests": self.config.max_requests,
                "error_rate_threshold": self.config.error_rate_threshold
            }
        }
    
    def reset(self):
        """重置熔断器"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_failure_time = 0
        self.logger.info(f"熔断器 {self.name} 已重置")


class CircuitBreakerManager:
    """熔断器管理器"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback_func: Optional[Callable] = None
    ) -> CircuitBreaker:
        """获取或创建熔断器"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                config=config,
                fallback_func=fallback_func
            )
            self.logger.info(f"创建熔断器: {name}")
        
        return self._breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """获取所有熔断器状态"""
        return {
            name: breaker.get_state()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self):
        """重置所有熔断器"""
        for breaker in self._breakers.values():
            breaker.reset()
        self.logger.info("所有熔断器已重置")
    
    def remove_breaker(self, name: str):
        """移除熔断器"""
        if name in self._breakers:
            del self._breakers[name]
            self.logger.info(f"移除熔断器: {name}")


# 全局熔断器管理器实例
_global_breaker_manager = CircuitBreakerManager()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
    fallback_func: Optional[Callable] = None
) -> CircuitBreaker:
    """获取全局熔断器"""
    return _global_breaker_manager.get_breaker(
        name=name,
        config=config,
        fallback_func=fallback_func
    )


def get_all_breaker_states() -> Dict[str, Dict[str, Any]]:
    """获取所有熔断器状态"""
    return _global_breaker_manager.get_all_states()


def reset_all_breakers():
    """重置所有熔断器"""
    _global_breaker_manager.reset_all()
