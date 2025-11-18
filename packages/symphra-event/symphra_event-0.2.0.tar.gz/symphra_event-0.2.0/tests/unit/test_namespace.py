"""测试命名空间"""

from __future__ import annotations

import pytest

from symphra_event import Namespace
from symphra_event.exceptions import InvalidNamespaceError


class TestNamespace:
    """命名空间测试套件"""

    def test_create_namespace(self) -> None:
        """测试创建命名空间"""
        ns = Namespace("user.auth.login")
        assert ns.path == "user.auth.login"
        assert ns.parts == ("user", "auth", "login")
        assert ns.name == "login"

    def test_invalid_namespace(self) -> None:
        """测试无效命名空间"""
        with pytest.raises(InvalidNamespaceError):
            Namespace("")

        with pytest.raises(InvalidNamespaceError):
            Namespace("user.123.login")  # 数字开头无效

    def test_namespace_parent(self) -> None:
        """测试父命名空间"""
        ns = Namespace("user.auth.login")
        parent = ns.parent
        assert parent is not None
        assert parent.path == "user.auth"

        grandparent = parent.parent
        assert grandparent is not None
        assert grandparent.path == "user"

        root = grandparent.parent
        assert root is None

    def test_namespace_matches(self) -> None:
        """测试命名空间匹配"""
        ns = Namespace("user.auth.login")

        # 精确匹配
        assert ns.matches("user.auth.login")

        # 单个通配符
        assert ns.matches("user.*.login")
        assert ns.matches("user.*.*")
        assert not ns.matches("user.*")

        # 双通配符
        assert ns.matches("user.**.login")
        assert ns.matches("**.login")
        assert ns.matches("user.**")

    def test_namespace_equality(self) -> None:
        """测试命名空间相等性"""
        ns1 = Namespace("user.auth")
        ns2 = Namespace("user.auth")
        ns3 = Namespace("user.profile")

        assert ns1 == ns2
        assert ns1 != ns3
        assert ns1 == "user.auth"
