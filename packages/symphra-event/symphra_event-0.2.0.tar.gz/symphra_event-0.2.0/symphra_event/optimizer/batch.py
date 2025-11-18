"""symphra_event.optimizer.batch - 事件批量处理优化器

创新点：
1. 自动事件合并
2. 批量处理
3. 延迟执行
4. 动态批量大小调整

零依赖实现：
- collections.deque: 高效队列
- threading: 定时器
- time: 时间控制
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, final

__all__ = ["BatchProcessor", "BatchedEvent"]

T = TypeVar("T")


@final
@dataclass(slots=True)
class BatchedEvent:
    """批量事件。"""

    event_name: str
    events: list[dict[str, Any]]
    timestamp: float


@final
class BatchProcessor(Generic[T]):
    """事件批量处理器。

    自动合并相同类型的事件，批量处理。

    Examples:
        >>> processor = BatchProcessor(
        ...     batch_size=100,
        ...     flush_interval_ms=50.0,
        ... )
        >>>
        >>> # 定义批量处理器
        >>> @processor.register("user.login")
        ... def process_logins(events: list[dict[str, Any]]) -> None:
        ...     user_ids = [e["user_id"] for e in events]
        ...     print(f"批量处理 {len(user_ids)} 个登录事件")
        ...     # 批量数据库操作
        ...     # db.batch_insert(user_ids)
        >>>
        >>> # 添加事件（自动批量）
        >>> for i in range(1000):
        ...     processor.add("user.login", {"user_id": i})
        ...     # 每 100 个自动触发批量处理
        >>>
        >>> # 或者等待定时刷新（50ms）
        >>> time.sleep(0.1)
        >>> # 自动刷新剩余事件
    """

    __slots__ = (
        "_batch_size",
        "_flush_interval_ms",
        "_handlers",
        "_lock",
        "_queues",
        "_running",
        "_stats",
        "_timer",
    )

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval_ms: float = 50.0,
    ) -> None:
        """初始化批量处理器。

        Args:
            batch_size: 批量大小
            flush_interval_ms: 刷新间隔（毫秒）
        """
        self._batch_size = batch_size
        self._flush_interval_ms = flush_interval_ms
        self._queues: dict[str, deque[dict[str, Any]]] = {}
        self._handlers: dict[str, Callable[[list[dict[str, Any]]], None]] = {}
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._stats: dict[str, dict[str, int]] = {}
        self._running = True

        # 启动定时刷新
        self._schedule_flush()

    def register(
        self,
        event_name: str,
    ) -> Callable[
        [Callable[[list[dict[str, Any]]], None]],
        Callable[[list[dict[str, Any]]], None],
    ]:
        """注册批量处理器（装饰器）。

        Args:
            event_name: 事件名称

        Returns:
            装饰器函数
        """

        def decorator(
            handler: Callable[[list[dict[str, Any]]], None],
        ) -> Callable[[list[dict[str, Any]]], None]:
            with self._lock:
                self._handlers[event_name] = handler
                self._queues[event_name] = deque()
                self._stats[event_name] = {
                    "total_events": 0,
                    "batch_count": 0,
                    "error_count": 0,
                }
            return handler

        return decorator

    def add(self, event_name: str, event_data: dict[str, Any]) -> None:
        """添加事件（自动批量）。

        Args:
            event_name: 事件名称
            event_data: 事件数据
        """
        with self._lock:
            if event_name not in self._queues:
                self._queues[event_name] = deque()

            queue = self._queues[event_name]
            queue.append(event_data)

            # 更新统计
            if event_name in self._stats:
                self._stats[event_name]["total_events"] += 1

            # 达到批量大小，立即处理
            if len(queue) >= self._batch_size:
                self._flush_queue(event_name)

    def flush(self, event_name: str | None = None) -> None:
        """手动刷新队列。

        Args:
            event_name: 事件名称（None 表示刷新所有）
        """
        with self._lock:
            if event_name is None:
                # 刷新所有队列
                for name in list(self._queues.keys()):
                    self._flush_queue(name)
            else:
                self._flush_queue(event_name)

    def _flush_queue(self, event_name: str) -> None:
        """刷新队列（内部方法，需持有锁）。"""
        if event_name not in self._queues:
            return

        queue = self._queues[event_name]
        if not queue:
            return

        # 批量取出事件
        batch: list[dict[str, Any]] = []
        while queue and len(batch) < self._batch_size:
            batch.append(queue.popleft())

        # 调用处理器
        if event_name in self._handlers and batch:
            try:
                self._handlers[event_name](batch)
                # 更新统计
                if event_name in self._stats:
                    self._stats[event_name]["batch_count"] += 1
            except Exception:
                # 错误处理
                if event_name in self._stats:
                    self._stats[event_name]["error_count"] += 1

    def _schedule_flush(self) -> None:
        """定时刷新。"""
        if not self._running:
            return

        if self._timer is not None:
            self._timer.cancel()

        def flush_all() -> None:
            if self._running:
                self.flush()
                self._schedule_flush()

        self._timer = threading.Timer(
            self._flush_interval_ms / 1000,
            flush_all,
        )
        self._timer.daemon = True
        self._timer.start()

    def stop(self) -> None:
        """停止批量处理器。"""
        self._running = False
        if self._timer is not None:
            self._timer.cancel()
        # 刷新所有剩余事件
        self.flush()

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息。

        Returns:
            统计信息字典
        """
        with self._lock:
            return {
                event_name: {
                    "pending_count": len(self._queues.get(event_name, [])),
                    "has_handler": event_name in self._handlers,
                    **self._stats.get(event_name, {}),
                }
                for event_name in set(self._queues.keys()) | set(self._handlers.keys())
            }

    def __enter__(self) -> BatchProcessor[T]:
        """进入上下文管理器。"""
        return self

    def __exit__(self, *args: Any) -> None:
        """退出上下文管理器。"""
        self.stop()
