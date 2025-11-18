"""测试执行策略。"""

from __future__ import annotations

import time

from symphra_event.execution.parallel import ParallelExecutor
from symphra_event.execution.sequential import SequentialExecutor
from symphra_event.types import Listener


class TestSequentialExecutor:
    """测试串行执行器。"""

    def test_empty_listeners(self) -> None:
        """测试空监听器列表。"""
        executor = SequentialExecutor()
        result = executor.execute(())

        assert result.success_count == 0
        assert result.total_count == 0
        assert len(result.errors) == 0

    def test_basic_execution(self) -> None:
        """测试基本执行。"""
        results: list[str] = []

        def handler1(**kwargs: object) -> None:
            results.append("handler1")

        def handler2(**kwargs: object) -> None:
            results.append("handler2")

        listeners = (
            Listener(handler=handler1, priority=100),
            Listener(handler=handler2, priority=50),
        )

        executor = SequentialExecutor()
        result = executor.execute(listeners, data="test")

        assert result.success_count == 2
        assert result.total_count == 2
        assert len(result.errors) == 0
        assert results == ["handler1", "handler2"]

    def test_with_condition(self) -> None:
        """测试条件过滤。"""
        results: list[str] = []

        def handler1(**kwargs: object) -> None:
            results.append("handler1")

        def handler2(**kwargs: object) -> None:
            results.append("handler2")

        def condition(kwargs: dict) -> bool:
            return kwargs.get("enabled", False)

        listeners = (
            Listener(handler=handler1, condition=condition),
            Listener(handler=handler2),
        )

        executor = SequentialExecutor()

        # 条件不满足
        result1 = executor.execute(listeners, enabled=False)
        assert result1.success_count == 1  # 只有 handler2
        assert results == ["handler2"]

        results.clear()

        # 条件满足
        result2 = executor.execute(listeners, enabled=True)
        assert result2.success_count == 2
        assert results == ["handler1", "handler2"]

    def test_error_isolation(self) -> None:
        """测试错误隔离。"""
        results: list[str] = []

        def handler1(**kwargs: object) -> None:
            results.append("handler1")

        def handler2(**kwargs: object) -> None:
            results.append("handler2")
            raise ValueError("Handler 2 failed")

        def handler3(**kwargs: object) -> None:
            results.append("handler3")

        listeners = (
            Listener(handler=handler1),
            Listener(handler=handler2),
            Listener(handler=handler3),
        )

        executor = SequentialExecutor()
        result = executor.execute(listeners)

        assert result.success_count == 2  # handler1 和 handler3
        assert result.total_count == 3
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
        assert results == ["handler1", "handler2", "handler3"]


class TestParallelExecutor:
    """测试并行执行器。"""

    def test_empty_listeners(self) -> None:
        """测试空监听器列表。"""
        executor = ParallelExecutor(max_workers=2)
        result = executor.execute(())

        assert result.success_count == 0
        assert result.total_count == 0
        assert len(result.errors) == 0

    def test_basic_parallel_execution(self) -> None:
        """测试基本并行执行。"""
        results: list[str] = []

        def handler1(**kwargs: object) -> None:
            time.sleep(0.01)
            results.append("handler1")

        def handler2(**kwargs: object) -> None:
            time.sleep(0.01)
            results.append("handler2")

        def handler3(**kwargs: object) -> None:
            time.sleep(0.01)
            results.append("handler3")

        listeners = (
            Listener(handler=handler1),
            Listener(handler=handler2),
            Listener(handler=handler3),
        )

        executor = ParallelExecutor(max_workers=3)
        start = time.time()
        result = executor.execute(listeners, data="test")
        elapsed = time.time() - start

        assert result.success_count == 3
        assert result.total_count == 3
        assert len(result.errors) == 0
        # 并行执行应该比串行快
        assert elapsed < 0.025  # 应该约 0.01 秒（并行）而非 0.03 秒（串行）

    def test_with_condition(self) -> None:
        """测试条件过滤。"""
        results: list[str] = []

        def handler1(**kwargs: object) -> None:
            results.append("handler1")

        def handler2(**kwargs: object) -> None:
            results.append("handler2")

        def condition(kwargs: dict) -> bool:
            return kwargs.get("enabled", False)

        listeners = (
            Listener(handler=handler1, condition=condition),
            Listener(handler=handler2),
        )

        executor = ParallelExecutor(max_workers=2)

        # 条件不满足
        result1 = executor.execute(listeners, enabled=False)
        assert result1.success_count == 1
        assert result1.total_count == 1  # 过滤后只有 1 个

        results.clear()

        # 条件满足
        result2 = executor.execute(listeners, enabled=True)
        assert result2.success_count == 2
        assert result2.total_count == 2

    def test_error_isolation(self) -> None:
        """测试错误隔离。"""

        def handler1(**kwargs: object) -> None:
            pass

        def handler2(**kwargs: object) -> None:
            raise ValueError("Handler 2 failed")

        def handler3(**kwargs: object) -> None:
            pass

        listeners = (
            Listener(handler=handler1),
            Listener(handler=handler2),
            Listener(handler=handler3),
        )

        executor = ParallelExecutor(max_workers=3)
        result = executor.execute(listeners)

        assert result.success_count == 2
        assert result.total_count == 3
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
