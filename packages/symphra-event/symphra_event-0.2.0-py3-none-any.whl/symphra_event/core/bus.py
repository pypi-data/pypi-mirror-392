"""symphra_event.core.bus - EventBus 全局事件总线"""

from __future__ import annotations

import threading
from typing import Any, ClassVar, final

from ..exceptions import InvalidNamespaceError
from .emitter import EventEmitter

__all__ = ["EventBus"]


@final
class EventBus:
    """全局事件总线（单例模式）。

    管理命名的事件发射器，提供跨模块的事件通信。

    线程安全：使用锁保护内部状态。

    Examples:
        >>> # 创建/获取 emitter
        >>> user_emitter = EventBus.create("user")
        >>> user_emitter = EventBus.get("user")
        >>>
        >>> # 移除 emitter
        >>> EventBus.remove("user")
        >>>
        >>> # 列出所有 emitter
        >>> names = EventBus.list()
    """

    _emitters: ClassVar[dict[str, EventEmitter[Any]]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def create(
        cls,
        name: str,
        *,
        overwrite: bool = False,
    ) -> EventEmitter[Any]:
        """创建命名的事件发射器。

        Args:
            name: 发射器名称
            overwrite: 是否覆盖已存在的发射器（默认 False）

        Returns:
            EventEmitter 实例

        Raises:
            InvalidNamespaceError: 如果名称已存在且 overwrite=False

        Examples:
            >>> emitter = EventBus.create("user")
            >>> emitter = EventBus.create("user", overwrite=True)  # 覆盖
        """
        with cls._lock:
            if name in cls._emitters and not overwrite:
                raise InvalidNamespaceError(
                    f"EventEmitter '{name}' already exists. "
                    f"Use overwrite=True to replace it."
                )

            emitter = EventEmitter[Any](name=name)
            cls._emitters[name] = emitter
            return emitter

    @classmethod
    def get(cls, name: str) -> EventEmitter[Any] | None:
        """获取命名的事件发射器。

        Args:
            name: 发射器名称

        Returns:
            EventEmitter 实例，如果不存在则返回 None

        Examples:
            >>> emitter = EventBus.get("user")
            >>> if emitter is None:
            ...     emitter = EventBus.create("user")
        """
        with cls._lock:
            return cls._emitters.get(name)

    @classmethod
    def get_or_create(cls, name: str) -> EventEmitter[Any]:
        """获取或创建命名的事件发射器。

        Args:
            name: 发射器名称

        Returns:
            EventEmitter 实例

        Examples:
            >>> emitter = EventBus.get_or_create("user")
        """
        with cls._lock:
            if name not in cls._emitters:
                cls._emitters[name] = EventEmitter[Any](name=name)
            return cls._emitters[name]

    @classmethod
    def remove(cls, name: str) -> bool:
        """移除命名的事件发射器。

        Args:
            name: 发射器名称

        Returns:
            是否成功移除

        Examples:
            >>> EventBus.remove("user")
            True
            >>> EventBus.remove("nonexistent")
            False
        """
        with cls._lock:
            if name in cls._emitters:
                del cls._emitters[name]
                return True
            return False

    @classmethod
    def list(cls) -> list[str]:
        """列出所有事件发射器名称。

        Returns:
            名称列表

        Examples:
            >>> EventBus.create("user")
            >>> EventBus.create("order")
            >>> EventBus.list()
            ['user', 'order']
        """
        with cls._lock:
            return list(cls._emitters.keys())

    @classmethod
    def clear(cls) -> None:
        """清空所有事件发射器。

        Examples:
            >>> EventBus.clear()
        """
        with cls._lock:
            cls._emitters.clear()

    @classmethod
    def stats(cls) -> dict[str, Any]:
        """获取统计信息。

        Returns:
            统计信息字典

        Examples:
            >>> stats = EventBus.stats()
            >>> print(stats['total'])
            2
            >>> print(stats['listeners'])
            {'user': 3, 'order': 5}
        """
        with cls._lock:
            return {
                "total": len(cls._emitters),
                "names": list(cls._emitters.keys()),
                "listeners": {
                    name: emitter.count() for name, emitter in cls._emitters.items()
                },
            }
