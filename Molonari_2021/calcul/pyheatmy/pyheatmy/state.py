from dataclasses import dataclass

from .params import Param

@dataclass
class State:
    params: Param
    energy: float
    ratio_accept: float
