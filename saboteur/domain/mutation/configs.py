from pydantic import Field

from saboteur.domain.base.configs import BaseConfig
from saboteur.domain.mutation.strategies import MutationStrategy


class MutationConfig(BaseConfig[MutationStrategy]):
    original_data: dict = Field(
        ..., description="The original dictionary data to be mutated."
    )
