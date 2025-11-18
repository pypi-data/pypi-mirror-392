from __future__ import annotations

import abc
import typing as t

import aiohttp
from pytoniq_core import (
    Address,
    BlockIdExt,
    Cell,
    SimpleAccount,
    Slice,
    Transaction,
    VmTuple,
)

from tonutils.decorators import ensure_connected
from tonutils.exceptions import PytoniqDependencyError

try:
    # noinspection PyPackageRequirements
    from pytoniq import LiteClient, LiteBalancer

    pytoniq_installed = True
except ImportError:
    from tonutils.clients.liteserver.stub import LiteClient, LiteBalancer

    pytoniq_installed = False

from tonutils.clients.base import BaseClient
from tonutils.types import (
    ContractState,
    ContractStateInfo,
    NetworkGlobalID,
    StackItem,
    StackItems,
    PublicKey,
)
from tonutils.utils import (
    cell_to_hex,
    norm_stack_num,
    norm_stack_cell,
)


def decode_stack(items: t.List[t.Any]) -> StackItems:
    out: StackItems = []
    for item in items:
        if item is None:
            out.append(None)
        elif isinstance(item, int):
            out.append(norm_stack_num(item))
        elif isinstance(item, Address):
            out.append(item.to_cell())
        elif isinstance(item, (Cell, Slice)):
            out.append(norm_stack_cell(item))
        elif isinstance(item, VmTuple):
            out.append(decode_stack(item.list))
        elif isinstance(item, list):
            out.append(decode_stack(item))
    return out


def encode_stack(items: t.List[StackItem]) -> t.List[t.Any]:
    out: t.List[t.Any] = []
    for item in items:
        if isinstance(item, int):
            out.append(item)
        elif isinstance(item, Address):
            out.append(item.to_cell().to_slice())
        elif isinstance(item, (Cell, Slice)):
            out.append(item)
        elif isinstance(item, (list, tuple)):
            out.append(encode_stack(list(item)))
    return out


