"""core/async_emitter 单元测试 - 补充覆盖率。"""

from __future__ import annotations

import asyncio

import pytest

from symphra_event.core.async_emitter import AsyncEventEmitter


class TestAsyncEmitterAdvanced:
    """AsyncEventEmitter 高级功能测试。"""

    @pytest.mark.asyncio
    async def test_mixed_sync_async_handlers(self) -> None:
        """测试混合同步和异步处理器。"""
        emitter = AsyncEventEmitter()
        results = []

        @emitter.on
        def sync_handler(data: str) -> None:
            results.append(f"sync_{data}")

        @emitter.on
        async def async_handler(data: str) -> None:
            await asyncio.sleep(0.01)
            results.append(f"async_{data}")

        await emitter.emit(data="test")

        assert "sync_test" in results
        assert "async_test" in results
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_async_error_isolation(self) -> None:
        """测试异步错误隔离。"""
        emitter = AsyncEventEmitter()
        results = []

        @emitter.on
        async def failing_handler(data: str) -> None:
            results.append("failing")
            raise ValueError("async error")

        @emitter.on
        async def working_handler(data: str) -> None:
            results.append("working")

        result = await emitter.emit(data="test")

        assert result.has_errors
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
        assert "failing" in results
        assert "working" in results
