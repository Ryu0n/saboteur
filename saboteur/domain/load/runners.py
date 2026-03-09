import time

from saboteur.domain.base.runners import AsyncBaseRunner
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.results import LoadResult


class LoadRunner(
    AsyncBaseRunner[
        LoadConfig,
        LoadStrategy,
        LoadContext,
        LoadResult,
    ]
):
    def _wrap_into_context(self, config: LoadConfig) -> LoadContext:
        return LoadContext(
            url=config.url,
            method=config.method,
            headers=config.headers,
            body=config.body,
            duration_seconds=config.duration_seconds,
            interval_seconds=config.interval_seconds,
            concurrency=config.concurrency,
        )

    async def load(self) -> dict:
        responses = {}
        context = self._wrap_into_context(self._config)
        strategies = await self._get_applicable_strategies(context)
        for strategy in strategies:
            context_with_response = await strategy.apply(context)
            assert context_with_response.responses is not None, (
                "Strategy did not return a response"
            )
            responses[strategy] = context_with_response.responses
        return responses

    async def run(self) -> LoadResult:
        start = time.monotonic()
        responses = await self.load()
        elapsed_time = time.monotonic() - start
        return LoadResult(
            result=responses,
            elapsed_time=elapsed_time,
        )

