import typing as t

from tonutils.clients.quicknode.provider import QuicknodeProvider
from tonutils.clients.toncenter.client import ToncenterClient
from tonutils.types import NetworkGlobalID


class QuicknodeClient(ToncenterClient):

    def __init__(
        self,
        http_provider_url: str,
        rps: t.Optional[int] = None,
        max_retries: int = 2,
    ) -> None:
        super().__init__(network=NetworkGlobalID.MAINNET)
        self.provider: QuicknodeProvider = QuicknodeProvider(
            http_provider_url=http_provider_url,
            rps=rps,
            max_retries=max_retries,
        )
