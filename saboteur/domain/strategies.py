from abc import ABC, abstractmethod
from saboteur.domain.contexts import MutationContext


class MutationStrategy(ABC):
    @abstractmethod
    def is_applicable(self, context: MutationContext) -> bool:
        pass
    
    @abstractmethod
    def apply(self, context: MutationContext) -> object:
        pass