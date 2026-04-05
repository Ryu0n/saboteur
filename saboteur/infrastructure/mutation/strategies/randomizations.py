import random

from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.utils.logging import logger


class IntegerRandomizationStrategy(MutationStrategy):
    def __init__(self, from_value: int = -1000, to_value: int = 1000):
        self.__from = from_value
        self.__to = to_value

    def is_applicable(self, context: MutationContext) -> bool:
        return context.value_type is int

    def apply(self, context: MutationContext) -> MutationContext:
        random_value = random.randint(self.__from, self.__to)
        logger.debug(
            f"IntegerRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a random integer {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths, value=random_value, value_type=int
        )


class FloatRandomizationStrategy(MutationStrategy):
    def __init__(self, from_value: float = -1000.0, to_value: float = 1000.0):
        self.__from = from_value
        self.__to = to_value

    def is_applicable(self, context: MutationContext) -> bool:
        return context.value_type is float

    def apply(self, context: MutationContext) -> MutationContext:
        random_value = random.uniform(self.__from, self.__to)
        logger.debug(
            f"FloatRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a random float {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths,
            value=random_value,
            value_type=float,
        )


class StringRandomizationStrategy(MutationStrategy):
    def __init__(self, length: int = 10):
        self.__length = length
        self.__chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def is_applicable(self, context: MutationContext) -> bool:
        return context.value_type is str

    def apply(self, context: MutationContext) -> MutationContext:
        random_value = "".join(random.choices(self.__chars, k=self.__length))
        logger.debug(
            f"StringRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a random string {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths, value=random_value, value_type=str
        )


class BooleanRandomizationStrategy(MutationStrategy):
    def is_applicable(self, context: MutationContext) -> bool:
        return context.value_type is bool

    def apply(self, context: MutationContext) -> MutationContext:
        random_value = random.choice([True, False])
        logger.debug(
            f"BooleanRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a random boolean {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths, value=random_value, value_type=bool
        )


class ListRandomizationStrategy(MutationStrategy):
    def is_applicable(self, context: MutationContext) -> bool:
        # Empty lists cannot be sampled from, so exclude them.
        return context.value_type is list and len(context.value) > 0

    def apply(self, context: MutationContext) -> MutationContext:
        random_value = [
            random.choice(context.value) for _ in context.value
        ]
        logger.debug(
            f"ListRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a random list {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths, value=random_value, value_type=list
        )


class DictRandomizationStrategy(MutationStrategy):
    def is_applicable(self, context: MutationContext) -> bool:
        return context.value_type is dict and len(context.value) > 1

    def apply(self, context: MutationContext) -> MutationContext:
        # Shuffle values across keys so the mapping actually changes.
        keys = list(context.value.keys())
        values = list(context.value.values())
        random.shuffle(values)
        random_value = dict(zip(keys, values))
        logger.debug(
            f"DictRandomizationStrategy replacing "
            f"{'.'.join(context.key_paths)}({context.value}) with a shuffled dict {random_value}"
        )
        return MutationContext(
            key_paths=context.key_paths, value=random_value, value_type=dict
        )
