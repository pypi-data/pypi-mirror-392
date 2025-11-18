"""依赖分析器插件。

该插件封装了依赖分析器功能。
"""

from __future__ import annotations

from typing import Any, final

from ..analysis.dependency import DependencyAnalyzer
from ..plugin.base import Plugin, PluginMetadata

__all__ = ["DependencyAnalyzerPlugin"]


@final
class DependencyAnalyzerPlugin(Plugin):
    """依赖分析器插件。

    提供监听器依赖关系分析能力：
    1. 自动检测监听器依赖
    2. 拓扑排序优化执行顺序
    3. 循环依赖检测
    4. 依赖图可视化

    Examples:
        >>> plugin = DependencyAnalyzerPlugin()
        >>> registry.register(plugin)
        >>> registry.install("dependency-analyzer", context=emitter)
        >>>
        >>> # 获取分析器
        >>> analyzer = plugin.analyzer
        >>> sorted_listeners = analyzer.topological_sort(listeners)
    """

    __slots__ = ("_analyzer",)

    def __init__(self) -> None:
        """初始化依赖分析器插件。"""
        self._analyzer: DependencyAnalyzer | None = None

    @property
    def metadata(self) -> PluginMetadata:
        """插件元数据。"""
        return PluginMetadata(
            name="dependency-analyzer",
            version="1.0.0",
            description="Listener dependency analyzer",
            author="Symphra",
            dependencies=[],
        )

    def install(self, context: Any = None) -> None:
        """安装插件。

        Args:
            context: 安装上下文（可选）
        """
        self._analyzer = DependencyAnalyzer()

    def uninstall(self) -> None:
        """卸载插件。"""
        self._analyzer = None

    @property
    def analyzer(self) -> DependencyAnalyzer:
        """获取依赖分析器实例。

        Returns:
            DependencyAnalyzer 实例

        Raises:
            RuntimeError: 如果插件未安装
        """
        if self._analyzer is None:
            raise RuntimeError(
                "Plugin 'dependency-analyzer' is not installed. Call install() first."
            )
        return self._analyzer
