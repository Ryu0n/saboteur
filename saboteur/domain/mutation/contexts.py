import copy

from dataclasses import dataclass
from typing import Generic, Type

from saboteur.domain.base.contexts import BaseContext
from saboteur.utils.generic import T


@dataclass(frozen=True)
class MutationContext(BaseContext, Generic[T]):
    """Context holding the value at a specific key path to be mutated.

    Args:
        Generic (T): The type of the value.
    """

    key_paths: list[str]
    value: T
    value_type: Type[T]

    def mutate(self, data: dict) -> dict:
        """Write self.value into data at the key path described by self.key_paths.

        Args:
            data (dict): The data to be mutated.

        Raises:
            ValueError: If the key path is invalid.

        Returns:
            dict: A deep copy of data with the value replaced.
        """
        copied = copy.deepcopy(data)
        temp = copied

        for k in self.key_paths[:-1]:
            temp = temp[k]
            if not isinstance(temp, dict):
                raise ValueError(f"Invalid key path: {self.key_paths}")

        temp[self.key_paths[-1]] = self.value
        return copied
