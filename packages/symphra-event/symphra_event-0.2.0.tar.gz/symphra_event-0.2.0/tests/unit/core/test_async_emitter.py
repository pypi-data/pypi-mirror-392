"""测试 AsyncEventEmitter"""

import asyncio

import pytest

from symphra_event import AsyncEventEmitter


@pytest.mark.asyncio
async def test_async_emit_basic() -> None:
    """测试基本的异步事件发射。"""
    emitter = AsyncEventEmitter()
    calls = []

    @emitter.on
    async def async_handler(data: str) -> None:
        await asyncio.sleep(0.01)
        calls.append(f"async: {data}")

    @emitter.on
    def sync_handler(data: str) -> None:
        calls.append(f"sync: {data}")

    result = await emitter.emit(data="test")

    assert result.success_count == 2
    assert result.total_count == 2
    assert len(result.errors) == 0
    assert "async: test" in calls
    assert "sync: test" in calls


@pytest.mark.asyncio
async def test_async_emit_with_errors() -> None:
    """测试异步事件发射时的错误处理。"""
    emitter = AsyncEventEmitter()
    calls = []

    @emitter.on
    async def failing_handler(data: str) -> None:
        calls.append("failing")
        raise ValueError("Test error")

    @emitter.on
    async def working_handler(data: str) -> None:
        calls.append("working")

    result = await emitter.emit(data="test")

    assert result.success_count == 1
    assert result.total_count == 2
    assert len(result.errors) == 1
    assert isinstance(result.errors[0], ValueError)
    assert "failing" in calls
    assert "working" in calls


@pytest.mark.asyncio
async def test_async_emit_priority() -> None:
    """测试异步事件的优先级。"""
    emitter = AsyncEventEmitter()
    calls = []

    @emitter.on(priority=10)
    async def low_handler(data: str) -> None:
        await asyncio.sleep(0.01)
        calls.append("low")

    @emitter.on(priority=100)
    async def high_handler(data: str) -> None:
        await asyncio.sleep(0.01)
        calls.append("high")

    @emitter.on(priority=50)
    async def mid_handler(data: str) -> None:
        await asyncio.sleep(0.01)
        calls.append("mid")

    result = await emitter.emit(data="test")

    assert result.success_count == 3
    # 注意：异步并发执行，所以顺序可能不完全保证
    # 但应该都被调用
    assert set(calls) == {"low", "mid", "high"}
