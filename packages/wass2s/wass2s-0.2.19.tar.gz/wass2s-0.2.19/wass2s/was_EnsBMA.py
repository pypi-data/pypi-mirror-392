# ensemble_bma_extended.py
# Replicates R's ensembleBMA in Python with:
#  - GaussianBMA / GammaBMA / GammaZeroInflatedBMA (EM fitting)
#  - Full xarray/Dask grid wrappers for Gaussian, Gamma, Gamma0
#  - Gaussian CRPS-first joint optimizer (LBFGS) for (a,b,σ,w)
#  - WASS2S-style facades: WAS_BMA_Gaussian, WAS_BMA_Gamma, WAS_BMA_Gamma0

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Iterable
import warnings

from scipy.stats import norm
from scipy.stats import gamma as scigamma
from scipy.special import gammaln, digamma
from scipy.optimize import minimize

try:
    import xarray as xr
except Exception:  # keep core usable without xarray
    xr = None

__all__ = [
    "ExchangeableGroups",
    "GaussianBMA", "GammaBMA", "GammaZeroInflatedBMA",
    "fit_gaussian_grid", "predict_gaussian_grid",
    "fit_gamma_grid", "predict_gamma_grid",
    "fit_gamma0_grid", "predict_gamma0_grid",
    "WAS_BMA_Gaussian", "WAS_BMA_Gamma", "WAS_BMA_Gamma0",
]

# ===============================================================
# Core helpers
# ===============================================================

@dataclass
class ExchangeableGroups:
    """Members in the same sublist share (a,b,dispersion). Example: [[0,1,2],[3,4],[5]]"""
    groups: List[List[int]]
    def n_groups(self) -> int: return len(self.groups)


def _nan_mask(*arrs: np.ndarray) -> np.ndarray:
    masks = []
    for a in arrs:
        a = np.asarray(a)
        if a.ndim == 2:
            masks.append(np.isfinite(a).all(axis=1))
        else:
            masks.append(np.isfinite(a))
    m = masks[0].copy()
    for mm in masks[1:]:
        m &= mm
    return m


