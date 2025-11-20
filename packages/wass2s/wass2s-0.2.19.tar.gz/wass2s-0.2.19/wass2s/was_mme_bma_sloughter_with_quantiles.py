# -*- coding: utf-8 -*-
from __future__ import annotations

import numpy as np
import xarray as xr

from typing import Optional, Tuple, Dict, Callable

from scipy.optimize import minimize_scalar
from scipy.stats import norm, gamma as st_gamma, lognorm, weibull_min, t
from scipy.special import gamma as sp_gamma

from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge

from dask.distributed import Client


# -----------------------------------------------------------------------------
# Helper: constant-probability logistic fallback (used if feature is constant)
# -----------------------------------------------------------------------------
class _ConstProb:
    """Simple object with a scikit-learn-like predict_proba interface.

    Returns a constant probability for class=1 ("dry").
    """

    def __init__(self, p: float):
        self.p = float(np.clip(p, 1e-12, 1 - 1e-12))

    def predict_proba(self, X):
        n = len(np.asarray(X).reshape(-1, 1))
        p1 = np.full(n, self.p)
        return np.column_stack([1 - p1, p1])


# -----------------------------------------------------------------------------
# Core: BMA Sloughter (with optional hurdle/zero-inflation and quantiles)
# -----------------------------------------------------------------------------
class BMA_Sloughter:
    """
    Bayesian Model Averaging (Sloughter-style) with optional zero-inflation (hurdle).

    - Member-specific debiasing: y ~ a_k + b_k * x_k (Linear or Ridge)
    - Mixture weights via EM with flooring to avoid collapse
    - Per-member dispersion parameter
    - Optional per-member dry probability p0_k via logistic on debiased μ_k
    - Predictive mean, CDF, and quantiles via robust bisection

    Distributions (parameterized so E[Y] = μ when Y≥0 families):
      * 'normal'     : N(μ, σ^2)
      * 'gamma'      : Gamma(shape=α, scale=μ/α)               (Y ≥ 0)
      * 'lognormal'  : LogNormal(s=σ_log, scale=exp(log(μ)-s^2/2)) (Y ≥ 0)
      * 'weibull'    : Weibull(k=c, scale=μ/Gamma(1+1/c))      (Y ≥ 0)
      * 't'          : Student t(df=22 by default, loc=μ, scale)

    For precipitation-like variables, use a positive family with zero_inflation=True.
    """

    def __init__(
        self,
        distribution: str = "normal",
        zero_inflation: bool = False,
        weight_floor: float = 1e-6,
        debias_model: str = "linear",  # 'linear' or 'ridge'
        ridge_alpha: float = 1e-4,
        df_t: int = 22,
    ):
        if distribution == "gaussian":
            distribution = "normal"
        if distribution not in ["normal", "gamma", "lognormal", "weibull", "t"]:
            raise ValueError("distribution must be one of: 'normal','gamma','lognormal','weibull','t'")

        self.distribution = distribution
        self.zero_inflation = bool(zero_inflation)
        self.weight_floor = float(weight_floor)
        self.debias_model = debias_model
        self.ridge_alpha = float(ridge_alpha)
        self.df = int(df_t) if distribution == "t" else None

        self.debiasing_models = []
        self.zero_models = []
        self.weights: Optional[np.ndarray] = None
        self.disp: Optional[np.ndarray] = None

        self.dist_configs = self._get_dist_configs()
        self.config = self.dist_configs[self.distribution]

    # -------------------- distribution configs --------------------
    def _get_dist_configs(self) -> Dict[str, Dict[str, Callable]]:
        return {
            "normal": {
                "pdf": lambda y, mu, sigma: norm.pdf(y, loc=mu, scale=sigma),
                "cdf": lambda q, mu, sigma: norm.cdf(q, loc=mu, scale=sigma),
                "initial": lambda res: np.nanstd(res) if res.size > 0 else 1.0,
                "bounds": (1e-5, np.inf),
                "closed_update": lambda r, res: (
                    np.sqrt(np.nansum(r * res**2) / max(np.nansum(r), 1e-12))
                ),
            },
            "gamma": {
                "pdf": lambda y, mu, alpha: st_gamma.pdf(
                    y, a=alpha, loc=0, scale=np.maximum(mu, 1e-12) / alpha
                ),
                "cdf": lambda q, mu, alpha: st_gamma.cdf(
                    q, a=alpha, loc=0, scale=np.maximum(mu, 1e-12) / alpha
                ),
                "initial": lambda y, mu: (
                    (np.nanmean(mu) ** 2 / np.nanvar(y))
                    if (np.nanvar(y) > 0 and np.nanmean(mu) > 0)
                    else 1.0
                ),
                "bounds": (0.01, 1000.0),
                "closed_update": None,
            },
            "lognormal": {
                "pdf": lambda y, mu, s: lognorm.pdf(
                    y, s=s, loc=0, scale=np.exp(np.log(np.maximum(mu, 1e-12)) - s**2 / 2)
                ),
                "cdf": lambda q, mu, s: lognorm.cdf(
                    q, s=s, loc=0, scale=np.exp(np.log(np.maximum(mu, 1e-12)) - s**2 / 2)
                ),
                "initial": lambda y, mu: (
                    np.sqrt(np.log(1 + (np.nanvar(y) / (np.nanmean(mu) ** 2))))
                    if (np.nanmean(mu) > 0 and np.nanvar(y) >= 0)
                    else 0.5
                ),
                "bounds": (0.01, 10.0),
                "closed_update": None,
            },
            "weibull": {
                "pdf": lambda y, mu, c: weibull_min.pdf(
                    y, c=c, loc=0, scale=np.maximum(mu, 1e-12) / sp_gamma(1 + 1.0 / c)
                ),
                "cdf": lambda q, mu, c: weibull_min.cdf(
                    q, c=c, loc=0, scale=np.maximum(mu, 1e-12) / sp_gamma(1 + 1.0 / c)
                ),
                "initial": lambda y, mu: 2.0,
                "bounds": (0.1, 10.0),
                "closed_update": None,
            },
            "t": {
                "pdf": lambda y, mu, scale, self=self: t.pdf(y, df=self.df, loc=mu, scale=scale),
                "cdf": lambda q, mu, scale, self=self: t.cdf(q, df=self.df, loc=mu, scale=scale),
                "initial": lambda res, self=self: (
                    np.nanstd(res) * np.sqrt((self.df - 2) / self.df) if (self.df and self.df > 2) else 1.0
                ),
                "bounds": (1e-5, np.inf),
                "closed_update": None,
            },
        }

    # -------------------- internal helpers --------------------
    def _make_debias_model(self):
        return Ridge(alpha=self.ridge_alpha) if self.debias_model == "ridge" else LinearRegression()

    def _fit_zero_models(self, mu_mat: np.ndarray, y: np.ndarray) -> None:
        z = (y <= 0).astype(int)
        self.zero_models = []
        for k in range(mu_mat.shape[1]):
            Xk = mu_mat[:, k].reshape(-1, 1)
            if not np.isfinite(Xk).all() or np.allclose(Xk, Xk[0]):
                p0 = float(np.clip(z.mean(), 1e-6, 1 - 1e-6))
                self.zero_models.append(_ConstProb(p0))
            else:
                clf = LogisticRegression(max_iter=200, solver="lbfgs")
                clf.fit(Xk, z)
                self.zero_models.append(clf)

    def _p0_member(self, mu_vec: np.ndarray, k: int) -> np.ndarray:
        if not self.zero_inflation:
            return np.zeros_like(mu_vec, dtype=float)
        clf = self.zero_models[k]
        return clf.predict_proba(mu_vec.reshape(-1, 1))[:, 1]

    # -------------------- public API --------------------
    def fit(self, ensemble_forecasts: np.ndarray, observations: np.ndarray) -> None:
        y = np.asarray(observations, dtype=float)
        X = np.asarray(ensemble_forecasts, dtype=float)
        if X.ndim != 2 or y.ndim != 1 or X.shape[0] != y.shape[0]:
            raise ValueError("Shapes must be (n_samples, m_members) and (n_samples,)")

        n_samples, m_members = X.shape

        # Debias per member
        self.debiasing_models = []
        mu_train = np.zeros((n_samples, m_members), dtype=float)
        for k in range(m_members):
            model = self._make_debias_model()
            xk = X[:, k].reshape(-1, 1)
            model.fit(xk, y)
            self.debiasing_models.append(model)
            mu_train[:, k] = model.predict(xk)

        if self.distribution in ["gamma", "lognormal", "weibull"]:
            mu_train = np.maximum(mu_train, 1e-5)

        if self.zero_inflation:
            self._fit_zero_models(mu_train, y)

        # Initialize weights & dispersion
        wk = np.ones(m_members, dtype=float) / m_members
        disp = np.zeros(m_members, dtype=float)
        for k in range(m_members):
            res_k = y - mu_train[:, k]
            if self.distribution in ["normal", "t"]:
                disp[k] = float(self.config["initial"](res_k))
            else:
                disp[k] = float(self.config["initial"](y, mu_train[:, k]))

        prev_LL = -np.inf
        tol = 1e-6
        max_iter = 100

        is_zero = y <= 0
        is_pos = ~is_zero

        for _ in range(max_iter):
            # E-step
            log_comp = np.zeros((n_samples, m_members), dtype=float)
            for k in range(m_members):
                wk_k = float(np.clip(wk[k], 1e-12, 1.0))
                if self.zero_inflation:
                    p0 = self._p0_member(mu_train[:, k], k)
                    # zeros
                    log_comp[is_zero, k] = np.log(wk_k) + np.log(np.clip(p0[is_zero], 1e-12, 1.0))
                    # positives
                    f_pos = self.config["pdf"](y[is_pos], mu_train[is_pos, k], disp[k])
                    log_comp[is_pos, k] = (
                        np.log(wk_k)
                        + np.log(np.clip(1 - p0[is_pos], 1e-12, 1.0))
                        + np.log(np.clip(f_pos, 1e-12, None))
                    )
                else:
                    f_all = self.config["pdf"](y, mu_train[:, k], disp[k])
                    log_comp[:, k] = np.log(wk_k) + np.log(np.clip(f_all, 1e-12, None))

            log_den = np.logaddexp.reduce(log_comp, axis=1)
            r_tk = np.exp(log_comp - log_den[:, None])

            # M-step: weights
            sum_r = r_tk.sum(axis=0)
            wk = sum_r / max(n_samples, 1)
            wk = np.clip(wk, self.weight_floor, None)
            wk = wk / wk.sum()

            # M-step: dispersion per member
            disp_new = np.zeros_like(disp)
            for k in range(m_members):
                if self.config.get("closed_update") is not None and self.distribution == "normal":
                    res_k = y - mu_train[:, k]
                    disp_new[k] = float(self.config["closed_update"](r_tk[:, k], res_k))
                    disp_new[k] = float(np.clip(disp_new[k], self.config["bounds"][0], np.inf))
                else:
                    def neg_ll(dsp: float) -> float:
                        lo, hi = self.config["bounds"]
                        if not (lo <= dsp <= hi):
                            return np.inf
                        if self.zero_inflation:
                            p0 = self._p0_member(mu_train[:, k], k)
                            ll_zero = r_tk[is_zero, k] * (
                                np.log(np.clip(wk[k], 1e-12, 1.0)) + np.log(np.clip(p0[is_zero], 1e-12, 1.0))
                            )
                            f_pos = self.config["pdf"](y[is_pos], mu_train[is_pos, k], dsp)
                            ll_pos = r_tk[is_pos, k] * (
                                np.log(np.clip(wk[k], 1e-12, 1.0))
                                + np.log(np.clip(1 - p0[is_pos], 1e-12, 1.0))
                                + np.log(np.clip(f_pos, 1e-12, None))
                            )
                            return -float(ll_zero.sum() + ll_pos.sum())
                        else:
                            f_all = self.config["pdf"](y, mu_train[:, k], dsp)
                            ll = r_tk[:, k] * (
                                np.log(np.clip(wk[k], 1e-12, 1.0)) + np.log(np.clip(f_all, 1e-12, None))
                            )
                            return -float(ll.sum())

                    res = minimize_scalar(
                        neg_ll,
                        bounds=self.config["bounds"],
                        method="bounded",
                        options={"xatol": 1e-5},
                    )
                    disp_new[k] = float(res.x if res.success else disp[k])
            disp = disp_new

            # Convergence check (full LL)
            if self.zero_inflation:
                LL = 0.0
                for t_idx in range(n_samples):
                    terms = []
                    for k in range(m_members):
                        wk_k = float(np.clip(wk[k], 1e-12, 1.0))
                        p0 = float(self._p0_member(mu_train[t_idx : t_idx + 1, k], k)[0])
                        if is_zero[t_idx]:
                            terms.append(np.log(wk_k) + np.log(np.clip(p0, 1e-12, 1.0)))
                        else:
                            f = float(self.config["pdf"](y[t_idx], mu_train[t_idx, k], disp[k]))
                            terms.append(
                                np.log(wk_k)
                                + np.log(np.clip(1 - p0, 1e-12, 1.0))
                                + np.log(np.clip(f, 1e-12, None))
                            )
                    LL += float(np.logaddexp.reduce(np.array(terms)))
            else:
                LL = 0.0
                for t_idx in range(n_samples):
                    terms = np.log(np.clip(wk, 1e-12, 1.0)).copy()
                    for k in range(m_members):
                        f = float(self.config["pdf"](y[t_idx], mu_train[t_idx, k], disp[k]))
                        terms[k] += np.log(np.clip(f, 1e-12, None))
                    LL += float(np.logaddexp.reduce(terms))

            if np.isfinite(prev_LL) and abs(LL - prev_LL) < tol:
                break
            prev_LL = LL

        self.weights = wk
        self.disp = disp

    def predict_cdf(self, new_forecasts: np.ndarray, q: float) -> np.ndarray:
        X = np.asarray(new_forecasts, dtype=float)
        if X.ndim != 2 or len(self.debiasing_models) != X.shape[1]:
            raise ValueError("new_forecasts must be (n_new, m_members) matching trained members.")

        n_new, m_members = X.shape
        mu_new = np.zeros((n_new, m_members), dtype=float)
        for k in range(m_members):
            mu_new[:, k] = self.debiasing_models[k].predict(X[:, k].reshape(-1, 1))
        if self.distribution in ["gamma", "lognormal", "weibull"]:
            mu_new = np.maximum(mu_new, 1e-5)

        cdf_mix = np.zeros(n_new, dtype=float)
        if self.zero_inflation:
            for k in range(m_members):
                p0k = self._p0_member(mu_new[:, k], k)
                Fk = self.config["cdf"](q, mu_new[:, k], self.disp[k])
                cdf_k = p0k + (1.0 - p0k) * Fk
                cdf_mix += self.weights[k] * cdf_k
        else:
            for k in range(m_members):
                Fk = self.config["cdf"](q, mu_new[:, k], self.disp[k])
                cdf_mix += self.weights[k] * Fk
        return np.clip(cdf_mix, 0.0, 1.0)

    def predict_mean(self, new_forecasts: np.ndarray) -> np.ndarray:
        X = np.asarray(new_forecasts, dtype=float)
        if X.ndim != 2 or len(self.debiasing_models) != X.shape[1]:
            raise ValueError("new_forecasts must be (n_new, m_members) matching trained members.")

        n_new, m_members = X.shape
        mu_new = np.zeros((n_new, m_members), dtype=float)
        for k in range(m_members):
            mu_new[:, k] = self.debiasing_models[k].predict(X[:, k].reshape(-1, 1))
        if self.distribution in ["gamma", "lognormal", "weibull"]:
            mu_new = np.maximum(mu_new, 1e-5)

        if self.zero_inflation:
            mean = np.zeros(n_new, dtype=float)
            for k in range(m_members):
                p0k = self._p0_member(mu_new[:, k], k)
                mean += self.weights[k] * (1.0 - p0k) * mu_new[:, k]
            return mean
        else:
            return np.sum(self.weights * mu_new, axis=1)

    def predict_quantile(
        self,
        new_forecasts: np.ndarray,
        qprob: float,
        tol: float = 1e-4,
        max_iter: int = 80,
        max_upper: float = 1e8,
    ) -> np.ndarray:
        """Predict the qprob-quantile via robust bisection on the mixture CDF.

        Works for both hurdle (zero-inflation) and continuous families.
        """
        X = np.asarray(new_forecasts, dtype=float)
        if X.ndim != 2 or len(self.debiasing_models) != X.shape[1]:
            raise ValueError("new_forecasts must be (n_new, m_members) matching trained members.")

        p = float(np.clip(qprob, 1e-12, 1 - 1e-12))

        n_new, m_members = X.shape
        mu_new = np.zeros((n_new, m_members), dtype=float)
        for k in range(m_members):
            mu_new[:, k] = self.debiasing_models[k].predict(X[:, k].reshape(-1, 1))
        if self.distribution in ["gamma", "lognormal", "weibull"]:
            mu_new = np.maximum(mu_new, 1e-5)

        # mix dry probability & mean proxy
        p0_mix = np.zeros(n_new, dtype=float)
        mean_proxy = np.zeros(n_new, dtype=float)
        if self.zero_inflation:
            for i in range(n_new):
                p0 = 0.0
                mpos = 0.0
                for k in range(m_members):
                    p0k = float(self._p0_member(mu_new[i : i + 1, k], k)[0])
                    p0 += self.weights[k] * p0k
                    mpos += self.weights[k] * (1.0 - p0k) * mu_new[i, k]
                p0_mix[i] = np.clip(p0, 0.0, 1.0)
                mean_proxy[i] = mpos
        else:
            mean_proxy = np.sum(self.weights * mu_new, axis=1)

        # scale proxy for real-line families
        scale_proxy = None
        if self.distribution in ["normal", "t"]:
            scale_proxy = float(np.sum(self.weights * self.disp))
            if not np.isfinite(scale_proxy) or scale_proxy <= 0:
                scale_proxy = 1.0

        out = np.empty(n_new, dtype=float)

        for i in range(n_new):
            # jump at 0 for hurdle
            if self.zero_inflation and p <= p0_mix[i] + 1e-12:
                out[i] = 0.0
                continue

            Xi = X[i : i + 1, :]

            def cdf_at(q):
                return float(self.predict_cdf(Xi, q)[0])

            # bracket
            if self.distribution in ["gamma", "lognormal", "weibull"]:
                L = 0.0
                base = max(1.0, mean_proxy[i], float(np.max(mu_new[i, :])))
                U = base * 4.0 + 1.0
                Fu = cdf_at(U)
                expand_guard = 0
                while Fu < p and U < max_upper:
                    U *= 2.0
                    Fu = cdf_at(U)
                    expand_guard += 1
                    if expand_guard > 60:
                        break
                if Fu < p:  # extreme tail
                    out[i] = U
                    continue
            else:
                mu_bar = mean_proxy[i]
                sbar = scale_proxy if scale_proxy is not None else 1.0
                k0 = 8.0
                L = mu_bar - k0 * sbar
                U = mu_bar + k0 * sbar
                FL, FU = cdf_at(L), cdf_at(U)
                expand_guard = 0
                while FL > p and expand_guard < 60:
                    L -= 2.0 * sbar
                    FL = cdf_at(L)
                    expand_guard += 1
                expand_guard = 0
                while FU < p and expand_guard < 60:
                    U += 2.0 * sbar
                    FU = cdf_at(U)
                    expand_guard += 1

            # bisection
            a, b = L, U
            for _ in range(max_iter):
                m = 0.5 * (a + b)
                Fm = cdf_at(m)
                if Fm < p:
                    a = m
                else:
                    b = m
                if abs(b - a) <= tol * max(1.0, abs(m)):
                    break
            out[i] = 0.5 * (a + b)

        return out


