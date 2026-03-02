import asyncio
import aiohttp

from saboteur.domain.base.strategies import BaseStrategy
from saboteur.domain.load.contexts import LoadContext


class LoadStrategy(BaseStrategy[LoadContext]):
    def is_applicable(self, context: LoadContext) -> bool:
        try:
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self.request(context))
            return response.status < 400
        except Exception:
            return False

    async def request(self, context: LoadContext) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=context.method,
                url=context.url,
                headers=context.headers,
                json=context.body,
            ) as response:
                return response
