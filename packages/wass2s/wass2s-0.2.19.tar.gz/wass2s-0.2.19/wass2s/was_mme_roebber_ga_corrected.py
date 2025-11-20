# -*- coding: utf-8 -*-
from __future__ import annotations

import operator
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import numpy as np
import xarray as xr

from scipy import stats
from scipy.stats import norm, t as st_t, weibull_min, gamma as st_gamma, lognorm as st_lognorm, laplace as st_laplace

# -----------------------------
# Config / defaults (literature-inspired)
# -----------------------------
DEFAULT_NUM_GENES = 8
DEFAULT_TOURNAMENT_SIZE = 3


# ==============================================================
# Gene (Roebber-style) — expression block with conditional gate
# ==============================================================
class Gene:
    """A single gene from Roebber-style GA equations.

    Each gene computes:  ( (c1*v1) O1 (c2*v2) ) O2 (c3*v3 )
    but only contributes if the relational gate on (v4, v5) is true.
    
    Values v1..v5 are **names** of predictors; actual values are supplied at evaluation time.
    All inputs are expected to be **normalized to [-1,1]**.
    """

    OPERATORS = {
        'ADD': operator.add,
        'MULTIPLY': operator.mul,
    }
    RELATIONAL_OPERATORS = {
        '<=': operator.le,
        '>': operator.gt,
    }

    def __init__(self, predictor_names: List[str]):
        if not predictor_names:
            raise ValueError("predictor_names must be a non-empty list")
        self.predictor_names = list(predictor_names)

        # choose random inputs
        self.v1_name = random.choice(self.predictor_names)
        self.v2_name = random.choice(self.predictor_names)
        self.v3_name = random.choice(self.predictor_names)
        self.v4_name = random.choice(self.predictor_names)
        self.v5_name = random.choice(self.predictor_names)

        # coefficients in [-1,1]
        self.c1 = random.uniform(-1, 1)
        self.c2 = random.uniform(-1, 1)
        self.c3 = random.uniform(-1, 1)

        # operators
        self.O1 = random.choice(tuple(self.OPERATORS.keys()))
        self.O2 = random.choice(tuple(self.OPERATORS.keys()))
        self.OR = random.choice(tuple(self.RELATIONAL_OPERATORS.keys()))  # relation between v4 and v5

    def evaluate(self, data_row: Dict[str, float]) -> float:
        """Return this gene's contribution for one sample (Eq. analogue of Roebber).

        data_row maps predictor name -> normalized value in [-1,1].
        If any predictor is missing, returns 0 (gene silent).
        """
        try:
            v1 = float(data_row[self.v1_name])
            v2 = float(data_row[self.v2_name])
            v3 = float(data_row[self.v3_name])
            v4 = float(data_row[self.v4_name])
            v5 = float(data_row[self.v5_name])
        except KeyError:
            return 0.0

        # relational gate
        gate = self.RELATIONAL_OPERATORS[self.OR](v4, v5)
        if not gate:
            return 0.0

        # core expression
        term1 = self.c1 * v1
        term2 = self.c2 * v2
        term3 = self.c3 * v3
        res = self.OPERATORS[self.O1](term1, term2)
        res = self.OPERATORS[self.O2](res, term3)
        return float(res)

    def mutate(self) -> None:
        """Mutate one randomly chosen element of the gene."""
        choices = ['v1_name', 'v2_name', 'v3_name', 'v4_name', 'v5_name', 'c1', 'c2', 'c3', 'O1', 'O2', 'OR']
        field = random.choice(choices)
        if field.startswith('v') and field.endswith('_name'):
            setattr(self, field, random.choice(self.predictor_names))
        elif field in {'c1','c2','c3'}:
            setattr(self, field, random.uniform(-1, 1))
        elif field in {'O1','O2'}:
            setattr(self, field, random.choice(tuple(self.OPERATORS.keys())))
        elif field == 'OR':
            setattr(self, field, random.choice(tuple(self.RELATIONAL_OPERATORS.keys())))

    def copy(self) -> 'Gene':
        g = Gene(self.predictor_names)
        g.v1_name = self.v1_name
        g.v2_name = self.v2_name
        g.v3_name = self.v3_name
        g.v4_name = self.v4_name
        g.v5_name = self.v5_name
        g.c1 = self.c1
        g.c2 = self.c2
        g.c3 = self.c3
        g.O1 = self.O1
        g.O2 = self.O2
        g.OR = self.OR
        return g


