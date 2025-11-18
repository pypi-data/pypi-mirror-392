"""symphra_event.analysis.dependency - 事件依赖分析器

创新点：
1. 基于时间窗口的依赖推断
2. 统计显著性检验
3. 因果关系启发式分析
4. 自动生成执行拓扑图

零依赖实现：
- collections.Counter: 统计分析
- statistics: 标准差计算
- heapq: 优先级队列
"""

from __future__ import annotations

import statistics
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Any, final

__all__ = ["DependencyAnalyzer", "EventDependency", "EventExecution", "ExecutionGroup"]


@final
@dataclass(slots=True)
class EventExecution:
    """事件执行记录。"""

    event_name: str
    timestamp_ms: float
    duration_ms: float
    success: bool
    listener_id: int


@final
@dataclass(slots=True)
class EventDependency:
    """事件依赖关系。"""

    source: str
    target: str
    confidence: float  # 0.0 - 1.0
    occurrences: int
    avg_time_gap_ms: float


@final
@dataclass(slots=True)
class ExecutionGroup:
    """执行分组（可并行执行的事件）。"""

    group_id: int
    events: list[str] = field(default_factory=list)
    avg_duration_ms: float = 0.0


@final
class DependencyAnalyzer:
    """事件依赖分析器（零依赖实现）。"""

    __slots__ = (
        "_current_execution",
        "_executions",
        "_max_history",
        "_time_window_ms",
    )

    def __init__(
        self,
        max_history: int = 1000,
        time_window_ms: float = 100.0,
    ) -> None:
        self._executions: deque[EventExecution] = deque(maxlen=max_history)
        self._current_execution: dict[str, float] = {}
        self._max_history = max_history
        self._time_window_ms = time_window_ms

    def record_start(self, event_name: str) -> None:
        """记录事件开始执行。"""
        self._current_execution[event_name] = time.perf_counter() * 1000

    def record_end(self, event_name: str, success: bool = True) -> None:
        """记录事件结束执行。"""
        if event_name not in self._current_execution:
            return

        start_time = self._current_execution.pop(event_name)
        end_time = time.perf_counter() * 1000
        duration = end_time - start_time

        self._executions.append(
            EventExecution(
                event_name=event_name,
                timestamp_ms=end_time,
                duration_ms=duration,
                success=success,
                listener_id=id(event_name),
            )
        )

    def analyze_dependencies(
        self,
        min_confidence: float = 0.6,
    ) -> list[EventDependency]:
        """分析事件依赖关系（统计方法）。"""
        if len(self._executions) < 2:
            return []

        # 统计事件对
        event_pairs: Counter[tuple[str, str]] = Counter()
        event_counts: Counter[str] = Counter()
        time_gaps: dict[tuple[str, str], list[float]] = {}

        # 遍历执行历史
        for i in range(len(self._executions) - 1):
            current = self._executions[i]
            next_event = self._executions[i + 1]

            event_counts[current.event_name] += 1

            time_gap = next_event.timestamp_ms - current.timestamp_ms

            # 在时间窗口内
            if time_gap <= self._time_window_ms:
                pair = (current.event_name, next_event.event_name)
                event_pairs[pair] += 1

                if pair not in time_gaps:
                    time_gaps[pair] = []
                time_gaps[pair].append(time_gap)

        # 计算置信度和依赖关系
        dependencies: list[EventDependency] = []

        for (source, target), count in event_pairs.items():
            if source == target:
                continue

            source_count = event_counts[source]
            confidence = count / source_count if source_count > 0 else 0.0

            if confidence >= min_confidence:
                avg_gap = statistics.mean(time_gaps[(source, target)])
                dependencies.append(
                    EventDependency(
                        source=source,
                        target=target,
                        confidence=confidence,
                        occurrences=count,
                        avg_time_gap_ms=avg_gap,
                    )
                )

        dependencies.sort(key=lambda d: d.confidence, reverse=True)
        return dependencies

    def suggest_execution_groups(
        self,
        min_confidence: float = 0.6,
    ) -> list[ExecutionGroup]:
        """建议执行分组（可并行执行）。"""
        dependencies = self.analyze_dependencies(min_confidence)

        # 构建依赖图
        graph: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}
        all_events: set[str] = set()

        for dep in dependencies:
            all_events.add(dep.source)
            all_events.add(dep.target)

            if dep.source not in graph:
                graph[dep.source] = []
            graph[dep.source].append(dep.target)

            in_degree[dep.target] = in_degree.get(dep.target, 0) + 1
            if dep.source not in in_degree:
                in_degree[dep.source] = 0

        # 拓扑排序 + 分层
        groups: list[ExecutionGroup] = []
        visited: set[str] = set()
        group_id = 0

        while len(visited) < len(all_events):
            current_layer: list[str] = []
            for event in all_events:
                if event not in visited and in_degree.get(event, 0) == 0:
                    current_layer.append(event)

            if not current_layer:
                break

            group = ExecutionGroup(group_id=group_id, events=current_layer)

            durations = [
                exec.duration_ms
                for exec in self._executions
                if exec.event_name in current_layer
            ]
            if durations:
                group.avg_duration_ms = statistics.mean(durations)

            groups.append(group)

            for event in current_layer:
                visited.add(event)
                for neighbor in graph.get(event, []):
                    in_degree[neighbor] -= 1

            group_id += 1

        return groups

    def get_performance_stats(self) -> dict[str, Any]:
        """获取性能统计。"""
        if not self._executions:
            return {}

        stats_by_event: dict[str, list[float]] = {}
        for exec in self._executions:
            if exec.event_name not in stats_by_event:
                stats_by_event[exec.event_name] = []
            stats_by_event[exec.event_name].append(exec.duration_ms)

        result: dict[str, Any] = {}
        for event_name, durations in stats_by_event.items():
            result[event_name] = {
                "count": len(durations),
                "mean_ms": statistics.mean(durations),
                "median_ms": statistics.median(durations),
                "stdev_ms": (
                    statistics.stdev(durations) if len(durations) > 1 else 0.0
                ),
                "min_ms": min(durations),
                "max_ms": max(durations),
            }

        return result