def _wls_ab(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    w = np.asarray(w, float); x = np.asarray(x, float); y = np.asarray(y, float)
    S0 = w.sum()
    if S0 <= 0: return 0.0, 1.0
    Sx = (w*x).sum(); Sy = (w*y).sum()
    Sxx = (w*x*x).sum(); Sxy = (w*x*y).sum()
    denom = S0*Sxx - Sx*Sx
    if denom <= 1e-15: return Sy/S0, 0.0
    b = (S0*Sxy - Sx*Sy)/denom
    a = (Sy - b*Sx)/S0
    return a, b


def _softplus(x: np.ndarray) -> np.ndarray:
    return np.where(x > 30, x, np.log1p(np.exp(x)))


# ===============================================================
# Base EM class
# ===============================================================

@dataclass
class _ParamsBase:
    weights_member: np.ndarray   # (m,)
    a_group: np.ndarray          # (G,)
    b_group: np.ndarray          # (G,)


class _BMABase:
    def __init__(
        self,
        exchangeable: Optional[ExchangeableGroups] = None,
        max_iter: int = 200,
        tol: float = 1e-6,
        w_floor: float = 1e-8,
        verbose: bool = False,
        random_state: Optional[int] = None,
    ):
        self.exchangeable = exchangeable
        self.max_iter = max_iter
        self.tol = tol
        self.w_floor = w_floor
        self.verbose = verbose
        self.rng = np.random.default_rng(random_state)
        self.params_: Optional[_ParamsBase] = None

    def _groups(self, m: int) -> ExchangeableGroups:
        return self.exchangeable or ExchangeableGroups([[k] for k in range(m)])

    # hooks implemented by subclasses
    def _init_extra(self, y: np.ndarray, F: np.ndarray, p: _ParamsBase) -> _ParamsBase: return p
    def _logpdf_matrix(self, y: np.ndarray, F: np.ndarray, p: _ParamsBase) -> np.ndarray: raise NotImplementedError
    def _mstep_params(self, y: np.ndarray, F: np.ndarray, r: np.ndarray, p: _ParamsBase) -> _ParamsBase: raise NotImplementedError

    def _member_ab(self, m: int, p: _ParamsBase) -> Tuple[np.ndarray, np.ndarray]:
        g = self._groups(m)
        a_k = np.zeros(m); b_k = np.zeros(m)
        for gi, Gm in enumerate(g.groups):
            a_k[Gm] = p.a_group[gi]; b_k[Gm] = p.b_group[gi]
        return a_k, b_k

    def fit(self, F: np.ndarray, y: np.ndarray):
        F = np.asarray(F, float); y = np.asarray(y, float)
        T, m = F.shape
        mask = _nan_mask(F, y)
        F, y = F[mask], y[mask]
        if F.size == 0: raise ValueError("No valid data to fit.")
        g = self._groups(m); G = g.n_groups()

        # init (a,b) from pooled regression on group mean; equal weights
        w = np.ones(m)/m
        a = np.zeros(G); b = np.ones(G)
        for gi, Gm in enumerate(g.groups):
            xg = F[:, Gm].mean(axis=1)
            a[gi], b[gi] = _wls_ab(y, xg, np.ones_like(y))
        p = _ParamsBase(weights_member=w, a_group=a, b_group=b)
        p = self._init_extra(y, F, p)

        prev_ll = -np.inf
        for it in range(self.max_iter):
            # E-step
            logpdf = self._logpdf_matrix(y, F, p)       # (T,m)
            lse = np.log(p.weights_member + 1e-300) + logpdf
            max_ = np.max(lse, axis=1, keepdims=True)
            num = np.exp(lse - max_); den = num.sum(axis=1, keepdims=True) + 1e-300
            r = num / den
            ll = np.sum(np.log(num.sum(axis=1)) + max_.squeeze())
            if self.verbose: print(f"[EM] {it:03d} ll={ll:.6f} Δ={ll-prev_ll:.3e}")
            if abs(ll - prev_ll) < self.tol: break
            prev_ll = ll

            # M-step
            w = r.sum(axis=0)/r.shape[0]
            w = np.maximum(w, self.w_floor); w /= w.sum()
            p.weights_member = w
            p = self._mstep_params(y, F, r, p)

        self.params_ = p
        return self


# ===============================================================
# Gaussian BMA (ensembleBMAnormal) + CRPS-first optimizer
# ===============================================================

@dataclass
class _GaussianParams(_ParamsBase):
    var_group: np.ndarray       # (G,)
    common_variance: bool = True


class GaussianBMA(_BMABase):
    """Gaussian BMA: y|k ~ N(a_g + b_g f_k, sigma_g^2) for member k in group g.

    Methods:
      - fit: EM on NLL (like R)
      - fit_crps_lbfgs: CRPS-first joint optimization of (a,b,σ,w) with LBFGS (common σ)
    """
    def __init__(self, exchangeable: Optional[ExchangeableGroups] = None,
                 common_variance: bool = True, var_floor: float = 1e-6,
                 **kw):
        super().__init__(exchangeable=exchangeable, **kw)
        self.var_floor = var_floor
        self.common_variance = common_variance

    # ----- EM pieces -----
    def _init_extra(self, y, F, p):
        G = self._groups(F.shape[1]).n_groups()
        return _GaussianParams(**p.__dict__, var_group=np.full(G, np.var(y)+self.var_floor),
                               common_variance=self.common_variance)

    def _logpdf_matrix(self, y, F, p: _GaussianParams):
        T, m = F.shape
        a_k, b_k = self._member_ab(m, p)
        mu = a_k + b_k*F
        if p.common_variance:
            v = np.full(m, p.var_group.mean())
        else:
            v = np.empty(m); g = self._groups(m)
            for gi, Gm in enumerate(g.groups): v[Gm] = p.var_group[gi]
        return -0.5*(np.log(2*np.pi*v) + (y[:,None]-mu)**2/v)

    def _mstep_params(self, y, F, r, p: _GaussianParams):
        m = F.shape[1]; g = self._groups(m)
        for gi, Gm in enumerate(g.groups):
            w_t = r[:, Gm].sum(axis=1)
            xg = F[:, Gm].mean(axis=1)
            a, b = _wls_ab(y, xg, w_t)
            p.a_group[gi], p.b_group[gi] = a, b
        a_k, b_k = self._member_ab(m, p)
        mu = a_k + b_k*F
        if p.common_variance:
            v = (r * (y[:,None]-mu)**2).sum() / max(r.sum(), 1e-12)
            p.var_group[:] = max(self.var_floor, v)
        else:
            for gi, Gm in enumerate(g.groups):
                num = (r[:,Gm] * (y[:,None]-mu[:,Gm])**2).sum()
                den = max(r[:,Gm].sum(), 1e-12)
                p.var_group[gi] = max(self.var_floor, num/den)
        return p

    # ----- Prediction -----
    def predictive_mean_var(self, f_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        p: _GaussianParams = self.params_; 
        if p is None: raise RuntimeError("Model not fitted.")
        f = np.atleast_2d(f_new).astype(float); m = f.shape[1]
        a_k, b_k = self._member_ab(m, p)
        mu = a_k + b_k*f
        if p.common_variance:
            v_m = np.full(m, p.var_group.mean())
        else:
            v_m = np.empty(m); g = self._groups(m)
            for gi, Gm in enumerate(g.groups): v_m[Gm] = p.var_group[gi]
        w = p.weights_member
        mean = (w*mu).sum(axis=1)
        var = (w*(v_m + (mu-mean[:,None])**2)).sum(axis=1)
        return mean.squeeze(), var.squeeze()

    def cdf(self, x: np.ndarray, f_new: np.ndarray) -> np.ndarray:
        p: _GaussianParams = self.params_
        if p is None: raise RuntimeError("Model not fitted.")
        f = np.atleast_2d(f_new)
        m = f.shape[1]
        a_k, b_k = self._member_ab(m, p)
        mu = a_k + b_k * f
        if p.common_variance:
            v_m = np.full(m, p.var_group.mean())
        else:
            v_m = np.empty(m); g = self._groups(m)
            for gi, Gm in enumerate(g.groups): v_m[Gm] = p.var_group[gi]
        x = np.asarray(x)[..., None]
        return (p.weights_member * norm.cdf(x, mu, np.sqrt(v_m))).sum(axis=-1)

    def ppf(self, q: np.ndarray, f_new: np.ndarray, lo: float=-1e4, hi: float=1e4, it: int=60) -> np.ndarray:
        q = np.atleast_1d(q); f = np.atleast_2d(f_new)
        out = np.empty((f.shape[0], q.size))
        for i in range(f.shape[0]):
            for j, qq in enumerate(q):
                a, b = lo, hi
                for _ in range(it):
                    mid = 0.5*(a+b)
                    c = (self.cdf(mid, f[i:i+1]) - qq)[0]
                    if c > 0: b = mid
                    else: a = mid
                out[i,j] = 0.5*(a+b)
        return out.squeeze()

    # ===========================================================
    # CRPS-first joint optimizer (LBFGS) for (a,b,σ,w)
    #   - common variance σ
    #   - exchangeable (a,b) per group
    # ===========================================================
    def fit_crps_lbfgs(
        self,
        F: np.ndarray,
        y: np.ndarray,
        init: str = "em",
        l2: float = 0.0,
        maxiter: int = 300,
        verbose: bool = False,
    ):
        F = np.asarray(F, float); y = np.asarray(y, float)
        T, m = F.shape
        g = self._groups(m); G = g.n_groups()
        # start from EM if requested
        if init == "em" or self.params_ is None:
            _ = self.fit(F, y)
        p0: _GaussianParams = self.params_
        # pack params -> theta
        a0 = p0.a_group.copy(); b0 = p0.b_group.copy();
        sigma0 = float(np.sqrt(p0.var_group.mean()))
        alpha0 = np.log(np.maximum(p0.weights_member, 1e-12))
        # Map members to group index
        group_idx = np.empty(m, dtype=int)
        for gi, Gm in enumerate(g.groups):
            group_idx[Gm] = gi

        def unpack(theta):
            a = theta[0:G]
            b = theta[G:2*G]
            s_raw = theta[2*G]
            alpha = theta[2*G+1:2*G+1+m]
            # stabilize logits to avoid drift
            alpha = alpha - alpha.mean()
            w = np.exp(alpha); w /= w.sum()
            sigma = np.exp(s_raw)  # positive
            return a, b, sigma, w

        def pack(a, b, sigma, alpha):
            s_raw = np.log(max(sigma, 1e-12))
            return np.concatenate([a, b, np.array([s_raw]), alpha])

        theta0 = pack(a0, b0, sigma0, alpha0)

        # Pre-allocate arrays for speed
        ones_m = np.ones(m)
        sqrt2 = np.sqrt(2.0)

        def objective(theta):
            a, b, sigma, w = unpack(theta)
            # build per-member a_k,b_k
            a_k = a[group_idx]; b_k = b[group_idx]
            # mu_tk
            mu = a_k + b_k * F  # (T,m)
            z = (y[:,None] - mu) / sigma
            Phi = norm.cdf(z); phi = norm.pdf(z)
            # A_tk for CRPS term1
            A = 2*sigma*phi + (y[:,None] - mu)*(2*Phi - 1)
            term1 = (A @ w).sum()
            # pairwise terms per t
            crps = 0.0
            d_obj_da = np.zeros(G)
            d_obj_db = np.zeros(G)
            d_obj_ds = 0.0
            d_obj_dw = np.zeros(m)
            for t in range(T):
                mu_t = mu[t]
                z_t = z[t]
                Phi_t = Phi[t]
                phi_t = phi[t]
                # term1 contrib to grads
                # d/dmu A = 1 - 2 Phi(z)
                dA_dmu = 1 - 2*Phi_t
                g_mu_term1 = w * dA_dmu  # (m,)
                # accumulate to a,b by groups
                for gi, Gm in enumerate(g.groups):
                    idx = np.array(Gm)
                    d_obj_da[gi] += g_mu_term1[idx].sum()
                    d_obj_db[gi] += (g_mu_term1[idx] * F[t, idx]).sum()
                # d/dsigma A = 2 phi(z)
                d_obj_ds += (w * (2*phi_t)).sum()
                # weights gradient: ∂/∂w A = A
                d_obj_dw += A[t]

                # pairwise part
                # Δ_ij, s = sqrt(2)*sigma, d_ij = Δ/s
                Delta = mu_t[:,None] - mu_t[None,:]
                s = sqrt2 * sigma
                d = Delta / s
                Phi_d = norm.cdf(d); phi_d = norm.pdf(d)
                # E_ij = 2 s φ(d) + Δ (2Φ(d) - 1)
                E = 2*s*phi_d + Delta*(2*Phi_d - 1)
                # objective subtracts 0.5 * w^T E w
                crps += (w @ A[t]) - 0.5 * (w @ (E @ w))
                # grads wrt mu for pairwise part: - w_k * Σ_j w_j (2Φ(d_kj)-1)
                H = (2*Phi_d - 1)  # (m,m)
                Hw = H @ w
                g_mu_pair = - w * Hw  # (m,)
                for gi, Gm in enumerate(g.groups):
                    idx = np.array(Gm)
                    d_obj_da[gi] += g_mu_pair[idx].sum()
                    d_obj_db[gi] += (g_mu_pair[idx] * F[t, idx]).sum()
                # grad wrt sigma for pairwise: -0.5 * 2√2 Σ_{ij} w_i w_j φ(d)
                d_obj_ds += - (np.sqrt(2.0) * (w[:,None] * w[None,:] * phi_d).sum())
                # grad wrt w: A - E w - (E^T w) / 2?  We derived: A - Σ_j w_j E_{kj}
                d_obj_dw += - (E @ w)

            # add L2 regularization on a,b to stabilize
            if l2 > 0:
                crps += 0.5*l2*(np.sum(a*a) + np.sum(b*b))
                d_obj_da += l2 * a
                d_obj_db += l2 * b

            # gradients wrt raw params
            # a,b already accumulated
            # sigma raw: s_raw = log sigma -> d/ds_raw = d/dsigma * sigma
            ds_raw = d_obj_ds * sigma
            # weights logits: softmax Jacobian: (diag(w) - w w^T) g_w
            g_w = d_obj_dw  # length m
            g_alpha = w * g_w - (w @ g_w) * w

            # pack gradient
            grad = np.concatenate([d_obj_da, d_obj_db, np.array([ds_raw]), g_alpha])
            # objective is total CRPS (sum over t)
            return crps, grad

        res = minimize(lambda th: objective(th)[0], theta0, jac=lambda th: objective(th)[1],
                       method='L-BFGS-B', options=dict(maxiter=maxiter, disp=verbose))
        a, b, sigma, w = unpack(res.x)
        # store into params_
        var = max(self.var_floor, float(sigma**2))
        p = _GaussianParams(weights_member=w, a_group=a, b_group=b,
                            var_group=np.full(g.n_groups(), var), common_variance=True)
        self.params_ = p
        return self

    # ---------- Optional weight-only CRPS refinement (components fixed) ----------
    @staticmethod
    def _A_gauss(y, mu, sigma):
        z = (y-mu)/sigma
        return 2*sigma*norm.pdf(z) + (y-mu)*(2*norm.cdf(z)-1)

    @staticmethod
    def _Eabs_diff(mu_i, sig_i, mu_j, sig_j):
        s = np.sqrt(sig_i**2 + sig_j**2)
        d = (mu_i - mu_j)/s
        return 2*s*norm.pdf(d) + (mu_i - mu_j)*(2*norm.cdf(d)-1)

    def refine_weights_by_crps(self, F: np.ndarray, y: np.ndarray, max_iter: int = 200):
        p: _GaussianParams = self.params_
        if p is None: raise RuntimeError("Fit first.")
        F = np.asarray(F,float); y = np.asarray(y,float)
        T, m = F.shape
        a_k, b_k = self._member_ab(m, p)
        mu = a_k + b_k*F
        if p.common_variance:
            sig = np.full(m, np.sqrt(p.var_group.mean()))
        else:
            sig = np.empty(m); g = self._groups(m)
            for gi,Gm in enumerate(g.groups): sig[Gm] = np.sqrt(p.var_group[gi])
        # precompute
        A = np.empty((T,m))
        for k in range(m):
            A[:,k] = self._A_gauss(y, mu[:,k], sig[k])
        E = np.empty((m,m))
        for i in range(m):
            for j in range(m):
                E[i,j] = self._Eabs_diff(mu[:,i].mean(), sig[i], mu[:,j].mean(), sig[j])
        w = p.weights_member.copy()
        logits = np.log(w + 1e-12)
        def crps_grad(logits):
            w = np.exp(logits - logits.max()); w /= w.sum()
            term1 = (A @ w).sum(); term2 = 0.5 * w @ E @ w
            crps = term1 - term2
            g_w = A.sum(0) - (E @ w)
            grad_logits = g_w * w - (w @ g_w) * w
            return -crps, -grad_logits  # minimize
        lr = 0.5
        val, grad = crps_grad(logits)
        for _ in range(max_iter):
            logits -= lr * grad
            val_new, grad = crps_grad(logits)
            if abs(val_new - val) < 1e-9: break
            val = val_new
        w = np.exp(logits - logits.max()); w /= w.sum()
        p.weights_member = np.maximum(w, self.w_floor); p.weights_member /= p.weights_member.sum()
        self.params_ = p
        return self


# ===============================================================
# Gamma BMA (ensembleBMAgamma) and Gamma0 (ensembleBMAgamma0)
# ===============================================================

@dataclass
class _GammaParams(_ParamsBase):
    shape_group: np.ndarray      # (G,)


class GammaBMA(_BMABase):
    """Gamma BMA for strictly-positive variables (e.g., wind speed).
    y|k ~ Gamma(shape=α_g, scale=μ_k/α_g), with μ_k = softplus(a_g + b_g f_k).
    """
    def __init__(self, exchangeable: Optional[ExchangeableGroups] = None,
                 shape_floor: float = 1e-3, **kw):
        super().__init__(exchangeable=exchangeable, **kw)
        self.shape_floor = shape_floor

    def _init_extra(self, y, F, p):
        G = self._groups(F.shape[1]).n_groups()
        return _GammaParams(**p.__dict__, shape_group=np.full(G, 5.0))

    def _mu(self, F, p: _GammaParams):
        m = F.shape[1]
        a_k, b_k = self._member_ab(m, p)
        return _softplus(a_k + b_k*F)

    def _logpdf_matrix(self, y, F, p: _GammaParams):
        y_pos = np.maximum(y, 1e-300)
        mu = self._mu(F, p)
        m = F.shape[1]; g = self._groups(m)
        alpha = np.empty(m)
        for gi,Gm in enumerate(g.groups): alpha[Gm] = max(self.shape_floor, p.shape_group[gi])
        return (alpha[None,:]-1)*np.log(y_pos[:,None]) - alpha[None,:]*np.log(mu) \
               - y_pos[:,None]*alpha[None,:]/mu - gammaln(alpha[None,:])

    def _mstep_params(self, y, F, r, p: _GammaParams):
        m = F.shape[1]; g = self._groups(m)
        pos = y > 0
        if not pos.any(): 
            warnings.warn("All zeros encountered; GammaBMA cannot fit. Consider GammaZeroInflatedBMA.")
            return p
        y_pos, F_pos, r_pos = y[pos], F[pos], r[pos]
        for gi, Gm in enumerate(g.groups):
            w_t = r_pos[:,Gm].sum(axis=1)
            xg = F_pos[:,Gm].mean(axis=1)
            a, b = _wls_ab(y_pos, xg, w_t)
            p.a_group[gi], p.b_group[gi] = a, b
        # simple fixed-point update for shape using method-of-moments/weighted Newton
        mu = self._mu(F_pos, p)
        for gi, Gm in enumerate(g.groups):
            r_g = r_pos[:,Gm]
            A = r_g.sum(axis=1)
            B = (r_g * np.log(np.maximum(mu[:,Gm], 1e-300))).sum(axis=1)
            C = (r_g / np.maximum(mu[:,Gm], 1e-300)).sum(axis=1)
            A = np.maximum(A, 1e-12)
            alpha = max(self.shape_floor, p.shape_group[gi])
            logy = np.log(np.maximum(y_pos, 1e-300))
            for _ in range(25):
                g1 = (A*(logy - digamma(alpha)) - B - y_pos*C).sum()
                H = -(A*(1.0/np.maximum(alpha,1e-6))).sum()
                step = g1 / (H if H != 0 else -1.0)
                alpha_new = alpha - 0.3*step
                if not np.isfinite(alpha_new): break
                if abs(alpha_new - alpha) < 1e-4: 
                    alpha = alpha_new; break
                alpha = max(self.shape_floor, alpha_new)
            p.shape_group[gi] = max(self.shape_floor, alpha)
        return p

    # mixture CDF and predictive moments
    def _component_params(self, F: np.ndarray, p: _GammaParams):
        m = F.shape[1]
        mu = self._mu(F, p)
        g = self._groups(m)
        alpha = np.empty(m)
        for gi, Gm in enumerate(g.groups): alpha[Gm] = p.shape_group[gi]
        scale = mu / np.maximum(alpha[None,:], 1e-12)
        return alpha, scale, mu

    def predictive_mean_var(self, f_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        p: _GammaParams = self.params_
        if p is None: raise RuntimeError("Model not fitted.")
        f = np.atleast_2d(f_new).astype(float); m = f.shape[1]
        alpha, scale, mu = self._component_params(f, p)
        w = p.weights_member
        mean = (w * mu).sum(axis=1)
        var = (w * (alpha[None,:]*(scale**2) + (mu - mean[:,None])**2)).sum(axis=1)
        return mean.squeeze(), var.squeeze()

    def cdf(self, x: np.ndarray, f_new: np.ndarray) -> np.ndarray:
        p: _GammaParams = self.params_
        if p is None: raise RuntimeError("Model not fitted.")
        f = np.atleast_2d(f_new).astype(float); x = np.asarray(x)
        alpha, scale, _ = self._component_params(f, p)
        w = p.weights_member
        # mixture CDF is weighted sum of component CDFs
        F_mix = np.zeros((f.shape[0],) + x.shape, dtype=float)
        # broadcast over x by adding last axis
        for i in range(f.shape[0]):
            Fi = np.zeros_like(x, dtype=float)
            for k in range(alpha.shape[1] if alpha.ndim==2 else alpha.shape[0]):
                ak = alpha[i,k] if alpha.ndim==2 else alpha[k]
                sk = scale[i,k] if scale.ndim==2 else scale[k]
                Fi = Fi + w[k] * scigamma.cdf(x, a=ak, scale=sk)
            F_mix[i] = Fi
        return F_mix.squeeze()

    def ppf(self, q: np.ndarray, f_new: np.ndarray, lo: float=0.0, hi: float=1e4, it: int=60) -> np.ndarray:
        q = np.atleast_1d(q); f = np.atleast_2d(f_new)
        out = np.empty((f.shape[0], q.size))
        for i in range(f.shape[0]):
            for j, qq in enumerate(q):
                a, b = lo, hi
                for _ in range(it):
                    mid = 0.5*(a+b)
                    c = (self.cdf(mid, f[i:i+1]) - qq)[0]
                    if c > 0: b = mid
                    else: a = mid
                out[i,j] = 0.5*(a+b)
        return out.squeeze()


@dataclass
class _Gamma0Params(_GammaParams):
    p0: float = 0.0


class GammaZeroInflatedBMA(GammaBMA):
    """Precipitation: P(Y=0)=p0; Y>0 ~ Gamma mixture as in GammaBMA."""
    def _init_extra(self, y, F, p):
        base: _GammaParams = super()._init_extra(y, F, p)
        return _Gamma0Params(**base.__dict__, p0=float(np.mean(y <= 0)))

    def fit(self, F: np.ndarray, y: np.ndarray):
        F = np.asarray(F, float); y = np.asarray(y, float)
        T, m = F.shape
        mask = _nan_mask(F, y); F, y = F[mask], y[mask]
        g = self._groups(m); G = g.n_groups()
        w = np.ones(m)/m
        a = np.zeros(G); b = np.ones(G)
        for gi,Gm in enumerate(g.groups):
            xg = F[:,Gm].mean(axis=1)
            a[gi], b[gi] = _wls_ab(y, xg, np.ones_like(y))
        p = _Gamma0Params(weights_member=w, a_group=a, b_group=b,
                          shape_group=np.full(G, 5.0), p0=float(np.mean(y<=0)))
        prev_ll = -np.inf
        for it in range(self.max_iter):
            pos = y > 0
            logpdf_pos = super()._logpdf_matrix(y[pos], F[pos], p)
            lse = np.log(p.weights_member + 1e-300) + logpdf_pos
            max_ = np.max(lse, axis=1, keepdims=True)
            num = np.exp(lse - max_); den = num.sum(axis=1, keepdims=True) + 1e-300
            r_pos = num/den
            ll = (np.log(num.sum(axis=1)) + max_.squeeze()).sum()
            nz = (~pos).sum()
            ll += nz*np.log(max(p.p0, 1e-12)) + pos.sum()*np.log(max(1-p.p0, 1e-12))
            if self.verbose: print(f"[EM] {it:03d} ll={ll:.6f} p0={p.p0:.3f}")
            if abs(ll - prev_ll) < self.tol: break
            prev_ll = ll
            # M-step
            w = r_pos.sum(axis=0)/max(pos.sum(),1e-12)
            w = np.maximum(w, self.w_floor); w /= w.sum()
            p.weights_member = w
            p.p0 = float((~pos).mean())
            if pos.any():
                p = super()._mstep_params(y[pos], F[pos], r_pos, p)
        self.params_ = p
        return self

    def predictive_mean_var(self, f_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        p: _Gamma0Params = self.params_
        if p is None: raise RuntimeError("Model not fitted.")
        mean_g, var_g = super().predictive_mean_var(f_new)
        mean = (1 - p.p0)*mean_g
        var  = (1 - p.p0)*var_g + (1 - p.p0)*p.p0*(mean_g**2)
        return mean.squeeze(), var.squeeze()

    def cdf(self, x: np.ndarray, f_new: np.ndarray) -> np.ndarray:
        p: _Gamma0Params = self.params_
        if p is None: raise RuntimeError("Model not fitted.")
        base = super().cdf(x, f_new)
        x = np.asarray(x)
        z = (x <= 0).astype(float)
        return (p.p0 * z) + (1 - p.p0) * base


# ===============================================================
# Xarray/Dask wrappers (Gaussian, Gamma, Gamma0)
# ===============================================================

def _require_xarray():
    if xr is None:
        raise ImportError("xarray is required for the xarray/Dask wrappers.")


def _groups_as_list(groups: ExchangeableGroups | List[List[int]]) -> List[List[int]]:
    return groups.groups if isinstance(groups, ExchangeableGroups) else groups


# -------- Gaussian wrappers --------

def fit_gaussian_grid(F_da, y_da, groups: List[List[int]], common_variance=True,
                      max_iter=200, tol=1e-6, w_floor=1e-8, verbose=False):
    _require_xarray()
    if 'member' not in F_da.dims or 'time' not in F_da.dims:
        raise ValueError("F_da must have dims ('time','member', ...).")
    groups_ll = _groups_as_list(groups)
    G = len(groups_ll)

    def core(F, y):
        model = GaussianBMA(exchangeable=ExchangeableGroups(groups_ll),
                            common_variance=common_variance,
                            max_iter=max_iter, tol=tol, w_floor=w_floor, verbose=False).fit(F, y)
        p: _GaussianParams = model.params_
        return p.weights_member, p.a_group, p.b_group, p.var_group

    out = xr.apply_ufunc(
        core, F_da, y_da,
        input_core_dims=[["time","member"], ["time"]],
        output_core_dims=[["member"], ["group"], ["group"], ["group"]],
        vectorize=True, dask='parallelized', output_dtypes=[float, float, float, float]
    )
    ds = xr.Dataset(
        data_vars=dict(
            weights_member=(('member',) + F_da.dims[2:], out[0]),
            a_group=(('group',) + F_da.dims[2:], out[1]),
            b_group=(('group',) + F_da.dims[2:], out[2]),
            var_group=(('group',) + F_da.dims[2:], out[3]),
        ),
        coords=dict(member=F_da['member'], group=np.arange(G))
    )
    ds.attrs['groups'] = groups_ll
    ds.attrs['common_variance'] = common_variance
    return ds


def predict_gaussian_grid(params_ds, F_test):
    _require_xarray()
    groups_ll = params_ds.attrs.get('groups')
    common_variance = params_ds.attrs.get('common_variance', True)

    def core(F, w, a, b, var):
        m = F.shape[-1]
        a_k = np.zeros(m); b_k = np.zeros(m)
        for gi, Gm in enumerate(groups_ll):
            a_k[Gm] = a[gi]; b_k[Gm] = b[gi]
        mu = a_k + b_k*F
        if common_variance:
            v_m = np.full(m, var.mean())
        else:
            v_m = np.zeros(m)
            for gi,Gm in enumerate(groups_ll):
                v_m[Gm] = var[gi]
        mean = (w*mu).sum(axis=-1)
        var_out = (w*(v_m + (mu-mean[...,None])**2)).sum(axis=-1)
        return mean, var_out

    if 'time' in F_test.dims:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['var_group'],
            input_core_dims=[["time","member"], ["member"], ["group"], ["group"], ["group"]],
            output_core_dims=[["time"], ["time"]],
            vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))
    else:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['var_group'],
            input_core_dims=[["member"], ["member"], ["group"], ["group"], ["group"]],
            output_core_dims=[[], []], vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))


