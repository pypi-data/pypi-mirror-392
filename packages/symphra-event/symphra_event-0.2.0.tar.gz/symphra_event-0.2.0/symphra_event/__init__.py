"""Symphra-Event - 高性能事件库

使用 __all__ 明确导出的公共 API，提供清晰的 IDE 支持。
"""

from __future__ import annotations

# 创新功能 - 依赖分析
from .analysis import DependencyAnalyzer, EventDependency, ExecutionGroup

# 核心模块
from .core.async_emitter import AsyncEventEmitter
from .core.bus import EventBus
from .core.emitter import EventEmitter

# 创新功能 - 时间旅行调试
from .debug import TimeTravelDebugger
from .decorators import emit, emitter, events

# 中间件
from .middleware import LoggingMiddleware, MiddlewareBase, ValidationMiddleware

# 命名空间
from .namespace import Namespace, NamespaceRegistry

# 创新功能 - 批量处理
from .optimizer import BatchProcessor

# 创新功能 - 零拷贝传输
from .transport import ZeroCopyBuffer, ZeroCopyPool

# 类型
from .types import CleanupStats, EmitResult, ExecutionMode, Listener, Priority

__version__ = "0.2.0"

__all__ = [
    # 核心类
    "EventEmitter",
    "AsyncEventEmitter",
    "EventBus",
    # 装饰器和函数
    "emitter",
    "emit",
    "events",
    # 命名空间
    "Namespace",
    "NamespaceRegistry",
    # 中间件
    "MiddlewareBase",
    "LoggingMiddleware",
    "ValidationMiddleware",
    # 类型
    "EmitResult",
    "ExecutionMode",
    "Listener",
    "Priority",
    "CleanupStats",
    # 创新功能
    "BatchProcessor",
    "ZeroCopyBuffer",
    "ZeroCopyPool",
    "DependencyAnalyzer",
    "EventDependency",
    "ExecutionGroup",
    "TimeTravelDebugger",
    # 版本
    "__version__",
]
