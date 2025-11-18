"""性能基准测试 - EventEmitter 核心性能。"""

from __future__ import annotations

from symphra_event.core.emitter import EventEmitter
from symphra_event.execution.parallel import ParallelExecutor
from symphra_event.execution.sequential import SequentialExecutor
from symphra_event.types import Listener


class TestEmitterPerformance:
    """EventEmitter 性能测试。"""

    def test_emit_performance(self, benchmark) -> None:
        """测试基本emit性能。"""
        emitter = EventEmitter()

        @emitter.on
        def handler(data: str) -> None:
            pass

        benchmark(emitter.emit, data="test")

    def test_emit_with_1000_listeners(self, benchmark) -> None:
        """测试1000个监听器的emit性能。"""
        emitter = EventEmitter()

        for i in range(1000):

            @emitter.on
            def handler(data: str, index=i) -> None:
                pass

        benchmark(emitter.emit, data="test")

    def test_on_registration_performance(self, benchmark) -> None:
        """测试监听器注册性能。"""
        emitter = EventEmitter()

        def register_handler() -> None:
            @emitter.on
            def handler(data: str) -> None:
                pass

            emitter.off(handler)  # 清理

        benchmark(register_handler)

    def test_off_performance(self, benchmark) -> None:
        """测试监听器移除性能。"""

        def setup():
            emitter = EventEmitter()

            def handler(data: str) -> None:
                pass

            emitter.on(handler)
            return emitter, handler

        emitter, handler = setup()
        benchmark(emitter.off, handler)

    def test_sequential_executor_performance(self, benchmark) -> None:
        """测试串行执行器性能。"""
        executor = SequentialExecutor()

        listeners = tuple(
            Listener(handler=lambda data: None, priority=0) for _ in range(100)
        )

        benchmark(executor.execute, listeners, data="test")

    def test_parallel_executor_performance(self, benchmark) -> None:
        """测试并行执行器性能。"""
        executor = ParallelExecutor(max_workers=4)

        listeners = tuple(
            Listener(handler=lambda data: None, priority=0) for _ in range(100)
        )

        benchmark(executor.execute, listeners, data="test")
