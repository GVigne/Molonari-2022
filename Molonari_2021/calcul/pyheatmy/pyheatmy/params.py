from collections import namedtuple
from dataclasses import dataclass
from random import uniform, gauss

from .utils import PARAM_LIST

Param = namedtuple("Parametres", PARAM_LIST)

@dataclass
class Prior:
    range: tuple
    sigma: float

    def perturb(self, val):
        new_val = val + gauss(0, self.sigma)
        while new_val > self.range[1]:
            new_val -= self.range[1]-self.range[0]
        while new_val < self.range[0]:
            new_val += self.range[1]-self.range[0]
        return new_val

class ParamsPriors:
    def __init__(self, priors):
        self.priors = priors

    def sample_params(self):
        return Param(*(
            uniform(*prior.range)
            for prior in self.priors
        ))

    def perturb(self, param):
        return Param(*(
            prior.perturb(val)
            for prior, val in zip(self.priors, param)
        ))
        
    def __iter__(self):
        return self.priors.__iter__()