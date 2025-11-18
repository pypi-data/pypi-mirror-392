"""symphra_event.core.async_emitter - 异步事件发射器"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from ..types import EmitResult
from ..utils import ensure_awaitable
from .emitter import EventEmitter

__all__ = ["AsyncEventEmitter"]


class AsyncEventEmitter(EventEmitter[Any]):
    """异步事件发射器。

    继承自 EventEmitter，支持异步处理器。
    同步和异步处理器可以混合使用。

    Examples:
        >>> emitter = AsyncEventEmitter()
        >>> @emitter.on
        ... async def async_handler(data: str) -> None:
        ...     await asyncio.sleep(1)
        ...     print(data)
        >>>
        >>> @emitter.on
        ... def sync_handler(data: str) -> None:
        ...     print(data)
        >>>
        >>> await emitter.emit(data="test")
    """

    async def emit(self, **kwargs: Any) -> EmitResult:  # type: ignore[override]
        """异步触发事件。

        同步和异步处理器都会被正确执行：
        - 异步处理器直接 await
        - 同步处理器在线程池中执行（避免阻塞事件循环）

        Args:
            **kwargs: 事件数据

        Returns:
            发射结果

        Examples:
            >>> result = await emitter.emit(data="test")
            >>> if result.has_errors:
            ...     for error in result.errors:
            ...         print(f"Error: {error}")
        """
        start_time = time.perf_counter()

        # 获取排序后的监听器
        listeners = self._get_sorted_listeners()
        total_count = len(listeners)

        if total_count == 0:
            return EmitResult(
                success_count=0,
                total_count=0,
                errors=(),
                elapsed_ms=0.0,
            )

        errors: list[Exception] = []
        success_count = 0
        to_remove: list[Any] = []

        # 创建任务列表
        tasks: list[asyncio.Task[None]] = []

        for listener in listeners:
            # 条件过滤
            condition = listener.condition
            if condition is not None and not condition(kwargs):
                continue

            # 创建任务
            async def execute_listener(listener: Any = listener) -> None:
                nonlocal success_count
                try:
                    handler = listener.handler
                    await ensure_awaitable(handler, **kwargs)
                    success_count += 1

                    # 一次性监听器
                    if listener.once:
                        to_remove.append(listener)

                except Exception as e:
                    errors.append(e)

            task = asyncio.create_task(execute_listener())
            tasks.append(task)

        # 并发执行所有任务
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=False)

        # 移除一次性监听器
        if to_remove:
            for listener in to_remove:
                handler_name = listener.handler.__name__
                if handler_name in self._listeners:
                    self._listeners[handler_name].discard(listener)
                    if not self._listeners[handler_name]:
                        del self._listeners[handler_name]

            self._sorted_cache = None

        # 计算耗时
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # 更新统计
        self._emit_count += 1

        return EmitResult(
            success_count=success_count,
            total_count=total_count,
            errors=tuple(errors),
            elapsed_ms=elapsed_ms,
        )

    def __repr__(self) -> str:
        name = self._name or "<unnamed>"
        count = self.count()
        return f"AsyncEventEmitter(name={name!r}, listeners={count})"
