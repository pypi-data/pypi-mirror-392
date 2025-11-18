"""测试 plugin.base 模块的插件基类"""

from __future__ import annotations

import pytest

from symphra_event.plugin.base import Plugin, PluginMetadata


class TestPluginMetadata:
    """测试 PluginMetadata"""

    def test_plugin_metadata_creation(self) -> None:
        """测试创建 PluginMetadata"""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            dependencies=["dep1", "dep2"],
        )

        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.author == "Test Author"
        assert metadata.dependencies == ["dep1", "dep2"]

    def test_plugin_metadata_default_values(self) -> None:
        """测试 PluginMetadata 的默认值"""
        metadata = PluginMetadata(
            name="test-plugin", version="1.0.0", description="Test plugin"
        )

        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.author is None
        assert metadata.dependencies == []

    def test_plugin_metadata_repr(self) -> None:
        """测试 PluginMetadata 的字符串表示"""
        metadata = PluginMetadata(
            name="test-plugin", version="1.0.0", description="Test plugin"
        )

        repr_str = repr(metadata)
        assert "PluginMetadata" in repr_str
        assert "test-plugin" in repr_str
        assert "1.0.0" in repr_str


class TestPlugin:
    """测试 Plugin 基类"""

    def test_plugin_is_abstract(self) -> None:
        """测试 Plugin 是抽象类"""

        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            Plugin()  # type: ignore[abstract]

    def test_concrete_plugin_implementation(self) -> None:
        """测试具体的插件实现"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test-plugin",
                    version="1.0.0",
                    description="Test plugin",
                    author="Test Author",
                )

            def install(self, context: object | None = None) -> None:
                self.installed = True  # type: ignore[attr-defined]

            def uninstall(self) -> None:
                self.uninstalled = True  # type: ignore[attr-defined]

        # 可以实例化具体实现
        plugin = TestPlugin()
        assert plugin.metadata.name == "test-plugin"
        assert plugin.metadata.version == "1.0.0"
        assert plugin.metadata.description == "Test plugin"
        assert plugin.metadata.author == "Test Author"

        # 测试 install 和 uninstall
        plugin.install()
        assert plugin.installed is True  # type: ignore[attr-defined]

        plugin.uninstall()
        assert plugin.uninstalled is True  # type: ignore[attr-defined]

    def test_plugin_with_dependencies(self) -> None:
        """测试带依赖的插件"""

        class PluginWithDeps(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="plugin-with-deps",
                    version="2.0.0",
                    description="Plugin with dependencies",
                    dependencies=["base-plugin", "logger-plugin"],
                )

            def install(self, context: object | None = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        plugin = PluginWithDeps()
        assert plugin.metadata.dependencies == ["base-plugin", "logger-plugin"]

    def test_plugin_repr(self) -> None:
        """测试 Plugin 的字符串表示"""

        class TestPlugin(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test-plugin", version="1.5.0", description="Test"
                )

            def install(self, context: object | None = None) -> None:
                pass

            def uninstall(self) -> None:
                pass

        plugin = TestPlugin()
        repr_str = repr(plugin)

        assert "Plugin" in repr_str
        assert "test-plugin" in repr_str
        assert "1.5.0" in repr_str

    def test_plugin_install_with_context(self) -> None:
        """测试插件安装时传递上下文"""

        class ContextPlugin(Plugin):
            def __init__(self) -> None:
                super().__init__()
                self.context: object | None = None

            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="context-plugin", version="1.0.0", description="Context plugin"
                )

            def install(self, context: object | None = None) -> None:
                self.context = context

            def uninstall(self) -> None:
                self.context = None

        plugin = ContextPlugin()
        context_obj = {"emitter": "test"}

        plugin.install(context_obj)
        assert plugin.context == context_obj

        plugin.uninstall()
        assert plugin.context is None
