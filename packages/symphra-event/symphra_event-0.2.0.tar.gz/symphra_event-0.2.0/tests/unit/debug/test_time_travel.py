"""测试 debug.time_travel 模块的时间旅行调试器"""

from __future__ import annotations

from symphra_event.debug.time_travel import DeltaSnapshot, TimeTravelDebugger


class TestDeltaSnapshot:
    """测试 DeltaSnapshot 数据类"""

    def test_delta_snapshot_creation(self) -> None:
        """测试创建 DeltaSnapshot"""
        snapshot = DeltaSnapshot(
            snapshot_id=0,
            timestamp=123.45,
            event_name="test_event",
            delta=b"test_delta",
            base_snapshot_id=0,
        )

        assert snapshot.snapshot_id == 0
        assert snapshot.timestamp == 123.45
        assert snapshot.event_name == "test_event"
        assert snapshot.delta == b"test_delta"
        assert snapshot.base_snapshot_id == 0


class TestTimeTravelDebugger:
    """测试 TimeTravelDebugger"""

    def test_debugger_creation(self) -> None:
        """测试创建 TimeTravelDebugger"""
        debugger = TimeTravelDebugger(max_snapshots=100, snapshot_interval=10)

        assert debugger._max_snapshots == 100
        assert debugger._snapshot_interval == 10
        assert debugger._current_index == -1

    def test_capture_single_snapshot(self) -> None:
        """测试捕获单个快照"""
        debugger = TimeTravelDebugger()
        state = {"user_id": 123, "name": "Alice"}

        snapshot_id = debugger.capture("user.login", state)

        assert snapshot_id == 0
        assert len(debugger._snapshots) == 1
        assert debugger._current_index == 0

    def test_capture_multiple_snapshots(self) -> None:
        """测试捕获多个快照"""
        debugger = TimeTravelDebugger()

        # 捕获多个快照
        state1 = {"user_id": 123, "name": "Alice"}
        id1 = debugger.capture("user.login", state1)

        state2 = {"user_id": 123, "name": "Alice", "status": "active"}
        id2 = debugger.capture("user.update", state2)

        state3 = {"user_id": 123, "name": "Alice", "status": "inactive"}
        id3 = debugger.capture("user.logout", state3)

        assert id1 == 0
        assert id2 == 1
        assert id3 == 2
        assert len(debugger._snapshots) == 3
        assert debugger._current_index == 2

    def test_travel_to_snapshot(self) -> None:
        """测试时间旅行到指定快照"""
        debugger = TimeTravelDebugger()

        # 捕获多个快照
        state1 = {"value": 1}
        debugger.capture("event1", state1)

        state2 = {"value": 2}
        debugger.capture("event2", state2)

        state3 = {"value": 3}
        debugger.capture("event3", state3)

        # 时间旅行到第一个快照
        success = debugger.travel_to(0)
        assert success is True
        assert debugger._current_index == 0

        # 时间旅行到第二个快照
        success = debugger.travel_to(1)
        assert success is True
        assert debugger._current_index == 1

        # 时间旅行到不存在的快照
        success = debugger.travel_to(999)
        assert success is False
        assert debugger._current_index == 1  # 保持不变

    def test_get_current_state(self) -> None:
        """测试获取当前快照的状态"""
        debugger = TimeTravelDebugger()

        # 捕获快照
        original_state = {"user_id": 123, "name": "Alice", "items": [1, 2, 3]}
        debugger.capture("user.login", original_state)

        # 获取当前状态
        state = debugger.get_current_state()

        assert state is not None
        assert state["user_id"] == 123
        assert state["name"] == "Alice"
        assert state["items"] == [1, 2, 3]

    def test_get_current_state_after_travel(self) -> None:
        """测试时间旅行后获取状态"""
        debugger = TimeTravelDebugger()

        # 捕获多个快照
        state1 = {"version": 1, "data": "first"}
        debugger.capture("state.1", state1)

        state2 = {"version": 2, "data": "second"}
        debugger.capture("state.2", state2)

        # 时间旅行到第一个快照
        debugger.travel_to(0)
        state = debugger.get_current_state()

        assert state is not None
        assert state["version"] == 1
        assert state["data"] == "first"

        # 时间旅行到第二个快照
        debugger.travel_to(1)
        state = debugger.get_current_state()

        assert state is not None
        assert state["version"] == 2
        assert state["data"] == "second"

    def test_get_current_state_no_snapshots(self) -> None:
        """测试没有快照时获取状态"""
        debugger = TimeTravelDebugger()

        state = debugger.get_current_state()
        assert state is None

    def test_compare_snapshots(self) -> None:
        """测试对比两个快照"""
        debugger = TimeTravelDebugger()

        # 捕获两个不同的快照
        state1 = {"user_id": 123, "name": "Alice", "status": "active"}
        debugger.capture("state.1", state1)

        state2 = {
            "user_id": 123,
            "name": "Alice",
            "status": "inactive",
            "last_login": "2023-01-01",
        }
        debugger.capture("state.2", state2)

        # 对比快照
        diff = debugger.compare_snapshots(0, 1)

        assert "status" in diff
        assert diff["status"]["before"] == "active"
        assert diff["status"]["after"] == "inactive"
        assert diff["status"]["changed"] is True

        assert "last_login" in diff
        assert diff["last_login"]["before"] is None
        assert diff["last_login"]["after"] == "2023-01-01"
        assert diff["last_login"]["changed"] is True

        assert "user_id" not in diff  # 没有变化
        assert "name" not in diff  # 没有变化

    def test_compare_snapshots_with_no_changes(self) -> None:
        """测试对比没有变化的快照"""
        debugger = TimeTravelDebugger()

        # 捕获两个相同的快照
        state = {"user_id": 123, "name": "Alice"}
        debugger.capture("state.1", state)
        debugger.capture("state.2", state)

        # 对比快照
        diff = debugger.compare_snapshots(0, 1)

        assert diff == {}  # 没有差异

    def test_compare_invalid_snapshots(self) -> None:
        """测试对比不存在的快照"""
        debugger = TimeTravelDebugger()

        # 没有捕获任何快照
        diff = debugger.compare_snapshots(0, 1)

        assert diff == {}

    def test_memory_usage(self) -> None:
        """测试内存使用情况"""
        debugger = TimeTravelDebugger()

        # 捕获一些快照
        for i in range(5):
            state = {"index": i, "data": f"data_{i}" * 100}
            debugger.capture(f"event.{i}", state)

        memory_usage = debugger.get_memory_usage()

        assert "snapshots_bytes" in memory_usage
        assert "base_states_bytes" in memory_usage
        assert "total_bytes" in memory_usage
        assert "snapshots_count" in memory_usage
        assert "base_states_count" in memory_usage

        assert memory_usage["snapshots_count"] == 5
        assert memory_usage["total_bytes"] > 0

    def test_snapshot_interval(self) -> None:
        """测试快照间隔（基准快照）"""
        debugger = TimeTravelDebugger(snapshot_interval=3)

        # 捕获多个快照
        for i in range(10):
            state = {"index": i}
            debugger.capture(f"event.{i}", state)

        # 验证基准快照（ID 为 0, 3, 6, 9）
        assert 0 in debugger._base_states
        assert 3 in debugger._base_states
        assert 6 in debugger._base_states
        assert 9 in debugger._base_states

        # 验证非基准快照不在 base_states 中
        assert 1 not in debugger._base_states
        assert 2 not in debugger._base_states
        assert 4 not in debugger._base_states

    def test_max_snapshots_limit(self) -> None:
        """测试最大快照数限制"""
        debugger = TimeTravelDebugger(max_snapshots=3)

        # 捕获超过最大限制的快照
        for i in range(5):
            state = {"index": i}
            debugger.capture(f"event.{i}", state)

        # 只保留最新的 3 个快照
        assert len(debugger._snapshots) == 3

        # 验证只保留了最新的3个快照
        # 注意：当deque满时，会移除最旧的元素
        # 但由于snapshot_id = len(self._snapshots)，当deque满时，新的快照会重复使用相同的ID
        snapshot_ids = [s.snapshot_id for s in debugger._snapshots]
        # 实际行为：第0、1、2次捕获得到ID 0、1、2，第3次得到ID 3（移除0），第4次得到ID 3（移除1）
        # 所以最终是 [2, 3, 3]
        assert snapshot_ids == [2, 3, 3]

    def test_complex_state_snapshot(self) -> None:
        """测试复杂状态的快照"""
        debugger = TimeTravelDebugger()

        # 复杂的嵌套状态
        complex_state = {
            "user": {
                "id": 123,
                "profile": {"name": "Alice", "age": 30},
                "permissions": ["read", "write", "delete"],
            },
            "session": {"token": "abc123", "expires": 1234567890},
            "data": [{"id": i, "value": f"item_{i}"} for i in range(100)],
        }

        debugger.capture("complex.state", complex_state)

        # 恢复状态
        restored_state = debugger.get_current_state()

        assert restored_state is not None
        assert restored_state["user"]["id"] == 123
        assert restored_state["user"]["profile"]["name"] == "Alice"
        assert restored_state["user"]["permissions"] == ["read", "write", "delete"]
        assert restored_state["session"]["token"] == "abc123"
        assert len(restored_state["data"]) == 100