# ==================================
# Individual — a sum of NUM_GENES
# ==================================
class Individual:
    """One predictive equation = sum of gene outputs."""

    def __init__(self, predictor_names: List[str], num_genes: int = DEFAULT_NUM_GENES):
        self.genes: List[Gene] = [Gene(predictor_names) for _ in range(int(num_genes))]
        self.mse: float = float('inf')
        self.predictor_names = list(predictor_names)

    def predict_row(self, row: Dict[str, float]) -> float:
        return sum(g.evaluate(row) for g in self.genes)

    def calculate_mse(self, rows: List[Dict[str, float]], y_norm: np.ndarray, clip_output: bool = True) -> None:
        n = len(rows)
        if n == 0:
            self.mse = float('inf')
            return
        preds = np.fromiter((self.predict_row(rows[i]) for i in range(n)), dtype=float, count=n)
        if clip_output:
            preds = np.clip(preds, -1.0, 1.0)  # keep in normalized domain
        err = y_norm - preds
        self.mse = float(np.mean(err * err))

    def reproduce(self, mutation_rate: float, crossover_rate: float) -> 'Individual':
        # clone
        child = Individual(self.predictor_names, num_genes=len(self.genes))
        child.genes = [g.copy() for g in self.genes]

        # mutation: mutate one random gene (with probability)
        if random.random() < mutation_rate:
            random.choice(child.genes).mutate()

        # crossover: swap one of the underlined groups between two distinct genes
        if random.random() < crossover_rate and len(child.genes) >= 2:
            i, j = random.sample(range(len(child.genes)), 2)
            g1, g2 = child.genes[i], child.genes[j]
            grp = random.choice(['g1','g2','g3','g4'])
            if grp == 'g1':  # (c1, v1, O1)
                g1.c1, g2.c1 = g2.c1, g1.c1
                g1.v1_name, g2.v1_name = g2.v1_name, g1.v1_name
                g1.O1, g2.O1 = g2.O1, g1.O1
            elif grp == 'g2':  # (c2, v2, O2)
                g1.c2, g2.c2 = g2.c2, g1.c2
                g1.v2_name, g2.v2_name = g2.v2_name, g1.v2_name
                g1.O2, g2.O2 = g2.O2, g1.O2
            elif grp == 'g3':  # (c3, v3)
                g1.c3, g2.c3 = g2.c3, g1.c3
                g1.v3_name, g2.v3_name = g2.v3_name, g1.v3_name
            else:  # 'g4'  (v4, OR, v5)
                g1.v4_name, g2.v4_name = g2.v4_name, g1.v4_name
                g1.OR, g2.OR = g2.OR, g1.OR
                g1.v5_name, g2.v5_name = g2.v5_name, g1.v5_name

        return child

    def copy(self) -> 'Individual':
        c = Individual(self.predictor_names, num_genes=len(self.genes))
        c.genes = [g.copy() for g in self.genes]
        c.mse = self.mse
        return c


