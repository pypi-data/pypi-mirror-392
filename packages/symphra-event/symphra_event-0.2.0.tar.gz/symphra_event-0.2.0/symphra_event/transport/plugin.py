"""零拷贝传输插件。

该插件封装了零拷贝传输功能。
"""

from __future__ import annotations

from typing import Any, final

from ..plugin.base import Plugin, PluginMetadata
from ..transport.zero_copy import ZeroCopyPool

__all__ = ["ZeroCopyPlugin"]


@final
class ZeroCopyPlugin(Plugin):
    """零拷贝传输插件。

    提供零拷贝事件数据传递能力：
    1. memoryview 零拷贝
    2. buffer protocol 支持
    3. 对象池复用
    4. 写时复制（COW）

    Examples:
        >>> plugin = ZeroCopyPlugin(pool_size=10, buffer_size=4096)
        >>> registry.register(plugin)
        >>> registry.install("zero-copy", context=emitter)
        >>>
        >>> # 获取缓冲池
        >>> pool = plugin.pool
        >>> buffer = pool.acquire()
        >>> buffer.write(b"data")
        >>> pool.release(buffer)
    """

    __slots__ = (
        "_buffer_size",
        "_pool",
        "_pool_size",
    )

    def __init__(
        self,
        pool_size: int = 10,
        buffer_size: int = 4096,
    ) -> None:
        """初始化零拷贝插件。

        Args:
            pool_size: 缓冲池大小（默认 10）
            buffer_size: 单个缓冲区大小（字节，默认 4096）
        """
        self._pool_size = pool_size
        self._buffer_size = buffer_size
        self._pool: ZeroCopyPool | None = None

    @property
    def metadata(self) -> PluginMetadata:
        """插件元数据。"""
        return PluginMetadata(
            name="zero-copy",
            version="1.0.0",
            description="Zero-copy event data transport",
            author="Symphra",
            dependencies=[],
        )

    def install(self, context: Any = None) -> None:
        """安装插件。

        Args:
            context: 安装上下文（可选）
        """
        self._pool = ZeroCopyPool(
            pool_size=self._pool_size,
            buffer_size=self._buffer_size,
        )

    def uninstall(self) -> None:
        """卸载插件。"""
        # ZeroCopyPool 不需要显式清理
        self._pool = None

    @property
    def pool(self) -> ZeroCopyPool:
        """获取零拷贝缓冲池实例。

        Returns:
            ZeroCopyPool 实例

        Raises:
            RuntimeError: 如果插件未安装
        """
        if self._pool is None:
            raise RuntimeError(
                "Plugin 'zero-copy' is not installed. Call install() first."
            )
        return self._pool
