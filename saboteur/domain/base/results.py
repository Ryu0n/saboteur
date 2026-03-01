from typing import TypeVar
from pydantic import BaseModel, Field
from saboteur.utils.time import get_kst_now_isoformat


class BaseResult(BaseModel):
    """Base class for results returned by runners."""

    result: dict = Field(
        {}, description="The resulting data after applying the runner's logic."
    )
    created_at: str = Field(
        default_factory=get_kst_now_isoformat,
        description="The timestamp when the result was created.",
    )
    elapsed_time: float = Field(
        0.0, description="The time taken to produce the result in seconds."
    )


T_Result = TypeVar("T_Result", bound=BaseResult)
