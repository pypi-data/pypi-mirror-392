import typing as t

from tonutils.clients.toncenter.provider import ToncenterProvider
from tonutils.types import NetworkGlobalID


class TatumProvider(ToncenterProvider):
    version = ""

    def __init__(
        self,
        network: NetworkGlobalID,
        api_key: str,
        base_url: t.Optional[str] = None,
        rps: t.Optional[int] = None,
        max_retries: t.Optional[int] = None,
    ) -> None:
        urls = {
            NetworkGlobalID.MAINNET: "https://ton-mainnet.gateway.tatum.io",
            NetworkGlobalID.TESTNET: "https://ton-testnet.gateway.tatum.io",
        }
        base_url = base_url or urls.get(network)

        super().__init__(
            api_key=api_key,
            network=network,
            base_url=base_url,
            rps=rps,
            max_retries=max_retries,
        )
