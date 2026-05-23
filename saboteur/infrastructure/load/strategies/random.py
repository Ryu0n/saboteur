import asyncio
import random
import time
from dataclasses import replace

import aiohttp

from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.results import LoadRequestRecord
from saboteur.domain.load.strategies import LoadStrategy


class RandomLoadStrategy(LoadStrategy):
    async def _run_load_test(self, context: LoadContext) -> list[LoadRequestRecord]:
        results: list[LoadRequestRecord] = []
        start_time = time.monotonic()

        async with aiohttp.ClientSession() as session:
            while time.monotonic() - start_time < context.duration_seconds:
                tasks = [
                    self._single_request(session, context)
                    for _ in range(context.concurrency)
                ]

                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)

                elapsed = time.monotonic() - start_time
                if elapsed < context.duration_seconds:
                    await asyncio.sleep(random.uniform(*context.random_interval))

        return results

    async def apply(self, context: LoadContext) -> LoadContext:
        """Run the load test with randomized intervals between batches."""
        results = await self._run_load_test(context)
        return replace(context, responses=results)
