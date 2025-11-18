import typing as t

from tonutils.clients.toncenter.provider import ToncenterProvider
from tonutils.types import NetworkGlobalID


class QuicknodeProvider(ToncenterProvider):
    version = ""

    def __init__(
        self,
        http_provider_url: str,
        rps: t.Optional[int] = None,
        max_retries: t.Optional[int] = None,
    ) -> None:
        super().__init__(
            network=NetworkGlobalID.MAINNET,
            base_url=http_provider_url,
            rps=rps,
            max_retries=max_retries,
        )
