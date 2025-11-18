"""This module contains the Tremors Logger and Collector definition.

A Tremors logger can be used as a drop-in replacement for a standard
:class:`~logging.Logger`. Collectors may be attached to a logger. Each time
a message is logged, the collectors run if they are enabled for the message
level. When a collector runs, it may update its state. A logger adds the
current state of all of its collectors to any :class:`~logging.LogRecord`
that it produces.

A logger may also be used as a context manager. When used this way, loggers
maintain a hierarchy. Each logger has a parent logger, unless it is the root
logger. The root logger assigns a :attr:`~Logger.group_id` that is shared
by all loggers in the hierarchy. Each logger has a :attr:`~Logger.path` from
its root logger to itself. Hierarchies may be nested by explicitly creating
a new root logger within an existing hierarchy.  The loggers in the nested
hierarchy will have a different group ID than the loggers in the containing
hierarchy. The paths in the nested hierarchy will also start from the new
root logger.

When a logger context is entered, or exited, a message is automatically
logged at a specified level, and collectors will run if they are enabled
for the message level. This allows us to define collectors that measure
lifecycle information, such as the duration of a context, or how much memory
was allocated at the beginning, and end of a context.

Each Tremors logger uses an underlying standard logger that may
be specified. The underlying logger can be configured in the normal
fashion. Underlying loggers may be shared by Tremors loggers. In fact,
it is common for all Tremors loggers to use the standard root logger. The
Tremors logger simply adds the states of its collectors to the records
produced by its standard logger. These augmented records can then be
processed by any :class:`~logging.Filter`, :class:`~logging.Formatter`,
or :class:`~logging.Handler` that knows about the extra record attributes.

A collector may be bundled with a formatter that can extract the collector
state from a record, and format it. This formatter can be used in a
filter, formatter, or handler that has been configured for the underling
logger. Tremors comes with many useful collector bundles. But you can also
define custom collectors, and bundles.
"""

from __future__ import annotations

import contextvars
import functools
import itertools
import logging
import sys
import uuid
from typing import TYPE_CHECKING, Any, NamedTuple, Self

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, MutableMapping
    from types import TracebackType
elif "sphinx" in sys.modules:
    from collections.abc import Callable, Mapping  # noqa: TC003
    from types import TracebackType  # noqa: TC003

_current_logger: contextvars.ContextVar[Logger | None] = contextvars.ContextVar(
    "_current_logger", default=None
)


class Collector[TState](NamedTuple):
    """The collector specification.

    Attributes:
        name: The name of the collector. When the collector runs
            for a logged message, the collector's state is added to the
            :class:`~logging.LogRecord`, and may be retrieved using this name.
        level: The minimum level a logged message must be for the collector
            to run.
        state: The initial state of the collector. Each time the collector
            runs, it may update this state.
        collect: When the collector runs, this function is called with the
            current state, and the logger. It returns the new state.
    """

    name: str
    level: int
    state: TState
    collect: Callable[[TState, Logger], TState]


def _collectors_reducer[T](
    acc: tuple[MutableMapping[str, Collector[T]], MutableMapping[str, T]],
    curr: tuple[tuple[Logger, int], tuple[str, Collector[T]]],
) -> tuple[MutableMapping[str, Collector[T]], MutableMapping[str, T]]:
    acc_collectors, acc_extra = acc
    (logger, level), (name, curr_c) = curr
    if curr_c.level != logging.NOTSET and level < curr_c.level:
        acc_collectors[name] = curr_c
        acc_extra[name] = curr_c.state
        return acc_collectors, acc_extra
    state = curr_c.collect(curr_c.state, logger)
    acc_collectors[name] = Collector(curr_c.name, curr_c.level, state, curr_c.collect)
    acc_extra[name] = state
    return acc_collectors, acc_extra


EXTRA_KEY = "tremors"