# ==========================================================
# GA driver + probability converters for terciles
# ==========================================================
class WAS_mme_RoebberGA:
    """
    Genetic Algorithm (Roebber 2013/2015 style) for statistical learning on gridded data.

    - Each gridpoint is trained independently on normalized predictors/target in [-1,1].
    - Population evolves via tournament selection, crossover of grouped gene pieces, and mutation.
    - Final prediction uses mean of top-`elite_size` individuals to reduce variance.
    """

    def __init__(
        self,
        population_size: int = 50,
        max_iter: int = 100,
        crossover_rate: float = 0.7,
        mutation_rate: float = 0.05,
        random_state: int = 42,
        dist_method: str = "gamma",
        elite_size: int = 5,
        num_genes: int = DEFAULT_NUM_GENES,
        tournament_size: int = DEFAULT_TOURNAMENT_SIZE,
    ):
        self.population_size = int(population_size)
        self.max_iter = int(max_iter)
        self.crossover_rate = float(crossover_rate)
        self.mutation_rate = float(mutation_rate)
        self.random_state = int(random_state)
        self.dist_method = str(dist_method)
        self.elite_size = int(elite_size)
        self.num_genes = int(num_genes)
        self.tournament_size = int(tournament_size)

        random.seed(self.random_state)
        np.random.seed(self.random_state)

        self.best_ensemble: Optional[List[Individual]] = None
        self.best_individual: Optional[Individual] = None
        self.best_fitness: float = float('-inf')

        self._y_minmax: Optional[Tuple[float, float]] = None
        self._pred_norm_ranges: Dict[str, Tuple[float, float]] = {}

    # -------------- normalization helpers --------------
    @staticmethod
    def _norm(arr: np.ndarray) -> np.ndarray:
        a = np.asarray(arr, dtype=float)
        mn = np.nanmin(a)
        mx = np.nanmax(a)
        if not np.isfinite(mn) or not np.isfinite(mx) or mx == mn:
            return np.zeros_like(a, dtype=float)
        return 2.0 * (a - mn) / (mx - mn) - 1.0

    @staticmethod
    def _denorm(x: np.ndarray, mn: float, mx: float) -> np.ndarray:
        if mx == mn:
            return np.full_like(x, mn, dtype=float)
        return (np.asarray(x, dtype=float) + 1.0) * 0.5 * (mx - mn) + mn

    def _prep(self, X_da: xr.DataArray, y_da: xr.DataArray) -> Tuple[List[Dict[str, float]], np.ndarray, List[str]]:
        # unify dims to (T, M, Y, X)
        X = X_da
        if ('T' in X.dims) and ('M' in X.dims) and ('Y' in X.dims) and ('X' in X.dims):
            X = X.transpose('T','M','Y','X')
        elif ('T' in X.dims) and ('Y' in X.dims) and ('X' in X.dims) and ('M' in X.dims):
            X = X.transpose('T','M','Y','X')
        else:
            raise ValueError("X_da must have dims (T,M,Y,X) or (T,Y,X,M)")

        y = y_da.transpose('T','Y','X')

        if 'M' not in X.coords:
            raise ValueError("X_da must carry coordinate 'M' naming predictors")
        predictor_names = [str(v) for v in X['M'].values.tolist()]

        # stack samples (T,Y,X)
        X_raw = X.stack(sample=('T','Y','X')).transpose('sample','M').values
        y_raw = y.stack(sample=('T','Y','X')).values
        if y_raw.ndim == 2 and y_raw.shape[1] == 1:
            y_raw = y_raw.ravel()

        valid = np.all(np.isfinite(X_raw), axis=1) & np.isfinite(y_raw)
        X_raw = X_raw[valid]
        y_raw = y_raw[valid]
        if X_raw.size == 0:
            return [], np.array([]), predictor_names

        # normalize per predictor
        self._pred_norm_ranges = {}
        X_norm_cols = []
        for j, name in enumerate(predictor_names):
            col = X_raw[:, j]
            mn, mx = float(np.nanmin(col)), float(np.nanmax(col))
            self._pred_norm_ranges[name] = (mn, mx)
            if mx == mn:
                X_norm_cols.append(np.zeros_like(col))
            else:
                x = 2 * (col - mn) / (mx - mn) - 1
                X_norm_cols.append(np.clip(x, -1, 1))
        X_norm = np.column_stack(X_norm_cols)

        rows: List[Dict[str, float]] = []
        for i in range(X_norm.shape[0]):
            rows.append({predictor_names[j]: X_norm[i, j] for j in range(len(predictor_names))})

        # normalize y
        y_mn = float(np.nanmin(y_raw))
        y_mx = float(np.nanmax(y_raw))
        self._y_minmax = (y_mn, y_mx)
        y_norm = self._norm(y_raw)
        return rows, y_norm, predictor_names

    def _tournament(self, pop: List[Individual]) -> Individual:
        cand = random.sample(pop, k=min(self.tournament_size, len(pop)))
        return min(cand, key=lambda ind: ind.mse)

    def _train_core(self, rows: List[Dict[str, float]], y_norm: np.ndarray, predictor_names: List[str]) -> List[Individual]:
        # initialize population
        pop: List[Individual] = [Individual(predictor_names, num_genes=self.num_genes) for _ in range(self.population_size)]
        for ind in pop:
            ind.calculate_mse(rows, y_norm)
        pop.sort(key=lambda i: i.mse)
        self.best_individual = pop[0].copy()
        self.best_fitness = -self.best_individual.mse

        for _ in range(self.max_iter):
            # elitism
            pop.sort(key=lambda i: i.mse)
            if pop[0].mse < self.best_individual.mse:
                self.best_individual = pop[0].copy()
                self.best_fitness = -pop[0].mse

            new_pop: List[Individual] = [self.best_individual.copy()]
            while len(new_pop) < self.population_size:
                parent = self._tournament(pop)
                child = parent.reproduce(self.mutation_rate, self.crossover_rate)
                new_pop.append(child)

            # evaluate
            for ind in new_pop:
                ind.calculate_mse(rows, y_norm)
            pop = new_pop

            if self.best_individual.mse < 1e-3:
                break

        pop.sort(key=lambda i: i.mse)
        self.best_ensemble = [ind.copy() for ind in pop[: self.elite_size]]
        return self.best_ensemble

    # ---------------------- public API ----------------------
    def compute_model(self, X_train: xr.DataArray, y_train: xr.DataArray, X_test: xr.DataArray, y_test: Optional[xr.DataArray] = None) -> xr.DataArray:
        rows, y_norm, predictor_names = self._prep(X_train, y_train)
        if not rows:
            return xr.DataArray(np.full(X_test.transpose('T','Y','X').shape, np.nan), coords={'T': X_test['T'], 'Y': X_test['Y'], 'X': X_test['X']}, dims=['T','Y','X'])

        ensemble = self._train_core(rows, y_norm, predictor_names)
        if not ensemble:
            return xr.DataArray(np.full(X_test.transpose('T','Y','X').shape, np.nan), coords={'T': X_test['T'], 'Y': X_test['Y'], 'X': X_test['X']}, dims=['T','Y','X'])

        # Prepare X_test
        X = X_test
        if ('T' in X.dims) and ('M' in X.dims) and ('Y' in X.dims) and ('X' in X.dims):
            X = X.transpose('T','M','Y','X')
        elif ('T' in X.dims) and ('Y' in X.dims) and ('X' in X.dims) and ('M' in X.dims):
            X = X.transpose('T','M','Y','X')
        else:
            raise ValueError("X_test must have dims (T,M,Y,X) or (T,Y,X,M)")

        X_raw = X.stack(sample=('T','Y','X')).transpose('sample','M').values
        test_valid = np.all(np.isfinite(X_raw), axis=1)
        X_raw = X_raw[test_valid]

        # normalize using training min/max, clip to [-1,1]
        names = predictor_names
        cols = []
        for j, name in enumerate(names):
            mn, mx = self._pred_norm_ranges.get(name, (0.0, 0.0))
            col = X_raw[:, j]
            if mx == mn:
                cols.append(np.zeros_like(col))
            else:
                x = 2 * (col - mn) / (mx - mn) - 1
                cols.append(np.clip(x, -1, 1))
        Xn = np.column_stack(cols) if cols else np.zeros((0, len(names)))
        rows_test: List[Dict[str, float]] = [ {names[j]: Xn[i, j] for j in range(len(names))} for i in range(Xn.shape[0]) ]

        # predictions via mean of elite
        preds_norm = np.full(test_valid.shape[0], np.nan, dtype=float)
        if rows_test:
            vals = []
            for row in rows_test:
                ensemble_vals = [sum(g.evaluate(row) for g in ind.genes) for ind in ensemble]
                vals.append(float(np.mean(ensemble_vals)))
            preds_norm[test_valid] = np.clip(np.array(vals, dtype=float), -1.0, 1.0)

        # reshape back to (T,Y,X) and denormalize
        T_ = X_test['T']
        Y_ = X_test['Y']
        Xc = X_test['X']
        preds_norm_full = np.full(T_.size * Y_.size * Xc.size, np.nan, dtype=float)
        preds_norm_full[test_valid] = preds_norm[test_valid]
        preds_norm_full = preds_norm_full.reshape(T_.size, Y_.size, Xc.size)

        mn, mx = self._y_minmax if self._y_minmax is not None else (0.0, 0.0)
        preds_denorm = self._denorm(preds_norm_full, mn, mx)

        return xr.DataArray(preds_denorm, coords={'T': T_, 'Y': Y_, 'X': Xc}, dims=['T','Y','X'])

    # ------------------ Probability Calculations ------------------
    @staticmethod
    def tercile_probs_student_t(best_guess: np.ndarray, error_variance: np.ndarray, T1: np.ndarray, T2: np.ndarray, dof: int) -> np.ndarray:
        n = best_guess.shape[-1] if best_guess.ndim else len(np.atleast_1d(best_guess))
        out = np.empty((3, n), dtype=float)
        if np.any(~np.isfinite(best_guess)):
            out[:] = np.nan
            return out
        sigma = np.sqrt(np.maximum(error_variance, 1e-12))
        z1 = (T1 - best_guess) / sigma
        z2 = (T2 - best_guess) / sigma
        out[0, :] = st_t.cdf(z1, df=max(dof,1))
        out[1, :] = st_t.cdf(z2, df=max(dof,1)) - out[0, :]
        out[2, :] = 1.0 - st_t.cdf(z2, df=max(dof,1))
        return out

    @staticmethod
    def tercile_probs_normal(best_guess: np.ndarray, error_variance: np.ndarray, T1: np.ndarray, T2: np.ndarray) -> np.ndarray:
        n = best_guess.shape[-1] if best_guess.ndim else len(np.atleast_1d(best_guess))
        out = np.empty((3, n), dtype=float)
        sigma = np.sqrt(np.maximum(error_variance, 1e-12))
        F1 = norm.cdf(T1, loc=best_guess, scale=sigma)
        F2 = norm.cdf(T2, loc=best_guess, scale=sigma)
        out[0, :] = F1
        out[1, :] = F2 - F1
        out[2, :] = 1.0 - F2
        return out

    @staticmethod
    def tercile_probs_gamma(best_guess: np.ndarray, error_variance: np.ndarray, T1: np.ndarray, T2: np.ndarray) -> np.ndarray:
        n = best_guess.shape[-1] if best_guess.ndim else len(np.atleast_1d(best_guess))
        out = np.empty((3, n), dtype=float)
        mu = np.maximum(best_guess, 1e-8)
        var = np.maximum(error_variance, 1e-12)
        k = mu**2 / var
        theta = var / mu
        F1 = st_gamma.cdf(np.maximum(T1,0.0), a=k, scale=theta)
        F2 = st_gamma.cdf(np.maximum(T2,0.0), a=k, scale=theta)
        out[0, :] = F1
        out[1, :] = np.clip(F2 - F1, 0.0, 1.0)
        out[2, :] = 1.0 - F2
        return out

    @staticmethod
    def tercile_probs_lognormal(best_guess: np.ndarray, error_variance: np.ndarray, T1: np.ndarray, T2: np.ndarray) -> np.ndarray:
        n = best_guess.shape[-1] if best_guess.ndim else len(np.atleast_1d(best_guess))
        out = np.empty((3, n), dtype=float)
        mu = np.maximum(best_guess, 1e-8)
        var = np.maximum(error_variance, 1e-12)
        s = np.sqrt(np.log(1.0 + var / (mu * mu)))
        m = np.log(mu) - 0.5 * s * s
        F1 = st_lognorm.cdf(np.maximum(T1, 0.0), s=s, scale=np.exp(m))
        F2 = st_lognorm.cdf(np.maximum(T2, 0.0), s=s, scale=np.exp(m))
        out[0, :] = F1
        out[1, :] = np.clip(F2 - F1, 0.0, 1.0)
        out[2, :] = 1.0 - F2
        return out

    @staticmethod
    def tercile_probs_nonparam(best_guess: np.ndarray, error_samples: np.ndarray, T1: np.ndarray, T2: np.ndarray) -> np.ndarray:
        # error_samples: 1D historical error vector (per grid cell)
        n = best_guess.shape[-1] if best_guess.ndim else len(np.atleast_1d(best_guess))
        out = np.full((3, n), np.nan, dtype=float)
        e = np.asarray(error_samples, dtype=float)
        e = e[np.isfinite(e)]
        if e.size == 0:
            return out
        bg = np.asarray(best_guess, dtype=float)
        for i in range(n):
            dist = bg[i] + e
            p_below = np.mean(dist < T1)
            p_between = np.mean((dist >= T1) & (dist < T2))
            out[0, i] = p_below
            out[1, i] = p_between
            out[2, i] = 1.0 - (p_below + p_between)
        return out

    # ------------------ High-level tercile prob API ------------------
    def compute_prob(self, Predictant: xr.DataArray, clim_year_start: int, clim_year_end: int, hindcast_det: xr.DataArray) -> xr.DataArray:
        # ensure dims
        Y = Predictant.transpose('T','Y','X')
        H = hindcast_det.transpose('T','Y','X')

        # climatology terciles
        i0 = Y.get_index('T').get_loc(str(clim_year_start)).start
        i1 = Y.get_index('T').get_loc(str(clim_year_end)).stop
        clim = Y.isel(T=slice(i0, i1))
        terc = clim.quantile([0.33, 0.67], dim='T')
        T1 = terc.isel(quantile=0).drop_vars('quantile')
        T2 = terc.isel(quantile=1).drop_vars('quantile')

        err_var = (Y - H).var(dim='T')
        dof = max(int(Y.sizes['T']) - 2, 1)

        if self.dist_method == 't':
            func = self.tercile_probs_student_t
            out = xr.apply_ufunc(
                func,
                H,
                err_var,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'gamma':
            out = xr.apply_ufunc(
                self.tercile_probs_gamma,
                H,
                err_var,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'normal':
            out = xr.apply_ufunc(
                self.tercile_probs_normal,
                H,
                err_var,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'lognormal':
            out = xr.apply_ufunc(
                self.tercile_probs_lognormal,
                H,
                err_var,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'nonparam':
            E = (Y - H)
            out = xr.apply_ufunc(
                self.tercile_probs_nonparam,
                H,
                E,
                T1,
                T2,
                input_core_dims=[('T',), ('T',), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        else:
            raise ValueError(f"Unsupported dist_method: {self.dist_method}")

        return (
            out.assign_coords(probability=('probability', ['PB','PN','PA']))
               .transpose('probability','T','Y','X')
        )

    def forecast(self, Predictant: xr.DataArray, clim_year_start: int, clim_year_end: int, hindcast_det: xr.DataArray, hindcast_det_cross: xr.DataArray, Predictor_for_year: xr.DataArray) -> Tuple[xr.DataArray, xr.DataArray]:
        # deterministic forecast using GA model trained on hindcast_det (as predictors) vs Predictant
        pred_da = self.compute_model(hindcast_det, Predictant, Predictor_for_year)

        # place forecast month matching first month of Predictant, year from Predictor_for_year['T']
        if 'T' in Predictor_for_year.coords:
            year = int(Predictor_for_year['T'].values.astype('datetime64[Y]').astype(int)[0] + 1970)
        else:
            year = int(np.datetime64('1970').astype('datetime64[Y]').astype(int) + 1970)
        month_1 = int(Predictant['T'].values[0].astype('datetime64[M]').astype(int) % 12 + 1)
        new_T = np.datetime64(f"{year}-{month_1:02d}-01")
        pred_da = pred_da.assign_coords(T=xr.DataArray([new_T], dims=['T']))
        pred_da['T'] = pred_da['T'].astype('datetime64[ns]')

        # probabilities using hindcast-based error (cross)
        Y = Predictant.transpose('T','Y','X')
        Evar = (Y - hindcast_det_cross.transpose('T','Y','X')).var(dim='T')
        i0 = Y.get_index('T').get_loc(str(clim_year_start)).start
        i1 = Y.get_index('T').get_loc(str(clim_year_end)).stop
        clim = Y.isel(T=slice(i0, i1))
        terc = clim.quantile([0.33, 0.67], dim='T')
        T1 = terc.isel(quantile=0).drop_vars('quantile')
        T2 = terc.isel(quantile=1).drop_vars('quantile')
        dof = max(int(Y.sizes['T']) - 2, 1)

        if self.dist_method == 't':
            func = self.tercile_probs_student_t
            out = xr.apply_ufunc(
                func,
                pred_da,
                Evar,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'gamma':
            out = xr.apply_ufunc(
                self.tercile_probs_gamma,
                pred_da,
                Evar,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'normal':
            out = xr.apply_ufunc(
                self.tercile_probs_normal,
                pred_da,
                Evar,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'lognormal':
            out = xr.apply_ufunc(
                self.tercile_probs_lognormal,
                pred_da,
                Evar,
                T1,
                T2,
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        elif self.dist_method == 'nonparam':
            E = (Y - hindcast_det_cross.transpose('T','Y','X')).rename({'T':'S'})
            out = xr.apply_ufunc(
                self.tercile_probs_nonparam,
                pred_da,
                E,
                T1,
                T2,
                input_core_dims=[('T',), ('S',), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability','T')],
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True},
            )
        else:
            raise ValueError(f"Unsupported dist_method: {self.dist_method}")

        prob_da = out.assign_coords(probability=('probability', ['PB','PN','PA'])).transpose('probability','T','Y','X')
        return pred_da, prob_da
