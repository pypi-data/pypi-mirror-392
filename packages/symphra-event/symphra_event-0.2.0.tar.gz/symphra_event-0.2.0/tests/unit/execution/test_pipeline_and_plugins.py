"""测试 Pipeline 执行模式和插件系统。"""

from __future__ import annotations

from symphra_event.analysis.plugin import DependencyAnalyzerPlugin
from symphra_event.debug.plugin import TimeTravelDebuggerPlugin
from symphra_event.execution.pipeline import PipelineExecutor
from symphra_event.optimizer.plugin import BatchProcessorPlugin
from symphra_event.plugin import Plugin, PluginMetadata, PluginRegistry
from symphra_event.transport.plugin import ZeroCopyPlugin
from symphra_event.types import Listener


class TestPipelineExecutor:
    """测试流水线执行器。"""

    def test_basic_pipeline(self) -> None:
        """测试基本流水线执行。"""
        results: list[str] = []

        def step1(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step1")
            data = kwargs.get("data", "")
            return {"data": f"{data}_step1"}

        def step2(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step2")
            data = kwargs["data"]
            return {"data": f"{data}_step2"}

        def step3(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step3")
            data = kwargs["data"]
            return {"data": f"{data}_step3"}

        listeners = (
            Listener(handler=step1, priority=100),
            Listener(handler=step2, priority=50),
            Listener(handler=step3, priority=10),
        )

        executor = PipelineExecutor()
        result = executor.execute(listeners, data="start")

        assert result.success_count == 3
        assert result.total_count == 3
        assert len(result.errors) == 0
        assert result.pipeline_output == {"data": "start_step1_step2_step3"}
        assert results == ["step1", "step2", "step3"]

    def test_pipeline_with_none_return(self) -> None:
        """测试返回 None 的流水线。"""

        def step1(**kwargs: dict[str, str]) -> dict[str, str]:
            return {"data": "step1"}

        def step2(**kwargs: dict[str, str]) -> None:
            # 不返回值
            pass

        def step3(**kwargs: dict[str, str]) -> dict[str, str]:
            # 应该接收 step1 的数据（step2 返回 None）
            data = kwargs["data"]
            return {"data": f"{data}_step3"}

        listeners = (
            Listener(handler=step1, priority=100),
            Listener(handler=step2, priority=50),
            Listener(handler=step3, priority=10),
        )

        executor = PipelineExecutor()
        result = executor.execute(listeners, data="start")

        assert result.success_count == 3
        assert result.pipeline_output == {"data": "step1_step3"}

    def test_pipeline_error_stops_execution(self) -> None:
        """测试流水线错误中断执行。"""
        results: list[str] = []

        def step1(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step1")
            return {"data": "step1"}

        def step2(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step2")
            raise ValueError("Step 2 failed")

        def step3(**kwargs: dict[str, str]) -> dict[str, str]:
            results.append("step3")
            return {"data": "step3"}

        listeners = (
            Listener(handler=step1, priority=100),
            Listener(handler=step2, priority=50),
            Listener(handler=step3, priority=10),
        )

        executor = PipelineExecutor()
        result = executor.execute(listeners)

        assert result.success_count == 1  # 只有 step1 成功
        assert result.total_count == 3
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
        assert results == ["step1", "step2"]  # step3 未执行

    def test_pipeline_invalid_return_type(self) -> None:
        """测试返回非 dict 类型抛出错误。"""

        def step1(**kwargs: dict[str, str]) -> str:  # 错误：返回 str
            return "invalid"  # type: ignore

        listeners = (Listener(handler=step1, priority=100),)

        executor = PipelineExecutor()
        result = executor.execute(listeners, data="test")

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeError)
        assert "must return dict or None" in str(result.errors[0])


class TestPluginSystem:
    """测试插件系统。"""

    def test_plugin_registry_basic(self) -> None:
        """测试基本插件注册。"""

        class TestPlugin(Plugin):
            def __init__(self) -> None:
                self.installed = False

            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test-plugin",
                    version="1.0.0",
                    description="Test plugin",
                )

            def install(self, context: object = None) -> None:
                self.installed = True

            def uninstall(self) -> None:
                self.installed = False

        registry = PluginRegistry()
        plugin = TestPlugin()

        # 注册
        registry.register(plugin)
        assert registry.is_registered("test-plugin")
        assert not registry.is_installed("test-plugin")

        # 安装
        registry.install("test-plugin")
        assert registry.is_installed("test-plugin")
        assert plugin.installed

        # 卸载
        registry.uninstall("test-plugin")
        assert not registry.is_installed("test-plugin")
        assert not plugin.installed

    def test_plugin_dependencies(self) -> None:
        """测试插件依赖解析。"""

        class PluginA(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="plugin-a",
                    version="1.0.0",
                    description="Plugin A",
                    dependencies=[],
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        class PluginB(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="plugin-b",
                    version="1.0.0",
                    description="Plugin B",
                    dependencies=["plugin-a"],  # 依赖 A
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin_a = PluginA()
        plugin_b = PluginB()

        registry.register(plugin_a)
        registry.register(plugin_b)

        # 安装所有（按依赖顺序）
        registry.install_all()

        assert registry.is_installed("plugin-a")
        assert registry.is_installed("plugin-b")


class TestBuiltinPlugins:
    """测试内置插件。"""

    def test_batch_processor_plugin(self) -> None:
        """测试批量处理插件。"""
        plugin = BatchProcessorPlugin(batch_size=10, flush_interval_ms=100.0)
        registry = PluginRegistry()

        registry.register(plugin)
        registry.install("batch-processor")

        processor = plugin.processor
        assert processor is not None

        # 注册批量处理器
        events: list[list[dict]] = []

        @processor.register("test.event")
        def handle_batch(batch: list[dict]) -> None:
            events.append(batch)

        # 添加事件
        for i in range(5):
            processor.add("test.event", {"id": i})

        # 手动刷新
        processor.flush()

        assert len(events) == 1
        assert len(events[0]) == 5

        registry.uninstall("batch-processor")

    def test_zero_copy_plugin(self) -> None:
        """测试零拷贝插件。"""
        plugin = ZeroCopyPlugin(pool_size=5, buffer_size=1024)
        registry = PluginRegistry()

        registry.register(plugin)
        registry.install("zero-copy")

        pool = plugin.pool
        assert pool is not None

        # 分配缓冲区
        buffer = pool.allocate()
        assert buffer is not None

        # 写入数据
        buffer.write(b"test data")

        # 释放
        pool.release(buffer)

        registry.uninstall("zero-copy")

    def test_dependency_analyzer_plugin(self) -> None:
        """测试依赖分析器插件。"""
        plugin = DependencyAnalyzerPlugin()
        registry = PluginRegistry()

        registry.register(plugin)
        registry.install("dependency-analyzer")

        analyzer = plugin.analyzer
        assert analyzer is not None

        registry.uninstall("dependency-analyzer")

    def test_time_travel_plugin(self) -> None:
        """测试时间旅行调试器插件。"""
        plugin = TimeTravelDebuggerPlugin(max_history=100)
        registry = PluginRegistry()

        registry.register(plugin)
        registry.install("time-travel")

        debugger = plugin.debugger
        assert debugger is not None

        # 捕获快照
        snapshot_id = debugger.capture("test.event", {"data": "test"})
        assert snapshot_id == 0

        registry.uninstall("time-travel")
