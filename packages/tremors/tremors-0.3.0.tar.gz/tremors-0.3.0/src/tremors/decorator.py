"""This module contains decorators for using Tremors loggers.

The :func:`logged` decorator wraps a callable in a Tremors logger context,
and injects that logger into the callable.
"""

import functools
import sys
from typing import TYPE_CHECKING, Any, cast, overload

if TYPE_CHECKING:
    from collections.abc import Callable
elif "sphinx" in sys.modules:
    from collections.abc import Callable  # noqa: TC003

import tremors


def _logged[TRet, **P](
    fn: Callable[P, TRet],
    *collectors: tremors.Collector[Any],
    name: str,
    logger_name: str | None = None,
) -> Callable[P, TRet]:
    @functools.wraps(fn)
    def logged_wrapper(*args: P.args, **kwargs: P.kwargs) -> TRet:
        if "logger" in kwargs:
            return fn(*args, **kwargs)
        with tremors.Logger(*collectors, name=name, logger_name=logger_name) as logger:
            kwargs["logger"] = logger
            return fn(*args, **kwargs)

    return logged_wrapper


@overload
def logged[TRet, **P](
    *collectors: tremors.Collector[Any], name: str, logger_name: str | None
) -> Callable[[Callable[P, TRet]], Callable[P, TRet]]: ...


@overload
def logged[TRet, **P](fn_or_collector: Callable[P, TRet]) -> Callable[P, TRet]: ...


def logged[TRet, **P](
    fn_or_collector: Callable[P, TRet] | tremors.Collector[Any] | None = None,
    *collectors: tremors.Collector[Any],
    name: str | None = None,
    logger_name: str | None = None,
) -> Callable[P, TRet] | Callable[[Callable[P, TRet]], Callable[P, TRet]]:
    """Inject a :class:`~tremors.logger.Logger` into a callable.

    The callable must have a keyword-only parameter ``logger``. If the
    value for ``logger`` is the default value, :data:`from_logged`, it is
    replaced by a logger with the specified collectors, name, and underlying
    logger. This logger is entered, and exited immediately before and after
    the callable runs. Otherwise, the supplied logger will be used in the
    call. A supplied logger will not be automatically entered, and exited.

    Args:
        fn_or_collector: If a callable, e.g., the decorator was used like
            ``@logged``, it is assumed that no collectors were specified,
            and the default collectors are used. Otherwise, it is assumed
            this is the first collector, e.g., the decorator was used like
            ``@logged(some_collector, ..., logger_name=...)``.
        *collectors: The rest of the collectors.
        name: The name of the logger. If None, the callable name is used.
        logger_name: The name of the underlying logger. If None, the standard
            root logger is used.
    """
    if callable(fn_or_collector):
        default_collectors = ()  # TODO @NAS: Implement default collectors.
        return _logged(fn_or_collector, *default_collectors, name=fn_or_collector.__name__)

    def decorator(fn: Callable[P, TRet]) -> Callable[P, TRet]:
        return (
            _logged(
                fn,
                fn_or_collector,
                *collectors,
                name=name if name is not None else fn.__name__,
                logger_name=logger_name,
            )
            if fn_or_collector
            else _logged(
                fn,
                *collectors,
                name=name if name is not None else fn.__name__,
                logger_name=logger_name,
            )
        )

    return decorator


from_logged: tremors.Logger = cast("tremors.Logger", None)
"""A sentinel logger value.

When used as the ``logger`` argument to a :func:`logged` callable, the
callable is wrapped in a :class:`~tremors.logger.Logger` context that is
injected into the callable as the ``logger`` argument.
"""
