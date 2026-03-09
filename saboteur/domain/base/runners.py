from typing import Generic
from abc import ABC, abstractmethod

from saboteur.domain.base.configs import T_Config
from saboteur.domain.base.strategies import T_Strategy, T_AsyncStrategy
from saboteur.domain.base.contexts import T_Context
from saboteur.domain.base.results import T_Result


class BaseRunner(
    ABC,
    Generic[
        T_Config,
        T_Strategy,
        T_Context,
        T_Result,
    ],
):
    def __init__(self, config: T_Config):
        self._config = config

    def _get_applicable_strategies(self, context: T_Context) -> list[T_Strategy]:
        return [s for s in self._config.strategies if s.is_applicable(context)]

    @abstractmethod
    def run(self) -> T_Result: ...


class AsyncBaseRunner(
    ABC,
    Generic[
        T_Config,
        T_AsyncStrategy,
        T_Context,
        T_Result,
    ],
):
    def __init__(self, config: T_Config):
        self._config = config

    async def _get_applicable_strategies(
        self, context: T_Context
    ) -> list[T_AsyncStrategy]:
        strategies = []
        for s in self._config.strategies:
            if await s.is_applicable(context):
                strategies.append(s)
        return strategies

    @abstractmethod
    async def run(self) -> T_Result: ...

