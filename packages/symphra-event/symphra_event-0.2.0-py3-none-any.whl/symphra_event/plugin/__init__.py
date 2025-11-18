"""symphra_event.plugin - Plugin 系统

Plugin 系统提供可扩展的功能插件机制。

特性：
1. 标准插件接口（Plugin 基类）
2. 插件注册表（PluginRegistry）
3. 自动依赖解析
4. 生命周期管理（install/uninstall）

Examples:
    >>> from symphra_event.plugin import Plugin, PluginMetadata, PluginRegistry
    >>>
    >>> # 定义插件
    >>> class MyPlugin(Plugin):
    ...     @property
    ...     def metadata(self) -> PluginMetadata:
    ...         return PluginMetadata(
    ...             name="my-plugin",
    ...             version="1.0.0",
    ...             description="My custom plugin"
    ...         )
    ...
    ...     def install(self, context=None):
    ...         print("Plugin installed")
    ...
    ...     def uninstall(self):
    ...         print("Plugin uninstalled")
    >>>
    >>> # 注册和使用
    >>> registry = PluginRegistry()
    >>> registry.register(MyPlugin())
    >>> registry.install_all(context=emitter)
"""

from __future__ import annotations

from .base import Plugin, PluginMetadata
from .registry import PluginDependencyError, PluginError, PluginRegistry

__all__ = [
    "Plugin",
    "PluginDependencyError",
    "PluginError",
    "PluginMetadata",
    "PluginRegistry",
]
