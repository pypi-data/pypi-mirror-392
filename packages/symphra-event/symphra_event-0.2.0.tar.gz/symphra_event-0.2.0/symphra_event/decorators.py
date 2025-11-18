"""symphra_event.decorators - 全局装饰器

提供简洁的全局装饰器 API。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, overload

from .core.emitter import EventEmitter
from .namespace import NamespaceRegistry
from .types import EmitResult, EventFilter

__all__ = ["emit", "emitter", "events"]

T = TypeVar("T", bound=Callable[..., Any])

# 全局命名空间注册表
_registry = NamespaceRegistry()


@overload
def emitter(namespace: str, /) -> Callable[[T], T]: ...


@overload
def emitter(
    namespace: str,
    /,
    *,
    priority: int = 0,
    once: bool = False,
    condition: EventFilter | None = None,
    tag: str | None = None,
) -> Callable[[T], T]: ...


def emitter(
    namespace: str,
    /,
    *,
    priority: int = 0,
    once: bool = False,
    condition: EventFilter | None = None,
    tag: str | None = None,
) -> Callable[[T], T]:
    """全局事件装饰器（支持命名空间）。

    Args:
        namespace: 命名空间路径，如 "user.auth.login"
        priority: 优先级（默认 0）
        once: 是否一次性监听（默认 False）
        condition: 条件过滤函数（默认 None）
        tag: 处理器标签（默认 None）

    Returns:
        装饰器函数

    Examples:
        >>> @emitter("user")
        ... def handler(data: dict[str, Any]) -> None:
        ...     print(data)
        >>>
        >>> @emitter("user.auth.login", priority=100)
        ... def on_login(data: dict[str, Any]) -> None:
        ...     print(f"Login: {data}")
    """

    def decorator(func: T) -> T:
        # 获取或创建 emitter
        ee = _registry.get(namespace)
        if ee is None:
            ee = EventEmitter[dict[str, Any]](name=namespace)
            _registry.register(namespace, ee)

        # 注册处理器
        ee.on(func, priority=priority, once=once, condition=condition, tag=tag)

        return func

    return decorator


def emit(namespace: str, /, **kwargs: Any) -> EmitResult:
    """触发事件（支持命名空间）。

    Args:
        namespace: 命名空间路径
        **kwargs: 事件数据

    Returns:
        发射结果

    Raises:
        ValueError: 命名空间不存在

    Examples:
        >>> emit("user.auth.login", user_id=123, username="alice")
        EmitResult(success_count=2, total_count=2, errors=())
    """
    ee = _registry.get(namespace)
    if ee is None:
        from .exceptions import InvalidNamespaceError

        raise InvalidNamespaceError(f"Namespace {namespace!r} not registered")

    result: EmitResult = ee.emit(**kwargs)
    return result


class EventsProxy:
    """事件代理（支持链式点号访问）。

    Examples:
        >>> events.user.auth.login.emit(user_id=123)
        >>> emitter = events.user.auth.login
        >>> emitter.on(handler)
    """

    __slots__ = ("_prefix", "_registry")

    def __init__(self, registry: NamespaceRegistry, prefix: str = "") -> None:
        object.__setattr__(self, "_registry", registry)
        object.__setattr__(self, "_prefix", prefix)

    def __getattr__(self, name: str) -> EventsProxy | EventEmitter[Any]:
        """支持点号访问。"""
        prefix = object.__getattribute__(self, "_prefix")
        registry = object.__getattribute__(self, "_registry")

        full_path = f"{prefix}.{name}" if prefix else name

        # 尝试获取 emitter
        ee = registry.get(full_path)
        if ee is not None:
            result: EventEmitter[Any] = ee
            return result

        # 返回新的代理
        proxy: EventsProxy = EventsProxy(registry, full_path)
        return proxy

    def __setattr__(self, name: str, value: Any) -> None:
        """禁止设置属性。"""
        raise AttributeError("Cannot set attribute on EventsProxy")

    def __repr__(self) -> str:
        prefix = object.__getattribute__(self, "_prefix")
        return f"EventsProxy({prefix!r})"


# 全局 events 对象
events = EventsProxy(_registry)
