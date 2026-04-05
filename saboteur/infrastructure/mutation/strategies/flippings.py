import random
from typing import Type, Any, Optional

from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.utils.types import AVAILABLE_PRIMITIVE_TYPES
from saboteur.utils.logging import logger


class TypeFlipStrategy(MutationStrategy):
    def __init__(
        self,
        to_type: Optional[Type[Any]] = None,
    ):
        # Defer random.choice to instantiation time, not module import time.
        self.__to = to_type if to_type is not None else random.choice(AVAILABLE_PRIMITIVE_TYPES)

    def is_applicable(self, context: MutationContext) -> bool:
        try:
            self.__to(context.value)
        except (ValueError, TypeError):
            return False
        return True

    def apply(self, context: MutationContext) -> MutationContext:
        try:
            logger.debug(
                f"TypeFlipStrategy converting "
                f"{'.'.join(context.key_paths)}({context.value}) to {self.__to}"
            )
            return MutationContext(
                key_paths=context.key_paths,
                value=self.__to(context.value),
                value_type=self.__to,
            )
        except Exception as e:
            logger.warning(
                f"TypeFlipStrategy failed to convert "
                f"{context.value} to {self.__to}: {e}",
                exc_info=True,
            )
            return context
