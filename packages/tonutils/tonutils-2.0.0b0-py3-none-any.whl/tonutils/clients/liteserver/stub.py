from __future__ import annotations

import typing as t
from types import TracebackType

from pytoniq_core import Account, ShardAccount, Transaction, BlockIdExt
from pytoniq_core.crypto.ciphers import Server

from tonutils.exceptions import PytoniqDependencyError
from tonutils.types import AddressLike


class BaseLiteClient:
    inited: bool

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise PytoniqDependencyError(self)

    async def run_get_method(
        self,
        address: AddressLike,
        method: t.Union[int, str],
        stack: t.List[t.Any],
    ) -> t.Any:
        raise PytoniqDependencyError(self)

    async def raw_send_message(self, message: bytes) -> None:
        raise PytoniqDependencyError(self)

    async def raw_get_account_state(
        self,
        address: AddressLike,
    ) -> t.Tuple[
        t.Optional[Account],
        t.Optional[ShardAccount],
    ]:
        raise PytoniqDependencyError(self)

    async def get_config_all(self) -> t.Dict[int, t.Any]:
        raise PytoniqDependencyError(self)

    async def get_transactions(
        self,
        address: AddressLike,
        count: int,
        from_lt: t.Optional[int] = None,
        to_lt: int = 0,
    ) -> t.List[Transaction]:
        raise PytoniqDependencyError(self)


class LiteClient(BaseLiteClient):
    timeout: int
    trust_level: int

    server: Server
    init_key_block: t.Optional[BlockIdExt]

    async def connect(self) -> None:
        raise PytoniqDependencyError(self)

    async def close(self) -> None:
        raise PytoniqDependencyError(self)

    async def __aenter__(self) -> LiteClient:
        raise PytoniqDependencyError(self)

    async def __aexit__(
        self,
        exc_type: t.Optional[type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> None:
        raise PytoniqDependencyError(self)

    @classmethod
    def from_config(
        cls,
        config: dict,
        ls_i: int = 0,
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LiteClient:
        raise PytoniqDependencyError(cls)


class LiteBalancer(BaseLiteClient):

    @classmethod
    def from_config(
        cls,
        config: dict,
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LiteBalancer:
        raise PytoniqDependencyError(cls)

    @classmethod
    def from_mainnet_config(
        cls,
        trust_level: int = 0,
        timeout: int = 10,
    ) -> LiteBalancer:
        raise PytoniqDependencyError(cls)

    @classmethod
    def from_testnet_config(
        cls,
        trust_level: int = 0,
        timeout: int = 10,
    ) -> LiteBalancer:
        raise PytoniqDependencyError(cls)

    async def start_up(self) -> None:
        raise PytoniqDependencyError(self)

    async def close_all(self) -> None:
        raise PytoniqDependencyError(self)

    async def __aenter__(self) -> LiteBalancer:
        raise PytoniqDependencyError(self)

    async def __aexit__(
        self,
        exc_type: t.Optional[type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> None:
        raise PytoniqDependencyError(self)
