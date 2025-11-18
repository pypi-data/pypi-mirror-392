from __future__ import annotations

import base64
import binascii
import typing as t

from pyapiq import AsyncClientAPI
from pytoniq_core import Address, Cell, Slice, Transaction

from tonutils.clients.base import BaseClient
from tonutils.clients.toncenter.provider import (
    RunGetMethodPayload,
    SendBocPayload,
    ToncenterProvider,
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
    cell_to_b64,
    cell_to_hex,
    norm_stack_num,
    norm_stack_cell,
    parse_stack_config,
)


def decode_stack(items: t.List[t.Any]) -> StackItems:
    out: StackItems = []
    for item in items:
        if not (isinstance(item, list) and len(item) == 2):
            continue
        tag, payload = item
        if tag == StackTag.NULL:
            out.append(None)
        elif tag == StackTag.NUM.value:
            out.append(norm_stack_num(payload))
        elif tag in (
            StackTag.CELL.value,
            StackTag.TVM_CELL.value,
            StackTag.SLICE.value,
            StackTag.TVM_SLICE.value,
        ):
            out.append(norm_stack_cell((payload or {}).get("bytes")))
        elif tag in (StackTag.LIST.value, StackTag.TUPLE.value):
            elements = (payload or {}).get("elements") or []
            out.append(decode_stack(elements) if len(elements) > 0 else None)
    return out


def encode_stack(items: t.List[StackItem]) -> t.List[list]:
    out: t.List[t.Any] = []
    for item in items:
        tpe = StackTag.of(item)
        if tpe is StackTag.NUM:
            out.append([StackTag.NUM.value, int(t.cast(int, item))])
        elif tpe is StackTag.CELL:
            cell = item.to_cell() if isinstance(item, Address) else t.cast(Cell, item)
            out.append([StackTag.TVM_CELL.value, cell_to_b64(cell)])
        elif tpe is StackTag.SLICE:
            cell = t.cast(Slice, item).to_cell()
            out.append([StackTag.TVM_SLICE.value, cell_to_b64(cell)])
        elif tpe in (StackTag.LIST, StackTag.TUPLE):
            out.append([tpe.value, {"elements": encode_stack(t.cast(list, item))}])
    return out


def _norm_lt(v: t.Any) -> t.Optional[int]:
    try:
        iv = int(v)
    except (TypeError, ValueError):
        return None
    return iv or None


def _norm_b64_hash_to_hex(b64s: t.Optional[str]) -> t.Optional[str]:
    if not b64s:
        return None
    try:
        h = base64.b64decode(b64s).hex()
    except (binascii.Error, ValueError):
        return None
    return None if h == bytes(32).hex() else h


class ToncenterClient(BaseClient):

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: t.Optional[str] = None,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: int = 2,
    ) -> None:
        self.network: NetworkGlobalID = network
        self.provider: ToncenterProvider = ToncenterProvider(
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
        payload = SendBocPayload(boc=boc)
        return await self.provider.send_boc(payload=payload)

    @ensure_connected
    async def _get_blockchain_config(self) -> t.Dict[int, t.Any]:
        request = await self.provider.get_config_all()

        if request.result is None:
            raise ClientError(
                "Invalid get_config_all response: missing 'result' field."
            )

        if request.result.config is None:
            raise ClientError(
                "Invalid config response: missing 'config' section in result."
            )

        if request.result.config.bytes is None:
            raise ClientError(
                "Invalid config response: missing 'bytes' field in 'config' section."
            )

        config_cell = Cell.one_from_boc(request.result.config.bytes)
        config_slice = config_cell.begin_parse()
        return parse_stack_config(config_slice)

    @ensure_connected
    async def _get_contract_info(self, address: str) -> ContractStateInfo:
        request = await self.provider.get_address_information(address)

        contract_info = ContractStateInfo(
            balance=int(request.result.balance),
            state=ContractState(request.result.state),
        )
        if bool(request.result.code):
            contract_info.code_raw = cell_to_hex(request.result.code)

        if bool(request.result.data):
            contract_info.data_raw = cell_to_hex(request.result.data)

        last_transaction_lt = last_transaction_hash = None
        if request.result.last_transaction_id:
            last_transaction_lt = _norm_lt(request.result.last_transaction_id.lt)
            last_transaction_hash = _norm_b64_hash_to_hex(
                request.result.last_transaction_id.hash
            )

        contract_info.last_transaction_lt = last_transaction_lt
        contract_info.last_transaction_hash = last_transaction_hash

        if (
            last_transaction_lt is None
            and last_transaction_hash is None
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
        if from_lt is not None:
            from_lt += 1

        request = await self.provider.get_transaction(
            address=address,
            limit=limit,
            from_lt=from_lt,
            to_lt=to_lt,
        )

        transactions = []
        for tx in request.result or []:
            if tx.data is not None:
                tx_slice = Slice.one_from_boc(tx.data)
                transactions.append(Transaction.deserialize(tx_slice))

        return transactions

    @ensure_connected
    async def _run_get_method(
        self,
        address: str,
        method_name: str,
        stack: t.Optional[t.List[t.Any]] = None,
    ) -> t.List[t.Any]:
        payload = RunGetMethodPayload(
            address=address,
            method=method_name,
            stack=encode_stack(stack or []),
        )
        request = await self.provider.run_get_method(payload=payload)
        if request.result is None:
            return []
        return decode_stack(request.result.stack or [])

    async def connect(self) -> None:
        await self.provider.ensure_session()

    async def close(self) -> None:
        await self.provider.close()
