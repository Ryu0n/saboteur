import asyncio
import time
from dataclasses import replace

import aiohttp

from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.strategies import LoadStrategy


class ExponentialBackoffLoadStrategy(LoadStrategy):
    """
    Load strategy that increases the interval between request batches exponentially.
    """

    def __init__(
        self,
        initial_interval: float = 1.0,
        multiplier: float = 2.0,
        max_interval: float = 60.0,
    ):
        self.initial_interval = initial_interval
        self.multiplier = multiplier
        self.max_interval = max_interval

    async def _run_load_test(self, context: LoadContext) -> list[dict]:
        results = []
        start_time = time.time()
        current_interval = self.initial_interval
        attempt = 0

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

                # Calculate wait time using exponential backoff
                # wait_time = initial_interval * (multiplier ^ attempt)
                wait_time = min(
                    self.initial_interval * (self.multiplier**attempt),
                    self.max_interval,
                )

                elapsed = time.time() - start_time
                if elapsed + wait_time < context.duration_seconds:
                    await asyncio.sleep(wait_time)
                else:
                    break
                
                attempt += 1

        return results

    async def apply(self, context: LoadContext) -> LoadContext:
        """Run the load test with exponential backoff based on the context configuration."""
        results = await self._run_load_test(context)
        return replace(context, responses=results)
