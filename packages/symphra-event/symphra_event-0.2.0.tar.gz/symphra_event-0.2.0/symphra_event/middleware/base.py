"""symphra_event.middleware.base - 中间件基类"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core.emitter import EventEmitter

__all__ = ["MiddlewareBase"]


class MiddlewareBase(ABC):
    """中间件基类。

    中间件在事件发射前后执行自定义逻辑。

    Examples:
        >>> class LoggingMiddleware(MiddlewareBase):
        ...     def before_emit(self, emitter, kwargs):
        ...         print(f"Before emit: {kwargs}")
        ...         return kwargs
        ...
        ...     def after_emit(self, emitter, result):
        ...         print(f"After emit: {result}")
        ...         return result
    """

    @abstractmethod
    def before_emit(
        self,
        emitter: EventEmitter[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """在事件发射前执行。

        Args:
            emitter: 事件发射器
            kwargs: 事件参数

        Returns:
            修改后的事件参数

        Raises:
            Exception: 任何异常都会阻止事件发射
        """
        ...

    @abstractmethod
    def after_emit(
        self,
        emitter: EventEmitter[Any],
        result: Any,
    ) -> Any:
        """在事件发射后执行。

        Args:
            emitter: 事件发射器
            result: 发射结果

        Returns:
            修改后的结果
        """
        ...
