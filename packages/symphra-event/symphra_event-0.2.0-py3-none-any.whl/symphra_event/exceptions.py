"""symphra_event.exceptions - 异常类定义"""

from __future__ import annotations

__all__ = [
    "EmitError",
    "EventEmitterError",
    "HandlerRegistrationError",
    "InvalidNamespaceError",
    "SymphraEventError",
]


class SymphraEventError(Exception):
    """基础异常类。"""

    pass


class EventEmitterError(SymphraEventError):
    """事件发射器错误。"""

    pass


class InvalidNamespaceError(SymphraEventError):
    """无效的命名空间。"""

    pass


class HandlerRegistrationError(EventEmitterError):
    """处理器注册错误。"""

    pass


class EmitError(EventEmitterError):
    """事件发射错误。"""

    pass
