from dataclasses import dataclass
from typing import TypeVar, Generic, Type


T = TypeVar('T')

@dataclass(frozen=True)
class MutationContext(Generic[T]):
    path: str
    original_value: T
    original_type: Type[T]