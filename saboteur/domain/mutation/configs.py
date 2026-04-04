from pydantic import Field

from saboteur.domain.base.configs import BaseConfig
from saboteur.domain.mutation.strategies import MutationStrategy


class MutationConfig(BaseConfig[MutationStrategy]):
    original_data: dict = Field(
        ..., description="The original dictionary data to be mutated."
    )
    max_targets: int = Field(
        default=1,
        gt=0,
        description="Maximum number of unique key paths to mutate in one run.",
    )
    stop_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Probability threshold used when traversing nested dictionaries.",
    )
    seed: int | None = Field(
        default=None,
        description="Optional random seed for reproducible target selection and mutations.",
    )
