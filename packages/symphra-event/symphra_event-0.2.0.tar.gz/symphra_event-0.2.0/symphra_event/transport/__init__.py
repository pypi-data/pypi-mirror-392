"""symphra_event.transport - 事件传输模块

提供零拷贝事件传递等高性能传输机制。
"""

from __future__ import annotations

from .plugin import ZeroCopyPlugin
from .zero_copy import ZeroCopyBuffer, ZeroCopyPool

__all__ = ["ZeroCopyBuffer", "ZeroCopyPlugin", "ZeroCopyPool"]
