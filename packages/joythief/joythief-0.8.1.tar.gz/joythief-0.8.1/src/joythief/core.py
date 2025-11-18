from __future__ import annotations

import typing as tp
from abc import ABC, abstractmethod
from enum import Enum, auto

if tp.TYPE_CHECKING:
    from typing_extensions import TypeAlias

T = tp.TypeVar("T")


class _MatcherState(Enum):
    UNCOMPARED = auto()
    UNEQUAL_ONCE = auto()
    EQUAL_ONCE = auto()
    OTHER = auto()


class Matcher(tp.Generic[T], ABC):
    """Abstract base class for all other matchers.

    Defines the core requirements for any matcher:

    - Must be `comparable for equality`_ with anything.
    - Must have a sensible `representation`_.

    As ``__eq__`` and ``__repr__`` are defined in
    :py:class:`~joythief.core.Matcher` itself, to provide core matcher
    behaviour, this abstract base class defines two equivalent abstract methods:
    :py:meth:`~joythief.core.Matcher.compare` and
    :py:meth:`~joythief.core.Matcher.represent`. You can write custom matchers
    by implementing these methods:

    .. code-block:: python

        import typing as tp

        from joythief.core import Matcher


        class IsWelcoming(Matcher[str]):

            def compare(self, other: tp.Any) -> bool:
                return other == "hello, world"

            def represent(self) -> str:
                return super().represent()  # 'IsWelcoming()'

    .. _comparable for equality: https://docs.python.org/3/reference/datamodel.html#object.__eq__
    .. _representation: https://docs.python.org/3/reference/datamodel.html#object.__repr__
    """

    __PLACEHOLDER = object()

    _compared_to: tp.Any
    _state: _MatcherState

    def __init__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        super().__init__(*args, **kwargs)
        self._compared_to = self.__PLACEHOLDER
        self._state = _MatcherState.UNCOMPARED

    def __eq__(self, other: tp.Any) -> bool:
        result = self.compare(other)
        if self._state == _MatcherState.UNCOMPARED:
            self._compared_to = other
            self._state = (
                _MatcherState.EQUAL_ONCE
                if result is not NotImplemented and result
                else _MatcherState.UNEQUAL_ONCE
            )
        elif other is not self._compared_to:
            self._compared_to = self.__PLACEHOLDER
            self._state = _MatcherState.OTHER
        return result

    def __ne__(self, other: tp.Any) -> bool:
        return not self == other

    def __repr__(self) -> str:
        if self._state == _MatcherState.EQUAL_ONCE:
            return repr(self._compared_to)
        return self.represent()

    @abstractmethod
    def compare(self, other: tp.Any) -> bool:
        """Equivalent to  `__eq__`__.

        .. __: https://docs.python.org/3/reference/datamodel.html#object.__eq__
        """
        raise NotImplementedError

    @abstractmethod
    def represent(self) -> str:
        """Equivalent to `__repr__`__.

        .. __: https://docs.python.org/3/reference/datamodel.html#object.__repr__
        """
        return f"{type(self).__name__}()"

    @property
    def not_implemented(self) -> bool:
        """The value :py:const:`NotImplemented`, force-cast to :py:class:`bool`.

        ``NotImplemented`` is special-cased in e.g. `__eq__`__, but cannot be
        returned from :py:meth:`compare` without a cast.

        .. __: https://docs.python.org/3/reference/datamodel.html#object.__eq__
        """
        return tp.cast(bool, NotImplemented)


MaybeMatcher: TypeAlias = tp.Union[T, Matcher[T]]
"""Either ``T`` or a matcher of ``T``."""
