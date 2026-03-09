import asyncio
import aiohttp

from saboteur.domain.base.strategies import AsyncBaseStrategy
from saboteur.domain.load.contexts import LoadContext
from saboteur.utils.logging import logger


class LoadStrategy(AsyncBaseStrategy[LoadContext]):
    async def _single_request(self, session: aiohttp.ClientSession, context: LoadContext) -> aiohttp.ClientResponse:
        kwargs = {
            "method": context.method,
            "url": context.url,
            "headers": context.headers,
        }
        if context.body is not None:
            kwargs["json"] = context.body

        async with session.request(**kwargs) as response:
            await response.read()
            logger.debug(f"Response: {response.status}")
            return response

    async def is_applicable(self, context: LoadContext) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                response: aiohttp.ClientResponse = await self._single_request(session, context)
                assert response.status < 400, "is_applicable Response is not OK"
                return True
        except Exception as e:
            return False

