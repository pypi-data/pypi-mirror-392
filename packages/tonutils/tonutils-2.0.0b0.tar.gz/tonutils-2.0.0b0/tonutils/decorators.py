import functools
import typing as t

from tonutils.exceptions import ClientNotConnectedError
from tonutils.protocols.client import ClientProtocol

__all__ = ["ensure_connected"]

_F = t.TypeVar(
    "_F",
    bound=t.Callable[..., t.Awaitable[t.Any]],
)


def ensure_connected(func: _F) -> _F:
    @functools.wraps(func)
    async def wrapper(self: ClientProtocol, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if not self.is_connected:
            raise ClientNotConnectedError(self)

        return await func(self, *args, **kwargs)

    return t.cast(_F, wrapper)
