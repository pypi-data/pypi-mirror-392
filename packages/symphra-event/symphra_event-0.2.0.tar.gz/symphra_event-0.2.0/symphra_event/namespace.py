"""symphra_event.namespace - 命名空间系统

支持分层命名空间和通配符匹配。
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, final

from .exceptions import InvalidNamespaceError

__all__ = ["Namespace", "NamespaceRegistry"]


@final
class Namespace:
    """命名空间（支持点号分隔）。

    Examples:
        >>> ns = Namespace("user.auth.login")
        >>> ns.parts
        ('user', 'auth', 'login')
        >>> ns.parent
        Namespace('user.auth')
        >>> ns.matches("user.**.login")
        True
    """

    __slots__ = ("_parts", "_path")

    def __init__(self, path: str) -> None:
        """初始化命名空间。

        Args:
            path: 命名空间路径，如 "user.auth.login"

        Raises:
            InvalidNamespaceError: 路径格式无效
        """
        if not path:
            raise InvalidNamespaceError("Namespace path cannot be empty")

        self._path = path
        self._parts = tuple(path.split("."))

        # 验证每个部分
        for part in self._parts:
            if not part or not part.isidentifier():
                raise InvalidNamespaceError(f"Invalid namespace part: {part!r}")

    @property
    def path(self) -> str:
        """完整路径。"""
        return self._path

    @property
    def parts(self) -> tuple[str, ...]:
        """路径各部分。"""
        return self._parts

    @property
    def parent(self) -> Namespace | None:
        """父命名空间。"""
        if len(self._parts) <= 1:
            return None
        return Namespace(".".join(self._parts[:-1]))

    @property
    def name(self) -> str:
        """最后一部分名称。"""
        return self._parts[-1]

    def matches(self, pattern: str) -> bool:
        """检查是否匹配模式。

        支持的模式：
        - `*`: 匹配单个部分
        - `**`: 匹配任意多个部分

        Args:
            pattern: 匹配模式

        Returns:
            是否匹配

        Examples:
            >>> ns = Namespace("user.auth.login")
            >>> ns.matches("user.*.*")
            True
            >>> ns.matches("user.**.login")
            True
        """
        pattern_parts = pattern.split(".")
        return self._matches_parts(self._parts, tuple(pattern_parts))

    @staticmethod
    def _matches_parts(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
        """递归匹配。"""
        if not pattern:
            return not parts

        if not parts:
            return all(p == "**" for p in pattern)

        current_pattern = pattern[0]

        if current_pattern == "**":
            # ** 匹配任意多个部分
            if len(pattern) == 1:
                return True
            # 尝试匹配后续部分
            for i in range(len(parts) + 1):
                if Namespace._matches_parts(parts[i:], pattern[1:]):
                    return True
            return False

        if current_pattern == "*" or current_pattern == parts[0]:
            return Namespace._matches_parts(parts[1:], pattern[1:])

        return False

    def __str__(self) -> str:
        return self._path

    def __repr__(self) -> str:
        return f"Namespace({self._path!r})"

    def __hash__(self) -> int:
        return hash(self._path)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Namespace):
            return self._path == other._path
        if isinstance(other, str):
            return self._path == other
        return NotImplemented


@final
class NamespaceRegistry:
    """命名空间注册表（使用 Trie 树优化）。

    Examples:
        >>> registry = NamespaceRegistry()
        >>> from symphra_event import EventEmitter
        >>> emitter = EventEmitter()
        >>> registry.register("user.auth.login", emitter)
        >>> registry.get("user.auth.login")
        EventEmitter(...)
    """

    __slots__ = ("_root",)

    def __init__(self) -> None:
        self._root: dict[str, Any] = {}

    def register(self, path: str, emitter: Any) -> None:
        """注册命名空间。

        Args:
            path: 命名空间路径
            emitter: 事件发射器

        Raises:
            InvalidNamespaceError: 路径已存在
        """
        ns = Namespace(path)
        node = self._root

        for part in ns.parts:
            if part not in node:
                node[part] = {}
            node = node[part]

        if "__emitter__" in node:
            raise InvalidNamespaceError(f"Namespace {path!r} already registered")

        node["__emitter__"] = emitter

    def get(self, path: str) -> Any | None:
        """获取命名空间对应的发射器。

        Args:
            path: 命名空间路径

        Returns:
            事件发射器，如果不存在则返回 None
        """
        ns = Namespace(path)
        node = self._root

        for part in ns.parts:
            if part not in node:
                return None
            node = node[part]

        return node.get("__emitter__")

    def find(self, pattern: str) -> Iterator[tuple[str, Any]]:
        """查找匹配模式的所有命名空间。

        Args:
            pattern: 匹配模式

        Yields:
            (路径, 发射器) 元组
        """

        def _traverse(
            node: dict[str, Any], path: list[str]
        ) -> Iterator[tuple[str, Any]]:
            if "__emitter__" in node:
                full_path = ".".join(path)
                if "*" not in pattern or Namespace(full_path).matches(pattern):
                    yield (full_path, node["__emitter__"])

            for key, child in node.items():
                if key != "__emitter__":
                    yield from _traverse(child, [*path, key])

        yield from _traverse(self._root, [])

    def unregister(self, path: str) -> bool:
        """注销命名空间。

        Args:
            path: 命名空间路径

        Returns:
            是否成功注销
        """
        ns = Namespace(path)
        node = self._root
        parents: list[tuple[dict[str, Any], str]] = []

        for part in ns.parts:
            if part not in node:
                return False
            parents.append((node, part))
            node = node[part]

        if "__emitter__" not in node:
            return False

        del node["__emitter__"]

        # 清理空节点
        for parent, key in reversed(parents):
            if not parent[key]:
                del parent[key]
            else:
                break

        return True