# -------- Gamma wrappers --------

def fit_gamma_grid(F_da, y_da, groups: List[List[int]],
                   max_iter=200, tol=1e-6, w_floor=1e-8, verbose=False):
    _require_xarray()
    if 'member' not in F_da.dims or 'time' not in F_da.dims:
        raise ValueError("F_da must have dims ('time','member', ...).")
    groups_ll = _groups_as_list(groups)
    G = len(groups_ll)

    def core(F, y):
        model = GammaBMA(exchangeable=ExchangeableGroups(groups_ll),
                         max_iter=max_iter, tol=tol, w_floor=w_floor, verbose=False).fit(F, y)
        p: _GammaParams = model.params_
        return p.weights_member, p.a_group, p.b_group, p.shape_group

    out = xr.apply_ufunc(
        core, F_da, y_da,
        input_core_dims=[["time","member"], ["time"]],
        output_core_dims=[["member"], ["group"], ["group"], ["group"]],
        vectorize=True, dask='parallelized', output_dtypes=[float, float, float, float]
    )
    ds = xr.Dataset(
        data_vars=dict(
            weights_member=(('member',) + F_da.dims[2:], out[0]),
            a_group=(('group',) + F_da.dims[2:], out[1]),
            b_group=(('group',) + F_da.dims[2:], out[2]),
            shape_group=(('group',) + F_da.dims[2:], out[3]),
        ),
        coords=dict(member=F_da['member'], group=np.arange(G))
    )
    ds.attrs['groups'] = groups_ll
    return ds


