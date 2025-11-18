"""测试 transport.zero_copy 模块的零拷贝功能"""

from __future__ import annotations

import pytest

from symphra_event.transport.zero_copy import ZeroCopyBuffer, ZeroCopyPool


class TestZeroCopyBuffer:
    """测试 ZeroCopyBuffer"""

    def test_buffer_creation(self) -> None:
        """测试创建缓冲区"""
        buffer = ZeroCopyBuffer(size=1024)

        assert buffer.size == 1024
        assert buffer.position == 0
        assert buffer.get_ref_count() == 0

    def test_buffer_write_and_read(self) -> None:
        """测试写入和读取数据"""
        buffer = ZeroCopyBuffer(size=1024)
        data = b"Hello, World!"

        # 写入数据
        written = buffer.write(data)
        assert written == len(data)
        assert buffer.position == len(data)

        # 读取数据
        view = buffer.read()
        assert bytes(view) == data
        assert buffer.get_ref_count() == 1

    def test_buffer_read_with_offset_and_length(self) -> None:
        """测试带偏移和长度的读取"""
        buffer = ZeroCopyBuffer(size=1024)
        data = b"Hello, World!"
        buffer.write(data)

        # 读取部分数据
        view = buffer.read(offset=7, length=5)
        assert bytes(view) == b"World"
        assert buffer.get_ref_count() == 1

    def test_buffer_multiple_reads(self) -> None:
        """测试多次读取（零拷贝）"""
        buffer = ZeroCopyBuffer(size=1024)
        data = b"Test Data"
        buffer.write(data)

        # 多次读取
        view1 = buffer.read()
        view2 = buffer.read()
        view3 = buffer.read()

        # 所有视图应该指向同一块内存
        assert bytes(view1) == data
        assert bytes(view2) == data
        assert bytes(view3) == data
        assert buffer.get_ref_count() == 3

    def test_buffer_write_too_large(self) -> None:
        """测试写入过大的数据"""
        buffer = ZeroCopyBuffer(size=10)
        data = b"This is too long"

        with pytest.raises(ValueError, match="Data too large"):
            buffer.write(data)

    def test_buffer_clear(self) -> None:
        """测试清空缓冲区"""
        buffer = ZeroCopyBuffer(size=1024)
        data = b"Test Data"
        buffer.write(data)

        # 清空
        buffer.clear()

        assert buffer.position == 0
        assert buffer.get_ref_count() == 0

    def test_buffer_write_empty_data(self) -> None:
        """测试写入空数据"""
        buffer = ZeroCopyBuffer(size=1024)
        data = b""

        written = buffer.write(data)
        assert written == 0
        assert buffer.position == 0


class TestZeroCopyPool:
    """测试 ZeroCopyPool"""

    def test_pool_creation(self) -> None:
        """测试创建缓冲池"""
        pool = ZeroCopyPool(pool_size=5, buffer_size=1024)

        stats = pool.get_stats()
        assert stats["total_buffers"] == 5
        assert stats["allocated_buffers"] == 0
        assert stats["available_buffers"] == 5
        assert stats["buffer_size"] == 1024

    def test_pool_allocate_and_release(self) -> None:
        """测试分配和释放缓冲区"""
        pool = ZeroCopyPool(pool_size=5, buffer_size=1024)

        # 分配缓冲区
        buffer1 = pool.allocate()
        assert isinstance(buffer1, ZeroCopyBuffer)
        assert buffer1.size == 1024

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 1
        assert stats["available_buffers"] == 4

        # 写入数据
        buffer1.write(b"Test")

        # 释放缓冲区
        pool.release(buffer1)

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 0
        assert stats["available_buffers"] == 5

        # 验证缓冲区已清空
        assert buffer1.position == 0
        assert buffer1.get_ref_count() == 0

    def test_pool_allocate_multiple(self) -> None:
        """测试分配多个缓冲区"""
        pool = ZeroCopyPool(pool_size=5, buffer_size=1024)

        # 分配多个缓冲区
        buffers = []
        for _ in range(3):
            buffer = pool.allocate()
            buffers.append(buffer)

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 3
        assert stats["available_buffers"] == 2

        # 释放所有缓冲区
        for buffer in buffers:
            pool.release(buffer)

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 0
        assert stats["available_buffers"] == 5

    def test_pool_exceed_pool_size(self) -> None:
        """测试超过池大小时的分配"""
        pool = ZeroCopyPool(pool_size=2, buffer_size=1024)

        # 分配超过池大小
        buffer1 = pool.allocate()
        buffer2 = pool.allocate()
        buffer3 = pool.allocate()  # 应该创建新的缓冲区

        stats = pool.get_stats()
        assert stats["total_buffers"] == 3  # 池大小增加了
        assert stats["allocated_buffers"] == 3

        # 释放所有缓冲区
        pool.release(buffer1)
        pool.release(buffer2)
        pool.release(buffer3)

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 0
        assert stats["available_buffers"] == 3

    def test_pool_buffer_reuse(self) -> None:
        """测试缓冲区复用"""
        pool = ZeroCopyPool(pool_size=5, buffer_size=1024)

        # 分配、写入、释放
        buffer1 = pool.allocate()
        buffer_id = id(buffer1)
        buffer1.write(b"Test Data")
        pool.release(buffer1)

        # 再次分配，应该得到相同的缓冲区（已清空）
        buffer2 = pool.allocate()
        buffer2_id = id(buffer2)

        # 应该是同一个缓冲区对象
        assert buffer_id == buffer2_id
        assert buffer2.position == 0  # 已清空
        assert buffer2.get_ref_count() == 0  # 引用计数已重置

    def test_pool_release_unallocated_buffer(self) -> None:
        """测试释放未分配的缓冲区（不应该出错）"""
        pool = ZeroCopyPool(pool_size=5, buffer_size=1024)
        buffer = ZeroCopyBuffer(size=1024)

        # 释放未通过 pool.allocate() 分配的缓冲区
        pool.release(buffer)  # 应该不执行任何操作

        stats = pool.get_stats()
        assert stats["allocated_buffers"] == 0
        assert stats["available_buffers"] == 5

    def test_pool_allocate_and_use_multiple_buffers(self) -> None:
        """测试分配和使用多个缓冲区"""
        pool = ZeroCopyPool(pool_size=3, buffer_size=100)

        # 分配多个缓冲区并写入不同数据
        buffer1 = pool.allocate()
        buffer1.write(b"Data1")

        buffer2 = pool.allocate()
        buffer2.write(b"Data2")

        buffer3 = pool.allocate()
        buffer3.write(b"Data3")

        # 验证数据
        assert bytes(buffer1.read()) == b"Data1"
        assert bytes(buffer2.read()) == b"Data2"
        assert bytes(buffer3.read()) == b"Data3"

        # 释放所有缓冲区
        pool.release(buffer1)
        pool.release(buffer2)
        pool.release(buffer3)

        # 重新分配并验证已清空
        new_buffer = pool.allocate()
        assert new_buffer.position == 0
        assert new_buffer.get_ref_count() == 0