# -----------------------------------------------------------------------------
# Grid wrapper using xarray/dask for (T,Y,X) fields
# -----------------------------------------------------------------------------
class WAS_mme_BMA_Sloughter:
    """
    Dask/xarray wrapper around BMA_Sloughter for gridded data.

    Methods
    -------
    compute_model : predictive mean field (T, Y, X)
    compute_prob  : tercile class probabilities (3, T, Y, X)
    compute_quantile : q-quantile field (T, Y, X)
    forecast      : convenience wrapper (mean, probs)

    Expects dims:
      X_train: (T, M, Y, X)
      y_train: (T, Y, X)
      X_test : (T, M, Y, X) or (forecast, M, Y, X)
    """

    def __init__(self, dist_method: str = "normal", nb_cores: int = 1):
        self.dist_method = dist_method
        self.nb_cores = int(nb_cores)

    # ---- scalar helpers used in apply_ufunc ----
    def fit_predict(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)

        n_forecast = X_test.shape[0]
        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((n_forecast,), np.nan, dtype=float)

        X_clean = X[ok, :]
        y_clean = y[ok]

        zero_infl = self.dist_method in ["gamma", "lognormal", "weibull"]
        model = BMA_Sloughter(self.dist_method, zero_inflation=zero_infl)
        model.fit(X_clean, y_clean)
        preds = model.predict_mean(X_test)
        return np.asarray(preds, dtype=float).reshape(n_forecast)

    def predict_proba(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray, t33: float, t67: float) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)

        n_forecast = X_test.shape[0]
        if not np.isfinite(t33) or not np.isfinite(t67):
            return np.full((3, n_forecast), np.nan, dtype=float)

        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((3, n_forecast), np.nan, dtype=float)

        X_clean = X[ok, :]
        y_clean = y[ok]

        zero_infl = self.dist_method in ["gamma", "lognormal", "weibull"]
        model = BMA_Sloughter(self.dist_method, zero_inflation=zero_infl)
        model.fit(X_clean, y_clean)

        pb = model.predict_cdf(X_test, t33)
        pn = model.predict_cdf(X_test, t67) - pb
        pa = 1.0 - model.predict_cdf(X_test, t67)

        out = np.vstack([pb, pn, pa]).astype(float)
        out = np.clip(out, 0.0, 1.0)
        s = out.sum(axis=0)
        good = s > 0
        out[:, good] /= s[good]
        return out

    def fit_predict_quantile(self, X: np.ndarray, y: np.ndarray, X_test: np.ndarray, qprob: float) -> np.ndarray:
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        X_test = np.asarray(X_test)

        n_forecast = X_test.shape[0]
        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=-1)
        if not np.any(ok):
            return np.full((n_forecast,), np.nan, dtype=float)

        X_clean = X[ok, :]
        y_clean = y[ok]

        zero_infl = self.dist_method in ["gamma", "lognormal", "weibull"]
        model = BMA_Sloughter(self.dist_method, zero_inflation=zero_infl)
        model.fit(X_clean, y_clean)
        q = model.predict_quantile(X_test, float(qprob))
        return np.asarray(q, dtype=float).reshape(n_forecast)

    # ---- public methods ----
    def compute_model(self, X_train: xr.DataArray, y_train: xr.DataArray, X_test: xr.DataArray) -> xr.DataArray:
        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index("X")) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index("Y")) / self.nb_cores)))

        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train["T"]).transpose("T", "M", "Y", "X")
        y_train = y_train.transpose("T", "Y", "X")

        if "T" in X_test.dims:
            X_test = X_test.rename({"T": "forecast"})
        X_test = X_test.transpose("forecast", "M", "Y", "X")

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)

        result = xr.apply_ufunc(
            self.fit_predict,
            X_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            y_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            X_test.chunk({"Y": chunksize_y, "X": chunksize_x}),
            input_core_dims=[("T", "M"), ("T",), ("forecast", "M")],
            output_core_dims=[("forecast",)],
            vectorize=True,
            dask="parallelized",
            output_dtypes=[float],
        )

        out = result.compute()
        client.close()
        return out.rename({"forecast": "T"}).transpose("T", "Y", "X")

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
            raise ValueError("clim_year_start and clim_year_end must be provided.")

        if Predictant is not None:
            idx_start = Predictant.get_index("T").get_loc(str(clim_year_start)).start
            idx_end = Predictant.get_index("T").get_loc(str(clim_year_end)).stop
            series = Predictant.isel(T=slice(idx_start, idx_end))
        else:
            idx_start = y_train.get_index("T").get_loc(str(clim_year_start)).start
            idx_end = y_train.get_index("T").get_loc(str(clim_year_end)).stop
            series = y_train.isel(T=slice(idx_start, idx_end))

        terciles = series.quantile([0.33, 0.67], dim="T")
        T1 = terciles.isel(quantile=0).drop_vars("quantile")
        T2 = terciles.isel(quantile=1).drop_vars("quantile")

        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index("X")) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index("Y")) / self.nb_cores)))

        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train["T"]).transpose("T", "M", "Y", "X")
        y_train = y_train.transpose("T", "Y", "X")

        if "T" in X_test.dims:
            X_test = X_test.rename({"T": "forecast"})
        X_test = X_test.transpose("forecast", "M", "Y", "X")

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)

        result = xr.apply_ufunc(
            self.predict_proba,
            X_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            y_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            X_test.chunk({"Y": chunksize_y, "X": chunksize_x}),
            T1.chunk({"Y": chunksize_y, "X": chunksize_x}),
            T2.chunk({"Y": chunksize_y, "X": chunksize_x}),
            input_core_dims=[("T", "M"), ("T",), ("forecast", "M"), (), ()],
            output_core_dims=[("probability", "forecast")],
            vectorize=True,
            dask="parallelized",
            output_dtypes=[float],
            dask_gufunc_kwargs={"output_sizes": {"probability": 3}},
        )

        out = result.compute()
        client.close()

        return (
            out.rename({"forecast": "T"})
            .assign_coords(probability=("probability", ["PB", "PN", "PA"]))
            .transpose("probability", "T", "Y", "X")
        )

    def compute_quantile(
        self,
        X_train: xr.DataArray,
        y_train: xr.DataArray,
        X_test: xr.DataArray,
        qprob: float,
    ) -> xr.DataArray:
        if not (0.0 < qprob < 1.0):
            raise ValueError("qprob must be in (0,1).")

        chunksize_x = int(np.maximum(1, np.round(len(y_train.get_index("X")) / self.nb_cores)))
        chunksize_y = int(np.maximum(1, np.round(len(y_train.get_index("Y")) / self.nb_cores)))

        X_train = X_train.copy()
        X_train = X_train.assign_coords(T=y_train["T"]).transpose("T", "M", "Y", "X")
        y_train = y_train.transpose("T", "Y", "X")

        if "T" in X_test.dims:
            X_test = X_test.rename({"T": "forecast"})
        X_test = X_test.transpose("forecast", "M", "Y", "X")

        client = Client(n_workers=self.nb_cores, threads_per_worker=1)

        result = xr.apply_ufunc(
            self.fit_predict_quantile,
            X_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            y_train.chunk({"Y": chunksize_y, "X": chunksize_x}),
            X_test.chunk({"Y": chunksize_y, "X": chunksize_x}),
            input_core_dims=[("T", "M"), ("T",), ("forecast", "M")],
            kwargs={"qprob": float(qprob)},
            output_core_dims=[("forecast",)],
            vectorize=True,
            dask="parallelized",
            output_dtypes=[float],
        )

        out = result.compute()
        client.close()
        return out.rename({"forecast": "T"}).transpose("T", "Y", "X")

    def forecast(
        self,
        predictant: xr.DataArray,
        clim_year_start: int,
        clim_year_end: int,
        Predictor: xr.DataArray,
        Predictor_for_year: xr.DataArray,
    ) -> Tuple[xr.DataArray, xr.DataArray]:
        if "M" in predictant.coords:
            predictant = predictant.isel(M=0).drop_vars("M").squeeze()

        predict_mean = self.compute_model(Predictor, predictant, Predictor_for_year)
        predict_proba = self.compute_prob(
            Predictor,
            predictant,
            Predictor_for_year,
            Predictant=None,
            clim_year_start=clim_year_start,
            clim_year_end=clim_year_end,
        )
        return predict_mean, predict_proba
