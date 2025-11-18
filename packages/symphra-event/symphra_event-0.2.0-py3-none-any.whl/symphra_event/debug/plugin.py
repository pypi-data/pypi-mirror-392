"""时间旅行调试器插件。

该插件封装了时间旅行调试器功能。
"""

from __future__ import annotations

from typing import Any, final

from ..debug.time_travel import TimeTravelDebugger
from ..plugin.base import Plugin, PluginMetadata

__all__ = ["TimeTravelDebuggerPlugin"]


@final
class TimeTravelDebuggerPlugin(Plugin):
    """时间旅行调试器插件。

    提供事件回放和调试能力：
    1. 事件录制
    2. 事件回放
    3. 时间旅行（前进/后退）
    4. 断点和单步调试

    Examples:
        >>> plugin = TimeTravelDebuggerPlugin(max_history=1000)
        >>> registry.register(plugin)
        >>> registry.install("time-travel", context=emitter)
        >>>
        >>> # 获取调试器
        >>> debugger = plugin.debugger
        >>> debugger.start_recording()
        >>> # ... 触发事件 ...
        >>> debugger.stop_recording()
        >>> debugger.replay()  # 回放所有事件
    """

    __slots__ = (
        "_debugger",
        "_max_history",
    )

    def __init__(self, max_history: int = 1000) -> None:
        """初始化时间旅行调试器插件。

        Args:
            max_history: 最大历史记录数（默认 1000）
        """
        self._max_history = max_history
        self._debugger: TimeTravelDebugger | None = None

    @property
    def metadata(self) -> PluginMetadata:
        """插件元数据。"""
        return PluginMetadata(
            name="time-travel",
            version="1.0.0",
            description="Time-travel debugger for event replay",
            author="Symphra",
            dependencies=[],
        )

    def install(self, context: Any = None) -> None:
        """安装插件。

        Args:
            context: 安装上下文（通常是 EventEmitter）
        """
        self._debugger = TimeTravelDebugger(
            max_snapshots=self._max_history,
        )

    def uninstall(self) -> None:
        """卸载插件。"""
        # TimeTravelDebugger 不需要显式清理
        self._debugger = None

    @property
    def debugger(self) -> TimeTravelDebugger:
        """获取时间旅行调试器实例。

        Returns:
            TimeTravelDebugger 实例

        Raises:
            RuntimeError: 如果插件未安装
        """
        if self._debugger is None:
            raise RuntimeError(
                "Plugin 'time-travel' is not installed. Call install() first."
            )
        return self._debugger