class BaseLiteserverClient(BaseClient, abc.ABC):

    @classmethod
    async def get_global_config(
        cls,
        network: NetworkGlobalID,
    ) -> t.Dict[t.Any, t.Any]:
        urls = {
            NetworkGlobalID.MAINNET: "https://ton.org/global-config.json",
            NetworkGlobalID.TESTNET: "https://ton.org/testnet-global.config.json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(urls[network]) as r:
                return await r.json()

    @ensure_connected
    async def _send_boc(self, boc: str) -> None:
        await self.provider.raw_send_message(bytes.fromhex(boc))

    @ensure_connected
    async def _get_blockchain_config(self) -> t.Dict[int, t.Any]:
        return await self.provider.get_config_all()

    @ensure_connected
    async def _get_contract_info(self, address: str) -> ContractStateInfo:
        account, shard_account = await self.provider.raw_get_account_state(address)

        simple_account = SimpleAccount.from_raw(account, Address(address))
        contract_info = ContractStateInfo(balance=simple_account.balance)

        if simple_account.state is not None:
            state_init = simple_account.state.state_init
            if state_init is not None:
                if state_init.code is not None:
                    contract_info.code_raw = cell_to_hex(state_init.code)
                if state_init.data is not None:
                    contract_info.data_raw = cell_to_hex(state_init.data)

            contract_info.state = ContractState(
                "uninit"
                if simple_account.state.type_ == "uninitialized"
                else simple_account.state.type_
            )

        if shard_account is not None:
            if shard_account.last_trans_lt is not None:
                contract_info.last_transaction_lt = int(shard_account.last_trans_lt)
            if shard_account.last_trans_hash is not None:
                contract_info.last_transaction_hash = (
                    shard_account.last_trans_hash.hex()
                )
        if (
            contract_info.last_transaction_lt is None
            and contract_info.last_transaction_hash is None
            and contract_info.state == ContractState.UNINIT
        ):
            contract_info.state = ContractState.NONEXIST

        return contract_info

    @ensure_connected
    async def _get_contract_transactions(
        self,
        address: str,
        limit: int = 100,
        from_lt: t.Optional[int] = None,
        to_lt: int = 0,
    ) -> t.List[Transaction]:
        return await self.provider.get_transactions(
            address=Address(address),
            count=limit,
            from_lt=from_lt,
            to_lt=to_lt,
        )

    @ensure_connected
    async def _run_get_method(
        self,
        address: str,
        method_name: str,
        stack: t.Optional[t.List[t.Any]] = None,
    ) -> t.List[t.Any]:
        stack_result = await self.provider.run_get_method(
            address=address,
            method=method_name,
            stack=encode_stack(stack or []),
        )
        return decode_stack(stack_result or [])


class LiteserverClient(BaseLiteserverClient):

    def __init__(
        self,
        network: NetworkGlobalID,
        host: str,
        port: int,
        server_pub_key: str,
        timeout: int = 10,
        trust_level: int = 2,
        init_key_block: t.Optional[BlockIdExt] = None,
    ) -> None:
        self.network: NetworkGlobalID = network
        self.provider: LiteClient = LiteClient(
            host=host,
            port=port,
            server_pub_key=server_pub_key,
            timeout=timeout,
            trust_level=trust_level,
            init_key_block=init_key_block,
        )

    async def __aenter__(self) -> LiteserverClient:
        await self.provider.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[t.Any],
    ) -> None:
        await self.provider.__aexit__(exc_type, exc_value, traceback)

    @classmethod
    def from_config(
        cls,
        network: NetworkGlobalID,
        config: t.Dict[t.Any, t.Any],
        ls_index: int = 0,
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LiteserverClient:
        if not pytoniq_installed:
            raise PytoniqDependencyError(cls)
        client = LiteClient.from_config(
            config=config,
            ls_i=ls_index,
            trust_level=trust_level,
            timeout=timeout,
        )
        pub_key = PublicKey(client.server.ed25519_public.encode())
        return LiteserverClient(
            network=network,
            host=client.server.host,
            port=client.server.port,
            server_pub_key=pub_key.as_b64,
            trust_level=client.trust_level,
            init_key_block=client.init_key_block,
            timeout=client.timeout,
        )

    @classmethod
    async def from_network(
        cls,
        network: NetworkGlobalID,
        ls_index: int = 0,
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LiteserverClient:
        config = await cls.get_global_config(network)
        return cls.from_config(
            network=network,
            config=config,
            ls_index=ls_index,
            trust_level=trust_level,
            timeout=timeout,
        )

    async def connect(self) -> None:
        await self.provider.connect()

    async def close(self) -> None:
        await self.provider.close()


class LitebalancerClient(BaseLiteserverClient):

    def __init__(
        self,
        network: NetworkGlobalID,
        clients: t.List[LiteClient],
        timeout: int = 10,
    ) -> None:
        self.network: NetworkGlobalID = network
        self.provider: LiteBalancer = LiteBalancer(
            peers=clients,
            timeout=timeout,
        )

    async def __aenter__(self) -> LitebalancerClient:
        await self.provider.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[t.Any],
    ) -> None:
        await self.provider.__aexit__(exc_type, exc_value, traceback)

    @classmethod
    def from_config(
        cls,
        network: NetworkGlobalID,
        config: t.Dict[t.Any, t.Any],
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LitebalancerClient:
        if not pytoniq_installed:
            raise PytoniqDependencyError(cls)
        clients = [
            LiteClient.from_config(config, ls_index, trust_level, timeout)
            for ls_index in range(len(config["liteservers"]))
        ]
        return cls(network=network, clients=clients)

    @classmethod
    async def from_network(
        cls,
        network: NetworkGlobalID,
        trust_level: int = 2,
        timeout: int = 10,
    ) -> LitebalancerClient:
        config = await cls.get_global_config(network)
        return cls.from_config(
            network=network,
            config=config,
            trust_level=trust_level,
            timeout=timeout,
        )

    async def connect(self) -> None:
        await self.provider.start_up()

    async def close(self) -> None:
        await self.provider.close_all()
