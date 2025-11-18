"""Plugin 注册表和管理器。

This module provides the PluginRegistry class for managing plugin lifecycle,
dependencies, and registration.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any, final

from .base import Plugin, PluginMetadata

__all__ = ["PluginDependencyError", "PluginError", "PluginRegistry"]

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Plugin 系统异常基类。"""


class PluginDependencyError(PluginError):
    """Plugin 依赖错误。"""


@final
class PluginRegistry:
    """Plugin 注册表。

    管理插件的注册、加载、卸载和依赖解析。

    特性：
    1. 自动依赖解析
    2. 插件生命周期管理
    3. 避免重复注册
    4. 支持按名称/类型查询

    Examples:
        >>> registry = PluginRegistry()
        >>> plugin = MyPlugin()
        >>> registry.register(plugin)
        >>> registry.install_all(context=emitter)
        >>> # 使用插件...
        >>> registry.uninstall_all()
    """

    __slots__ = (
        "_context",  # Any (usually EventEmitter/EventBus)
        "_installed",  # set[str]
        "_plugins",  # dict[str, Plugin]
    )

    def __init__(self) -> None:
        """初始化插件注册表。"""
        self._plugins: dict[str, Plugin] = {}
        self._installed: set[str] = set()
        self._context: Any = None

    def register(self, plugin: Plugin) -> None:
        """注册插件。

        Args:
            plugin: 要注册的插件实例

        Raises:
            PluginError: 如果插件已注册
        """
        name = plugin.metadata.name

        if name in self._plugins:
            raise PluginError(f"Plugin {name!r} is already registered")

        self._plugins[name] = plugin
        logger.info(f"Registered plugin: {name} v{plugin.metadata.version}")

    def unregister(self, name: str) -> None:
        """注销插件。

        Args:
            name: 插件名称

        Raises:
            PluginError: 如果插件未注册
        """
        if name not in self._plugins:
            raise PluginError(f"Plugin {name!r} is not registered")

        # 如果已安装，先卸载
        if name in self._installed:
            self.uninstall(name)

        del self._plugins[name]
        logger.info(f"Unregistered plugin: {name}")

    def install(self, name: str, context: Any = None) -> None:
        """安装并激活插件。

        Args:
            name: 插件名称
            context: 安装上下文（通常是 EventEmitter 或 EventBus）

        Raises:
            PluginError: 如果插件未注册或已安装
            PluginDependencyError: 如果依赖未满足
        """
        if name not in self._plugins:
            raise PluginError(f"Plugin {name!r} is not registered")

        if name in self._installed:
            raise PluginError(f"Plugin {name!r} is already installed")

        plugin = self._plugins[name]

        # 检查依赖
        self._check_dependencies(plugin.metadata)

        # 安装插件
        try:
            plugin.install(context or self._context)
            self._installed.add(name)
            logger.info(f"Installed plugin: {name}")
        except Exception as e:
            logger.error(f"Failed to install plugin {name}: {e}")
            raise PluginError(f"Failed to install plugin {name!r}") from e

    def uninstall(self, name: str) -> None:
        """卸载插件。

        Args:
            name: 插件名称

        Raises:
            PluginError: 如果插件未安装
        """
        if name not in self._installed:
            raise PluginError(f"Plugin {name!r} is not installed")

        plugin = self._plugins[name]

        try:
            plugin.uninstall()
            self._installed.remove(name)
            logger.info(f"Uninstalled plugin: {name}")
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {name}: {e}")
            raise PluginError(f"Failed to uninstall plugin {name!r}") from e

    def install_all(self, context: Any = None) -> None:
        """安装所有已注册的插件。

        按依赖顺序安装。

        Args:
            context: 安装上下文
        """
        if context is not None:
            self._context = context

        # 拓扑排序：按依赖顺序安装
        sorted_plugins = self._topological_sort()

        for name in sorted_plugins:
            if name not in self._installed:
                try:
                    self.install(name, context)
                except Exception as e:
                    logger.error(f"Failed to install plugin {name}: {e}")
                    # 继续安装其他插件

    def uninstall_all(self) -> None:
        """卸载所有已安装的插件。

        按依赖的逆序卸载。
        """
        # 逆序卸载
        sorted_plugins = list(reversed(self._topological_sort()))

        for name in sorted_plugins:
            if name in self._installed:
                try:
                    self.uninstall(name)
                except Exception as e:
                    logger.error(f"Failed to uninstall plugin {name}: {e}")
                    # 继续卸载其他插件

    def get(self, name: str) -> Plugin | None:
        """获取插件实例。

        Args:
            name: 插件名称

        Returns:
            插件实例，如果不存在返回 None
        """
        return self._plugins.get(name)

    def is_registered(self, name: str) -> bool:
        """检查插件是否已注册。

        Args:
            name: 插件名称

        Returns:
            是否已注册
        """
        return name in self._plugins

    def is_installed(self, name: str) -> bool:
        """检查插件是否已安装。

        Args:
            name: 插件名称

        Returns:
            是否已安装
        """
        return name in self._installed

    def list_plugins(self) -> list[PluginMetadata]:
        """列出所有已注册的插件。

        Returns:
            插件元数据列表
        """
        return [plugin.metadata for plugin in self._plugins.values()]

    def list_installed(self) -> list[str]:
        """列出所有已安装的插件名称。

        Returns:
            已安装插件名称列表
        """
        return list(self._installed)

    def _check_dependencies(self, metadata: PluginMetadata) -> None:
        """检查插件依赖是否满足。

        Args:
            metadata: 插件元数据

        Raises:
            PluginDependencyError: 如果依赖未满足
        """
        for dep_name in metadata.dependencies:
            if dep_name not in self._plugins:
                raise PluginDependencyError(
                    f"Plugin {metadata.name!r} depends on {dep_name!r}, "
                    f"but it is not registered"
                )

            if dep_name not in self._installed:
                raise PluginDependencyError(
                    f"Plugin {metadata.name!r} depends on {dep_name!r}, "
                    f"but it is not installed"
                )

    def _topological_sort(self) -> list[str]:
        """拓扑排序插件（按依赖顺序）。

        使用 Kahn 算法。

        Returns:
            排序后的插件名称列表

        Raises:
            PluginDependencyError: 如果存在循环依赖
        """
        # 计算入度
        in_degree: dict[str, int] = {name: 0 for name in self._plugins}
        adj_list: dict[str, list[str]] = {name: [] for name in self._plugins}

        for name, plugin in self._plugins.items():
            for dep_name in plugin.metadata.dependencies:
                if dep_name in self._plugins:
                    adj_list[dep_name].append(name)
                    in_degree[name] += 1

        # BFS
        queue: list[str] = [name for name, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查循环依赖
        if len(result) != len(self._plugins):
            raise PluginDependencyError("Circular dependency detected in plugins")

        return result

    def __iter__(self) -> Iterator[Plugin]:
        """迭代所有已注册的插件。"""
        return iter(self._plugins.values())

    def __len__(self) -> int:
        """返回已注册的插件数量。"""
        return len(self._plugins)

    def __contains__(self, name: str) -> bool:
        """检查插件是否已注册。"""
        return name in self._plugins
