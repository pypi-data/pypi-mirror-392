"""Plugin 基类和接口定义。

提供插件系统的基础类和接口。
所有插件必须继承自 Plugin 类并实现所需的生命周期方法。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, final

__all__ = ["Plugin", "PluginMetadata"]


class PluginMetadata:
    """Plugin 元数据。"""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str | None = None,
        dependencies: list[str] | None = None,
    ) -> None:
        """初始化插件元数据。

        Args:
            name: Plugin 名称（唯一标识）
            version: 版本号（遵循 SemVer）
            description: 功能描述
            author: 作者信息
            dependencies: 依赖的其他插件名称列表

        """
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.dependencies = dependencies or []

    def __repr__(self) -> str:
        return f"PluginMetadata(name={self.name!r}, version={self.version!r})"


class Plugin(ABC):
    """Plugin 基类。

    所有插件必须继承此类并实现 install() 和 uninstall() 方法。

    示例：
        >>> class MyPlugin(Plugin):
        ...     @property
        ...     def metadata(self) -> PluginMetadata:
        ...         return PluginMetadata(
        ...             name="my-plugin",
        ...             version="1.0.0",
        ...             description="My custom plugin"
        ...         )
        ...
        ...     def install(self, context: Any) -> None:
        ...         print("Plugin installed")
        ...
        ...     def uninstall(self) -> None:
        ...         print("Plugin uninstalled")

    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """获取插件元数据。

        Returns:
            Plugin 元数据对象

        """
        ...

    @abstractmethod
    def install(self, context: Any = None) -> None:
        """安装并激活插件。

        Args:
            context: 安装上下文（通常是 EventEmitter/EventBus 实例）

        """
        ...

    @abstractmethod
    def uninstall(self) -> None:
        """卸载并停用插件。"""
        ...

    @final
    def __repr__(self) -> str:
        return f"Plugin({self.metadata.name!r} v{self.metadata.version})"
