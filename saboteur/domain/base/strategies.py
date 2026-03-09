from typing import TypeVar, Generic
from abc import ABC, abstractmethod
from saboteur.domain.base.contexts import T_Context


class BaseStrategy(ABC, Generic[T_Context]):
    @abstractmethod
    def is_applicable(self, context: T_Context) -> bool: ...

    @abstractmethod
    def apply(self, context: T_Context) -> T_Context: ...


class AsyncBaseStrategy(ABC, Generic[T_Context]):
    @abstractmethod
    async def is_applicable(self, context: T_Context) -> bool: ...

    @abstractmethod
    async def apply(self, context: T_Context) -> T_Context: ...


T_Strategy = TypeVar("T_Strategy", bound=BaseStrategy)
T_AsyncStrategy = TypeVar("T_AsyncStrategy", bound=AsyncBaseStrategy)