class Logger(logging.LoggerAdapter[logging.Logger]):
    """The Tremors logger.

    Args:
        *collectors: Collectors that will be attached to the logger, and will
            be run for every logged message for which the collector is enabled.
        name: The name of the logger. This name is logged in entering, and
            exiting messages. This name is used to generate the path, but
            may be altered in the path to be unique in the hierarchy.
        logger_name: The name of the underlying :class:`~logging.Logger`
            that will be used to log messages. If None, the root logger will
            be used.
        ctx_level: The level at which entered and exited messages will
            be logged.
        is_root: If True, a root logger with no parent that starts a new
            hierarchy will be created.
    """

    def __init__(
        self,
        *collectors: Collector[Any],
        name: str,
        logger_name: str | None = None,
        ctx_level: int = logging.INFO,
        is_root: bool = False,
    ) -> None:
        """Initialize the logger."""
        super().__init__(logging.getLogger(logger_name))
        self._name = name
        self._collectors: Mapping[str, Collector[Any]] = {c.name: c for c in collectors}
        self._entered = 0
        self._ctx_level = ctx_level
        self._cv_token: contextvars.Token[Logger | None] | None = None
        self._is_root = is_root
        self._parent: Logger | None = None
        self._group_id: uuid.UUID | None = None
        self._path: tuple[str, ...] | None = None
        self._path_registry: dict[str, int] = {}

    def __enter__(self) -> Self:
        """Enter the context.

        The logger will only be added to the hierarchy, and log the entered
        message if the logger is not currently entered, i.e., it has not
        been entered before, or the number of times it has been entered,
        and exited are balanced.

        If the logger is added to the hierarchy, an entered message will be
        logged at the ``ctx_level`` the logger was initialized with. These
        messages may be suppressed by specifying a sufficiently low
        level. These messages may also be filtered out. The message text
        will be ``"entered: %s" % name`` where ``name`` is the name the
        logger was initialized with.
        """
        self._entered += 1
        if self._entered != 1:
            return self
        if not self._is_root:
            self._parent = _current_logger.get()
        if self._parent:
            self._group_id = self._parent.group_id
            self._path = self._parent.register_path(self)
        else:
            self._group_id = uuid.uuid4()
            self._path = (self._name,)
        self._cv_token = _current_logger.set(self)
        self.log(self._ctx_level, "entered: %s", self._name)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context.

        The logger will only be removed from the hierarchy if it is exiting
        for the last time, i.e., the number of times it has been entered,
        and exited are balanced.

        If the logger is removed from the hierarchy, or it is exiting
        due to an exception, an exited message will be logged. See
        :meth:`~Logger.__enter__` for how the message is logged, and how to
        suppress it.  The message text will be ``"exited: %s" % name``.
        """
        self._entered -= 1
        exc_info = (exc_type, exc_val, exc_tb) if exc_type and exc_val else None
        if self._entered == 0 or exc_info:
            self.log(self._ctx_level, "exited: %s", self._name, exc_info=exc_info)
        if self._entered == 0 and self._cv_token:
            _current_logger.reset(self._cv_token)

    @property
    def group_id(self) -> uuid.UUID | None:
        """The group ID for the hierarchy assigned by the root logger."""
        return self._group_id

    @property
    def name(self) -> str:
        """The logger name.

        This is not the name of the underlying Python logger. This is the name
        of the logger in the path if the logger has been entered. Otherwise,
        it is the ``name`` that the logger was initialized with.
        """
        return self._path[-1] if self._path else self._name

    @property
    def parent(self) -> Logger | None:
        """The parent logger, or None if this is a root logger."""
        return self._parent

    @property
    def path(self) -> tuple[str, ...] | None:
        """The logger path.

        The path is a sequence of logger names following the hierarchy of
        loggers from the root logger to this one. The final name in the
        path will be the name that the logger was initialized with if a
        logger with the same name has not been registered at that path index
        yet. Otherwise, an incremental number is appended to the initial
        name to get a unique name for that path index.

        Example:
            If there are 2 loggers named "baz" at the third level of the
            hierarchy, their respecitve paths will be:

            .. code-block:: python

                ["foo", "bar", "baz"]
                ["foo", "bar", "baz2"]
        """
        return self._path

    def register_path(self, logger: Logger) -> tuple[str, ...]:
        """A logger can register a path for itself with its parent.

        This method should not be called directly. The logger will
        automatically register itself with its parent.
        """
        if logger.parent is not self:
            msg = "logger is not a child of this logger."
            raise RuntimeError(msg)
        if not self._path:
            msg = "path has not been initialized"
            raise RuntimeError(msg)
        name = logger.name
        if name not in self._path_registry:
            self._path_registry[name] = 1
            return (*self._path, name)
        self._path_registry[name] += 1
        return (*self._path, f"{name}{self._path_registry[name]}")

    def log(  # noqa: PLR0913
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Run collectors, and log a message at the given level.

        The arguments are interpreted as for :meth:`~logging.Logger.debug`.
        """
        initial_collectors: MutableMapping[str, Collector[Any]] = {}
        initial_extra: MutableMapping[str, Any] = {}
        self._collectors, own_extra = functools.reduce(
            _collectors_reducer,
            zip(itertools.repeat((self, level)), self._collectors.items(), strict=False),
            (initial_collectors, initial_extra),
        )
        return self.logger.log(
            level,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra={**extra, EXTRA_KEY: own_extra} if extra is not None else {EXTRA_KEY: own_extra},
            **kwargs,
        )
