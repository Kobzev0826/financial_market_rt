from collections.abc import Callable
from typing import Any, ParamSpec, Protocol, TypeVar, overload

import backoff
from backoff.types import Details
from loguru import logger


def default_backoff_handler(details: Details) -> None:
    # sentry_exception(details["exception"])  # type: ignore
    logger.error("Backoff: {wait:0.1f} seconds after {tries} tries calling {target}".format(**details))


T = TypeVar("T")
P = ParamSpec("P")


class Decorator(Protocol):
    def __call__(self, func: Callable[P, T], /) -> Callable[P, T]:
        ...


@overload
def default_backoff(f: None = ..., /, **kwargs: Any) -> Decorator:
    ...


@overload
def default_backoff(f: Callable[P, T], /, **kwargs: Any) -> Callable[P, T]:
    ...


def default_backoff(f: Callable[P, T] | None = None, /, **kwargs: Any) -> Decorator | Callable[P, T]:
    """
    Preconfigured backoff decorator with default values for exponential backoff.
    You can use it for sync/async functions/methods matrix. For example:

        @default_backoff
        def foo():
            ...

        @default_backoff(max_time=60)
        async def bar(self, a: int, b: int):
            ...
    """

    def decorator(f: Callable[P, T]) -> Callable[P, T]:
        defaults: dict[str, Any] = {
            "factor": 5,
            "max_value": 60,
            "jitter": None,
            "on_backoff": default_backoff_handler,
        }
        defaults.update(kwargs)
        decorator = backoff.on_exception(backoff.expo, Exception, **defaults)
        wrapped = decorator(f)
        return wrapped

    if f is None:
        return decorator
    else:
        return decorator(f)
