from typing import Any

from pydantic import BaseModel, Field

from saboteur.domain.base.results import BaseResult


class MutationTrace(BaseModel):
    key_path: list[str] = Field(
        default_factory=list,
        description="Nested key path selected for mutation.",
    )
    strategy: str = Field(..., description="Strategy class name used for the mutation.")
    original_value: Any = Field(..., description="Value before mutation.")
    mutated_value: Any = Field(..., description="Value returned by the strategy.")


class MutationResult(BaseResult):
    applied_mutations: list[MutationTrace] = Field(
        default_factory=list,
        description="Detailed trace of each mutation applied during the run.",
    )
