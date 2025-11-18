"""symphra_event.types - 核心类型定义

使用 Python 3.11+ 的现代类型特性。
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, ParamSpec, TypeAlias, TypeVar, final

__all__ = [
    "CleanupStats",
    "EmitResult",
    "EventFilter",
    "EventHandler",
    "ExecutionMode",
    "Listener",
    "Priority",
]

# ============================================================================
# Type Variables
# ============================================================================

P = ParamSpec("P")
T = TypeVar("T")

# ============================================================================
# Type Aliases
# ============================================================================

# 事件处理器
EventHandler: TypeAlias = Callable[..., None]

# 异步事件处理器
AsyncEventHandler: TypeAlias = Callable[..., Awaitable[None]]

# 条件过滤器
EventFilter: TypeAlias = Callable[[dict[str, Any]], bool]

# ============================================================================
# Enums
# ============================================================================


@final
class ExecutionMode(Enum):
    """事件执行模式。"""

    SEQUENTIAL = auto()  # 串行执行
    PARALLEL = auto()  # 并行执行（线程池）
    PIPELINE = auto()  # 流水线执行（上一个输出作为下一个输入）

    def __str__(self) -> str:
        return self.name.lower()


@final
class Priority(Enum):
    """预定义优先级常量。"""

    CRITICAL = 1000
    HIGH = 100
    NORMAL = 0
    LOW = -100
    LOWEST = -1000

    def __int__(self) -> int:
        return self.value


# ============================================================================
# Data Classes
# ============================================================================


@final
@dataclass(slots=True, frozen=True, kw_only=True)
class Listener:
    """事件监听器（不可变）。

    使用 slots=True 减少内存占用约 40%。
    使用 frozen=True 确保不可变性和线程安全。
    """

    handler: Callable[..., Any]
    priority: int = 0
    once: bool = False
    condition: EventFilter | None = None
    tag: str | None = None

    def __hash__(self) -> int:
        """基于 handler 的 id 进行哈希。"""
        return hash(id(self.handler))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Listener):
            return NotImplemented
        return id(self.handler) == id(other.handler)


@final
@dataclass(slots=True, frozen=True)
class EmitResult:
    """事件发射结果（不可变）。"""

    success_count: int
    total_count: int
    errors: tuple[Exception, ...] = ()
    elapsed_ms: float = 0.0
    pipeline_output: dict[str, Any] | None = None  # 流水线模式的最终输出

    @property
    def failed_count(self) -> int:
        """失败的监听器数量。"""
        return len(self.errors)

    @property
    def success_rate(self) -> float:
        """成功率（0.0 - 1.0）。"""
        if self.total_count == 0:
            return 1.0
        return self.success_count / self.total_count

    @property
    def has_errors(self) -> bool:
        """是否有错误。"""
        return len(self.errors) > 0


@final
@dataclass(slots=True, frozen=True)
class CleanupStats:
    """清理统计信息（不可变）。"""

    dead_refs_removed: int
    listeners_remaining: int
    elapsed_ms: float