def predict_gamma_grid(params_ds, F_test):
    _require_xarray()
    groups_ll = params_ds.attrs.get('groups')

    def core(F, w, a, b, shape):
        m = F.shape[-1]
        a_k = np.zeros(m); b_k = np.zeros(m)
        for gi, Gm in enumerate(groups_ll):
            a_k[Gm] = a[gi]; b_k[Gm] = b[gi]
        mu = _softplus(a_k + b_k*F)
        alpha = np.zeros(m)
        for gi,Gm in enumerate(groups_ll):
            alpha[Gm] = max(1e-3, shape[gi])
        scale = mu / np.maximum(alpha, 1e-12)
        mean = (w*mu).sum(axis=-1)
        var_out = (w*(alpha*(scale**2) + (mu-mean[...,None])**2)).sum(axis=-1)
        return mean, var_out

    if 'time' in F_test.dims:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['shape_group'],
            input_core_dims=[["time","member"], ["member"], ["group"], ["group"], ["group"]],
            output_core_dims=[["time"], ["time"]],
            vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))
    else:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['shape_group'],
            input_core_dims=[["member"], ["member"], ["group"], ["group"], ["group"]],
            output_core_dims=[[], []], vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))


# -------- Gamma0 wrappers --------

def fit_gamma0_grid(F_da, y_da, groups: List[List[int]],
                    max_iter=200, tol=1e-6, w_floor=1e-8, verbose=False):
    _require_xarray()
    if 'member' not in F_da.dims or 'time' not in F_da.dims:
        raise ValueError("F_da must have dims ('time','member', ...).")
    groups_ll = _groups_as_list(groups)
    G = len(groups_ll)

    def core(F, y):
        model = GammaZeroInflatedBMA(exchangeable=ExchangeableGroups(groups_ll),
                                     max_iter=max_iter, tol=tol, w_floor=w_floor, verbose=False).fit(F, y)
        p: _Gamma0Params = model.params_
        return p.weights_member, p.a_group, p.b_group, p.shape_group, p.p0

    out = xr.apply_ufunc(
        core, F_da, y_da,
        input_core_dims=[["time","member"], ["time"]],
        output_core_dims=[["member"], ["group"], ["group"], ["group"], []],
        vectorize=True, dask='parallelized', output_dtypes=[float, float, float, float, float]
    )
    ds = xr.Dataset(
        data_vars=dict(
            weights_member=(('member',) + F_da.dims[2:], out[0]),
            a_group=(('group',) + F_da.dims[2:], out[1]),
            b_group=(('group',) + F_da.dims[2:], out[2]),
            shape_group=(('group',) + F_da.dims[2:], out[3]),
            p0=(F_da.dims[2:], out[4]),
        ),
        coords=dict(member=F_da['member'], group=np.arange(G))
    )
    ds.attrs['groups'] = groups_ll
    return ds


