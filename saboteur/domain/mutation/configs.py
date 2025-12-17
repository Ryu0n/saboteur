from typing import Optional, List
from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from saboteur.domain.mutation.strategies import MutationStrategy


class MutationConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    strategies: List[MutationStrategy] = Field(default_factory=list, description="List of mutation strategies to be used.")
    apply_all_strategies: bool = Field(default=False, description="Flag to determine if all applicable strategies should be applied.")
    num_strategies: Optional[int] = Field(default=None, description="Number of strategies to apply randomly if not applying all.")
    apply_all_keys: bool = Field(default=False, description="Flag to determine if mutations should be applied to all keys in the data structure.")
    num_keys: Optional[int] = Field(default=None, description="Number of keys to mutate randomly if not applying to all keys.")
    
    @model_validator(mode="after")
    def validate_strategy_counts(self):
        if self.apply_all_strategies:
            assert self.num_strategies is None, (
                "num_strategies should be None when apply_all_strategies is True."
            )
        else:
            assert self.num_strategies is not None or self.num_strategies > 0, (
                "num_strategies should be a positive integer or not None when apply_all_strategies is False."
            )
        return self
    
    @model_validator(mode="after")
    def validate_key_counts(self):
        if self.apply_all_keys:
            assert self.num_keys is None, (
                "num_keys should be None when apply_all_keys is True."
            )
        else:
            assert self.num_keys is not None or self.num_keys > 0, (
                "num_keys should be a positive integer or not None when apply_all_keys is False."
            )
        return self