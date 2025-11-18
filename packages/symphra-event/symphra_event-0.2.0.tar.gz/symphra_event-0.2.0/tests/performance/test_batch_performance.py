"""性能基准测试 - 批量处理优化器。"""

from __future__ import annotations

from symphra_event.optimizer.batch import BatchProcessor


class TestBatchProcessorPerformance:
    """BatchProcessor 性能测试。"""

    def test_batch_add_performance(self, benchmark) -> None:
        """测试批量添加事件性能。"""
        processor = BatchProcessor(batch_size=1000, flush_interval_ms=1000.0)

        @processor.register("test.event")
        def handle_batch(events: list) -> None:
            pass

        def add_events() -> None:
            for i in range(100):
                processor.add("test.event", {"id": i})

        benchmark(add_events)
        processor.stop()

    def test_batch_flush_performance(self, benchmark) -> None:
        """测试批量刷新性能。"""
        processor = BatchProcessor(batch_size=10000, flush_interval_ms=10000.0)

        @processor.register("test.event")
        def handle_batch(events: list) -> None:
            pass

        # 添加1000个事件
        for i in range(1000):
            processor.add("test.event", {"id": i})

        benchmark(processor.flush, "test.event")
        processor.stop()
