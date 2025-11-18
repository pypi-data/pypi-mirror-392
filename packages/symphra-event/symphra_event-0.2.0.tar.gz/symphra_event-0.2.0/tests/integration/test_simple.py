"""简单测试验证核心功能"""

from symphra_event import EventEmitter, emit, emitter


def test_basic_functionality() -> None:
    """测试基本功能。"""
    # 测试 EventEmitter
    emitter_instance = EventEmitter()
    calls = []

    @emitter_instance.on
    def handler(data: str) -> None:
        calls.append(data)

    emitter_instance.emit(data="test")
    assert len(calls) == 1
    assert calls[0] == "test"  # 注意：emit 传递的是 **kwargs


def test_global_decorator() -> None:
    """测试全局装饰器。"""
    calls = []

    @emitter("test_event")
    def handler(data: str) -> None:
        calls.append(data)

    emit("test_event", data="hello")
    assert len(calls) == 1


if __name__ == "__main__":
    test_basic_functionality()
    test_global_decorator()
    print("✅ All basic tests passed!")
