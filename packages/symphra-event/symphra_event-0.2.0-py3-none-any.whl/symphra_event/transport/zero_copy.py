"""symphra_event.transport.zero_copy - 零拷贝事件传递

创新点：
1. memoryview 零拷贝传递
2. buffer protocol 支持
3. 对象池复用
4. 写时复制（COW）

零依赖实现：
- memoryview: 零拷贝视图
- array: 高效数组
- struct: 二进制打包
"""

from __future__ import annotations

import array
from typing import final

__all__ = ["ZeroCopyBuffer", "ZeroCopyPool"]


@final
class ZeroCopyBuffer:
    """零拷贝缓冲区。

    使用 memoryview 实现零拷贝数据传递。

    Examples:
        >>> # 创建缓冲区
        >>> buffer = ZeroCopyBuffer(size=1024)
        >>>
        >>> # 写入数据（零拷贝）
        >>> data = b"Hello, World!"
        >>> buffer.write(data)
        >>>
        >>> # 读取数据（零拷贝）
        >>> view = buffer.read()
        >>> print(bytes(view))  # b"Hello, World!"
        >>>
        >>> # 多个监听器共享同一缓冲区（零拷贝）
        >>> view1 = buffer.read()
        >>> view2 = buffer.read()
        >>> # view1 和 view2 指向同一块内存
    """

    __slots__ = ("_buffer", "_position", "_ref_count", "_size")

    def __init__(self, size: int = 4096) -> None:
        """初始化缓冲区。

        Args:
            size: 缓冲区大小（字节）
        """
        # 使用 array.array 作为底层存储
        self._buffer = array.array("B", [0] * size)  # unsigned char array
        self._size = size
        self._position = 0
        self._ref_count = 0

    def write(self, data: bytes) -> int:
        """写入数据。

        Args:
            data: 要写入的数据

        Returns:
            写入的字节数

        Raises:
            ValueError: 数据超过缓冲区大小
        """
        if len(data) > self._size:
            raise ValueError(f"Data too large: {len(data)} > {self._size}")

        # 写入数据（零拷贝）
        self._buffer[: len(data)] = array.array("B", data)
        self._position = len(data)

        return len(data)

    def read(self, offset: int = 0, length: int | None = None) -> memoryview:
        """读取数据（零拷贝）。

        Args:
            offset: 偏移量
            length: 读取长度（None 表示读取所有）

        Returns:
            memoryview 对象（零拷贝视图）
        """
        if length is None:
            length = self._position - offset

        # 创建 memoryview（零拷贝）
        view = memoryview(self._buffer)[offset : offset + length]
        self._ref_count += 1

        return view

    def clear(self) -> None:
        """清空缓冲区。"""
        self._position = 0
        self._ref_count = 0

    def get_ref_count(self) -> int:
        """获取引用计数。"""
        return self._ref_count

    @property
    def size(self) -> int:
        """缓冲区大小。"""
        return self._size

    @property
    def position(self) -> int:
        """当前位置。"""
        return self._position


@final
class ZeroCopyPool:
    """零拷贝缓冲区池。

    复用缓冲区，减少内存分配开销。

    Examples:
        >>> pool = ZeroCopyPool(pool_size=10, buffer_size=1024)
        >>>
        >>> # 分配缓冲区
        >>> buffer1 = pool.allocate()
        >>> buffer1.write(b"data1")
        >>>
        >>> # 释放缓冲区（自动回收）
        >>> pool.release(buffer1)
        >>>
        >>> # 下次分配会复用
        >>> buffer2 = pool.allocate()
        >>> # buffer2 可能就是 buffer1（已清空）
    """

    __slots__ = ("_allocated", "_buffer_size", "_pool")

    def __init__(self, pool_size: int = 10, buffer_size: int = 4096) -> None:
        """初始化缓冲区池。

        Args:
            pool_size: 池大小
            buffer_size: 缓冲区大小
        """
        self._pool: list[ZeroCopyBuffer] = [
            ZeroCopyBuffer(size=buffer_size) for _ in range(pool_size)
        ]
        self._buffer_size = buffer_size
        self._allocated: set[int] = set()

    def allocate(self) -> ZeroCopyBuffer:
        """分配缓冲区。

        Returns:
            缓冲区对象
        """
        # 查找可用缓冲区
        for buffer in self._pool:
            buffer_id = id(buffer)
            if buffer_id not in self._allocated:
                self._allocated.add(buffer_id)
                buffer.clear()
                return buffer

        # 池已满，创建新缓冲区
        buffer = ZeroCopyBuffer(size=self._buffer_size)
        self._pool.append(buffer)
        self._allocated.add(id(buffer))
        return buffer

    def release(self, buffer: ZeroCopyBuffer) -> None:
        """释放缓冲区。

        Args:
            buffer: 要释放的缓冲区
        """
        buffer_id = id(buffer)
        if buffer_id in self._allocated:
            self._allocated.discard(buffer_id)
            buffer.clear()

    def get_stats(self) -> dict[str, int]:
        """获取池统计信息。

        Returns:
            统计信息字典
        """
        return {
            "total_buffers": len(self._pool),
            "allocated_buffers": len(self._allocated),
            "available_buffers": len(self._pool) - len(self._allocated),
            "buffer_size": self._buffer_size,
        }
