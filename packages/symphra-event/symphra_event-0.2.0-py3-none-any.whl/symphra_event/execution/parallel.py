"""symphra_event.execution.parallel - 并行执行器"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from ..types import EmitResult, Listener

__all__ = ["ParallelExecutor"]


class ParallelExecutor:
    """并行执行器。

    使用线程池并行执行监听器。

    Examples:
        >>> executor = ParallelExecutor(max_workers=4)
        >>> result = executor.execute(listeners, data="test")
        >>> executor.close()  # 使用完后关闭
    """

    def __init__(self, max_workers: int = 4) -> None:
        """初始化并行执行器。

        Args:
            max_workers: 最大工作线程数（默认 4）
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute(
        self,
        listeners: tuple[Listener, ...],
        **kwargs: Any,
    ) -> EmitResult:
        """并行执行监听器。

        Args:
            listeners: 监听器列表
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

        # 过滤满足条件的监听器
        active_listeners = [
            listener
            for listener in listeners
            if listener.condition is None or listener.condition(kwargs)
        ]

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_listener = {
                executor.submit(listener.handler, **kwargs): listener
                for listener in active_listeners
            }

            # 收集结果
            for future in as_completed(future_to_listener):
                try:
                    future.result()  # 获取结果或异常
                    success_count += 1
                except Exception as e:
                    errors.append(e)

        # 计算耗时
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return EmitResult(
            success_count=success_count,
            total_count=len(active_listeners),
            errors=tuple(errors),
            elapsed_ms=elapsed_ms,
        )
