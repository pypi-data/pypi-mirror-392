import typing as t

from pyapiq import AsyncClientAPI, async_endpoint
from pyapiq.types import HTTPMethod, ReturnType, RepeatQuery
from pydantic import BaseModel

from tonutils.types import NetworkGlobalID, ContractState


class BlockchainMessagePayload(BaseModel):
    boc: str


class BlockchainConfigResult(BaseModel):
    raw: t.Optional[str] = None


class BlockchainAccountResult(BaseModel):
    balance: int = 0
    status: str = ContractState.NONEXIST.value
    code: t.Optional[str] = None
    data: t.Optional[str] = None
    last_transaction_lt: t.Optional[int] = None
    last_transaction_hash: t.Optional[str] = None


class _BlockchainAccountTransaction(BaseModel):
    raw: t.Optional[str] = None


class BlockchainAccountTransactionsResult(BaseModel):
    transactions: t.Optional[t.List[_BlockchainAccountTransaction]] = None


class BlockchainAccountMethodResult(BaseModel):
    stack: t.Optional[t.List[t.Any]] = None


class TonapiProvider(AsyncClientAPI):
    version = "v2"

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: str,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: t.Optional[int] = None,
    ) -> None:
        urls = {
            NetworkGlobalID.MAINNET: "https://tonapi.io",
            NetworkGlobalID.TESTNET: "https://testnet.tonapi.io",
        }
        base_url = base_url or urls.get(network)
        headers = {"Authorization": f"Bearer {api_key}"}

        super().__init__(
            base_url=base_url,
            headers=headers,
            rps=rps,
            max_retries=max_retries,
        )

    @async_endpoint(
        HTTPMethod.POST,
        path="/blockchain/message",
        return_as=ReturnType.NONE,
    )
    async def blockchain_message(  # type: ignore[empty-body]
        self,
        payload: BlockchainMessagePayload,
    ) -> None: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/blockchain/config",
        return_as=BlockchainConfigResult,
    )
    async def blockchain_config(  # type: ignore[empty-body]
        self,
    ) -> BlockchainConfigResult: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/blockchain/accounts/{address}",
        return_as=BlockchainAccountResult,
    )
    async def blockchain_account(  # type: ignore[empty-body]
        self,
        address: str,
    ) -> BlockchainAccountResult: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/blockchain/accounts/{address}/transactions",
        return_as=BlockchainAccountTransactionsResult,
    )
    async def blockchain_account_transactions(  # type: ignore[empty-body]
        self,
        address: str,
        limit: int = 100,
        after_lt: t.Optional[int] = None,
        before_lt: t.Optional[int] = 0,
        sort_order: t.Optional[t.Literal["asc", "desc"]] = "desc",
    ) -> BlockchainAccountTransactionsResult: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/blockchain/accounts/{address}/methods/{method_name}",
        return_as=BlockchainAccountMethodResult,
    )
    async def blockchain_account_method(  # type: ignore[empty-body]
        self,
        address: str,
        method_name: str,
        args: t.Annotated[t.List[t.Any], RepeatQuery],
    ) -> BlockchainAccountMethodResult: ...
