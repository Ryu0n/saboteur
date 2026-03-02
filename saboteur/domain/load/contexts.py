from dataclasses import dataclass

from saboteur.domain.base.contexts import BaseContext


@dataclass(frozen=True)
class LoadContext(BaseContext):
    """Context for HTTP request load testing.

    Args:
        BaseContext (_type_): _description_
    """

    url: str
    method: str
    headers: dict
    body: dict
    response: dict = None
