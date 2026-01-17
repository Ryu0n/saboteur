from dataclasses import dataclass
from typing import Generic, Type

from saboteur.utils.generic import T


@dataclass(frozen=True)
class MutationContext(Generic[T]):
    """Context for original value to be mutated.

    Args:
        Generic (T): The type of the original value.
    """
    path: str
    original_value: T
    original_type: Type[T]