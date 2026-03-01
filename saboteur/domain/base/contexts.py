from abc import ABC
from typing import TypeVar


class BaseContext(ABC): ...


T_Context = TypeVar("T_Context", bound=BaseContext)
