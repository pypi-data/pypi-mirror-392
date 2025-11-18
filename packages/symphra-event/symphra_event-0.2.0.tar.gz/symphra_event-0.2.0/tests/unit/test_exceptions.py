"""测试 exceptions 模块的异常类"""

from __future__ import annotations

import pytest

from symphra_event.exceptions import (
    EmitError,
    EventEmitterError,
    HandlerRegistrationError,
    InvalidNamespaceError,
    SymphraEventError,
)


class TestSymphraEventError:
    """测试 SymphraEventError"""

    def test_symphra_event_error_is_exception(self) -> None:
        """测试 SymphraEventError 是 Exception 的子类"""
        assert issubclass(SymphraEventError, Exception)

    def test_symphra_event_error_can_be_raised(self) -> None:
        """测试可以抛出 SymphraEventError"""
        with pytest.raises(SymphraEventError, match="test error"):
            raise SymphraEventError("test error")

    def test_symphra_event_error_can_be_caught(self) -> None:
        """测试可以捕获 SymphraEventError"""
        try:
            raise SymphraEventError("test error")
        except SymphraEventError as e:
            assert str(e) == "test error"


class TestEventEmitterError:
    """测试 EventEmitterError"""

    def test_event_emitter_error_is_symphra_event_error(self) -> None:
        """测试 EventEmitterError 是 SymphraEventError 的子类"""
        assert issubclass(EventEmitterError, SymphraEventError)

    def test_event_emitter_error_is_exception(self) -> None:
        """测试 EventEmitterError 是 Exception 的子类"""
        assert issubclass(EventEmitterError, Exception)

    def test_event_emitter_error_can_be_raised(self) -> None:
        """测试可以抛出 EventEmitterError"""
        with pytest.raises(EventEmitterError, match="emitter error"):
            raise EventEmitterError("emitter error")

    def test_event_emitter_error_can_be_caught_as_symphra_event_error(self) -> None:
        """测试可以捕获 EventEmitterError 作为 SymphraEventError"""
        try:
            raise EventEmitterError("emitter error")
        except SymphraEventError as e:
            assert str(e) == "emitter error"


class TestInvalidNamespaceError:
    """测试 InvalidNamespaceError"""

    def test_invalid_namespace_error_is_symphra_event_error(self) -> None:
        """测试 InvalidNamespaceError 是 SymphraEventError 的子类"""
        assert issubclass(InvalidNamespaceError, SymphraEventError)

    def test_invalid_namespace_error_is_exception(self) -> None:
        """测试 InvalidNamespaceError 是 Exception 的子类"""
        assert issubclass(InvalidNamespaceError, Exception)

    def test_invalid_namespace_error_can_be_raised(self) -> None:
        """测试可以抛出 InvalidNamespaceError"""
        with pytest.raises(InvalidNamespaceError, match="invalid namespace"):
            raise InvalidNamespaceError("invalid namespace")


class TestHandlerRegistrationError:
    """测试 HandlerRegistrationError"""

    def test_handler_registration_error_is_event_emitter_error(self) -> None:
        """测试 HandlerRegistrationError 是 EventEmitterError 的子类"""
        assert issubclass(HandlerRegistrationError, EventEmitterError)

    def test_handler_registration_error_is_symphra_event_error(self) -> None:
        """测试 HandlerRegistrationError 是 SymphraEventError 的子类"""
        assert issubclass(HandlerRegistrationError, SymphraEventError)

    def test_handler_registration_error_is_exception(self) -> None:
        """测试 HandlerRegistrationError 是 Exception 的子类"""
        assert issubclass(HandlerRegistrationError, Exception)

    def test_handler_registration_error_can_be_raised(self) -> None:
        """测试可以抛出 HandlerRegistrationError"""
        with pytest.raises(HandlerRegistrationError, match="registration error"):
            raise HandlerRegistrationError("registration error")

    def test_handler_registration_error_can_be_caught_as_event_emitter_error(
        self,
    ) -> None:
        """测试可以捕获 HandlerRegistrationError 作为 EventEmitterError"""
        try:
            raise HandlerRegistrationError("registration error")
        except EventEmitterError as e:
            assert str(e) == "registration error"


class TestEmitError:
    """测试 EmitError"""

    def test_emit_error_is_event_emitter_error(self) -> None:
        """测试 EmitError 是 EventEmitterError 的子类"""
        assert issubclass(EmitError, EventEmitterError)

    def test_emit_error_is_symphra_event_error(self) -> None:
        """测试 EmitError 是 SymphraEventError 的子类"""
        assert issubclass(EmitError, SymphraEventError)

    def test_emit_error_is_exception(self) -> None:
        """测试 EmitError 是 Exception 的子类"""
        assert issubclass(EmitError, Exception)

    def test_emit_error_can_be_raised(self) -> None:
        """测试可以抛出 EmitError"""
        with pytest.raises(EmitError, match="emit error"):
            raise EmitError("emit error")

    def test_emit_error_can_be_caught_as_event_emitter_error(self) -> None:
        """测试可以捕获 EmitError 作为 EventEmitterError"""
        try:
            raise EmitError("emit error")
        except EventEmitterError as e:
            assert str(e) == "emit error"


class TestExceptionHierarchy:
    """测试异常继承层次"""

    def test_complete_exception_hierarchy(self) -> None:
        """测试完整的异常继承层次"""
        # Exception -> SymphraEventError -> EventEmitterError -> HandlerRegistrationError
        assert issubclass(HandlerRegistrationError, EventEmitterError)
        assert issubclass(EventEmitterError, SymphraEventError)
        assert issubclass(SymphraEventError, Exception)

        # Exception -> SymphraEventError -> EventEmitterError -> EmitError
        assert issubclass(EmitError, EventEmitterError)
        assert issubclass(EventEmitterError, SymphraEventError)
        assert issubclass(SymphraEventError, Exception)

        # Exception -> SymphraEventError -> InvalidNamespaceError
        assert issubclass(InvalidNamespaceError, SymphraEventError)
        assert issubclass(SymphraEventError, Exception)
