"""
    @author: Nicolas Flipo
    @date: 11.02.2021

    Contains the LinSys Class which corresponds to the Matrix linear system
        of equations
    Filling of RHS and LHS
    System solving

"""

import numpy as np
from codepyheat.hydrogeol import CODE_HYD


class LinSys():
    def __init__(self, ncells):
        self.lhs = np.zeros([ncells, ncells], dtype=float)
        self.rhs = np.zeros([ncells, 1], dtype=float)
        self.x = np.zeros([ncells, 1], dtype=float)

    def setLhsVal(self, i, j, val):
        if val != CODE_HYD:
            self.lhs[i][j] = val

    def setRhsVal(self, i, val):
        if val != CODE_HYD:
            self.rhs[i] = val

    def solveSysLin(self):
        self.x = np.linalg.solve(self.lhs, self.rhs)
