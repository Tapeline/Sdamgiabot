import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, cast, get_type_hints

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection

_dishka_container: AsyncContainer | None


def setup_dishka(container: AsyncContainer) -> None:
    global _dishka_container
    _dishka_container = container


def inject[_Ret_T, **_Args_T](
        func: Callable[_Args_T, _Ret_T]
) -> Callable[_Args_T, _Ret_T]:
    wrapped = wrap_injection(
        func=func,
        is_async=True,
        container_getter=(
            lambda _, __: _dishka_container
        ),
    )
    return cast(
        Callable[_Args_T, _Ret_T],
        wrapped
    )


async def periodic[**P](
        interval_sec: float,
        coro: Callable[P, Coroutine[Any, Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs
) -> None:
    """Make a periodic task."""
    while True:
        await asyncio.sleep(interval_sec)
        await coro(*args, **kwargs)


def run_periodic[**P](
        interval_sec: float,
        coro: Callable[P, Coroutine[Any, Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs
) -> Any:
    """Run periodic task."""
    return asyncio.create_task(
        periodic(interval_sec, coro, *args, **kwargs)
    )
