from typing import Sequence, Union
from random import random, choice
from operator import attrgetter
from numbers import Number
import sys

import numpy as np
from tqdm import trange
from scipy.interpolate import lagrange

from .params import Param, ParamsPriors, Prior
from .state import State
from .checker import checker
from .utils import C_W, RHO_W, LAMBDA_W, PARAM_LIST, compute_next_h, compute_next_temp


class Column:
    def __init__(
        self,
        river_bed: float,
        depth_sensors: Sequence[float],
        offset: float,
        dH_measures: list,
        T_measures: list,
        sigma_meas_P: float,
        sigma_meas_T: float,
    ):
        self.depth_sensors = depth_sensors
        self.offset = offset

        #! Pour l'instant on suppose que les temps matchent
        self._times = [t for t, _ in dH_measures]
        self._dH = np.array([d for _, (d, _) in dH_measures])
        self._T_riv = np.array([t for _, (_, t) in dH_measures])
        self._T_aq = np.array([t[-1]-1 for _, t in T_measures])
        self._T_measures = np.array([t[:-1] for _, t in T_measures])

        self._real_z = np.array([0] + depth_sensors) + offset
        self._real_z[0] -= offset
        self._states = None
        self._z_solve = None

    @classmethod
    def from_dict(cls, col_dict):
        return cls(**col_dict)

    @checker
    def compute_solve_transi(self, param: tuple, nb_cells: int, verbose = True):
        nb_cells += 2
        if not isinstance(param, Param):
            param = Param(*param)
        self._param = param
        
        if verbose:
            print(
                "--- Compute Solve Transi ---",
                self._param,
                sep = '\n'
            )
        dz = self._real_z[-1]/(nb_cells-1)
        self._z_solve = np.concatenate(
            [
                np.array([0]),
                np.linspace(dz/2, self._real_z[-1]-dz/2, nb_cells-2),
                np.array([self._real_z[-1]])
            ],
            axis = 0)
        dz = abs(self._z_solve[1] - self._z_solve[0])
        K = 10 ** -param.moinslog10K
        heigth = abs(self._real_z[-1] - self._real_z[0])
        Ss = param.n / heigth

        H_res = np.zeros((len(self._times), nb_cells), dtype=np.float32)
        temps = np.zeros((len(self._times), nb_cells), dtype=np.float32)

        H_res[0] = np.linspace(self._dH[0], 0, nb_cells)
        #temps[0] = np.linspace(self._T_riv[0], self._T_aq[0], nb_cells)
        lagr = lagrange(self._real_z, [self._T_riv[0], *self._T_measures[0], self._T_aq[0]])
        temps[0] = lagr(self._z_solve)

        for k in range(1, len(self._times)):
            dt = (self._times[k] - self._times[k - 1]).total_seconds()
            H_res[k] = compute_next_h(
                K, Ss, dt, dz, H_res[k - 1], self._dH[k], 0
            )
            temps[k] = compute_next_temp(
                *param[:],
                dt,
                dz,
                temps[k - 1],
                H_res[k],
                H_res[k - 1],
                self._T_riv[k],
                self._T_aq[k]
            )

        self._z_solve = self._z_solve[1:-1]
        self._temps = temps[:,1:-1]
        self._H_res = H_res[:,1:-1]
        self._flows = - K * (H_res[:, 1] - H_res[:, 0]) / dz
        
        if verbose:
            print("Done.")

    @compute_solve_transi.needed
    def get_depths_solve(self):
        return self._z_solve

    depths_solve = property(get_depths_solve)

    def get_times_solve(self):
        return self._times

    times_solve = property(get_times_solve)

    @compute_solve_transi.needed
    def get_temps_solve(self, z=None):
        if z is None:
            return self._temps
        z_ind = np.argmin(np.abs(self.depths_solve - z))
        return self._temps[:, z_ind]

    temps_solve = property(get_temps_solve)

    @compute_solve_transi.needed
    def get_advec_flows_solve(self):
        dz = abs(self._z_solve[1] - self._z_solve[0])
        return -RHO_W * C_W * 10**-self._param.moinslog10K * np.gradient(self._H_res, dz, axis = -1) * (self.temps_solve - (273.15 if self.temps_solve[0,0] > 200 else 0))

    advec_flows_solve = property(get_advec_flows_solve)

    @compute_solve_transi.needed
    def get_conduc_flows_solve(self):
        lambda_m = (
            self._param.n * (LAMBDA_W) ** 0.5
            + (1.0 - self._param.n) * (self._param.lambda_s) ** 0.5
        ) ** 2
        dz = abs(self._z_solve[1] - self._z_solve[0])
        return lambda_m * np.gradient(self.temps_solve, dz, axis=-1)

    conduc_flows_solve = property(get_conduc_flows_solve)

    @compute_solve_transi.needed
    def get_flows_solve(self, z=None):
        if z is None:
            return self._flows
        z_ind = np.argmin(np.abs(self.depths_solve - z))
        return self._flows[:, z_ind]

    flows_solve = property(get_flows_solve)

    def solve_anal(self, param: tuple, P: Union[float, Sequence]):
        raise NotImplementedError

    @checker
    def compute_mcmc(
        self,
        nb_iter: int,
        priors: dict,
        nb_cells: int,
        quantile: Union[float, Sequence[float]] = (0.05, 0.5, 0.95),
        verbose = True
    ):
        if isinstance(quantile, Number):
            quantile = [quantile]
        
        priors = ParamsPriors(
            [Prior((a, b), c) for (a, b), c in (priors[lbl] for lbl in PARAM_LIST)]
        )

        ind_ref = [
            np.argmin(
                np.abs(z - np.linspace(self._real_z[0], self._real_z[-1], nb_cells))
            )
            for z in self._real_z[1:-1]
        ]

        temp_ref = self._T_measures[:, :]

        def compute_energy(temp: np.array, sigma_obs: float = 1):
            # norm = sum(np.linalg.norm(x-y) for x,y in zip(temp,temp_ref))
            norm = np.sum(np.linalg.norm(temp - temp_ref, axis=-1))
            return 0.5 * (norm / sigma_obs) ** 2

        def compute_acceptance(actual_energy: float, prev_energy: float):
            return min(1, np.exp((prev_energy - actual_energy) / len(self._times) ** 1))

        if verbose:
            print(
                "--- Compute Mcmc ---",
                "Priors :",
                *(f"    {prior}" for prior in priors),
                f"Number of cells : {nb_cells}",
                f"Number of iterations : {nb_iter}",
                "Launch Mcmc",
                sep = '\n'
            )

        self._states = list()

        nb_z = np.linspace(self._real_z[0], self._real_z[-1], nb_cells).size
        _temps = np.zeros((nb_iter + 1, len(self._times), nb_z), np.float32)
        _flows = np.zeros((nb_iter + 1, len(self._times)), np.float32)

        for _ in trange(1000, desc="Init Mcmc ", file = sys.stdout):
            init_param = priors.sample_params()
            self.compute_solve_transi(init_param, nb_cells, verbose = False)

            self._states.append(
                State(
                    params=init_param,
                    energy=compute_energy(self.temps_solve[:, ind_ref]),
                    ratio_accept=1,
                )
            )

        self._states = [min(self._states, key=attrgetter("energy"))]

        _temps[0] = self.temps_solve
        _flows[0] = self.flows_solve

        for _ in trange(nb_iter, desc="Mcmc Computation ", file=sys.stdout):
            params = priors.perturb(self._states[-1].params)
            self.compute_solve_transi(params, nb_cells, verbose = False)
            energy = compute_energy(self.temps_solve[:, ind_ref])
            ratio_accept = compute_acceptance(energy, self._states[-1].energy)
            if random() < ratio_accept:
                self._states.append(
                    State(
                        params=params,
                        energy=energy,
                        ratio_accept=ratio_accept,
                    )
                )
                _temps[_] = self.temps_solve
                _flows[_] = self.flows_solve
            else:
                self._states.append(self._states[-1])
                self._states[-1].ratio_accept = ratio_accept
                _temps[_] = _temps[_ - 1]
                _flows[_] = _flows[_ - 1]
        self.compute_solve_transi.reset(self)

        if verbose:
            print("Mcmc Done.\n Start quantiles computation")
        
        self._quantiles_temps = {
            quant: res
            for quant, res in zip(quantile, np.quantile(_temps, quantile, axis=0))
        }
        self._quantiles_flows = {
            quant: res
            for quant, res in zip(quantile, np.quantile(_flows, quantile, axis=0))
        }
        if verbose:
            print("Quantiles Done.")

    @compute_mcmc.needed
    def get_depths_mcmc(self):
        return self._times

    depths_mcmc = property(get_depths_mcmc)

    @compute_mcmc.needed
    def get_times_mcmc(self):
        return self._times

    times_mcmc = property(get_times_mcmc)

    @compute_mcmc.needed
    def sample_param(self):
        return choice([s.params for s in self._states])

    @compute_mcmc.needed
    def get_best_param(self):
        """return the params that minimize the energy"""
        return min(self._states, key=attrgetter("energy")).params

    @compute_mcmc.needed
    def get_all_params(self):
        return [s.params for s in self._states]

    all_params = property(get_all_params)

    @compute_mcmc.needed
    def get_all_moinslog10K(self):
        return [s.params.moinslog10K for s in self._states]

    all_moinslog10K = property(get_all_moinslog10K)

    @compute_mcmc.needed
    def get_all_n(self):
        return [s.params.n for s in self._states]

    all_n = property(get_all_n)

    @compute_mcmc.needed
    def get_all_lambda_s(self):
        return [s.params.lambda_s for s in self._states]

    all_lambda_s = property(get_all_lambda_s)

    @compute_mcmc.needed
    def get_all_rhos_cs(self):
        return [s.params.rhos_cs for s in self._states]

    all_rhos_cs = property(get_all_rhos_cs)

    @compute_mcmc.needed
    def get_all_energy(self):
        return [s.energy for s in self._states]

    all_energy = property(get_all_energy)

    @compute_mcmc.needed
    def get_all_acceptance_ratio(self):
        return [s.ratio_accept for s in self._states]

    all_acceptance_ratio = property(get_all_acceptance_ratio)

    @compute_mcmc.needed
    def get_temps_quantile(self, quantile):
        return self._quantiles_temps[quantile]

    @compute_mcmc.needed
    def get_flows_quantile(self, quantile):
        return self._quantiles_flows[quantile]
