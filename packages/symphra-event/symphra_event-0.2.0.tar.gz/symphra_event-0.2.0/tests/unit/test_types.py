"""测试 types 模块的类型定义"""

from __future__ import annotations

from symphra_event.types import (
    CleanupStats,
    EmitResult,
    ExecutionMode,
    Listener,
    Priority,
)


class TestExecutionMode:
    """ExecutionMode 枚举测试"""

    def test_execution_mode_values(self) -> None:
        """测试 ExecutionMode 的值"""
        assert ExecutionMode.SEQUENTIAL.value == 1
        assert ExecutionMode.PARALLEL.value == 2
        assert ExecutionMode.PIPELINE.value == 3

    def test_execution_mode_str(self) -> None:
        """测试 ExecutionMode 的字符串表示"""
        assert str(ExecutionMode.SEQUENTIAL) == "sequential"
        assert str(ExecutionMode.PARALLEL) == "parallel"
        assert str(ExecutionMode.PIPELINE) == "pipeline"


class TestPriority:
    """Priority 枚举测试"""

    def test_priority_values(self) -> None:
        """测试 Priority 的值"""
        assert int(Priority.CRITICAL) == 1000
        assert int(Priority.HIGH) == 100
        assert int(Priority.NORMAL) == 0
        assert int(Priority.LOW) == -100
        assert int(Priority.LOWEST) == -1000


class TestListener:
    """Listener 数据类测试"""

    def test_listener_creation(self) -> None:
        """测试创建 Listener"""

        def handler(data: dict[str, str]) -> None:
            pass

        listener = Listener(handler=handler, priority=100, once=True, tag="test")

        assert listener.handler == handler
        assert listener.priority == 100
        assert listener.once is True
        assert listener.tag == "test"
        assert listener.condition is None

    def test_listener_hash(self) -> None:
        """测试 Listener 的哈希"""

        def handler1(data: dict[str, str]) -> None:
            pass

        def handler2(data: dict[str, str]) -> None:
            pass

        listener1 = Listener(handler=handler1)
        listener2 = Listener(handler=handler2)
        listener1_duplicate = Listener(handler=handler1)

        # 相同 handler 应该有相同的哈希
        assert hash(listener1) == hash(listener1_duplicate)
        # 不同 handler 应该有不同的哈希
        assert hash(listener1) != hash(listener2)

    def test_listener_equality(self) -> None:
        """测试 Listener 的相等性"""

        def handler1(data: dict[str, str]) -> None:
            pass

        def handler2(data: dict[str, str]) -> None:
            pass

        listener1 = Listener(handler=handler1)
        listener2 = Listener(handler=handler2)
        listener1_duplicate = Listener(handler=handler1, priority=50)  # 不同优先级

        # 相同 handler 应该相等（忽略其他属性）
        assert listener1 == listener1_duplicate
        # 不同 handler 不应该相等
        assert listener1 != listener2


class TestEmitResult:
    """EmitResult 数据类测试"""

    def test_emit_result_creation(self) -> None:
        """测试创建 EmitResult"""
        result = EmitResult(success_count=3, total_count=5, elapsed_ms=10.5)

        assert result.success_count == 3
        assert result.total_count == 5
        assert result.elapsed_ms == 10.5
        assert len(result.errors) == 0

    def test_emit_result_with_errors(self) -> None:
        """测试带错误的 EmitResult"""
        errors = (ValueError("error1"), RuntimeError("error2"))
        result = EmitResult(
            success_count=3, total_count=5, errors=errors, elapsed_ms=10.5
        )

        assert result.success_count == 3
        assert result.total_count == 5
        assert result.errors == errors
        assert result.failed_count == 2
        assert result.has_errors is True

    def test_emit_result_success_rate(self) -> None:
        """测试 EmitResult 的成功率"""
        # 全部成功
        result1 = EmitResult(success_count=5, total_count=5)
        assert result1.success_rate == 1.0

        # 部分成功
        result2 = EmitResult(success_count=3, total_count=5)
        assert result2.success_rate == 0.6

        # 全部失败
        result3 = EmitResult(success_count=0, total_count=5)
        assert result3.success_rate == 0.0

        # 没有监听器
        result4 = EmitResult(success_count=0, total_count=0)
        assert result4.success_rate == 1.0


class TestCleanupStats:
    """CleanupStats 数据类测试"""

    def test_cleanup_stats_creation(self) -> None:
        """测试创建 CleanupStats"""
        stats = CleanupStats(
            dead_refs_removed=10, listeners_remaining=5, elapsed_ms=2.5
        )

        assert stats.dead_refs_removed == 10
        assert stats.listeners_remaining == 5
        assert stats.elapsed_ms == 2.5
