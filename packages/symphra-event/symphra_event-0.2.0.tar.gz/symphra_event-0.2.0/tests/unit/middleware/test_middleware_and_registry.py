"""测试中间件和插件注册表的高级功能。"""

from __future__ import annotations

import pytest

from symphra_event.middleware.builtin import (
    LoggingMiddleware,
    ValidationMiddleware,
)
from symphra_event.plugin import (
    Plugin,
    PluginDependencyError,
    PluginError,
    PluginMetadata,
    PluginRegistry,
)


class TestMiddleware:
    """测试中间件。"""

    def test_validation_middleware_success(self) -> None:
        """测试验证中间件 - 成功情况。"""

        def validator(kwargs: dict) -> bool:
            return "data" in kwargs and len(kwargs["data"]) > 0

        middleware = ValidationMiddleware(validator)
        result = middleware.before_emit(None, {"data": "test"})
        assert result == {"data": "test"}

    def test_validation_middleware_failure(self) -> None:
        """测试验证中间件 - 失败情况。"""

        def validator(kwargs: dict) -> bool:
            return "data" in kwargs

        middleware = ValidationMiddleware(validator)

        with pytest.raises(ValueError, match="Validation failed"):
            middleware.before_emit(None, {"invalid": "test"})

    def test_logging_middleware(self) -> None:
        """测试日志中间件。"""
        from symphra_event.core.emitter import EventEmitter
        from symphra_event.types import EmitResult

        middleware = LoggingMiddleware()
        emitter = EventEmitter(name="test")

        # before_emit 应该返回原始 kwargs
        result = middleware.before_emit(emitter, {"data": "test"})
        assert result == {"data": "test"}

        # after_emit 应该不抛出异常
        emit_result = EmitResult(
            success_count=1, total_count=1, errors=(), elapsed_ms=1.0
        )
        middleware.after_emit(emitter, emit_result)


class TestPluginRegistryAdvanced:
    """测试插件注册表的高级功能。"""

    def test_register_duplicate(self) -> None:
        """测试注册重复插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)

        with pytest.raises(PluginError, match="already registered"):
            registry.register(plugin)

    def test_unregister(self) -> None:
        """测试注销插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)
        assert registry.is_registered("test")

        registry.unregister("test")
        assert not registry.is_registered("test")

    def test_unregister_not_registered(self) -> None:
        """测试注销未注册的插件。"""
        registry = PluginRegistry()

        with pytest.raises(PluginError, match="not registered"):
            registry.unregister("nonexistent")

    def test_install_not_registered(self) -> None:
        """测试安装未注册的插件。"""
        registry = PluginRegistry()

        with pytest.raises(PluginError, match="not registered"):
            registry.install("nonexistent")

    def test_install_already_installed(self) -> None:
        """测试重复安装插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)
        registry.install("test")

        with pytest.raises(PluginError, match="already installed"):
            registry.install("test")

    def test_uninstall_not_installed(self) -> None:
        """测试卸载未安装的插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)

        with pytest.raises(PluginError, match="not installed"):
            registry.uninstall("test")

    def test_missing_dependency(self) -> None:
        """测试缺少依赖。"""

        class PluginWithDep(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="with-dep",
                    version="1.0.0",
                    description="With dependency",
                    dependencies=["missing-dep"],
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = PluginWithDep()

        registry.register(plugin)

        with pytest.raises(PluginDependencyError, match="not registered"):
            registry.install("with-dep")

    def test_circular_dependency(self) -> None:
        """测试循环依赖检测。"""

        class PluginA(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="plugin-a",
                    version="1.0.0",
                    description="Plugin A",
                    dependencies=["plugin-b"],
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
                    dependencies=["plugin-a"],
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        registry.register(PluginA())
        registry.register(PluginB())

        with pytest.raises(PluginDependencyError, match="Circular dependency"):
            registry.install_all()

    def test_list_plugins(self) -> None:
        """测试列出插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "test"

    def test_list_installed(self) -> None:
        """测试列出已安装插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)
        assert len(registry.list_installed()) == 0

        registry.install("test")
        assert len(registry.list_installed()) == 1
        assert registry.list_installed()[0] == "test"

    def test_get_plugin(self) -> None:
        """测试获取插件。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        registry.register(plugin)

        retrieved = registry.get("test")
        assert retrieved is plugin

        assert registry.get("nonexistent") is None

    def test_contains(self) -> None:
        """测试 __contains__。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()

        assert "test" not in registry
        registry.register(plugin)
        assert "test" in registry

    def test_len(self) -> None:
        """测试 __len__。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        assert len(registry) == 0

        plugin = TestPlugin()
        registry.register(plugin)
        assert len(registry) == 1

    def test_iter(self) -> None:
        """测试 __iter__。"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test",
                    version="1.0.0",
                    description="Test",
                )

            def install(self, context: object = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = TestPlugin()
        registry.register(plugin)

        plugins = list(registry)
        assert len(plugins) == 1
        assert plugins[0] is plugin
