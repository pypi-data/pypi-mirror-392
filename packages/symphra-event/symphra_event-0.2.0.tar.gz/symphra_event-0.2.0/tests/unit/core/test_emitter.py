"""测试 EventEmitter 核心功能"""

from __future__ import annotations

from symphra_event import EventEmitter


class TestEventEmitter:
    """EventEmitter 测试套件"""

    def test_create_emitter(self) -> None:
        """测试创建 EventEmitter"""
        emitter = EventEmitter[dict[str, str]]()
        assert emitter.count() == 0
        assert len(emitter) == 0
        assert not emitter

    def test_on_decorator(self) -> None:
        """测试 on 装饰器"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[dict[str, str]] = []

        @emitter.on
        def handler(data: dict[str, str]) -> None:
            calls.append(data)

        assert emitter.count() == 1
        assert bool(emitter)

    def test_emit_basic(self) -> None:
        """测试基础 emit"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[dict[str, str]] = []

        @emitter.on
        def handler(data: dict[str, str]) -> None:
            calls.append(data)

        result = emitter.emit(data="test")

        assert result.success_count == 1
        assert result.total_count == 1
        assert not result.has_errors
        assert result.success_rate == 1.0
        assert len(calls) == 1
        # emit以关键字参数传递，处理器接收时直接获得值
        assert calls[0] == "test"

    def test_emit_multiple_handlers(self) -> None:
        """测试多个处理器"""
        emitter = EventEmitter[dict[str, int]]()
        calls: list[str] = []

        @emitter.on
        def handler1(value: int) -> None:
            calls.append("handler1")

        @emitter.on
        def handler2(value: int) -> None:
            calls.append("handler2")

        @emitter.on
        def handler3(value: int) -> None:
            calls.append("handler3")

        result = emitter.emit(value=123)

        assert result.success_count == 3
        assert result.total_count == 3
        assert len(calls) == 3

    def test_priority_ordering(self) -> None:
        """测试优先级排序"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[str] = []

        @emitter.on(priority=10)
        def low(data: str) -> None:
            calls.append("low")

        @emitter.on(priority=100)
        def high(data: str) -> None:
            calls.append("high")

        @emitter.on(priority=50)
        def mid(data: str) -> None:
            calls.append("mid")

        emitter.emit(data="test")

        assert calls == ["high", "mid", "low"]

    def test_once_handler(self) -> None:
        """测试一次性处理器"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[str] = []

        @emitter.on(once=True)
        def handler(data: str) -> None:
            calls.append(data)

        assert emitter.count() == 1

        emitter.emit(data="first")
        assert len(calls) == 1
        assert calls[0] == "first"
        assert emitter.count() == 0  # 自动移除

        emitter.emit(data="second")
        assert len(calls) == 1  # 不再触发

    def test_condition_filter(self) -> None:
        """测试条件过滤"""
        emitter = EventEmitter[dict[str, int]]()
        calls: list[int] = []

        @emitter.on(condition=lambda kwargs: kwargs["value"] > 10)
        def handler(value: int) -> None:
            calls.append(value)

        emitter.emit(value=5)  # 不触发
        assert len(calls) == 0

        emitter.emit(value=15)  # 触发
        assert len(calls) == 1
        assert calls[0] == 15

    def test_off_by_handler(self) -> None:
        """测试按处理器移除"""
        emitter = EventEmitter[dict[str, str]]()

        @emitter.on
        def handler(data: str) -> None:
            pass

        assert emitter.count() == 1

        removed = emitter.off(handler)
        assert removed == 1
        assert emitter.count() == 0

    def test_off_by_tag(self) -> None:
        """测试按标签移除"""
        emitter = EventEmitter[dict[str, str]]()

        @emitter.on(tag="group1")
        def handler1(data: str) -> None:
            pass

        @emitter.on(tag="group1")
        def handler2(data: str) -> None:
            pass

        @emitter.on(tag="group2")
        def handler3(data: str) -> None:
            pass

        assert emitter.count() == 3

        removed = emitter.off(tag="group1")
        assert removed == 2
        assert emitter.count() == 1

    def test_exception_isolation(self) -> None:
        """测试异常隔离"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[str] = []

        @emitter.on
        def failing_handler(data: str) -> None:
            calls.append("failing")
            raise ValueError("Error")

        @emitter.on
        def working_handler(data: str) -> None:
            calls.append("working")

        result = emitter.emit(data="test")

        assert result.success_count == 1
        assert result.failed_count == 1
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
        assert calls == ["failing", "working"]

    def test_clear(self) -> None:
        """测试清空"""
        emitter = EventEmitter[dict[str, str]]()

        @emitter.on
        def handler1(data: str) -> None:
            pass

        @emitter.on
        def handler2(data: str) -> None:
            pass

        assert emitter.count() == 2

        emitter.clear()
        assert emitter.count() == 0

    def test_repr(self) -> None:
        """测试 repr"""
        emitter = EventEmitter[dict[str, str]](name="test")
        assert "test" in repr(emitter)
        assert "listeners=0" in repr(emitter)

    def test_call_syntax(self) -> None:
        """测试函数调用语法"""
        emitter = EventEmitter[dict[str, str]]()
        calls: list[str] = []

        @emitter.on
        def handler(data: str) -> None:
            calls.append(data)

        # 使用 emitter(data=...) 语法
        result = emitter(data="test")

        assert result.success_count == 1
        assert calls[0] == "test"
