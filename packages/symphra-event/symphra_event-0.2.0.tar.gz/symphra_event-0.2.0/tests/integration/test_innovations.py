"""测试创新功能模块。"""

import time

from symphra_event import (
    BatchProcessor,
    DependencyAnalyzer,
    TimeTravelDebugger,
    ZeroCopyBuffer,
    ZeroCopyPool,
)


def test_batch_processor_basic() -> None:
    """测试批量处理器基础功能。"""
    processor = BatchProcessor[dict](batch_size=3, flush_interval_ms=100.0)

    results: list[list[dict]] = []

    @processor.register("test.event")
    def handle_batch(events: list[dict]) -> None:
        results.append(events)

    # 添加事件
    for i in range(5):
        processor.add("test.event", {"id": i})

    # 应该触发一次批量处理（前3个）
    assert len(results) == 1
    assert len(results[0]) == 3

    # 手动刷新剩余的
    processor.flush()
    assert len(results) == 2
    assert len(results[1]) == 2

    processor.stop()


def test_zero_copy_buffer() -> None:
    """测试零拷贝缓冲区。"""
    buffer = ZeroCopyBuffer(size=1024)

    # 写入数据
    data = b"Hello, World!"
    written = buffer.write(data)
    assert written == len(data)
    assert buffer.position == len(data)

    # 读取数据（零拷贝）
    view = buffer.read()
    assert bytes(view) == data

    # 清空
    buffer.clear()
    assert buffer.position == 0


def test_zero_copy_pool() -> None:
    """测试零拷贝缓冲区池。"""
    pool = ZeroCopyPool(pool_size=2, buffer_size=512)

    # 分配缓冲区
    buf1 = pool.allocate()
    buf2 = pool.allocate()

    assert buf1 is not None
    assert buf2 is not None

    # 释放
    pool.release(buf1)
    stats = pool.get_stats()
    assert stats["allocated_buffers"] == 1
    assert stats["available_buffers"] == 1


def test_dependency_analyzer() -> None:
    """测试依赖分析器。"""
    analyzer = DependencyAnalyzer(max_history=100, time_window_ms=50.0)

    # 记录执行
    for _ in range(10):
        analyzer.record_start("validate")
        time.sleep(0.001)
        analyzer.record_end("validate")

        analyzer.record_start("save")
        time.sleep(0.001)
        analyzer.record_end("save")

    # 分析依赖
    deps = analyzer.analyze_dependencies(min_confidence=0.5)
    assert len(deps) > 0

    # 获取性能统计
    stats = analyzer.get_performance_stats()
    assert "validate" in stats
    assert "save" in stats


def test_time_travel_debugger() -> None:
    """测试时间旅行调试器。"""
    debugger = TimeTravelDebugger(max_snapshots=10, snapshot_interval=3)

    # 捕获状态
    state1 = {"user_id": 123, "name": "Alice"}
    snapshot_id1 = debugger.capture("user.login", state1)

    state2 = {"user_id": 123, "name": "Alice", "status": "active"}
    snapshot_id2 = debugger.capture("user.update", state2)

    # 时间旅行
    assert debugger.travel_to(snapshot_id1)
    restored = debugger.get_current_state()
    assert restored == state1

    assert debugger.travel_to(snapshot_id2)
    restored = debugger.get_current_state()
    assert restored == state2

    # 对比
    diff = debugger.compare_snapshots(snapshot_id1, snapshot_id2)
    assert "status" in diff

    # 内存使用
    memory = debugger.get_memory_usage()
    assert memory["snapshots_count"] == 2
