"""symphra_event.optimizer - 事件优化器模块

提供事件批量处理、缓存等性能优化功能。
"""

from __future__ import annotations

from .batch import BatchProcessor
from .plugin import BatchProcessorPlugin

__all__ = ["BatchProcessor", "BatchProcessorPlugin"]
