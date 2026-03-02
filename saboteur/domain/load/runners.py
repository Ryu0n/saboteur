import time

from saboteur.domain.base.runners import BaseRunner
from saboteur.domain.load.configs import LoadTestConfig
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.results import LoadResult


class LoadRunner(
    BaseRunner[
        LoadTestConfig,
        LoadStrategy,
        LoadContext,
    ]
):
    def _wrap_into_context(self, config: LoadTestConfig) -> LoadContext:
        return LoadContext(
            url=config.url,
            method=config.method,
            headers=config.headers,
            body=config.body,
        )

    def load(self) -> None:
        responses = {}
        context = self._wrap_into_context(self._config)
        strategies = self._get_applicable_strategies(context)
        for strategy in strategies:
            context_with_response = strategy.apply(context)
            assert context_with_response.response is not None, (
                "Strategy did not return a response"
            )
            responses[strategy] = context_with_response.response
        return responses

    def run(self) -> None:
        start = time.monotonic()
        responses = self.load()
        elapsed_time = time.monotonic() - start
        return LoadResult(
            result=responses,
            elapsed_time=elapsed_time,
        )
