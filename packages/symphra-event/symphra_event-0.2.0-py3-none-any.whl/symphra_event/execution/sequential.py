"""symphra_event.execution.sequential - 串行执行器"""

from __future__ import annotations

import time
from typing import Any

from ..types import EmitResult, Listener

__all__ = ["SequentialExecutor"]


class SequentialExecutor:
    """串行执行器。

    按优先级顺序依次执行监听器。

    Examples:
        >>> executor = SequentialExecutor()
        >>> result = executor.execute(listeners, data="test")
    """

    @staticmethod
    def execute(
        listeners: tuple[Listener, ...],
        **kwargs: Any,
    ) -> EmitResult:
        """串行执行监听器。

        Args:
            listeners: 监听器列表（已排序）
            **kwargs: 事件参数

        Returns:
            执行结果
        """
        start_time = time.perf_counter()
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

        # 依次执行
        for listener in listeners:
            try:
                # 条件过滤
                condition = listener.condition
                if condition is not None and not condition(kwargs):
                    continue

                # 执行处理器
                handler = listener.handler
                handler(**kwargs)
                success_count += 1

            except Exception as e:
                errors.append(e)

        # 计算耗时
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return EmitResult(
            success_count=success_count,
            total_count=total_count,
            errors=tuple(errors),
            elapsed_ms=elapsed_ms,
        )
