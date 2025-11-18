"""symphra_event.middleware.builtin - 内置中间件"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .base import MiddlewareBase

if TYPE_CHECKING:
    from ..core.emitter import EventEmitter
    from ..types import EmitResult

__all__ = [
    "LoggingMiddleware",
    "ValidationMiddleware",
]


class LoggingMiddleware(MiddlewareBase):
    """日志中间件。

    记录事件发射的详细信息。

    Examples:
        >>> emitter = EventEmitter()
        >>> emitter.use(LoggingMiddleware())
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """初始化日志中间件。

        Args:
            logger: 日志记录器（可选）
        """
        self.logger = logger or logging.getLogger(__name__)

    def before_emit(
        self,
        emitter: EventEmitter[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """记录发射前信息。"""
        self.logger.debug(f"[{emitter._name}] Emitting event with {len(kwargs)} args")
        return kwargs

    def after_emit(
        self,
        emitter: EventEmitter[Any],
        result: EmitResult,
    ) -> EmitResult:
        """记录发射后信息。"""
        if result.has_errors:
            self.logger.warning(
                f"[{emitter._name}] Emit completed with {len(result.errors)} errors"
            )
        else:
            self.logger.debug(
                f"[{emitter._name}] Emit completed successfully "
                f"in {result.elapsed_ms:.2f}ms"
            )
        return result


class ValidationMiddleware(MiddlewareBase):
    """验证中间件。

    验证事件参数是否符合要求。

    Examples:
        >>> def validate(kwargs):
        ...     if 'user_id' not in kwargs:
        ...         raise ValueError("Missing user_id")
        ...     return True
        >>>
        >>> emitter = EventEmitter()
        >>> emitter.use(ValidationMiddleware(validator=validate))
    """

    def __init__(
        self,
        validator: Any,
        *,
        required_keys: list[str] | None = None,
    ) -> None:
        """初始化验证中间件。

        Args:
            validator: 验证函数
            required_keys: 必需的键列表（可选）
        """
        self.validator = validator
        self.required_keys = required_keys or []

    def before_emit(
        self,
        emitter: EventEmitter[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """验证参数。"""
        # 检查必需键
        for key in self.required_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required key: {key}")

        # 执行自定义验证
        if self.validator and not self.validator(kwargs):
            raise ValueError("Validation failed")

        return kwargs

    def after_emit(
        self,
        emitter: EventEmitter[Any],
        result: EmitResult,
    ) -> EmitResult:
        """发射后不做处理。"""
        return result
