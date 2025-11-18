"""symphra_event.utils - 工具函数"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import Any

__all__ = [
    "ensure_awaitable",
    "is_coroutine_function",
]


def is_coroutine_function(func: Callable[..., Any]) -> bool:
    """检查函数是否是协程函数。

    Args:
        func: 要检查的函数

    Returns:
        是否是协程函数
    """
    return asyncio.iscoroutinefunction(func) or inspect.iscoroutinefunction(func)


async def ensure_awaitable(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """确保函数结果是可等待的。

    如果是协程函数，直接 await；
    如果是同步函数，在线程池中执行。

    Args:
        func: 要执行的函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数执行结果
    """
    if is_coroutine_function(func):
        return await func(*args, **kwargs)
    else:
        # 在线程池中执行同步函数
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
