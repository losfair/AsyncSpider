from ..base_classes import FetcherBaseClass
from ..models import Request, Response
import asyncio
import aiohttp

__all__ = ['AioFetcher']


class AioFetcher(FetcherBaseClass):
    def __init__(self):
        super().__init__()
        self.session = None

    def activate(self):
        async def _get_session():
            return aiohttp.ClientSession()

        loop = asyncio.get_event_loop()
        self.session = loop.run_until_complete(loop.create_task(_get_session()))
        super().activate()

    def close(self):
        self.session.close()
        self.session = None
        super().close()

    async def request(self, request: Request) -> Response:
        with aiohttp.Timeout(request.timeout):
            async with self.session.request(request.method, request.url, **request.kwargs) as resp:
                status = resp.status
                content = await resp.read()
                text = await resp.text()
                return Response(request, status, content, text)
