"""symphra_event.execution.pipeline - 流水线执行器

流水线执行模式：上一个监听器的输出作为下一个监听器的输入。
适用场景：数据转换管道、ETL 处理、数据流转等。
"""

from __future__ import annotations

import time
from typing import Any

from ..types import EmitResult, Listener

__all__ = ["PipelineExecutor"]


class PipelineExecutor:
    """流水线执行器。

    按优先级顺序执行监听器，每个监听器的返回值作为下一个监听器的输入。

    工作原理：
    1. 第一个监听器接收原始 kwargs
    2. 后续监听器接收前一个监听器的返回值（必须是 dict）
    3. 如果返回值不是 dict，抛出 TypeError
    4. 最终返回最后一个监听器的输出

    Examples:
        >>> executor = PipelineExecutor()
        >>> # 定义流水线处理器
        >>> def validate(data: dict) -> dict:
        ...     return {"validated": data}
        >>> def transform(validated: dict) -> dict:
        ...     return {"transformed": validated["validated"].upper()}
        >>> def save(transformed: dict) -> dict:
        ...     return {"saved": True}
        >>>
        >>> listeners = (validate, transform, save)
        >>> result = executor.execute(listeners, data="test")
        >>> # result.pipeline_output = {"saved": True}
    """

    @staticmethod
    def execute(
        listeners: tuple[Listener, ...],
        **kwargs: Any,
    ) -> EmitResult:
        """流水线执行监听器。

        Args:
            listeners: 监听器列表（已按优先级排序）
            **kwargs: 初始事件参数

        Returns:
            执行结果（包含最终输出）

        Raises:
            TypeError: 如果监听器返回值不是 dict
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
        current_data = kwargs  # 初始数据

        # 流水线执行
        for listener in listeners:
            try:
                # 条件过滤
                condition = listener.condition
                if condition is not None and not condition(current_data):
                    # 跳过但不传递数据
                    continue

                # 执行处理器
                handler = listener.handler
                result = handler(**current_data)

                # 验证返回值类型
                if result is not None:
                    if not isinstance(result, dict):
                        raise TypeError(
                            f"Pipeline handler {handler.__name__!r} "
                            f"must return dict or None, got {type(result).__name__}"
                        )
                    # 更新当前数据为返回值
                    current_data = result

                success_count += 1

            except Exception as e:
                errors.append(e)
                # 流水线中断：错误发生后停止执行
                break

        # 计算耗时
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return EmitResult(
            success_count=success_count,
            total_count=total_count,
            errors=tuple(errors),
            elapsed_ms=elapsed_ms,
            pipeline_output=current_data,  # 返回流水线最终输出
        )
