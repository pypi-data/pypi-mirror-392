"""
TiMEM监控和日志组件

提供企业级监控、日志记录、性能指标收集等功能。
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import asynccontextmanager
from .exceptions import TiMEMError


@dataclass
class RequestMetrics:
    """请求指标"""
    request_id: str
    method: str
    endpoint: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status_code: Optional[int] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    error_rate: float


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 创建JSON格式化器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_request(
        self,
        request_id: str,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        success: bool,
        user_id: Optional[str] = None,
        domain: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """记录请求日志"""
        log_data = {
            "type": "request",
            "request_id": request_id,
            "method": method,
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "domain": domain
        }
        
        if error_message:
            log_data["error_message"] = error_message
        
        if success:
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))
    
    def log_system_event(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """记录系统事件日志"""
        log_data = {
            "type": "system_event",
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data:
            log_data.update(data)
        
        self.logger.info(json.dumps(log_data))
    
    def log_business_event(
        self,
        event_type: str,
        user_id: str,
        domain: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """记录业务事件日志"""
        log_data = {
            "type": "business_event",
            "event_type": event_type,
            "user_id": user_id,
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data:
            log_data.update(data)
        
        self.logger.info(json.dumps(log_data))


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: List[RequestMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self.max_metrics_history = 1000
        
        # 统计信息
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_duration = 0.0
        
        # 日志记录器
        self.logger = StructuredLogger(f"{__name__}.MetricsCollector")
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        success: bool,
        user_id: Optional[str] = None,
        domain: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """记录请求指标"""
        request_id = str(uuid.uuid4())
        
        metric = RequestMetrics(
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            start_time=time.time() - duration,
            end_time=time.time(),
            duration=duration,
            status_code=status_code,
            success=success,
            error_message=error_message,
            user_id=user_id,
            domain=domain
        )
        
        # 添加到历史记录
        self.metrics.append(metric)
        if len(self.metrics) > self.max_metrics_history:
            self.metrics.pop(0)
        
        # 更新统计信息
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_duration += duration
        
        # 记录日志
        self.logger.log_request(
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            duration=duration,
            status_code=status_code,
            success=success,
            user_id=user_id,
            domain=domain,
            error_message=error_message
        )
    
    def record_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        active_connections: int
    ):
        """记录系统指标"""
        system_metric = SystemMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_connections=active_connections,
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            average_response_time=self.get_average_response_time(),
            error_rate=self.get_error_rate()
        )
        
        self.system_metrics.append(system_metric)
        if len(self.system_metrics) > self.max_metrics_history:
            self.system_metrics.pop(0)
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if self.total_requests == 0:
            return 0.0
        return self.total_duration / self.total_requests
    
    def get_error_rate(self) -> float:
        """获取错误率"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def get_recent_metrics(self, limit: int = 100) -> List[RequestMetrics]:
        """获取最近的指标"""
        return self.metrics[-limit:] if self.metrics else []
    
    def get_system_metrics_summary(self) -> Dict[str, Any]:
        """获取系统指标摘要"""
        if not self.system_metrics:
            return {}
        
        latest = self.system_metrics[-1]
        return {
            "timestamp": latest.timestamp,
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "active_connections": latest.active_connections,
            "total_requests": latest.total_requests,
            "successful_requests": latest.successful_requests,
            "failed_requests": latest.failed_requests,
            "average_response_time": latest.average_response_time,
            "error_rate": latest.error_rate,
            "success_rate": self.get_success_rate()
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, name: str):
        self.name = name
        self.metrics_collector = MetricsCollector()
        self.logger = StructuredLogger(f"{__name__}.{name}")
        
        # 监控配置
        self.slow_request_threshold = 5.0  # 慢请求阈值（秒）
        self.high_error_rate_threshold = 0.1  # 高错误率阈值
        
        # 告警回调
        self.alert_callbacks: List[Callable] = []
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def _check_alerts(self, metric: RequestMetrics):
        """检查告警条件"""
        # 慢请求告警
        if metric.duration and metric.duration > self.slow_request_threshold:
            self._trigger_alert("slow_request", {
                "request_id": metric.request_id,
                "duration": metric.duration,
                "threshold": self.slow_request_threshold
            })
        
        # 高错误率告警
        if self.metrics_collector.get_error_rate() > self.high_error_rate_threshold:
            self._trigger_alert("high_error_rate", {
                "error_rate": self.metrics_collector.get_error_rate(),
                "threshold": self.high_error_rate_threshold
            })
    
    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """触发告警"""
        alert_data = {
            "type": "alert",
            "alert_type": alert_type,
            "monitor_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        self.logger.logger.warning(json.dumps(alert_data))
        
        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                self.logger.logger.error(f"告警回调执行失败: {str(e)}")
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        success: bool,
        user_id: Optional[str] = None,
        domain: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """记录请求并检查告警"""
        self.metrics_collector.record_request(
            method=method,
            endpoint=endpoint,
            duration=duration,
            status_code=status_code,
            success=success,
            user_id=user_id,
            domain=domain,
            error_message=error_message
        )
        
        # 创建指标对象用于告警检查
        metric = RequestMetrics(
            request_id=str(uuid.uuid4()),
            method=method,
            endpoint=endpoint,
            start_time=time.time() - duration,
            end_time=time.time(),
            duration=duration,
            status_code=status_code,
            success=success,
            error_message=error_message,
            user_id=user_id,
            domain=domain
        )
        
        self._check_alerts(metric)
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        summary = self.metrics_collector.get_system_metrics_summary()
        
        # 健康状态判断
        is_healthy = True
        issues = []
        
        if summary.get("error_rate", 0) > self.high_error_rate_threshold:
            is_healthy = False
            issues.append(f"错误率过高: {summary['error_rate']:.2%}")
        
        if summary.get("average_response_time", 0) > self.slow_request_threshold:
            is_healthy = False
            issues.append(f"平均响应时间过长: {summary['average_response_time']:.2f}s")
        
        return {
            "is_healthy": is_healthy,
            "issues": issues,
            "summary": summary,
            "thresholds": {
                "slow_request": self.slow_request_threshold,
                "high_error_rate": self.high_error_rate_threshold
            }
        }


class MonitoringDecorator:
    """监控装饰器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func):
        """装饰器实现"""
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_message = None
                status_code = 200
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    status_code = 500
                    raise
                finally:
                    duration = time.time() - start_time
                    self.monitor.record_request(
                        method="POST",  # 默认方法
                        endpoint=func.__name__,
                        duration=duration,
                        status_code=status_code,
                        success=success,
                        error_message=error_message
                    )
            
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_message = None
                status_code = 200
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    status_code = 500
                    raise
                finally:
                    duration = time.time() - start_time
                    self.monitor.record_request(
                        method="POST",  # 默认方法
                        endpoint=func.__name__,
                        duration=duration,
                        status_code=status_code,
                        success=success,
                        error_message=error_message
                    )
            
            return sync_wrapper


# 全局监控器实例
_global_monitor = PerformanceMonitor("TiMEM_Global")


def get_global_monitor() -> PerformanceMonitor:
    """获取全局监控器"""
    return _global_monitor


def monitor_function(monitor: Optional[PerformanceMonitor] = None):
    """函数监控装饰器"""
    if monitor is None:
        monitor = _global_monitor
    
    return MonitoringDecorator(monitor)
