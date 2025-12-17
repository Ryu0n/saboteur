import random
from typing import Type, Any, Optional

from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.utils.types import AVAILABLE_PRIMITIVE_TYPES
from saboteur.utils.logging import logger


class TypeFlipStrategy(MutationStrategy):
    def __init__(
        self,
        from_type: Optional[Type[Any]] = random.choice(AVAILABLE_PRIMITIVE_TYPES),
        to_type: Optional[Type[Any]] = random.choice(AVAILABLE_PRIMITIVE_TYPES),
    ):
        self.__from = from_type
        self.__to = to_type

    def is_applicable(self, context: MutationContext) -> bool:
        if not isinstance(context.original_value, self.__from):
            return False
        return True

    def apply(self, context: MutationContext) -> Any:
        try:
            logger.debug(
                f"TypeFlipStrategy converting "
                f"{context.original_value} from {self.__from} to {self.__to}"
            )
            return self.__to(context.original_value)
        except Exception as e:
            logger.warning(
                f"TypeFlipStrategy failed to convert "
                f"{context.original_value} from {self.__from} to {self.__to}: {e}",
                exc_info=True,
            )
            return context.original_value