def predict_gamma0_grid(params_ds, F_test):
    _require_xarray()
    groups_ll = params_ds.attrs.get('groups')

    def core(F, w, a, b, shape, p0):
        m = F.shape[-1]
        a_k = np.zeros(m); b_k = np.zeros(m)
        for gi, Gm in enumerate(groups_ll):
            a_k[Gm] = a[gi]; b_k[Gm] = b[gi]
        mu = _softplus(a_k + b_k*F)
        alpha = np.zeros(m)
        for gi,Gm in enumerate(groups_ll):
            alpha[Gm] = max(1e-3, shape[gi])
        scale = mu / np.maximum(alpha, 1e-12)
        mean_g = (w*mu).sum(axis=-1)
        var_g  = (w*(alpha*(scale**2) + (mu-mean_g[...,None])**2)).sum(axis=-1)
        mean = (1 - p0)*mean_g
        var  = (1 - p0)*var_g + (1 - p0)*p0*(mean_g**2)
        return mean, var

    if 'time' in F_test.dims:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['shape_group'], params_ds['p0'],
            input_core_dims=[["time","member"], ["member"], ["group"], ["group"], ["group"], []],
            output_core_dims=[["time"], ["time"]],
            vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))
    else:
        out = xr.apply_ufunc(
            core, F_test, params_ds['weights_member'], params_ds['a_group'],
            params_ds['b_group'], params_ds['shape_group'], params_ds['p0'],
            input_core_dims=[["member"], ["member"], ["group"], ["group"], ["group"], []],
            output_core_dims=[[], []], vectorize=True, dask='parallelized', output_dtypes=[float, float]
        )
        return xr.Dataset(dict(mean=out[0], var=out[1]))


