from typing import Any
from saboteur.domain.strategies import MutationStrategy
from saboteur.domain.contexts import MutationContext


class NullInjectionStrategy(MutationStrategy):
    def is_applicable(self, context: MutationContext) -> bool:
        return context.original_value is not None

    def apply(self, context: MutationContext) -> Any:
        return None