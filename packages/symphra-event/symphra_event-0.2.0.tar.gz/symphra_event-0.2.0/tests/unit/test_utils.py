"""测试 utils 模块的工具函数"""

from __future__ import annotations

import asyncio

import pytest

from symphra_event.utils import ensure_awaitable, is_coroutine_function


class TestIsCoroutineFunction:
    """测试 is_coroutine_function"""

    def test_sync_function(self) -> None:
        """测试同步函数"""

        def sync_func() -> None:
            pass

        assert is_coroutine_function(sync_func) is False

    def test_async_function(self) -> None:
        """测试异步函数"""

        async def async_func() -> None:
            pass

        assert is_coroutine_function(async_func) is True

    def test_async_lambda(self) -> None:
        """测试异步 lambda"""

        # lambda 不能是异步的，但可以使用 asyncio.coroutine
        def sync_lambda() -> None:
            return None

        assert is_coroutine_function(sync_lambda) is False


class TestEnsureAwaitable:
    """测试 ensure_awaitable"""

    @pytest.mark.asyncio
    async def test_ensure_awaitable_with_sync_function(self) -> None:
        """测试确保同步函数可等待"""

        def sync_func(x: int, y: int) -> int:
            return x + y

        result = await ensure_awaitable(sync_func, 1, 2)
        assert result == 3

    @pytest.mark.asyncio
    async def test_ensure_awaitable_with_async_function(self) -> None:
        """测试确保异步函数可等待"""

        async def async_func(x: int, y: int) -> int:
            await asyncio.sleep(0.001)  # 模拟异步操作
            return x + y

        result = await ensure_awaitable(async_func, 1, 2)
        assert result == 3

    @pytest.mark.asyncio
    async def test_ensure_awaitable_with_kwargs(self) -> None:
        """测试确保可等待并传递关键字参数"""

        def sync_func(x: int, y: int, z: int = 0) -> int:
            return x + y + z

        result = await ensure_awaitable(sync_func, 1, 2, z=3)
        assert result == 6

    @pytest.mark.asyncio
    async def test_ensure_awaitable_with_async_kwargs(self) -> None:
        """测试确保异步函数可等待并传递关键字参数"""

        async def async_func(x: int, y: int, z: int = 0) -> int:
            await asyncio.sleep(0.001)
            return x + y + z

        result = await ensure_awaitable(async_func, 1, 2, z=3)
        assert result == 6