# ===============================================================
# WASS2S facade classes
# ===============================================================

class WAS_BMA_Gaussian:
    """WASS2S facade for Gaussian BMA.

    Parameters
    ----------
    groups : List[List[int]]
        Exchangeable member groups.
    fit_method : {"em","crps"}
        EM on NLL ("em") or CRPS-first joint optimizer ("crps").
    common_variance : bool
        If True, one σ shared across groups (recommended, matches R default).
    """
    def __init__(self, groups: List[List[int]], fit_method: str = "em", common_variance: bool = True):
        self.groups = groups
        self.fit_method = fit_method
        self.common_variance = common_variance
        self.model = GaussianBMA(exchangeable=ExchangeableGroups(groups), common_variance=common_variance)

    def fit(self, F: np.ndarray, y: np.ndarray):
        if self.fit_method == "crps":
            self.model.fit_crps_lbfgs(F, y)
        else:
            self.model.fit(F, y)
        return self

    def predict(self, F_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return self.model.predictive_mean_var(F_new)

    def predict_tercile_probs(self, F_new: np.ndarray, terciles: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t1, t2 = terciles
        pB = self.model.cdf(t1, F_new)
        pA = 1 - self.model.cdf(t2, F_new)
        pN = 1 - pB - pA
        return pB, pN, pA


class WAS_BMA_Gamma:
    """WASS2S facade for Gamma BMA (strictly-positive variables)."""
    def __init__(self, groups: List[List[int]]):
        self.groups = groups
        self.model = GammaBMA(exchangeable=ExchangeableGroups(groups))

    def fit(self, F: np.ndarray, y: np.ndarray):
        self.model.fit(F, y); return self

    def predict(self, F_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return self.model.predictive_mean_var(F_new)

    def predict_tercile_probs(self, F_new: np.ndarray, terciles: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t1, t2 = terciles
        pB = self.model.cdf(t1, F_new)
        pA = 1 - self.model.cdf(t2, F_new)
        pN = 1 - pB - pA
        return pB, pN, pA


class WAS_BMA_Gamma0:
    """WASS2S facade for Zero-Inflated Gamma BMA (precipitation)."""
    def __init__(self, groups: List[List[int]]):
        self.groups = groups
        self.model = GammaZeroInflatedBMA(exchangeable=ExchangeableGroups(groups))

    def fit(self, F: np.ndarray, y: np.ndarray):
        self.model.fit(F, y); return self

    def predict(self, F_new: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return self.model.predictive_mean_var(F_new)

    def predict_tercile_probs(self, F_new: np.ndarray, terciles: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t1, t2 = terciles
        pB = self.model.cdf(t1, F_new)
        pA = 1 - self.model.cdf(t2, F_new)
        pN = 1 - pB - pA
        return pB, pN, pA
