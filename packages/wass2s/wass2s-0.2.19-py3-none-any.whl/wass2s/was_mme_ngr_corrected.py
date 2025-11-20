# -*- coding: utf-8 -*-
from __future__ import annotations

import numpy as np
import xarray as xr

from typing import Optional, Tuple

from scipy.optimize import minimize
from scipy.stats import norm

from dask.distributed import Client


# -----------------------------------------------------------------------------
# Nonhomogeneous Gaussian Regression (NGR)
# -----------------------------------------------------------------------------
class NGR:
    """
    Nonhomogeneous Gaussian Regression (NGR) for probabilistic post-processing.

    Supports both exchangeable and non-exchangeable members, with parameter
    estimation by negative log-likelihood (NLL) or CRPS minimization.

    Predictive distribution for observation y_t is Gaussian:
        y_t | X_t ~ N( mu_t, sigma_t^2 ),
    with
        mu_t = a + b * xbar_t                 (exchangeable)
             = a + sum_j b_j * x_{t,j}       (non-exchangeable),
        sigma_t^2 = c + d * s_t^2,            c>0, d>0,
    where xbar_t is the ensemble mean and s_t^2 is ensemble variance.

    We parameterize c = exp(gamma_raw), d = exp(delta_raw) to enforce positivity.
    """

    def __init__(
        self,
        exchangeable: bool = True,
        estimation_method: str = "log_likelihood",  # or "crps"
        l2_penalty: float = 0.0,                    # ridge penalty on mean coefficients b
        min_sigma: float = 1e-4,
    ):
        self.exchangeable = bool(exchangeable)
        self.estimation_method = estimation_method.lower()
        if self.estimation_method not in {"log_likelihood", "crps"}:
            raise ValueError("estimation_method must be 'log_likelihood' or 'crps'")
        self.l2_penalty = float(l2_penalty)
        self.min_sigma = float(min_sigma)

        self.params: Optional[np.ndarray] = None  # [a, b, gamma_raw, delta_raw] or [a, b1..bm, gamma_raw, delta_raw]
        self.m: Optional[int] = None

    # -------------------------- core computations --------------------------
    def _compute_mu_t(self, X: np.ndarray, params: np.ndarray) -> np.ndarray:
        if self.exchangeable:
            a, b = params[0], params[1]
            xbar = np.mean(X, axis=1)
            return a + b * xbar
        else:
            a = params[0]
            b = params[1:1 + self.m]
            return a + X @ b

    def _compute_sigma_t(self, X: np.ndarray, params: np.ndarray) -> np.ndarray:
        # ensemble variance with ddof handling
        if self.m is None:
            raise RuntimeError("Model not initialized with number of members.")
        if self.m > 1:
            st2 = np.var(X, axis=1, ddof=1)
        else:
            st2 = np.zeros(X.shape[0])

        gamma_raw, delta_raw = params[-2], params[-1]
        c = np.exp(gamma_raw)
        d = np.exp(delta_raw)
        sigma2 = c + d * st2
        sigma = np.sqrt(np.maximum(sigma2, self.min_sigma ** 2))
        return sigma

    # -------------------------- objectives --------------------------
    def _neg_loglik(self, params: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
        mu = self._compute_mu_t(X, params)
        sigma = self._compute_sigma_t(X, params)
        z = (y - mu) / sigma
        nll = 0.5 * np.sum(z**2 + 2.0 * np.log(sigma) + np.log(2.0 * np.pi))
        # ridge penalty on mean coefficients (exclude intercept and variance params)
        if self.exchangeable:
            b = params[1]
            pen = self.l2_penalty * (b ** 2)
        else:
            b = params[1:1 + self.m]
            pen = self.l2_penalty * float(np.sum(b ** 2))
        return nll + pen

    def _crps_objective(self, params: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
        # Closed-form CRPS for Gaussian
        mu = self._compute_mu_t(X, params)
        sigma = self._compute_sigma_t(X, params)
        z = (y - mu) / sigma
        crps = sigma * (z * (2.0 * norm.cdf(z) - 1.0) + 2.0 * norm.pdf(z) - 1.0 / np.sqrt(np.pi))
        mean_crps = float(np.mean(crps))
        # ridge penalty on mean coefficients
        if self.exchangeable:
            b = params[1]
            pen = self.l2_penalty * (b ** 2)
        else:
            b = params[1:1 + self.m]
            pen = self.l2_penalty * float(np.sum(b ** 2))
        return mean_crps + pen

    # -------------------------- fitting --------------------------
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        X = np.asarray(X_train, dtype=float)
        y = np.asarray(y_train, dtype=float)
        if X.ndim != 2 or y.ndim != 1:
            raise ValueError("X_train must be 2D (n_samples, m); y_train must be 1D (n_samples,)")
        if X.shape[0] != y.shape[0]:
            raise ValueError("Number of samples in X_train and y_train must match")

        n, m = X.shape
        self.m = m

        # Initial mean parameters via least squares
        if self.exchangeable:
            xbar = np.mean(X, axis=1)
            A = np.column_stack([np.ones(n), xbar])  # [1, xbar]
        else:
            A = np.column_stack([np.ones(n), X])     # [1, X]
        try:
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)  # intercept + slopes
        except np.linalg.LinAlgError:
            beta = np.zeros(A.shape[1])
        mu_hat = A @ beta

        # Initial variance parameters from regressing residual^2 on st2
        if m > 1:
            st2 = np.var(X, axis=1, ddof=1)
        else:
            st2 = np.zeros(n)
        resid2 = (y - mu_hat) ** 2
        B = np.column_stack([np.ones(n), st2])  # ~ c + d * st2
        try:
            theta, *_ = np.linalg.lstsq(B, resid2, rcond=None)
            c0 = max(theta[0], 1e-4)
            d0 = max(theta[1], 1e-4)
        except np.linalg.LinAlgError:
            c0, d0 = 1.0, 0.5

        gamma_raw0 = np.log(c0)  # since c = exp(gamma_raw)
        delta_raw0 = np.log(d0)  # since d = exp(delta_raw)

        if self.exchangeable:
            initial = np.array([beta[0], beta[1], gamma_raw0, delta_raw0], dtype=float)
        else:
            initial = np.concatenate([beta, [gamma_raw0, delta_raw0]]).astype(float)

        # Choose objective
        objective = self._neg_loglik if self.estimation_method == "log_likelihood" else self._crps_objective

        result = minimize(
            objective,
            initial,
            args=(X, y),
            method="L-BFGS-B",
            options={"maxiter": 1000, "ftol": 1e-9}
        )
        if not result.success:
            # Keep best effort but warn
            print("Warning: NGR optimization did not converge:", result.message)
        self.params = result.x

    # -------------------------- predictions --------------------------
    def predict(self, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.params is None:
            raise ValueError("Model must be fitted before prediction")
        X = np.asarray(X_test, dtype=float)
        if X.ndim != 2 or X.shape[1] != self.m:
            raise ValueError(f"X_test must be 2D with {self.m} members")
        mu = self._compute_mu_t(X, self.params)
        sigma = self._compute_sigma_t(X, self.params)
        return mu, sigma

    def prob_less_than(self, X_test: np.ndarray, q: float | np.ndarray) -> np.ndarray:
        mu, sigma = self.predict(X_test)
        return norm.cdf(q, loc=mu, scale=sigma)

    def predict_quantile(self, X_test: np.ndarray, qprob: float) -> np.ndarray:
        """Analytic Gaussian quantile: mu + sigma * Phi^{-1}(qprob)."""
        if not (0.0 < qprob < 1.0):
            raise ValueError("qprob must be in (0,1)")
        mu, sigma = self.predict(X_test)
        z = norm.ppf(qprob)
        return mu + sigma * z


# -----------------------------------------------------------------------------
# Dask/xarray wrapper for gridded NGR
# -----------------------------------------------------------------------------
class WAS_mme_NGR_Model:
    """
    NGR on gridded data with xarray/dask.

    Provides
      * compute_model   : Gaussian predictive mean (T, Y, X)
      * compute_prob    : Tercile probabilities (3, T, Y, X)
      * compute_quantile: Gaussian predictive quantile at qprob (T, Y, X)
      * forecast        : convenience wrapper returning (mean, probs)
    """

    def __init__(self, exchangeable: bool = True, estimation_method: str = 'log_likelihood', nb_cores: int = 1, l2_penalty: float = 0.0):
        self.exchangeable = exchangeable
        self.estimation_method = estimation_method
        self.nb_cores = int(nb_cores)
        self.l2_penalty = float(l2_penalty)

    # ---- scalar helpers used in apply_ufunc ----
    def _fit_predict_mean(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)
        n_forecast = X_test.shape[0]

        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((n_forecast,), np.nan, dtype=float)

        Xc, yc = X[ok, :], y[ok]
        model = NGR(self.exchangeable, self.estimation_method, l2_penalty=self.l2_penalty)
        model.fit(Xc, yc)
        mu, _ = model.predict(X_test)
        return np.asarray(mu, dtype=float).reshape(n_forecast)

    def _fit_predict_proba(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray, t33: float, t67: float) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)
        n_forecast = X_test.shape[0]

        if not np.isfinite(t33) or not np.isfinite(t67):
            return np.full((3, n_forecast), np.nan, dtype=float)

        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((3, n_forecast), np.nan, dtype=float)

        Xc, yc = X[ok, :], y[ok]
        model = NGR(self.exchangeable, self.estimation_method, l2_penalty=self.l2_penalty)
        model.fit(Xc, yc)
        p_b = model.prob_less_than(X_test, t33)
        p_t67 = model.prob_less_than(X_test, t67)
        p_n = p_t67 - p_b
        p_a = 1.0 - p_t67
        out = np.vstack([p_b, p_n, p_a]).astype(float)
        out = np.clip(out, 0.0, 1.0)
        s = out.sum(axis=0)
        good = s > 0
        out[:, good] /= s[good]
        return out

    def _fit_predict_quantile(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray, qprob: float) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)
        n_forecast = X_test.shape[0]

        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((n_forecast,), np.nan, dtype=float)

        Xc, yc = X[ok, :], y[ok]
        model = NGR(self.exchangeable, self.estimation_method, l2_penalty=self.l2_penalty)
        model.fit(Xc, yc)
        q = model.predict_quantile(X_test, float(qprob))
        return np.asarray(q, dtype=float).reshape(n_forecast)

    # ---- public grid methods ----
    def compute_model(self, X_train: xr.DataArray, y_train: xr.DataArray, X_test: xr.DataArray) -> xr.DataArray:
        # chunk sizes
        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index('X')) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index('Y')) / self.nb_cores)))

        # align training dims
        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train['T']).transpose('T', 'M', 'Y', 'X')
        y_train = y_train.transpose('T', 'Y', 'X')

        # normalize test dims
        if 'T' in X_test.dims:
            X_test = X_test.rename({'T': 'forecast'})
        X_test = X_test.transpose('forecast', 'M', 'Y', 'X')

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)
        result = xr.apply_ufunc(
            self._fit_predict_mean,
            X_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            y_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            X_test.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            input_core_dims=[('T', 'M'), ('T',), ('forecast', 'M')],
            output_core_dims=[('forecast',)],
            vectorize=True,
            dask='parallelized',
            output_dtypes=[float],
        )
        out = result.compute()
        client.close()
        return out.rename({'forecast': 'T'}).transpose('T', 'Y', 'X')

    def compute_prob(
        self,
        X_train: xr.DataArray,
        y_train: xr.DataArray,
        X_test: xr.DataArray,
        Predictant: Optional[xr.DataArray] = None,
        clim_year_start: Optional[int] = None,
        clim_year_end: Optional[int] = None,
    ) -> xr.DataArray:
        if clim_year_start is None or clim_year_end is None:
            raise ValueError("clim_year_start and clim_year_end must be provided")

        # choose series for terciles
        if Predictant is not None:
            idx_start = Predictant.get_index('T').get_loc(str(clim_year_start)).start
            idx_end = Predictant.get_index('T').get_loc(str(clim_year_end)).stop
            series = Predictant.isel(T=slice(idx_start, idx_end))
        else:
            idx_start = y_train.get_index('T').get_loc(str(clim_year_start)).start
            idx_end = y_train.get_index('T').get_loc(str(clim_year_end)).stop
            series = y_train.isel(T=slice(idx_start, idx_end))

        terciles = series.quantile([0.33, 0.67], dim='T')
        T1 = terciles.isel(quantile=0).drop_vars('quantile')
        T2 = terciles.isel(quantile=1).drop_vars('quantile')

        # chunk sizes
        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index('X')) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index('Y')) / self.nb_cores)))

        # align training dims
        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train['T']).transpose('T', 'M', 'Y', 'X')
        y_train = y_train.transpose('T', 'Y', 'X')

        # normalize test dims
        if 'T' in X_test.dims:
            X_test = X_test.rename({'T': 'forecast'})
        X_test = X_test.transpose('forecast', 'M', 'Y', 'X')

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)
        result = xr.apply_ufunc(
            self._fit_predict_proba,
            X_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            y_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            X_test.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            T1.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            T2.chunk({'Y': chunksize_y, 'X': chunksize_x}),
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

    def compute_quantile(self, X_train: xr.DataArray, y_train: xr.DataArray, X_test: xr.DataArray, qprob: float) -> xr.DataArray:
        if not (0.0 < qprob < 1.0):
            raise ValueError("qprob must be in (0,1)")

        # chunk sizes
        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index('X')) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index('Y')) / self.nb_cores)))

        # align training dims
        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train['T']).transpose('T', 'M', 'Y', 'X')
        y_train = y_train.transpose('T', 'Y', 'X')

        # normalize test dims
        if 'T' in X_test.dims:
            X_test = X_test.rename({'T': 'forecast'})
        X_test = X_test.transpose('forecast', 'M', 'Y', 'X')

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)
        result = xr.apply_ufunc(
            self._fit_predict_quantile,
            X_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            y_train.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            X_test.chunk({'Y': chunksize_y, 'X': chunksize_x}),
            input_core_dims=[('T', 'M'), ('T',), ('forecast', 'M')],
            kwargs={'qprob': float(qprob)},
            output_core_dims=[('forecast',)],
            vectorize=True,
            dask='parallelized',
            output_dtypes=[float],
        )
        out = result.compute()
        client.close()
        return out.rename({'forecast': 'T'}).transpose('T', 'Y', 'X')

    def forecast(self, Predictant: xr.DataArray, clim_year_start: int, clim_year_end: int, Predictor: xr.DataArray, Predictor_for_year: xr.DataArray) -> Tuple[xr.DataArray, xr.DataArray]:
        # ensure predictant has (T,Y,X)
        if 'M' in Predictant.coords:
            Predictant = Predictant.isel(M=0).drop_vars('M').squeeze()
        Predictant = Predictant.transpose('T', 'Y', 'X')

        mean_field = self.compute_model(Predictor, Predictant, Predictor_for_year)
        prob_field = self.compute_prob(Predictor, Predictant, Predictor_for_year, Predictant=None, clim_year_start=clim_year_start, clim_year_end=clim_year_end)
        return mean_field, prob_field
