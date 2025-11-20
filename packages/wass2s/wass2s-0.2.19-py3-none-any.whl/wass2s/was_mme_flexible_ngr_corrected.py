# -*- coding: utf-8 -*-
from __future__ import annotations

import numpy as np
import xarray as xr

from typing import Optional, Tuple

from scipy.optimize import minimize
from scipy.stats import (
    norm,
    logistic as st_logistic,
    genextreme,
    gamma as st_gamma,
    weibull_min,
    laplace as st_laplace,
    pareto as st_pareto,
)

from dask.distributed import Client


# -----------------------------------------------------------------------------
# Flexible Nonhomogeneous Regression (NGR) supporting multiple distributions
# -----------------------------------------------------------------------------
class FlexibleNGR:
    """
    Flexible Nonhomogeneous Regression (NGR) supporting multiple predictive families.

    Families supported (case-insensitive; 'gaussian' == 'normal'):
      - 'gaussian'/'normal':  y ~ N(μ, σ²) with μ = a + b x̄,  σ² = γ² + δ² s²
      - 'lognormal'        :  ln y ~ N(μ, σ²) with μ,σ linked to x̄, s² as above
      - 'logistic'         :  y ~ Logistic(loc=μ, scale=σ) with μ = a + b x̄,  σ = exp(c + d s)
      - 'gev'              :  y ~ GEV(ξ, loc=μ, scale=σ), μ = a + b x̄, σ = exp(c + d x̄)
      - 'gamma'            :  y ~ Gamma(shape=k, scale=θ) with mean m=exp(μ), var v = exp(γ) + exp(δ) s²,
                               k = m² / v, θ = v / m
      - 'weibull'          :  y ~ Weibull(k, λ) with λ = exp(a + b x̄), k = exp(c + d log(s+ε))
      - 'laplace'          :  y ~ Laplace(loc=μ, scale=σ) with μ = a + b x̄, σ = exp(c + d s)
      - 'pareto'           :  y ~ Pareto(b, scale) with scale = exp(a + b x̄), b = 1 + exp(c + d log(s+ε))

    where x̄ and s² are ensemble mean and variance; s = sqrt(s²).
    """

    def __init__(self, distribution: str = "gaussian", min_sigma: float = 1e-4):
        self.distribution = distribution.lower()
        if self.distribution == "normal":
            self.distribution = "gaussian"
        supported = [
            "gaussian",
            "lognormal",
            "logistic",
            "gev",
            "gamma",
            "weibull",
            "laplace",
            "pareto",
        ]
        if self.distribution not in supported:
            raise ValueError(f"Supported distributions are: {', '.join(supported)}")
        self.params: Optional[np.ndarray] = None
        self.min_sigma = float(min_sigma)

    # --------------------------- helpers ---------------------------
    def _ensemble_stats(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        X = np.asarray(X, dtype=float)
        if X.ndim != 2:
            raise ValueError("X must be 2D (n_samples, n_members)")
        n, m = X.shape
        xbar = np.mean(X, axis=1)
        if m > 1:
            s2 = np.var(X, axis=1, ddof=1)
        else:
            s2 = np.zeros(n, dtype=float)
        s = np.sqrt(np.maximum(s2, 0.0))
        return xbar, s2, s

    # ----------------------- log-likelihoods -----------------------
    def _ll_gaussian(self, p, xbar, s2, y):
        a, b, gamma, delta = p
        mu = a + b * xbar
        sig2 = (gamma ** 2) + (delta ** 2) * s2
        sig = np.sqrt(np.maximum(sig2, self.min_sigma ** 2))
        z = (y - mu) / sig
        return -np.sum(-0.5 * (z**2 + 2 * np.log(sig) + np.log(2 * np.pi)))

    def _ll_lognormal(self, p, xbar, s2, y):
        if np.any(y <= 0):
            return np.inf
        ln_y = np.log(y)
        return self._ll_gaussian(p, xbar, s2, ln_y)

    def _ll_logistic(self, p, xbar, s, y):
        a, b, c, d = p
        mu = a + b * xbar
        sig = np.exp(c + d * s)
        z = (y - mu) / sig
        # logistic pdf: exp(-z) / (sig * (1+exp(-z))^2)
        return -np.sum(-z - np.log(sig) - 2.0 * np.log1p(np.exp(-z)))

    def _ll_gev(self, p, xbar, y):
        a, b, c, d, xi = p
        mu = a + b * xbar
        sig = np.exp(c + d * xbar)
        # Support check using z = 1 + xi*(y-mu)/sig
        z = 1.0 + xi * (y - mu) / sig
        if np.any(sig <= 0) or np.any(z <= 0):
            return np.inf
        if abs(xi) > 1e-8:
            ll = -np.log(sig) + (-1.0 / xi - 1.0) * np.log(z) - z ** (-1.0 / xi)
        else:  # Gumbel limit
            u = (y - mu) / sig
            ll = -np.log(sig) - u - np.exp(-u)
        return -np.sum(ll)

    def _ll_gamma(self, p, xbar, s2, y):
        # mean m = exp(a + b xbar) > 0 ; variance v = exp(gamma_raw) + exp(delta_raw) * s2
        a, b, gamma_raw, delta_raw = p
        m = np.exp(a + b * xbar)
        v = np.exp(gamma_raw) + np.exp(delta_raw) * s2
        k = np.maximum(m**2 / np.maximum(v, 1e-12), 1e-6)  # shape
        theta = np.maximum(v / np.maximum(m, 1e-12), 1e-12)  # scale
        if np.any(y < 0) or np.any(theta <= 0) or np.any(k <= 0):
            return np.inf
        return -np.sum(st_gamma.logpdf(y, a=k, scale=theta))

    def _ll_weibull(self, p, xbar, s, y):
        a, b, c, d = p
        lam = np.exp(a + b * xbar)  # scale
        k = np.exp(c + d * np.log(s + 1e-8))  # shape
        if np.any(lam <= 0) or np.any(k <= 0) or np.any(y < 0):
            return np.inf
        return -np.sum(weibull_min.logpdf(y, c=k, scale=lam))

    def _ll_laplace(self, p, xbar, s, y):
        a, b, c, d = p
        loc = a + b * xbar
        scale = np.exp(c + d * s)
        if np.any(scale <= 0):
            return np.inf
        return -np.sum(st_laplace.logpdf(y, loc=loc, scale=scale))

    def _ll_pareto(self, p, xbar, s, y):
        a, b, c, d = p
        scale = np.exp(a + b * xbar)
        shape = 1.0 + np.exp(c + d * np.log(s + 1e-8))
        if np.any(scale <= 0) or np.any(shape <= 1.0) or np.any(y < scale):
            return np.inf
        return -np.sum(st_pareto.logpdf(y, b=shape, scale=scale))

    # ----------------------------- fit -----------------------------
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        if X_train.shape[0] != y_train.shape[0]:
            raise ValueError("Number of samples in X_train and y_train must match")
        xbar, s2, s = self._ensemble_stats(X_train)
        y = np.asarray(y_train, dtype=float)

        fam = self.distribution
        if fam == 'gaussian':
            init = np.array([0.0, 1.0, 1.0, 1.0])
            obj = lambda p: self._ll_gaussian(p, xbar, s2, y)
            bounds = None
        elif fam == 'lognormal':
            init = np.array([0.0, 1.0, 1.0, 1.0])
            obj = lambda p: self._ll_lognormal(p, xbar, s2, y)
            bounds = None
        elif fam == 'logistic':
            init = np.array([0.0, 1.0, 0.0, 0.0])
            obj = lambda p: self._ll_logistic(p, xbar, s, y)
            bounds = None
        elif fam == 'gev':
            init = np.array([0.0, 1.0, 0.0, 0.0, 0.1])
            # Bound xi to a reasonable range to stabilize tail behavior
            bounds = [(-np.inf, np.inf)] * 4 + [(-0.5, 0.5)]
            res = minimize(self._ll_gev, init, args=(xbar, y), method='L-BFGS-B', bounds=bounds)
            if not res.success:
                print(f"Warning: GEV optimization did not converge: {res.message}")
            self.params = res.x
            return
        elif fam == 'gamma':
            init = np.array([0.0, 0.0, np.log(1.0), np.log(0.5)])
            obj = lambda p: self._ll_gamma(p, xbar, s2, y)
            bounds = None
        elif fam == 'weibull':
            init = np.array([0.0, 0.0, 0.0, 0.0])
            obj = lambda p: self._ll_weibull(p, xbar, s, y)
            bounds = None
        elif fam == 'laplace':
            init = np.array([0.0, 1.0, 0.0, 0.0])
            obj = lambda p: self._ll_laplace(p, xbar, s, y)
            bounds = None
        elif fam == 'pareto':
            init = np.array([0.0, 0.0, 0.0, 0.0])
            obj = lambda p: self._ll_pareto(p, xbar, s, y)
            bounds = None
        else:
            raise ValueError("Unsupported distribution")

        res = minimize(obj, init, method='L-BFGS-B', bounds=bounds)
        if not res.success:
            print(f"Warning: {fam} optimization did not converge: {res.message}")
        self.params = res.x

    # -------------------------- parameter maps --------------------------
    def _params_gaussian(self, xbar, s2):
        a, b, gamma, delta = self.params
        mu = a + b * xbar
        sig = np.sqrt(np.maximum(gamma**2 + delta**2 * s2, self.min_sigma ** 2))
        return mu, sig

    def _params_lognormal(self, xbar, s2):
        a, b, gamma, delta = self.params
        mu = a + b * xbar
        sig = np.sqrt(np.maximum(gamma**2 + delta**2 * s2, self.min_sigma ** 2))
        return mu, sig  # parameters of ln Y

    def _params_logistic(self, xbar, s):
        a, b, c, d = self.params
        mu = a + b * xbar
        sig = np.exp(c + d * s)
        return mu, sig

    def _params_gev(self, xbar):
        a, b, c, d, xi = self.params
        mu = a + b * xbar
        sig = np.exp(c + d * xbar)
        return mu, sig, xi

    def _params_gamma(self, xbar, s2):
        a, b, gamma_raw, delta_raw = self.params
        m = np.exp(a + b * xbar)
        v = np.exp(gamma_raw) + np.exp(delta_raw) * s2
        k = np.maximum(m**2 / np.maximum(v, 1e-12), 1e-6)
        theta = np.maximum(v / np.maximum(m, 1e-12), 1e-12)
        return k, theta

    def _params_weibull(self, xbar, s):
        a, b, c, d = self.params
        lam = np.exp(a + b * xbar)
        k = np.exp(c + d * np.log(s + 1e-8))
        return lam, k

    def _params_laplace(self, xbar, s):
        a, b, c, d = self.params
        loc = a + b * xbar
        scale = np.exp(c + d * s)
        return loc, scale

    def _params_pareto(self, xbar, s):
        a, b, c, d = self.params
        scale = np.exp(a + b * xbar)
        shape = 1.0 + np.exp(c + d * np.log(s + 1e-8))
        return scale, shape

    # ------------------------------ predict ------------------------------
    def predict(self, X_test: np.ndarray):
        if self.params is None:
            raise ValueError("Model must be fitted before prediction")
        xbar, s2, s = self._ensemble_stats(X_test)
        fam = self.distribution
        if fam == 'gaussian':
            return self._params_gaussian(xbar, s2)
        if fam == 'lognormal':
            return self._params_lognormal(xbar, s2)
        if fam == 'logistic':
            return self._params_logistic(xbar, s)
        if fam == 'gev':
            return self._params_gev(xbar)
        if fam == 'gamma':
            return self._params_gamma(xbar, s2)
        if fam == 'weibull':
            return self._params_weibull(xbar, s)
        if fam == 'laplace':
            return self._params_laplace(xbar, s)
        if fam == 'pareto':
            return self._params_pareto(xbar, s)
        raise ValueError("Unsupported distribution")

    # ------------------------- predictive CDFs -------------------------
    def prob_less_than(self, X_test: np.ndarray, q: float | np.ndarray) -> np.ndarray:
        fam = self.distribution
        if fam == 'gaussian':
            mu, sig = self.predict(X_test)
            return norm.cdf(q, loc=mu, scale=sig)
        if fam == 'lognormal':
            mu, sig = self.predict(X_test)
            q = np.asarray(q)
            out = np.zeros_like(mu, dtype=float)
            mask = q > 0
            out[mask] = norm.cdf(np.log(q[mask] if q.ndim else np.log(q)), loc=mu[mask], scale=sig[mask]) if q.ndim else norm.cdf(np.log(q), loc=mu, scale=sig)
            return out
        if fam == 'logistic':
            mu, sig = self.predict(X_test)
            return st_logistic.cdf(q, loc=mu, scale=sig)
        if fam == 'gev':
            mu, sig, xi = self.predict(X_test)
            return genextreme.cdf(q, c=-xi, loc=mu, scale=sig)
        if fam == 'gamma':
            k, theta = self.predict(X_test)
            return st_gamma.cdf(q, a=k, scale=theta)
        if fam == 'weibull':
            lam, k = self.predict(X_test)
            return weibull_min.cdf(q, c=k, scale=lam)
        if fam == 'laplace':
            loc, scale = self.predict(X_test)
            return st_laplace.cdf(q, loc=loc, scale=scale)
        if fam == 'pareto':
            scale, shape = self.predict(X_test)
            return st_pareto.cdf(q, b=shape, scale=scale)
        raise ValueError("Unsupported distribution")


# -----------------------------------------------------------------------------
# Gridded wrapper with xarray/dask
# -----------------------------------------------------------------------------
class WAS_mme_FlexibleNGR_Model:
    """
    Gridwise Flexible NGR: fits per grid cell and outputs tercile probabilities.
    """

    def __init__(self, distribution: str = 'gaussian', nb_cores: int = 1):
        self.distribution = distribution
        self.nb_cores = int(nb_cores)

    # scalar used by apply_ufunc
    def _fit_predict(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray, t33: float, t67: float) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)
        nF = X_test.shape[0]

        if not (np.isfinite(t33) and np.isfinite(t67)):
            return np.full((3, nF), np.nan, dtype=float)

        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((3, nF), np.nan, dtype=float)

        Xc, yc = X[ok, :], y[ok]
        model = FlexibleNGR(self.distribution)
        try:
            model.fit(Xc, yc)
        except Exception:
            return np.full((3, nF), np.nan, dtype=float)

        pb = model.prob_less_than(X_test, t33)
        pt67 = model.prob_less_than(X_test, t67)
        pn = pt67 - pb
        pa = 1.0 - pt67
        out = np.vstack([pb, pn, pa]).astype(float)
        out = np.clip(out, 0.0, 1.0)
        s = out.sum(axis=0)
        good = s > 0
        out[:, good] /= s[good]
        return out

    def compute_model(
        self,
        X_train: xr.DataArray,
        y_train: xr.DataArray,
        X_test: xr.DataArray,
        Predictant: Optional[xr.DataArray] = None,
        clim_year_start: Optional[int] = None,
        clim_year_end: Optional[int] = None,
    ) -> xr.DataArray:
        # choose terciles
        if Predictant is not None and clim_year_start is not None and clim_year_end is not None:
            i0 = Predictant.get_index('T').get_loc(str(clim_year_start)).start
            i1 = Predictant.get_index('T').get_loc(str(clim_year_end)).stop
            series = Predictant.isel(T=slice(i0, i1))
        else:
            series = y_train
        terc = series.quantile([0.33, 0.67], dim='T')
        T1 = terc.isel(quantile=0).drop_vars('quantile')
        T2 = terc.isel(quantile=1).drop_vars('quantile')

        # chunking
        cx = int(np.maximum(1, np.round(len(y_train.get_index('X')) / self.nb_cores)))
        cy = int(np.maximum(1, np.round(len(y_train.get_index('Y')) / self.nb_cores)))

        # align dims
        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train['T']).transpose('T', 'M', 'Y', 'X')
        y_train = y_train.transpose('T', 'Y', 'X')

        if 'T' in X_test.dims:
            X_test = X_test.rename({'T': 'forecast'})
        X_test = X_test.transpose('forecast', 'M', 'Y', 'X')

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)
        result = xr.apply_ufunc(
            self._fit_predict,
            X_train.chunk({'Y': cy, 'X': cx}),
            y_train.chunk({'Y': cy, 'X': cx}),
            X_test.chunk({'Y': cy, 'X': cx}),
            T1.chunk({'Y': cy, 'X': cx}),
            T2.chunk({'Y': cy, 'X': cx}),
            input_core_dims=[('T', 'M'), ('T',), ('forecast', 'M'), (), ()],
            output_core_dims=[('probability', 'forecast')],
            vectorize=True,
            dask='parallelized',
            output_dtypes=[float],
            dask_gufunc_kwargs={'output_sizes': {'probability': 3}},
        )
        out = result.compute()
        client.close()
        return (
            out.rename({'forecast': 'T'})
               .assign_coords(probability=('probability', ['PB', 'PN', 'PA']))
               .transpose('probability', 'T', 'Y', 'X')
        )

    def forecast(
        self,
        Predictant: xr.DataArray,
        clim_year_start: int,
        clim_year_end: int,
        Predictor: xr.DataArray,
        Predictor_for_year: xr.DataArray,
    ) -> xr.DataArray:
        if 'M' in Predictant.coords:
            Predictant = Predictant.isel(M=0).drop_vars('M').squeeze()
        Predictant = Predictant.transpose('T', 'Y', 'X')

        # compute terciles from predictant climatology window
        i0 = Predictant.get_index('T').get_loc(str(clim_year_start)).start
        i1 = Predictant.get_index('T').get_loc(str(clim_year_end)).stop
        series = Predictant.isel(T=slice(i0, i1))
        terc = series.quantile([0.33, 0.67], dim='T')
        T1 = terc.isel(quantile=0).drop_vars('quantile')
        T2 = terc.isel(quantile=1).drop_vars('quantile')

        cx = int(np.maximum(1, np.round(len(Predictant.get_index('X')) / self.nb_cores)))
        cy = int(np.maximum(1, np.round(len(Predictant.get_index('Y')) / self.nb_cores)))

        Predictor = Predictor.assign_coords(T=Predictant['T']).transpose('T', 'M', 'Y', 'X')

        if 'T' in Predictor_for_year.dims:
            Xfy = Predictor_for_year.rename({'T': 'forecast'})
        else:
            Xfy = Predictor_for_year.transpose('forecast', 'M', 'Y', 'X')

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)
        result = xr.apply_ufunc(
            self._fit_predict,
            Predictor.chunk({'Y': cy, 'X': cx}),
            Predictant.chunk({'Y': cy, 'X': cx}),
            Xfy.chunk({'Y': cy, 'X': cx}),
            T1.chunk({'Y': cy, 'X': cx}),
            T2.chunk({'Y': cy, 'X': cx}),
            input_core_dims=[('T', 'M'), ('T',), ('forecast', 'M'), (), ()],
            output_core_dims=[('probability', 'forecast')],
            vectorize=True,
            dask='parallelized',
            output_dtypes=[float],
            dask_gufunc_kwargs={'output_sizes': {'probability': 3}},
        )
        out = result.compute()
        client.close()

        out = out.rename({'forecast': 'T'})
        # label probabilities and transpose
        return (
            out.assign_coords(probability=('probability', ['PB', 'PN', 'PA']))
               .transpose('probability', 'T', 'Y', 'X')
        )
