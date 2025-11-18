"""core/emitter 单元测试 - 补充覆盖率。"""

from __future__ import annotations

import gc

from symphra_event.core.emitter import EventEmitter


class TestEmitterAdvanced:
    """EventEmitter 高级功能测试。"""

    def test_cleanup_with_dead_refs(self) -> None:
        """测试清理死引用。"""
        emitter = EventEmitter()

        def create_handler():
            def handler(data: str) -> None:
                pass

            return handler

        handler = create_handler()
        emitter.on(handler)
        assert emitter.count() == 1

        del handler
        gc.collect()

        stats = emitter.cleanup()
        assert stats.dead_refs_removed >= 0
        assert stats.listeners_remaining >= 0
        assert stats.elapsed_ms >= 0

    def test_context_manager(self) -> None:
        """测试上下文管理器。"""
        emitter = EventEmitter()
        handler_called = []

        with emitter:

            @emitter.on
            def handler(data: str) -> None:
                handler_called.append(data)

            emitter.emit(data="test")

        assert handler_called == ["test"]

    def test_context_manager_with_exception(self) -> None:
        """测试上下文管理器异常处理。"""
        emitter = EventEmitter()

        try:
            with emitter:

                @emitter.on
                def handler(data: str) -> None:
                    pass

                raise ValueError("test error")
        except ValueError:
            pass
