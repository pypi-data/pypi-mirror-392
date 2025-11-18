import typing as t

from tonutils.clients.tatum.provider import TatumProvider
from tonutils.clients.toncenter.client import ToncenterClient
from tonutils.types import NetworkGlobalID


class TatumClient(ToncenterClient):

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: str,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: int = 2,
    ) -> None:
        super().__init__(network=network)
        self.provider: TatumProvider = TatumProvider(
            api_key=api_key,
            network=network,
            base_url=base_url,
            rps=rps,
            max_retries=max_retries,
        )
