import copy

from dataclasses import dataclass
from typing import Generic, Type

from saboteur.domain.base.contexts import BaseContext
from saboteur.utils.generic import T


@dataclass(frozen=True)
class MutationContext(BaseContext, Generic[T]):
    """Context for original value to be mutated.

    Args:
        Generic (T): The type of the original value.
    """

    key_paths: list[str]
    original_value: T
    original_type: Type[T]

    def mutate(self, data: dict) -> dict:
        """Replace the original value in the data with the mutated value.

        Args:
            data (dict): The data to be mutated.

        Raises:
            ValueError: _description_

        Returns:
            dict: The mutated data.
        """
        copied = copy.deepcopy(data)
        temp = copied

        for k in self.key_paths[:-1]:
            temp = temp[k]
            if not isinstance(temp, dict):
                raise ValueError(f"Invalid key path: {self.key_paths}")

        temp[self.key_paths[-1]] = self.original_value
        return copied
