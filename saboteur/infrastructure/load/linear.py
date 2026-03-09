import asyncio
import time
from dataclasses import replace

import aiohttp

from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.strategies import LoadStrategy


class LinearLoadStrategy(LoadStrategy):
    async def _run_load_test(self, context: LoadContext) -> list[dict]:
        results = []
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < context.duration_seconds:
                tasks = [
                    self._single_request(session, context)
                    for _ in range(context.concurrency)
                ]

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in batch_results:
                    if isinstance(res, Exception):
                        results.append({"status": 500, "error": str(res)})
                    else:
                        results.append({"status": res.status})

                elapsed = time.time() - start_time
                if elapsed < context.duration_seconds:
                    await asyncio.sleep(context.interval_seconds)

        return results

    async def apply(self, context: LoadContext) -> LoadContext:
        """Run the load test linearly based on the context configuration."""
        results = await self._run_load_test(context)
        return replace(context, responses=results)
