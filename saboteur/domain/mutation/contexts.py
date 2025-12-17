from dataclasses import dataclass
from typing import Generic, Type

from saboteur.utils.generic import T


@dataclass(frozen=True)
class MutationContext(Generic[T]):
    path: str
    original_value: T
    original_type: Type[T]