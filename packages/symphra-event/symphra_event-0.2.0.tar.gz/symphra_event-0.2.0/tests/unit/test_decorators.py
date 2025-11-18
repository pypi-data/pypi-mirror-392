"""测试全局装饰器"""

from __future__ import annotations

import pytest

from symphra_event import emit, emitter, events
from symphra_event.exceptions import InvalidNamespaceError


class TestGlobalDecorator:
    """全局装饰器测试套件"""

    def test_emitter_decorator(self) -> None:
        """测试 emitter 装饰器"""
        calls: list[str] = []

        @emitter("test.basic")
        def handler(data: str) -> None:
            calls.append(data)

        result = emit("test.basic", data="hello")

        assert result.success_count == 1
        assert len(calls) == 1
        assert calls[0] == "hello"

    def test_emit_nonexistent_namespace(self) -> None:
        """测试触发不存在的命名空间"""
        with pytest.raises(InvalidNamespaceError):
            emit("nonexistent.namespace", data="test")

    def test_events_proxy(self) -> None:
        """测试 events 代理"""
        calls: list[int] = []

        @emitter("user.login")
        def handler(user_id: int) -> None:
            calls.append(user_id)

        # 使用 events 代理
        events.user.login.emit(user_id=123)

        assert len(calls) == 1
        assert calls[0] == 123

    def test_namespace_with_priority(self) -> None:
        """测试命名空间与优先级"""
        calls: list[str] = []

        @emitter("order", priority=100)
        def high_priority(action: str) -> None:
            calls.append("high")

        @emitter("order", priority=10)
        def low_priority(action: str) -> None:
            calls.append("low")

        emit("order", action="create")

        assert calls == ["high", "low"]
