from __future__ import annotations

import typing as t

from pyapiq import AsyncClientAPI
from pytoniq_core import Address, Cell, Slice, Transaction

from tonutils.clients.base import BaseClient
from tonutils.clients.tonapi.provider import (
    BlockchainMessagePayload,
    TonapiProvider,
)
from tonutils.decorators import ensure_connected
from tonutils.exceptions import ClientError
from tonutils.types import (
    ContractState,
    ContractStateInfo,
    NetworkGlobalID,
    StackTag,
    StackItem,
    StackItems,
)
from tonutils.utils import (
    cell_to_hex,
    norm_stack_num,
    norm_stack_cell,
    parse_stack_config,
)


def decode_stack(items: t.List[t.Any]) -> StackItems:
    out: StackItems = []
    for item in items:
        if not isinstance(item, dict):
            continue
        tpe = item.get("type")
        val = item.get(tpe)
        if tpe == StackTag.NULL.value:
            out.append(None)
        elif tpe == StackTag.NUM.value and val is not None:
            out.append(norm_stack_num(t.cast(str | int, val)))
        elif tpe in (StackTag.CELL.value, StackTag.SLICE.value):
            out.append(norm_stack_cell(val))
        elif tpe in (StackTag.LIST.value, StackTag.TUPLE.value):
            inner: t.List[t.Any] = []
            for el in val or []:
                inner.append(decode_stack([el])[0] if isinstance(el, dict) else el)
            out.append(inner)
    return out


def encode_stack(items: t.List[StackItem]) -> t.List[t.Any]:
    out: t.List[t.Any] = []
    for item in items:
        tpe = StackTag.of(item)
        if tpe == StackTag.NUM:
            out.append(hex(t.cast(int, item)))
        elif tpe == StackTag.CELL:
            cell = item.to_cell() if isinstance(item, Address) else item
            out.append(cell_to_hex(cell))
        elif tpe == StackTag.SLICE:
            cell = t.cast(Slice, item).to_cell()
            out.append(cell_to_hex(cell))
        elif tpe in (StackTag.LIST, StackTag.TUPLE):
            out.append(encode_stack(t.cast(list, item)))
    return out


class TonapiClient(BaseClient):

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: str,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: int = 2,
    ) -> None:
        self.network: NetworkGlobalID = network
        self.provider: TonapiProvider = TonapiProvider(
            api_key=api_key,
            network=network,
            base_url=base_url,
            rps=rps,
            max_retries=max_retries,
        )

    async def __aenter__(self) -> AsyncClientAPI:
        return await self.provider.__aenter__()

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[t.Any],
    ) -> None:
        await self.provider.__aexit__(exc_type, exc_value, traceback)

    @ensure_connected
    async def _send_boc(self, boc: str) -> None:
        payload = BlockchainMessagePayload(boc=boc)
        return await self.provider.blockchain_message(payload=payload)

    @ensure_connected
    async def _get_blockchain_config(self) -> t.Dict[int, t.Any]:
        result = await self.provider.blockchain_config()

        if result.raw is None:
            raise ClientError("Invalid config response: missing 'raw' field")

        config_cell = Cell.one_from_boc(result.raw)[0]
        config_slice = config_cell.begin_parse()
        return parse_stack_config(config_slice)

    @ensure_connected
    async def _get_contract_info(self, address: str) -> ContractStateInfo:
        result = await self.provider.blockchain_account(address)

        contract_info = ContractStateInfo(
            balance=result.balance,
            state=ContractState(result.status),
            last_transaction_lt=result.last_transaction_lt,
            last_transaction_hash=result.last_transaction_hash,
        )
        if result.code is not None:
            contract_info.code_raw = cell_to_hex(result.code)
        if result.data is not None:
            contract_info.data_raw = cell_to_hex(result.data)

        return contract_info

    @ensure_connected
    async def _get_contract_transactions(
        self,
        address: str,
        limit: int = 100,
        from_lt: t.Optional[int] = None,
        to_lt: int = 0,
    ) -> t.List[Transaction]:
        if from_lt is not None:
            from_lt += 1

        result = await self.provider.blockchain_account_transactions(
            address=address,
            limit=limit,
            after_lt=to_lt,
            before_lt=from_lt,
        )

        transactions = []
        for tx in result.transactions or []:
            if tx.raw is not None:
                tx_slice = Slice.one_from_boc(tx.raw)
                transactions.append(Transaction.deserialize(tx_slice))

        return transactions

    @ensure_connected
    async def _run_get_method(
        self,
        address: str,
        method_name: str,
        stack: t.Optional[t.List[t.Any]] = None,
    ) -> t.List[t.Any]:
        result = await self.provider.blockchain_account_method(
            address=address,
            method_name=method_name,
            args=encode_stack(stack or []),
        )
        return decode_stack(result.stack or [])

    async def connect(self) -> None:
        await self.provider.ensure_session()

    async def close(self) -> None:
        await self.provider.close()
