import typing as t

from pyapiq import AsyncClientAPI, async_endpoint
from pyapiq.types import ReturnType, HTTPMethod
from pydantic import BaseModel

from tonutils.types import ContractState, NetworkGlobalID
from tonutils.utils import to_cell, cell_to_b64


class SendBocPayload(BaseModel):
    boc: str

    def model_post_init(self, context: t.Any, /) -> None:
        cell = to_cell(self.boc)
        self.boc = cell_to_b64(cell)


class _Config(BaseModel):
    bytes: t.Optional[str] = None


class _ConfigAll(BaseModel):
    config: t.Optional[_Config] = None


class GetConfigAllResult(BaseModel):
    result: t.Optional[_ConfigAll] = None


class _LastTransactionID(BaseModel):
    lt: t.Optional[str] = None
    hash: t.Optional[str] = None


class _AddressInformation(BaseModel):
    balance: int = 0
    state: t.Optional[str] = ContractState.UNINIT.value
    code: t.Optional[str] = None
    data: t.Optional[str] = None
    last_transaction_id: t.Optional[_LastTransactionID] = None

    def model_post_init(self, _: t.Any) -> None:
        if self.state == "uninitialized":
            self.state = "uninit"


class GetAddressInformationResult(BaseModel):
    result: _AddressInformation = _AddressInformation()


class _Transaction(BaseModel):
    data: t.Optional[str] = None


class GetTransactionResult(BaseModel):
    result: t.Optional[t.List[_Transaction]] = None


class _GetMethod(BaseModel):
    stack: t.List[t.Any]


class RunGetMethodPayload(BaseModel):
    address: str
    method: str
    stack: t.List[t.Any]


class RunGetMethodResul(BaseModel):
    result: t.Optional[_GetMethod] = None


class ToncenterProvider(AsyncClientAPI):
    version = "v2"

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: t.Optional[str] = None,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: t.Optional[int] = None,
    ) -> None:
        urls = {
            NetworkGlobalID.MAINNET: "https://toncenter.com/api",
            NetworkGlobalID.TESTNET: "https://testnet.toncenter.com/api",
        }
        base_url = base_url or urls.get(network)
        headers = {"X-Api-Key": api_key} if api_key else {}

        super().__init__(
            base_url=base_url,
            headers=headers,
            rps=rps,
            max_retries=max_retries,
        )

    @async_endpoint(
        HTTPMethod.POST,
        path="/sendBoc",
        return_as=ReturnType.NONE,
    )
    async def send_boc(  # type: ignore[empty-body]
        self,
        payload: SendBocPayload,
    ) -> None: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/getConfigAll",
        return_as=GetConfigAllResult,
    )
    async def get_config_all(  # type: ignore[empty-body]
        self,
    ) -> GetConfigAllResult: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/getAddressInformation",
        return_as=GetAddressInformationResult,
    )
    async def get_address_information(  # type: ignore[empty-body]
        self,
        address: str,
    ) -> GetAddressInformationResult: ...

    @async_endpoint(
        HTTPMethod.GET,
        path="/getTransactions",
        return_as=GetTransactionResult,
    )
    async def get_transaction(  # type: ignore[empty-body]
        self,
        address: str,
        limit: int = 100,
        from_lt: t.Optional[int] = None,
        to_lt: int = 0,
    ) -> GetTransactionResult: ...

    @async_endpoint(
        HTTPMethod.POST,
        path="/runGetMethod",
        return_as=RunGetMethodResul,
    )
    async def run_get_method(  # type: ignore[empty-body]
        self,
        payload: RunGetMethodPayload,
    ) -> RunGetMethodResul: ...
