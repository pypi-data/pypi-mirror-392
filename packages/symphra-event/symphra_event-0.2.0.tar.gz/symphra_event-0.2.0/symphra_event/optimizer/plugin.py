"""批量处理优化器插件。

该插件封装了 BatchProcessor，以插件形式提供批量事件处理能力。
"""

from __future__ import annotations

from typing import Any, final

from ..optimizer.batch import BatchProcessor
from ..plugin.base import Plugin, PluginMetadata

__all__ = ["BatchProcessorPlugin"]


@final
class BatchProcessorPlugin(Plugin):
    """批量处理优化器插件。

    提供事件批量处理能力：
    1. 自动事件合并
    2. 批量处理
    3. 延迟执行
    4. 动态批量大小调整

    Examples:
        >>> plugin = BatchProcessorPlugin(
        ...     batch_size=100,
        ...     flush_interval_ms=50.0
        ... )
        >>> registry.register(plugin)
        >>> registry.install("batch-processor", context=emitter)
        >>>
        >>> # 获取处理器
        >>> processor = plugin.processor
        >>> processor.add("user.login", {"user_id": 123})
    """

    __slots__ = (
        "_batch_size",
        "_flush_interval_ms",
        "_processor",
    )

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval_ms: float = 50.0,
    ) -> None:
        """初始化批量处理插件。

        Args:
            batch_size: 批量大小（默认 100）
            flush_interval_ms: 刷新间隔（毫秒，默认 50.0）
        """
        self._batch_size = batch_size
        self._flush_interval_ms = flush_interval_ms
        self._processor: BatchProcessor[Any] | None = None

    @property
    def metadata(self) -> PluginMetadata:
        """插件元数据。"""
        return PluginMetadata(
            name="batch-processor",
            version="1.0.0",
            description="Event batch processing optimizer",
            author="Symphra",
            dependencies=[],
        )

    def install(self, context: Any = None) -> None:
        """安装插件。

        Args:
            context: 安装上下文（可选）
        """
        self._processor = BatchProcessor(
            batch_size=self._batch_size,
            flush_interval_ms=self._flush_interval_ms,
        )

    def uninstall(self) -> None:
        """卸载插件。"""
        if self._processor is not None:
            self._processor.stop()
            self._processor = None

    @property
    def processor(self) -> BatchProcessor[Any]:
        """获取批量处理器实例。

        Returns:
            BatchProcessor 实例

        Raises:
            RuntimeError: 如果插件未安装
        """
        if self._processor is None:
            raise RuntimeError(
                "Plugin 'batch-processor' is not installed. Call install() first."
            )
        return self._processor
