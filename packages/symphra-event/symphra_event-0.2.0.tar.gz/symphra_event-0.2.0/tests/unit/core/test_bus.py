"""测试 EventBus"""

import pytest

from symphra_event import EventBus, EventEmitter
from symphra_event.exceptions import InvalidNamespaceError


def test_eventbus_create() -> None:
    """测试创建命名的事件发射器。"""
    EventBus.clear()  # 清理

    emitter = EventBus.create("test")
    assert isinstance(emitter, EventEmitter)
    assert emitter._name == "test"


def test_eventbus_create_duplicate() -> None:
    """测试创建重复名称的发射器。"""
    EventBus.clear()

    EventBus.create("test")

    with pytest.raises(InvalidNamespaceError):
        EventBus.create("test")

    # 使用 overwrite 应该成功
    emitter = EventBus.create("test", overwrite=True)
    assert isinstance(emitter, EventEmitter)


def test_eventbus_get() -> None:
    """测试获取事件发射器。"""
    EventBus.clear()

    EventBus.create("test")

    emitter = EventBus.get("test")
    assert emitter is not None
    assert emitter._name == "test"

    # 获取不存在的
    assert EventBus.get("nonexistent") is None


def test_eventbus_get_or_create() -> None:
    """测试获取或创建事件发射器。"""
    EventBus.clear()

    # 首次调用：创建
    emitter1 = EventBus.get_or_create("test")
    assert isinstance(emitter1, EventEmitter)

    # 再次调用：获取
    emitter2 = EventBus.get_or_create("test")
    assert emitter1 is emitter2


def test_eventbus_remove() -> None:
    """测试移除事件发射器。"""
    EventBus.clear()

    EventBus.create("test")
    assert EventBus.remove("test") is True
    assert EventBus.get("test") is None

    # 移除不存在的
    assert EventBus.remove("nonexistent") is False


def test_eventbus_list() -> None:
    """测试列出所有事件发射器。"""
    EventBus.clear()

    EventBus.create("test1")
    EventBus.create("test2")
    EventBus.create("test3")

    names = EventBus.list()
    assert len(names) == 3
    assert "test1" in names
    assert "test2" in names
    assert "test3" in names


def test_eventbus_stats() -> None:
    """测试统计信息。"""
    EventBus.clear()

    emitter1 = EventBus.create("test1")
    emitter2 = EventBus.create("test2")

    @emitter1.on
    def handler1(data: str) -> None:
        pass

    @emitter2.on
    def handler2(data: str) -> None:
        pass

    @emitter2.on
    def handler3(data: str) -> None:
        pass

    stats = EventBus.stats()
    assert stats["total"] == 2
    assert "test1" in stats["names"]
    assert "test2" in stats["names"]
    assert stats["listeners"]["test1"] == 1
    assert stats["listeners"]["test2"] == 2
