from typing import Any
from saboteur.domain.strategies import MutationStrategy
from saboteur.domain.contexts import MutationContext


class TypeFlipStrategy(MutationStrategy):
    def is_applicable(self, context: MutationContext) -> bool:
        return isinstance(context.original_value, (int, str))

    def apply(self, context: MutationContext) -> Any:
        val = context.original_value
        if isinstance(val, int):
            return str(val)
        if isinstance(val, str):
            return int(val) if val.isdigit() else -1