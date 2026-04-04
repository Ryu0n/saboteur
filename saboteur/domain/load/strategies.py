import time
import aiohttp

from saboteur.domain.base.strategies import AsyncBaseStrategy
from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.results import LoadRequestRecord
from saboteur.utils.logging import logger


class LoadStrategy(AsyncBaseStrategy[LoadContext]):
    async def _single_request(
        self, session: aiohttp.ClientSession, context: LoadContext
    ) -> LoadRequestRecord:
        kwargs = {
            "method": context.method,
            "url": context.url,
            "headers": context.headers,
        }
        if context.body is not None:
            kwargs["json"] = context.body

        started_at = time.monotonic()
        try:
            async with session.request(**kwargs) as response:
                await response.read()
                latency_ms = (time.monotonic() - started_at) * 1000
                logger.debug(f"Response: {response.status}")
                return LoadRequestRecord(
                    status=response.status,
                    ok=response.status < 400,
                    latency_ms=latency_ms,
                )
        except Exception as exc:
            latency_ms = (time.monotonic() - started_at) * 1000
            logger.warning("Load request failed: %s", exc)
            return LoadRequestRecord(
                status=500,
                ok=False,
                latency_ms=latency_ms,
                error=str(exc),
            )

    async def is_applicable(self, context: LoadContext) -> bool:
        return bool(context.url and context.method)
