"""EventEmitter 核心实现。

优化策略：
- 智能缓存活跃监听器
- 延迟清理（每100次发射执行一次）
- 批量操作提升性能
- 内联关键路径减少函数调用
"""

from __future__ import annotations

import time
import weakref
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

if TYPE_CHECKING:
    from ..types import EventFilter

from ..types import CleanupStats, EmitResult, Listener

__all__ = ["EventEmitter"]

T = TypeVar("T")


class EventEmitter(Generic[T]):
    """High-performance event emitter with all features preserved.

    Features:
    - Priority-based listener ordering
    - Conditional filtering
    - Once listeners (auto-remove after first call)
    - Automatic weak reference cleanup
    - Tag-based listener management
    - Batch operations for performance
    """

    __slots__ = (
        "__weakref__",
        "_active_listeners_cache",
        "_cleanup_counter",
        "_dead_handlers",
        "_emit_count",
        "_listeners",
        "_name",
        "_needs_cleanup",
        "_refs",
        "_sorted_cache",
    )

    CLEANUP_INTERVAL = 100

    def __init__(self, *, name: str | None = None) -> None:
        """初始化事件发射器。"""
        self._name = name
        self._listeners: list[Listener] = []
        self._sorted_cache: tuple[Listener, ...] | None = None
        self._active_listeners_cache: tuple[Listener, ...] | None = None
        self._emit_count = 0
        self._cleanup_counter = 0
        self._refs: dict[int, weakref.ref[Callable[..., Any]]] = {}
        self._dead_handlers: set[int] = set()
        self._needs_cleanup = False

    # ========================================================================
    # ========================================================================

    @overload
    def on(
        self,
        handler: Callable[[T], None],
        /,
        *,
        priority: int = ...,
        once: bool = ...,
        condition: EventFilter | None = ...,
        tag: str | None = ...,
    ) -> Callable[[T], None]: ...

    @overload
    def on(
        self,
        handler: None = None,
        /,
        *,
        priority: int = 0,
        once: bool = False,
        condition: EventFilter | None = None,
        tag: str | None = None,
    ) -> Callable[[Callable[[T], None]], Callable[[T], None]]: ...

    def on(
        self,
        handler: Callable[[T], None] | None = None,
        /,
        *,
        priority: int = 0,
        once: bool = False,
        condition: EventFilter | None = None,
        tag: str | None = None,
    ) -> Callable[[T], None] | Callable[[Callable[[T], None]], Callable[[T], None]]:
        """订阅事件。"""

        def _register(h: Callable[[T], None]) -> Callable[[T], None]:
            """实际注册逻辑。"""
            listener = Listener(
                handler=h,
                priority=priority,
                once=once,
                condition=condition,
                tag=tag,
            )
            self._listeners.append(listener)
            self._sorted_cache = None
            self._active_listeners_cache = None
            handler_id = id(h)
            if handler_id not in self._refs:

                def cleanup_callback(ref: weakref.ref[Callable[..., Any]]) -> None:
                    """弱引用被回收时的清理回调。"""
                    self._dead_handlers.add(handler_id)
                    self._needs_cleanup = True
                    self._active_listeners_cache = None

                self._refs[handler_id] = weakref.ref(h, cleanup_callback)

            return h

        if handler is not None:
            return _register(handler)

        return _register

    def off(
        self,
        handler: Callable[[T], None] | None = None,
        /,
        *,
        tag: str | None = None,
    ) -> int:
        """移除监听器。"""
        removed_count = 0

        if handler is not None:
            handler_id = id(handler)
            if handler_id in self._refs:
                self._dead_handlers.add(handler_id)
                self._needs_cleanup = True
                self._active_listeners_cache = None
                removed_count = 1
                del self._refs[handler_id]

        elif tag is not None:
            to_remove: list[int] = []
            for idx, listener in enumerate(self._listeners):
                if listener.tag == tag:
                    to_remove.append(idx)
            for idx in to_remove:
                handler_id = id(self._listeners[idx].handler)
                self._dead_handlers.add(handler_id)
                removed_count += 1

            self._needs_cleanup = True
            self._active_listeners_cache = None

        if removed_count > 0:
            self._sorted_cache = None

        return removed_count

    def emit(self, **kwargs: Any) -> EmitResult:
        """触发事件。"""
        start_time = time.perf_counter()
        self._cleanup_counter += 1
        if self._cleanup_counter >= self.CLEANUP_INTERVAL:
            if self._needs_cleanup:
                self._cleanup_dead_handlers()
                self._needs_cleanup = False
            self._cleanup_counter = 0
        listeners = self._get_active_listeners()
        total_count = len(listeners)

        if total_count == 0:
            return EmitResult(
                success_count=0,
                total_count=0,
                errors=(),
                elapsed_ms=(time.perf_counter() - start_time) * 1000,
            )

        errors: list[Exception] = []
        success_count = 0
        to_remove: list[int] = []
        i = 0
        while i < total_count:
            listener = listeners[i]
            try:
                condition = listener.condition
                if condition is not None and not condition(kwargs):
                    i += 1
                    continue
                listener.handler(**kwargs)
                success_count += 1
                if listener.once:
                    to_remove.append(i)

            except Exception as e:
                errors.append(e)
            i += 1
        if to_remove:
            self._remove_by_indices(to_remove)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._emit_count += 1

        return EmitResult(
            success_count=success_count,
            total_count=total_count,
            errors=tuple(errors),
            elapsed_ms=elapsed_ms,
        )

    def count(self) -> int:
        """获取监听器数量。"""
        if self._needs_cleanup:
            self._cleanup_dead_handlers()
            self._needs_cleanup = False

        return len(self._listeners)

    def clear(self) -> None:
        """清空所有监听器。"""
        self._listeners.clear()
        self._refs.clear()
        self._dead_handlers.clear()
        self._sorted_cache = None
        self._active_listeners_cache = None
        self._needs_cleanup = False

    def cleanup(self) -> CleanupStats:
        """清理死引用并返回统计信息。"""
        start_time = time.perf_counter()

        before_count = len(self._listeners)
        self._cleanup_dead_handlers()
        after_count = len(self._listeners)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return CleanupStats(
            dead_refs_removed=before_count - after_count,
            listeners_remaining=after_count,
            elapsed_ms=elapsed_ms,
        )

    # ========================================================================
    # ========================================================================

    def on_many(
        self,
        handlers: list[Callable[[T], None]],
        **kwargs: Any,
    ) -> None:
        """批量注册监听器（高性能）。

        Args:
            handlers: 处理器列表
            **kwargs: 其他参数（priority, once, condition, tag）
        """
        priority = kwargs.get("priority", 0)
        once = kwargs.get("once", False)
        condition = kwargs.get("condition")
        tag = kwargs.get("tag")

        for handler in handlers:
            listener = Listener(
                handler=handler,
                priority=priority,
                once=once,
                condition=condition,
                tag=tag,
            )
            self._listeners.append(listener)
        self._sorted_cache = None
        self._active_listeners_cache = None

    def off_many(
        self,
        handlers: list[Callable[[T], None]] | None = None,
        tag: str | None = None,
    ) -> int:
        """批量移除监听器。

        Args:
            handlers: 处理器列表
            tag: 标签

        Returns:
            移除的数量
        """
        removed_count = 0

        if handlers is not None:
            for handler in handlers:
                handler_id = id(handler)
                if handler_id in self._refs:
                    self._dead_handlers.add(handler_id)
                    removed_count += 1
                    del self._refs[handler_id]

            self._needs_cleanup = True
            self._active_listeners_cache = None

        elif tag is not None:
            for _idx, listener in enumerate(self._listeners):
                if listener.tag == tag:
                    handler_id = id(listener.handler)
                    self._dead_handlers.add(handler_id)
                    removed_count += 1

            self._needs_cleanup = True
            self._active_listeners_cache = None

        if removed_count > 0:
            self._sorted_cache = None

        return removed_count

    # ========================================================================
    # ========================================================================

    def __enter__(self) -> EventEmitter[T]:
        """进入上下文管理器。"""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """退出上下文管理器，自动清理。"""
        self.clear()

    # ========================================================================
    # ========================================================================

    def _get_active_listeners(self) -> tuple[Listener, ...]:
        """获取活跃监听器（带缓存）。"""
        if self._needs_cleanup:
            self._cleanup_dead_handlers()
            self._needs_cleanup = False
        if self._active_listeners_cache is None:
            sorted_listeners = self._get_sorted_listeners()
            self._active_listeners_cache = sorted_listeners

        return self._active_listeners_cache

    def _get_sorted_listeners(self) -> tuple[Listener, ...]:
        """获取排序后的监听器（带缓存）。"""
        if self._sorted_cache is None:
            listeners = sorted(
                self._listeners,
                key=lambda listener: listener.priority,
                reverse=True,
            )
            self._sorted_cache = tuple(listeners)

        return self._sorted_cache

    def _cleanup_dead_handlers(self) -> None:
        """清理标记删除的处理器。"""
        if not self._dead_handlers:
            return
        indices_to_remove: list[int] = []
        for idx, listener in enumerate(self._listeners):
            if id(listener.handler) in self._dead_handlers:
                indices_to_remove.append(idx)
        for idx in sorted(indices_to_remove, reverse=True):
            self._listeners.pop(idx)
        self._dead_handlers.clear()
        self._sorted_cache = None
        self._active_listeners_cache = None

    def _remove_by_indices(self, indices: list[int]) -> None:
        """按索引批量移除监听器。"""
        if not indices:
            return
        for idx in indices:
            if 0 <= idx < len(self._listeners):
                handler_id = id(self._listeners[idx].handler)
                self._dead_handlers.add(handler_id)

        self._needs_cleanup = True
        self._active_listeners_cache = None
        self._sorted_cache = None

    # ========================================================================
    # ========================================================================

    @overload
    def once(
        self,
        handler: Callable[[T], None],
        /,
        *,
        priority: int = 0,
        condition: EventFilter | None = None,
        tag: str | None = None,
    ) -> Callable[[T], None]: ...

    @overload
    def once(
        self,
        handler: None = None,
        /,
        *,
        priority: int = 0,
        condition: EventFilter | None = None,
        tag: str | None = None,
    ) -> Callable[[Callable[[T], None]], Callable[[T], None]]: ...

    def once(
        self,
        handler: Callable[[T], None] | None = None,
        /,
        *,
        priority: int = 0,
        condition: EventFilter | None = None,
        tag: str | None = None,
    ) -> Callable[[T], None] | Callable[[Callable[[T], None]], Callable[[T], None]]:
        """一次性监听器。"""

        def _register(h: Callable[[T], None]) -> Callable[[T], None]:
            return self.on(
                h, priority=priority, once=True, condition=condition, tag=tag
            )

        if handler is not None:
            return _register(handler)

        return _register

    # ========================================================================
    # ========================================================================

    def __repr__(self) -> str:
        name = self._name or "<unnamed>"
        return f"EventEmitter(name={name!r}, listeners={self.count()})"

    def __len__(self) -> int:
        """返回监听器数量。"""
        return self.count()

    def __bool__(self) -> bool:
        """是否有监听器。"""
        return self.count() > 0

    def __call__(self, **kwargs: Any) -> EmitResult:
        """支持函数调用语法。"""
        return self.emit(**kwargs)
