import inspect
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, TypeAlias, TypeVar

from kong.common.app_logger import app_logger
from kong.sdk.config import config

logger = app_logger(__name__)

T = TypeVar("T")

Unused: TypeAlias = tuple[timedelta, Callable[[Any], Coroutine[None, None, T]]]


@dataclass(frozen=True)
class StoredState:
    value: Any
    last_access_time: datetime
    unused: Unused | None = None


class UseState:
    def __init__(self, ttl: timedelta):
        self._states: dict[str, StoredState] = {}
        self._ttl = ttl

    @property
    def states(self):
        return self._states

    async def recycle(self):
        for key in list(self._states.keys()):
            state = self._states[key]
            if (datetime.now() - state.last_access_time) >= (
                state.unused[0] if state.unused else self._ttl
            ):
                if state.unused:
                    try:
                        await state.unused[1](state.value)
                        logger.debug("run unused", lambda: dict(key=key))
                    except Exception as ex:
                        logger.error(
                            "run unused failed", lambda: dict(key=key), error=ex
                        )
                        raise ex

                del self._states[key]
                logger.debug("recycle", lambda: dict(expired=key))


__states = UseState(ttl=config.extension.state.ttl)


async def use_state(
    key: str,
    producer: Callable[[], T],
    unused: Unused = None,
) -> T:
    await __states.recycle()

    if key not in __states.states:
        value = (
            await producer() if inspect.iscoroutinefunction(producer) else producer()
        )
        __states.states[key] = StoredState(
            value=value,
            last_access_time=datetime.now(),
            unused=unused,
        )

        logger.info(
            "create state",
            lambda: dict(key=key, value=logger.shorten(value)),
        )

        return value

    stored_state = __states.states[key]

    logger.info(
        "reuse state",
        lambda: dict(key=key, value=logger.shorten(stored_state)),
    )

    __states.states[key] = StoredState(
        value=stored_state.value,
        last_access_time=datetime.now(),
        unused=stored_state.unused,
    )

    return stored_state.value
